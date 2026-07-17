"""
QShield Enterprise
==================

Post-Quantum Cryptography (PQC) Result Model

Stores quantum-readiness assessment results discovered during a scan.

One scan may generate multiple PQCResult records for different
services, endpoints, certificates, or applications.
"""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import (
    Boolean,
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


class PQCReadinessLevel(str, enum.Enum):
    NOT_READY = "Not Ready"
    PLANNING = "Planning"
    HYBRID = "Hybrid"
    PQC_READY = "PQC Ready"


# ============================================================
# MODEL
# ============================================================


class PQCResult(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    Post-Quantum Cryptography assessment.
    """

    __tablename__ = "pqc_results"

    __table_args__ = (
        Index("idx_pqc_scan", "scan_id"),
        Index("idx_pqc_target", "target"),
        Index("idx_pqc_readiness", "readiness"),
    )

    # ============================================================
    # Relationships
    # ============================================================

    scan_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey(
            "scans.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # ============================================================
    # Target
    # ============================================================

    target: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    service: Mapped[str | None] = mapped_column(
        String(255),
    )

    # ============================================================
    # Classical Cryptography
    # ============================================================

    rsa_detected: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    ecc_detected: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    ecdh_detected: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    ecdsa_detected: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    diffie_hellman_detected: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # ============================================================
    # PQC Support
    # ============================================================

    ml_kem_supported: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    ml_dsa_supported: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    slh_dsa_supported: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    hybrid_mode: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    readiness: Mapped[PQCReadinessLevel] = mapped_column(
        Enum(PQCReadinessLevel),
        default=PQCReadinessLevel.NOT_READY,
        nullable=False,
    )

    # ============================================================
    # Assessment
    # ============================================================

    quantum_vulnerable: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    migration_required: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    migration_priority: Mapped[int] = mapped_column(
        Integer,
        default=5,
    )

    findings: Mapped[str | None] = mapped_column(
        Text,
    )

    recommendations: Mapped[str | None] = mapped_column(
        Text,
    )

    # ============================================================
    # Relationships
    # ============================================================

    scan = relationship(
        "Scan",
        back_populates="pqc_results",
    )
        # ============================================================
    # Helper Properties
    # ============================================================

    @property
    def classical_algorithms(self) -> list[str]:
        """
        Return the detected classical cryptographic algorithms.
        """

        algorithms: list[str] = []

        if self.rsa_detected:
            algorithms.append("RSA")

        if self.ecc_detected:
            algorithms.append("ECC")

        if self.ecdh_detected:
            algorithms.append("ECDH")

        if self.ecdsa_detected:
            algorithms.append("ECDSA")

        if self.diffie_hellman_detected:
            algorithms.append("Diffie-Hellman")

        return algorithms

    @property
    def pqc_algorithms(self) -> list[str]:
        """
        Return the detected NIST-standardized PQC algorithms.
        """

        algorithms: list[str] = []

        if self.ml_kem_supported:
            algorithms.append("ML-KEM")

        if self.ml_dsa_supported:
            algorithms.append("ML-DSA")

        if self.slh_dsa_supported:
            algorithms.append("SLH-DSA")

        return algorithms

    @property
    def pqc_algorithm_count(self) -> int:
        return len(self.pqc_algorithms)

    @property
    def is_pqc_enabled(self) -> bool:
        """
        Returns True if at least one PQC algorithm is supported.
        """

        return self.pqc_algorithm_count > 0

    @property
    def is_quantum_ready(self) -> bool:
        """
        Conservative quantum-readiness assessment.
        """

        return (
            self.readiness == PQCReadinessLevel.PQC_READY
            and self.is_pqc_enabled
            and not self.quantum_vulnerable
        )

    # ============================================================
    # Serialization
    # ============================================================

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "scan_id": str(self.scan_id),
            "target": self.target,
            "service": self.service,
            "rsa_detected": self.rsa_detected,
            "ecc_detected": self.ecc_detected,
            "ecdh_detected": self.ecdh_detected,
            "ecdsa_detected": self.ecdsa_detected,
            "diffie_hellman_detected": self.diffie_hellman_detected,
            "classical_algorithms": self.classical_algorithms,
            "ml_kem_supported": self.ml_kem_supported,
            "ml_dsa_supported": self.ml_dsa_supported,
            "slh_dsa_supported": self.slh_dsa_supported,
            "pqc_algorithms": self.pqc_algorithms,
            "pqc_algorithm_count": self.pqc_algorithm_count,
            "hybrid_mode": self.hybrid_mode,
            "readiness": self.readiness.value,
            "quantum_vulnerable": self.quantum_vulnerable,
            "migration_required": self.migration_required,
            "migration_priority": self.migration_priority,
            "is_pqc_enabled": self.is_pqc_enabled,
            "is_quantum_ready": self.is_quantum_ready,
            "findings": self.findings,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            "<PQCResult("
            f"id={self.id}, "
            f"target='{self.target}', "
            f"readiness='{self.readiness.value}'"
            ")>"
        )