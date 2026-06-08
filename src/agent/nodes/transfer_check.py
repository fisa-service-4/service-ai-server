from src.agent.state import ChatAgentState
from src.agent.tools.transfer import get_bank_accounts, get_transfer_limit


async def transfer_check_node(state: ChatAgentState) -> dict:
    token = state.get("token")
    from_account_id = state.get("from_account_id", "")

    try:
        accounts = await get_bank_accounts(token=token)
    except Exception:
        accounts = []

    _ROLE_DISPLAY = {
        "DEPOSIT": "입금 통장",
        "SALARY": "월급 통장",
        "EMERGENCY": "비상금 통장",
        "STOCK": "투자 통장",
    }

    # 계좌 조회 실패
    if not from_account_id and not accounts:
        msg = "연동된 계좌 정보를 불러올 수 없습니다. 잠시 후 다시 시도해주세요."
        return {
            "realtime_data": {},
            "transfer_info_complete": False,
            "messages": state["messages"] + [{"role": "assistant", "content": msg}],
        }

    # 출금 계좌 미지정 → 계좌 목록 + 입금 정보 요청을 한 번에 표시
    if not from_account_id and accounts:
        lines = ["이체를 진행할게요. 아래 정보를 함께 알려주세요.\n"]
        lines.append("[출금 계좌 선택]")
        for i, acc in enumerate(accounts, start=1):
            balance = acc.get("balance") or 0
            role = acc.get("accountRole")
            bank_code = acc.get("bankCode", "")
            if bank_code in {"243", "247"}:
                display_name = "주식 계좌"
            else:
                display_name = _ROLE_DISPLAY.get(role, acc.get("accountName", "계좌"))
            lines.append(
                f"{i}. {display_name} "
                f"({acc.get('accountNumber', '')}) "
                f"- {balance:,}원"
            )
        lines.append("\n입금하실 은행, 계좌번호, 금액을 함께 말씀해 주세요.")
        lines.append("예) \"1번에서 신한은행 110-123-456789로 5만원\"")
        msg = "\n".join(lines)
        return {
            "realtime_data": {"accounts": accounts},
            "transfer_info_complete": False,
            "messages": state["messages"] + [{"role": "assistant", "content": msg}],
        }

    # 출금 계좌 있으면 잔액 조회
    limit_data = {}
    if from_account_id:
        try:
            limit_data = await get_transfer_limit(from_account_id, token=token)
        except Exception:
            limit_data = {}

    to_bank_code = state.get("to_bank_code", "")
    to_account_number = state.get("to_account_number", "")
    amount = state.get("amount", 0)
    balance = limit_data.get("balance", 0) or 0

    if amount and balance < amount:
        msg = f"잔액이 부족합니다. 현재 잔액: {balance:,}원, 이체 금액: {amount:,}원"
        return {
            "realtime_data": {"accounts": accounts, "transfer_limit": balance},
            "transfer_info_complete": False,
            "messages": state["messages"] + [{"role": "assistant", "content": msg}],
        }

    all_complete = (
        bool(from_account_id)
        and bool(to_bank_code)
        and bool(to_account_number)
        and bool(amount)
    )

    return {
        "realtime_data": {
            "accounts": accounts,
            "transfer_limit": balance,
        },
        "transfer_info_complete": all_complete,
    }
