"""
Shared Redis connection, used both for pub/sub (real-time events)
and, later if needed, caching. One connection pool for the whole app.
"""
import redis.asyncio as aioredis
from app.core.config import settings

redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)