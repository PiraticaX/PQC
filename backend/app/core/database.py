"""
Temporary compatibility layer.

New code should import from app.database.session instead.
"""

from app.database.database import engine
from app.database.session import (
    SessionLocal,
    get_db,
)


def check_database_connection() -> bool:
    """Verify that the synchronous database engine can execute a query."""
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
        return True
    except Exception:
        return False


def close_database() -> None:
    """Dispose database connections."""
    engine.dispose()
