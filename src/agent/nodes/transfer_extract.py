import json

from src.agent.state import ChatAgentState
from src.agent.llm import client, MODEL
from src.agent.tools.transfer import get_bank_accounts

_BASE_PROMPT = """사용자의 메시지에서 이체 정보를 추출하세요.
다음 JSON 형식으로만 응답하세요:
{
  "has_transfer_intent": true 또는 false,
  "from_account_id": "출금 계좌 ID (숫자, 없으면 null)",
  "to_bank_code": "입금 은행 코드 (예: 020, 088, 없으면 null)",
  "to_account_number": "입금 계좌번호 (예: 110-123-456789, 없으면 null)",
  "amount": 금액 (숫자, 없으면 null),
  "description": "이체 메모 (없으면 null)",
  "missing": ["부족한 정보 목록"],
  "question": "사용자에게 물어볼 내용 (정보가 충분하면 null)"
}

has_transfer_intent 판단 기준 (명시적 실행 의도):
- true: "이체해줘", "보내줘", "이체할게", "이체할래", "이체해", "송금해줘", "송금할게", "송금할래", "보낼게", "보낼래"
- false: 계좌/금액 정보만 언급하거나 조회만 하는 경우

은행 코드 참고: 우리은행=020, 신한은행=088, KB국민은행=004, NH농협=011, 하나은행=081, 카카오뱅크=090, 토스뱅크=092"""


async def transfer_extract_node(state: ChatAgentState) -> dict:
    token = state.get("token")

    # 계좌 목록이 없으면 먼저 로드 (LLM이 "1번" 같은 번호를 account_id로 매핑하기 위해)
    accounts = state.get("realtime_data", {}).get("accounts", [])
    if not accounts:
        try:
            accounts = await get_bank_accounts(token=token)
        except Exception:
            accounts = []

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
        raw = (response.choices[0].message.content or "").strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        extracted = json.loads(raw.strip())
    except (json.JSONDecodeError, IndexError, AttributeError):
        extracted = {"missing": ["파싱 오류"], "question": "다시 말씀해 주시겠어요?"}

    question = extracted.get("question")
    has_transfer_intent = extracted.get("has_transfer_intent", False)

    from_account_id = extracted.get("from_account_id") or state.get("from_account_id") or ""
    to_bank_code = extracted.get("to_bank_code") or state.get("to_bank_code") or ""
    to_account_number = extracted.get("to_account_number") or state.get("to_account_number") or ""
    amount = extracted.get("amount") or state.get("amount") or 0

    fields_complete = bool(from_account_id) and bool(to_bank_code) and bool(to_account_number) and bool(amount)
    # 이체 실행은 명시적 의도가 있고 모든 필드가 채워진 경우만
    transfer_info_complete = fields_complete and has_transfer_intent

    updated_messages = state["messages"]
    if question and not fields_complete:
        updated_messages = state["messages"] + [{"role": "assistant", "content": question}]
    elif fields_complete and not has_transfer_intent:
        confirm_msg = "이체를 진행할까요? 진행하시려면 \"이체할게\" 또는 \"이체해줘\"라고 말씀해 주세요."
        updated_messages = state["messages"] + [{"role": "assistant", "content": confirm_msg}]

    return {
        "from_account_id": from_account_id,
        "to_bank_code": to_bank_code,
        "to_account_number": to_account_number,
        "amount": amount,
        "description": extracted.get("description") or "",
        "transfer_info_complete": transfer_info_complete,
        "realtime_data": {**state.get("realtime_data", {}), "accounts": accounts},
        "messages": updated_messages,
    }
