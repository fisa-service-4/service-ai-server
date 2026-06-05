from src.agent.state import ChatAgentState
from src.agent.tools.transfer import get_bank_accounts, get_transfer_limit


async def transfer_check_node(state: ChatAgentState) -> dict:
    token = state.get("token")
    from_account_id = state.get("from_account_id", "")

    try:
        accounts = await get_bank_accounts(token=token)
    except Exception:
        accounts = []

    # 출금 계좌 미지정 → 번호 선택지 표시 (ID 노출 없음)
    if not from_account_id and accounts:
        lines = ["출금 계좌를 선택해 주세요."]
        for i, acc in enumerate(accounts, start=1):
            balance = acc.get("balance") or 0
            lines.append(
                f"{i}. {acc.get('accountName', '계좌')} "
                f"({acc.get('accountNumber', '')}) "
                f"- {balance:,}원"
            )
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

    return {
        "realtime_data": {
            "accounts": accounts,
            "transfer_limit": limit_data.get("balance"),
        },
        "transfer_info_complete": True,
    }
