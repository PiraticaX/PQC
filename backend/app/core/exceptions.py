"""
QShield Enterprise
==================

Exception Handling Infrastructure.

Responsibilities:

- Centralized application exceptions
- HTTP error mapping
- Security exception handling
- Database exception handling
- API error formatting
- Global FastAPI exception handlers

"""

from __future__ import annotations


import logging


from typing import Any


from fastapi import FastAPI
from fastapi import Request
from fastapi import status


from fastapi.exceptions import RequestValidationError


from fastapi.responses import JSONResponse


from sqlalchemy.exc import SQLAlchemyError



logger = logging.getLogger(__name__)



# ============================================================
# Base Exceptions
# ============================================================


class QShieldException(
    Exception
):
    """
    Base application exception.

    All internal exceptions inherit
    from this class.
    """

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: dict[str, Any] | None = None,
    ):

        self.message = message

        self.code = code

        self.details = details or {}


        super().__init__(

            message

        )



# ============================================================
# Authentication Exceptions
# ============================================================


class AuthenticationException(
    QShieldException
):
    """
    Authentication failure.
    """

    def __init__(
        self,
        message: str = "Authentication failed.",
    ):

        super().__init__(

            message=message,

            code="AUTHENTICATION_FAILED",

        )



class TokenExpiredException(
    AuthenticationException
):
    """
    Expired token.
    """

    def __init__(self):

        super().__init__(

            "Token expired."

        )


        self.code = "TOKEN_EXPIRED"



class InvalidTokenException(
    AuthenticationException
):
    """
    Invalid token.
    """

    def __init__(self):

        super().__init__(

            "Invalid token."

        )


        self.code = "INVALID_TOKEN"



# ============================================================
# Authorization Exceptions
# ============================================================


class PermissionDeniedException(
    QShieldException
):
    """
    User lacks permission.
    """

    def __init__(
        self,
        resource: str | None = None,
    ):

        super().__init__(

            message="Permission denied.",

            code="PERMISSION_DENIED",

            details={

                "resource":

                    resource

            }

        )



class AccessDeniedException(
    QShieldException
):
    """
    Access forbidden.
    """

    def __init__(self):

        super().__init__(

            message="Access denied.",

            code="ACCESS_DENIED",

        )



# ============================================================
# Resource Exceptions
# ============================================================


class ResourceNotFoundException(
    QShieldException
):
    """
    Resource missing.
    """

    def __init__(
        self,
        resource: str,
    ):

        super().__init__(

            message=f"{resource} not found.",

            code="RESOURCE_NOT_FOUND",

        )



class ResourceAlreadyExistsException(
    QShieldException
):
    """
    Duplicate resource.
    """

    def __init__(
        self,
        resource: str,
    ):

        super().__init__(

            message=f"{resource} already exists.",

            code="RESOURCE_EXISTS",

        )



# ============================================================
# Validation Exceptions
# ============================================================


class ValidationException(
    QShieldException
):
    """
    Business validation failure.
    """

    def __init__(
        self,
        message: str,
        fields: dict[str, Any] | None = None,
    ):

        super().__init__(

            message=message,

            code="VALIDATION_ERROR",

            details={

                "fields":

                    fields or {}

            }

        )



# ============================================================
# Security Exceptions
# ============================================================


class EncryptionException(
    QShieldException
):
    """
    Cryptography failure.
    """

    def __init__(
        self,
        message: str = "Encryption operation failed.",
    ):

        super().__init__(

            message=message,

            code="ENCRYPTION_ERROR",

        )



class KeyManagementException(
    QShieldException
):
    """
    Key lifecycle failure.
    """

    def __init__(
        self,
        message: str = "Key management operation failed.",
    ):

        super().__init__(

            message=message,

            code="KEY_MANAGEMENT_ERROR",

        )



class PQCException(
    QShieldException
):
    """
    Post quantum cryptography failure.
    """

    def __init__(
        self,
        message: str = "PQC operation failed.",
    ):

        super().__init__(

            message=message,

            code="PQC_ERROR",

        )



# ============================================================
# Database Exceptions
# ============================================================


class DatabaseException(
    QShieldException
):
    """
    Database operation failure.
    """

    def __init__(
        self,
        message: str = "Database operation failed.",
    ):

        super().__init__(

            message=message,

            code="DATABASE_ERROR",

        )



# ============================================================
# Exception Response Builder
# ============================================================


def exception_response(
    exc: QShieldException,
):
    """
    Convert exception to API response.
    """

    return JSONResponse(

        status_code=status.HTTP_400_BAD_REQUEST,

        content={

            "success":

                False,


            "error":

                {

                    "code":

                        exc.code,


                    "message":

                        exc.message,


                    "details":

                        exc.details,

                }

        }

    )



# ============================================================
# FastAPI Exception Handlers
# ============================================================


async def qshield_exception_handler(
    request: Request,
    exc: QShieldException,
):
    """
    Handle internal application exceptions.
    """

    logger.error(

        exc.message,

        extra={

            "path":

                request.url.path,


            "error_code":

                exc.code,

        },

    )


    return exception_response(

        exc

    )



async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """
    Handle request validation errors.
    """

    return JSONResponse(

        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,

        content={

            "success":

                False,


            "error":

                {

                    "code":

                        "VALIDATION_ERROR",


                    "message":

                        "Invalid request data.",


                    "details":

                        exc.errors(),

                }

        }

    )



async def database_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
):
    """
    Handle database failures.
    """

    logger.exception(

        "Database error",

    )


    return JSONResponse(

        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

        content={

            "success":

                False,


            "error":

                {

                    "code":

                        "DATABASE_ERROR",


                    "message":

                        "Database operation failed.",

                }

        }

    )



# ============================================================
# Registration
# ============================================================


def register_exception_handlers(
    app: FastAPI,
):
    """
    Register all global exception handlers.
    """

    app.add_exception_handler(

        QShieldException,

        qshield_exception_handler,

    )


    app.add_exception_handler(

        RequestValidationError,

        validation_exception_handler,

    )


    app.add_exception_handler(

        SQLAlchemyError,

        database_exception_handler,

    )