"""
QShield Enterprise
==================

Scheduled Scan Model

Stores recurring scan schedules and execution metadata.

A scheduled scan defines when and how a scan should be executed
automatically.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base
from app.database.mixins import (
    TimestampMixin,
    UUIDMixin,
)
from app.database.types import GUID


# ============================================================
# ENUMS
# ============================================================


class ScheduleFrequency(str, enum.Enum):
    ONCE = "Once"
    HOURLY = "Hourly"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    CRON = "Cron"


class ScheduledScanStatus(str, enum.Enum):
    ACTIVE = "Active"
    PAUSED = "Paused"
    DISABLED = "Disabled"


# ============================================================
# MODEL
# ============================================================


class ScheduledScan(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    Automated scan schedule.
    """

    __tablename__ = "scheduled_scans"

    __table_args__ = (
        Index("idx_schedule_owner", "owner_id"),
        Index("idx_schedule_next_run", "next_run_at"),
        Index("idx_schedule_status", "status"),
    )

    # ============================================================
    # Relationships
    # ============================================================

    owner_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    asset_group_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey(
            "asset_groups.id",
            ondelete="SET NULL",
        ),
    )

    # ============================================================
    # Schedule
    # ============================================================

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
    )

    frequency: Mapped[ScheduleFrequency] = mapped_column(
        Enum(ScheduleFrequency),
        nullable=False,
    )

    cron_expression: Mapped[str | None] = mapped_column(
        String(128),
    )

    timezone: Mapped[str] = mapped_column(
        String(64),
        default="UTC",
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    status: Mapped[ScheduledScanStatus] = mapped_column(
        Enum(ScheduledScanStatus),
        default=ScheduledScanStatus.ACTIVE,
        nullable=False,
    )

    # ============================================================
    # Execution
    # ============================================================

    next_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    last_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    last_success_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    max_retries: Mapped[int] = mapped_column(
        Integer,
        default=3,
    )

    scan_configuration: Mapped[str | None] = mapped_column(
        Text,
    )

    # ============================================================
    # Relationships
    # ============================================================

    owner = relationship(
        "User",
        back_populates="scheduled_scans",
    )

    asset_group = relationship(
        "AssetGroup",
        back_populates="scheduled_scans",
    )
        # ============================================================
    # Helper Properties
    # ============================================================

    @property
    def is_active(self) -> bool:
        """
        Returns True when the schedule is enabled and active.
        """

        return (
            self.enabled
            and self.status == ScheduledScanStatus.ACTIVE
        )

    @property
    def can_retry(self) -> bool:
        """
        Returns True when additional retry attempts are available.
        """

        return self.retry_count < self.max_retries

    @property
    def is_due(self) -> bool:
        """
        Returns True when the scheduled execution time has arrived.
        """

        if not self.next_run_at:
            return False

        return (
            self.is_active
            and datetime.utcnow() >= self.next_run_at
        )

    @property
    def has_run(self) -> bool:
        """
        Returns True if the schedule has executed at least once.
        """

        return self.last_run_at is not None

    # ============================================================
    # Serialization
    # ============================================================

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "owner_id": str(self.owner_id),
            "asset_group_id": (
                str(self.asset_group_id)
                if self.asset_group_id
                else None
            ),
            "name": self.name,
            "description": self.description,
            "frequency": self.frequency.value,
            "cron_expression": self.cron_expression,
            "timezone": self.timezone,
            "enabled": self.enabled,
            "status": self.status.value,
            "next_run_at": (
                self.next_run_at.isoformat()
                if self.next_run_at
                else None
            ),
            "last_run_at": (
                self.last_run_at.isoformat()
                if self.last_run_at
                else None
            ),
            "last_success_at": (
                self.last_success_at.isoformat()
                if self.last_success_at
                else None
            ),
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "scan_configuration": self.scan_configuration,
            "is_active": self.is_active,
            "is_due": self.is_due,
            "has_run": self.has_run,
            "can_retry": self.can_retry,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            "<ScheduledScan("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"frequency='{self.frequency.value}', "
            f"status='{self.status.value}'"
            ")>"
        )