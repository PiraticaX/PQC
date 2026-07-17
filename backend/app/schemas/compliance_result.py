"""
QShield Enterprise
==================

Compliance Result Schemas

Pydantic schemas representing compliance assessments,
framework mappings, controls, evidence and gap analysis.

Compatible with Pydantic v2.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import Field

from app.schemas.base import (
    BaseSchema,
    UUIDTimestampSchema,
)


# ============================================================
# Enumerations
# ============================================================


class ComplianceFramework(str, Enum):
    """
    Supported compliance frameworks.
    """

    NIST_CSF_20 = "NIST_CSF_2.0"

    ISO_27001_2022 = "ISO_27001_2022"

    CIS_CONTROLS_V8 = "CIS_CONTROLS_V8"

    PCI_DSS_40 = "PCI_DSS_4.0"

    SOC2 = "SOC2"

    HIPAA = "HIPAA"

    GDPR = "GDPR"

    NIS2 = "NIS2"

    CMMC_20 = "CMMC_2.0"

    IEC_62443 = "IEC_62443"

    DORA = "DORA"

    CUSTOM = "CUSTOM"


class ComplianceStatus(str, Enum):
    """
    Compliance state.
    """

    COMPLIANT = "COMPLIANT"

    PARTIALLY_COMPLIANT = "PARTIALLY_COMPLIANT"

    NON_COMPLIANT = "NON_COMPLIANT"

    NOT_APPLICABLE = "NOT_APPLICABLE"

    NOT_ASSESSED = "NOT_ASSESSED"


class ControlSeverity(str, Enum):
    """
    Importance of a compliance control.
    """

    CRITICAL = "CRITICAL"

    HIGH = "HIGH"

    MEDIUM = "MEDIUM"

    LOW = "LOW"

    INFORMATIONAL = "INFORMATIONAL"


class EvidenceType(str, Enum):
    """
    Evidence classification.
    """

    CONFIGURATION = "CONFIGURATION"

    LOG = "LOG"

    SCREENSHOT = "SCREENSHOT"

    REPORT = "REPORT"

    CERTIFICATE = "CERTIFICATE"

    POLICY = "POLICY"

    PROCEDURE = "PROCEDURE"

    API_RESPONSE = "API_RESPONSE"

    SCAN_RESULT = "SCAN_RESULT"

    MANUAL = "MANUAL"


# ============================================================
# Framework
# ============================================================


class FrameworkReference(BaseSchema):
    """
    Compliance framework information.
    """

    framework: ComplianceFramework

    version: str

    display_name: str

    publisher: str

    description: str | None = None


# ============================================================
# Control
# ============================================================


class ComplianceControl(BaseSchema):
    """
    Compliance control definition.
    """

    control_id: str

    title: str

    description: str

    family: str

    severity: ControlSeverity

    framework: ComplianceFramework

    mandatory: bool = True

    automated: bool = False


# ============================================================
# Evidence
# ============================================================


class ComplianceEvidence(BaseSchema):
    """
    Evidence supporting a compliance decision.
    """

    evidence_id: UUID

    title: str

    type: EvidenceType

    description: str | None = None

    source: str | None = None

    collected_at: datetime

    collected_by: str | None = None

    verified: bool = False

    reference: str | None = None


# ============================================================
# Base
# ============================================================


class ComplianceResultBase(BaseSchema):
    """
    Shared compliance assessment fields.
    """

    asset_id: UUID

    scan_id: UUID

    hostname: str

    framework: ComplianceFramework
    # ============================================================
# Control Assessment
# ============================================================


class ControlAssessment(BaseSchema):
    """
    Assessment result for a single compliance control.
    """

    control: ComplianceControl

    status: ComplianceStatus

    score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    assessed_at: datetime

    assessor: str | None = None

    automated: bool = False

    notes: str | None = None

    evidence: list[
        ComplianceEvidence
    ] = Field(default_factory=list)


# ============================================================
# Assessment Finding
# ============================================================


class ComplianceFinding(BaseSchema):
    """
    Compliance assessment finding.
    """

    id: str

    title: str

    description: str

    severity: ControlSeverity

    status: ComplianceStatus

    affected_controls: list[str] = Field(
        default_factory=list,
    )

    evidence_ids: list[UUID] = Field(
        default_factory=list,
    )

    recommendation: str | None = None


# ============================================================
# Exception / Risk Acceptance
# ============================================================


class ComplianceException(BaseSchema):
    """
    Approved compliance exception.
    """

    exception_id: UUID

    control_id: str

    justification: str

    approved_by: str

    approved_at: datetime

    expires_at: datetime | None = None

    compensating_controls: list[str] = Field(
        default_factory=list,
    )

    active: bool = True


# ============================================================
# Gap Analysis
# ============================================================


class ComplianceGap(BaseSchema):
    """
    Gap preventing compliance.
    """

    control_id: str

    title: str

    current_state: str

    required_state: str

    severity: ControlSeverity

    estimated_effort: str | None = None

    estimated_cost: str | None = None


# ============================================================
# Remediation
# ============================================================


class RemediationTask(BaseSchema):
    """
    Individual remediation action.
    """

    task_id: UUID

    title: str

    description: str

    owner: str | None = None

    priority: ControlSeverity

    completed: bool = False

    due_date: datetime | None = None


class RemediationPlan(BaseSchema):
    """
    Compliance remediation roadmap.
    """

    name: str

    completion_percentage: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    estimated_completion: datetime | None = None

    tasks: list[
        RemediationTask
    ] = Field(default_factory=list)


# ============================================================
# Compliance Score
# ============================================================


class ComplianceScore(BaseSchema):
    """
    Overall framework score.
    """

    overall_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    maturity_level: str | None = None

    compliant_controls: int = 0

    partially_compliant_controls: int = 0

    non_compliant_controls: int = 0

    not_applicable_controls: int = 0

    # ============================================================
# Framework Summary
# ============================================================


class ComplianceFrameworkSummary(BaseSchema):
    """
    High-level framework summary.
    """

    framework: ComplianceFramework

    version: str

    total_controls: int = 0

    assessed_controls: int = 0

    compliant_controls: int = 0

    partially_compliant_controls: int = 0

    non_compliant_controls: int = 0

    overall_status: ComplianceStatus

    score: float = Field(
        default=0,
        ge=0,
        le=100,
    )


# ============================================================
# Evidence Summary
# ============================================================


class ComplianceEvidenceSummary(BaseSchema):
    """
    Summary of collected evidence.
    """

    total_evidence: int = 0

    verified_evidence: int = 0

    pending_verification: int = 0

    evidence_types: dict[
        EvidenceType,
        int,
    ] = Field(default_factory=dict)


# ============================================================
# Compliance Trend
# ============================================================


class ComplianceTrend(BaseSchema):
    """
    Historical compliance score.
    """

    assessment_date: datetime

    score: float = Field(
        ge=0,
        le=100,
    )

    compliant_controls: int

    non_compliant_controls: int


# ============================================================
# Executive Summary
# ============================================================


class ExecutiveSummary(BaseSchema):
    """
    Executive-level assessment summary.
    """

    overview: str

    key_strengths: list[str] = Field(
        default_factory=list,
    )

    key_risks: list[str] = Field(
        default_factory=list,
    )

    top_priorities: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# Response
# ============================================================


class ComplianceResultResponse(
    UUIDTimestampSchema,
    ComplianceResultBase,
):
    """
    Standard compliance assessment response.
    """

    framework_summary: (
        ComplianceFrameworkSummary
    )

    score: ComplianceScore

    evidence_summary: (
        ComplianceEvidenceSummary
    )

    executive_summary: ExecutiveSummary

    control_assessments: list[
        ControlAssessment
    ] = Field(default_factory=list)

    findings: list[
        ComplianceFinding
    ] = Field(default_factory=list)

    gaps: list[
        ComplianceGap
    ] = Field(default_factory=list)

    remediation_plan: RemediationPlan

    exceptions: list[
        ComplianceException
    ] = Field(default_factory=list)


# ============================================================
# Detail
# ============================================================


class ComplianceResultDetail(
    ComplianceResultResponse
):
    """
    Detailed compliance assessment.
    """

    evidence: list[
        ComplianceEvidence
    ] = Field(default_factory=list)

    trends: list[
        ComplianceTrend
    ] = Field(default_factory=list)

    metadata: dict[str, str] = Field(
        default_factory=dict,
    )
    # ============================================================
# Framework Distribution
# ============================================================


class FrameworkDistribution(BaseSchema):
    """
    Compliance framework distribution.
    """

    framework: ComplianceFramework

    assessed_assets: int

    compliant_assets: int

    average_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )


# ============================================================
# Control Status Distribution
# ============================================================


class ControlStatusDistribution(BaseSchema):
    """
    Distribution of control assessment status.
    """

    compliant: int = 0

    partially_compliant: int = 0

    non_compliant: int = 0

    not_applicable: int = 0

    not_assessed: int = 0


# ============================================================
# Maturity Distribution
# ============================================================


class ComplianceMaturityDistribution(BaseSchema):
    """
    Compliance maturity distribution.
    """

    initial: int = 0

    developing: int = 0

    defined: int = 0

    managed: int = 0

    optimized: int = 0


# ============================================================
# Statistics
# ============================================================


class ComplianceStatistics(BaseSchema):
    """
    Aggregate compliance statistics.
    """

    total_assets: int = 0

    total_assessments: int = 0

    average_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    total_controls: int = 0

    total_findings: int = 0

    total_exceptions: int = 0

    total_evidence: int = 0

    framework_distribution: list[
        FrameworkDistribution
    ] = Field(default_factory=list)

    control_status: (
        ControlStatusDistribution
    )

    maturity_distribution: (
        ComplianceMaturityDistribution
    )


# ============================================================
# Dashboard Summary
# ============================================================


class ComplianceDashboardSummary(BaseSchema):
    """
    Executive dashboard summary.
    """

    average_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    compliant_assets: int = 0

    non_compliant_assets: int = 0

    critical_findings: int = 0

    overdue_remediations: int = 0

    expiring_exceptions: int = 0

    evidence_pending_review: int = 0
    # ============================================================
# Dashboard
# ============================================================


class ComplianceDashboard(BaseSchema):
    """
    Enterprise compliance dashboard.
    """

    summary: ComplianceDashboardSummary

    statistics: ComplianceStatistics

    highest_scoring_assets: list[
        ComplianceResultResponse
    ] = Field(default_factory=list)

    lowest_scoring_assets: list[
        ComplianceResultResponse
    ] = Field(default_factory=list)

    critical_findings: list[
        ComplianceFinding
    ] = Field(default_factory=list)

    remediation_overview: list[
        RemediationTask
    ] = Field(default_factory=list)

    expiring_exceptions: list[
        ComplianceException
    ] = Field(default_factory=list)


# ============================================================
# Export
# ============================================================


class ComplianceExportResponse(BaseSchema):
    """
    Compliance export metadata.
    """

    filename: str

    format: str

    generated_at: datetime

    total_records: int

    framework: ComplianceFramework | None = None

    download_url: str | None = None


# ============================================================
# List Response
# ============================================================


class ComplianceListResponse(BaseSchema):
    """
    Paginated compliance assessment results.
    """

    results: list[
        ComplianceResultResponse
    ] = Field(default_factory=list)

    total: int

    page: int = 1

    page_size: int = 25

    total_pages: int = 1


# ============================================================
# Convenience Summary
# ============================================================


class ComplianceOverview(BaseSchema):
    """
    Lightweight overview used by dashboards
    and API summaries.
    """

    framework: ComplianceFramework

    status: ComplianceStatus

    score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    assessed_controls: int = 0

    compliant_controls: int = 0

    outstanding_findings: int = 0

    last_assessment: datetime | None = None


# ============================================================
# End of File
# ============================================================