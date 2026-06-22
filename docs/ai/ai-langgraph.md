# LangGraph Agent

## ChatAgentState
```python
class ChatAgentState(TypedDict):
    # 공통
    user_id: str
    token: str               # JWT Bearer 토큰
    session_id: int          # 채팅 세션 ID
    messages: list
    intent: str              # ASSET / STOCK / TRANSFER / UNKNOWN
    current_task: str

    # 가드
    guard_passed: bool       # 정책 통과 여부
    guard_reason: str        # 차단 사유

    # 자산관리
    rag_context: str         # Vector DB 검색 결과
    analysis_data: dict      # 분석 DB 분석 후 데이터
    realtime_data: dict      # 실시간 조회 운영 데이터 (잔액 등)
    recommended_ratio: dict  # 추천 자산 분배 비율
    want_apply: bool
    apply_confirmed: bool
    apply_pin_verified: bool
    asset_action_type: str   # 자산 액션 유형

    # 증권
    account_id: int          # 증권 계좌 ID
    stock_info: dict         # {code, name, quantity, price, order_type}
    pending_action: dict
    info_complete: bool
    confirmed: bool
    stock_pin_verified: bool

    # 동적 데이터 분석
    need_extra: bool
    raw_data: dict           # 동적 분석용 로우 데이터 (분석 후 None 처리)
    extra_analysis_data: dict  # 도출된 인사이트

    # 이체
    from_account_id: str
    to_bank_code: str        # 입금 은행 코드
    to_account_number: str   # 입금 계좌번호
    amount: int
    description: str
    transfer_info_complete: bool
    transfer_confirmed: bool
    transfer_pin_verified: bool
```

---

## Node 구성
| 구분 | 노드 | 역할 |
| --- | --- | --- |
| 공통 | Initialize | user_profile + analysis_data 로드 |
| 공통 | Router | ASSET / STOCK / TRANSFER 의도 분류 |
| 공통 | Guard | 정책 기반 요청 차단 (guard_passed 설정) |
| 자산 | Asset_Flow | 자산 상담 서브그래프 (RAG_Consult → Asset_Action → Verifier → Executor) |
| 증권 | Stock_Flow | 증권 서브그래프 (Stock_Extract → Stock_Check → Verifier → Executor) |
| 이체 | Transfer_Flow | 이체 서브그래프 (Transfer_Extract → Transfer_Check → Verifier → Executor) |
| 저장 | Save_Memory | 대화 저장 + Vector DB 업데이트 |

---

## Edge
```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.agent.state import ChatAgentState
from src.agent.nodes.initialize import initialize_node
from src.agent.nodes.router import router_node
from src.agent.nodes.guard import guard_node
from src.agent.nodes.save_memory import save_memory_node
from src.agent.subgraphs import asset_graph, stock_graph, transfer_graph


def _route_after_guard(state: ChatAgentState) -> str:
    if not state.get("guard_passed", True):
        return "Save_Memory"
    return {
        "ASSET":    "Asset_Flow",
        "UNKNOWN":  "Asset_Flow",
        "STOCK":    "Stock_Flow",
        "TRANSFER": "Transfer_Flow",
    }.get(state.get("intent", "UNKNOWN"), "Save_Memory")


graph = StateGraph(ChatAgentState)

graph.add_node("Initialize", initialize_node)
graph.add_node("Router", router_node)
graph.add_node("Guard", guard_node)
graph.add_node("Asset_Flow", asset_graph)
graph.add_node("Stock_Flow", stock_graph)
graph.add_node("Transfer_Flow", transfer_graph)
graph.add_node("Save_Memory", save_memory_node)

graph.set_entry_point("Initialize")
graph.add_edge("Initialize", "Router")
graph.add_edge("Router", "Guard")

# Guard 분기: guard_passed=False → Save_Memory, 나머지 → 도메인 서브그래프
# UNKNOWN intent는 Asset_Flow로 라우팅
graph.add_conditional_edges(
    "Guard",
    _route_after_guard,
    {
        "Asset_Flow":    "Asset_Flow",
        "Stock_Flow":    "Stock_Flow",
        "Transfer_Flow": "Transfer_Flow",
        "Save_Memory":   "Save_Memory",
    },
)

graph.add_edge("Asset_Flow", "Save_Memory")
graph.add_edge("Stock_Flow", "Save_Memory")
graph.add_edge("Transfer_Flow", "Save_Memory")
graph.add_edge("Save_Memory", END)

chat_graph = graph.compile(checkpointer=MemorySaver())
```