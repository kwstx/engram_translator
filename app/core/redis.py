from functools import lru_cache
import redis
from app.core.config import settings


@lru_cache
def get_redis_client() -> redis.Redis | None:
    if not settings.REDIS_URL:
        return None

    return redis.Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=settings.REDIS_CONNECT_TIMEOUT_SECONDS,
        socket_timeout=settings.REDIS_SOCKET_TIMEOUT_SECONDS,
        health_check_interval=30,
        retry_on_timeout=True,
    )
