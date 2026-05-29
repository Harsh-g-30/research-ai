from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from app.services.search.tavily_search import search_products
from app.services.agent.state import AgentState
import json
import uuid

# Init LLM
llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0.1
)

fast_llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model="llama-3.1-8b-instant",
    temperature=0.1
)

# ─── Node 1: Extract Intent ───────────────────────────────────────────────────
def extract_intent(state: AgentState) -> AgentState:
    print("🧠 Node 1: Extracting intent...")

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert at understanding product research queries.
        Extract structured information from the user query.
        Respond ONLY with valid JSON, no markdown, no explanation."""),
        ("human", """Query: {query}
        
        Return this exact JSON structure:
        {{
            "category": "laptop/smartphone/headphone/car/bike/tv/camera/etc",
            "use_case": "what they will use it for",
            "budget_min": null or number in INR,
            "budget_max": null or number in INR,
            "preferences": {{
                "brand_preference": [],
                "brand_avoid": [],
                "key_priorities": []
            }}
        }}""")
    ])

    response = fast_llm.invoke(prompt.format_messages(query=state["query"]))

    try:
        data = json.loads(response.content)
        state["category"] = data.get("category", "general")
        state["use_case"] = data.get("use_case", "")
        state["budget_min"] = data.get("budget_min")
        state["budget_max"] = data.get("budget_max")
        state["preferences"] = data.get("preferences", {})
    except Exception as e:
        print(f"Intent extraction error: {e}")
        state["category"] = "general"
        state["use_case"] = state["query"]
        state["preferences"] = {}

    print(f"   Category: {state['category']} | Use case: {state['use_case']}")
    return state


# ─── Node 2: Generate Search Queries ─────────────────────────────────────────
def generate_search_queries(state: AgentState) -> AgentState:
    print("🔍 Node 2: Generating search queries...")

    budget_str = ""
    if state.get("budget_max"):
        budget_str = f"under ₹{state['budget_max']}"

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Generate focused product research search queries. Respond ONLY with a JSON array of strings."),
        ("human", """Product category: {category}
        Use case: {use_case}
        Budget: {budget}
        User preferences: {preferences}
        Applied filters: {filters}
        
        Generate 4 targeted search queries to find the best products.
        Include queries for: best products, reviews, comparisons, and buying guides.
        Return ONLY a JSON array: ["query1", "query2", "query3", "query4"]""")
    ])

    response = fast_llm.invoke(prompt.format_messages(
        category=state["category"],
        use_case=state["use_case"],
        budget=budget_str,
        preferences=json.dumps(state.get("preferences", {})),
        filters=json.dumps(state.get("filters", {}))
    ))

    try:
        queries = json.loads(response.content)
        state["search_queries"] = queries
    except:
        state["search_queries"] = [
            f"best {state['category']} for {state['use_case']} {budget_str}",
            f"top {state['category']} recommendations {budget_str}",
            f"{state['category']} buying guide {state['use_case']}",
            f"{state['category']} comparison review 2024"
        ]

    print(f"   Queries: {state['search_queries']}")
    return state


# ─── Node 3: Search the Web ───────────────────────────────────────────────────
def search_web(state: AgentState) -> AgentState:
    print("🌐 Node 3: Searching the web...")

    results = search_products(state["search_queries"])
    state["raw_search_results"] = results

    print(f"   Found {len(results)} search result sets")
    return state


# ─── Node 4: Extract Products ─────────────────────────────────────────────────
def extract_products(state: AgentState) -> AgentState:
    print("📦 Node 4: Extracting product information...")

    # Combine all search content
    combined_content = ""
    source_urls = []

    for result_set in state["raw_search_results"]:
        combined_content += f"\nSearch: {result_set['query']}\n"
        combined_content += f"Answer: {result_set['answer']}\n"
        for r in result_set["results"]:
            combined_content += f"Source: {r.get('title', '')} - {r.get('content', '')[:300]}\n"
            source_urls.append(r.get("url", ""))

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a product research expert. Extract specific product recommendations from search results.
        Respond ONLY with valid JSON, no markdown."""),
        ("human", """Based on this search data, extract the top products for:
        Category: {category}
        Use case: {use_case}  
        Budget: {budget_min} to {budget_max} INR
        Filters applied: {filters}
        
        Search Results:
        {content}
        
        Return JSON array of up to 5 products:
        [{{
            "name": "Product Name",
            "brand": "Brand",
            "price": "₹XX,XXX",
            "specs": {{"key": "value"}},
            "pros": ["pro1", "pro2"],
            "cons": ["con1", "con2"],
            "score": 8.5,
            "reason": "Why this matches the user's needs",
            "source_urls": ["url1"]
        }}]""")
    ])

    response = llm.invoke(prompt.format_messages(
        category=state["category"],
        use_case=state["use_case"],
        budget_min=state.get("budget_min", "any"),
        budget_max=state.get("budget_max", "any"),
        filters=json.dumps(state.get("filters", {})),
        content=combined_content[:4000]
    ))

    try:
        products = json.loads(response.content)
        state["products"] = products
    except Exception as e:
        print(f"Product extraction error: {e}")
        state["products"] = []

    print(f"   Extracted {len(state['products'])} products")
    return state


# ─── Node 5: Rank & Explain ───────────────────────────────────────────────────
def rank_and_explain(state: AgentState) -> AgentState:
    print("🏆 Node 5: Ranking and explaining...")

    if not state["products"]:
        state["ranked_results"] = []
        state["summary"] = "No products found matching your criteria."
        return state

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert product advisor. Your job is to rank products 
        and write a genuinely helpful, specific summary tailored to the user's exact needs.
        Never write generic summaries. Always reference the user's specific use case, budget, 
        and priorities. Respond ONLY with valid JSON."""),
        ("human", """Rank these products for this specific user:
        
        Original Query: {query}
        Use case: {use_case}
        Budget: up to ₹{budget}
        Key priorities: {priorities}
        
        Products found: {products}
        
        Instructions:
        - Rank by best fit for THIS user's specific use case and budget
        - Update each product's "reason" to explain WHY it fits this user specifically
        - Update each product's "score" based on fit for this use case
        - Write a summary that mentions the #1 pick by name and explains the key tradeoff
        
        Return JSON:
        {{
            "ranked_products": [
                {{
                    "name": "product name",
                    "brand": "brand",
                    "price": "price",
                    "specs": {{}},
                    "pros": [],
                    "cons": [],
                    "score": 0.0,
                    "reason": "specific reason why this fits THIS user's needs",
                    "source_urls": []
                }}
            ],
            "summary": "2-3 sentence summary mentioning top pick by name, why it wins for this use case, and one key tradeoff to be aware of"
        }}""")
    ])

    response = llm.invoke(prompt.format_messages(
        query=state["query"],
        use_case=state["use_case"],
        budget=state.get("budget_max", "flexible"),
        priorities=json.dumps(state.get("preferences", {}).get("key_priorities", [])),
        products=json.dumps(state["products"])
    ))

    try:
        data = json.loads(response.content)
        state["ranked_results"] = data.get("ranked_products", state["products"])
        state["summary"] = data.get("summary", "")
    except Exception as e:
        print(f"Ranking error: {e}")
        state["ranked_results"] = state["products"]
        state["summary"] = "Here are the best matches for your query."

    print(f"   Ranked {len(state['ranked_results'])} products")
    return state