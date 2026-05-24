from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from src.agent.graph import chat_graph
from src.api.response import ok, fail

router = APIRouter(prefix="/api/v1/ai/chat", tags=["AI Chat"])

# DB 연결 전 임시 인메모리
_sessions: dict[int, dict] = {}
_session_counter = 0
_message_counter = 0


class CreateSessionRequest(BaseModel):
    title: str


class SendMessageRequest(BaseModel):
    sessionId: int
    message: str


@router.post("/sessions", status_code=201)
async def create_session(
    body: CreateSessionRequest,
    authorization: str | None = Header(None),
):
    global _session_counter
    _session_counter += 1
    session_id = _session_counter

    _sessions[session_id] = {
        "user_id": _extract_user_id(authorization),
        "title": body.title,
        "messages": [],
        "status": "ACTIVE",
    }

    return ok({"sessionId": session_id, "status": "ACTIVE"})


@router.post("/messages")
async def send_message(
    body: SendMessageRequest,
    authorization: str | None = Header(None),
):
    global _message_counter

    session = _sessions.get(body.sessionId)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    session["messages"].append({"role": "user", "content": body.message})

    config = {"configurable": {"thread_id": str(body.sessionId)}}
    initial_state = {
        "user_id": session["user_id"],
        "messages": session["messages"],
    }

    try:
        result = await chat_graph.ainvoke(initial_state, config=config)
    except Exception as e:
        import logging
        logging.getLogger(__name__).exception("chat_graph 실행 오류: %s", e)
        return fail("AI_001", "AI 응답 생성에 실패했습니다.")

    ai_messages = [m for m in result.get("messages", []) if m.get("role") == "assistant"]
    ai_content = ai_messages[-1]["content"] if ai_messages else "처리가 완료되었습니다."
    intent = result.get("intent", "UNKNOWN")
    action_required = bool(result.get("pending_action"))

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
    authorization: str | None = Header(None),
):
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    _sessions[session_id]["status"] = "CLOSED"

    return ok({"sessionId": session_id, "status": "CLOSED"})


@router.get("/sessions")
async def get_sessions(authorization: str = Header(...)):
    user_id = _extract_user_id(authorization)
    user_sessions = [
        {"sessionId": sid, "title": s["title"], "status": s["status"]}
        for sid, s in _sessions.items()
        if s["user_id"] == user_id
    ]
    return ok(user_sessions)


@router.get("/sessions/{session_id}/messages")
async def get_messages(
    session_id: int,
    authorization: str | None = Header(None),
):
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    return ok({"messages": session["messages"]})


def _extract_user_id(authorization: str) -> str:
    # TODO: JWT 파싱으로 교체
    return "1"
