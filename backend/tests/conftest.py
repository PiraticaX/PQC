"""
QShield Enterprise
==================

Pytest Configuration.

Provides shared fixtures for:

- API testing
- Database testing
- Authentication testing
- Service testing
- Worker testing
- Integration testing

"""

from __future__ import annotations


import asyncio


import os


import pytest



from typing import AsyncGenerator
from typing import Generator



# ============================================================
# Test Environment
# ============================================================


@pytest.fixture(
    scope="session",
    autouse=True,
)
def setup_test_environment():
    """
    Configure test environment.

    """

    os.environ[

        "ENVIRONMENT"

    ] = "testing"



    os.environ[

        "DATABASE_URL"

    ] = "sqlite:///:memory:"



    yield



# ============================================================
# Async Event Loop
# ============================================================


@pytest.fixture(
    scope="session",
)
def event_loop() -> Generator:
    """
    Create async event loop.

    """

    loop = asyncio.new_event_loop()



    yield loop



    loop.close()



# ============================================================
# Test Database
# ============================================================


@pytest.fixture
async def test_database():
    """
    Temporary database fixture.

    """

    database = {

        "status":

            "connected",


        "engine":

            "sqlite",

    }



    yield database



# ============================================================
# API Client
# ============================================================


@pytest.fixture
async def api_client():
    """
    API client fixture.

    """

    class MockAPIClient:
        """
        Lightweight API client mock.
        """



        async def get(
            self,
            path: str,
        ):

            return {

                "method":

                    "GET",


                "path":

                    path,

            }



        async def post(
            self,
            path: str,
            json: dict | None = None,
        ):

            return {

                "method":

                    "POST",


                "path":

                    path,


                "data":

                    json,

            }



        async def delete(
            self,
            path: str,
        ):

            return {

                "method":

                    "DELETE",


                "path":

                    path,

            }



    client = MockAPIClient()



    yield client



# ============================================================
# Authentication Fixtures
# ============================================================


@pytest.fixture
def test_user():
    """
    Default authenticated user.

    """

    return {

        "id":

            "usr_test001",


        "email":

            "admin@qshield.test",


        "roles":

            [

                "admin"

            ],


        "permissions":

            [

                "read",

                "write",

                "admin",

            ],

    }



@pytest.fixture
def auth_token():
    """
    Mock authentication token.

    """

    return "test.jwt.token"



# ============================================================
# Security Fixtures
# ============================================================


@pytest.fixture
def encryption_key():
    """
    Test encryption key.

    """

    return (

        "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA="

    )



@pytest.fixture
def sample_payload():
    """
    Generic security payload.

    """

    return {

        "event":

            "security_test",


        "severity":

            "high",


        "source":

            "pytest",

    }



# ============================================================
# Storage Fixtures
# ============================================================


@pytest.fixture
def temporary_directory(
    tmp_path,
):
    """
    Temporary file storage.

    """

    return tmp_path



@pytest.fixture
def sample_file(
    tmp_path,
):
    """
    Create sample file.

    """

    file = tmp_path / "sample.txt"



    file.write_text(

        "QShield Test Data"

    )



    return file



# ============================================================
# Integration Mocks
# ============================================================


@pytest.fixture
def mock_quantum_backend():
    """
    Mock quantum provider.

    """

    return {

        "provider":

            "local_simulator",


        "status":

            "available",

    }



@pytest.fixture
def mock_cloud_provider():
    """
    Mock cloud provider.

    """

    return {

        "provider":

            "aws",


        "status":

            "connected",

    }



# ============================================================
# Cleanup
# ============================================================


@pytest.fixture(
    autouse=True,
)
def cleanup_after_test():
    """
    Cleanup hook.

    """

    yield