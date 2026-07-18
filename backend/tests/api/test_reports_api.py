"""
QShield Enterprise
==================

Reports API Tests.

Tests:

- Report generation
- Report retrieval
- Report export
- Security reports
- Compliance reports
- PQC migration reports
- Report history

"""

from __future__ import annotations



import pytest



# ============================================================
# Report Listing Tests
# ============================================================


@pytest.mark.asyncio
async def test_get_reports(
    api_client,
):
    """
    Reports listing endpoint.
    """

    response = await api_client.get(

        "/reports"

    )



    assert response["method"] == "GET"

    assert response["path"] == "/reports"



# ============================================================
# Report Generation Tests
# ============================================================


@pytest.mark.asyncio
async def test_generate_report(
    api_client,
):
    """
    Generate security report.
    """

    response = await api_client.post(

        "/reports",

        json={

            "type":

                "security",


            "format":

                "json",

        },

    )



    assert response["path"] == "/reports"

    assert response["data"]["type"] == "security"



@pytest.mark.asyncio
async def test_generate_invalid_report(
    api_client,
):
    """
    Invalid report payload.
    """

    response = await api_client.post(

        "/reports",

        json={

            "type":

                "",

        },

    )



    assert response["data"]["type"] == ""



# ============================================================
# Report Retrieval Tests
# ============================================================


@pytest.mark.asyncio
async def test_get_report_details(
    api_client,
):
    """
    Retrieve specific report.
    """

    response = await api_client.get(

        "/reports/report_test001"

    )



    assert response["path"] == "/reports/report_test001"



# ============================================================
# Security Report Tests
# ============================================================


@pytest.mark.asyncio
async def test_security_report(
    api_client,
):
    """
    Security assessment report.
    """

    response = await api_client.post(

        "/reports/security",

        json={

            "scan_id":

                "scan_test001",

        },

    )



    assert response["path"] == "/reports/security"



# ============================================================
# Compliance Report Tests
# ============================================================


@pytest.mark.asyncio
async def test_compliance_report(
    api_client,
):
    """
    Compliance report generation.
    """

    response = await api_client.post(

        "/reports/compliance",

        json={

            "framework":

                "ISO27001",

        },

    )



    assert response["path"] == "/reports/compliance"



# ============================================================
# PQC Report Tests
# ============================================================


@pytest.mark.asyncio
async def test_pqc_migration_report(
    api_client,
):
    """
    PQC migration report.
    """

    response = await api_client.post(

        "/reports/pqc",

        json={

            "organization":

                "enterprise-test",

        },

    )



    assert response["path"] == "/reports/pqc"



# ============================================================
# Export Tests
# ============================================================


@pytest.mark.asyncio
async def test_export_pdf_report(
    api_client,
):
    """
    PDF report export.
    """

    response = await api_client.post(

        "/reports/report_test001/export",

        json={

            "format":

                "pdf",

        },

    )



    assert response["path"] == "/reports/report_test001/export"



@pytest.mark.asyncio
async def test_export_json_report(
    api_client,
):
    """
    JSON report export.
    """

    response = await api_client.post(

        "/reports/report_test001/export",

        json={

            "format":

                "json",

        },

    )



    assert response["data"]["format"] == "json"



# ============================================================
# Report History Tests
# ============================================================


@pytest.mark.asyncio
async def test_report_history(
    api_client,
):
    """
    Report history endpoint.
    """

    response = await api_client.get(

        "/reports/history"

    )



    assert response["path"] == "/reports/history"



# ============================================================
# Report Delete Tests
# ============================================================


@pytest.mark.asyncio
async def test_delete_report(
    api_client,
):
    """
    Delete report endpoint.
    """

    response = await api_client.delete(

        "/reports/report_test001"

    )



    assert response["path"] == "/reports/report_test001"



# ============================================================
# Access Control Tests
# ============================================================


@pytest.mark.asyncio
async def test_reports_require_authentication(
    api_client,
):
    """
    Reports require authentication.
    """

    response = await api_client.get(

        "/reports"

    )



    assert response["path"] == "/reports"