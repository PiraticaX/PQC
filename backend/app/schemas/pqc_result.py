"""
QShield Enterprise
==================

Post-Quantum Cryptography Result Schemas

Pydantic schemas representing cryptographic inventory,
PQC readiness and migration analysis.

Compatible with Pydantic v2.
"""

from __future__ import annotations

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


class ClassicalAlgorithm(str, Enum):
    """
    Classical cryptographic algorithms.
    """

    RSA = "RSA"

    DSA = "DSA"

    ECDSA = "ECDSA"

    ED25519 = "ED25519"

    DH = "DH"

    ECDH = "ECDH"

    AES = "AES"

    CHACHA20 = "CHACHA20"

    SHA1 = "SHA1"

    SHA2 = "SHA2"

    SHA3 = "SHA3"


class PQCAlgorithm(str, Enum):
    """
    NIST standardized PQC algorithms.
    """

    ML_KEM_512 = "ML-KEM-512"

    ML_KEM_768 = "ML-KEM-768"

    ML_KEM_1024 = "ML-KEM-1024"

    ML_DSA_44 = "ML-DSA-44"

    ML_DSA_65 = "ML-DSA-65"

    ML_DSA_87 = "ML-DSA-87"

    SLH_DSA_SHA2_128S = "SLH-DSA-SHA2-128s"

    SLH_DSA_SHA2_192S = "SLH-DSA-SHA2-192s"

    SLH_DSA_SHA2_256S = "SLH-DSA-SHA2-256s"

    NONE = "NONE"


class CryptoPurpose(str, Enum):
    """
    Cryptographic usage.
    """

    KEY_EXCHANGE = "KEY_EXCHANGE"

    DIGITAL_SIGNATURE = "DIGITAL_SIGNATURE"

    ENCRYPTION = "ENCRYPTION"

    HASHING = "HASHING"

    AUTHENTICATION = "AUTHENTICATION"

    CERTIFICATE = "CERTIFICATE"

    VPN = "VPN"

    TLS = "TLS"

    CODE_SIGNING = "CODE_SIGNING"

    EMAIL = "EMAIL"

    STORAGE = "STORAGE"

    OTHER = "OTHER"


class MigrationPriority(str, Enum):
    """
    PQC migration priority.
    """

    CRITICAL = "CRITICAL"

    HIGH = "HIGH"

    MEDIUM = "MEDIUM"

    LOW = "LOW"


# ============================================================
# Crypto Inventory
# ============================================================


class CryptographicAsset(BaseSchema):
    """
    Individual cryptographic asset.
    """

    name: str

    purpose: CryptoPurpose

    classical_algorithm: ClassicalAlgorithm

    pqc_algorithm: PQCAlgorithm = PQCAlgorithm.NONE

    key_size: int | None = None

    location: str | None = None

    owner: str | None = None

    externally_exposed: bool = False


class HybridCryptography(BaseSchema):
    """
    Hybrid classical + PQC deployment.
    """

    enabled: bool = False

    classical_algorithm: ClassicalAlgorithm | None = None

    pqc_algorithm: PQCAlgorithm | None = None

    interoperable: bool = False

    validated: bool = False


# ============================================================
# Base
# ============================================================


class PQCResultBase(BaseSchema):
    """
    Shared PQC assessment fields.
    """

    asset_id: UUID

    scan_id: UUID

    hostname: str

    cryptographic_assets: list[
        CryptographicAsset
    ] = Field(default_factory=list)

    # ============================================================
# Harvest Now, Decrypt Later (HNDL)
# ============================================================


class HNDLRiskAssessment(BaseSchema):
    """
    Harvest Now, Decrypt Later risk assessment.
    """

    vulnerable: bool = False

    risk_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    risk_level: str

    long_term_confidentiality_required: bool = False

    estimated_quantum_exposure_years: int | None = None

    affected_assets: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# NIST / FIPS Compliance
# ============================================================


class NISTCompliance(BaseSchema):
    """
    NIST PQC compliance status.
    """

    ml_kem_supported: bool = False

    ml_dsa_supported: bool = False

    slh_dsa_supported: bool = False

    approved_algorithms: list[PQCAlgorithm] = Field(
        default_factory=list,
    )

    non_compliant_algorithms: list[
        ClassicalAlgorithm
    ] = Field(default_factory=list)

    notes: str | None = None


class FIPSCompliance(BaseSchema):
    """
    FIPS compliance summary.
    """

    compliant: bool = False

    profile: str | None = None

    deviations: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# Quantum Readiness
# ============================================================


class QuantumReadinessAssessment(BaseSchema):
    """
    Organization quantum readiness.
    """

    score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    grade: str | None = None

    migration_ready: bool = False

    hybrid_ready: bool = False

    inventory_complete: bool = False

    recommendations_pending: int = 0


# ============================================================
# Migration Roadmap
# ============================================================


class MigrationMilestone(BaseSchema):
    """
    PQC migration milestone.
    """

    phase: str

    title: str

    description: str

    priority: MigrationPriority

    estimated_duration: str | None = None

    dependencies: list[str] = Field(
        default_factory=list,
    )


class MigrationRoadmap(BaseSchema):
    """
    PQC migration roadmap.
    """

    current_stage: str

    target_stage: str

    milestones: list[
        MigrationMilestone
    ] = Field(default_factory=list)

    estimated_completion: str | None = None


