"""
Temporary compatibility layer.

New code should import from app.database.session instead.
"""

from app.database.database import engine
from app.database.session import (
    SessionLocal,
    get_db,
    check_database_connection,
)

def close_database() -> None:
    """Dispose database connections."""
    engine.dispose()