"""
QShield Enterprise
==================

Scan Service Tests.

Tests:

- Scan creation logic
- Scan execution workflow
- Finding processing
- Risk scoring
- PQC scan handling
- Scan failure recovery
- Service exceptions

"""

from __future__ import annotations



import pytest



from backend.tests.fixtures.scans import (
    create_scan,
    vulnerability_scan,
    pqc_assessment_scan,
    failed_scan,
    running_scan,
)



# ============================================================
# Scan Creation Tests
# ============================================================


def test_create_scan_payload():
    """
    Scan creation payload validation.
    """

    scan = create_scan()



    assert scan["id"]

    assert scan["type"] == "security"

    assert scan["status"] == "completed"



def test_scan_default_findings():
    """
    New scans should have findings collection.
    """

    scan = create_scan()



    assert isinstance(

        scan["findings"],

        list,

    )



# ============================================================
# Scan Execution Tests
# ============================================================


def test_scan_execution_state():
    """
    Running scans should track progress.
    """

    scan = running_scan()



    assert scan["status"] == "running"

    assert scan["progress"] > 0



def test_completed_scan_state():
    """
    Completed scans should contain results.
    """

    scan = vulnerability_scan()



    assert scan["status"] == "completed"

    assert scan["findings"]



# ============================================================
# Vulnerability Processing Tests
# ============================================================


def test_vulnerability_finding_processing():
    """
    Vulnerability findings should be processed.
    """

    scan = vulnerability_scan()



    finding = scan["findings"][0]



    assert finding["id"]

    assert finding["severity"]

    assert finding["title"]



def test_risk_score_calculation():
    """
    Risk score should be calculated.
    """

    scan = vulnerability_scan()



    assert scan["risk_score"] > 0

    assert scan["risk_score"] <= 100



# ============================================================
# PQC Scan Tests
# ============================================================


def test_pqc_scan_processing():
    """
    PQC scans should identify crypto risks.
    """

    scan = pqc_assessment_scan()



    assert scan["type"] == "pqc_assessment"



    assert scan["cryptography"]["rsa"] is True



    assert scan["cryptography"]["pqc_ready"] is False



def test_pqc_recommendations():
    """
    PQC migration recommendations.
    """

    scan = pqc_assessment_scan()



    assert len(

        scan["recommendations"]

    ) > 0



# ============================================================
# Failure Handling Tests
# ============================================================


def test_failed_scan_recovery():
    """
    Failed scans should store retry information.
    """

    scan = failed_scan()



    assert scan["status"] == "failed"

    assert scan["retry_count"] > 0



def test_failed_scan_error_message():
    """
    Failed scans should include errors.
    """

    scan = failed_scan()



    assert scan["error"]



# ============================================================
# Service Validation Tests
# ============================================================


def test_scan_requires_target():
    """
    Scan must have target.
    """

    scan = create_scan()



    assert scan["target"]



def test_scan_identifier_exists():
    """
    Scan should have identifier.
    """

    scan = create_scan()



    assert scan["id"] is not None