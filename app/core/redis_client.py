from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

try:
    import redis as redis_lib
except Exception:
    redis_lib = None

if TYPE_CHECKING:
    from redis import Redis
from app.core.config import settings


@lru_cache
def get_redis_client() -> Redis | None:
    if not settings.REDIS_URL:
        return None

    if redis_lib is None:
        return None

    return redis_lib.Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=settings.REDIS_CONNECT_TIMEOUT_SECONDS,
        socket_timeout=settings.REDIS_SOCKET_TIMEOUT_SECONDS,
        health_check_interval=30,
        retry_on_timeout=True,
    )
