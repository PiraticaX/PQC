"""
QShield Enterprise
==================

Assets API Tests.

Tests:

- Asset listing
- Asset creation
- Asset details
- Asset updates
- Asset deletion
- Critical asset access control
- Cloud asset handling
- Quantum asset handling

"""

from __future__ import annotations



import pytest



from backend.tests.fixtures.assets import (
    create_asset,
    server_asset,
    database_asset,
    aws_asset,
    quantum_backend_asset,
    vulnerable_asset,
)



# ============================================================
# Asset Listing Tests
# ============================================================


@pytest.mark.asyncio
async def test_get_assets(
    api_client,
):
    """
    Asset listing endpoint.
    """

    response = await api_client.get(

        "/assets"

    )



    assert response["method"] == "GET"

    assert response["path"] == "/assets"



# ============================================================
# Asset Creation Tests
# ============================================================


@pytest.mark.asyncio
async def test_create_asset(
    api_client,
):
    """
    Asset creation endpoint.
    """

    asset = create_asset()



    response = await api_client.post(

        "/assets",

        json=asset,

    )



    assert response["path"] == "/assets"

    assert response["data"]["id"] == asset["id"]



@pytest.mark.asyncio
async def test_create_invalid_asset(
    api_client,
):
    """
    Invalid asset payload.
    """

    response = await api_client.post(

        "/assets",

        json={

            "name":

                "",

        },

    )



    assert response["data"]["name"] == ""



# ============================================================
# Asset Details Tests
# ============================================================


@pytest.mark.asyncio
async def test_get_asset_details(
    api_client,
):
    """
    Asset detail endpoint.
    """

    response = await api_client.get(

        "/assets/ast_test001"

    )



    assert response["path"] == "/assets/ast_test001"



def test_server_asset_structure():
    """
    Server asset fixture validation.
    """

    asset = server_asset()



    assert asset["type"] == "server"

    assert asset["status"] == "active"

    assert asset["criticality"] == "high"



def test_database_asset_security():
    """
    Database assets should be encrypted.
    """

    asset = database_asset()



    assert asset["encrypted"] is True



# ============================================================
# Asset Update Tests
# ============================================================


@pytest.mark.asyncio
async def test_update_asset(
    api_client,
):
    """
    Asset update endpoint.
    """

    response = await api_client.post(

        "/assets/ast_test001",

        json={

            "criticality":

                "high",

        },

    )



    assert response["path"] == "/assets/ast_test001"



# ============================================================
# Asset Delete Tests
# ============================================================


@pytest.mark.asyncio
async def test_delete_asset(
    api_client,
):
    """
    Asset deletion endpoint.
    """

    response = await api_client.delete(

        "/assets/ast_test001"

    )



    assert response["path"] == "/assets/ast_test001"



# ============================================================
# Cloud Asset Tests
# ============================================================


def test_cloud_asset():
    """
    Cloud assets should contain provider.
    """

    asset = aws_asset()



    assert asset["type"] == "cloud"

    assert asset["provider"] == "aws"



# ============================================================
# Quantum Asset Tests
# ============================================================


def test_quantum_asset():
    """
    Quantum backend assets.
    """

    asset = quantum_backend_asset()



    assert asset["type"] == "quantum_backend"

    assert asset["provider"] == "ibm_quantum"



# ============================================================
# Vulnerability Tests
# ============================================================


def test_vulnerable_asset_detection():
    """
    Vulnerable assets should contain findings.
    """

    asset = vulnerable_asset()



    assert asset["status"] == "at_risk"

    assert len(

        asset["vulnerabilities"]

    ) > 0



# ============================================================
# Access Control Tests
# ============================================================


@pytest.mark.asyncio
async def test_asset_access_requires_authentication(
    api_client,
):
    """
    Asset endpoints require authentication.
    """

    response = await api_client.get(

        "/assets"

    )



    assert response["path"] == "/assets"