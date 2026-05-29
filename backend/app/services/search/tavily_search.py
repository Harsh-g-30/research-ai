from tavily import TavilyClient
from app.core.config import settings

client = TavilyClient(api_key=settings.TAVILY_API_KEY)

def search_products(queries: list[str]) -> list[dict]:
    """Run multiple search queries and return combined results."""
    all_results = []

    for query in queries:
        try:
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=5,
                include_answer=True
            )
            all_results.append({
                "query": query,
                "answer": response.get("answer", ""),
                "results": response.get("results", [])
            })
        except Exception as e:
            print(f"Search error for '{query}': {e}")

    return all_results