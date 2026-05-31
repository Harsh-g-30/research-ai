from sqlalchemy import create_engine, Column, String, Float, DateTime, JSON, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ── Tables ────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id       = Column(String, primary_key=True)
    name     = Column(String, nullable=False)
    email    = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SearchHistory(Base):
    __tablename__ = "search_history"

    id           = Column(String, primary_key=True)
    user_id      = Column(String, nullable=True)   # null = anonymous
    query        = Column(Text, nullable=False)
    category     = Column(String, nullable=True)
    filters      = Column(JSON, default={})
    results      = Column(JSON, default=[])
    summary      = Column(Text, nullable=True)
    created_at   = Column(DateTime, default=datetime.utcnow)

class SavedProduct(Base):
    __tablename__ = "saved_products"

    id         = Column(String, primary_key=True)
    user_id    = Column(String, nullable=False)
    name       = Column(String, nullable=False)
    brand      = Column(String, nullable=True)
    price      = Column(String, nullable=True)
    specs      = Column(JSON, default={})
    score      = Column(Float, nullable=True)
    reason     = Column(Text, nullable=True)
    saved_at   = Column(DateTime, default=datetime.utcnow)

# ── Dependency ────────────────────────────────────────────────────────────────

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)