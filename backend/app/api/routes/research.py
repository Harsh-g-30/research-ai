from fastapi import APIRouter, HTTPException
from app.models.schemas import ResearchRequest, ResearchResponse
from app.services.agent.graph import research_graph
import uuid

router = APIRouter()

@router.post("/", response_model=ResearchResponse)
async def research_products(request: ResearchRequest):
    """Main research endpoint — runs the full LangGraph agent pipeline."""
    try:
        session_id = str(uuid.uuid4())

        # Run the LangGraph agent
        result = research_graph.invoke({
            "query": request.query,
            "filters": request.filters or {},
            "category": "",
            "budget_min": None,
            "budget_max": None,
            "use_case": "",
            "preferences": {},
            "search_queries": [],
            "raw_search_results": [],
            "products": [],
            "embeddings_stored": False,
            "ranked_results": [],
            "summary": "",
            "error": None
        })

        return ResearchResponse(
            query=request.query,
            category=result["category"],
            filters_applied=result["filters"],
            results=result["ranked_results"],
            summary=result["summary"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/filters")
async def get_dynamic_filters(body: dict):
    """Generate dynamic filters for a product category."""
    from langchain_groq import ChatGroq
    from app.core.config import settings
    from langchain_core.prompts import ChatPromptTemplate
    import json

    query = body.get("query", "")

    llm = ChatGroq(api_key=settings.GROQ_API_KEY, model="llama-3.1-8b-instant", temperature=0)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Generate dynamic UI filters for product research. Respond ONLY with valid JSON."),
        ("human", """Product query: {query}
        
        Generate relevant filters for this product category.
        Return JSON:
        {{
            "category": "detected category",
            "filters": [
                {{
                    "key": "filter_key",
                    "label": "Display Label",
                    "type": "range/select/multiselect/boolean",
                    "options": ["option1"] or null,
                    "min": 0 or null,
                    "max": 100000 or null,
                    "unit": "₹/GB/inch/etc" or null
                }}
            ]
        }}""")
    ])

    response = llm.invoke(prompt.format_messages(query=query))

    try:
        return json.loads(response.content)
    except:
        return {"category": "general", "filters": []}