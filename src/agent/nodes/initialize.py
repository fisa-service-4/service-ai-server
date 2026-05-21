from src.agent.state import ChatAgentState


def initialize_node(state: ChatAgentState) -> dict:
    return {
        "analysis_data": {},
        "realtime_data": {},
        "intent": "",
        "current_task": "",
        "rag_context": "",
        "recommended_ratio": {},
        "want_apply": False,
        "apply_confirmed": False,
        "apply_pin_verified": False,
        "stock_info": {},
        "pending_action": {},
        "info_complete": False,
        "confirmed": False,
        "stock_pin_verified": False,
        "need_extra": False,
        "raw_data": {},
        "extra_analysis_data": {},
        "from_account_id": "",
        "to_account_id": "",
        "amount": 0,
        "description": "",
        "transfer_info_complete": False,
        "transfer_confirmed": False,
        "transfer_pin_verified": False,
    }
