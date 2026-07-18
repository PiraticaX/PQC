"""
QShield Enterprise
==================

Asset Test Fixtures.

Provides:

- Enterprise asset data
- Cloud assets
- Server assets
- Application assets
- Quantum resources
- Vulnerable asset scenarios

Used across:

- Asset API tests
- Security scan tests
- Risk analysis tests
- Compliance tests

"""

from __future__ import annotations



from typing import Any



# ============================================================
# Asset Factory
# ============================================================


def create_asset(
    asset_id: str = "ast_test001",
    name: str = "Test Server",
    asset_type: str = "server",
    criticality: str = "medium",
) -> dict[str, Any]:
    """
    Create generic asset.

    """

    return {

        "id":

            asset_id,


        "name":

            name,


        "type":

            asset_type,


        "criticality":

            criticality,


        "status":

            "active",


        "owner":

            "security-team",


        "environment":

            "production",


        "tags":

            [

                "qshield",

                "test",

            ],

    }



# ============================================================
# Infrastructure Assets
# ============================================================


def server_asset() -> dict[str, Any]:
    """
    Production server asset.

    """

    return {

        "id":

            "ast_server001",


        "name":

            "Production API Server",


        "type":

            "server",


        "criticality":

            "high",


        "ip_address":

            "10.0.1.10",


        "operating_system":

            "Linux",


        "environment":

            "production",


        "status":

            "active",

    }



def database_asset() -> dict[str, Any]:
    """
    Database asset.

    """

    return {

        "id":

            "ast_database001",


        "name":

            "Security Database",


        "type":

            "database",


        "criticality":

            "critical",


        "technology":

            "PostgreSQL",


        "encrypted":

            True,


        "environment":

            "production",

    }



# ============================================================
# Application Assets
# ============================================================


def application_asset() -> dict[str, Any]:
    """
    Application service asset.

    """

    return {

        "id":

            "ast_app001",


        "name":

            "QShield Portal",


        "type":

            "application",


        "criticality":

            "high",


        "version":

            "1.0.0",


        "authentication":

            "oauth2",


        "status":

            "active",

    }



# ============================================================
# Cloud Assets
# ============================================================


def aws_asset() -> dict[str, Any]:
    """
    AWS cloud asset.

    """

    return {

        "id":

            "ast_cloud001",


        "name":

            "AWS Production Account",


        "type":

            "cloud",


        "provider":

            "aws",


        "region":

            "us-east-1",


        "criticality":

            "high",

    }



def azure_asset() -> dict[str, Any]:
    """
    Azure cloud asset.

    """

    return {

        "id":

            "ast_cloud002",


        "name":

            "Azure Enterprise Tenant",


        "type":

            "cloud",


        "provider":

            "azure",


        "criticality":

            "high",

    }



# ============================================================
# Quantum Assets
# ============================================================


def quantum_backend_asset() -> dict[str, Any]:
    """
    Quantum computing resource.

    """

    return {

        "id":

            "ast_quantum001",


        "name":

            "IBM Quantum Backend",


        "type":

            "quantum_backend",


        "provider":

            "ibm_quantum",


        "status":

            "available",


        "criticality":

            "medium",

    }



# ============================================================
# Vulnerable Assets
# ============================================================


def vulnerable_asset() -> dict[str, Any]:
    """
    Asset containing vulnerabilities.

    """

    return {

        "id":

            "ast_vulnerable001",


        "name":

            "Legacy Application Server",


        "type":

            "server",


        "criticality":

            "critical",


        "vulnerabilities":

            [

                {

                    "id":

                        "CVE-2026-0001",


                    "severity":

                        "critical",

                }

            ],


        "status":

            "at_risk",

    }



# ============================================================
# Asset Collections
# ============================================================


def asset_collection() -> list[dict[str, Any]]:
    """
    Collection of test assets.

    """

    return [

        server_asset(),

        database_asset(),

        application_asset(),

        aws_asset(),

        azure_asset(),

        quantum_backend_asset(),

    ]