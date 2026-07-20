"""
QShield Enterprise

Webhook Model
"""

from __future__ import annotations


from sqlalchemy import (
    String,
    Boolean,
    Text,
)


from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)


from app.database.base import Base


from app.database.mixins import (
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
)



class Webhook(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):

    __tablename__ = "webhooks"


    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


    url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )


    secret: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )


    event_types: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )


    def disable(self):

        self.enabled = False