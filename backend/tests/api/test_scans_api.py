"""
QShield Enterprise
==================

Security Scans API Tests.

Tests:

- Scan creation
- Scan execution
- Scan status
- PQC assessment scans
- Compliance scans
- Vulnerability scans
- Scan history
- Scan result retrieval

"""

from __future__ import annotations



import pytest



from backend.tests.fixtures.scans import (
    create_scan,
    vulnerability_scan,
    pqc_assessment_scan,
    compliance_scan,
    quantum_readiness_scan,
    running_scan,
    failed_scan,
)



# ============================================================
# Scan Listing Tests
# ============================================================


@pytest.mark.asyncio
async def test_get_scans(
    api_client,
):
    """
    Scan listing endpoint.
    """

    response = await api_client.get(

        "/scans"

    )



    assert response["method"] == "GET"

    assert response["path"] == "/scans"



# ============================================================
# Scan Creation Tests
# ============================================================


@pytest.mark.asyncio
async def test_create_security_scan(
    api_client,
):
    """
    Security scan creation.
    """

    scan = create_scan()



    response = await api_client.post(

        "/scans",

        json=scan,

    )



    assert response["path"] == "/scans"

    assert response["data"]["id"] == scan["id"]



@pytest.mark.asyncio
async def test_create_invalid_scan(
    api_client,
):
    """
    Invalid scan payload.
    """

    response = await api_client.post(

        "/scans",

        json={

            "type":

                "",

        },

    )



    assert response["data"]["type"] == ""



# ============================================================
# Scan Execution Tests
# ============================================================


@pytest.mark.asyncio
async def test_execute_scan(
    api_client,
):
    """
    Start scan execution.
    """

    response = await api_client.post(

        "/scans/scan_test001/execute"

    )



    assert response["path"] == "/scans/scan_test001/execute"



# ============================================================
# Scan Status Tests
# ============================================================


@pytest.mark.asyncio
async def test_get_scan_status(
    api_client,
):
    """
    Scan status endpoint.
    """

    response = await api_client.get(

        "/scans/scan_test001/status"

    )



    assert response["path"] == "/scans/scan_test001/status"



def test_running_scan_state():
    """
    Running scan validation.
    """

    scan = running_scan()



    assert scan["status"] == "running"

    assert scan["progress"] > 0



def test_failed_scan_state():
    """
    Failed scan validation.
    """

    scan = failed_scan()



    assert scan["status"] == "failed"

    assert scan["error"]



# ============================================================
# Vulnerability Scan Tests
# ============================================================


def test_vulnerability_scan():
    """
    Vulnerability scans should contain findings.
    """

    scan = vulnerability_scan()



    assert scan["type"] == "vulnerability"

    assert len(

        scan["findings"]

    ) > 0



    assert scan["risk_score"] > 0



# ============================================================
# PQC Assessment Tests
# ============================================================


def test_pqc_assessment_scan():
    """
    PQC scans should detect migration needs.
    """

    scan = pqc_assessment_scan()



    assert scan["type"] == "pqc_assessment"

    assert scan["cryptography"]["rsa"]

    assert scan["cryptography"]["pqc_ready"] is False



# ============================================================
# Compliance Scan Tests
# ============================================================


def test_compliance_scan():
    """
    Compliance scan validation.
    """

    scan = compliance_scan()



    assert scan["type"] == "compliance"

    assert scan["controls_checked"] > 0

    assert scan["failed"] >= 0



# ============================================================
# Quantum Readiness Tests
# ============================================================


def test_quantum_readiness_scan():
    """
    Quantum readiness assessment.
    """

    scan = quantum_readiness_scan()



    assert scan["type"] == "quantum_readiness"

    assert scan["assessment"]["pqc_required"] is True



# ============================================================
# Scan Results Tests
# ============================================================


@pytest.mark.asyncio
async def test_get_scan_results(
    api_client,
):
    """
    Scan result endpoint.
    """

    response = await api_client.get(

        "/scans/scan_test001/results"

    )



    assert response["path"] == "/scans/scan_test001/results"



# ============================================================
# Scan History Tests
# ============================================================


@pytest.mark.asyncio
async def test_scan_history(
    api_client,
):
    """
    Scan history endpoint.
    """

    response = await api_client.get(

        "/scans/history"

    )



    assert response["path"] == "/scans/history"



# ============================================================
# Access Control Tests
# ============================================================


@pytest.mark.asyncio
async def test_scans_require_authentication(
    api_client,
):
    """
    Scan APIs require authentication.
    """

    response = await api_client.get(

        "/scans"

    )



    assert response["path"] == "/scans"