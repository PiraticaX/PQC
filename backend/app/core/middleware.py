"""
QShield Enterprise
==================

Application Middleware Infrastructure.

Responsibilities:

- Request tracing
- Request ID generation
- CORS configuration
- Security headers
- Request logging
- Response timing
- Error tracking

Integrates with:

- Logging Infrastructure
- Audit System
- Security Module
- Monitoring Layer

"""

from __future__ import annotations


import logging


import time


import uuid


from typing import Callable


from fastapi import FastAPI
from fastapi import Request


from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware


from starlette.responses import Response



from app.core.config import settings


from app.core.logging import get_logger


from app.core.security import security_headers



logger = get_logger(

    __name__

)



# ============================================================
# Request ID Middleware
# ============================================================


class RequestIDMiddleware(
    BaseHTTPMiddleware
):
    """
    Adds unique request identifier.

    Used for:

    - Distributed tracing
    - Debugging
    - Audit correlation

    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:


        request_id = str(

            uuid.uuid4()

        )


        request.state.request_id = request_id



        response = await call_next(

            request

        )



        response.headers[

            "X-Request-ID"

        ] = request_id



        return response



# ============================================================
# Request Logging Middleware
# ============================================================


class LoggingMiddleware(
    BaseHTTPMiddleware
):
    """
    Logs every API request.

    Captures:

    - Method
    - Path
    - Status
    - Duration

    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:


        start_time = time.perf_counter()



        response = await call_next(

            request

        )



        duration = (

            time.perf_counter()

            -

            start_time

        )



        logger.info(

            "API request completed",

            extra={

                "request_id":

                    getattr(

                        request.state,

                        "request_id",

                        None

                    ),


                "method":

                    request.method,


                "path":

                    request.url.path,


                "status_code":

                    response.status_code,


                "duration_ms":

                    round(

                        duration * 1000,

                        2

                    ),

            },

        )



        return response



# ============================================================
# Security Headers Middleware
# ============================================================


class SecurityHeadersMiddleware(
    BaseHTTPMiddleware
):
    """
    Adds security headers.

    Headers:

    - HSTS
    - XSS Protection
    - Frame Protection
    - Content Protection

    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:


        response = await call_next(

            request

        )



        headers = security_headers()



        for key, value in headers.items():

            response.headers[key] = value



        return response



# ============================================================
# Performance Middleware
# ============================================================


class PerformanceMiddleware(
    BaseHTTPMiddleware
):
    """
    API performance monitoring.

    Tracks:

    - Slow requests
    - Response latency

    """

    SLOW_REQUEST_THRESHOLD = 1.0



    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:


        start = time.time()



        response = await call_next(

            request

        )



        elapsed = (

            time.time()

            -

            start

        )



        if elapsed > self.SLOW_REQUEST_THRESHOLD:

            logger.warning(

                "Slow API request detected",

                extra={

                    "path":

                        request.url.path,


                    "duration":

                        elapsed,

                },

            )



        return response



# ============================================================
# Middleware Registration
# ============================================================


def register_middleware(
    app: FastAPI,
):
    """
    Register complete middleware stack.

    Order:

    1. CORS
    2. Request ID
    3. Logging
    4. Security Headers
    5. Performance

    """



    # --------------------------------------------------------
    # CORS
    # --------------------------------------------------------


    app.add_middleware(

        CORSMiddleware,

        allow_origins=
            settings.CORS_ORIGINS,

        allow_credentials=True,

        allow_methods=[

            "*"

        ],

        allow_headers=[

            "*"

        ],

    )



    # --------------------------------------------------------
    # Request Tracking
    # --------------------------------------------------------


    app.add_middleware(

        RequestIDMiddleware

    )



    # --------------------------------------------------------
    # Logging
    # --------------------------------------------------------


    app.add_middleware(

        LoggingMiddleware

    )



    # --------------------------------------------------------
    # Security
    # --------------------------------------------------------


    app.add_middleware(

        SecurityHeadersMiddleware

    )



    # --------------------------------------------------------
    # Performance
    # --------------------------------------------------------


    app.add_middleware(

        PerformanceMiddleware

    )



    logger.info(

        "Middleware stack initialized"

    )