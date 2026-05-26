from src.agent.state import ChatAgentState
from src.agent.tools.transfer import get_bank_accounts, get_transfer_limit


async def transfer_check_node(state: ChatAgentState) -> dict:
    token = state.get("token")
    try:
        accounts = await get_bank_accounts(token=token)
        limit_data = await get_transfer_limit(state.get("from_account_id", ""), token=token)
    except Exception:
        accounts = []
        limit_data = {}

    return {
        "realtime_data": {
            "accounts": accounts,
            "transfer_limit": limit_data.get("balance"),
        },
        "transfer_info_complete": True,
    }
