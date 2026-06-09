from langgraph.graph import StateGraph, END

from src.agent.state import ChatAgentState
from src.agent.nodes.rag_consult import rag_consult_node
from src.agent.nodes.asset_action import asset_action_node
from src.agent.nodes.verifier import verifier_node
from src.agent.nodes.executor import executor_node


def build_asset_graph():
    graph = StateGraph(ChatAgentState)

    graph.add_node("RAG_Consult", rag_consult_node)
    graph.add_node("Asset_Action", asset_action_node)
    graph.add_node("Verifier", verifier_node)
    graph.add_node("Executor", executor_node)

    graph.set_entry_point("RAG_Consult")
    graph.add_edge("RAG_Consult", "Asset_Action")

    graph.add_conditional_edges(
        "Asset_Action",
        lambda x: "action" if x.get("pending_action") else "done",
        {"action": "Verifier", "done": END},
    )

    graph.add_conditional_edges(
        "Verifier",
        lambda x: "ok" if x.get("apply_pin_verified") else "fail",
        {"ok": "Executor", "fail": END},
    )

    graph.add_edge("Executor", END)

    return graph.compile()


asset_graph = build_asset_graph()
