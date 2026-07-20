"""
Security Event Model
"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.mixins import (
    UUIDMixin,
    TimestampMixin,
)


class Event(
    UUIDMixin,
    TimestampMixin,
    Base,
):

    __tablename__ = "events"


    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


    severity: Mapped[str] = mapped_column(
        String(50),
        default="info",
    )


    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )