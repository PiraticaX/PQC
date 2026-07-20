"""
QShield Enterprise
==================

FastAPI Application Entry Point.

Responsibilities
----------------
• Configure application logging
• Bootstrap database
• Initialize cache layer
• Register middleware
• Register API routes
• Manage application lifecycle
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.cache import close_cache, init_cache
from app.core.config import settings
from app.core.database import close_database
from app.core.logging import configure_logging, get_logger
from app.core.middleware import register_middleware
from app.database.bootstrap import startup_database

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

configure_logging()

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI application lifecycle.

    Startup
    -------
    1. Bootstrap database
    2. Initialize cache

    Shutdown
    --------
    1. Close cache
    2. Dispose database connections
    """

    logger.info("=" * 80)
    logger.info("Starting %s", settings.APP_NAME)
    logger.info("Version : %s", settings.APP_VERSION)
    logger.info("Environment : %s", settings.ENVIRONMENT)
    logger.info("=" * 80)

    try:
        # -------------------------------------------------------------
        # Database
        # -------------------------------------------------------------

        logger.info("Bootstrapping database...")

        await startup_database()

        logger.info("Database ready.")

        # -------------------------------------------------------------
        # Cache
        # -------------------------------------------------------------

        logger.info("Initializing cache...")

        await init_cache()

        logger.info("Cache ready.")

        logger.info("Application startup completed successfully.")

        yield

    except Exception:

        logger.exception(
            "Application startup failed."
        )

        raise

    finally:

        logger.info("=" * 80)
        logger.info("Stopping %s", settings.APP_NAME)
        logger.info("=" * 80)

        try:
            await close_cache()
        except Exception:
            logger.exception("Failed to shutdown cache.")

        try:
            await close_database()
        except Exception:
            logger.exception("Failed to shutdown database.")

        logger.info("Shutdown complete.")


# ---------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Post Quantum Cryptography Security Platform",
    debug=settings.DEBUG,
    lifespan=lifespan,
)


# ---------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------

register_middleware(app)


# ---------------------------------------------------------------------
# API
# ---------------------------------------------------------------------

app.include_router(api_router)


# ---------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------

@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint.
    """

    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "operational",
    }


@app.get("/health", tags=["System"])
async def health():
    """
    Health endpoint.
    """

    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


logger.info("QShield Enterprise application initialized.")