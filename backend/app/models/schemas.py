from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# ── Research ──────────────────────────────────────────────────────────────────

class ResearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = {}

class FilterOption(BaseModel):
    key: str
    label: str
    type: str
    options: Optional[List[str]] = None
    min: Optional[float] = None
    max: Optional[float] = None
    unit: Optional[str] = None

class FiltersResponse(BaseModel):
    category: str
    filters: List[FilterOption]

class ProductResult(BaseModel):
    name: str
    brand: Optional[str] = None
    price: Optional[str] = None
    specs: Optional[Dict[str, Any]] = {}
    pros: Optional[List[str]] = []
    cons: Optional[List[str]] = []
    score: Optional[float] = None
    reason: Optional[str] = None
    source_urls: Optional[List[str]] = []

class ResearchResponse(BaseModel):
    id: Optional[str] = None
    query: str
    category: str
    filters_applied: Dict[str, Any]
    results: List[ProductResult]
    summary: str
    cached: Optional[bool] = False

# ── Auth ──────────────────────────────────────────────────────────────────────

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

# ── History ───────────────────────────────────────────────────────────────────

class SearchHistoryItem(BaseModel):
    id: str
    query: str
    category: Optional[str]
    summary: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True