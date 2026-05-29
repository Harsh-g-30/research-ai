from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import research, auth

app = FastAPI(
    title="ResearchAI API",
    description="AI-powered product research platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research.router, prefix="/api/research", tags=["Research"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])

@app.get("/")
def root():
    return {"status": "ResearchAI is running 🚀"}

@app.get("/health")
def health():
    return {"status": "healthy"}