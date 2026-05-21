from typing import TypedDict


class ChatAgentState(TypedDict):
    # 공통
    user_id: str
    messages: list
    intent: str              # ASSET / STOCK / TRANSFER / UNKNOWN
    current_task: str

    # 자산관리
    rag_context: str
    analysis_data: dict
    realtime_data: dict
    recommended_ratio: dict
    want_apply: bool
    apply_confirmed: bool
    apply_pin_verified: bool

    # 증권
    stock_info: dict         # {code, name, quantity, price, order_type}
    pending_action: dict
    info_complete: bool
    confirmed: bool
    stock_pin_verified: bool

    # 동적 데이터 분석
    need_extra: bool
    raw_data: dict
    extra_analysis_data: dict

    # 이체
    from_account_id: str
    to_account_id: str
    amount: int
    description: str
    transfer_info_complete: bool
    transfer_confirmed: bool
    transfer_pin_verified: bool
