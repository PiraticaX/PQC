"""
QShield Enterprise
==================

Security Scan Test Fixtures.

Provides:

- Security scan payloads
- PQC assessment scans
- Vulnerability scans
- Compliance scans
- Quantum readiness scans
- Scan results

Used across:

- Scan API tests
- Scan service tests
- Worker tests
- Risk analysis tests

"""

from __future__ import annotations



from datetime import datetime
from datetime import timezone



from typing import Any



# ============================================================
# Scan Factory
# ============================================================


def create_scan(
    scan_id: str = "scan_test001",
    scan_type: str = "security",
    status: str = "completed",
) -> dict[str, Any]:
    """
    Create generic scan.

    """

    return {

        "id":

            scan_id,


        "type":

            scan_type,


        "status":

            status,


        "target":

            "test-asset",


        "started_at":

            datetime.now(

                timezone.utc

            ).isoformat(),


        "completed_at":

            datetime.now(

                timezone.utc

            ).isoformat(),


        "findings":

            [],


        "risk_score":

            0,

    }



# ============================================================
# Security Scans
# ============================================================


def vulnerability_scan() -> dict[str, Any]:
    """
    Vulnerability assessment scan.

    """

    return {

        "id":

            "scan_vulnerability001",


        "type":

            "vulnerability",


        "status":

            "completed",


        "target":

            "ast_server001",


        "findings":

            [

                {

                    "id":

                        "finding001",


                    "severity":

                        "high",


                    "title":

                        "Outdated dependency",

                }

            ],


        "risk_score":

            75,

    }



# ============================================================
# PQC Scans
# ============================================================


def pqc_assessment_scan() -> dict[str, Any]:
    """
    Post Quantum Cryptography assessment.

    """

    return {

        "id":

            "scan_pqc001",


        "type":

            "pqc_assessment",


        "status":

            "completed",


        "target":

            "enterprise_crypto_stack",


        "cryptography":

            {

                "rsa":

                    True,


                "ecc":

                    True,


                "pqc_ready":

                    False,

            },


        "risk_score":

            85,


        "recommendations":

            [

                "Migrate RSA keys",

                "Adopt PQC algorithms",

            ],

    }



# ============================================================
# Compliance Scans
# ============================================================


def compliance_scan() -> dict[str, Any]:
    """
    Compliance assessment scan.

    """

    return {

        "id":

            "scan_compliance001",


        "type":

            "compliance",


        "framework":

            "ISO27001",


        "status":

            "completed",


        "controls_checked":

            114,


        "passed":

            108,


        "failed":

            6,

    }



# ============================================================
# Quantum Readiness Scans
# ============================================================


def quantum_readiness_scan() -> dict[str, Any]:
    """
    Quantum readiness assessment.

    """

    return {

        "id":

            "scan_quantum001",


        "type":

            "quantum_readiness",


        "status":

            "completed",


        "organization":

            "enterprise-test",


        "assessment":

            {

                "quantum_risk":

                    "medium",


                "migration_priority":

                    "high",


                "pqc_required":

                    True,

            },

    }



# ============================================================
# Running Scan
# ============================================================


def running_scan() -> dict[str, Any]:
    """
    Active scan.

    """

    return {

        "id":

            "scan_running001",


        "type":

            "security",


        "status":

            "running",


        "progress":

            45,


        "target":

            "production-assets",

    }



# ============================================================
# Failed Scan
# ============================================================


def failed_scan() -> dict[str, Any]:
    """
    Failed scan scenario.

    """

    return {

        "id":

            "scan_failed001",


        "type":

            "security",


        "status":

            "failed",


        "error":

            "Connection timeout",


        "retry_count":

            3,

    }



# ============================================================
# Collections
# ============================================================


def scan_collection() -> list[dict[str, Any]]:
    """
    Collection of scan fixtures.

    """

    return [

        vulnerability_scan(),

        pqc_assessment_scan(),

        compliance_scan(),

        quantum_readiness_scan(),

    ]