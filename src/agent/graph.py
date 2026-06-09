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


def build_graph():
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

    return graph.compile(checkpointer=MemorySaver())


chat_graph = build_graph()
