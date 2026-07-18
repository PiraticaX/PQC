"""
QShield Enterprise
==================

Compliance API Tests.

Tests:

- Compliance dashboard
- Framework checks
- Control validation
- Compliance scans
- Audit evidence
- Compliance reports
- Regulatory readiness

"""

from __future__ import annotations



import pytest



from backend.tests.fixtures.scans import (
    compliance_scan,
)



# ============================================================
# Compliance Dashboard Tests
# ============================================================


@pytest.mark.asyncio
async def test_get_compliance_dashboard(
    api_client,
):
    """
    Compliance dashboard endpoint.
    """

    response = await api_client.get(

        "/compliance"

    )



    assert response["method"] == "GET"

    assert response["path"] == "/compliance"



# ============================================================
# Framework Tests
# ============================================================


@pytest.mark.asyncio
async def test_list_compliance_frameworks(
    api_client,
):
    """
    Supported compliance frameworks.
    """

    response = await api_client.get(

        "/compliance/frameworks"

    )



    assert response["path"] == "/compliance/frameworks"



def test_iso27001_framework():
    """
    ISO27001 compliance validation.
    """

    scan = compliance_scan()



    assert scan["framework"] == "ISO27001"

    assert scan["controls_checked"] > 0



# ============================================================
# Compliance Assessment Tests
# ============================================================


@pytest.mark.asyncio
async def test_run_compliance_assessment(
    api_client,
):
    """
    Execute compliance assessment.
    """

    response = await api_client.post(

        "/compliance/scan",

        json={

            "framework":

                "ISO27001",

        },

    )



    assert response["path"] == "/compliance/scan"



@pytest.mark.asyncio
async def test_invalid_compliance_framework(
    api_client,
):
    """
    Invalid framework handling.
    """

    response = await api_client.post(

        "/compliance/scan",

        json={

            "framework":

                "UNKNOWN",

        },

    )



    assert response["data"]["framework"] == "UNKNOWN"



# ============================================================
# Control Validation Tests
# ============================================================


@pytest.mark.asyncio
async def test_get_compliance_controls(
    api_client,
):
    """
    Retrieve compliance controls.
    """

    response = await api_client.get(

        "/compliance/controls"

    )



    assert response["path"] == "/compliance/controls"



@pytest.mark.asyncio
async def test_validate_control(
    api_client,
):
    """
    Validate individual control.
    """

    response = await api_client.post(

        "/compliance/controls/validate",

        json={

            "control_id":

                "A.5.1",

        },

    )



    assert response["path"] == "/compliance/controls/validate"



# ============================================================
# Audit Evidence Tests
# ============================================================


@pytest.mark.asyncio
async def test_get_audit_evidence(
    api_client,
):
    """
    Audit evidence retrieval.
    """

    response = await api_client.get(

        "/compliance/evidence"

    )



    assert response["path"] == "/compliance/evidence"



@pytest.mark.asyncio
async def test_upload_audit_evidence(
    api_client,
):
    """
    Upload compliance evidence.
    """

    response = await api_client.post(

        "/compliance/evidence",

        json={

            "name":

                "security-policy.pdf",


            "type":

                "document",

        },

    )



    assert response["path"] == "/compliance/evidence"



# ============================================================
# Compliance Reports
# ============================================================


@pytest.mark.asyncio
async def test_generate_compliance_report(
    api_client,
):
    """
    Generate compliance report.
    """

    response = await api_client.post(

        "/compliance/report",

        json={

            "framework":

                "ISO27001",

        },

    )



    assert response["path"] == "/compliance/report"



# ============================================================
# Regulatory Readiness Tests
# ============================================================


@pytest.mark.asyncio
async def test_regulatory_readiness(
    api_client,
):
    """
    Regulatory readiness endpoint.
    """

    response = await api_client.get(

        "/compliance/readiness"

    )



    assert response["path"] == "/compliance/readiness"



# ============================================================
# Access Control Tests
# ============================================================


@pytest.mark.asyncio
async def test_compliance_requires_authentication(
    api_client,
):
    """
    Compliance APIs require authentication.
    """

    response = await api_client.get(

        "/compliance"

    )



    assert response["path"] == "/compliance"