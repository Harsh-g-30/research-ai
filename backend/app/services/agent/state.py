from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    # Input
    query: str
    filters: Dict[str, Any]

    # Extracted intent
    category: str
    budget_min: Optional[float]
    budget_max: Optional[float]
    use_case: str
    preferences: Dict[str, Any]

    # Search
    search_queries: List[str]
    raw_search_results: List[Dict[str, Any]]

    # Processed
    products: List[Dict[str, Any]]
    embeddings_stored: bool

    # Output
    ranked_results: List[Dict[str, Any]]
    summary: str
    error: Optional[str]