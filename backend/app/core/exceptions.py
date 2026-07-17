"""
QShield Enterprise
==================

Centralized exception hierarchy.

Why this exists
---------------
Using custom exceptions provides:

- Consistent error handling
- Better API responses
- Cleaner service code
- Easier debugging
- Future integration with monitoring systems

Services should raise these exceptions instead of generic Exception.
FastAPI exception handlers can later convert these into structured JSON
responses.

Example:

    raise AssetNotFoundError(asset_id)

instead of

    raise Exception("Asset not found")
"""

from __future__ import annotations

from typing import Any


class QShieldException(Exception):
    """
    Base exception for the entire application.

    Every custom exception should inherit from this class.
    """

    def __init__(
        self,
        message: str,
        *,
        code: str = "QSHIELD_ERROR",
        details: Any | None = None,
    ) -> None:
        super().__init__(message)

        self.message = message
        self.code = code
        self.details = details

    def to_dict(self) -> dict:
        """
        Serialize exception into a JSON-friendly structure.
        """

        return {
            "success": False,
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            },
        }


# ============================================================================
# Asset Exceptions
# ============================================================================


class AssetError(QShieldException):
    """Base asset exception."""


class AssetNotFoundError(AssetError):
    def __init__(self, asset_id: int):
        super().__init__(
            message=f"Asset '{asset_id}' was not found.",
            code="ASSET_NOT_FOUND",
            details={"asset_id": asset_id},
        )


class AssetAlreadyExistsError(AssetError):
    def __init__(self, asset_name: str):
        super().__init__(
            message=f"Asset '{asset_name}' already exists.",
            code="ASSET_ALREADY_EXISTS",
            details={"asset": asset_name},
        )


class InvalidAssetError(AssetError):
    def __init__(self, reason: str):
        super().__init__(
            message=f"Invalid asset: {reason}",
            code="INVALID_ASSET",
        )


# ============================================================================
# Scan Exceptions
# ============================================================================


class ScanError(QShieldException):
    """Base scan exception."""


class ScanAlreadyRunningError(ScanError):
    def __init__(self, asset_id: int):
        super().__init__(
            message="A scan is already running for this asset.",
            code="SCAN_ALREADY_RUNNING",
            details={"asset_id": asset_id},
        )


class ScanFailedError(ScanError):
    def __init__(self, reason: str):
        super().__init__(
            message=f"Scan failed: {reason}",
            code="SCAN_FAILED",
        )


class ScanTimeoutError(ScanError):
    def __init__(self):
        super().__init__(
            message="Scan exceeded the configured timeout.",
            code="SCAN_TIMEOUT",
        )


# ============================================================================
# TLS
# ============================================================================


class TLSException(QShieldException):
    """Base TLS exception."""


class TLSConnectionError(TLSException):
    def __init__(self, host: str):
        super().__init__(
            message=f"Unable to establish TLS connection to '{host}'.",
            code="TLS_CONNECTION_FAILED",
            details={"host": host},
        )


class CertificateValidationError(TLSException):
    def __init__(self, reason: str):
        super().__init__(
            message=f"Certificate validation failed: {reason}",
            code="CERTIFICATE_VALIDATION_FAILED",
        )


# ============================================================================
# DNS
# ============================================================================


class DNSException(QShieldException):
    """Base DNS exception."""


class DNSLookupError(DNSException):
    def __init__(self, domain: str):
        super().__init__(
            message=f"DNS lookup failed for '{domain}'.",
            code="DNS_LOOKUP_FAILED",
            details={"domain": domain},
        )


# ============================================================================
# PQC
# ============================================================================


class PQCException(QShieldException):
    """Base PQC exception."""


class OQSUnavailableError(PQCException):
    def __init__(self):
        super().__init__(
            message="liboqs runtime is unavailable.",
            code="OQS_RUNTIME_UNAVAILABLE",
        )


class UnsupportedAlgorithmError(PQCException):
    def __init__(self, algorithm: str):
        super().__init__(
            message=f"Unsupported algorithm '{algorithm}'.",
            code="UNSUPPORTED_ALGORITHM",
            details={"algorithm": algorithm},
        )


# ============================================================================
# Reporting
# ============================================================================


class ReportException(QShieldException):
    """Base report exception."""


class ReportGenerationError(ReportException):
    def __init__(self, reason: str):
        super().__init__(
            message=f"Report generation failed: {reason}",
            code="REPORT_GENERATION_FAILED",
        )


# ============================================================================
# Authentication
# ============================================================================


class AuthenticationError(QShieldException):
    def __init__(self):
        super().__init__(
            message="Authentication failed.",
            code="AUTHENTICATION_FAILED",
        )


class AuthorizationError(QShieldException):
    def __init__(self):
        super().__init__(
            message="Permission denied.",
            code="PERMISSION_DENIED",
        )


# ============================================================================
# Validation
# ============================================================================


class ValidationException(QShieldException):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
        )


# ============================================================================
# Database
# ============================================================================


class DatabaseException(QShieldException):
    """Base database exception."""


class DatabaseConnectionError(DatabaseException):
    def __init__(self):
        super().__init__(
            message="Unable to connect to the database.",
            code="DATABASE_CONNECTION_FAILED",
        )


class DatabaseIntegrityError(DatabaseException):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="DATABASE_INTEGRITY_ERROR",
        )


# ============================================================================
# Internal Errors
# ============================================================================


class InternalServerException(QShieldException):
    def __init__(self):
        super().__init__(
            message="An unexpected internal error occurred.",
            code="INTERNAL_SERVER_ERROR",
        )