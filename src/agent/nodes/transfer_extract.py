import json

from src.agent.state import ChatAgentState
from src.agent.llm import client, MODEL

_SYSTEM_PROMPT = """사용자의 메시지에서 이체 정보를 추출하세요.
다음 JSON 형식으로만 응답하세요:
{
  "from_account_id": "출금 계좌 ID (없으면 null)",
  "to_account_id": "입금 계좌 ID (없으면 null)",
  "amount": 금액 (없으면 null),
  "description": "이체 메모 (없으면 null)",
  "missing": ["부족한 정보 목록"],
  "question": "사용자에게 물어볼 내용 (정보가 충분하면 null)"
}"""


def transfer_extract_node(state: ChatAgentState) -> dict:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            *state["messages"],
        ],
        temperature=0,
    )

    try:
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        extracted = json.loads(raw.strip())
    except (json.JSONDecodeError, IndexError):
        extracted = {"missing": ["파싱 오류"], "question": "다시 말씀해 주시겠어요?"}

    question = extracted.get("question")
    info_complete = not extracted.get("missing") and question is None

    updated_messages = state["messages"]
    if question:
        updated_messages = state["messages"] + [{"role": "assistant", "content": question}]

    return {
        "from_account_id": extracted.get("from_account_id") or "",
        "to_account_id": extracted.get("to_account_id") or "",
        "amount": extracted.get("amount") or 0,
        "description": extracted.get("description") or "",
        "transfer_info_complete": info_complete,
        "messages": updated_messages,
    }
