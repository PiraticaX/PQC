"""
QShield Enterprise
==================

Queue Job Model

Tracks background jobs executed by workers.

Used for:

- Celery jobs
- Scheduler tasks
- Async processing
- Scan execution
- Report generation
"""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import (
    String,
    Text,
    Enum,
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


# ============================================================
# ENUMS
# ============================================================


class QueueJobStatus(str, enum.Enum):

    PENDING = "pending"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"



class QueueJobPriority(str, enum.Enum):

    LOW = "low"

    NORMAL = "normal"

    HIGH = "high"

    CRITICAL = "critical"



# ============================================================
# MODEL
# ============================================================


class QueueJob(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):

    """
    Background execution job.
    """

    __tablename__ = "queue_jobs"


    __table_args__ = (

        Index(
            "idx_queue_status",
            "status",
        ),

        Index(
            "idx_queue_type",
            "job_type",
        ),

    )


    # --------------------------------------------------------
    # Job Definition
    # --------------------------------------------------------


    job_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


    # --------------------------------------------------------
    # Execution
    # --------------------------------------------------------


    status: Mapped[QueueJobStatus] = mapped_column(
        Enum(QueueJobStatus),
        default=QueueJobStatus.PENDING,
        nullable=False,
    )


    priority: Mapped[QueueJobPriority] = mapped_column(
        Enum(QueueJobPriority),
        default=QueueJobPriority.NORMAL,
        nullable=False,
    )


    payload: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


    result: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


    # --------------------------------------------------------
    # Worker Information
    # --------------------------------------------------------


    worker_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )


    attempts: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )


    max_attempts: Mapped[int] = mapped_column(
        default=3,
        nullable=False,
    )


    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------


    def mark_running(self):

        self.status = QueueJobStatus.RUNNING


    def mark_completed(
        self,
        result: str | None = None,
    ):

        self.status = QueueJobStatus.COMPLETED
        self.result = result



    def mark_failed(
        self,
        error: str,
    ):

        self.status = QueueJobStatus.FAILED
        self.error_message = error



    def to_dict(self):

        return {

            "id": str(self.id),

            "job_type": self.job_type,

            "name": self.name,

            "status": self.status.value,

            "priority": self.priority.value,

        }