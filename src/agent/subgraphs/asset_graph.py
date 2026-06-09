from langgraph.graph import StateGraph, END

from src.agent.state import ChatAgentState
from src.agent.nodes.rag_consult import rag_consult_node
from src.agent.nodes.asset_action import asset_action_node
from src.agent.nodes.verifier import verifier_node
from src.agent.nodes.executor import executor_node


def _route_after_asset_action(state: ChatAgentState) -> str:
    if state.get("pending_action"):
        return "Verifier"
    if state.get("asset_action_type") == "consult":
        return "RAG_Consult"
    return "done"


def build_asset_graph():
    graph = StateGraph(ChatAgentState)

    graph.add_node("Asset_Action", asset_action_node)
    graph.add_node("RAG_Consult", rag_consult_node)
    graph.add_node("Verifier", verifier_node)
    graph.add_node("Executor", executor_node)

    graph.set_entry_point("Asset_Action")

    graph.add_conditional_edges(
        "Asset_Action",
        _route_after_asset_action,
        {
            "Verifier":   "Verifier",
            "RAG_Consult": "RAG_Consult",
            "done":       END,
        },
    )

    graph.add_edge("RAG_Consult", END)

    graph.add_conditional_edges(
        "Verifier",
        lambda x: "ok" if x.get("apply_pin_verified") else "fail",
        {"ok": "Executor", "fail": END},
    )

    graph.add_edge("Executor", END)

    return graph.compile()


asset_graph = build_asset_graph()
