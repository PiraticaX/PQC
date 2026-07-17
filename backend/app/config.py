"""
QShield Enterprise
==================

Global application configuration.

This module centralizes environment configuration for the application.
It intentionally avoids business logic so it can be safely imported
throughout the project without creating circular dependencies.

Priority:
1. Environment Variables
2. Default Values

Author:
QShield Enterprise
"""

from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------
# Application Information
# ---------------------------------------------------------------------

APP_NAME: str = "QShield Enterprise"

APP_VERSION: str = "2.0.0"

API_PREFIX: str = "/api"

# ---------------------------------------------------------------------
# Base Directories
# ---------------------------------------------------------------------

BASE_DIR: Path = Path(__file__).resolve().parent

PROJECT_ROOT: Path = BASE_DIR.parent.parent

DATA_DIR: Path = PROJECT_ROOT / "data"

REPORT_DIR: Path = DATA_DIR / "reports"

LOG_DIR: Path = DATA_DIR / "logs"

TEMP_DIR: Path = DATA_DIR / "temp"

# Ensure required directories exist.
for directory in (
    DATA_DIR,
    REPORT_DIR,
    LOG_DIR,
    TEMP_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DATA_DIR / 'qshield.db'}",
)

# ---------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------

HOST: str = os.getenv("HOST", "0.0.0.0")

PORT: int = int(os.getenv("PORT", "8000"))

DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

RELOAD: bool = os.getenv("RELOAD", "false").lower() == "true"

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

LOG_LEVEL: str = os.getenv(
    "LOG_LEVEL",
    "INFO",
).upper()

LOG_FILE: Path = LOG_DIR / "qshield.log"

# ---------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------

SECRET_KEY: str = os.getenv(
    "SECRET_KEY",
    "CHANGE_ME_IN_PRODUCTION",
)

ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)

# ---------------------------------------------------------------------
# Scanner Configuration
# ---------------------------------------------------------------------

DEFAULT_TIMEOUT_SECONDS: int = int(
    os.getenv("DEFAULT_TIMEOUT_SECONDS", "15")
)

MAX_REDIRECTS: int = int(
    os.getenv("MAX_REDIRECTS", "10")
)

MAX_CONCURRENT_SCANS: int = int(
    os.getenv("MAX_CONCURRENT_SCANS", "5")
)

USER_AGENT: str = (
    "QShield-Enterprise/2.0 "
    "(Authorized Security Assessment Platform)"
)

# ---------------------------------------------------------------------
# Report Configuration
# ---------------------------------------------------------------------

REPORT_RETENTION_DAYS: int = int(
    os.getenv("REPORT_RETENTION_DAYS", "365")
)

# ---------------------------------------------------------------------
# PostgreSQL (Future)
# ---------------------------------------------------------------------

POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")

POSTGRES_PORT: int = int(
    os.getenv("POSTGRES_PORT", "5432")
)

POSTGRES_DATABASE: str = os.getenv(
    "POSTGRES_DATABASE",
    "qshield",
)

POSTGRES_USER: str = os.getenv(
    "POSTGRES_USER",
    "postgres",
)

POSTGRES_PASSWORD: str = os.getenv(
    "POSTGRES_PASSWORD",
    "postgres",
)

# ---------------------------------------------------------------------
# Redis (Future Background Jobs)
# ---------------------------------------------------------------------

REDIS_URL: str = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0",
)

# ---------------------------------------------------------------------
# OQS
# ---------------------------------------------------------------------

OQS_INSTALL_PATH: str = os.getenv(
    "OQS_INSTALL_PATH",
    "/usr/local",
)

# ---------------------------------------------------------------------
# Feature Flags
# ---------------------------------------------------------------------

ENABLE_PQC: bool = os.getenv(
    "ENABLE_PQC",
    "true",
).lower() == "true"

ENABLE_AI: bool = os.getenv(
    "ENABLE_AI",
    "true",
).lower() == "true"

ENABLE_BACKGROUND_SCANS: bool = os.getenv(
    "ENABLE_BACKGROUND_SCANS",
    "false",
).lower() == "true"

# ---------------------------------------------------------------------
# Compliance
# ---------------------------------------------------------------------

SUPPORTED_FRAMEWORKS: tuple[str, ...] = (
    "OWASP",
    "NIST",
    "NIST-PQC",
    "ISO27001",
    "PCI-DSS",
    "CIS",
)

# ---------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------

DEFAULT_TIMEZONE: str = "UTC"

DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
