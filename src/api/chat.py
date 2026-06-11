import jwt
import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from src.agent.graph import chat_graph
from src.api.response import ok
import src.agent.tools.client as backend

try:
    from langgraph.errors import GraphInterrupt as _GraphInterrupt
except ImportError:
    _GraphInterrupt = None

router = APIRouter(prefix="/api/v1/ai", tags=["AI Chat"])
_bearer = HTTPBearer()
_log = logging.getLogger(__name__)

# LangGraph 대화 컨텍스트 로컬 캐시 (에페머럴 — 서버 재시작 시 초기화, 백엔드 DB가 원본)
_chat_threads: dict[int, dict] = {}


class SendMessageRequest(BaseModel):
    sessionId: int
    message: str
    isPin: bool = False


def _extract_user_id(credentials: HTTPAuthorizationCredentials) -> str:
    try:
        payload = jwt.decode(
            credentials.credentials,
            options={"verify_signature": False},
            algorithms=["HS256", "RS256"],
        )
        return str(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")


async def _get_or_init_thread(session_id: int, user_id: str, token: str) -> dict:
    """로컬 스레드 캐시 반환. 없으면 백엔드에서 메시지 이력을 가져와 초기화."""
    if session_id in _chat_threads:
        if _chat_threads[session_id]["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")
        return _chat_threads[session_id]

    messages = []
    try:
        resp = await backend.get(
            f"/api/v1/ai/chat/sessions/{session_id}/messages",
            token=token,
            params={"size": 100},
        )
        for m in (resp.get("data") or {}).get("content", []):
            role = "user" if m.get("role") == "USER" else "assistant"
            messages.append({"role": role, "content": m.get("content", "")})
    except Exception as e:
        _log.error("[Chat] 메시지 이력 로드 실패 (session_id=%s): %s", session_id, e)
        raise HTTPException(status_code=503, detail="메시지 이력을 불러올 수 없습니다.")

    _chat_threads[session_id] = {
        "user_id": user_id,
        "messages": messages,
        "thread_version": 1,
        "pre_interrupt_count": None,
    }
    return _chat_threads[session_id]


async def _save_message(
    session_id: int,
    token: str,
    role: str,
    content: str,
    intent: str | None = None,
    action_type: str | None = None,
) -> None:
    try:
        payload: dict = {"sessionId": session_id, "role": role, "content": content}
        if intent:
            payload["intent"] = intent
        if action_type:
            payload["actionType"] = action_type
        await backend.post("/api/v1/ai/chat/messages/record", token=token, body=payload)
    except Exception as e:
        _log.warning("[Chat] 메시지 DB 저장 실패 (session_id=%s, role=%s): %s", session_id, role, e)


@router.post("/chat/run")
async def send_message(
    body: SendMessageRequest,
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
):
    user_id = _extract_user_id(credentials)
    token = credentials.credentials
    session_id = body.sessionId

    thread = await _get_or_init_thread(session_id, user_id, token)

    if not body.isPin:
        thread["messages"].append({"role": "user", "content": body.message})
        await _save_message(session_id, token, "USER", body.message)

    thread_version = thread.get("thread_version", 1)
    config = {"configurable": {"thread_id": f"{session_id}_{thread_version}"}}
    initial_state = {
        "user_id": user_id,
        "token": token,
        "session_id": session_id,
        "messages": thread["messages"],
    }

    is_interrupted = False
    try:
        snapshot = chat_graph.get_state(config)
        is_interrupted = snapshot is not None and bool(snapshot.next)
    except Exception:
        pass

    from langgraph.types import Command

    try:
        if is_interrupted and body.isPin:
            result = await chat_graph.ainvoke(Command(resume=body.message), config=config)
        elif is_interrupted and not body.isPin:
            pre_count = thread.pop("pre_interrupt_count", None)
            if pre_count is not None:
                new_user_msg = thread["messages"][-1]
                thread["messages"] = thread["messages"][:pre_count] + [new_user_msg]
            thread["thread_version"] = thread_version + 1
            config = {"configurable": {"thread_id": f"{session_id}_{thread['thread_version']}"}}
            initial_state = {
                "user_id": user_id,
                "token": token,
                "session_id": session_id,
                "messages": thread["messages"],
            }
            result = await chat_graph.ainvoke(initial_state, config=config)
        else:
            result = await chat_graph.ainvoke(initial_state, config=config)
    except BaseException as e:
        if _GraphInterrupt and isinstance(e, _GraphInterrupt):
            result = None
        else:
            _log.exception("chat_graph 실행 오류: %s", e)
            fallback = "죄송합니다. 해당 질문에는 답변하기 어렵습니다. 다른 방식으로 질문해 주시거나, 계좌 조회·이체·주식 주문 등 필요하신 부분을 알려주세요."
            thread["messages"].append({"role": "assistant", "content": fallback})
            await _save_message(session_id, token, "AI", fallback, intent="UNKNOWN")
            return ok({
                "role": "AI",
                "intent": "UNKNOWN",
                "content": fallback,
                "actionRequired": False,
            })

    caught_interrupt = result is None
    try:
        post_snapshot = chat_graph.get_state(config)
        snapshot_next = post_snapshot.next if post_snapshot else ()
        snapshot_interrupts = getattr(post_snapshot, "interrupts", ()) if post_snapshot else ()
        now_interrupted = caught_interrupt or bool(snapshot_next) or bool(snapshot_interrupts)
        sv = post_snapshot.values if post_snapshot else {}
        _log.info(
            "[Chat] caught_interrupt=%s next=%s interrupts=%s now_interrupted=%s",
            caught_interrupt, snapshot_next, snapshot_interrupts, now_interrupted,
        )
    except Exception:
        now_interrupted = caught_interrupt
        sv = result or {}

    if now_interrupted:
        if snapshot_interrupts:
            interrupt_val = getattr(snapshot_interrupts[0], "value", None)
            ai_content = interrupt_val if isinstance(interrupt_val, str) else "PIN을 입력해 주세요."
        else:
            ai_msgs = [m for m in sv.get("messages", []) if isinstance(m, dict) and m.get("role") == "assistant"]
            ai_content = ai_msgs[-1]["content"] if ai_msgs else "PIN을 입력해 주세요."
        intent = sv.get("intent", "STOCK")
        thread["pre_interrupt_count"] = len(thread["messages"])
        thread["messages"].append({"role": "assistant", "content": ai_content})
        await _save_message(session_id, token, "AI", ai_content, intent=intent, action_type="PIN_REQUIRED")
        return ok({
            "role": "AI",
            "intent": intent,
            "content": ai_content,
            "actionRequired": True,
            "requirePin": True,
        })

    messages_source = result if result is not None else sv
    ai_messages = [
        m for m in messages_source.get("messages", [])
        if isinstance(m, dict) and m.get("role") == "assistant"
    ]
    ai_content = ai_messages[-1]["content"] if ai_messages else "처리가 완료되었습니다."
    intent = messages_source.get("intent", "UNKNOWN")
    action_required = bool(messages_source.get("pending_action"))

    thread["messages"].append({"role": "assistant", "content": ai_content})
    await _save_message(session_id, token, "AI", ai_content, intent=intent)

    return ok({
        "role": "AI",
        "intent": intent,
        "content": ai_content,
        "actionRequired": action_required,
    })
