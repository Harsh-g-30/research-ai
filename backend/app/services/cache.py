import redis
import json
import hashlib
from app.core.config import settings

# Connect to Redis
try:
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
    r.ping()
    print("✅ Redis connected")
except Exception as e:
    print(f"⚠️ Redis not available: {e}")
    r = None

CACHE_TTL = 60 * 60 * 24  # 24 hours

def make_cache_key(query: str, filters: dict) -> str:
    """Create a unique cache key from query + filters."""
    raw = f"{query.lower().strip()}:{json.dumps(filters, sort_keys=True)}"
    return f"research:{hashlib.md5(raw.encode()).hexdigest()}"

def get_cached(query: str, filters: dict):
    """Return cached result or None."""
    if not r:
        return None
    try:
        key = make_cache_key(query, filters)
        data = r.get(key)
        if data:
            print(f"⚡ Cache HIT for: {query[:50]}")
            return json.loads(data)
    except Exception as e:
        print(f"Cache get error: {e}")
    return None

def set_cache(query: str, filters: dict, result: dict):
    """Store result in Redis for 24 hours."""
    if not r:
        return
    try:
        key = make_cache_key(query, filters)
        r.setex(key, CACHE_TTL, json.dumps(result))
        print(f"💾 Cached result for: {query[:50]}")
    except Exception as e:
        print(f"Cache set error: {e}")

def clear_cache():
    """Clear all research cache keys."""
    if not r:
        return
    keys = r.keys("research:*")
    if keys:
        r.delete(*keys)
    print(f"🗑️ Cleared {len(keys)} cache entries")