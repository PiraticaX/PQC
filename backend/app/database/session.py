"""
QShield Enterprise
==================

Database Session Management

This module provides:

- SQLAlchemy Declarative Base
- Session Factory
- Scoped database sessions
- FastAPI dependency injection
- Database initialization

Every ORM model in the application must inherit from Base.

Example
-------
from app.database.session import Base

class Asset(Base):
    __tablename__ = "assets"
"""

from __future__ import annotations

from sqlalchemy import text

from collections.abc import Generator

from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)

from app.core.logging import get_logger
from app.database.database import engine

logger = get_logger(__name__)


# -------------------------------------------------------------------------
# Base ORM Class
# -------------------------------------------------------------------------


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.

    Every database model must inherit from this class.
    """

    pass


# -------------------------------------------------------------------------
# Session Factory
# -------------------------------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)


# -------------------------------------------------------------------------
# Dependency Injection
# -------------------------------------------------------------------------


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency.

    Example
    -------

    @router.get("/assets")
    def list_assets(db: Session = Depends(get_db)):
        ...

    A new SQLAlchemy session is created for each request and
    automatically closed after the request finishes.
    """

    db = SessionLocal()

    try:
        yield db

    except Exception:
        logger.exception("Database session rolled back due to an exception.")
        db.rollback()
        raise

    finally:
        db.close()


# -------------------------------------------------------------------------
# Database Initialization
# -------------------------------------------------------------------------


def create_database() -> None:
    """
    Creates all database tables.

    During development this creates any tables that do not exist.

    Production deployments should use Alembic migrations instead.
    """

    logger.info("Creating database tables...")

    Base.metadata.create_all(bind=engine)

    logger.info("Database initialization complete.")


# -------------------------------------------------------------------------
# Health Check
# -------------------------------------------------------------------------


def check_database_connection() -> bool:
    """
    Verify database connectivity.

    Returns
    -------
    bool
        True if the database is reachable.
    """

    try:
        with engine.connect() as connection:
            connection.exec_driver_sql(text("SELECT 1"))

        return True

    except Exception:
        logger.exception("Database connectivity check failed.")
        return False