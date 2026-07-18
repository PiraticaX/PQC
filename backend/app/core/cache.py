"""
QShield Enterprise
==================

Cache Infrastructure.

Responsibilities:

- Distributed caching
- Redis integration
- In-memory fallback cache
- TTL management
- Cache invalidation
- Response caching helpers

Supports:

- Redis
- Local memory cache
- Async operations

"""

from __future__ import annotations


import json


import logging


from datetime import datetime
from datetime import timedelta
from datetime import timezone


from typing import Any


from functools import wraps



from app.core.config import settings



logger = logging.getLogger(__name__)



# ============================================================
# Optional Redis Import
# ============================================================


try:

    import redis.asyncio as redis


    REDIS_AVAILABLE = True


except ImportError:

    REDIS_AVAILABLE = False



# ============================================================
# Memory Cache Fallback
# ============================================================


_memory_cache: dict[str, dict[str, Any]] = {}



# ============================================================
# Redis Client
# ============================================================


redis_client = None



async def init_cache():
    """
    Initialize cache backend.

    Uses:

    - Redis when available
    - Memory fallback

    """

    global redis_client


    if (

        settings.CACHE_ENABLED

        and REDIS_AVAILABLE

    ):

        try:

            redis_client = redis.from_url(

                settings.REDIS_URL,

                decode_responses=True,

            )


            await redis_client.ping()



            logger.info(

                "Redis cache initialized"

            )


        except Exception as exc:

            logger.warning(

                "Redis unavailable. Using memory cache. %s",

                exc,

            )


            redis_client = None



async def close_cache():
    """
    Close cache connections.
    """

    global redis_client


    if redis_client:

        await redis_client.close()



# ============================================================
# Cache Operations
# ============================================================


async def set_cache(
    key: str,
    value: Any,
    ttl: int | None = None,
):
    """
    Store value in cache.

    Args:

        key:
            Cache identifier

        value:
            Data object

        ttl:
            Expiration seconds

    """

    ttl = ttl or settings.CACHE_TIMEOUT



    serialized = json.dumps(

        value,

        default=str,

    )



    if redis_client:

        await redis_client.set(

            key,

            serialized,

            ex=ttl,

        )


        return



    _memory_cache[key] = {

        "value":

            serialized,


        "expires":

            datetime.now(

                timezone.utc

            )

            +

            timedelta(

                seconds=ttl

            )

    }



async def get_cache(
    key: str,
) -> Any | None:
    """
    Retrieve cached value.
    """

    if redis_client:

        value = await redis_client.get(

            key

        )


        if value:

            return json.loads(

                value

            )


        return None



    item = _memory_cache.get(

        key

    )


    if not item:

        return None



    if item["expires"] < datetime.now(

        timezone.utc

    ):

        del _memory_cache[key]


        return None



    return json.loads(

        item["value"]

    )



async def delete_cache(
    key: str,
):
    """
    Remove cache entry.
    """

    if redis_client:

        await redis_client.delete(

            key

        )

        return



    _memory_cache.pop(

        key,

        None

    )



async def clear_cache():
    """
    Clear all cache entries.
    """

    if redis_client:

        await redis_client.flushdb()

        return



    _memory_cache.clear()



# ============================================================
# Cache Decorator
# ============================================================


def cached(
    prefix: str,
    ttl: int | None = None,
):
    """
    Function result caching decorator.

    Example:

        @cached("users")
        async def get_users():
            ...

    """

    def decorator(func):

        @wraps(func)
        async def wrapper(
            *args,
            **kwargs
        ):

            key = (

                f"{prefix}:"

                +

                str(args)

                +

                str(kwargs)

            )



            cached_value = await get_cache(

                key

            )


            if cached_value is not None:

                return cached_value



            result = await func(

                *args,

                **kwargs

            )


            await set_cache(

                key,

                result,

                ttl,

            )



            return result



        return wrapper



    return decorator



# ============================================================
# Cache Namespaces
# ============================================================


class CacheKeys:
    """
    Standard cache key patterns.
    """

    USER = "user"

    ORGANIZATION = "organization"

    SESSION = "session"

    PERMISSION = "permission"

    ROLE = "role"

    API_KEY = "api_key"

    ASSET = "asset"

    RISK = "risk"

    REPORT = "report"

    CONFIG = "config"



# ============================================================
# Cache Health
# ============================================================


async def cache_health() -> dict[str, Any]:
    """
    Cache service health.
    """

    if redis_client:

        try:

            await redis_client.ping()


            return {

                "status":

                    "healthy",


                "backend":

                    "redis",

            }


        except Exception:

            pass



    return {

        "status":

            "healthy",


        "backend":

            "memory",

    }