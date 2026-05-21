from src.agent.state import ChatAgentState
from src.agent.tools.transfer import get_bank_accounts, get_transfer_limit


async def transfer_check_node(state: ChatAgentState) -> dict:
    # TODO: token 연동 (백엔드 인증 완성 후)
    try:
        accounts = await get_bank_accounts()
        limit_data = await get_transfer_limit(state.get("from_account_id", ""))
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
