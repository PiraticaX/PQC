"""
QShield Enterprise
==================

Global Exception Framework.

Contains:

- Base application exceptions
- Security exceptions
- Authentication exceptions
- Validation exceptions
- Integration exceptions
- Worker exceptions

All modules should raise
these standardized exceptions.

"""

from __future__ import annotations



# ============================================================
# Base Exception
# ============================================================


class QShieldException(
    Exception
):
    """
    Base QShield exception.

    All custom exceptions inherit
    from this class.

    """



    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: dict | None = None,
    ):

        super().__init__(

            message

        )


        self.message = message

        self.code = code

        self.details = details or {}



    def to_dict(
        self,
    ) -> dict:
        """
        Convert exception into API-safe format.
        """

        return {

            "error":

                self.__class__.__name__,


            "message":

                self.message,


            "code":

                self.code,


            "details":

                self.details,

        }



# ============================================================
# Authentication Exceptions
# ============================================================


class AuthenticationError(
    QShieldException
):
    """
    Authentication failure.
    """



class InvalidTokenError(
    AuthenticationError
):
    """
    Invalid or expired token.
    """



class SessionExpiredError(
    AuthenticationError
):
    """
    User session expired.
    """



class InvalidCredentialsError(
    AuthenticationError
):
    """
    Invalid login credentials.
    """



# ============================================================
# Authorization Exceptions
# ============================================================


class AuthorizationError(
    QShieldException
):
    """
    Permission denied.
    """



class PermissionDeniedError(
    AuthorizationError
):
    """
    User lacks required permission.
    """



class RoleAccessError(
    AuthorizationError
):
    """
    Role restriction failure.
    """



# ============================================================
# Validation Exceptions
# ============================================================


class ValidationError(
    QShieldException
):
    """
    Invalid input data.
    """



class InvalidRequestError(
    ValidationError
):
    """
    Malformed API request.
    """



class InvalidSchemaError(
    ValidationError
):
    """
    Schema validation failed.
    """



# ============================================================
# Security Exceptions
# ============================================================


class SecurityError(
    QShieldException
):
    """
    General security failure.
    """



class EncryptionError(
    SecurityError
):
    """
    Encryption/decryption failure.
    """



class KeyManagementError(
    SecurityError
):
    """
    Key lifecycle failure.
    """



class CryptographicError(
    SecurityError
):
    """
    Cryptographic operation failure.
    """



# ============================================================
# Integration Exceptions
# ============================================================


class IntegrationError(
    QShieldException
):
    """
    External integration failure.
    """



class ConnectionError(
    IntegrationError
):
    """
    External service connection failure.
    """



class ProviderUnavailableError(
    IntegrationError
):
    """
    Provider unavailable.
    """



class ExternalAPIError(
    IntegrationError
):
    """
    External API request failure.
    """



# ============================================================
# Database Exceptions
# ============================================================


class DatabaseError(
    QShieldException
):
    """
    Database operation failure.
    """



class RecordNotFoundError(
    DatabaseError
):
    """
    Requested record missing.
    """



class DuplicateRecordError(
    DatabaseError
):
    """
    Duplicate data conflict.
    """



# ============================================================
# Worker Exceptions
# ============================================================


class WorkerError(
    QShieldException
):
    """
    Background worker failure.
    """



class TaskExecutionError(
    WorkerError
):
    """
    Worker task execution failure.
    """



class TaskTimeoutError(
    WorkerError
):
    """
    Worker timeout.
    """



# ============================================================
# Storage Exceptions
# ============================================================


class StorageError(
    QShieldException
):
    """
    Storage operation failure.
    """



class FileNotFoundError(
    StorageError
):
    """
    Stored file missing.
    """



class FileUploadError(
    StorageError
):
    """
    File upload failed.
    """



# ============================================================
# Compliance Exceptions
# ============================================================


class ComplianceError(
    QShieldException
):
    """
    Compliance assessment failure.
    """



class AuditFailureError(
    ComplianceError
):
    """
    Audit validation failed.
    """



# ============================================================
# Quantum Exceptions
# ============================================================


class QuantumError(
    QShieldException
):
    """
    Quantum execution failure.
    """



class QuantumBackendError(
    QuantumError
):
    """
    Quantum provider failure.
    """



class QuantumCircuitError(
    QuantumError
):
    """
    Invalid quantum circuit.
    """



# ============================================================
# Exception Helpers
# ============================================================


def raise_error(
    exception: type[QShieldException],
    message: str,
    code: str | None = None,
    details: dict | None = None,
):
    """
    Raise standardized QShield exception.
    """

    raise exception(

        message,

        code,

        details,

    )