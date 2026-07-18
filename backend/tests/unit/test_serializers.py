"""
QShield Enterprise
==================

Serializer Unit Tests.

Tests:

- Object serialization
- Datetime conversion
- UUID conversion
- Sensitive field filtering
- API response serialization
- Event serialization
- Database model conversion

"""

from __future__ import annotations



from datetime import datetime
from datetime import timezone



from uuid import uuid4



from decimal import Decimal



import pytest



from backend.utils.serializers import (
    serialize_value,
    serialize_object,
    remove_sensitive_fields,
    mask_sensitive_fields,
    serialize_response,
    serialize_list,
    model_to_dict,
    serialize_event,
)



# ============================================================
# Basic Serialization Tests
# ============================================================


def test_datetime_serialization():
    """
    Datetime should convert to ISO format.
    """

    now = datetime.now(

        timezone.utc

    )



    result = serialize_value(

        now

    )



    assert isinstance(

        result,

        str,

    )



    assert "T" in result



def test_uuid_serialization():
    """
    UUID should convert to string.
    """

    identifier = uuid4()



    result = serialize_value(

        identifier

    )



    assert result == str(

        identifier

    )



def test_decimal_serialization():
    """
    Decimal should convert to float.
    """

    result = serialize_value(

        Decimal(

            "10.50"

        )

    )



    assert result == 10.5



# ============================================================
# Collection Serialization Tests
# ============================================================


def test_list_serialization():
    """
    Lists should serialize recursively.
    """

    result = serialize_value(

        [

            uuid4(),

            Decimal(

                "5.25"

            ),

        ]

    )



    assert isinstance(

        result[0],

        str,

    )



    assert result[1] == 5.25



def test_dictionary_serialization():
    """
    Dictionary values should serialize.
    """

    result = serialize_value(

        {

            "amount":

                Decimal(

                    "20.5"

                )

        }

    )



    assert result["amount"] == 20.5



# ============================================================
# Object Serialization Tests
# ============================================================


def test_object_serialization():
    """
    Objects should convert into dictionaries.
    """

    class User:

        def __init__(self):

            self.name = "admin"

            self.role = "security"



    result = serialize_object(

        User()

    )



    assert result["name"] == "admin"

    assert result["role"] == "security"



def test_object_excluded_fields():
    """
    Excluded fields should not serialize.
    """

    data = {

        "username":

            "admin",


        "password":

            "secret",

    }



    result = serialize_object(

        data,

        exclude={

            "password"

        },

    )



    assert "password" not in result



# ============================================================
# Sensitive Data Tests
# ============================================================


def test_remove_sensitive_fields():
    """
    Sensitive values should be removed.
    """

    payload = {

        "username":

            "admin",


        "password":

            "secret",

    }



    result = remove_sensitive_fields(

        payload

    )



    assert "password" not in result

    assert result["username"] == "admin"



def test_mask_sensitive_fields():
    """
    Sensitive values should be masked.
    """

    payload = {

        "api_key":

            "qsk_secret_key",

        "name":

            "QShield",

    }



    result = mask_sensitive_fields(

        payload

    )



    assert result["api_key"] == "********"

    assert result["name"] == "QShield"



# ============================================================
# API Response Tests
# ============================================================


def test_response_serialization():
    """
    API responses should wrap data.
    """

    result = serialize_response(

        {

            "status":

                "active"

        }

    )



    assert "data" in result



def test_list_response_serialization():
    """
    Lists should serialize.
    """

    result = serialize_list(

        [

            {

                "id":

                    1

            },

            {

                "id":

                    2

            },

        ]

    )



    assert len(result) == 2



# ============================================================
# Database Model Tests
# ============================================================


def test_model_to_dict():
    """
    Database-like objects should convert.
    """

    class MockModel:

        __table__ = type(

            "Table",

            (),

            {

                "columns":

                    [

                        type(

                            "Column",

                            (),

                            {

                                "name":

                                    "id"

                            },

                        )()

                    ]

            },

        )



        id = "001"



    result = model_to_dict(

        MockModel()

    )



    assert result["id"] == "001"



# ============================================================
# Event Serialization Tests
# ============================================================


def test_event_serialization():
    """
    Events should contain metadata.
    """

    result = serialize_event(

        "security.alert",

        {

            "severity":

                "high"

        },

    )



    assert "event_id" in result

    assert "timestamp" in result

    assert result["event_type"] == "security.alert"