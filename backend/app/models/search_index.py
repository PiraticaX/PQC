"""
QShield Enterprise

Search Index Model
"""

from __future__ import annotations


import uuid


from sqlalchemy import (
    String,
    Text,
    Index,
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



class SearchIndex(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):

    __tablename__ = "search_indexes"


    __table_args__ = (

        Index(
            "idx_search_entity",
            "entity_type",
        ),

    )


    entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


    entity_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False,
    )


    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )