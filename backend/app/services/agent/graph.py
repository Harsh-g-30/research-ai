from langgraph.graph import StateGraph, END
from app.services.agent.state import AgentState
from app.services.agent.nodes import (
    extract_intent,
    generate_search_queries,
    search_web,
    extract_products,
    rank_and_explain
)

def build_research_graph():
    """Build and compile the LangGraph research agent."""

    graph = StateGraph(AgentState)

    # Add all nodes
    graph.add_node("extract_intent", extract_intent)
    graph.add_node("generate_search_queries", generate_search_queries)
    graph.add_node("search_web", search_web)
    graph.add_node("extract_products", extract_products)
    graph.add_node("rank_and_explain", rank_and_explain)

    # Define the flow
    graph.set_entry_point("extract_intent")
    graph.add_edge("extract_intent", "generate_search_queries")
    graph.add_edge("generate_search_queries", "search_web")
    graph.add_edge("search_web", "extract_products")
    graph.add_edge("extract_products", "rank_and_explain")
    graph.add_edge("rank_and_explain", END)

    return graph.compile()

# Single instance
research_graph = build_research_graph()