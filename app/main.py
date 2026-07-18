"""
QShield Enterprise
==================

Application Entry Point.

Responsibilities:

- FastAPI application initialization
- Router registration
- Middleware registration
- Database lifecycle management
- Cache initialization
- Exception handling
- Event system initialization
- Health monitoring

"""

from __future__ import annotations


import logging


from contextlib import asynccontextmanager


from fastapi import FastAPI


from fastapi.middleware.gzip import GZipMiddleware



from app.core.config import settings


from app.core.database import init_database
from app.core.database import close_database


from app.core.cache import init_cache
from app.core.cache import close_cache


from app.core.middleware import register_middleware


from app.core.exceptions import register_exception_handlers


from app.core.logging import configure_logging


from app.core.events import event_bus_health



# ============================================================
# API Routers
# ============================================================


from app.api.router import router as api_router



# ============================================================
# Logging
# ============================================================


configure_logging()


logger = logging.getLogger(__name__)



# ============================================================
# Application Lifespan
# ============================================================


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    """
    Application lifecycle manager.

    Startup:

    - Database
    - Cache
    - Event systems

    Shutdown:

    - Database cleanup
    - Cache cleanup

    """

    logger.info(

        "Starting QShield Enterprise"

    )


    # -------------------------------
    # Startup
    # -------------------------------


    await init_database()


    await init_cache()



    logger.info(

        "QShield Enterprise started"

    )



    yield



    # -------------------------------
    # Shutdown
    # -------------------------------


    logger.info(

        "Stopping QShield Enterprise"

    )


    await close_cache()


    await close_database()



    logger.info(

        "Shutdown completed"

    )



# ============================================================
# FastAPI Application
# ============================================================


app = FastAPI(

    title=settings.APP_NAME,

    version=settings.APP_VERSION,

    description=

        """

        QShield Enterprise Security Platform.

        

        Capabilities:

        

        - Identity & Access Management

        - Post Quantum Cryptography

        - Risk Intelligence

        - Vulnerability Management

        - Compliance Automation

        - Security Analytics

        - Enterprise Reporting

        

        """,

    docs_url="/docs",

    redoc_url="/redoc",

    lifespan=lifespan,

)



# ============================================================
# Middleware Registration
# ============================================================


register_middleware(

    app

)



# Compression

app.add_middleware(

    GZipMiddleware,

    minimum_size=1000,

)



# ============================================================
# Exception Handling
# ============================================================


register_exception_handlers(

    app

)



# ============================================================
# API Routes
# ============================================================


app.include_router(

    api_router,

    prefix=settings.API_PREFIX,

)



# ============================================================
# Root Endpoint
# ============================================================


@app.get(
    "/",
)
async def root():
    """
    Root service information.
    """

    return {

        "application":

            settings.APP_NAME,


        "version":

            settings.APP_VERSION,


        "status":

            "operational",


        "environment":

            settings.ENVIRONMENT,

    }



# ============================================================
# Health Endpoint
# ============================================================


@app.get(
    "/health",
)
async def health():
    """
    Application health status.
    """

    return {

        "status":

            "healthy",


        "application":

            settings.APP_NAME,


        "version":

            settings.APP_VERSION,


        "components":

            {

                "api":

                    "healthy",


                "database":

                    "managed",


                "cache":

                    "managed",


                "events":

                    event_bus_health(),

            }

    }



# ============================================================
# Version Endpoint
# ============================================================


@app.get(
    "/version",
)
async def version():
    """
    Application version metadata.
    """

    return {

        "name":

            settings.APP_NAME,


        "version":

            settings.APP_VERSION,


        "api":

            settings.API_PREFIX,

    }



# ============================================================
# Development Runner
# ============================================================


if __name__ == "__main__":

    import uvicorn



    uvicorn.run(

        "app.main:app",

        host=settings.HOST,

        port=settings.PORT,

        reload=settings.DEBUG,

    )