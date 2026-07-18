"""
QShield Enterprise
==================

Finding Service

Business logic layer for managing security findings.

A Finding represents a security issue discovered during
a scan execution.

This service is independent from FastAPI and can be used by:

- REST API
- Scanner workers
- Celery tasks
- Risk engine
- Reporting engine
- Compliance workflows
- CLI tools

Responsibilities
-----------------

• Finding CRUD operations
• Severity management
• Risk calculation
• CVSS handling
• Scanner ingestion
• Finding lifecycle
• Analytics
• Reporting support

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
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.finding import Finding
from app.models.finding import FindingSeverity
from app.models.finding import FindingStatus

from app.models.scan import Scan


from app.schemas.finding import (
    FindingCreate,
    FindingDashboard,
    FindingListResponse,
    FindingResponse,
    FindingSummary,
    FindingUpdate,
)


logger = logging.getLogger(__name__)


class FindingService:
    """
    Enterprise Finding Service.

    Manages the complete lifecycle of security findings.

    Lifecycle:

        DISCOVERED
             |
             v
        OPEN
             |
        +----+----+
        |         |
        v         v
     FIXED     ACCEPTED
    """


    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db


    # ============================================================
    # Validation Helpers
    # ============================================================

    @staticmethod
    def normalize_title(
        value: str,
    ) -> str:
        """
        Normalize finding title.
        """

        return (
            value
            .strip()
            .replace(
                "  ",
                " ",
            )
        )


    @staticmethod
    def normalize_cvss(
        score: float | None,
    ) -> float:
        """
        Normalize CVSS score.

        CVSS range:
        0.0 - 10.0
        """

        if score is None:
            return 0.0


        return round(
            max(
                0.0,
                min(
                    10.0,
                    score,
                ),
            ),
            1,
        )


    @staticmethod
    def calculate_risk_score(
        severity: FindingSeverity,
        cvss_score: float,
    ) -> float:
        """
        Calculate internal risk score.

        Converts CVSS severity into
        QShield risk scale:

        0 - 100
        """

        multiplier = {

            FindingSeverity.CRITICAL:
                10,

            FindingSeverity.HIGH:
                8,

            FindingSeverity.MEDIUM:
                5,

            FindingSeverity.LOW:
                2,

            FindingSeverity.INFO:
                0.5,

        }


        return round(
            min(
                100,
                cvss_score
                *
                multiplier.get(
                    severity,
                    1,
                ),
            ),
            2,
        )


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


        count = await self.db.scalar(
            stmt,
        )


        return bool(count)
        # ============================================================
    # Database Helpers
    # ============================================================

    async def get_finding_model(
        self,
        finding_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> Finding | None:
        """
        Retrieve Finding ORM object.
        """

        stmt = (
            select(Finding)
            .where(
                Finding.id == finding_id,
            )
        )


        if not include_deleted:

            stmt = stmt.where(
                Finding.deleted_at.is_(None),
            )


        result = await self.db.execute(
            stmt,
        )


        return result.scalar_one_or_none()



    async def get_scan_model(
        self,
        scan_id: UUID,
    ) -> Scan | None:
        """
        Retrieve related scan.
        """

        stmt = (
            select(Scan)
            .where(
                Scan.id == scan_id,
                Scan.deleted_at.is_(None),
            )
        )


        result = await self.db.execute(
            stmt,
        )


        return result.scalar_one_or_none()



    async def finding_exists(
        self,
        scan_id: UUID,
        title: str,
    ) -> bool:
        """
        Check duplicate finding.

        Prevents duplicate findings
        from scanner retries.
        """

        stmt = (
            select(func.count())
            .select_from(
                Finding,
            )
            .where(

                Finding.scan_id == scan_id,

                func.lower(
                    Finding.title,
                )
                ==
                title.lower(),

                Finding.deleted_at.is_(None),

            )
        )


        count = await self.db.scalar(
            stmt,
        )


        return bool(count)



    async def commit(
        self,
    ) -> None:
        """
        Commit transaction safely.
        """

        try:

            await self.db.commit()


        except Exception:

            await self.db.rollback()


            logger.exception(
                "Database commit failed."
            )

            raise



    async def rollback(
        self,
    ) -> None:
        """
        Rollback current transaction.
        """

        await self.db.rollback()
            # ============================================================
    # Serialization Helpers
    # ============================================================

    @staticmethod
    def _summary(
        finding: Finding,
    ) -> FindingSummary:
        """
        Convert Finding ORM object into summary schema.
        """

        return FindingSummary(

            id=finding.id,

            created_at=finding.created_at,

            updated_at=finding.updated_at,

            scan_id=finding.scan_id,

            title=finding.title,

            severity=finding.severity,

            status=finding.status,

            cvss_score=finding.cvss_score,

            risk_score=finding.risk_score,

            category=finding.category,

            discovered_at=finding.discovered_at,

        )



    @staticmethod
    def _response(
        finding: Finding,
    ) -> FindingResponse:
        """
        Convert Finding ORM object into response schema.
        """

        return FindingResponse(

            id=finding.id,

            created_at=finding.created_at,

            updated_at=finding.updated_at,

            scan_id=finding.scan_id,

            title=finding.title,

            description=finding.description,

            severity=finding.severity,

            status=finding.status,

            category=finding.category,

            cvss_score=finding.cvss_score,

            risk_score=finding.risk_score,

            cve_id=finding.cve_id,

            affected_component=finding.affected_component,

            remediation=finding.remediation,

            evidence=finding.evidence,

            discovered_at=finding.discovered_at,

            resolved_at=finding.resolved_at,

        )



    @staticmethod
    def serialize_collection(
        findings: list[Finding],
    ) -> list[FindingSummary]:
        """
        Convert finding collection to summaries.
        """

        return [

            FindingService._summary(
                finding,
            )

            for finding in findings

        ]



    # ============================================================
    # Validation
    # ============================================================

    @staticmethod
    def validate_severity(
        severity: FindingSeverity,
    ) -> None:
        """
        Validate finding severity.
        """

        if severity not in FindingSeverity:

            raise ValueError(
                "Unsupported finding severity."
            )



    @staticmethod
    def validate_status(
        status: FindingStatus,
    ) -> None:
        """
        Validate finding status.
        """

        if status not in FindingStatus:

            raise ValueError(
                "Unsupported finding status."
            )
            # ============================================================
    # Create Finding
    # ============================================================

    async def create_finding(
        self,
        payload: FindingCreate,
    ) -> FindingResponse:
        """
        Create a security finding.

        Workflow
        --------

        1. Validate scan
        2. Prevent duplicate findings
        3. Normalize data
        4. Calculate risk score
        5. Store finding
        """

        if not await self.scan_exists(
            payload.scan_id,
        ):
            raise ValueError(
                "Scan does not exist."
            )


        title = self.normalize_title(
            payload.title,
        )


        if await self.finding_exists(
            payload.scan_id,
            title,
        ):
            raise ValueError(
                "Finding already exists."
            )


        self.validate_severity(
            payload.severity,
        )


        self.validate_status(
            payload.status,
        )


        cvss_score = (
            self.normalize_cvss(
                payload.cvss_score,
            )
        )


        risk_score = (
            self.calculate_risk_score(
                payload.severity,
                cvss_score,
            )
        )


        finding = Finding(

            scan_id=payload.scan_id,

            title=title,

            description=payload.description,

            severity=payload.severity,

            status=payload.status,

            category=payload.category,

            cvss_score=cvss_score,

            risk_score=risk_score,

            cve_id=payload.cve_id,

            affected_component=(
                payload.affected_component
            ),

            remediation=payload.remediation,

            evidence=payload.evidence,

            discovered_at=(
                datetime.utcnow()
            ),

        )


        self.db.add(
            finding,
        )


        try:

            await self.commit()

            await self.db.refresh(
                finding,
            )


            logger.info(
                "Created finding. id=%s scan=%s",
                finding.id,
                finding.scan_id,
            )


            return self._response(
                finding,
            )


        except Exception:

            logger.exception(
                "Failed creating finding."
            )

            raise



    async def duplicate_finding(
        self,
        finding_id: UUID,
    ) -> FindingResponse:
        """
        Duplicate finding definition.

        Creates a new open finding.
        """

        source = await self.get_finding_model(
            finding_id,
        )


        if source is None:
            raise ValueError(
                "Finding not found."
            )


        duplicate = Finding(

            scan_id=source.scan_id,

            title=f"{source.title} Copy",

            description=source.description,

            severity=source.severity,

            status=FindingStatus.OPEN,

            category=source.category,

            cvss_score=source.cvss_score,

            risk_score=source.risk_score,

            cve_id=source.cve_id,

            affected_component=(
                source.affected_component
            ),

            remediation=source.remediation,

            evidence=source.evidence,

            discovered_at=datetime.utcnow(),

        )


        self.db.add(
            duplicate,
        )


        await self.commit()

        await self.db.refresh(
            duplicate,
        )


        return self._response(
            duplicate,
        )
        # ============================================================
    # Retrieve Findings
    # ============================================================

    async def get_finding(
        self,
        finding_id: UUID,
    ) -> FindingResponse:
        """
        Retrieve finding by ID.
        """

        finding = await self.get_finding_model(
            finding_id,
        )


        if finding is None:
            raise ValueError(
                "Finding not found."
            )


        return self._response(
            finding,
        )



    async def get_finding_summary(
        self,
        finding_id: UUID,
    ) -> FindingSummary:
        """
        Retrieve lightweight finding details.
        """

        finding = await self.get_finding_model(
            finding_id,
        )


        if finding is None:
            raise ValueError(
                "Finding not found."
            )


        return self._summary(
            finding,
        )



    async def get_scan_findings(
        self,
        scan_id: UUID,
        *,
        severity: FindingSeverity | None = None,
        status: FindingStatus | None = None,
    ) -> list[FindingSummary]:
        """
        Retrieve findings for a scan.

        Supports filtering by:

        - Severity
        - Status
        """

        filters = [

            Finding.scan_id == scan_id,

            Finding.deleted_at.is_(None),

        ]


        if severity:

            filters.append(
                Finding.severity == severity,
            )


        if status:

            filters.append(
                Finding.status == status,
            )


        stmt = (
            select(Finding)
            .where(
                *filters,
            )
            .order_by(
                Finding.created_at.desc(),
            )
        )


        result = await self.db.execute(
            stmt,
        )


        findings = list(
            result.scalars().all()
        )


        return self.serialize_collection(
            findings,
        )



    async def get_latest_findings(
        self,
        *,
        limit: int = 20,
    ) -> list[FindingSummary]:
        """
        Return recently discovered findings.
        """

        stmt = (
            select(Finding)
            .where(
                Finding.deleted_at.is_(None),
            )
            .order_by(
                Finding.created_at.desc(),
            )
            .limit(limit)
        )


        result = await self.db.execute(
            stmt,
        )


        return self.serialize_collection(
            list(
                result.scalars().all()
            )
        )



    async def finding_count(
        self,
        *,
        scan_id: UUID | None = None,
    ) -> int:
        """
        Count findings.

        Optional:
        - By scan
        """

        stmt = (
            select(func.count())
            .select_from(
                Finding,
            )
            .where(
                Finding.deleted_at.is_(None),
            )
        )


        if scan_id:

            stmt = stmt.where(
                Finding.scan_id == scan_id,
            )


        count = await self.db.scalar(
            stmt,
        )


        return int(
            count or 0
        )
        # ============================================================
    # List Findings
    # ============================================================

    async def list_findings(
        self,
        *,
        scan_id: UUID | None = None,
        severity: FindingSeverity | None = None,
        status: FindingStatus | None = None,
        category: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 25,
    ) -> FindingListResponse:
        """
        Retrieve paginated findings.

        Supports filtering by:

        - Scan
        - Severity
        - Status
        - Category
        - Text search
        """

        filters = [

            Finding.deleted_at.is_(None),

        ]


        if scan_id:

            filters.append(
                Finding.scan_id == scan_id,
            )


        if severity:

            filters.append(
                Finding.severity == severity,
            )


        if status:

            filters.append(
                Finding.status == status,
            )


        if category:

            filters.append(
                Finding.category == category,
            )


        if search:

            pattern = (
                f"%{search.strip()}%"
            )

            filters.append(

                or_(

                    Finding.title.ilike(
                        pattern,
                    ),

                    Finding.description.ilike(
                        pattern,
                    ),

                    Finding.cve_id.ilike(
                        pattern,
                    ),

                )

            )


        # --------------------------------------------------------
        # Count
        # --------------------------------------------------------

        count_stmt = (
            select(func.count())
            .select_from(
                Finding,
            )
            .where(
                *filters,
            )
        )


        total = await self.db.scalar(
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



        stmt = (
            select(Finding)
            .where(
                *filters,
            )
            .order_by(
                Finding.risk_score.desc(),
                Finding.created_at.desc(),
            )
            .offset(
                offset,
            )
            .limit(
                page_size,
            )
        )


        result = await self.db.execute(
            stmt,
        )


        findings = list(
            result.scalars().all()
        )


        total_pages = (
            (total + page_size - 1)
            // page_size
            if total
            else 1
        )


        return FindingListResponse(

            findings=self.serialize_collection(
                findings,
            ),

            total=total,

            page=page,

            page_size=page_size,

            total_pages=total_pages,

        )



    async def search_findings(
        self,
        query: str,
        *,
        limit: int = 50,
    ) -> list[FindingSummary]:
        """
        Search findings globally.
        """

        pattern = (
            f"%{query.strip()}%"
        )


        stmt = (
            select(Finding)
            .where(

                Finding.deleted_at.is_(None),

                or_(

                    Finding.title.ilike(
                        pattern,
                    ),

                    Finding.description.ilike(
                        pattern,
                    ),

                    Finding.cve_id.ilike(
                        pattern,
                    ),

                    Finding.category.ilike(
                        pattern,
                    ),

                ),

            )
            .order_by(
                Finding.risk_score.desc(),
            )
            .limit(limit)
        )


        result = await self.db.execute(
            stmt,
        )


        findings = list(
            result.scalars().all()
        )


        return self.serialize_collection(
            findings,
        )
        # ============================================================
    # List Findings
    # ============================================================

    async def list_findings(
        self,
        *,
        scan_id: UUID | None = None,
        severity: FindingSeverity | None = None,
        status: FindingStatus | None = None,
        category: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 25,
    ) -> FindingListResponse:
        """
        Retrieve paginated findings.

        Supports filtering by:

        - Scan
        - Severity
        - Status
        - Category
        - Text search
        """

        filters = [

            Finding.deleted_at.is_(None),

        ]


        if scan_id:

            filters.append(
                Finding.scan_id == scan_id,
            )


        if severity:

            filters.append(
                Finding.severity == severity,
            )


        if status:

            filters.append(
                Finding.status == status,
            )


        if category:

            filters.append(
                Finding.category == category,
            )


        if search:

            pattern = (
                f"%{search.strip()}%"
            )

            filters.append(

                or_(

                    Finding.title.ilike(
                        pattern,
                    ),

                    Finding.description.ilike(
                        pattern,
                    ),

                    Finding.cve_id.ilike(
                        pattern,
                    ),

                )

            )


        # --------------------------------------------------------
        # Count
        # --------------------------------------------------------

        count_stmt = (
            select(func.count())
            .select_from(
                Finding,
            )
            .where(
                *filters,
            )
        )


        total = await self.db.scalar(
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



        stmt = (
            select(Finding)
            .where(
                *filters,
            )
            .order_by(
                Finding.risk_score.desc(),
                Finding.created_at.desc(),
            )
            .offset(
                offset,
            )
            .limit(
                page_size,
            )
        )


        result = await self.db.execute(
            stmt,
        )


        findings = list(
            result.scalars().all()
        )


        total_pages = (
            (total + page_size - 1)
            // page_size
            if total
            else 1
        )


        return FindingListResponse(

            findings=self.serialize_collection(
                findings,
            ),

            total=total,

            page=page,

            page_size=page_size,

            total_pages=total_pages,

        )



    async def search_findings(
        self,
        query: str,
        *,
        limit: int = 50,
    ) -> list[FindingSummary]:
        """
        Search findings globally.
        """

        pattern = (
            f"%{query.strip()}%"
        )


        stmt = (
            select(Finding)
            .where(

                Finding.deleted_at.is_(None),

                or_(

                    Finding.title.ilike(
                        pattern,
                    ),

                    Finding.description.ilike(
                        pattern,
                    ),

                    Finding.cve_id.ilike(
                        pattern,
                    ),

                    Finding.category.ilike(
                        pattern,
                    ),

                ),

            )
            .order_by(
                Finding.risk_score.desc(),
            )
            .limit(limit)
        )


        result = await self.db.execute(
            stmt,
        )


        findings = list(
            result.scalars().all()
        )


        return self.serialize_collection(
            findings,
        )
        # ============================================================
    # Finding Lifecycle Management
    # ============================================================

    async def update_finding(
        self,
        finding_id: UUID,
        payload: FindingUpdate,
    ) -> FindingResponse:
        """
        Update finding metadata.

        Supports:

        - Title
        - Description
        - Severity
        - Status
        - Remediation
        - Evidence
        """

        finding = await self.get_finding_model(
            finding_id,
        )


        if finding is None:
            raise ValueError(
                "Finding not found."
            )


        updates = payload.model_dump(
            exclude_none=True,
        )


        if "title" in updates:

            finding.title = (
                self.normalize_title(
                    updates.pop(
                        "title",
                    )
                )
            )


        if "severity" in updates:

            self.validate_severity(
                updates["severity"],
            )


        if "status" in updates:

            self.validate_status(
                updates["status"],
            )


        for field, value in updates.items():

            setattr(
                finding,
                field,
                value,
            )


        if (
            "severity" in updates
            or "cvss_score" in updates
        ):

            finding.risk_score = (
                self.calculate_risk_score(
                    finding.severity,
                    finding.cvss_score,
                )
            )


        await self.commit()

        await self.db.refresh(
            finding,
        )


        logger.info(
            "Updated finding. id=%s",
            finding.id,
        )


        return self._response(
            finding,
        )



    async def change_status(
        self,
        finding_id: UUID,
        status: FindingStatus,
    ) -> FindingResponse:
        """
        Change finding lifecycle status.
        """

        finding = await self.get_finding_model(
            finding_id,
        )


        if finding is None:

            raise ValueError(
                "Finding not found."
            )


        self.validate_status(
            status,
        )


        finding.status = status


        if status in (

            FindingStatus.RESOLVED,

            FindingStatus.ACCEPTED,

        ):

            finding.resolved_at = (
                datetime.utcnow()
            )


        await self.commit()

        await self.db.refresh(
            finding,
        )


        return self._response(
            finding,
        )



    async def resolve_finding(
        self,
        finding_id: UUID,
    ) -> FindingResponse:
        """
        Mark finding as resolved.
        """

        return await self.change_status(
            finding_id,
            FindingStatus.RESOLVED,
        )



    async def accept_risk(
        self,
        finding_id: UUID,
    ) -> FindingResponse:
        """
        Mark finding as accepted risk.

        Used for exceptions and
        compliance workflows.
        """

        return await self.change_status(
            finding_id,
            FindingStatus.ACCEPTED,
        )



    async def reopen_finding(
        self,
        finding_id: UUID,
    ) -> FindingResponse:
        """
        Reopen resolved finding.
        """

        return await self.change_status(
            finding_id,
            FindingStatus.OPEN,
        )
        # ============================================================
    # Risk Management
    # ============================================================

    async def recalculate_risk(
        self,
        finding_id: UUID,
    ) -> FindingResponse:
        """
        Recalculate finding risk score.

        Formula is based on:

        - Severity
        - CVSS score
        """

        finding = await self.get_finding_model(
            finding_id,
        )


        if finding is None:

            raise ValueError(
                "Finding not found."
            )


        finding.risk_score = (
            self.calculate_risk_score(
                finding.severity,
                finding.cvss_score,
            )
        )


        await self.commit()

        await self.db.refresh(
            finding,
        )


        return self._response(
            finding,
        )



    async def update_cvss_score(
        self,
        finding_id: UUID,
        cvss_score: float,
    ) -> FindingResponse:
        """
        Update CVSS score.

        Automatically recalculates
        internal risk score.
        """

        finding = await self.get_finding_model(
            finding_id,
        )


        if finding is None:

            raise ValueError(
                "Finding not found."
            )


        finding.cvss_score = (
            self.normalize_cvss(
                cvss_score,
            )
        )


        finding.risk_score = (
            self.calculate_risk_score(
                finding.severity,
                finding.cvss_score,
            )
        )


        await self.commit()

        await self.db.refresh(
            finding,
        )


        return self._response(
            finding,
        )



    async def update_severity(
        self,
        finding_id: UUID,
        severity: FindingSeverity,
    ) -> FindingResponse:
        """
        Update finding severity.

        Recalculates risk automatically.
        """

        finding = await self.get_finding_model(
            finding_id,
        )


        if finding is None:

            raise ValueError(
                "Finding not found."
            )


        self.validate_severity(
            severity,
        )


        finding.severity = severity


        finding.risk_score = (
            self.calculate_risk_score(
                severity,
                finding.cvss_score,
            )
        )


        await self.commit()

        await self.db.refresh(
            finding,
        )


        return self._response(
            finding,
        )



    async def increase_risk(
        self,
        finding_id: UUID,
        amount: float,
    ) -> FindingResponse:
        """
        Increase finding risk score manually.
        """

        finding = await self.get_finding_model(
            finding_id,
        )


        if finding is None:

            raise ValueError(
                "Finding not found."
            )


        finding.risk_score = min(
            100,
            finding.risk_score + amount,
        )


        await self.commit()

        await self.db.refresh(
            finding,
        )


        return self._response(
            finding,
        )



    async def decrease_risk(
        self,
        finding_id: UUID,
        amount: float,
    ) -> FindingResponse:
        """
        Reduce finding risk score manually.
        """

        finding = await self.get_finding_model(
            finding_id,
        )


        if finding is None:

            raise ValueError(
                "Finding not found."
            )


        finding.risk_score = max(
            0,
            finding.risk_score - amount,
        )


        await self.commit()

        await self.db.refresh(
            finding,
        )


        return self._response(
            finding,
        )
        # ============================================================
    # Scanner Ingestion
    # ============================================================

    async def ingest_scanner_findings(
        self,
        scan_id: UUID,
        findings: list[dict[str, Any]],
    ) -> list[FindingSummary]:
        """
        Bulk ingest findings from scanner engines.

        Used by:

        - Nmap scanner
        - TLS scanner
        - PQC scanner
        - HTTP scanner
        - Compliance scanner
        """

        if not await self.scan_exists(
            scan_id,
        ):
            raise ValueError(
                "Scan does not exist."
            )


        created: list[Finding] = []


        for item in findings:

            title = self.normalize_title(
                item.get(
                    "title",
                    "Unknown Finding",
                )
            )


            if await self.finding_exists(
                scan_id,
                title,
            ):
                continue


            severity = item.get(
                "severity",
                FindingSeverity.INFO,
            )


            if isinstance(
                severity,
                str,
            ):
                severity = (
                    FindingSeverity(
                        severity.lower()
                    )
                )


            cvss = self.normalize_cvss(
                item.get(
                    "cvss_score",
                    0,
                )
            )


            finding = Finding(

                scan_id=scan_id,

                title=title,

                description=item.get(
                    "description",
                ),

                severity=severity,

                status=(
                    FindingStatus.OPEN
                ),

                category=item.get(
                    "category",
                ),

                cvss_score=cvss,

                risk_score=(
                    self.calculate_risk_score(
                        severity,
                        cvss,
                    )
                ),

                cve_id=item.get(
                    "cve_id",
                ),

                affected_component=item.get(
                    "affected_component",
                ),

                remediation=item.get(
                    "remediation",
                ),

                evidence=item.get(
                    "evidence",
                ),

                discovered_at=datetime.utcnow(),

            )


            self.db.add(
                finding,
            )


            created.append(
                finding,
            )


        if created:

            await self.commit()


            for finding in created:

                await self.db.refresh(
                    finding,
                )


        logger.info(
            "Ingested %s findings for scan=%s",
            len(created),
            scan_id,
        )


        return self.serialize_collection(
            created,
        )



    async def bulk_update_status(
        self,
        finding_ids: list[UUID],
        status: FindingStatus,
    ) -> int:
        """
        Update multiple finding statuses.
        """

        self.validate_status(
            status,
        )


        stmt = (
            select(Finding)
            .where(
                Finding.id.in_(
                    finding_ids,
                ),
            )
        )


        result = await self.db.execute(
            stmt,
        )


        findings = list(
            result.scalars().all()
        )


        for finding in findings:

            finding.status = status


            if status in (

                FindingStatus.RESOLVED,

                FindingStatus.ACCEPTED,

            ):

                finding.resolved_at = (
                    datetime.utcnow()
                )


        if findings:

            await self.commit()


        return len(findings)



    async def delete_finding(
        self,
        finding_id: UUID,
        *,
        hard_delete: bool = False,
    ) -> None:
        """
        Delete finding.

        Default:
            Soft delete

        Optional:
            Permanent deletion
        """

        finding = await self.get_finding_model(
            finding_id,
            include_deleted=True,
        )


        if finding is None:

            raise ValueError(
                "Finding not found."
            )


        if hard_delete:

            await self.db.delete(
                finding,
            )

        else:

            finding.soft_delete()


        await self.commit()


        logger.info(
            "Deleted finding. id=%s",
            finding_id,
        )
            # ============================================================
    # Finding Statistics
    # ============================================================

    async def get_statistics(
        self,
        *,
        scan_id: UUID | None = None,
    ) -> dict[str, Any]:
        """
        Return finding statistics.

        Includes:

        - Total findings
        - Severity distribution
        - Status distribution
        - Average risk score
        """

        filters = [

            Finding.deleted_at.is_(None),

        ]


        if scan_id:

            filters.append(
                Finding.scan_id == scan_id,
            )


        total = await self.db.scalar(
            select(func.count())
            .select_from(
                Finding,
            )
            .where(
                *filters,
            )
        )


        avg_risk = await self.db.scalar(
            select(
                func.avg(
                    Finding.risk_score,
                )
            )
            .where(
                *filters,
            )
        )



        # --------------------------------------------------------
        # Severity Distribution
        # --------------------------------------------------------

        severity_rows = await self.db.execute(
            select(
                Finding.severity,
                func.count(
                    Finding.id,
                ),
            )
            .where(
                *filters,
            )
            .group_by(
                Finding.severity,
            )
        )


        severity_distribution = {

            severity.value:
                count

            for severity, count
            in severity_rows.all()

        }



        # --------------------------------------------------------
        # Status Distribution
        # --------------------------------------------------------

        status_rows = await self.db.execute(
            select(
                Finding.status,
                func.count(
                    Finding.id,
                ),
            )
            .where(
                *filters,
            )
            .group_by(
                Finding.status,
            )
        )


        status_distribution = {

            status.value:
                count

            for status, count
            in status_rows.all()

        }



        return {

            "total_findings":
                int(
                    total or 0
                ),

            "average_risk_score":
                (
                    round(
                        float(avg_risk),
                        2,
                    )
                    if avg_risk
                    else 0
                ),

            "severity_distribution":
                severity_distribution,

            "status_distribution":
                status_distribution,

        }



    async def get_severity_breakdown(
        self,
        *,
        scan_id: UUID | None = None,
    ) -> dict[str, int]:
        """
        Return findings grouped by severity.
        """

        filters = [

            Finding.deleted_at.is_(None),

        ]


        if scan_id:

            filters.append(
                Finding.scan_id == scan_id,
            )


        result = await self.db.execute(
            select(
                Finding.severity,
                func.count(
                    Finding.id,
                ),
            )
            .where(
                *filters,
            )
            .group_by(
                Finding.severity,
            )
        )


        return {

            severity.value:
                count

            for severity, count
            in result.all()

        }



    async def get_high_risk_findings(
        self,
        *,
        threshold: float = 70,
        limit: int = 50,
    ) -> list[FindingSummary]:
        """
        Return high-risk findings.

        Used by:

        - SOC dashboard
        - AI recommendation engine
        - Reports
        """

        stmt = (
            select(Finding)
            .where(

                Finding.risk_score >= threshold,

                Finding.deleted_at.is_(None),

            )
            .order_by(
                Finding.risk_score.desc(),
            )
            .limit(limit)
        )


        result = await self.db.execute(
            stmt,
        )


        return self.serialize_collection(
            list(
                result.scalars().all()
            )
        )
        # ============================================================
    # Dashboard Analytics
    # ============================================================

    async def get_dashboard(
        self,
    ) -> FindingDashboard:
        """
        Build finding dashboard metrics.

        Provides:

        - Total findings
        - Severity counts
        - Open issues
        - Resolved issues
        - Critical risks
        - Recent findings
        """

        statistics = await self.get_statistics()


        critical = await self.db.scalar(
            select(func.count())
            .select_from(
                Finding,
            )
            .where(
                Finding.severity
                == FindingSeverity.CRITICAL,

                Finding.deleted_at.is_(None),
            )
        )


        open_findings = await self.db.scalar(
            select(func.count())
            .select_from(
                Finding,
            )
            .where(

                Finding.status
                == FindingStatus.OPEN,

                Finding.deleted_at.is_(None),

            )
        )


        resolved = await self.db.scalar(
            select(func.count())
            .select_from(
                Finding,
            )
            .where(

                Finding.status
                == FindingStatus.RESOLVED,

                Finding.deleted_at.is_(None),

            )
        )


        recent_stmt = (
            select(Finding)
            .where(
                Finding.deleted_at.is_(None),
            )
            .order_by(
                Finding.created_at.desc(),
            )
            .limit(10)
        )


        recent_result = await self.db.execute(
            recent_stmt,
        )


        recent_findings = list(
            recent_result.scalars().all()
        )


        return FindingDashboard(

            total_findings=(
                statistics[
                    "total_findings"
                ]
            ),

            average_risk_score=(
                statistics[
                    "average_risk_score"
                ]
            ),

            critical_findings=(
                int(
                    critical or 0
                )
            ),

            open_findings=(
                int(
                    open_findings or 0
                )
            ),

            resolved_findings=(
                int(
                    resolved or 0
                )
            ),

            severity_distribution=(
                statistics[
                    "severity_distribution"
                ]
            ),

            status_distribution=(
                statistics[
                    "status_distribution"
                ]
            ),

            recent_findings=(
                self.serialize_collection(
                    recent_findings,
                )
            ),

        )



    async def get_unresolved_findings(
        self,
        *,
        limit: int = 100,
    ) -> list[FindingSummary]:
        """
        Return findings requiring action.

        Includes:

        - Open
        - In Progress
        """

        stmt = (
            select(Finding)
            .where(

                Finding.status.in_(
                    [
                        FindingStatus.OPEN,
                        FindingStatus.IN_PROGRESS,
                    ]
                ),

                Finding.deleted_at.is_(None),

            )
            .order_by(
                Finding.risk_score.desc(),
            )
            .limit(limit)
        )


        result = await self.db.execute(
            stmt,
        )


        return self.serialize_collection(
            list(
                result.scalars().all()
            )
        )



    async def get_security_posture_score(
        self,
    ) -> float:
        """
        Calculate overall security posture score.

        Score:

        100 = No risk
        0   = Maximum risk
        """

        avg_risk = await self.db.scalar(
            select(
                func.avg(
                    Finding.risk_score,
                )
            )
            .where(
                Finding.deleted_at.is_(None),
                Finding.status
                != FindingStatus.RESOLVED,
            )
        )


        if avg_risk is None:

            return 100.0


        return round(
            max(
                0,
                100 - float(avg_risk),
            ),
            2,
        )
        # ============================================================
    # Export Utilities
    # ============================================================

    async def export_finding(
        self,
        finding_id: UUID,
    ) -> dict[str, Any]:
        """
        Export complete finding metadata.

        Used by:

        - Reports
        - Compliance exports
        - External integrations
        """

        finding = await self.get_finding_model(
            finding_id,
        )


        if finding is None:

            raise ValueError(
                "Finding not found."
            )


        return finding.to_dict()



    async def export_scan_findings(
        self,
        scan_id: UUID,
    ) -> list[dict[str, Any]]:
        """
        Export all findings for a scan.
        """

        stmt = (
            select(Finding)
            .where(
                Finding.scan_id == scan_id,

                Finding.deleted_at.is_(None),
            )
            .order_by(
                Finding.risk_score.desc(),
            )
        )


        result = await self.db.execute(
            stmt,
        )


        findings = list(
            result.scalars().all()
        )


        return [

            finding.to_dict()

            for finding in findings

        ]



    # ============================================================
    # Cleanup
    # ============================================================

    async def restore_finding(
        self,
        finding_id: UUID,
    ) -> FindingResponse:
        """
        Restore soft deleted finding.
        """

        stmt = (
            select(Finding)
            .where(
                Finding.id == finding_id,
            )
        )


        result = await self.db.execute(
            stmt,
        )


        finding = (
            result.scalar_one_or_none()
        )


        if finding is None:

            raise ValueError(
                "Finding not found."
            )


        finding.deleted_at = None


        await self.commit()

        await self.db.refresh(
            finding,
        )


        return self._response(
            finding,
        )



    async def purge_deleted_findings(
        self,
        *,
        older_than_days: int = 180,
    ) -> int:
        """
        Permanently remove deleted findings.
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
            select(Finding)
            .where(

                Finding.deleted_at.is_not(None),

                Finding.deleted_at <= cutoff,

            )
        )


        result = await self.db.execute(
            stmt,
        )


        findings = list(
            result.scalars().all()
        )


        for finding in findings:

            await self.db.delete(
                finding,
            )


        if findings:

            await self.commit()


        logger.info(
            "Purged %s deleted findings.",
            len(findings),
        )


        return len(findings)



    async def bulk_delete_findings(
        self,
        finding_ids: list[UUID],
    ) -> int:
        """
        Soft delete multiple findings.
        """

        stmt = (
            select(Finding)
            .where(
                Finding.id.in_(
                    finding_ids,
                ),
            )
        )


        result = await self.db.execute(
            stmt,
        )


        findings = list(
            result.scalars().all()
        )


        for finding in findings:

            finding.soft_delete()


        if findings:

            await self.commit()


        return len(findings)



# ============================================================
# End of File
# ============================================================
