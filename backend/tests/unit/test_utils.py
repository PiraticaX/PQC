"""
QShield Enterprise
==================

Utility Unit Tests.

Tests:

- File utilities
- Retry utilities
- Pagination
- Response helpers
- Crypto helpers
- Date utilities
- JSON utilities
- Decorators

"""

from __future__ import annotations



import asyncio


from datetime import datetime
from datetime import timezone



import pytest



from backend.utils.file_utils import (
    ensure_directory,
    write_file,
    read_file,
    file_exists,
    format_file_size,
)



from backend.utils.crypto import (
    generate_random_token,
    generate_hmac,
    verify_hmac,
)



from backend.utils.pagination import (
    PaginationParams,
    paginate,
)



from backend.utils.response import (
    success_response,
    error_response,
)



from backend.utils.datetime_utils import (
    utc_now,
    utc_isoformat,
)



from backend.utils.json_utils import (
    serialize_json,
    deserialize_json,
)



# ============================================================
# File Utility Tests
# ============================================================


def test_directory_creation(
    tmp_path,
):
    """
    Directory should be created.
    """

    directory = tmp_path / "security"



    result = ensure_directory(

        directory

    )



    assert result.exists()



def test_file_write_and_read(
    tmp_path,
):
    """
    Files should write/read correctly.
    """

    file = tmp_path / "test.txt"



    write_file(

        file,

        "QShield",

    )



    assert file_exists(

        file

    )



    content = read_file(

        file

    )



    assert content == "QShield"



def test_file_size_formatting():
    """
    File sizes should format.
    """

    result = format_file_size(

        1024

    )



    assert "KB" in result



# ============================================================
# Crypto Utility Tests
# ============================================================


def test_random_token_generation():
    """
    Tokens should generate.
    """

    token = generate_random_token()



    assert token

    assert isinstance(

        token,

        str,

    )



def test_hmac_generation_and_verification():
    """
    HMAC should verify.
    """

    payload = "security-event"

    secret = "secret"



    signature = generate_hmac(

        payload,

        secret,

    )



    assert verify_hmac(

        payload,

        signature,

        secret,

    )



# ============================================================
# Pagination Tests
# ============================================================


def test_pagination_parameters():
    """
    Pagination offset calculation.
    """

    params = PaginationParams(

        page=2,

        size=10,

    )



    assert params.offset == 10

    assert params.limit == 10



def test_list_pagination():
    """
    Lists should paginate.
    """

    result = paginate(

        [

            1,

            2,

            3,

            4,

            5,

        ],

        page=1,

        size=2,

    )



    assert result.items == [

        1,

        2,

    ]



    assert result.metadata.pages == 3



# ============================================================
# Response Tests
# ============================================================


def test_success_response():
    """
    Success responses should format.
    """

    response = success_response(

        {

            "id":

                "001"

        }

    )



    assert response["status"] == "success"

    assert response["data"]["id"] == "001"



def test_error_response():
    """
    Error responses should format.
    """

    response = error_response(

        "Failed",

        code="ERR001",

    )



    assert response["status"] == "error"

    assert response["error"]["code"] == "ERR001"



# ============================================================
# Date Utility Tests
# ============================================================


def test_utc_datetime():
    """
    UTC time should generate.
    """

    result = utc_now()



    assert isinstance(

        result,

        datetime,

    )



    assert result.tzinfo == timezone.utc



def test_utc_iso_format():
    """
    ISO timestamps should generate.
    """

    result = utc_isoformat()



    assert isinstance(

        result,

        str,

    )



    assert "T" in result



# ============================================================
# JSON Utility Tests
# ============================================================


def test_json_serialization():
    """
    Objects should serialize.
    """

    payload = {

        "name":

            "QShield",

        "active":

            True,

    }



    result = serialize_json(

        payload

    )



    assert isinstance(

        result,

        str,

    )



def test_json_deserialization():
    """
    JSON should deserialize.
    """

    payload = '{"system":"QShield"}'



    result = deserialize_json(

        payload

    )



    assert result["system"] == "QShield"