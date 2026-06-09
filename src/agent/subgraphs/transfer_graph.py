from langgraph.graph import StateGraph, END

from src.agent.state import ChatAgentState
from src.agent.nodes.transfer_extract import transfer_extract_node
from src.agent.nodes.transfer_check import transfer_check_node
from src.agent.nodes.verifier import verifier_node
from src.agent.nodes.executor import executor_node


def build_transfer_graph():
    graph = StateGraph(ChatAgentState)

    graph.add_node("Transfer_Extract", transfer_extract_node)
    graph.add_node("Transfer_Check", transfer_check_node)
    graph.add_node("Verifier", verifier_node)
    graph.add_node("Executor", executor_node)

    graph.set_entry_point("Transfer_Extract")
    graph.add_edge("Transfer_Extract", "Transfer_Check")

    graph.add_conditional_edges(
        "Transfer_Check",
        lambda x: "ready" if x.get("transfer_info_complete") else "done",
        {"ready": "Verifier", "done": END},
    )

    graph.add_conditional_edges(
        "Verifier",
        lambda x: "ok" if x.get("transfer_pin_verified") else "fail",
        {"ok": "Executor", "fail": END},
    )

    graph.add_edge("Executor", END)

    return graph.compile()


transfer_graph = build_transfer_graph()
