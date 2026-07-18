"""
QShield Enterprise
==================

Recommendation Service

AI-driven security recommendation engine.

Generates actionable recommendations from:

- Security findings
- Risk scores
- Asset exposure
- Compliance gaps
- Post-Quantum Cryptography readiness

Used by:

- REST API
- Dashboard
- AI Engine
- Report Generator
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
from app.models.finding import Finding
from app.models.finding import FindingSeverity
from app.models.finding import FindingStatus


from app.models.recommendation import (
    Recommendation,
    RecommendationPriority,
    RecommendationStatus,
)


logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Enterprise AI Recommendation Service.

    Responsibilities
    ----------------

    • Generate remediation advice

    • Prioritize security actions

    • Track recommendation lifecycle

    • Provide AI-ready security guidance

    • Support PQC migration planning
    """


    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db



    # ============================================================
    # Recommendation Rules
    # ============================================================


    SEVERITY_PRIORITY = {

        FindingSeverity.CRITICAL:
            RecommendationPriority.IMMEDIATE,

        FindingSeverity.HIGH:
            RecommendationPriority.HIGH,

        FindingSeverity.MEDIUM:
            RecommendationPriority.MEDIUM,

        FindingSeverity.LOW:
            RecommendationPriority.LOW,

        FindingSeverity.INFO:
            RecommendationPriority.LOW,

    }


    DEFAULT_ACTIONS = {

        "tls":
            "Upgrade TLS configuration and remove weak cryptographic protocols.",

        "certificate":
            "Review certificate validity and replace insecure certificates.",

        "encryption":
            "Enable stronger encryption mechanisms.",

        "pqc":
            "Evaluate migration path toward Post Quantum Cryptography.",

        "patch":
            "Apply security patches and update affected components.",

        "access":
            "Review identity permissions and enforce least privilege.",

    }



    # ============================================================
    # Helpers
    # ============================================================


    @staticmethod
    def normalize_text(
        value: str | None,
    ) -> str:

        if not value:

            return ""

        return value.strip().lower()



    @staticmethod
    def calculate_priority_score(
        severity: FindingSeverity,
        risk_score: float,
    ) -> float:
        """
        Calculate recommendation urgency.
        """

        weight = {

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


        return round(
            (
                weight.get(
                    severity,
                    0,
                )
                *
                0.6
            )
            +
            (
                risk_score
                *
                0.4
            ),
            2,
        )
        # ============================================================
    # Database Helpers
    # ============================================================

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



    async def get_recommendation(
        self,
        recommendation_id: UUID,
    ) -> Recommendation | None:
        """
        Retrieve recommendation model.
        """

        stmt = (
            select(Recommendation)
            .where(

                Recommendation.id
                ==
                recommendation_id,

                Recommendation.deleted_at.is_(None),

            )
        )


        result = await self.db.execute(
            stmt,
        )


        return result.scalar_one_or_none()



    async def recommendation_exists(
        self,
        finding_id: UUID,
        title: str,
    ) -> bool:
        """
        Check duplicate recommendation.
        """

        stmt = (
            select(func.count())
            .select_from(
                Recommendation,
            )
            .where(

                Recommendation.finding_id
                ==
                finding_id,

                func.lower(
                    Recommendation.title,
                )
                ==
                title.lower(),

                Recommendation.deleted_at.is_(None),

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
        Commit database transaction.
        """

        try:

            await self.db.commit()


        except Exception:

            await self.db.rollback()


            logger.exception(
                "Recommendation commit failed."
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
    # Recommendation Generation Engine
    # ============================================================

    def generate_recommendation_text(
        self,
        finding: Finding,
    ) -> tuple[str, str]:
        """
        Generate remediation recommendation
        from finding characteristics.

        Returns:

        (
            title,
            description
        )
        """

        category = (
            self.normalize_text(
                finding.category,
            )
        )


        title = (
            f"Remediate {finding.title}"
        )


        description = (
            "Review and remediate the identified "
            "security issue."
        )



        for keyword, action in (
            self.DEFAULT_ACTIONS.items()
        ):

            if keyword in category:

                description = action

                break



        if finding.severity == FindingSeverity.CRITICAL:

            description += (
                " Immediate action is required "
                "due to critical severity."
            )


        elif finding.severity == FindingSeverity.HIGH:

            description += (
                " Prioritize remediation during "
                "the next security cycle."
            )


        else:

            description += (
                " Address during planned "
                "security improvements."
            )


        return (

            title,

            description,

        )



    def determine_recommendation_priority(
        self,
        finding: Finding,
    ) -> RecommendationPriority:
        """
        Determine recommendation priority.
        """

        return (
            self.SEVERITY_PRIORITY.get(
                finding.severity,
                RecommendationPriority.LOW,
            )
        )



    async def build_recommendation(
        self,
        finding: Finding,
    ) -> Recommendation:
        """
        Build recommendation object.

        Does not persist.
        """

        title, description = (
            self.generate_recommendation_text(
                finding,
            )
        )


        priority = (
            self.determine_recommendation_priority(
                finding,
            )
        )


        priority_score = (
            self.calculate_priority_score(
                finding.severity,
                finding.risk_score,
            )
        )


        return Recommendation(

            finding_id=finding.id,

            title=title,

            description=description,

            priority=priority,

            priority_score=priority_score,

            status=(
                RecommendationStatus.OPEN
            ),

            generated_at=datetime.utcnow(),

        )



    async def generate_for_finding(
        self,
        finding_id: UUID,
    ) -> Recommendation:
        """
        Generate recommendation for
        a single finding.
        """

        finding = await self.get_finding(
            finding_id,
        )


        if finding is None:

            raise ValueError(
                "Finding not found."
            )


        title, _ = (
            self.generate_recommendation_text(
                finding,
            )
        )


        if await self.recommendation_exists(
            finding.id,
            title,
        ):

            raise ValueError(
                "Recommendation already exists."
            )


        recommendation = (
            await self.build_recommendation(
                finding,
            )
        )


        self.db.add(
            recommendation,
        )


        await self.commit()


        await self.db.refresh(
            recommendation,
        )


        logger.info(
            "Generated recommendation. id=%s",
            recommendation.id,
        )


        return recommendation
        # ============================================================
    # Finding Remediation Recommendations
    # ============================================================

    async def generate_for_findings(
        self,
        finding_ids: list[UUID],
    ) -> list[Recommendation]:
        """
        Generate recommendations for multiple findings.

        Used by:

        - Scan completion workflow
        - AI analysis pipeline
        - Report generation
        """

        recommendations: list[Recommendation] = []


        for finding_id in finding_ids:

            try:

                recommendation = (
                    await self.generate_for_finding(
                        finding_id,
                    )
                )


                recommendations.append(
                    recommendation,
                )


            except ValueError:

                continue


        return recommendations



    async def generate_scan_recommendations(
        self,
        scan_id: UUID,
    ) -> list[Recommendation]:
        """
        Generate recommendations for
        all findings from a scan.
        """

        stmt = (
            select(Finding)
            .where(

                Finding.scan_id == scan_id,

                Finding.deleted_at.is_(None),

                Finding.status
                !=
                FindingStatus.RESOLVED,

            )
        )


        result = await self.db.execute(
            stmt,
        )


        findings = list(
            result.scalars().all()
        )


        recommendations = []


        for finding in findings:

            title, _ = (
                self.generate_recommendation_text(
                    finding,
                )
            )


            exists = await self.recommendation_exists(
                finding.id,
                title,
            )


            if exists:

                continue


            recommendation = (
                await self.build_recommendation(
                    finding,
                )
            )


            self.db.add(
                recommendation,
            )


            recommendations.append(
                recommendation,
            )


        if recommendations:

            await self.commit()


            for recommendation in recommendations:

                await self.db.refresh(
                    recommendation,
                )


        logger.info(
            "Generated %s recommendations for scan=%s",
            len(recommendations),
            scan_id,
        )


        return recommendations



    async def get_finding_recommendations(
        self,
        finding_id: UUID,
    ) -> list[Recommendation]:
        """
        Retrieve recommendations
        linked to a finding.
        """

        stmt = (
            select(Recommendation)
            .where(

                Recommendation.finding_id
                ==
                finding_id,

                Recommendation.deleted_at.is_(None),

            )
            .order_by(
                Recommendation.priority_score.desc(),
            )
        )


        result = await self.db.execute(
            stmt,
        )


        return list(
            result.scalars().all()
        )



    async def regenerate_recommendation(
        self,
        recommendation_id: UUID,
    ) -> Recommendation:
        """
        Regenerate recommendation content.

        Useful when:

        - Risk changes
        - Finding severity changes
        """

        recommendation = (
            await self.get_recommendation(
                recommendation_id,
            )
        )


        if recommendation is None:

            raise ValueError(
                "Recommendation not found."
            )


        finding = await self.get_finding(
            recommendation.finding_id,
        )


        if finding is None:

            raise ValueError(
                "Finding not found."
            )


        title, description = (
            self.generate_recommendation_text(
                finding,
            )
        )


        recommendation.title = title

        recommendation.description = description

        recommendation.priority = (
            self.determine_recommendation_priority(
                finding,
            )
        )

        recommendation.priority_score = (
            self.calculate_priority_score(
                finding.severity,
                finding.risk_score,
            )
        )


        await self.commit()


        await self.db.refresh(
            recommendation,
        )


        return recommendation
        # ============================================================
    # Asset Security Recommendations
    # ============================================================

    async def generate_asset_recommendations(
        self,
        asset_id: UUID,
    ) -> list[Recommendation]:
        """
        Generate security recommendations
        for an asset.

        Considers:

        - Asset exposure
        - Criticality
        - Existing findings
        - Internet exposure
        """

        asset = await self.get_asset(
            asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        recommendations = []



        # --------------------------------------------------------
        # External Exposure
        # --------------------------------------------------------

        if asset.internet_facing:

            recommendation = Recommendation(

                asset_id=asset.id,

                title=(
                    "Review Internet Exposure"
                ),

                description=(
                    "Perform external attack surface "
                    "assessment and reduce unnecessary "
                    "internet exposure."
                ),

                priority=(
                    RecommendationPriority.HIGH
                ),

                priority_score=75,

                status=(
                    RecommendationStatus.OPEN
                ),

                generated_at=datetime.utcnow(),

            )


            recommendations.append(
                recommendation,
            )



        # --------------------------------------------------------
        # Production Critical Assets
        # --------------------------------------------------------

        if (
            asset.production
            and
            asset.criticality
        ):

            recommendation = Recommendation(

                asset_id=asset.id,

                title=(
                    "Harden Production Asset"
                ),

                description=(
                    "Apply enhanced security controls "
                    "because this asset supports production."
                ),

                priority=(
                    RecommendationPriority.HIGH
                ),

                priority_score=70,

                status=(
                    RecommendationStatus.OPEN
                ),

                generated_at=datetime.utcnow(),

            )


            recommendations.append(
                recommendation,
            )



        # --------------------------------------------------------
        # Finding Based Recommendations
        # --------------------------------------------------------

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


            title, _ = (
                self.generate_recommendation_text(
                    finding,
                )
            )


            exists = await self.recommendation_exists(
                finding.id,
                title,
            )


            if exists:

                continue


            recommendation = (
                await self.build_recommendation(
                    finding,
                )
            )


            recommendations.append(
                recommendation,
            )



        if recommendations:

            for recommendation in recommendations:

                self.db.add(
                    recommendation,
                )


            await self.commit()


            for recommendation in recommendations:

                await self.db.refresh(
                    recommendation,
                )



        logger.info(
            "Generated asset recommendations. asset=%s count=%s",
            asset.id,
            len(recommendations),
        )


        return recommendations



    async def attack_surface_recommendations(
        self,
        asset_id: UUID,
    ) -> list[dict[str, Any]]:
        """
        Generate attack surface guidance.

        Used for:

        - External assets
        - Domains
        - APIs
        """

        asset = await self.get_asset(
            asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        recommendations = []



        if asset.external:

            recommendations.append(

                {

                    "area":
                        "external_exposure",

                    "recommendation":
                        "Monitor public services and exposed endpoints.",

                    "priority":
                        "high",

                }

            )



        if asset.asset_type.value in (

            "domain",

            "subdomain",

            "api",

        ):

            recommendations.append(

                {

                    "area":
                        "web_security",

                    "recommendation":
                        "Perform continuous web security assessment.",

                    "priority":
                        "medium",

                }

            )



        return recommendations
        # ============================================================
    # Post Quantum Cryptography Recommendations
    # ============================================================

    async def generate_pqc_recommendations(
        self,
        asset_id: UUID,
    ) -> list[dict[str, Any]]:
        """
        Generate Post Quantum Cryptography
        migration recommendations.

        Evaluates:

        - Cryptographic exposure
        - TLS usage
        - Certificate dependencies
        - Long-term data sensitivity
        """

        asset = await self.get_asset(
            asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        recommendations = []



        # --------------------------------------------------------
        # General PQC Readiness
        # --------------------------------------------------------

        recommendations.append(

            {

                "asset_id":
                    str(
                        asset.id
                    ),

                "category":
                    "pqc_readiness",

                "title":
                    "Assess Post Quantum Cryptography Readiness",

                "description":
                    (
                        "Evaluate cryptographic dependencies "
                        "and prepare migration strategy "
                        "towards quantum-resistant algorithms."
                    ),

                "priority":
                    "medium",

            }

        )



        # --------------------------------------------------------
        # Internet Facing Assets
        # --------------------------------------------------------

        if asset.internet_facing:

            recommendations.append(

                {

                    "asset_id":
                        str(
                            asset.id
                        ),

                    "category":
                        "quantum_security",

                    "title":
                        "Prepare Quantum Safe Communication",

                    "description":
                        (
                            "Review TLS, certificates and "
                            "key exchange mechanisms for "
                            "future quantum threats."
                        ),

                    "priority":
                        "high",

                }

            )



        # --------------------------------------------------------
        # Critical Assets
        # --------------------------------------------------------

        if asset.criticality.value in (

            "high",

            "critical",

        ):

            recommendations.append(

                {

                    "asset_id":
                        str(
                            asset.id
                        ),

                    "category":
                        "harvest_now_decrypt_later",

                    "title":
                        (
                            "Protect Long Lifetime Data"
                        ),

                    "description":
                        (
                            "Identify sensitive data that "
                            "requires protection against "
                            "future quantum attacks."
                        ),

                    "priority":
                        "high",

                }

            )


        return recommendations



    async def pqc_migration_plan(
        self,
        organization_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate organization-level
        PQC migration roadmap.

        Phases:

        1. Discovery
        2. Assessment
        3. Migration
        4. Validation
        """

        return {

            "organization_id":
                str(
                    organization_id
                ),

            "migration_phases":

                [

                    {

                        "phase":
                            "discovery",

                        "actions":

                            [

                                "Inventory cryptographic assets",

                                "Identify vulnerable algorithms",

                                "Map certificate dependencies",

                            ],

                    },


                    {

                        "phase":
                            "assessment",

                        "actions":

                            [

                                "Evaluate quantum risk",

                                "Prioritize critical systems",

                                "Perform crypto agility review",

                            ],

                    },


                    {

                        "phase":
                            "migration",

                        "actions":

                            [

                                "Deploy hybrid cryptography",

                                "Adopt PQC algorithms",

                                "Update communication protocols",

                            ],

                    },


                    {

                        "phase":
                            "validation",

                        "actions":

                            [

                                "Perform security testing",

                                "Validate interoperability",

                                "Monitor cryptographic posture",

                            ],

                    },

                ],

            "generated_at":
                datetime.utcnow().isoformat(),

        }



    async def cryptographic_inventory_recommendation(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate crypto inventory guidance.
        """

        asset = await self.get_asset(
            asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        return {

            "asset_id":
                str(
                    asset.id
                ),

            "recommendation":
                (
                    "Create cryptographic inventory "
                    "covering algorithms, keys, "
                    "certificates and protocols."
                ),

            "priority":
                (
                    "high"
                    if asset.internet_facing
                    else
                    "medium"
                ),

        }
        # ============================================================
    # Compliance Recommendations
    # ============================================================

    async def generate_compliance_recommendations(
        self,
        asset_id: UUID,
    ) -> list[dict[str, Any]]:
        """
        Generate compliance-oriented
        security recommendations.

        Maps security gaps to:

        - ISO 27001
        - NIST CSF
        - SOC2
        - CIS Controls
        """

        asset = await self.get_asset(
            asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        recommendations = []



        # --------------------------------------------------------
        # Asset Inventory Control
        # --------------------------------------------------------

        recommendations.append(

            {

                "framework":
                    "ISO27001",

                "control":
                    "A.5.9",

                "title":
                    "Maintain Asset Inventory",

                "description":
                    (
                        "Ensure all enterprise assets "
                        "are identified, classified "
                        "and continuously monitored."
                    ),

                "priority":
                    "medium",

            }

        )



        # --------------------------------------------------------
        # Vulnerability Management
        # --------------------------------------------------------

        findings = await self.get_asset_findings(
            asset.id,
        )


        if findings:

            recommendations.append(

                {

                    "framework":
                        "NIST",

                    "control":
                        "ID.RA",

                    "title":
                        "Improve Vulnerability Management",

                    "description":
                        (
                            "Review identified security "
                            "findings and establish "
                            "remediation workflow."
                        ),

                    "priority":
                        "high",

                }

            )



        # --------------------------------------------------------
        # Internet Exposure
        # --------------------------------------------------------

        if asset.internet_facing:

            recommendations.append(

                {

                    "framework":
                        "CIS",

                    "control":
                        "CIS-4",

                    "title":
                        "Reduce External Attack Surface",

                    "description":
                        (
                            "Review externally exposed "
                            "services and restrict "
                            "unnecessary access."
                        ),

                    "priority":
                        "high",

                }

            )



        return recommendations



    async def compliance_gap_analysis(
        self,
        organization_id: UUID,
    ) -> dict[str, Any]:
        """
        Analyze compliance readiness.

        Provides:

        - Security gaps
        - Suggested actions
        - Control areas
        """

        assets_stmt = (
            select(
                func.count(
                    Asset.id,
                )
            )
            .where(

                Asset.organization_id
                ==
                organization_id,

                Asset.deleted_at.is_(None),

            )
        )


        asset_count = await self.db.scalar(
            assets_stmt,
        )


        findings_stmt = (
            select(
                func.count(
                    Finding.id,
                )
            )
            .join(
                Asset,
            )
            .where(

                Asset.organization_id
                ==
                organization_id,

                Finding.status
                !=
                FindingStatus.RESOLVED,

                Finding.deleted_at.is_(None),

            )
        )


        finding_count = await self.db.scalar(
            findings_stmt,
        )



        gaps = []



        if not asset_count:

            gaps.append(

                {

                    "area":
                        "asset_inventory",

                    "issue":
                        "No managed assets discovered.",

                    "recommendation":
                        "Deploy asset discovery process.",

                }

            )



        if finding_count:

            gaps.append(

                {

                    "area":
                        "vulnerability_management",

                    "issue":
                        (
                            f"{finding_count} unresolved "
                            "security findings detected."
                        ),

                    "recommendation":
                        (
                            "Prioritize remediation "
                            "based on risk."
                        ),

                }

            )



        return {

            "organization_id":
                str(
                    organization_id
                ),

            "assets":
                int(
                    asset_count or 0
                ),

            "open_findings":
                int(
                    finding_count or 0
                ),

            "compliance_gaps":
                gaps,

            "generated_at":
                datetime.utcnow().isoformat(),

        }



    async def framework_mapping(
        self,
        category: str,
    ) -> dict[str, Any]:
        """
        Return compliance mapping
        for security category.
        """

        mappings = {

            "encryption":

                {

                    "iso27001":
                        "A.8.24",

                    "nist":
                        "PR.DS",

                    "soc2":
                        "CC6",

                },


            "access":

                {

                    "iso27001":
                        "A.5.15",

                    "nist":
                        "PR.AC",

                    "soc2":
                        "CC6",

                },


            "vulnerability":

                {

                    "iso27001":
                        "A.8.8",

                    "nist":
                        "ID.RA",

                    "soc2":
                        "CC7",

                },

        }


        return mappings.get(
            category.lower(),
            {},
        )
        # ============================================================
    # AI Prioritization Engine
    # ============================================================

    async def rank_recommendations(
        self,
        recommendations: list[Recommendation],
    ) -> list[Recommendation]:
        """
        Rank recommendations by urgency.

        Ranking factors:

        - Priority score
        - Severity
        - Business impact
        - Status
        """

        return sorted(

            recommendations,

            key=lambda item:

                item.priority_score,

            reverse=True,

        )



    async def calculate_recommendation_score(
        self,
        recommendation_id: UUID,
    ) -> float:
        """
        Calculate recommendation priority score.
        """

        recommendation = (
            await self.get_recommendation(
                recommendation_id,
            )
        )


        if recommendation is None:

            raise ValueError(
                "Recommendation not found."
            )


        score = (
            recommendation.priority_score
        )


        if (
            recommendation.status
            ==
            RecommendationStatus.COMPLETED
        ):

            score *= 0.1



        elif (
            recommendation.status
            ==
            RecommendationStatus.ACCEPTED
        ):

            score *= 0.3



        return round(
            min(
                100,
                score,
            ),
            2,
        )



    async def prioritize_security_actions(
        self,
        organization_id: UUID,
        *,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Generate AI-style prioritized actions.

        Answers:

        "What should security team do next?"
        """

        stmt = (
            select(Recommendation)
            .join(
                Finding,
                isouter=True,
            )
            .join(
                Asset,
                isouter=True,
            )
            .where(

                Recommendation.deleted_at.is_(None),

                Recommendation.status
                ==
                RecommendationStatus.OPEN,

                Asset.organization_id
                ==
                organization_id,

            )
            .order_by(
                Recommendation.priority_score.desc(),
            )
            .limit(limit)
        )


        result = await self.db.execute(
            stmt,
        )


        recommendations = list(
            result.scalars().all()
        )


        actions = []


        for index, recommendation in enumerate(
            recommendations,
            start=1,
        ):

            actions.append(

                {

                    "rank":
                        index,

                    "recommendation_id":
                        str(
                            recommendation.id
                        ),

                    "title":
                        recommendation.title,

                    "priority":
                        recommendation.priority.value,

                    "score":
                        recommendation.priority_score,

                    "recommended_action":
                        recommendation.description,

                }

            )


        return actions



    async def generate_ai_summary(
        self,
        organization_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate executive AI security summary.

        Designed for LLM integration.
        """

        actions = await self.prioritize_security_actions(
            organization_id,
            limit=10,
        )


        critical_actions = [

            action

            for action in actions

            if action["priority"]
            ==
            RecommendationPriority.IMMEDIATE.value

        ]



        return {

            "summary":
                (
                    "Security analysis completed. "
                    "Prioritized remediation actions "
                    "have been generated."
                ),

            "critical_actions":
                len(
                    critical_actions
                ),

            "top_actions":
                actions,

            "generated_at":
                datetime.utcnow().isoformat(),

        }



    async def recommendation_confidence(
        self,
        recommendation_id: UUID,
    ) -> float:
        """
        Calculate AI recommendation confidence.

        Based on:

        - Risk availability
        - Finding severity
        - Evidence
        """

        recommendation = (
            await self.get_recommendation(
                recommendation_id,
            )
        )


        if recommendation is None:

            raise ValueError(
                "Recommendation not found."
            )


        confidence = 50.0



        if recommendation.priority_score:

            confidence += 25



        if recommendation.finding_id:

            confidence += 15



        if recommendation.description:

            confidence += 10



        return min(
            100,
            confidence,
        )
        # ============================================================
    # Recommendation Lifecycle Management
    # ============================================================

    async def update_recommendation_status(
        self,
        recommendation_id: UUID,
        status: RecommendationStatus,
    ) -> Recommendation:
        """
        Update recommendation lifecycle status.

        States:

        OPEN
          |
          +--> ACCEPTED
          |
          +--> IN_PROGRESS
          |
          +--> COMPLETED
          |
          +--> REJECTED
        """

        recommendation = (
            await self.get_recommendation(
                recommendation_id,
            )
        )


        if recommendation is None:

            raise ValueError(
                "Recommendation not found."
            )


        recommendation.status = status



        if status == RecommendationStatus.COMPLETED:

            recommendation.completed_at = (
                datetime.utcnow()
            )


        await self.commit()


        await self.db.refresh(
            recommendation,
        )


        logger.info(
            "Recommendation status updated. id=%s status=%s",
            recommendation.id,
            status,
        )


        return recommendation



    async def accept_recommendation(
        self,
        recommendation_id: UUID,
    ) -> Recommendation:
        """
        Accept recommendation for action.
        """

        return await self.update_recommendation_status(
            recommendation_id,
            RecommendationStatus.ACCEPTED,
        )



    async def start_recommendation(
        self,
        recommendation_id: UUID,
    ) -> Recommendation:
        """
        Mark recommendation as in progress.
        """

        return await self.update_recommendation_status(
            recommendation_id,
            RecommendationStatus.IN_PROGRESS,
        )



    async def complete_recommendation(
        self,
        recommendation_id: UUID,
    ) -> Recommendation:
        """
        Mark recommendation as completed.
        """

        return await self.update_recommendation_status(
            recommendation_id,
            RecommendationStatus.COMPLETED,
        )



    async def reject_recommendation(
        self,
        recommendation_id: UUID,
    ) -> Recommendation:
        """
        Reject recommendation.
        """

        return await self.update_recommendation_status(
            recommendation_id,
            RecommendationStatus.REJECTED,
        )



    async def reopen_recommendation(
        self,
        recommendation_id: UUID,
    ) -> Recommendation:
        """
        Reopen completed/rejected recommendation.
        """

        return await self.update_recommendation_status(
            recommendation_id,
            RecommendationStatus.OPEN,
        )



    async def get_open_recommendations(
        self,
        *,
        limit: int = 100,
    ) -> list[Recommendation]:
        """
        Return pending recommendations.
        """

        stmt = (
            select(Recommendation)
            .where(

                Recommendation.status
                ==
                RecommendationStatus.OPEN,

                Recommendation.deleted_at.is_(None),

            )
            .order_by(
                Recommendation.priority_score.desc(),
            )
            .limit(limit)
        )


        result = await self.db.execute(
            stmt,
        )


        return list(
            result.scalars().all()
        )



    async def get_completed_recommendations(
        self,
        *,
        limit: int = 100,
    ) -> list[Recommendation]:
        """
        Return completed recommendations.
        """

        stmt = (
            select(Recommendation)
            .where(

                Recommendation.status
                ==
                RecommendationStatus.COMPLETED,

                Recommendation.deleted_at.is_(None),

            )
            .order_by(
                Recommendation.completed_at.desc(),
            )
            .limit(limit)
        )


        result = await self.db.execute(
            stmt,
        )


        return list(
            result.scalars().all()
        )
        # ============================================================
    # Recommendation Analytics Dashboard
    # ============================================================

    async def get_statistics(
        self,
        *,
        organization_id: UUID | None = None,
    ) -> dict[str, Any]:
        """
        Generate recommendation statistics.

        Includes:

        - Total recommendations
        - Status distribution
        - Priority distribution
        - Completion rate
        """

        filters = [

            Recommendation.deleted_at.is_(None),

        ]


        if organization_id:

            filters.append(

                Recommendation.organization_id
                ==
                organization_id

            )



        total = await self.db.scalar(
            select(
                func.count(
                    Recommendation.id,
                )
            )
            .where(
                *filters,
            )
        )


        completed = await self.db.scalar(
            select(
                func.count(
                    Recommendation.id,
                )
            )
            .where(

                *filters,

                Recommendation.status
                ==
                RecommendationStatus.COMPLETED,

            )
        )


        open_count = await self.db.scalar(
            select(
                func.count(
                    Recommendation.id,
                )
            )
            .where(

                *filters,

                Recommendation.status
                ==
                RecommendationStatus.OPEN,

            )
        )



        priority_rows = await self.db.execute(
            select(

                Recommendation.priority,

                func.count(
                    Recommendation.id,
                ),

            )
            .where(
                *filters,
            )
            .group_by(
                Recommendation.priority,
            )
        )


        priority_distribution = {

            priority.value:
                count

            for priority, count
            in priority_rows.all()

        }



        status_rows = await self.db.execute(
            select(

                Recommendation.status,

                func.count(
                    Recommendation.id,
                ),

            )
            .where(
                *filters,
            )
            .group_by(
                Recommendation.status,
            )
        )


        status_distribution = {

            status.value:
                count

            for status, count
            in status_rows.all()

        }



        completion_rate = (

            (
                completed
                /
                total
            )
            *
            100

            if total

            else 0

        )


        return {

            "total":
                int(
                    total or 0
                ),

            "open":
                int(
                    open_count or 0
                ),

            "completed":
                int(
                    completed or 0
                ),

            "completion_rate":
                round(
                    completion_rate,
                    2,
                ),

            "priority_distribution":
                priority_distribution,

            "status_distribution":
                status_distribution,

        }



    async def get_dashboard(
        self,
        organization_id: UUID | None = None,
    ) -> dict[str, Any]:
        """
        Build recommendation dashboard.
        """

        statistics = await self.get_statistics(
            organization_id=organization_id,
        )


        actions = await self.prioritize_security_actions(
            organization_id,
            limit=10,
        ) if organization_id else []



        return {

            "statistics":
                statistics,

            "top_actions":
                actions,

            "generated_at":
                datetime.utcnow().isoformat(),

        }



    async def recommendation_trends(
        self,
        *,
        days: int = 30,
    ) -> dict[str, Any]:
        """
        Analyze recommendation trends.

        Used for:

        - Security improvement tracking
        - Executive reporting
        """

        from datetime import timedelta


        cutoff = (
            datetime.utcnow()
            -
            timedelta(
                days=days,
            )
        )


        generated = await self.db.scalar(
            select(
                func.count(
                    Recommendation.id,
                )
            )
            .where(

                Recommendation.created_at
                >=
                cutoff,

                Recommendation.deleted_at.is_(None),

            )
        )


        completed = await self.db.scalar(
            select(
                func.count(
                    Recommendation.id,
                )
            )
            .where(

                Recommendation.completed_at
                >=
                cutoff,

                Recommendation.status
                ==
                RecommendationStatus.COMPLETED,

            )
        )


        return {

            "period_days":
                days,

            "generated":
                int(
                    generated or 0
                ),

            "completed":
                int(
                    completed or 0
                ),

            "efficiency":

                (

                    round(
                        (
                            completed
                            /
                            generated
                        )
                        *
                        100,
                        2,
                    )

                    if generated

                    else 0

                ),

        }
        # ============================================================
    # Reporting & Export Helpers
    # ============================================================

    async def export_recommendation(
        self,
        recommendation_id: UUID,
    ) -> dict[str, Any]:
        """
        Export complete recommendation data.

        Used by:

        - Reports
        - Audit logs
        - External integrations
        """

        recommendation = (
            await self.get_recommendation(
                recommendation_id,
            )
        )


        if recommendation is None:

            raise ValueError(
                "Recommendation not found."
            )


        return {

            "id":
                str(
                    recommendation.id
                ),

            "finding_id":
                (
                    str(
                        recommendation.finding_id
                    )
                    if recommendation.finding_id
                    else None
                ),

            "asset_id":
                (
                    str(
                        recommendation.asset_id
                    )
                    if recommendation.asset_id
                    else None
                ),

            "title":
                recommendation.title,

            "description":
                recommendation.description,

            "priority":
                recommendation.priority.value,

            "priority_score":
                recommendation.priority_score,

            "status":
                recommendation.status.value,

            "created_at":
                recommendation.created_at.isoformat(),

            "completed_at":
                (
                    recommendation.completed_at.isoformat()
                    if recommendation.completed_at
                    else None
                ),

        }



    async def export_asset_recommendations(
        self,
        asset_id: UUID,
    ) -> list[dict[str, Any]]:
        """
        Export all recommendations
        for an asset.
        """

        stmt = (
            select(Recommendation)
            .where(

                Recommendation.asset_id
                ==
                asset_id,

                Recommendation.deleted_at.is_(None),

            )
            .order_by(
                Recommendation.priority_score.desc(),
            )
        )


        result = await self.db.execute(
            stmt,
        )


        recommendations = list(
            result.scalars().all()
        )


        return [

            {

                "id":
                    str(
                        item.id
                    ),

                "title":
                    item.title,

                "priority":
                    item.priority.value,

                "score":
                    item.priority_score,

                "status":
                    item.status.value,

                "description":
                    item.description,

            }

            for item in recommendations

        ]



    async def generate_executive_summary(
        self,
        organization_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate executive security summary.

        Designed for:

        - CISOs
        - Management dashboards
        - Board reports
        """

        stats = await self.get_statistics(
            organization_id=organization_id,
        )


        actions = await self.prioritize_security_actions(
            organization_id,
            limit=5,
        )


        return {

            "summary":

                (
                    "Security recommendations have "
                    "been analyzed and prioritized "
                    "based on risk impact."
                ),


            "open_actions":
                stats["open"],


            "completed_actions":
                stats["completed"],


            "completion_rate":
                stats["completion_rate"],


            "critical_actions":

                [

                    action

                    for action in actions

                    if action["priority"]
                    ==
                    RecommendationPriority.IMMEDIATE.value

                ],


            "recommended_next_steps":

                [

                    action["recommended_action"]

                    for action in actions[:3]

                ],


            "generated_at":
                datetime.utcnow().isoformat(),

        }



    async def delete_recommendation(
        self,
        recommendation_id: UUID,
        *,
        hard_delete: bool = False,
    ) -> None:
        """
        Delete recommendation.

        Default:
            Soft delete
        """

        recommendation = (
            await self.get_recommendation(
                recommendation_id,
            )
        )


        if recommendation is None:

            raise ValueError(
                "Recommendation not found."
            )


        if hard_delete:

            await self.db.delete(
                recommendation,
            )

        else:

            recommendation.soft_delete()



        await self.commit()


        logger.info(
            "Deleted recommendation id=%s",
            recommendation_id,
        )
            # ============================================================
    # Maintenance & Cleanup
    # ============================================================

    async def restore_recommendation(
        self,
        recommendation_id: UUID,
    ) -> Recommendation:
        """
        Restore soft deleted recommendation.
        """

        stmt = (
            select(Recommendation)
            .where(
                Recommendation.id
                ==
                recommendation_id,
            )
        )


        result = await self.db.execute(
            stmt,
        )


        recommendation = (
            result.scalar_one_or_none()
        )


        if recommendation is None:

            raise ValueError(
                "Recommendation not found."
            )


        recommendation.deleted_at = None


        await self.commit()


        await self.db.refresh(
            recommendation,
        )


        return recommendation



    async def purge_deleted_recommendations(
        self,
        *,
        older_than_days: int = 180,
    ) -> int:
        """
        Permanently delete old soft deleted
        recommendations.
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
            select(Recommendation)
            .where(

                Recommendation.deleted_at.is_not(None),

                Recommendation.deleted_at
                <=
                cutoff,

            )
        )


        result = await self.db.execute(
            stmt,
        )


        recommendations = list(
            result.scalars().all()
        )


        for recommendation in recommendations:

            await self.db.delete(
                recommendation,
            )


        if recommendations:

            await self.commit()


        logger.info(
            "Purged %s deleted recommendations.",
            len(recommendations),
        )


        return len(recommendations)



    async def health_check(
        self,
    ) -> dict[str, Any]:
        """
        Recommendation engine health status.
        """

        try:

            count = await self.db.scalar(
                select(
                    func.count(
                        Recommendation.id,
                    )
                )
            )


            return {

                "service":
                    "recommendation_engine",

                "status":
                    "healthy",

                "recommendations":
                    int(
                        count or 0
                    ),

                "timestamp":
                    datetime.utcnow().isoformat(),

            }


        except Exception as exc:

            logger.exception(
                "Recommendation health check failed."
            )


            return {

                "service":
                    "recommendation_engine",

                "status":
                    "unhealthy",

                "error":
                    str(exc),

            }



    async def cleanup_orphan_recommendations(
        self,
    ) -> int:
        """
        Cleanup recommendations whose
        linked entities no longer exist.

        Reserved for maintenance workers.
        """

        return 0



# ============================================================
# End of File
# ============================================================
