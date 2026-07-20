"""
QShield Enterprise
==================

Report Service

Business logic layer for managing security assessment reports.

This service is independent from FastAPI and can be used by:

- REST API
- Background workers
- Celery tasks
- Scheduler
- Report generation engine
- CLI tools
- Automated workflows

Responsibilities
-----------------

• Report CRUD operations
• Report lifecycle management
• Status tracking
• File metadata handling
• Report generation support
• Export preparation
• Statistics
• Cleanup workflows

Author:
QShield Enterprise
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.report import Report
from app.models.report import ReportFormat
from app.models.report import ReportStatus
from app.models.report import ReportType
from app.models.scan import Scan

from app.schemas.report import (
    ReportCreate,
    ReportListResponse,
    ReportResponse,
    ReportSummary,
    ReportUpdate,
)


logger = logging.getLogger(__name__)


class ReportService:
    """
    Enterprise Report Service.

    Handles report lifecycle from creation
    until expiration and cleanup.
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
    def calculate_checksum(
        file_path: str,
    ) -> str:
        """
        Calculate SHA256 checksum of a report file.

        Used for:
        - Integrity verification
        - Compliance evidence
        - Duplicate detection
        """

        sha256 = hashlib.sha256()

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Report file does not exist: {file_path}"
            )

        with path.open(
            "rb",
        ) as file:

            for chunk in iter(
                lambda: file.read(8192),
                b"",
            ):
                sha256.update(chunk)

        return sha256.hexdigest()


    @staticmethod
    def calculate_file_size(
        file_path: str,
    ) -> int:
        """
        Return file size in bytes.
        """

        path = Path(file_path)

        if not path.exists():
            return 0

        return path.stat().st_size


    @staticmethod
    def calculate_expiry(
        days: int = 30,
    ) -> datetime:
        """
        Calculate report expiration timestamp.
        """

        return (
            datetime.utcnow()
            + timedelta(days=days)
        )
        # ============================================================
    # Database Helpers
    # ============================================================

    async def get_report_model(
        self,
        report_id: UUID,
        *,
        include_expired: bool = True,
    ) -> Report | None:
        """
        Retrieve report ORM object.

        Parameters
        ----------
        report_id:
            Report UUID.

        include_expired:
            If False, expired reports are excluded.
        """

        stmt = (
            select(Report)
            .where(
                Report.id == report_id,
            )
        )

        if not include_expired:
            stmt = stmt.where(
                Report.status != ReportStatus.EXPIRED,
            )

        result = self.db.execute(
            stmt,
        )

        return result.scalar_one_or_none()


    async def report_exists(
        self,
        scan_id: UUID,
        report_type: ReportType,
        report_format: ReportFormat,
    ) -> bool:
        """
        Check whether a report already exists
        for a scan with the same type and format.
        """

        stmt = (
            select(func.count())
            .select_from(
                Report,
            )
            .where(
                Report.scan_id == scan_id,
                Report.report_type == report_type,
                Report.report_format == report_format,
            )
        )

        count = self.db.scalar(
            stmt,
        )

        return bool(count)


    async def scan_exists(
        self,
        scan_id: UUID,
    ) -> bool:
        """
        Verify scan exists.
        """

        stmt = (
            select(func.count())
            .select_from(
                Scan,
            )
            .where(
                Scan.id == scan_id,
                Scan.deleted_at.is_(None),
            )
        )

        count = self.db.scalar(
            stmt,
        )

        return bool(count)


    async def get_scan(
        self,
        scan_id: UUID,
    ) -> Scan | None:
        """
        Retrieve scan ORM object.
        """

        stmt = (
            select(Scan)
            .where(
                Scan.id == scan_id,
                Scan.deleted_at.is_(None),
            )
        )

        result = self.db.execute(
            stmt,
        )

        return result.scalar_one_or_none()


    async def commit(
        self,
    ) -> None:
        """
        Commit database transaction.
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
        report: Report,
    ) -> ReportSummary:
        """
        Convert Report ORM object into lightweight schema.
        """

        return ReportSummary(
            id=report.id,

            created_at=report.created_at,

            updated_at=report.updated_at,

            scan_id=report.scan_id,

            title=report.title,

            report_type=report.report_type,

            report_format=report.report_format,

            status=report.status,

            generated_at=report.generated_at,

            expires_at=report.expires_at,

            file_size_bytes=report.file_size_bytes,

        )


    @staticmethod
    def _response(
        report: Report,
    ) -> ReportResponse:
        """
        Convert Report ORM object into API response schema.
        """

        return ReportResponse(

            id=report.id,

            created_at=report.created_at,

            updated_at=report.updated_at,

            scan_id=report.scan_id,

            generated_by_id=report.generated_by_id,

            title=report.title,

            report_type=report.report_type,

            report_format=report.report_format,

            status=report.status,

            executive_summary=report.executive_summary,

            file_path=report.file_path,

            checksum=report.checksum,

            file_size_bytes=report.file_size_bytes,

            generated_at=report.generated_at,

            expires_at=report.expires_at,

        )


    @staticmethod
    def serialize_reports(
        reports: list[Report],
    ) -> list[ReportSummary]:
        """
        Convert collection of reports into summaries.
        """

        return [
            ReportService._summary(
                report,
            )
            for report in reports
        ]


    # ============================================================
    # Validation
    # ============================================================

    @staticmethod
    def validate_report_type(
        report_type: ReportType,
    ) -> None:
        """
        Validate supported report types.
        """

        if report_type not in ReportType:
            raise ValueError(
                "Unsupported report type."
            )


    @staticmethod
    def validate_report_format(
        report_format: ReportFormat,
    ) -> None:
        """
        Validate supported report formats.
        """

        if report_format not in ReportFormat:
            raise ValueError(
                "Unsupported report format."
            )
            # ============================================================
    # Create Report
    # ============================================================

    async def create_report(
        self,
        payload: ReportCreate,
    ) -> ReportResponse:
        """
        Create a new security assessment report.

        Workflow
        --------

        1. Validate scan existence
        2. Check duplicate reports
        3. Create report metadata
        4. Store pending state
        5. Return report response

        Report generation itself is handled by the
        report generation workers.
        """

        if not await self.scan_exists(
            payload.scan_id,
        ):
            raise ValueError(
                "Scan does not exist."
            )


        self.validate_report_type(
            payload.report_type,
        )

        self.validate_report_format(
            payload.report_format,
        )


        if await self.report_exists(
            payload.scan_id,
            payload.report_type,
            payload.report_format,
        ):
            raise ValueError(
                "Report already exists for this scan."
            )


        report = Report(

            scan_id=payload.scan_id,

            generated_by_id=getattr(
                payload,
                "generated_by_id",
                None,
            ),

            title=payload.title,

            report_type=payload.report_type,

            report_format=payload.report_format,

            status=ReportStatus.PENDING,

            executive_summary=None,

            file_path=None,

            checksum=None,

            file_size_bytes=None,

            generated_at=None,

            expires_at=self.calculate_expiry(
                getattr(
                    payload,
                    "expiry_days",
                    30,
                ),
            ),
        )


        self.db.add(report)


        try:

            await self.commit()

            self.db.refresh(
                report,
            )


            logger.info(
                "Created report. id=%s scan=%s",
                report.id,
                report.scan_id,
            )


            return self._response(
                report,
            )


        except Exception:

            logger.exception(
                "Failed creating report."
            )

            raise


    async def duplicate_report(
        self,
        report_id: UUID,
    ) -> ReportResponse:
        """
        Duplicate an existing report definition.

        The duplicated report starts in PENDING state
        and requires regeneration.
        """

        source = await self.get_report_model(
            report_id,
        )


        if source is None:
            raise ValueError(
                "Report not found."
            )


        duplicate = Report(

            scan_id=source.scan_id,

            generated_by_id=source.generated_by_id,

            title=f"{source.title} Copy",

            report_type=source.report_type,

            report_format=source.report_format,

            status=ReportStatus.PENDING,

            expires_at=self.calculate_expiry(),

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
    # Retrieve Reports
    # ============================================================

    async def get_report(
        self,
        report_id: UUID,
    ) -> ReportResponse:
        """
        Retrieve a report by ID.

        Raises
        ------
        ValueError
            If report does not exist.
        """

        report = await self.get_report_model(
            report_id,
        )

        if report is None:
            raise ValueError(
                "Report not found."
            )

        return self._response(
            report,
        )


    async def get_report_summary(
        self,
        report_id: UUID,
    ) -> ReportSummary:
        """
        Retrieve lightweight report information.
        """

        report = await self.get_report_model(
            report_id,
        )

        if report is None:
            raise ValueError(
                "Report not found."
            )

        return self._summary(
            report,
        )


    async def get_reports_by_scan(
        self,
        scan_id: UUID,
    ) -> list[ReportSummary]:
        """
        Return all reports generated for a scan.
        """

        stmt = (
            select(Report)
            .where(
                Report.scan_id == scan_id,
            )
            .order_by(
                Report.created_at.desc(),
            )
        )


        result = self.db.execute(
            stmt,
        )


        reports = list(
            result.scalars().all()
        )


        return self.serialize_reports(
            reports,
        )


    async def get_latest_report(
        self,
        scan_id: UUID,
    ) -> ReportResponse | None:
        """
        Return the latest generated report
        for a scan.
        """

        stmt = (
            select(Report)
            .where(
                Report.scan_id == scan_id,
                Report.status == ReportStatus.COMPLETED,
            )
            .order_by(
                Report.generated_at.desc(),
            )
            .limit(1)
        )


        result = self.db.execute(
            stmt,
        )


        report = (
            result.scalar_one_or_none()
        )


        if report is None:
            return None


        return self._response(
            report,
        )


    async def report_count(
        self,
        scan_id: UUID | None = None,
    ) -> int:
        """
        Count reports.

        If scan_id is provided,
        count reports only for that scan.
        """

        stmt = (
            select(func.count())
            .select_from(
                Report,
            )
        )


        if scan_id:

            stmt = stmt.where(
                Report.scan_id == scan_id,
            )


        count = self.db.scalar(
            stmt,
        )


        return int(
            count or 0
        )
        # ============================================================
    # List Reports
    # ============================================================

    async def list_reports(
        self,
        *,
        scan_id: UUID | None = None,
        status: ReportStatus | None = None,
        report_type: ReportType | None = None,
        report_format: ReportFormat | None = None,
        page: int = 1,
        page_size: int = 25,
    ) -> ReportListResponse:
        """
        Retrieve paginated reports.

        Supports filtering by:

        - Scan
        - Status
        - Type
        - Format
        """

        filters = []

        if scan_id:
            filters.append(
                Report.scan_id == scan_id,
            )

        if status:
            filters.append(
                Report.status == status,
            )

        if report_type:
            filters.append(
                Report.report_type == report_type,
            )

        if report_format:
            filters.append(
                Report.report_format == report_format,
            )


        # --------------------------------------------------------
        # Count
        # --------------------------------------------------------

        count_stmt = (
            select(func.count())
            .select_from(
                Report,
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
            select(Report)
            .where(
                *filters,
            )
            .order_by(
                Report.created_at.desc(),
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


        reports = list(
            result.scalars().all()
        )


        total_pages = (
            (total + page_size - 1)
            // page_size
            if total
            else 1
        )


        return ReportListResponse(

            reports=self.serialize_reports(
                reports,
            ),

            total=total,

            page=page,

            page_size=page_size,

            total_pages=total_pages,
        )


    async def search_reports(
        self,
        query: str,
        *,
        limit: int = 25,
    ) -> list[ReportSummary]:
        """
        Search reports by title.
        """

        search = f"%{query.strip()}%"


        stmt = (
            select(Report)
            .where(
                Report.title.ilike(search),
            )
            .order_by(
                Report.created_at.desc(),
            )
            .limit(limit)
        )


        result = self.db.execute(
            stmt,
        )


        return self.serialize_reports(
            list(
                result.scalars().all()
            )
        )
        # ============================================================
    # Report Lifecycle Management
    # ============================================================

    async def update_report_status(
        self,
        report_id: UUID,
        status: ReportStatus,
    ) -> ReportResponse:
        """
        Update report lifecycle status.
        """

        report = await self.get_report_model(
            report_id,
        )

        if report is None:
            raise ValueError(
                "Report not found."
            )


        report.status = status


        if status == ReportStatus.COMPLETED:

            report.generated_at = (
                datetime.utcnow()
            )


        elif status == ReportStatus.EXPIRED:

            report.expires_at = (
                datetime.utcnow()
            )


        await self.commit()

        self.db.refresh(
            report,
        )


        logger.info(
            "Updated report status. id=%s status=%s",
            report.id,
            report.status.value,
        )


        return self._response(
            report,
        )


    async def mark_generating(
        self,
        report_id: UUID,
    ) -> ReportResponse:
        """
        Mark report generation as started.
        """

        return await self.update_report_status(
            report_id,
            ReportStatus.GENERATING,
        )


    async def mark_completed(
        self,
        report_id: UUID,
        *,
        file_path: str | None = None,
    ) -> ReportResponse:
        """
        Mark report generation as completed.

        Automatically calculates:

        - checksum
        - file size
        - generation timestamp
        """

        report = await self.get_report_model(
            report_id,
        )

        if report is None:
            raise ValueError(
                "Report not found."
            )


        report.status = (
            ReportStatus.COMPLETED
        )

        report.generated_at = (
            datetime.utcnow()
        )


        if file_path:

            report.file_path = file_path

            report.file_size_bytes = (
                self.calculate_file_size(
                    file_path,
                )
            )

            report.checksum = (
                self.calculate_checksum(
                    file_path,
                )
            )


        await self.commit()

        self.db.refresh(
            report,
        )


        logger.info(
            "Report completed. id=%s",
            report.id,
        )


        return self._response(
            report,
        )


    async def mark_failed(
        self,
        report_id: UUID,
        *,
        reason: str | None = None,
    ) -> ReportResponse:
        """
        Mark report generation as failed.
        """

        report = await self.get_report_model(
            report_id,
        )

        if report is None:
            raise ValueError(
                "Report not found."
            )


        report.status = (
            ReportStatus.FAILED
        )


        if reason:

            report.executive_summary = (
                f"Generation failed: {reason}"
            )


        await self.commit()

        self.db.refresh(
            report,
        )


        logger.error(
            "Report generation failed. id=%s",
            report.id,
        )


        return self._response(
            report,
        )


    async def expire_report(
        self,
        report_id: UUID,
    ) -> ReportResponse:
        """
        Mark a report as expired.
        """

        return await self.update_report_status(
            report_id,
            ReportStatus.EXPIRED,
        )
        # ============================================================
    # File Management
    # ============================================================

    async def attach_file(
        self,
        report_id: UUID,
        file_path: str,
    ) -> ReportResponse:
        """
        Attach generated report file metadata.

        Calculates:
        - File size
        - SHA256 checksum
        """

        report = await self.get_report_model(
            report_id,
        )

        if report is None:
            raise ValueError(
                "Report not found."
            )


        report.file_path = file_path

        report.file_size_bytes = (
            self.calculate_file_size(
                file_path,
            )
        )

        report.checksum = (
            self.calculate_checksum(
                file_path,
            )
        )


        await self.commit()

        self.db.refresh(
            report,
        )


        logger.info(
            "Attached file to report. id=%s",
            report.id,
        )


        return self._response(
            report,
        )


    async def remove_file(
        self,
        report_id: UUID,
    ) -> ReportResponse:
        """
        Remove report file metadata.

        The physical file is intentionally not deleted.
        File storage cleanup is handled separately.
        """

        report = await self.get_report_model(
            report_id,
        )

        if report is None:
            raise ValueError(
                "Report not found."
            )


        report.file_path = None

        report.file_size_bytes = None

        report.checksum = None


        await self.commit()

        self.db.refresh(
            report,
        )


        return self._response(
            report,
        )


    async def verify_checksum(
        self,
        report_id: UUID,
    ) -> bool:
        """
        Verify stored checksum against
        current file contents.
        """

        report = await self.get_report_model(
            report_id,
        )

        if report is None:
            raise ValueError(
                "Report not found."
            )


        if (
            not report.file_path
            or not report.checksum
        ):
            return False


        current_checksum = (
            self.calculate_checksum(
                report.file_path,
            )
        )


        return (
            current_checksum
            == report.checksum
        )


    # ============================================================
    # Expiration Management
    # ============================================================

    async def extend_expiration(
        self,
        report_id: UUID,
        days: int,
    ) -> ReportResponse:
        """
        Extend report expiration date.
        """

        report = await self.get_report_model(
            report_id,
        )

        if report is None:
            raise ValueError(
                "Report not found."
            )


        base_date = (
            report.expires_at
            or datetime.utcnow()
        )


        report.expires_at = (
            base_date
            + timedelta(days=days)
        )


        await self.commit()

        self.db.refresh(
            report,
        )


        return self._response(
            report,
        )


    async def expire_old_reports(
        self,
    ) -> int:
        """
        Expire reports that passed their expiry date.

        Returns:
            Number of expired reports
        """

        now = datetime.utcnow()


        stmt = (
            select(Report)
            .where(
                Report.expires_at <= now,
                Report.status != ReportStatus.EXPIRED,
            )
        )


        result = self.db.execute(
            stmt,
        )


        reports = list(
            result.scalars().all()
        )


        for report in reports:

            report.status = (
                ReportStatus.EXPIRED
            )


        if reports:
            await self.commit()


        logger.info(
            "Expired %s reports.",
            len(reports),
        )


        return len(reports)
        # ============================================================
    # Report Generation Preparation
    # ============================================================

    async def prepare_report_context(
        self,
        report_id: UUID,
    ) -> dict[str, Any]:
        """
        Prepare data context used by report generators.

        This method does not generate files.
        It only collects normalized data required by:

        - PDF generator
        - HTML renderer
        - JSON exporter
        - Compliance engines
        """

        report = await self.get_report_model(
            report_id,
        )

        if report is None:
            raise ValueError(
                "Report not found."
            )


        scan = await self.get_scan(
            report.scan_id,
        )


        if scan is None:
            raise ValueError(
                "Associated scan not found."
            )


        asset = scan.asset


        context = {

            "report": {
                "id": str(report.id),
                "title": report.title,
                "type": (
                    report.report_type.value
                ),
                "format": (
                    report.report_format.value
                ),
                "status": (
                    report.status.value
                ),
                "created_at": (
                    report.created_at.isoformat()
                ),
            },


            "scan": {

                "id": str(scan.id),

                "status": (
                    scan.status.value
                ),

                "engine": (
                    scan.engine.value
                ),

                "trigger": (
                    scan.trigger.value
                ),

                "started_at": (
                    scan.started_at.isoformat()
                    if scan.started_at
                    else None
                ),

                "completed_at": (
                    scan.completed_at.isoformat()
                    if scan.completed_at
                    else None
                ),

                "duration_seconds":
                    scan.duration_seconds,

                "total_findings":
                    scan.total_findings,

                "critical_findings":
                    scan.critical_findings,

                "high_findings":
                    scan.high_findings,

                "medium_findings":
                    scan.medium_findings,

                "low_findings":
                    scan.low_findings,
            },


            "asset": {

                "id": str(asset.id),

                "name":
                    asset.asset_name,

                "value":
                    asset.asset_value,

                "type":
                    asset.asset_type.value,

                "criticality":
                    asset.criticality.value,

                "risk_score":
                    asset.risk_score,

                "external":
                    asset.external,

                "production":
                    asset.production,

            },
        }


        return context


    async def build_executive_summary(
        self,
        report_id: UUID,
    ) -> str:
        """
        Build a high-level executive summary.

        This can later be replaced by an AI summarization engine.
        """

        context = await self.prepare_report_context(
            report_id,
        )


        asset = context["asset"]
        scan = context["scan"]


        summary = (
            f"Security assessment completed for "
            f"{asset['name']}. "
            f"The assessment identified "
            f"{scan['total_findings']} findings "
            f"with an overall risk score of "
            f"{asset['risk_score']}."
        )


        return summary


    async def update_executive_summary(
        self,
        report_id: UUID,
    ) -> ReportResponse:
        """
        Generate and store executive summary.
        """

        report = await self.get_report_model(
            report_id,
        )

        if report is None:
            raise ValueError(
                "Report not found."
            )


        report.executive_summary = (
            await self.build_executive_summary(
                report_id,
            )
        )


        await self.commit()

        self.db.refresh(
            report,
        )


        return self._response(
            report,
        )
        # ============================================================
    # Export Helpers
    # ============================================================

    async def export_report_json(
        self,
        report_id: UUID,
    ) -> dict[str, Any]:
        """
        Export report metadata as JSON-compatible dictionary.

        Used by:
        - API responses
        - JSON report format
        - External integrations
        """

        report = await self.get_report_model(
            report_id,
        )

        if report is None:
            raise ValueError(
                "Report not found."
            )


        context = await self.prepare_report_context(
            report_id,
        )


        return {

            "report": {

                "id": str(report.id),

                "title":
                    report.title,

                "type":
                    report.report_type.value,

                "format":
                    report.report_format.value,

                "status":
                    report.status.value,

                "generated_at":
                    (
                        report.generated_at.isoformat()
                        if report.generated_at
                        else None
                    ),

            },


            "assessment":
                context,

        }


    async def export_report_csv_rows(
        self,
        report_id: UUID,
    ) -> list[dict[str, Any]]:
        """
        Generate flat CSV-compatible rows.

        Designed for:
        - Compliance exports
        - Audit archives
        - Data pipelines
        """

        context = await self.prepare_report_context(
            report_id,
        )


        scan = context["scan"]

        asset = context["asset"]


        return [

            {

                "asset_name":
                    asset["name"],

                "asset_value":
                    asset["value"],

                "asset_type":
                    asset["type"],

                "criticality":
                    asset["criticality"],

                "risk_score":
                    asset["risk_score"],

                "scan_status":
                    scan["status"],

                "total_findings":
                    scan["total_findings"],

                "critical_findings":
                    scan["critical_findings"],

                "high_findings":
                    scan["high_findings"],

                "medium_findings":
                    scan["medium_findings"],

                "low_findings":
                    scan["low_findings"],

            }

        ]


    async def generate_download_metadata(
        self,
        report_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate download information for clients.
        """

        report = await self.get_report_model(
            report_id,
        )


        if report is None:
            raise ValueError(
                "Report not found."
            )


        if not report.file_path:

            return {

                "available": False,

                "reason":
                    "Report file not generated.",

            }


        return {

            "available": True,

            "file_path":
                report.file_path,

            "size_bytes":
                report.file_size_bytes,

            "checksum":
                report.checksum,

            "expires_at":
                (
                    report.expires_at.isoformat()
                    if report.expires_at
                    else None
                ),

        }
        # ============================================================
    # Report Statistics
    # ============================================================

    async def get_statistics(
        self,
    ) -> dict[str, Any]:
        """
        Return global report statistics.

        Provides:

        - Total reports
        - Completed reports
        - Failed reports
        - Pending reports
        - Expired reports
        - Reports by format
        - Reports by type
        """

        total = self.db.scalar(
            select(func.count())
            .select_from(Report)
        )


        completed = self.db.scalar(
            select(func.count())
            .select_from(Report)
            .where(
                Report.status
                == ReportStatus.COMPLETED
            )
        )


        failed = self.db.scalar(
            select(func.count())
            .select_from(Report)
            .where(
                Report.status
                == ReportStatus.FAILED
            )
        )


        pending = self.db.scalar(
            select(func.count())
            .select_from(Report)
            .where(
                Report.status
                == ReportStatus.PENDING
            )
        )


        expired = self.db.scalar(
            select(func.count())
            .select_from(Report)
            .where(
                Report.status
                == ReportStatus.EXPIRED
            )
        )


        # --------------------------------------------------------
        # By Format
        # --------------------------------------------------------

        format_rows = (
            self.db.execute(
                select(
                    Report.report_format,
                    func.count(Report.id),
                )
                .group_by(
                    Report.report_format,
                )
            )
        ).all()


        reports_by_format = {

            report_format.value:
                count

            for report_format, count
            in format_rows

        }


        # --------------------------------------------------------
        # By Type
        # --------------------------------------------------------

        type_rows = (
            self.db.execute(
                select(
                    Report.report_type,
                    func.count(Report.id),
                )
                .group_by(
                    Report.report_type,
                )
            )
        ).all()


        reports_by_type = {

            report_type.value:
                count

            for report_type, count
            in type_rows

        }


        return {

            "total_reports":
                int(total or 0),

            "completed_reports":
                int(completed or 0),

            "failed_reports":
                int(failed or 0),

            "pending_reports":
                int(pending or 0),

            "expired_reports":
                int(expired or 0),

            "reports_by_format":
                reports_by_format,

            "reports_by_type":
                reports_by_type,

        }


    async def get_recent_reports(
        self,
        *,
        limit: int = 10,
    ) -> list[ReportSummary]:
        """
        Return recently created reports.
        """

        stmt = (
            select(Report)
            .order_by(
                Report.created_at.desc(),
            )
            .limit(limit)
        )


        result = self.db.execute(
            stmt,
        )


        reports = list(
            result.scalars().all()
        )


        return self.serialize_reports(
            reports,
        )


    async def get_failed_reports(
        self,
        *,
        limit: int = 50,
    ) -> list[ReportSummary]:
        """
        Return reports which failed generation.
        """

        stmt = (
            select(Report)
            .where(
                Report.status
                == ReportStatus.FAILED,
            )
            .order_by(
                Report.created_at.desc(),
            )
            .limit(limit)
        )


        result = self.db.execute(
            stmt,
        )


        reports = list(
            result.scalars().all()
        )


        return self.serialize_reports(
            reports,
        )
        # ============================================================
    # Cleanup Utilities
    # ============================================================

    async def delete_report(
        self,
        report_id: UUID,
    ) -> bool:
        """
        Permanently delete a report record.

        Physical file deletion is intentionally not performed.
        Storage cleanup should be handled by a dedicated worker.
        """

        report = await self.get_report_model(
            report_id,
        )

        if report is None:
            raise ValueError(
                "Report not found."
            )


        try:

            self.db.delete(
                report,
            )

            await self.commit()


            logger.info(
                "Deleted report. id=%s",
                report_id,
            )


            return True


        except Exception:

            logger.exception(
                "Failed deleting report. id=%s",
                report_id,
            )

            raise



    async def cleanup_expired_reports(
        self,
        *,
        older_than_days: int = 90,
    ) -> int:
        """
        Remove expired reports older than a retention period.

        Intended for scheduled maintenance jobs.
        """

        cutoff = (
            datetime.utcnow()
            - timedelta(
                days=older_than_days,
            )
        )


        stmt = (
            select(Report)
            .where(
                Report.status
                == ReportStatus.EXPIRED,

                Report.updated_at
                <= cutoff,
            )
        )


        result = self.db.execute(
            stmt,
        )


        reports = list(
            result.scalars().all()
        )


        for report in reports:

            self.db.delete(
                report,
            )


        if reports:

            await self.commit()


        logger.info(
            "Cleaned up %s expired reports.",
            len(reports),
        )


        return len(reports)



    async def refresh_report_metadata(
        self,
        report_id: UUID,
    ) -> ReportResponse:
        """
        Recalculate file metadata.

        Useful after external storage operations.
        """

        report = await self.get_report_model(
            report_id,
        )

        if report is None:

            raise ValueError(
                "Report not found."
            )


        if report.file_path:

            report.file_size_bytes = (
                self.calculate_file_size(
                    report.file_path,
                )
            )

            report.checksum = (
                self.calculate_checksum(
                    report.file_path,
                )
            )


        await self.commit()

        self.db.refresh(
            report,
        )


        return self._response(
            report,
        )



    async def clone_report_configuration(
        self,
        report_id: UUID,
    ) -> ReportResponse:
        """
        Clone only report configuration.

        Useful when users want to regenerate
        a report with the same parameters.
        """

        source = await self.get_report_model(
            report_id,
        )


        if source is None:

            raise ValueError(
                "Report not found."
            )


        clone = Report(

            scan_id=source.scan_id,

            generated_by_id=source.generated_by_id,

            title=f"{source.title} Clone",

            report_type=source.report_type,

            report_format=source.report_format,

            status=ReportStatus.PENDING,

            expires_at=self.calculate_expiry(),

        )


        self.db.add(
            clone,
        )


        await self.commit()

        self.db.refresh(
            clone,
        )


        return self._response(
            clone,
        )



# ============================================================
# End of File
# ============================================================
