# LangGraph Agent

## ChatAgentState
```python
class ChatAgentState(TypedDict):
    # 공통
    user_id: str
    messages: list
    intent: str              # ASSET / STOCK / TRANSFER / UNKNOWN
    current_task: str

    # 자산관리
    rag_context: str         # Vector DB 검색 결과
    analysis_data: dict      # 분석 DB 분석 후 데이터
    realtime_data: dict      # 실시간 조회 운영 데이터 (잔액 등)
    recommended_ratio: dict  # 추천 자산 분배 비율
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
    raw_data: dict           # 동적 분석용 로우 데이터 (분석 후 None 처리)
    extra_analysis_data: dict  # 도출된 인사이트

    # 이체
    from_account_id: str
    to_account_id: str
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
| 자산 | RAG_Consult | 분석 리포트 + Vector 검색 → 금융 상담 |
| 자산 | Asset_Action | 분배 추천 pending_action 생성 |
| 증권 | Stock_Extract | 종목/수량 추출 + 정보 부족 시 질문 |
| 증권 | Stock_Check | 잔액/시세 조회 → 주문 가능 여부 확인 |
| 이체 | Transfer_Extract | 계좌/금액/메모 추출 |
| 이체 | Transfer_Check | 잔액/한도 조회 |
| 보안 | Verifier | Interrupt → PIN 입력 대기 |
| 실행 | Executor | 백엔드 API 호출 (이체/주문/설정변경) |
| 저장 | Save_Memory | 대화 저장 + Vector DB 업데이트 |

---

## Edge
```python
from langgraph.graph import StateGraph, END

graph = StateGraph(ChatAgentState)

graph.set_entry_point("Initialize")
graph.add_edge("Initialize", "Router")

# 라우터 분기
graph.add_conditional_edges(
    "Router",
    lambda x: x["intent"],
    {
        "ASSET":    "RAG_Consult",
        "STOCK":    "Stock_Extract",
        "TRANSFER": "Transfer_Extract",
        "UNKNOWN":  "Save_Memory"
    }
)

# 자산관리
graph.add_edge("RAG_Consult", "Asset_Action")
graph.add_conditional_edges(
    "Asset_Action",
    lambda x: "action" if x.get("pending_action") else "done",
    {"action": "Verifier", "done": "Save_Memory"}
)

# 증권
graph.add_edge("Stock_Extract", "Stock_Check")
graph.add_conditional_edges(
    "Stock_Check",
    lambda x: "ready" if x.get("info_complete") else "more",
    {"ready": "Verifier", "more": "Stock_Extract"}
)

# 이체
graph.add_edge("Transfer_Extract", "Transfer_Check")
graph.add_conditional_edges(
    "Transfer_Check",
    lambda x: "ready" if x.get("transfer_info_complete") else "more",
    {"ready": "Verifier", "more": "Transfer_Extract"}
)

# 보안 게이트
graph.add_conditional_edges(
    "Verifier",
    lambda x: "ok" if (
        x.get("stock_pin_verified") or
        x.get("transfer_pin_verified") or
        x.get("apply_pin_verified")
    ) else "fail",
    {"ok": "Executor", "fail": "Save_Memory"}
)

graph.add_edge("Executor", "Save_Memory")
graph.add_edge("Save_Memory", END)

app = graph.compile(
    checkpointer=memory,
    interrupt_before=["Verifier"]  # PIN 입력 전 대기
)
```