"""
QShield Enterprise
==================

Scan Service

Business logic layer for managing security scans.

This service is independent from FastAPI and can be used by:

- REST API
- Background workers
- Celery tasks
- Scanner orchestrator
- Scheduler
- CLI tools
- Automated pipelines

Responsibilities
-----------------

• Scan creation
• Scan lifecycle management
• Scanner coordination
• Status tracking
• Statistics
• Pagination
• Filtering
• Reporting integration

Author:
QShield Enterprise
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.scan import Scan
from app.models.scan import ScanEngine
from app.models.scan import ScanStatus
from app.models.scan import ScanTrigger

from app.schemas.scan import (
    ScanCreate,
    ScanDashboard,
    ScanListResponse,
    ScanResponse,
    ScanSummary,
    ScanUpdate,
)


logger = logging.getLogger(__name__)


class ScanService:
    """
    Enterprise Scan Service.

    Handles complete scan lifecycle:

    PENDING
        |
        v
    QUEUED
        |
        v
    RUNNING
        |
        +------------+
        |            |
        v            v
    COMPLETED     FAILED
    """


    def __init__(
        self,
        db: Session,
    ):
        self.db = db


    # ============================================================
    # Validation Helpers
    # ============================================================

    @staticmethod
    def normalize_configuration(
        configuration: dict[str, Any] | None,
    ) -> str | None:
        """
        Normalize scan configuration.

        Stored as serialized JSON string.
        """

        if configuration is None:
            return None

        import json

        return json.dumps(
            configuration,
            sort_keys=True,
        )


    @staticmethod
    def calculate_duration(
        started_at: datetime | None,
        completed_at: datetime | None,
    ) -> float | None:
        """
        Calculate scan execution duration.
        """

        if not started_at or not completed_at:
            return None

        return (
            completed_at - started_at
        ).total_seconds()


    async def asset_exists(
        self,
        asset_id: UUID,
    ) -> bool:
        """
        Verify asset exists.
        """

        stmt = (
            select(func.count())
            .select_from(Asset)
            .where(
                Asset.id == asset_id,
                Asset.deleted_at.is_(None),
            )
        )

        count = self.db.scalar(
            stmt,
        )

        return bool(count)
        # ============================================================
    # Database Helpers
    # ============================================================

    async def get_scan_model(
        self,
        scan_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> Scan | None:
        """
        Retrieve Scan ORM object.

        Parameters
        ----------
        scan_id:
            Scan UUID.

        include_deleted:
            Include soft deleted scans.
        """

        stmt = (
            select(Scan)
            .where(
                Scan.id == scan_id,
            )
        )

        if not include_deleted:
            stmt = stmt.where(
                Scan.deleted_at.is_(None),
            )

        result = self.db.execute(
            stmt,
        )

        return result.scalar_one_or_none()


    async def get_asset_model(
        self,
        asset_id: UUID,
    ) -> Asset | None:
        """
        Retrieve related asset.
        """

        stmt = (
            select(Asset)
            .where(
                Asset.id == asset_id,
                Asset.deleted_at.is_(None),
            )
        )

        result = self.db.execute(
            stmt,
        )

        return result.scalar_one_or_none()


    async def scan_exists(
        self,
        asset_id: UUID,
        *,
        status: ScanStatus | None = None,
    ) -> bool:
        """
        Check whether a scan exists for an asset.

        Optional status filter can be used to check
        active scans.
        """

        filters = [
            Scan.asset_id == asset_id,
            Scan.deleted_at.is_(None),
        ]

        if status:
            filters.append(
                Scan.status == status,
            )

        stmt = (
            select(func.count())
            .select_from(Scan)
            .where(
                *filters,
            )
        )

        count = self.db.scalar(
            stmt,
        )

        return bool(count)


    async def active_scan_exists(
        self,
        asset_id: UUID,
    ) -> bool:
        """
        Check if asset already has a running scan.
        """

        return await self.scan_exists(
            asset_id,
            status=ScanStatus.RUNNING,
        )


    async def commit(
        self,
    ) -> None:
        """
        Commit transaction safely.
        """

        try:

            self.db.commit()

        except Exception:

            self.db.rollback()

            logger.exception(
                "Database commit failed."
            )

            raise
            # ============================================================
    # Serialization Helpers
    # ============================================================

    @staticmethod
    def _summary(
        scan: Scan,
    ) -> ScanSummary:
        """
        Convert Scan ORM object into lightweight response.
        """

        return ScanSummary(

            id=scan.id,

            created_at=scan.created_at,

            updated_at=scan.updated_at,

            asset_id=scan.asset_id,

            status=scan.status,

            trigger=scan.trigger,

            engine=scan.engine,

            started_at=scan.started_at,

            completed_at=scan.completed_at,

            duration_seconds=(
                scan.duration_seconds
            ),

            total_findings=(
                scan.total_findings
            ),

            critical_findings=(
                scan.critical_findings
            ),

            high_findings=(
                scan.high_findings
            ),

            medium_findings=(
                scan.medium_findings
            ),

            low_findings=(
                scan.low_findings
            ),

        )


    @staticmethod
    def _response(
        scan: Scan,
    ) -> ScanResponse:
        """
        Convert Scan ORM object into full API response.
        """

        return ScanResponse(

            id=scan.id,

            created_at=scan.created_at,

            updated_at=scan.updated_at,

            asset_id=scan.asset_id,

            status=scan.status,

            trigger=scan.trigger,

            engine=scan.engine,

            queued_at=scan.queued_at,

            started_at=scan.started_at,

            completed_at=scan.completed_at,

            duration_seconds=(
                scan.duration_seconds
            ),

            worker_name=(
                scan.worker_name
            ),

            worker_version=(
                scan.worker_version
            ),

            configuration=(
                scan.configuration
            ),

            error_message=(
                scan.error_message
            ),

            total_findings=(
                scan.total_findings
            ),

            critical_findings=(
                scan.critical_findings
            ),

            high_findings=(
                scan.high_findings
            ),

            medium_findings=(
                scan.medium_findings
            ),

            low_findings=(
                scan.low_findings
            ),

            informational_findings=(
                scan.informational_findings
            ),
        )


    @staticmethod
    def serialize_collection(
        scans: list[Scan],
    ) -> list[ScanSummary]:
        """
        Convert list of scans into summaries.
        """

        return [
            ScanService._summary(
                scan,
            )
            for scan in scans
        ]


    # ============================================================
    # Validation
    # ============================================================

    @staticmethod
    def validate_engine(
        engine: ScanEngine,
    ) -> None:
        """
        Validate scanner engine.
        """

        if engine not in ScanEngine:
            raise ValueError(
                "Unsupported scan engine."
            )


    @staticmethod
    def validate_trigger(
        trigger: ScanTrigger,
    ) -> None:
        """
        Validate scan trigger.
        """

        if trigger not in ScanTrigger:
            raise ValueError(
                "Unsupported scan trigger."
            )
            # ============================================================
    # Create Scan
    # ============================================================

    async def create_scan(
        self,
        payload: ScanCreate,
    ) -> ScanResponse:
        """
        Create a new scan execution.

        Workflow
        --------

        1. Validate asset
        2. Validate scanner configuration
        3. Prevent duplicate active scans
        4. Create scan in PENDING state
        5. Return scan metadata
        """

        if not await self.asset_exists(
            payload.asset_id,
        ):
            raise ValueError(
                "Asset does not exist."
            )


        self.validate_engine(
            payload.engine,
        )

        self.validate_trigger(
            payload.trigger,
        )


        if await self.active_scan_exists(
            payload.asset_id,
        ):
            raise ValueError(
                "A scan is already running for this asset."
            )


        scan = Scan(

            asset_id=payload.asset_id,

            status=ScanStatus.PENDING,

            trigger=payload.trigger,

            engine=payload.engine,

            description=getattr(
                payload,
                "description",
                None,
            ),

            configuration=(
                self.normalize_configuration(
                    getattr(
                        payload,
                        "configuration",
                        None,
                    )
                )
            ),

            worker_name=None,

            worker_version=None,

        )


        self.db.add(
            scan,
        )


        try:

            await self.commit()

            self.db.refresh(
                scan,
            )


            logger.info(
                "Created scan. id=%s asset=%s",
                scan.id,
                scan.asset_id,
            )


            return self._response(
                scan,
            )


        except Exception:

            logger.exception(
                "Failed creating scan."
            )

            raise



    async def duplicate_scan(
        self,
        scan_id: UUID,
    ) -> ScanResponse:
        """
        Duplicate scan configuration.

        Creates a new pending scan using
        the same asset and scanner settings.
        """

        source = await self.get_scan_model(
            scan_id,
        )


        if source is None:
            raise ValueError(
                "Scan not found."
            )


        duplicate = Scan(

            asset_id=source.asset_id,

            status=ScanStatus.PENDING,

            trigger=ScanTrigger.MANUAL,

            engine=source.engine,

            configuration=source.configuration,

            description=source.description,

        )


        self.db.add(
            duplicate,
        )


        await self.commit()

        self.db.refresh(
            duplicate,
        )


        return self._response(
            duplicate,
        )
        # ============================================================
    # Retrieve Scan
    # ============================================================

    async def get_scan(
        self,
        scan_id: UUID,
    ) -> ScanResponse:
        """
        Retrieve a scan by ID.

        Raises
        ------
        ValueError
            If scan does not exist.
        """

        scan = await self.get_scan_model(
            scan_id,
        )

        if scan is None:
            raise ValueError(
                "Scan not found."
            )


        return self._response(
            scan,
        )


    async def get_scan_summary(
        self,
        scan_id: UUID,
    ) -> ScanSummary:
        """
        Retrieve lightweight scan details.
        """

        scan = await self.get_scan_model(
            scan_id,
        )

        if scan is None:
            raise ValueError(
                "Scan not found."
            )


        return self._summary(
            scan,
        )


    async def get_scan_detail(
        self,
        scan_id: UUID,
    ) -> dict[str, Any]:
        """
        Retrieve complete scan details.

        Includes:
        - Asset information
        - Findings summary
        - Timing
        - Scanner metadata
        """

        scan = await self.get_scan_model(
            scan_id,
        )

        if scan is None:
            raise ValueError(
                "Scan not found."
            )


        asset = scan.asset


        return {

            "scan": self._response(
                scan,
            ),

            "asset": {

                "id": str(asset.id),

                "name":
                    asset.asset_name,

                "value":
                    asset.asset_value,

                "type":
                    asset.asset_type.value,

                "risk_score":
                    asset.risk_score,

            },

            "statistics": {

                "total_findings":
                    scan.total_findings,

                "critical":
                    scan.critical_findings,

                "high":
                    scan.high_findings,

                "medium":
                    scan.medium_findings,

                "low":
                    scan.low_findings,

                "informational":
                    scan.informational_findings,

            },

        }


    async def get_latest_scan(
        self,
        asset_id: UUID,
    ) -> ScanResponse | None:
        """
        Return the latest scan executed for an asset.
        """

        stmt = (
            select(Scan)
            .where(
                Scan.asset_id == asset_id,
                Scan.deleted_at.is_(None),
            )
            .order_by(
                Scan.created_at.desc(),
            )
            .limit(1)
        )


        result = self.db.execute(
            stmt,
        )


        scan = (
            result.scalar_one_or_none()
        )


        if scan is None:
            return None


        return self._response(
            scan,
        )
        # ============================================================
    # List Scans
    # ============================================================

    async def list_scans(
        self,
        *,
        asset_id: UUID | None = None,
        status: ScanStatus | None = None,
        engine: ScanEngine | None = None,
        trigger: ScanTrigger | None = None,
        page: int = 1,
        page_size: int = 25,
    ) -> ScanListResponse:
        """
        Retrieve paginated scans.

        Supports filtering by:

        - Asset
        - Status
        - Engine
        - Trigger
        """

        filters = [
            Scan.deleted_at.is_(None),
        ]


        if asset_id:

            filters.append(
                Scan.asset_id == asset_id,
            )


        if status:

            filters.append(
                Scan.status == status,
            )


        if engine:

            filters.append(
                Scan.engine == engine,
            )


        if trigger:

            filters.append(
                Scan.trigger == trigger,
            )


        # --------------------------------------------------------
        # Count
        # --------------------------------------------------------

        count_stmt = (
            select(func.count())
            .select_from(
                Scan,
            )
            .where(
                *filters,
            )
        )


        total = self.db.scalar(
            count_stmt,
        )


        total = int(
            total or 0
        )


        # --------------------------------------------------------
        # Pagination
        # --------------------------------------------------------

        page = max(
            1,
            page,
        )


        page_size = max(
            1,
            min(
                page_size,
                100,
            ),
        )


        offset = (
            page - 1
        ) * page_size


        # --------------------------------------------------------
        # Query
        # --------------------------------------------------------

        stmt = (
            select(Scan)
            .where(
                *filters,
            )
            .order_by(
                Scan.created_at.desc(),
            )
            .offset(
                offset,
            )
            .limit(
                page_size,
            )
        )


        result = self.db.execute(
            stmt,
        )


        scans = list(
            result.scalars().all()
        )


        total_pages = (
            (total + page_size - 1)
            // page_size
            if total
            else 1
        )


        return ScanListResponse(

            scans=self.serialize_collection(
                scans,
            ),

            total=total,

            page=page,

            page_size=page_size,

            total_pages=total_pages,
        )



    async def search_scans(
        self,
        query: str,
        *,
        limit: int = 25,
    ) -> list[ScanSummary]:
        """
        Search scans using asset information.
        """

        search = (
            f"%{query.strip()}%"
        )


        stmt = (
            select(Scan)
            .join(
                Asset,
            )
            .where(
                or_(
                    Asset.asset_name.ilike(search),
                    Asset.asset_value.ilike(search),
                    Asset.hostname.ilike(search),
                ),
                Scan.deleted_at.is_(None),
            )
            .order_by(
                Scan.created_at.desc(),
            )
            .limit(limit)
        )


        result = self.db.execute(
            stmt,
        )


        return self.serialize_collection(
            list(
                result.scalars().all()
            )
        )
        # ============================================================
    # Scan Lifecycle - Queue & Start
    # ============================================================

    async def queue_scan(
        self,
        scan_id: UUID,
        *,
        worker_name: str | None = None,
        worker_version: str | None = None,
    ) -> ScanResponse:
        """
        Move scan from PENDING to QUEUED.

        Used by:
        - Scheduler
        - Scan orchestrator
        - Worker queue
        """

        scan = await self.get_scan_model(
            scan_id,
        )


        if scan is None:
            raise ValueError(
                "Scan not found."
            )


        if scan.status not in (
            ScanStatus.PENDING,
            ScanStatus.QUEUED,
        ):
            raise ValueError(
                "Only pending scans can be queued."
            )


        scan.status = (
            ScanStatus.QUEUED
        )

        scan.queued_at = (
            datetime.utcnow()
        )


        if worker_name:
            scan.worker_name = worker_name


        if worker_version:
            scan.worker_version = worker_version


        await self.commit()

        self.db.refresh(
            scan,
        )


        logger.info(
            "Scan queued. id=%s",
            scan.id,
        )


        return self._response(
            scan,
        )



    async def start_scan(
        self,
        scan_id: UUID,
        *,
        worker_name: str | None = None,
        worker_version: str | None = None,
    ) -> ScanResponse:
        """
        Start scan execution.

        Changes state:

        QUEUED -> RUNNING
        """

        scan = await self.get_scan_model(
            scan_id,
        )


        if scan is None:
            raise ValueError(
                "Scan not found."
            )


        if scan.status not in (
            ScanStatus.PENDING,
            ScanStatus.QUEUED,
        ):
            raise ValueError(
                "Scan cannot be started from current state."
            )


        scan.status = (
            ScanStatus.RUNNING
        )

        scan.started_at = (
            datetime.utcnow()
        )


        if worker_name:
            scan.worker_name = worker_name


        if worker_version:
            scan.worker_version = worker_version


        await self.commit()

        self.db.refresh(
            scan,
        )


        logger.info(
            "Scan started. id=%s",
            scan.id,
        )


        return self._response(
            scan,
        )



    async def restart_scan(
        self,
        scan_id: UUID,
    ) -> ScanResponse:
        """
        Restart a completed or failed scan.

        Creates a fresh execution state.
        """

        scan = await self.get_scan_model(
            scan_id,
        )


        if scan is None:
            raise ValueError(
                "Scan not found."
            )


        scan.status = (
            ScanStatus.PENDING
        )

        scan.queued_at = None

        scan.started_at = None

        scan.completed_at = None

        scan.duration_seconds = None

        scan.error_message = None


        await self.commit()

        self.db.refresh(
            scan,
        )


        return self._response(
            scan,
        )
        # ============================================================
    # Scan Lifecycle - Complete / Fail / Cancel
    # ============================================================

    async def complete_scan(
        self,
        scan_id: UUID,
    ) -> ScanResponse:
        """
        Mark scan execution as completed.

        Calculates:
        - Completion timestamp
        - Duration
        - Final state
        """

        scan = await self.get_scan_model(
            scan_id,
        )


        if scan is None:
            raise ValueError(
                "Scan not found."
            )


        if scan.status != ScanStatus.RUNNING:
            raise ValueError(
                "Only running scans can be completed."
            )


        scan.status = (
            ScanStatus.COMPLETED
        )

        scan.completed_at = (
            datetime.utcnow()
        )


        scan.calculate_duration()


        await self.commit()

        self.db.refresh(
            scan,
        )


        logger.info(
            "Scan completed. id=%s duration=%s",
            scan.id,
            scan.duration_seconds,
        )


        return self._response(
            scan,
        )



    async def fail_scan(
        self,
        scan_id: UUID,
        message: str,
    ) -> ScanResponse:
        """
        Mark scan as failed.
        """

        scan = await self.get_scan_model(
            scan_id,
        )


        if scan is None:
            raise ValueError(
                "Scan not found."
            )


        scan.fail(
            message,
        )


        await self.commit()

        self.db.refresh(
            scan,
        )


        logger.error(
            "Scan failed. id=%s error=%s",
            scan.id,
            message,
        )


        return self._response(
            scan,
        )



    async def cancel_scan(
        self,
        scan_id: UUID,
    ) -> ScanResponse:
        """
        Cancel an active scan.
        """

        scan = await self.get_scan_model(
            scan_id,
        )


        if scan is None:
            raise ValueError(
                "Scan not found."
            )


        if scan.status not in (
            ScanStatus.PENDING,
            ScanStatus.QUEUED,
            ScanStatus.RUNNING,
        ):
            raise ValueError(
                "Only active scans can be cancelled."
            )


        scan.cancel()


        await self.commit()

        self.db.refresh(
            scan,
        )


        logger.info(
            "Scan cancelled. id=%s",
            scan.id,
        )


        return self._response(
            scan,
        )



    async def timeout_scan(
        self,
        scan_id: UUID,
    ) -> ScanResponse:
        """
        Mark scan execution as timed out.
        """

        scan = await self.get_scan_model(
            scan_id,
        )


        if scan is None:
            raise ValueError(
                "Scan not found."
            )


        scan.timeout()


        await self.commit()

        self.db.refresh(
            scan,
        )


        logger.warning(
            "Scan timeout. id=%s",
            scan.id,
        )


        return self._response(
            scan,
        )
        # ============================================================
    # Finding Statistics
    # ============================================================

    async def update_finding_statistics(
        self,
        scan_id: UUID,
    ) -> ScanResponse:
        """
        Recalculate finding statistics.

        Uses related Finding objects and updates:

        - Total findings
        - Critical
        - High
        - Medium
        - Low
        - Informational
        """

        scan = await self.get_scan_model(
            scan_id,
        )


        if scan is None:
            raise ValueError(
                "Scan not found."
            )


        findings = scan.findings


        scan.total_findings = len(
            findings
        )


        scan.critical_findings = sum(
            1
            for finding in findings
            if getattr(
                finding,
                "severity",
                None,
            )
            == "critical"
        )


        scan.high_findings = sum(
            1
            for finding in findings
            if getattr(
                finding,
                "severity",
                None,
            )
            == "high"
        )


        scan.medium_findings = sum(
            1
            for finding in findings
            if getattr(
                finding,
                "severity",
                None,
            )
            == "medium"
        )


        scan.low_findings = sum(
            1
            for finding in findings
            if getattr(
                finding,
                "severity",
                None,
            )
            == "low"
        )


        scan.informational_findings = sum(
            1
            for finding in findings
            if getattr(
                finding,
                "severity",
                None,
            )
            in (
                "info",
                "informational",
            )
        )


        await self.commit()

        self.db.refresh(
            scan,
        )


        logger.info(
            "Updated finding statistics for scan=%s",
            scan.id,
        )


        return self._response(
            scan,
        )



    async def update_statistics_from_payload(
        self,
        scan_id: UUID,
        statistics: dict[str, int],
    ) -> ScanResponse:
        """
        Update scan counters from scanner output.

        Used by external scanner workers.
        """

        scan = await self.get_scan_model(
            scan_id,
        )


        if scan is None:
            raise ValueError(
                "Scan not found."
            )


        scan.total_findings = (
            statistics.get(
                "total",
                scan.total_findings,
            )
        )


        scan.critical_findings = (
            statistics.get(
                "critical",
                scan.critical_findings,
            )
        )


        scan.high_findings = (
            statistics.get(
                "high",
                scan.high_findings,
            )
        )


        scan.medium_findings = (
            statistics.get(
                "medium",
                scan.medium_findings,
            )
        )


        scan.low_findings = (
            statistics.get(
                "low",
                scan.low_findings,
            )
        )


        scan.informational_findings = (
            statistics.get(
                "informational",
                scan.informational_findings,
            )
        )


        await self.commit()

        self.db.refresh(
            scan,
        )


        return self._response(
            scan,
        )
        # ============================================================
    # Scanner Worker Helpers
    # ============================================================

    async def assign_worker(
        self,
        scan_id: UUID,
        *,
        worker_name: str,
        worker_version: str | None = None,
    ) -> ScanResponse:
        """
        Assign scanner worker metadata.

        Used by:
        - Celery workers
        - Kubernetes jobs
        - Scanner agents
        """

        scan = await self.get_scan_model(
            scan_id,
        )


        if scan is None:
            raise ValueError(
                "Scan not found."
            )


        scan.worker_name = worker_name


        if worker_version:
            scan.worker_version = worker_version


        await self.commit()

        self.db.refresh(
            scan,
        )


        logger.info(
            "Worker assigned. scan=%s worker=%s",
            scan.id,
            worker_name,
        )


        return self._response(
            scan,
        )



    async def update_configuration(
        self,
        scan_id: UUID,
        configuration: dict[str, Any],
    ) -> ScanResponse:
        """
        Update scanner configuration.

        Configuration is stored as serialized JSON.
        """

        scan = await self.get_scan_model(
            scan_id,
        )


        if scan is None:
            raise ValueError(
                "Scan not found."
            )


        scan.configuration = (
            self.normalize_configuration(
                configuration,
            )
        )


        await self.commit()

        self.db.refresh(
            scan,
        )


        return self._response(
            scan,
        )



    async def attach_error(
        self,
        scan_id: UUID,
        error_message: str,
    ) -> ScanResponse:
        """
        Attach scanner execution error.

        Does not automatically fail the scan.
        """

        scan = await self.get_scan_model(
            scan_id,
        )


        if scan is None:
            raise ValueError(
                "Scan not found."
            )


        scan.error_message = (
            error_message
        )


        await self.commit()

        self.db.refresh(
            scan,
        )


        return self._response(
            scan,
        )



    async def heartbeat(
        self,
        scan_id: UUID,
    ) -> bool:
        """
        Scanner heartbeat.

        Used to verify that a worker
        is still processing the scan.

        Returns True if scan exists and is running.
        """

        scan = await self.get_scan_model(
            scan_id,
        )


        if scan is None:
            return False


        return (
            scan.status
            == ScanStatus.RUNNING
        )



    async def recover_stuck_scans(
        self,
        timeout_minutes: int = 60,
    ) -> int:
        """
        Recover scans stuck in RUNNING state.

        Intended for scheduler jobs.

        Running scans older than timeout
        are marked as TIMEOUT.
        """

        from datetime import timedelta


        cutoff = (
            datetime.utcnow()
            -
            timedelta(
                minutes=timeout_minutes,
            )
        )


        stmt = (
            select(Scan)
            .where(
                Scan.status
                == ScanStatus.RUNNING,

                Scan.started_at
                <= cutoff,
            )
        )


        result = self.db.execute(
            stmt,
        )


        scans = list(
            result.scalars().all()
        )


        for scan in scans:

            scan.timeout()


        if scans:
            await self.commit()


        logger.warning(
            "Recovered %s stuck scans.",
            len(scans),
        )


        return len(scans)
        # ============================================================
    # Scan State Queries
    # ============================================================

    async def get_running_scans(
        self,
        *,
        limit: int = 50,
    ) -> list[ScanSummary]:
        """
        Return currently running scans.

        Used by:
        - Monitoring dashboards
        - Worker managers
        - Operations teams
        """

        stmt = (
            select(Scan)
            .where(
                Scan.status
                == ScanStatus.RUNNING,

                Scan.deleted_at.is_(None),
            )
            .order_by(
                Scan.started_at.asc(),
            )
            .limit(limit)
        )


        result = self.db.execute(
            stmt,
        )


        scans = list(
            result.scalars().all()
        )


        return self.serialize_collection(
            scans,
        )



    async def get_pending_scans(
        self,
        *,
        limit: int = 50,
    ) -> list[ScanSummary]:
        """
        Return pending scans waiting for execution.
        """

        stmt = (
            select(Scan)
            .where(
                Scan.status
                == ScanStatus.PENDING,

                Scan.deleted_at.is_(None),
            )
            .order_by(
                Scan.created_at.asc(),
            )
            .limit(limit)
        )


        result = self.db.execute(
            stmt,
        )


        return self.serialize_collection(
            list(
                result.scalars().all()
            )
        )



    async def get_queued_scans(
        self,
        *,
        limit: int = 50,
    ) -> list[ScanSummary]:
        """
        Return scans queued for workers.
        """

        stmt = (
            select(Scan)
            .where(
                Scan.status
                == ScanStatus.QUEUED,

                Scan.deleted_at.is_(None),
            )
            .order_by(
                Scan.queued_at.asc(),
            )
            .limit(limit)
        )


        result = self.db.execute(
            stmt,
        )


        return self.serialize_collection(
            list(
                result.scalars().all()
            )
        )



    async def get_failed_scans(
        self,
        *,
        limit: int = 50,
    ) -> list[ScanSummary]:
        """
        Return failed scan executions.
        """

        stmt = (
            select(Scan)
            .where(
                Scan.status
                == ScanStatus.FAILED,

                Scan.deleted_at.is_(None),
            )
            .order_by(
                Scan.completed_at.desc(),
            )
            .limit(limit)
        )


        result = self.db.execute(
            stmt,
        )


        return self.serialize_collection(
            list(
                result.scalars().all()
            )
        )



    async def get_completed_scans(
        self,
        *,
        asset_id: UUID | None = None,
        limit: int = 50,
    ) -> list[ScanSummary]:
        """
        Return successfully completed scans.
        """

        filters = [

            Scan.status
            == ScanStatus.COMPLETED,

            Scan.deleted_at.is_(None),

        ]


        if asset_id:

            filters.append(
                Scan.asset_id
                == asset_id,
            )


        stmt = (
            select(Scan)
            .where(
                *filters,
            )
            .order_by(
                Scan.completed_at.desc(),
            )
            .limit(limit)
        )


        result = self.db.execute(
            stmt,
        )


        return self.serialize_collection(
            list(
                result.scalars().all()
            )
        )
        # ============================================================
    # Scan Analytics
    # ============================================================

    async def get_statistics(
        self,
    ) -> dict[str, Any]:
        """
        Return global scan statistics.

        Includes:

        - Total scans
        - Running scans
        - Completed scans
        - Failed scans
        - Average duration
        - Findings summary
        """

        total = self.db.scalar(
            select(func.count())
            .select_from(
                Scan,
            )
        )


        running = self.db.scalar(
            select(func.count())
            .select_from(
                Scan,
            )
            .where(
                Scan.status
                == ScanStatus.RUNNING,
            )
        )


        completed = self.db.scalar(
            select(func.count())
            .select_from(
                Scan,
            )
            .where(
                Scan.status
                == ScanStatus.COMPLETED,
            )
        )


        failed = self.db.scalar(
            select(func.count())
            .select_from(
                Scan,
            )
            .where(
                Scan.status
                == ScanStatus.FAILED,
            )
        )


        average_duration = self.db.scalar(
            select(
                func.avg(
                    Scan.duration_seconds,
                )
            )
            .where(
                Scan.duration_seconds
                != None,
            )
        )


        findings = self.db.execute(
            select(
                func.sum(
                    Scan.total_findings,
                ),
                func.sum(
                    Scan.critical_findings,
                ),
                func.sum(
                    Scan.high_findings,
                ),
            )
        )


        findings_row = findings.one()


        return {

            "total_scans":
                int(total or 0),

            "running_scans":
                int(running or 0),

            "completed_scans":
                int(completed or 0),

            "failed_scans":
                int(failed or 0),

            "average_duration_seconds":
                (
                    round(
                        float(
                            average_duration
                        ),
                        2,
                    )
                    if average_duration
                    else 0
                ),

            "findings":

                {
                    "total":
                        int(
                            findings_row[0]
                            or 0
                        ),

                    "critical":
                        int(
                            findings_row[1]
                            or 0
                        ),

                    "high":
                        int(
                            findings_row[2]
                            or 0
                        ),
                },

        }



    async def get_engine_statistics(
        self,
    ) -> dict[str, int]:
        """
        Return scan count grouped by scanner engine.
        """

        rows = self.db.execute(
            select(
                Scan.engine,
                func.count(
                    Scan.id,
                ),
            )
            .group_by(
                Scan.engine,
            )
        )


        return {

            engine.value:
                count

            for engine, count
            in rows.all()

        }



    async def get_trigger_statistics(
        self,
    ) -> dict[str, int]:
        """
        Return scan count grouped by trigger.
        """

        rows = self.db.execute(
            select(
                Scan.trigger,
                func.count(
                    Scan.id,
                ),
            )
            .group_by(
                Scan.trigger,
            )
        )


        return {

            trigger.value:
                count

            for trigger, count
            in rows.all()

        }
        # ============================================================
    # Dashboard Metrics
    # ============================================================

    async def get_dashboard(
        self,
    ) -> ScanDashboard:
        """
        Generate scan dashboard information.

        Used by:

        - Admin dashboard
        - Security operations center
        - Monitoring APIs
        """

        statistics = await self.get_statistics()

        engine_statistics = (
            await self.get_engine_statistics()
        )

        trigger_statistics = (
            await self.get_trigger_statistics()
        )


        recent_scans_stmt = (
            select(Scan)
            .where(
                Scan.deleted_at.is_(None),
            )
            .order_by(
                Scan.created_at.desc(),
            )
            .limit(10)
        )


        recent_result = self.db.execute(
            recent_scans_stmt,
        )


        recent_scans = list(
            recent_result.scalars().all()
        )


        return ScanDashboard(

            total_scans=(
                statistics["total_scans"]
            ),

            running_scans=(
                statistics["running_scans"]
            ),

            completed_scans=(
                statistics["completed_scans"]
            ),

            failed_scans=(
                statistics["failed_scans"]
            ),

            average_duration_seconds=(
                statistics[
                    "average_duration_seconds"
                ]
            ),

            total_findings=(
                statistics[
                    "findings"
                ][
                    "total"
                ]
            ),

            critical_findings=(
                statistics[
                    "findings"
                ][
                    "critical"
                ]
            ),

            high_findings=(
                statistics[
                    "findings"
                ][
                    "high"
                ]
            ),

            engine_distribution=(
                engine_statistics
            ),

            trigger_distribution=(
                trigger_statistics
            ),

            recent_scans=(
                self.serialize_collection(
                    recent_scans,
                )
            ),

        )



    async def execution_health(
        self,
    ) -> dict[str, Any]:
        """
        Return operational scan health.

        Helps identify:

        - Stuck workers
        - Failed execution rate
        - Queue pressure
        """

        pending = self.db.scalar(
            select(func.count())
            .select_from(
                Scan,
            )
            .where(
                Scan.status
                == ScanStatus.PENDING,
            )
        )


        queued = self.db.scalar(
            select(func.count())
            .select_from(
                Scan,
            )
            .where(
                Scan.status
                == ScanStatus.QUEUED,
            )
        )


        running = self.db.scalar(
            select(func.count())
            .select_from(
                Scan,
            )
            .where(
                Scan.status
                == ScanStatus.RUNNING,
            )
        )


        failed = self.db.scalar(
            select(func.count())
            .select_from(
                Scan,
            )
            .where(
                Scan.status
                == ScanStatus.FAILED,
            )
        )


        return {

            "queue_depth":
                int(
                    (pending or 0)
                    +
                    (queued or 0)
                ),

            "running_workers":
                int(
                    running or 0
                ),

            "failed_executions":
                int(
                    failed or 0
                ),

            "healthy":
                (
                    (running or 0)
                    < 100
                ),

        }
        # ============================================================
    # Cleanup Utilities
    # ============================================================

    async def soft_delete_scan(
        self,
        scan_id: UUID,
    ) -> bool:
        """
        Soft delete a scan.

        The scan data remains available for audit purposes.
        """

        scan = await self.get_scan_model(
            scan_id,
        )


        if scan is None:
            raise ValueError(
                "Scan not found."
            )


        scan.soft_delete()


        await self.commit()


        logger.info(
            "Soft deleted scan. id=%s",
            scan_id,
        )


        return True



    async def restore_scan(
        self,
        scan_id: UUID,
    ) -> ScanResponse:
        """
        Restore a soft deleted scan.
        """

        stmt = (
            select(Scan)
            .where(
                Scan.id == scan_id,
            )
        )


        result = self.db.execute(
            stmt,
        )


        scan = (
            result.scalar_one_or_none()
        )


        if scan is None:
            raise ValueError(
                "Scan not found."
            )


        scan.deleted_at = None


        await self.commit()

        self.db.refresh(
            scan,
        )


        logger.info(
            "Restored scan. id=%s",
            scan_id,
        )


        return self._response(
            scan,
        )



    async def purge_deleted_scans(
        self,
        *,
        older_than_days: int = 90,
    ) -> int:
        """
        Permanently remove soft deleted scans.

        Intended for scheduled maintenance.

        Returns:
            Number of removed scans.
        """

        from datetime import timedelta


        cutoff = (
            datetime.utcnow()
            -
            timedelta(
                days=older_than_days,
            )
        )


        stmt = (
            select(Scan)
            .where(
                Scan.deleted_at.is_not(None),

                Scan.deleted_at
                <= cutoff,
            )
        )


        result = self.db.execute(
            stmt,
        )


        scans = list(
            result.scalars().all()
        )


        for scan in scans:

            self.db.delete(
                scan,
            )


        if scans:

            await self.commit()


        logger.info(
            "Purged %s deleted scans.",
            len(scans),
        )


        return len(scans)



    async def remove_failed_old_scans(
        self,
        *,
        older_than_days: int = 180,
    ) -> int:
        """
        Cleanup failed scans older than retention period.
        """

        from datetime import timedelta


        cutoff = (
            datetime.utcnow()
            -
            timedelta(
                days=older_than_days,
            )
        )


        stmt = (
            select(Scan)
            .where(
                Scan.status
                == ScanStatus.FAILED,

                Scan.created_at
                <= cutoff,
            )
        )


        result = self.db.execute(
            stmt,
        )


        scans = list(
            result.scalars().all()
        )


        for scan in scans:

            self.db.delete(
                scan,
            )


        if scans:

            await self.commit()


        logger.info(
            "Removed %s old failed scans.",
            len(scans),
        )


        return len(scans)
        # ============================================================
    # Final Utilities
    # ============================================================

    async def export_scan(
        self,
        scan_id: UUID,
    ) -> dict[str, Any]:
        """
        Export complete scan metadata.

        Used by:

        - Reporting engine
        - Audit exports
        - External integrations
        """

        scan = await self.get_scan_model(
            scan_id,
        )


        if scan is None:
            raise ValueError(
                "Scan not found."
            )


        return scan.to_dict(
            include_findings=True,
        )



    async def clone_and_queue_scan(
        self,
        scan_id: UUID,
    ) -> ScanResponse:
        """
        Clone an existing scan and queue it.

        Useful for:
        - Re-scanning assets
        - Scheduled remediation checks
        """

        cloned = await self.duplicate_scan(
            scan_id,
        )


        return await self.queue_scan(
            cloned.id,
        )



    async def get_asset_scan_history(
        self,
        asset_id: UUID,
        *,
        limit: int = 100,
    ) -> list[ScanSummary]:
        """
        Return scan history for an asset.
        """

        stmt = (
            select(Scan)
            .where(
                Scan.asset_id == asset_id,

                Scan.deleted_at.is_(None),
            )
            .order_by(
                Scan.created_at.desc(),
            )
            .limit(limit)
        )


        result = self.db.execute(
            stmt,
        )


        scans = list(
            result.scalars().all()
        )


        return self.serialize_collection(
            scans,
        )



    async def delete_scan(
        self,
        scan_id: UUID,
        *,
        hard_delete: bool = False,
    ) -> None:
        """
        Delete scan.

        Default:
            Soft delete

        Optional:
            Permanent deletion
        """

        scan = await self.get_scan_model(
            scan_id,
            include_deleted=True,
        )


        if scan is None:
            raise ValueError(
                "Scan not found."
            )


        if hard_delete:

            self.db.delete(
                scan,
            )

        else:

            scan.soft_delete()


        await self.commit()


        logger.info(
            "Deleted scan. id=%s hard=%s",
            scan_id,
            hard_delete,
        )



# ============================================================
# End of File
# ============================================================
