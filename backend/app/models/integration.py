"""
External Integration Model
"""

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.mixins import (
    UUIDMixin,
    TimestampMixin,
)


class Integration(
    UUIDMixin,
    TimestampMixin,
    Base,
):

    __tablename__ = "integrations"


    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )