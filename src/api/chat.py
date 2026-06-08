import jwt
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from src.agent.graph import chat_graph
from src.api.response import ok, fail

try:
    from langgraph.errors import GraphInterrupt as _GraphInterrupt
except ImportError:
    _GraphInterrupt = None

router = APIRouter(prefix="/api/v1/ai/chat", tags=["AI Chat"])

_bearer = HTTPBearer()

# DB 연결 전 임시 인메모리
_sessions: dict[int, dict] = {}
_session_counter = 0
_message_counter = 0


class CreateSessionRequest(BaseModel):
    title: str


class SendMessageRequest(BaseModel):
    sessionId: int
    message: str
    isPin: bool = False


import logging as _logging
_auth_log = _logging.getLogger(__name__)


def _extract_user_id(credentials: HTTPAuthorizationCredentials) -> str:
    try:
        payload = jwt.decode(credentials.credentials, options={"verify_signature": False}, algorithms=["HS256", "RS256"])
        _auth_log.info("[Auth] token payload=%s", payload)
        return str(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")


@router.post("/sessions", status_code=201)
async def create_session(
    body: CreateSessionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
):
    global _session_counter
    _session_counter += 1
    session_id = _session_counter

    _sessions[session_id] = {
        "user_id": _extract_user_id(credentials),
        "title": body.title,
        "messages": [],
        "status": "ACTIVE",
    }

    return ok({"sessionId": session_id, "status": "ACTIVE"})


@router.post("/messages")
async def send_message(
    body: SendMessageRequest,
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
):
    global _message_counter

    session = _sessions.get(body.sessionId)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    if not body.isPin:
        session["messages"].append({"role": "user", "content": body.message})

    config = {"configurable": {"thread_id": str(body.sessionId)}}
    initial_state = {
        "user_id": session["user_id"],
        "token": credentials.credentials,
        "messages": session["messages"],
    }

    import logging
    from langgraph.types import Command
    _log = logging.getLogger(__name__)

    # interrupt() 대기 상태 감지
    is_interrupted = False
    try:
        snapshot = chat_graph.get_state(config)
        is_interrupted = snapshot is not None and bool(snapshot.next)
    except Exception:
        pass

    try:
        if is_interrupted:
            result = await chat_graph.ainvoke(Command(resume=body.message), config=config)
        else:
            result = await chat_graph.ainvoke(initial_state, config=config)
    except BaseException as e:
        if _GraphInterrupt and isinstance(e, _GraphInterrupt):
            result = None
        else:
            _log.exception("chat_graph 실행 오류: %s", e)
            fallback = "죄송합니다. 해당 질문에는 답변하기 어렵습니다. 다른 방식으로 질문해 주시거나, 계좌 조회·이체·주식 주문 등 필요하신 부분을 알려주세요."
            session["messages"].append({"role": "assistant", "content": fallback})
            _message_counter += 1
            return ok({
                "messageId": _message_counter,
                "role": "AI",
                "intent": "UNKNOWN",
                "content": fallback,
                "actionRequired": False,
            })

    # ainvoke 이후 snapshot으로 interrupt 여부 판단
    caught_interrupt = result is None  # GraphInterrupt exception으로 감지된 경우
    try:
        post_snapshot = chat_graph.get_state(config)
        snapshot_next = post_snapshot.next if post_snapshot else ()
        snapshot_interrupts = getattr(post_snapshot, "interrupts", ()) if post_snapshot else ()
        now_interrupted = caught_interrupt or bool(snapshot_next) or bool(snapshot_interrupts)
        sv = post_snapshot.values if post_snapshot else {}
        _log.info("[Chat] caught_interrupt=%s next=%s interrupts=%s now_interrupted=%s",
                  caught_interrupt, snapshot_next, snapshot_interrupts, now_interrupted)
    except Exception:
        now_interrupted = caught_interrupt
        sv = result or {}

    if now_interrupted:
        ai_msgs = [m for m in sv.get("messages", []) if isinstance(m, dict) and m.get("role") == "assistant"]
        ai_content = ai_msgs[-1]["content"] if ai_msgs else "PIN을 입력해 주세요."
        intent = sv.get("intent", "STOCK")
        session["messages"].append({"role": "assistant", "content": ai_content})
        _message_counter += 1
        return ok({
            "messageId": _message_counter,
            "role": "AI",
            "intent": intent,
            "content": ai_content,
            "actionRequired": True,
            "requirePin": True,
        })

    messages_source = result if result is not None else sv
    ai_messages = [m for m in messages_source.get("messages", []) if isinstance(m, dict) and m.get("role") == "assistant"]
    ai_content = ai_messages[-1]["content"] if ai_messages else "처리가 완료되었습니다."
    intent = messages_source.get("intent", "UNKNOWN")
    action_required = bool(messages_source.get("pending_action"))

    session["messages"].append({"role": "assistant", "content": ai_content})

    _message_counter += 1

    return ok({
        "messageId": _message_counter,
        "role": "AI",
        "intent": intent,
        "content": ai_content,
        "actionRequired": action_required,
    })


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
):
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    _sessions[session_id]["status"] = "CLOSED"

    return ok({"sessionId": session_id, "status": "CLOSED"})


@router.get("/sessions")
async def get_sessions(credentials: HTTPAuthorizationCredentials = Depends(_bearer)):
    user_id = _extract_user_id(credentials)
    user_sessions = [
        {"sessionId": sid, "title": s["title"], "status": s["status"]}
        for sid, s in _sessions.items()
        if s["user_id"] == user_id
    ]
    return ok(user_sessions)


@router.get("/sessions/{session_id}/messages")
async def get_messages(
    session_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
):
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    return ok({"messages": session["messages"]})
