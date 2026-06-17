# 노드 간에 공유되는 공용 저장소/ 각 노드들은 이 딕셔너리를 읽고 변경할 부분만 반환
from typing import TypedDict


class ChatAgentState(TypedDict):
    # 공통
    user_id: str
    token: str
    session_id: int
    messages: list
    intent: str              # ASSET / STOCK / TRANSFER / UNKNOWN
    current_task: str

    # 가드
    guard_passed: bool       # True: 서브그래프 진입 허용 / False: 즉시 END
    guard_reason: str        # 정책 차단 사유 (로깅/디버깅용)

    # 자산관리
    rag_context: str
    analysis_data: dict
    realtime_data: dict
    recommended_ratio: dict
    want_apply: bool
    apply_confirmed: bool
    apply_pin_verified: bool
    asset_action_type: str   # "apply" / "recommend" / "consult"

    # 증권
    account_id: int
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
    to_bank_code: str
    to_account_number: str
    amount: int
    description: str
    transfer_info_complete: bool
    transfer_confirmed: bool
    transfer_pin_verified: bool
