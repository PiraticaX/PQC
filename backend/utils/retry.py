"""
QShield Enterprise
==================

Retry Utilities.

Provides:

- Retry mechanisms
- Exponential backoff
- Async retry support
- Fault tolerance helpers

Used across:

- Workers
- Integrations
- External APIs
- Cloud services
"""

from __future__ import annotations


import asyncio


import functools


import logging


import time



from typing import Any
from typing import Callable
from typing import Type



logger = logging.getLogger(__name__)



# ============================================================
# Retry Configuration
# ============================================================


DEFAULT_RETRIES = 3


DEFAULT_DELAY_SECONDS = 1


DEFAULT_BACKOFF_FACTOR = 2



# ============================================================
# Sync Retry
# ============================================================


def retry(
    retries: int = DEFAULT_RETRIES,
    delay: float = DEFAULT_DELAY_SECONDS,
    backoff: float = DEFAULT_BACKOFF_FACTOR,
    exceptions: tuple[
        Type[Exception],
        ...
    ] = (Exception,),
):
    """
    Retry synchronous function.

    Example:

        @retry(retries=3)
        def call_api():
            ...

    """

    def decorator(
        func: Callable,
    ):

        @functools.wraps(

            func

        )
        def wrapper(
            *args,
            **kwargs,
        ):

            attempts = 0

            current_delay = delay



            while attempts < retries:

                try:

                    return func(

                        *args,

                        **kwargs,

                    )



                except exceptions as exc:

                    attempts += 1



                    logger.warning(

                        "Retry %s/%s failed for %s: %s",

                        attempts,

                        retries,

                        func.__name__,

                        exc,

                    )



                    if attempts >= retries:

                        raise



                    time.sleep(

                        current_delay

                    )



                    current_delay *= backoff



            return None



        return wrapper



    return decorator



# ============================================================
# Async Retry
# ============================================================


def async_retry(
    retries: int = DEFAULT_RETRIES,
    delay: float = DEFAULT_DELAY_SECONDS,
    backoff: float = DEFAULT_BACKOFF_FACTOR,
    exceptions: tuple[
        Type[Exception],
        ...
    ] = (Exception,),
):
    """
    Retry async coroutine.

    Example:

        @async_retry()
        async def fetch():

            ...

    """

    def decorator(
        func: Callable,
    ):

        @functools.wraps(

            func

        )
        async def wrapper(
            *args,
            **kwargs,
        ):

            attempts = 0

            current_delay = delay



            while attempts < retries:

                try:

                    return await func(

                        *args,

                        **kwargs,

                    )



                except exceptions as exc:

                    attempts += 1



                    logger.warning(

                        "Async retry %s/%s failed for %s: %s",

                        attempts,

                        retries,

                        func.__name__,

                        exc,

                    )



                    if attempts >= retries:

                        raise



                    await asyncio.sleep(

                        current_delay

                    )



                    current_delay *= backoff



            return None



        return wrapper



    return decorator



# ============================================================
# Manual Retry Executor
# ============================================================


def execute_with_retry(
    function: Callable,
    retries: int = DEFAULT_RETRIES,
    *args,
    **kwargs,
) -> Any:
    """
    Execute function with retry.

    """

    attempt = 0



    while attempt < retries:

        try:

            return function(

                *args,

                **kwargs,

            )



        except Exception:

            attempt += 1



            if attempt >= retries:

                raise



    return None



# ============================================================
# Async Executor
# ============================================================


async def execute_async_with_retry(
    function: Callable,
    retries: int = DEFAULT_RETRIES,
    *args,
    **kwargs,
) -> Any:
    """
    Execute async function with retry.

    """

    attempt = 0



    while attempt < retries:

        try:

            return await function(

                *args,

                **kwargs,

            )



        except Exception:

            attempt += 1



            if attempt >= retries:

                raise



            await asyncio.sleep(

                2 ** attempt

            )



    return None