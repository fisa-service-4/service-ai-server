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


def _extract_user_id(credentials: HTTPAuthorizationCredentials) -> str:
    try:
        payload = jwt.decode(credentials.credentials, options={"verify_signature": False}, algorithms=["HS256"])
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

    session["messages"].append({"role": "user", "content": body.message})

    config = {"configurable": {"thread_id": str(body.sessionId)}}
    initial_state = {
        "user_id": session["user_id"],
        "token": credentials.credentials,
        "messages": session["messages"],
    }

    try:
        result = await chat_graph.ainvoke(initial_state, config=config)

        ai_messages = [m for m in result.get("messages", []) if isinstance(m, dict) and m.get("role") == "assistant"]
        ai_content = ai_messages[-1]["content"] if ai_messages else "처리가 완료되었습니다."
        intent = result.get("intent", "UNKNOWN")
        action_required = bool(result.get("pending_action"))

        session["messages"].append({"role": "assistant", "content": ai_content})

        global _message_counter
        _message_counter += 1

        return ok({
            "messageId": _message_counter,
            "role": "AI",
            "intent": intent,
            "content": ai_content,
            "actionRequired": action_required,
        })
    except BaseException as e:
        import logging
        _log = logging.getLogger(__name__)

        if _GraphInterrupt and isinstance(e, _GraphInterrupt):
            # Graph paused before Verifier (PIN confirmation needed).
            # Extract the last saved state to return the AI recommendation.
            try:
                snapshot = chat_graph.get_state(config)
                sv = snapshot.values if snapshot else {}
                ai_msgs = [m for m in sv.get("messages", []) if isinstance(m, dict) and m.get("role") == "assistant"]
                ai_content = ai_msgs[-1]["content"] if ai_msgs else "추가 확인이 필요합니다."
                intent = sv.get("intent", "ASSET")
                session["messages"].append({"role": "assistant", "content": ai_content})
                _message_counter += 1
                return ok({
                    "messageId": _message_counter,
                    "role": "AI",
                    "intent": intent,
                    "content": ai_content,
                    "actionRequired": True,
                })
            except Exception:
                _log.exception("GraphInterrupt 상태 복구 실패")

        _log.exception("chat_graph 실행 오류: %s", e)
        return fail("AI_001", "AI 응답 생성에 실패했습니다.")


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
