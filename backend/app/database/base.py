"""Compatibility export for the application's single declarative base."""

from app.database.session import Base

__all__ = ["Base"]
