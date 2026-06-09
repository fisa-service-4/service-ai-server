from langgraph.graph import StateGraph, END

from src.agent.state import ChatAgentState
from src.agent.nodes.stock_extract import stock_extract_node
from src.agent.nodes.stock_check import stock_check_node
from src.agent.nodes.verifier import verifier_node
from src.agent.nodes.executor import executor_node


def build_stock_graph():
    graph = StateGraph(ChatAgentState)

    graph.add_node("Stock_Extract", stock_extract_node)
    graph.add_node("Stock_Check", stock_check_node)
    graph.add_node("Verifier", verifier_node)
    graph.add_node("Executor", executor_node)

    graph.set_entry_point("Stock_Extract")
    graph.add_edge("Stock_Extract", "Stock_Check")

    graph.add_conditional_edges(
        "Stock_Check",
        lambda x: (
            "done" if (
                (x.get("stock_info") or {}).get("is_inquiry")
                or (x.get("stock_info") or {}).get("is_holdings")
            )
            else ("ready" if x.get("info_complete") else "more")
        ),
        {"done": END, "ready": "Verifier", "more": "Stock_Extract"},
    )

    graph.add_conditional_edges(
        "Verifier",
        lambda x: "ok" if x.get("stock_pin_verified") else "fail",
        {"ok": "Executor", "fail": END},
    )

    graph.add_edge("Executor", END)

    return graph.compile()


stock_graph = build_stock_graph()
