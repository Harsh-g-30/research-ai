from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# --- Research Request ---
class ResearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = {}

# --- Filter Schema ---
class FilterOption(BaseModel):
    key: str
    label: str
    type: str        # "range", "select", "multiselect", "boolean"
    options: Optional[List[str]] = None
    min: Optional[float] = None
    max: Optional[float] = None
    unit: Optional[str] = None

class FiltersResponse(BaseModel):
    category: str
    filters: List[FilterOption]

# --- Product Result ---
class ProductResult(BaseModel):
    name: str
    brand: Optional[str]
    price: Optional[str]
    specs: Dict[str, Any]
    pros: List[str]
    cons: List[str]
    score: float
    reason: str
    source_urls: List[str]

# --- Research Response ---
class ResearchResponse(BaseModel):
    query: str
    category: str
    filters_applied: Dict[str, Any]
    results: List[ProductResult]
    summary: str

# --- Auth ---
class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str