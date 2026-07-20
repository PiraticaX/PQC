"""
QShield Enterprise

Security Policy Model
"""

from __future__ import annotations


from sqlalchemy import (
    String,
    Text,
    Boolean,
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



class Policy(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):

    __tablename__ = "policies"


    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


    policy_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


    rules: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )


    def disable(self):

        self.enabled = False