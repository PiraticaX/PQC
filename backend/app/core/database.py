"""
QShield Enterprise
==================

Database Infrastructure.

Responsibilities:

- Async database engine creation
- Session management
- SQLAlchemy base declaration
- Transaction handling
- Database health checks
- Connection lifecycle management

Technology:

- SQLAlchemy 2.x
- AsyncIO
- Async database drivers

"""

from __future__ import annotations


import logging


from contextlib import asynccontextmanager


from typing import AsyncGenerator


from sqlalchemy import text


from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine


from sqlalchemy.orm import DeclarativeBase



from app.core.config import settings



logger = logging.getLogger(__name__)



# ============================================================
# Database Base
# ============================================================


class Base(
    DeclarativeBase
):
    """
    SQLAlchemy declarative base.

    All database models inherit from this class.

    Example:

        class User(Base):
            ...

    """

    pass



# ============================================================
# Engine Configuration
# ============================================================


def create_database_engine() -> AsyncEngine:
    """
    Create async database engine.

    Supports:

    - PostgreSQL
    - SQLite
    - MySQL compatible async drivers

    """

    connect_args = {}


    if settings.DATABASE_URL.startswith(
        "sqlite"
    ):

        connect_args = {

            "check_same_thread": False

        }



    return create_async_engine(

        settings.DATABASE_URL,

        echo=settings.DEBUG,

        pool_pre_ping=True,

        pool_size=settings.DATABASE_POOL_SIZE
        if "sqlite" not in settings.DATABASE_URL
        else 5,

        max_overflow=settings.DATABASE_MAX_OVERFLOW
        if "sqlite" not in settings.DATABASE_URL
        else 0,

        connect_args=connect_args,

    )



# ============================================================
# Global Engine
# ============================================================


engine: AsyncEngine = create_database_engine()



# ============================================================
# Session Factory
# ============================================================


AsyncSessionLocal = async_sessionmaker(

    bind=engine,

    class_=AsyncSession,

    expire_on_commit=False,

    autoflush=False,

    autocommit=False,

)



# ============================================================
# FastAPI Dependency
# ============================================================


async def get_db():
    AsyncGenerator[AsyncSession, None]
    """
    Provide database session.

    Usage:

        db: AsyncSession = Depends(get_db)

    """

    async with AsyncSessionLocal() as session:

        try:

            yield session


        except Exception:

            await session.rollback()

            raise


        finally:

            await session.close()



# ============================================================
# Transaction Helper
# ============================================================


@asynccontextmanager
async def transaction(
    session: AsyncSession
):
    """
    Database transaction context.

    Example:

        async with transaction(db):
            db.add(object)

    """

    try:

        async with session.begin():

            yield session


    except Exception:

        await session.rollback()

        raise



# ============================================================
# Database Health
# ============================================================


async def check_database_health():
    dict
    """
    Check database connectivity.
    """

    try:

        async with engine.connect() as connection:

            await connection.execute(

                text(
                    "SELECT 1"
                )

            )


        return {

            "status":

                "healthy",


            "database":

                "connected",

        }


    except Exception as exc:

        logger.exception(

            "Database health check failed"

        )


        return {

            "status":

                "unhealthy",


            "database":

                "disconnected",


            "error":

                str(exc),

        }



# ============================================================
# Startup / Shutdown
# ============================================================


async def init_database():
    """
    Initialize database resources.

    Production migrations should be handled by:

    - Alembic
    - Migration pipeline

    """

    logger.info(

        "Database initialized"

    )



async def close_database():
    """
    Close database connections.
    """

    await engine.dispose()


    logger.info(

        "Database connections closed"

    )