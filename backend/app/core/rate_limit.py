"""
QShield Enterprise
==================

Rate Limiting Infrastructure.

Responsibilities:

- API request throttling
- User based rate limiting
- IP based rate limiting
- Redis distributed counters
- In-memory fallback
- Endpoint protection
- Abuse prevention

Supports:

- Redis backend
- Local memory fallback

"""

from __future__ import annotations


import logging


import time


from collections import defaultdict


from functools import wraps


from typing import Callable, Any



from fastapi import HTTPException
from fastapi import Request
from fastapi import status



from app.core.config import settings


from app.core.cache import get_cache
from app.core.cache import set_cache



logger = logging.getLogger(__name__)



# ============================================================
# Memory Rate Limit Store
# ============================================================


_rate_store: dict[str, list[float]] = defaultdict(

    list

)



# ============================================================
# Key Generation
# ============================================================


def generate_rate_key(
    identifier: str,
    endpoint: str | None = None,
) -> str:
    """
    Generate rate limit key.

    Examples:

        ip:127.0.0.1:/login

        user:123:/api

    """

    if endpoint:

        return f"rate:{identifier}:{endpoint}"


    return f"rate:{identifier}"



# ============================================================
# Core Rate Limiter
# ============================================================


async def check_rate_limit(
    key: str,
    limit: int | None = None,
    window: int | None = None,
) -> bool:
    """
    Check if request is allowed.

    Returns:

    True  -> allowed

    False -> blocked

    """

    if not settings.RATE_LIMIT_ENABLED:

        return True



    limit = (

        limit

        or

        settings.RATE_LIMIT_REQUESTS

    )


    window = (

        window

        or

        settings.RATE_LIMIT_WINDOW_SECONDS

    )



    now = time.time()



    # --------------------------------------------------------
    # Redis based limiter
    # --------------------------------------------------------


    cached = await get_cache(

        key

    )



    if cached is not None:

        timestamps = cached


    else:

        timestamps = []



    timestamps = [

        timestamp

        for timestamp in timestamps

        if now - timestamp < window

    ]



    if len(timestamps) >= limit:

        return False



    timestamps.append(

        now

    )



    await set_cache(

        key,

        timestamps,

        ttl=window,

    )



    return True



# ============================================================
# Request Identifier
# ============================================================


def get_client_identifier(
    request: Request,
) -> str:
    """
    Extract client identifier.

    Priority:

    1. Authenticated user
    2. API key
    3. IP address

    """

    user = getattr(

        request.state,

        "user",

        None

    )


    if user:

        return f"user:{user.id}"



    api_key = request.headers.get(

        "X-API-Key"

    )


    if api_key:

        return f"api:{api_key[:10]}"



    return (

        f"ip:{request.client.host}"

        if request.client

        else

        "unknown"

    )



# ============================================================
# FastAPI Dependency
# ============================================================


async def rate_limit(
    request: Request,
    limit: int | None = None,
    window: int | None = None,
):
    """
    FastAPI rate limiting dependency.

    Usage:

        Depends(rate_limit)

    """

    identifier = get_client_identifier(

        request

    )


    key = generate_rate_key(

        identifier,

        request.url.path,

    )



    allowed = await check_rate_limit(

        key,

        limit,

        window,

    )



    if not allowed:

        logger.warning(

            "Rate limit exceeded",

            extra={

                "identifier":

                    identifier,


                "endpoint":

                    request.url.path,

            },

        )


        raise HTTPException(

            status_code=

                status.HTTP_429_TOO_MANY_REQUESTS,

            detail=

                "Too many requests. Please try again later.",

        )



    return True



# ============================================================
# Decorator
# ============================================================


def rate_limited(
    limit: int = 100,
    window: int = 60,
):
    """
    Decorator for service functions.

    Example:

        @rate_limited(
            10,
            60
        )

    """

    def decorator(
        func: Callable
    ):

        @wraps(func)
        async def wrapper(
            *args,
            **kwargs
        ):

            identifier = str(

                kwargs.get(

                    "user_id",

                    "system"

                )

            )


            key = generate_rate_key(

                identifier,

                func.__name__,

            )



            allowed = await check_rate_limit(

                key,

                limit,

                window,

            )



            if not allowed:

                raise HTTPException(

                    status_code=429,

                    detail=

                    "Rate limit exceeded.",

                )



            return await func(

                *args,

                **kwargs

            )


        return wrapper


    return decorator



# ============================================================
# Predefined Policies
# ============================================================


class RateLimitPolicies:
    """
    Standard enterprise policies.
    """

    LOGIN = {

        "limit":

            5,

        "window":

            60,

    }


    API = {

        "limit":

            100,

        "window":

            60,

    }


    PASSWORD_RESET = {

        "limit":

            3,

        "window":

            300,

    }


    KEY_OPERATIONS = {

        "limit":

            10,

        "window":

            60,

    }



# ============================================================
# Health Check
# ============================================================


async def rate_limit_health() -> dict[str, Any]:
    """
    Rate limiter health.
    """

    return {

        "status":

            "healthy",


        "enabled":

            settings.RATE_LIMIT_ENABLED,


        "backend":

            "redis_or_memory",

    }