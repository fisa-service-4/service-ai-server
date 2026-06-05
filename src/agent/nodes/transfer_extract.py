import json

from src.agent.state import ChatAgentState
from src.agent.llm import client, MODEL

_BASE_PROMPT = """사용자의 메시지에서 이체 정보를 추출하세요.
다음 JSON 형식으로만 응답하세요:
{
  "from_account_id": "출금 계좌 ID (숫자, 없으면 null)",
  "to_bank_code": "입금 은행 코드 (예: 020, 088, 없으면 null)",
  "to_account_number": "입금 계좌번호 (예: 110-123-456789, 없으면 null)",
  "amount": 금액 (숫자, 없으면 null),
  "description": "이체 메모 (없으면 null)",
  "missing": ["부족한 정보 목록"],
  "question": "사용자에게 물어볼 내용 (정보가 충분하면 null)"
}

은행 코드 참고: 우리은행=020, 신한은행=088, KB국민은행=004, NH농협=011, 하나은행=081, 카카오뱅크=090, 토스뱅크=092"""


def transfer_extract_node(state: ChatAgentState) -> dict:
    # 계좌 목록이 있으면 프롬프트에 컨텍스트 추가 (ID는 내부용, 사용자에게 미노출)
    accounts = state.get("realtime_data", {}).get("accounts", [])
    system_prompt = _BASE_PROMPT
    if accounts:
        account_lines = ["\n[사용자 보유 계좌 목록 - from_account_id 매핑 참고용]"]
        for i, acc in enumerate(accounts, start=1):
            account_lines.append(
                f"{i}번: {acc.get('accountName', '계좌')} "
                f"({acc.get('accountNumber', '')}) → accountId: {acc.get('accountId')}"
            )
        system_prompt += "\n".join(account_lines)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
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
        "to_bank_code": extracted.get("to_bank_code") or "",
        "to_account_number": extracted.get("to_account_number") or "",
        "amount": extracted.get("amount") or 0,
        "description": extracted.get("description") or "",
        "transfer_info_complete": info_complete,
        "messages": updated_messages,
    }