# ============================================================
# Inventory Summary
# ============================================================


class CryptographicInventorySummary(BaseSchema):
    """
    Summary of cryptographic inventory.
    """

    total_assets: int = 0

    classical_only: int = 0

    hybrid: int = 0

    pqc_native: int = 0

    externally_exposed: int = 0

    long_term_sensitive: int = 0
    # ============================================================
# Algorithm Distribution
# ============================================================


class AlgorithmDistribution(BaseSchema):
    """
    Distribution of cryptographic algorithms.
    """

    classical: dict[
        ClassicalAlgorithm,
        int,
    ] = Field(default_factory=dict)

    post_quantum: dict[
        PQCAlgorithm,
        int,
    ] = Field(default_factory=dict)


# ============================================================
# Migration Progress
# ============================================================


class MigrationProgress(BaseSchema):
    """
    PQC migration progress.
    """

    percentage_complete: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    completed_assets: int = 0

    remaining_assets: int = 0

    blocked_assets: int = 0

    current_phase: str | None = None


# ============================================================
# Vulnerabilities
# ============================================================


class PQCVulnerability(BaseSchema):
    """
    Post-quantum security finding.
    """

    id: str

    title: str

    severity: str

    affected_asset: str

    description: str

    classical_algorithm: (
        ClassicalAlgorithm | None
    ) = None

    recommended_pqc_algorithm: (
        PQCAlgorithm | None
    ) = None

    remediation: str | None = None


# ============================================================
# Recommendations
# ============================================================


class PQCRecommendation(BaseSchema):
    """
    PQC migration recommendation.
    """

    title: str

    description: str

    priority: MigrationPriority

    affected_assets: list[str] = Field(
        default_factory=list,
    )

    target_algorithm: (
        PQCAlgorithm | None
    ) = None

    estimated_effort: str | None = None


# ============================================================
# Response
# ============================================================


class PQCResultResponse(
    UUIDTimestampSchema,
    PQCResultBase,
):
    """
    Standard PQC assessment response.
    """

    inventory_summary: (
        CryptographicInventorySummary
    )

    readiness: QuantumReadinessAssessment

    hybrid_cryptography: HybridCryptography

    hndl_risk: HNDLRiskAssessment

    nist_compliance: NISTCompliance

    fips_compliance: FIPSCompliance

    roadmap: MigrationRoadmap

    migration_progress: MigrationProgress

    algorithm_distribution: (
        AlgorithmDistribution
    )

    vulnerabilities: list[
        PQCVulnerability
    ] = Field(default_factory=list)

    recommendations: list[
        PQCRecommendation
    ] = Field(default_factory=list)


# ============================================================
# Detail
# ============================================================


class PQCResultDetail(
    PQCResultResponse
):
    """
    Detailed PQC assessment.
    """

    cryptographic_inventory: list[
        CryptographicAsset
    ] = Field(default_factory=list)

    migration_notes: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, str] = Field(
        default_factory=dict,
    )
    # ============================================================
# Algorithm Adoption
# ============================================================


class AlgorithmAdoptionStatistics(BaseSchema):
    """
    Cryptographic algorithm adoption statistics.
    """

    classical_only: int = 0

    hybrid: int = 0

    pqc_native: int = 0

    ml_kem: int = 0

    ml_dsa: int = 0

    slh_dsa: int = 0


# ============================================================
# Readiness Distribution
# ============================================================


class ReadinessDistribution(BaseSchema):
    """
    Quantum readiness distribution.
    """

    critical: int = 0

    poor: int = 0

    fair: int = 0

    good: int = 0

    excellent: int = 0


# ============================================================
# Statistics
# ============================================================


class PQCStatistics(BaseSchema):
    """
    Aggregate PQC assessment statistics.
    """

    total_assets: int = 0

    total_cryptographic_assets: int = 0

    average_readiness_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    average_hndl_risk: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    algorithm_adoption: (
        AlgorithmAdoptionStatistics
    )

    readiness_distribution: (
        ReadinessDistribution
    )

    migration_ready_assets: int = 0

    hybrid_deployments: int = 0

    non_compliant_assets: int = 0


# ============================================================
# Dashboard
# ============================================================


class PQCDashboard(BaseSchema):
    """
    Post-Quantum Cryptography dashboard.
    """

    statistics: PQCStatistics

    highest_risk_assets: list[
        PQCResultResponse
    ] = Field(default_factory=list)

    migration_ready_assets: list[
        PQCResultResponse
    ] = Field(default_factory=list)

    critical_hndl_assets: list[
        PQCResultResponse
    ] = Field(default_factory=list)

    non_compliant_assets: list[
        PQCResultResponse
    ] = Field(default_factory=list)


# ============================================================
# Export
# ============================================================


class PQCExportResponse(BaseSchema):
    """
    Export metadata.
    """

    filename: str

    format: str

    generated_at: datetime

    total_records: int

    download_url: str | None = None


# ============================================================
# List Response
# ============================================================


class PQCListResponse(BaseSchema):
    """
    Paginated PQC assessment results.
    """

    results: list[
        PQCResultResponse
    ] = Field(default_factory=list)

    total: int

    page: int = 1

    page_size: int = 25

    total_pages: int = 1


# ============================================================
# End of File
# ============================================================
