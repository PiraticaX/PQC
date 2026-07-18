"""
QShield Enterprise
==================

Risk Service

Central security risk intelligence engine.

This service calculates and manages:

- Finding risk scores
- Asset risk posture
- Organization security posture
- Risk prioritization
- Risk trends
- Security analytics

Used by:

- REST API
- Dashboard
- AI Recommendation Engine
- Report Generator
- Compliance Engine
- SOC Operations

Author:
QShield Enterprise
"""

from __future__ import annotations

import logging

from datetime import datetime
from typing import Any
from uuid import UUID


from sqlalchemy import func
from sqlalchemy import select


from sqlalchemy.ext.asyncio import AsyncSession


from app.models.asset import Asset
from app.models.asset import Criticality


from app.models.finding import Finding
from app.models.finding import FindingSeverity
from app.models.finding import FindingStatus


from app.models.scan import Scan



logger = logging.getLogger(__name__)


class RiskService:
    """
    Enterprise Risk Intelligence Service.

    Responsibilities
    ----------------

    • Calculate security risk

    • Aggregate finding impact

    • Calculate asset posture

    • Calculate organization posture

    • Rank security priorities

    • Provide risk analytics
    """


    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db



    # ============================================================
    # Risk Constants
    # ============================================================


    SEVERITY_WEIGHTS = {

        FindingSeverity.CRITICAL:
            100,

        FindingSeverity.HIGH:
            75,

        FindingSeverity.MEDIUM:
            50,

        FindingSeverity.LOW:
            25,

        FindingSeverity.INFO:
            5,

    }


    CRITICALITY_MULTIPLIERS = {

        Criticality.CRITICAL:
            1.5,

        Criticality.HIGH:
            1.25,

        Criticality.MEDIUM:
            1.0,

        Criticality.LOW:
            0.75,

    }



    # ============================================================
    # Helpers
    # ============================================================


    @staticmethod
    def clamp_score(
        score: float,
    ) -> float:
        """
        Keep score between 0-100.
        """

        return round(
            max(
                0,
                min(
                    100,
                    score,
                ),
            ),
            2,
        )
        # ============================================================
    # Database Helpers
    # ============================================================

    async def get_asset(
        self,
        asset_id: UUID,
    ) -> Asset | None:
        """
        Retrieve asset model.
        """

        stmt = (
            select(Asset)
            .where(
                Asset.id == asset_id,

                Asset.deleted_at.is_(None),
            )
        )


        result = await self.db.execute(
            stmt,
        )


        return result.scalar_one_or_none()



    async def get_finding(
        self,
        finding_id: UUID,
    ) -> Finding | None:
        """
        Retrieve finding model.
        """

        stmt = (
            select(Finding)
            .where(
                Finding.id == finding_id,

                Finding.deleted_at.is_(None),
            )
        )


        result = await self.db.execute(
            stmt,
        )


        return result.scalar_one_or_none()



    async def get_asset_findings(
        self,
        asset_id: UUID,
    ) -> list[Finding]:
        """
        Retrieve all findings associated
        with an asset through scans.
        """

        stmt = (
            select(Finding)
            .join(
                Scan,
            )
            .where(

                Scan.asset_id == asset_id,

                Finding.deleted_at.is_(None),

                Scan.deleted_at.is_(None),

            )
        )


        result = await self.db.execute(
            stmt,
        )


        return list(
            result.scalars().all()
        )



    async def get_asset_scans(
        self,
        asset_id: UUID,
    ) -> list[Scan]:
        """
        Retrieve all scans for asset.
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
        )


        result = await self.db.execute(
            stmt,
        )


        return list(
            result.scalars().all()
        )



    async def organization_assets(
        self,
        organization_id: UUID,
    ) -> list[Asset]:
        """
        Retrieve all organization assets.
        """

        stmt = (
            select(Asset)
            .where(

                Asset.organization_id
                ==
                organization_id,

                Asset.deleted_at.is_(None),

            )
        )


        result = await self.db.execute(
            stmt,
        )


        return list(
            result.scalars().all()
        )



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
                "Risk service commit failed."
            )

            raise
            # ============================================================
    # Risk Calculation Engine
    # ============================================================

    def calculate_finding_base_risk(
        self,
        finding: Finding,
    ) -> float:
        """
        Calculate base risk score for a finding.

        Factors:

        - Severity
        - CVSS score
        - Finding status
        """

        severity_weight = (
            self.SEVERITY_WEIGHTS.get(
                finding.severity,
                0,
            )
        )


        cvss_factor = (
            finding.cvss_score
            /
            10
        )


        base_score = (
            severity_weight
            *
            cvss_factor
        )


        # Resolved findings reduce active risk

        if (
            finding.status
            ==
            FindingStatus.RESOLVED
        ):

            base_score *= 0.05



        elif (
            finding.status
            ==
            FindingStatus.ACCEPTED
        ):

            base_score *= 0.25



        return self.clamp_score(
            base_score,
        )



    def calculate_asset_risk(
        self,
        asset: Asset,
        findings: list[Finding],
    ) -> float:
        """
        Calculate overall asset risk.

        Formula:

        Finding Impact
              +
        Asset Criticality
              +
        Exposure Factor

        Returns:

        0 - 100
        """

        if not findings:

            return 0.0



        finding_scores = [

            self.calculate_finding_base_risk(
                finding,
            )

            for finding in findings

        ]


        # Highest risks dominate

        top_risks = sorted(
            finding_scores,
            reverse=True,
        )[:5]


        finding_score = (
            sum(top_risks)
            /
            len(top_risks)
        )



        criticality_multiplier = (
            self.CRITICALITY_MULTIPLIERS.get(
                asset.criticality,
                1.0,
            )
        )


        exposure_factor = 1.0


        if asset.external:

            exposure_factor += 0.15


        if asset.internet_facing:

            exposure_factor += 0.20


        if asset.production:

            exposure_factor += 0.25



        final_score = (
            finding_score
            *
            criticality_multiplier
            *
            exposure_factor
        )


        return self.clamp_score(
            final_score,
        )



    def calculate_posture_score(
        self,
        risk_score: float,
    ) -> float:
        """
        Convert risk score into security posture.

        100 = Excellent
        0   = Critical
        """

        return self.clamp_score(
            100 - risk_score,
        )



    def risk_level(
        self,
        score: float,
    ) -> str:
        """
        Convert numeric risk score
        into readable category.
        """

        if score >= 90:

            return "critical"


        if score >= 70:

            return "high"


        if score >= 40:

            return "medium"


        if score >= 10:

            return "low"


        return "minimal"
        # ============================================================
    # Finding Risk Calculation APIs
    # ============================================================

    async def calculate_finding_risk(
        self,
        finding_id: UUID,
    ) -> dict[str, Any]:
        """
        Calculate and return finding risk intelligence.

        Returns:

        - Base risk score
        - Severity
        - CVSS
        - Risk level
        """

        finding = await self.get_finding(
            finding_id,
        )


        if finding is None:

            raise ValueError(
                "Finding not found."
            )


        risk_score = (
            self.calculate_finding_base_risk(
                finding,
            )
        )


        return {

            "finding_id":
                str(finding.id),

            "severity":
                finding.severity.value,

            "cvss_score":
                finding.cvss_score,

            "risk_score":
                risk_score,

            "risk_level":
                self.risk_level(
                    risk_score,
                ),

            "status":
                finding.status.value,

        }



    async def update_finding_risk(
        self,
        finding_id: UUID,
    ) -> Finding:
        """
        Recalculate and store finding risk.

        Keeps database risk value
        synchronized.
        """

        finding = await self.get_finding(
            finding_id,
        )


        if finding is None:

            raise ValueError(
                "Finding not found."
            )


        finding.risk_score = (
            self.calculate_finding_base_risk(
                finding,
            )
        )


        await self.commit()


        await self.db.refresh(
            finding,
        )


        logger.info(
            "Updated finding risk. id=%s score=%s",
            finding.id,
            finding.risk_score,
        )


        return finding



    async def bulk_update_finding_risk(
        self,
        finding_ids: list[UUID],
    ) -> int:
        """
        Recalculate risk for multiple findings.
        """

        updated = 0


        for finding_id in finding_ids:

            try:

                await self.update_finding_risk(
                    finding_id,
                )

                updated += 1


            except ValueError:

                continue


        return updated



    async def calculate_scan_risk(
        self,
        scan_id: UUID,
    ) -> float:
        """
        Calculate risk score for a scan.

        Aggregates all findings
        belonging to the scan.
        """

        stmt = (
            select(Finding)
            .where(

                Finding.scan_id == scan_id,

                Finding.deleted_at.is_(None),

            )
        )


        result = await self.db.execute(
            stmt,
        )


        findings = list(
            result.scalars().all()
        )


        if not findings:

            return 0.0



        scores = [

            self.calculate_finding_base_risk(
                finding,
            )

            for finding in findings

        ]


        return self.clamp_score(
            max(scores),
        )
        # ============================================================
    # Asset Risk Management
    # ============================================================

    async def calculate_asset_risk_score(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Calculate complete asset risk posture.

        Includes:

        - Finding impact
        - Asset criticality
        - Exposure
        - Production impact
        """

        asset = await self.get_asset(
            asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        findings = await self.get_asset_findings(
            asset_id,
        )


        risk_score = (
            self.calculate_asset_risk(
                asset,
                findings,
            )
        )


        return {

            "asset_id":
                str(asset.id),

            "asset_name":
                asset.asset_name,

            "criticality":
                asset.criticality.value,

            "external":
                asset.external,

            "production":
                asset.production,

            "finding_count":
                len(findings),

            "risk_score":
                risk_score,

            "risk_level":
                self.risk_level(
                    risk_score,
                ),

            "posture_score":
                self.calculate_posture_score(
                    risk_score,
                ),

        }



    async def update_asset_risk(
        self,
        asset_id: UUID,
    ) -> Asset:
        """
        Calculate and store asset risk score.
        """

        asset = await self.get_asset(
            asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        findings = await self.get_asset_findings(
            asset_id,
        )


        risk_score = (
            self.calculate_asset_risk(
                asset,
                findings,
            )
        )


        asset.update_risk_score(
            risk_score,
        )


        await self.commit()


        await self.db.refresh(
            asset,
        )


        logger.info(
            "Updated asset risk. asset=%s score=%s",
            asset.id,
            asset.risk_score,
        )


        return asset



    async def bulk_update_asset_risk(
        self,
        asset_ids: list[UUID],
    ) -> int:
        """
        Recalculate risk for multiple assets.
        """

        updated = 0


        for asset_id in asset_ids:

            try:

                await self.update_asset_risk(
                    asset_id,
                )

                updated += 1


            except ValueError:

                continue


        return updated



    async def recalculate_all_assets(
        self,
        organization_id: UUID,
    ) -> int:
        """
        Recalculate risk for all assets
        in an organization.
        """

        assets = await self.organization_assets(
            organization_id,
        )


        updated = 0


        for asset in assets:

            await self.update_asset_risk(
                asset.id,
            )

            updated += 1


        return updated
        # ============================================================
    # Organization Risk Posture
    # ============================================================

    async def calculate_organization_risk(
        self,
        organization_id: UUID,
    ) -> dict[str, Any]:
        """
        Calculate overall organization security posture.

        Aggregates:

        - Asset risk
        - Critical assets
        - Finding exposure
        - Average risk
        """

        assets = await self.organization_assets(
            organization_id,
        )


        if not assets:

            return {

                "organization_id":
                    str(organization_id),

                "asset_count":
                    0,

                "risk_score":
                    0,

                "posture_score":
                    100,

                "risk_level":
                    "minimal",

            }



        asset_scores = []


        critical_assets = 0


        total_findings = 0



        for asset in assets:

            findings = await self.get_asset_findings(
                asset.id,
            )


            total_findings += len(
                findings,
            )


            score = (
                self.calculate_asset_risk(
                    asset,
                    findings,
                )
            )


            asset_scores.append(
                score,
            )


            if asset.criticality == Criticality.CRITICAL:

                critical_assets += 1



        average_risk = (
            sum(asset_scores)
            /
            len(asset_scores)
        )


        organization_risk = (
            self.clamp_score(
                average_risk,
            )
        )


        return {

            "organization_id":
                str(organization_id),

            "asset_count":
                len(assets),

            "critical_assets":
                critical_assets,

            "total_findings":
                total_findings,

            "risk_score":
                organization_risk,

            "posture_score":
                self.calculate_posture_score(
                    organization_risk,
                ),

            "risk_level":
                self.risk_level(
                    organization_risk,
                ),

        }



    async def get_security_posture(
        self,
        organization_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate executive security posture.

        Designed for:

        - Leadership dashboard
        - Reports
        - Compliance reviews
        """

        posture = await self.calculate_organization_risk(
            organization_id,
        )


        recommendations = []


        if posture["risk_score"] >= 70:

            recommendations.append(
                "Immediate remediation required for high risk exposure."
            )


        if posture["critical_assets"] > 0:

            recommendations.append(
                "Review security controls for critical assets."
            )


        if posture["total_findings"] > 100:

            recommendations.append(
                "Prioritize vulnerability reduction program."
            )


        posture["recommendations"] = (
            recommendations
        )


        posture["generated_at"] = (
            datetime.utcnow().isoformat()
        )


        return posture



    async def compare_posture(
        self,
        organization_id: UUID,
        previous_score: float,
    ) -> dict[str, Any]:
        """
        Compare current security posture
        against previous assessment.
        """

        current = (
            await self.calculate_organization_risk(
                organization_id,
            )
        )


        difference = (
            current["risk_score"]
            -
            previous_score
        )


        return {

            "current_risk":
                current["risk_score"],

            "previous_risk":
                previous_score,

            "change":
                round(
                    difference,
                    2,
                ),

            "improved":
                difference < 0,

        }
        # ============================================================
    # Risk Prioritization Engine
    # ============================================================

    async def prioritize_findings(
        self,
        *,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Rank findings by remediation priority.

        Priority considers:

        - Risk score
        - Severity
        - Asset impact
        - Exposure
        """

        stmt = (
            select(Finding)
            .where(

                Finding.deleted_at.is_(None),

                Finding.status
                != FindingStatus.RESOLVED,

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


        prioritized = []


        for index, finding in enumerate(
            findings,
            start=1,
        ):

            priority = "low"


            if finding.risk_score >= 90:

                priority = "immediate"


            elif finding.risk_score >= 70:

                priority = "high"


            elif finding.risk_score >= 40:

                priority = "medium"



            prioritized.append(

                {

                    "rank":
                        index,

                    "finding_id":
                        str(
                            finding.id
                        ),

                    "title":
                        finding.title,

                    "severity":
                        finding.severity.value,

                    "risk_score":
                        finding.risk_score,

                    "priority":
                        priority,

                    "status":
                        finding.status.value,

                }

            )


        return prioritized



    async def calculate_remediation_priority(
        self,
        finding_id: UUID,
    ) -> dict[str, Any]:
        """
        Calculate remediation priority score.

        Factors:

        - Risk
        - Severity
        - Age
        - Exploitability
        """

        finding = await self.get_finding(
            finding_id,
        )


        if finding is None:

            raise ValueError(
                "Finding not found."
            )


        age_days = (
            (
                datetime.utcnow()
                -
                finding.created_at
            )
            .days
        )


        age_factor = min(
            20,
            age_days / 10,
        )


        severity_factor = (
            self.SEVERITY_WEIGHTS.get(
                finding.severity,
                0,
            )
            /
            5
        )


        priority_score = (

            finding.risk_score

            +

            age_factor

            +

            severity_factor

        )


        priority_score = (
            self.clamp_score(
                priority_score,
            )
        )


        return {

            "finding_id":
                str(
                    finding.id
                ),

            "priority_score":
                priority_score,

            "priority_level":
                self.risk_level(
                    priority_score,
                ),

            "age_days":
                age_days,

        }



    async def top_risk_assets(
        self,
        organization_id: UUID,
        *,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Return highest risk assets.
        """

        assets = await self.organization_assets(
            organization_id,
        )


        ranked = []


        for asset in assets:

            findings = await self.get_asset_findings(
                asset.id,
            )


            risk = self.calculate_asset_risk(
                asset,
                findings,
            )


            ranked.append(

                {

                    "asset_id":
                        str(
                            asset.id
                        ),

                    "asset_name":
                        asset.asset_name,

                    "risk_score":
                        risk,

                    "risk_level":
                        self.risk_level(
                            risk,
                        ),

                    "findings":
                        len(
                            findings
                        ),

                }

            )


        ranked.sort(
            key=lambda x:
                x["risk_score"],
            reverse=True,
        )


        return ranked[:limit]
        # ============================================================
    # Risk Trends & Historical Analysis
    # ============================================================

    async def calculate_risk_trend(
        self,
        organization_id: UUID,
    ) -> dict[str, Any]:
        """
        Calculate current risk trend.

        Compares:

        - Active findings
        - Resolved findings
        - Asset exposure
        """

        assets = await self.organization_assets(
            organization_id,
        )


        total_risk = 0.0

        total_assets = len(
            assets,
        )

        total_findings = 0

        resolved_findings = 0

        active_findings = 0



        for asset in assets:

            findings = await self.get_asset_findings(
                asset.id,
            )


            asset_risk = (
                self.calculate_asset_risk(
                    asset,
                    findings,
                )
            )


            total_risk += asset_risk


            for finding in findings:

                total_findings += 1


                if (
                    finding.status
                    ==
                    FindingStatus.RESOLVED
                ):

                    resolved_findings += 1

                else:

                    active_findings += 1



        average_risk = (

            total_risk
            /
            total_assets

            if total_assets

            else 0

        )


        remediation_rate = (

            (
                resolved_findings
                /
                total_findings
            )
            *
            100

            if total_findings

            else 100

        )


        return {

            "organization_id":
                str(
                    organization_id
                ),

            "average_risk":
                self.clamp_score(
                    average_risk,
                ),

            "risk_level":
                self.risk_level(
                    average_risk,
                ),

            "total_findings":
                total_findings,

            "active_findings":
                active_findings,

            "resolved_findings":
                resolved_findings,

            "remediation_rate":
                round(
                    remediation_rate,
                    2,
                ),

            "calculated_at":
                datetime.utcnow().isoformat(),

        }



    async def risk_change_percentage(
        self,
        current_score: float,
        previous_score: float,
    ) -> float:
        """
        Calculate risk percentage change.
        """

        if previous_score == 0:

            return 0.0


        change = (

            (
                current_score
                -
                previous_score
            )

            /

            previous_score

        ) * 100


        return round(
            change,
            2,
        )



    async def improvement_summary(
        self,
        current_score: float,
        previous_score: float,
    ) -> dict[str, Any]:
        """
        Generate risk improvement summary.
        """

        change = await self.risk_change_percentage(
            current_score,
            previous_score,
        )


        return {

            "current_score":
                current_score,

            "previous_score":
                previous_score,

            "change_percentage":
                change,

            "improved":
                current_score
                <
                previous_score,

            "direction":

                (
                    "improving"

                    if current_score
                    <
                    previous_score

                    else

                    "degrading"
                ),

        }



    async def exposure_analysis(
        self,
        organization_id: UUID,
    ) -> dict[str, Any]:
        """
        Analyze external exposure.

        Considers:

        - Internet facing assets
        - Production assets
        - Critical assets
        """

        assets = await self.organization_assets(
            organization_id,
        )


        internet_assets = 0

        production_assets = 0

        critical_assets = 0



        for asset in assets:

            if asset.internet_facing:

                internet_assets += 1


            if asset.production:

                production_assets += 1


            if asset.criticality == Criticality.CRITICAL:

                critical_assets += 1



        return {

            "total_assets":
                len(
                    assets
                ),

            "internet_facing":
                internet_assets,

            "production_assets":
                production_assets,

            "critical_assets":
                critical_assets,

            "exposure_score":
                self.clamp_score(

                    (
                        internet_assets
                        +
                        production_assets
                        +
                        (
                            critical_assets
                            *
                            2
                        )
                    )

                    /
                    max(
                        len(assets),
                        1,
                    )
                    *
                    25

                ),

        }
        # ============================================================
    # Remediation Impact Analysis
    # ============================================================

    async def calculate_remediation_impact(
        self,
        finding_ids: list[UUID],
    ) -> dict[str, Any]:
        """
        Calculate expected risk reduction after remediation.

        Used by:

        - Security teams
        - AI recommendations
        - Remediation planning

        """

        findings = []


        for finding_id in finding_ids:

            finding = await self.get_finding(
                finding_id,
            )


            if finding:

                findings.append(
                    finding,
                )


        if not findings:

            return {

                "findings":
                    0,

                "risk_reduction":
                    0,

                "percentage":
                    0,

            }



        current_risk = sum(

            self.calculate_finding_base_risk(
                finding,
            )

            for finding in findings

        )


        remaining_risk = 0



        risk_reduction = (
            self.clamp_score(
                current_risk
                -
                remaining_risk,
            )
        )


        percentage = (

            (
                risk_reduction
                /
                current_risk
            )
            *
            100

            if current_risk

            else 0

        )


        return {

            "findings":
                len(
                    findings
                ),

            "current_risk":
                round(
                    current_risk,
                    2,
                ),

            "expected_remaining_risk":
                remaining_risk,

            "risk_reduction":
                round(
                    risk_reduction,
                    2,
                ),

            "reduction_percentage":
                round(
                    percentage,
                    2,
                ),

        }



    async def simulate_risk_reduction(
        self,
        asset_id: UUID,
        finding_ids: list[UUID],
    ) -> dict[str, Any]:
        """
        Simulate asset risk after fixing findings.

        Does not modify database.
        """

        asset = await self.get_asset(
            asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        all_findings = await self.get_asset_findings(
            asset_id,
        )


        current_risk = (
            self.calculate_asset_risk(
                asset,
                all_findings,
            )
        )


        remaining_findings = [

            finding

            for finding in all_findings

            if finding.id
            not in finding_ids

        ]


        simulated_risk = (
            self.calculate_asset_risk(
                asset,
                remaining_findings,
            )
        )


        return {

            "asset_id":
                str(
                    asset.id
                ),

            "current_risk":
                current_risk,

            "simulated_risk":
                simulated_risk,

            "risk_reduction":
                round(
                    current_risk
                    -
                    simulated_risk,
                    2,
                ),

            "improvement_percentage":
                (
                    round(
                        (
                            (
                                current_risk
                                -
                                simulated_risk
                            )
                            /
                            current_risk
                        )
                        *
                        100,
                        2,
                    )
                    if current_risk
                    else 0
                ),

        }



    async def remediation_priority_matrix(
        self,
        organization_id: UUID,
    ) -> list[dict[str, Any]]:
        """
        Build remediation priority matrix.

        Helps answer:

        "What should we fix first?"
        """

        assets = await self.organization_assets(
            organization_id,
        )


        matrix = []


        for asset in assets:

            findings = await self.get_asset_findings(
                asset.id,
            )


            for finding in findings:

                if (
                    finding.status
                    ==
                    FindingStatus.RESOLVED
                ):

                    continue


                priority = (
                    self.calculate_finding_base_risk(
                        finding,
                    )
                )


                matrix.append(

                    {

                        "asset_id":
                            str(
                                asset.id
                            ),

                        "asset":
                            asset.asset_name,

                        "finding_id":
                            str(
                                finding.id
                            ),

                        "finding":
                            finding.title,

                        "severity":
                            finding.severity.value,

                        "priority_score":
                            priority,

                    }

                )


        matrix.sort(
            key=lambda item:
                item["priority_score"],
            reverse=True,
        )


        return matrix
        # ============================================================
    # Risk Dashboard Analytics
    # ============================================================

    async def get_dashboard_metrics(
        self,
        organization_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate executive risk dashboard.

        Includes:

        - Overall risk
        - Security posture
        - Asset exposure
        - Finding severity
        - Remediation progress
        """

        posture = await self.calculate_organization_risk(
            organization_id,
        )


        trend = await self.calculate_risk_trend(
            organization_id,
        )


        exposure = await self.exposure_analysis(
            organization_id,
        )


        priority_items = (
            await self.remediation_priority_matrix(
                organization_id,
            )
        )


        critical_count = sum(

            1

            for item in priority_items

            if item["severity"]
            ==
            FindingSeverity.CRITICAL.value

        )


        high_count = sum(

            1

            for item in priority_items

            if item["severity"]
            ==
            FindingSeverity.HIGH.value

        )



        return {

            "organization_id":
                str(
                    organization_id
                ),

            "security_posture":

                {

                    "risk_score":
                        posture["risk_score"],

                    "posture_score":
                        posture["posture_score"],

                    "risk_level":
                        posture["risk_level"],

                },


            "exposure":

                exposure,


            "findings":

                {

                    "total":
                        trend["total_findings"],

                    "active":
                        trend["active_findings"],

                    "resolved":
                        trend["resolved_findings"],

                    "remediation_rate":
                        trend["remediation_rate"],

                },


            "priority":

                {

                    "critical":
                        critical_count,

                    "high":
                        high_count,

                    "total_items":
                        len(
                            priority_items
                        ),

                },


            "generated_at":
                datetime.utcnow().isoformat(),

        }



    async def get_risk_distribution(
        self,
        organization_id: UUID,
    ) -> dict[str, int]:
        """
        Return assets grouped by risk level.
        """

        assets = await self.organization_assets(
            organization_id,
        )


        distribution = {

            "critical": 0,

            "high": 0,

            "medium": 0,

            "low": 0,

            "minimal": 0,

        }


        for asset in assets:

            findings = await self.get_asset_findings(
                asset.id,
            )


            score = (
                self.calculate_asset_risk(
                    asset,
                    findings,
                )
            )


            level = self.risk_level(
                score,
            )


            distribution[level] += 1



        return distribution



    async def get_top_vulnerable_assets(
        self,
        organization_id: UUID,
        *,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Return assets requiring immediate attention.
        """

        ranked = await self.top_risk_assets(
            organization_id,
            limit=limit,
        )


        return [

            {

                "asset":
                    item["asset_name"],

                "risk_score":
                    item["risk_score"],

                "risk_level":
                    item["risk_level"],

                "findings":
                    item["findings"],

            }

            for item in ranked

        ]



    async def calculate_business_risk(
        self,
        organization_id: UUID,
    ) -> dict[str, Any]:
        """
        Translate technical risk into
        business security impact.
        """

        posture = await self.calculate_organization_risk(
            organization_id,
        )


        impact = "low"


        if posture["risk_score"] >= 80:

            impact = "critical"


        elif posture["risk_score"] >= 60:

            impact = "high"


        elif posture["risk_score"] >= 30:

            impact = "medium"



        return {

            "business_impact":
                impact,

            "security_risk":
                posture["risk_score"],

            "recommended_action":

                (

                    "Immediate executive review"

                    if impact
                    ==
                    "critical"

                    else

                    "Continue monitoring"

                ),

        }
        # ============================================================
    # Risk Reporting & Export
    # ============================================================

    async def generate_risk_report(
        self,
        organization_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate complete risk assessment report.

        Used by:

        - Report Service
        - Executive dashboards
        - Compliance exports
        """

        posture = await self.calculate_organization_risk(
            organization_id,
        )


        dashboard = await self.get_dashboard_metrics(
            organization_id,
        )


        vulnerable_assets = (
            await self.get_top_vulnerable_assets(
                organization_id,
                limit=10,
            )
        )


        distribution = (
            await self.get_risk_distribution(
                organization_id,
            )
        )


        return {

            "organization_id":
                str(
                    organization_id
                ),

            "summary":

                {

                    "risk_score":
                        posture["risk_score"],

                    "posture_score":
                        posture["posture_score"],

                    "risk_level":
                        posture["risk_level"],

                },


            "dashboard":
                dashboard,


            "risk_distribution":
                distribution,


            "top_risk_assets":
                vulnerable_assets,


            "generated_at":
                datetime.utcnow().isoformat(),

        }



    async def export_asset_risk(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Export detailed asset risk profile.
        """

        asset = await self.get_asset(
            asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        findings = await self.get_asset_findings(
            asset_id,
        )


        risk_score = (
            self.calculate_asset_risk(
                asset,
                findings,
            )
        )


        return {

            "asset":

                {

                    "id":
                        str(
                            asset.id
                        ),

                    "name":
                        asset.asset_name,

                    "type":
                        asset.asset_type.value,

                    "criticality":
                        asset.criticality.value,

                },


            "risk":

                {

                    "score":
                        risk_score,

                    "level":
                        self.risk_level(
                            risk_score,
                        ),

                    "posture":
                        self.calculate_posture_score(
                            risk_score,
                        ),

                },


            "findings":

                [

                    {

                        "id":
                            str(
                                finding.id
                            ),

                        "title":
                            finding.title,

                        "severity":
                            finding.severity.value,

                        "risk_score":
                            self.calculate_finding_base_risk(
                                finding,
                            ),

                        "status":
                            finding.status.value,

                    }

                    for finding in findings

                ],


            "generated_at":
                datetime.utcnow().isoformat(),

        }



    async def compliance_summary(
        self,
        organization_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate compliance-oriented summary.

        Focuses on:

        - Open risks
        - Critical exposure
        - Remediation status
        """

        trend = await self.calculate_risk_trend(
            organization_id,
        )


        posture = await self.calculate_organization_risk(
            organization_id,
        )


        return {

            "overall_status":

                (

                    "non_compliant"

                    if posture["risk_score"]
                    >=
                    70

                    else

                    "acceptable"

                ),


            "risk_score":
                posture["risk_score"],


            "open_findings":
                trend["active_findings"],


            "resolved_findings":
                trend["resolved_findings"],


            "remediation_rate":
                trend["remediation_rate"],


            "generated_at":
                datetime.utcnow().isoformat(),

        }
        # ============================================================
    # Maintenance & Cleanup Utilities
    # ============================================================

    async def refresh_all_risk_scores(
        self,
        organization_id: UUID,
    ) -> dict[str, int]:
        """
        Recalculate all risk scores.

        Updates:

        - Findings
        - Assets

        Used by:

        - Scheduled jobs
        - Risk engine workers
        """

        assets = await self.organization_assets(
            organization_id,
        )


        findings_updated = 0

        assets_updated = 0



        for asset in assets:

            findings = await self.get_asset_findings(
                asset.id,
            )


            for finding in findings:

                finding.risk_score = (
                    self.calculate_finding_base_risk(
                        finding,
                    )
                )

                findings_updated += 1



            asset_risk = (
                self.calculate_asset_risk(
                    asset,
                    findings,
                )
            )


            asset.update_risk_score(
                asset_risk,
            )


            assets_updated += 1



        await self.commit()


        logger.info(
            "Risk refresh completed. assets=%s findings=%s",
            assets_updated,
            findings_updated,
        )


        return {

            "assets_updated":
                assets_updated,

            "findings_updated":
                findings_updated,

        }



    async def health_check(
        self,
    ) -> dict[str, Any]:
        """
        Risk engine health status.
        """

        try:

            result = await self.db.execute(
                select(
                    func.count(
                        Asset.id,
                    )
                )
            )


            asset_count = result.scalar() or 0


            return {

                "service":
                    "risk_engine",

                "status":
                    "healthy",

                "tracked_assets":
                    asset_count,

                "timestamp":
                    datetime.utcnow().isoformat(),

            }


        except Exception as exc:

            logger.exception(
                "Risk engine health check failed."
            )


            return {

                "service":
                    "risk_engine",

                "status":
                    "unhealthy",

                "error":
                    str(exc),

            }



    async def cleanup_orphan_data(
        self,
    ) -> int:
        """
        Placeholder maintenance hook.

        Reserved for:

        - Removing orphaned risk snapshots
        - Cleaning historical records
        - Database optimization
        """

        return 0



# ============================================================
# End of File
# ============================================================
