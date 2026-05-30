from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.agent.state import ChatAgentState
from src.agent.nodes.initialize import initialize_node
from src.agent.nodes.router import router_node
from src.agent.nodes.rag_consult import rag_consult_node
from src.agent.nodes.asset_action import asset_action_node
from src.agent.nodes.stock_extract import stock_extract_node
from src.agent.nodes.stock_check import stock_check_node
from src.agent.nodes.transfer_extract import transfer_extract_node
from src.agent.nodes.transfer_check import transfer_check_node
from src.agent.nodes.verifier import verifier_node
from src.agent.nodes.executor import executor_node
from src.agent.nodes.save_memory import save_memory_node


def build_graph():
    graph = StateGraph(ChatAgentState)

    graph.add_node("Initialize", initialize_node)
    graph.add_node("Router", router_node)
    graph.add_node("RAG_Consult", rag_consult_node)
    graph.add_node("Asset_Action", asset_action_node)
    graph.add_node("Stock_Extract", stock_extract_node)
    graph.add_node("Stock_Check", stock_check_node)
    graph.add_node("Transfer_Extract", transfer_extract_node)
    graph.add_node("Transfer_Check", transfer_check_node)
    graph.add_node("Verifier", verifier_node)
    graph.add_node("Executor", executor_node)
    graph.add_node("Save_Memory", save_memory_node)

    graph.set_entry_point("Initialize")
    graph.add_edge("Initialize", "Router")

    graph.add_conditional_edges(
        "Router",
        lambda x: x["intent"],
        {
            "ASSET":    "RAG_Consult",
            "STOCK":    "Stock_Extract",
            "TRANSFER": "Transfer_Extract",
            "UNKNOWN":  "RAG_Consult",
        }
    )

    graph.add_edge("RAG_Consult", "Asset_Action")
    graph.add_conditional_edges(
        "Asset_Action",
        lambda x: "action" if x.get("pending_action") else "done",
        {"action": "Verifier", "done": "Save_Memory"}
    )

    graph.add_edge("Stock_Extract", "Stock_Check")
    graph.add_conditional_edges(
        "Stock_Check",
        lambda x: "done" if x.get("stock_info", {}).get("is_inquiry") else ("ready" if x.get("info_complete") else "more"),
        {"done": "Save_Memory", "ready": "Verifier", "more": "Stock_Extract"}
    )

    graph.add_edge("Transfer_Extract", "Transfer_Check")
    graph.add_conditional_edges(
        "Transfer_Check",
        lambda x: "ready" if x.get("transfer_info_complete") else "more",
        {"ready": "Verifier", "more": "Transfer_Extract"}
    )

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

    return graph.compile(
        checkpointer=MemorySaver(),
    )


chat_graph = build_graph()
