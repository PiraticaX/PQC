"""
QShield Enterprise
==================

Decorator Utilities.

Provides:

- Function logging
- Execution timing
- Authentication wrappers
- Permission checks
- Role validation
- Async support

Used across:

- APIs
- Services
- Workers
- Security modules
"""

from __future__ import annotations


import functools


import logging


import time



from typing import Callable
from typing import Any



logger = logging.getLogger(__name__)



# ============================================================
# Logging Decorator
# ============================================================


def log_execution(
):
    """
    Log function execution.

    Example:

        @log_execution
        def process():
            ...

    """

    def decorator(
        func: Callable,
    ):

        @functools.wraps(

            func

        )
        async def async_wrapper(
            *args,
            **kwargs,
        ):

            logger.info(

                "Executing %s",

                func.__name__,

            )


            result = await func(

                *args,

                **kwargs,

            )


            logger.info(

                "Completed %s",

                func.__name__,

            )


            return result



        @functools.wraps(

            func

        )
        def sync_wrapper(
            *args,
            **kwargs,
        ):

            logger.info(

                "Executing %s",

                func.__name__,

            )


            result = func(

                *args,

                **kwargs,

            )


            logger.info(

                "Completed %s",

                func.__name__,

            )


            return result



        if _is_async(

            func

        ):

            return async_wrapper



        return sync_wrapper



    return decorator



# ============================================================
# Timing Decorator
# ============================================================


def measure_time(
):
    """
    Measure execution duration.

    """

    def decorator(
        func: Callable,
    ):

        @functools.wraps(

            func

        )
        async def async_wrapper(
            *args,
            **kwargs,
        ):

            start = time.time()



            result = await func(

                *args,

                **kwargs,

            )



            duration = time.time() - start



            logger.debug(

                "%s executed in %.4fs",

                func.__name__,

                duration,

            )


            return result



        @functools.wraps(

            func

        )
        def sync_wrapper(
            *args,
            **kwargs,
        ):

            start = time.time()



            result = func(

                *args,

                **kwargs,

            )



            duration = time.time() - start



            logger.debug(

                "%s executed in %.4fs",

                func.__name__,

                duration,

            )


            return result



        if _is_async(

            func

        ):

            return async_wrapper



        return sync_wrapper



    return decorator



# ============================================================
# Authentication Decorator
# ============================================================


def require_auth(
):
    """
    Require authenticated user.

    Expects:

        kwargs["current_user"]

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

            user = kwargs.get(

                "current_user"

            )



            if not user:

                raise PermissionError(

                    "Authentication required"

                )



            return await func(

                *args,

                **kwargs,

            )



        return wrapper



    return decorator



# ============================================================
# Permission Decorator
# ============================================================


def require_permission(
    permission: str,
):
    """
    Validate user permission.

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

            user = kwargs.get(

                "current_user"

            )



            if not user:

                raise PermissionError(

                    "Authentication required"

                )



            permissions = getattr(

                user,

                "permissions",

                [],

            )



            if permission not in permissions:

                raise PermissionError(

                    "Permission denied"

                )



            return await func(

                *args,

                **kwargs,

            )



        return wrapper



    return decorator



# ============================================================
# Role Decorator
# ============================================================


def require_role(
    role: str,
):
    """
    Validate user role.

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

            user = kwargs.get(

                "current_user"

            )



            roles = getattr(

                user,

                "roles",

                [],

            )



            if role not in roles:

                raise PermissionError(

                    "Role access denied"

                )



            return await func(

                *args,

                **kwargs,

            )



        return wrapper



    return decorator



# ============================================================
# Internal Helpers
# ============================================================


def _is_async(
    func: Callable,
) -> bool:
    """
    Check coroutine function.

    """

    import inspect


    return inspect.iscoroutinefunction(

        func

    )