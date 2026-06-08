from src.agent.state import ChatAgentState
from src.agent.tools.transfer import get_bank_accounts

_BANK_NAMES = {
    "020": "우리은행", "088": "신한은행", "004": "KB국민은행", "011": "NH농협",
    "081": "하나은행", "090": "카카오뱅크", "092": "토스뱅크", "071": "우체국",
    "089": "케이뱅크", "243": "한국투자증권", "247": "NH투자증권",
}


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

    to_bank_code = state.get("to_bank_code", "")
    to_account_number = state.get("to_account_number", "")
    amount = state.get("amount", 0)

    # 이미 조회한 계좌 목록에서 출금 계좌 잔액 추출 (별도 잔액 API 불필요)
    from_account = next(
        (a for a in accounts if str(a.get("accountId")) == str(from_account_id)),
        None,
    )
    balance = int(from_account.get("balance") or 0) if from_account else 0

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

    if all_complete:
        to_bank_name = _BANK_NAMES.get(to_bank_code, to_bank_code)
        from_acc_name = from_account.get("accountName", "") if from_account else ""
        from_acc_num = from_account.get("accountNumber", "") if from_account else ""
        remaining = balance - amount
        msg = (
            f"💰 이체 확인\n"
            f"• 출금 계좌: {from_acc_name} ({from_acc_num})\n"
            f"• 입금 계좌: {to_bank_name} {to_account_number}\n"
            f"• 이체 금액: {amount:,}원\n"
            f"• 이체 후 잔액: {remaining:,}원\n"
            f"PIN을 입력해 주세요."
        )
        return {
            "realtime_data": {"accounts": accounts, "transfer_limit": balance},
            "transfer_info_complete": True,
            "messages": state["messages"] + [{"role": "assistant", "content": msg}],
        }

    return {
        "realtime_data": {
            "accounts": accounts,
            "transfer_limit": balance,
        },
        "transfer_info_complete": all_complete,
    }
