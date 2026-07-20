"""
QShield Enterprise

Scheduled Job Model
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



class ScheduledJob(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):

    __tablename__ = "scheduled_jobs"


    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


    schedule: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


    task_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )


    metadata_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )