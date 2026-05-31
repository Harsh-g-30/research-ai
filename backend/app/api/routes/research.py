from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.schemas import ResearchRequest, ResearchResponse
from app.services.agent.graph import research_graph
from app.services.cache import get_cached, set_cache
from app.db.database import get_db, SearchHistory
from app.core.config import settings
import uuid

router = APIRouter()

@router.post("/", response_model=ResearchResponse)
async def research_products(request: ResearchRequest, db: Session = Depends(get_db)):
    try:
        # 1. Check Redis cache first
        cached = get_cached(request.query, request.filters or {})
        if cached:
            cached["cached"] = True
            return ResearchResponse(**cached)

        # 2. Run LangGraph agent
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

        search_id = str(uuid.uuid4())

        # 3. Save to PostgreSQL
        history = SearchHistory(
            id=search_id,
            user_id=None,
            query=request.query,
            category=result["category"],
            filters=request.filters or {},
            results=result["ranked_results"],
            summary=result["summary"]
        )
        db.add(history)
        db.commit()

        # 4. Build response
        response_data = {
            "id": search_id,
            "query": request.query,
            "category": result["category"],
            "filters_applied": result["filters"],
            "results": result["ranked_results"],
            "summary": result["summary"],
            "cached": False
        }

        # 5. Store in Redis cache
        set_cache(request.query, request.filters or {}, response_data)

        return ResearchResponse(**response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
def get_search_history(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent search history."""
    history = db.query(SearchHistory)\
        .order_by(SearchHistory.created_at.desc())\
        .limit(limit)\
        .all()
    return [
        {
            "id": h.id,
            "query": h.query,
            "category": h.category,
            "summary": h.summary,
            "created_at": h.created_at
        }
        for h in history
    ]


@router.post("/filters")
async def get_dynamic_filters(body: dict):
    from langchain_groq import ChatGroq
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
                    "unit": "INR/GB/inch/etc" or null
                }}
            ]
        }}""")
    ])

    response = llm.invoke(prompt.format_messages(query=query))
    try:
        return json.loads(response.content)
    except:
        return {"category": "general", "filters": []}