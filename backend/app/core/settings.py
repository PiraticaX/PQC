"""
QShield Enterprise
==================

Application settings loader.

This module exposes a single immutable Settings object that
contains validated runtime configuration.

All modules should import:

    from app.core.settings import settings

instead of reading environment variables directly.

This keeps configuration centralized, predictable, and testable.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    API_PREFIX,
    APP_NAME,
    APP_VERSION,
    DATA_DIR,
    DATABASE_URL,
    DATE_FORMAT,
    DEBUG,
    DEFAULT_TIMEOUT_SECONDS,
    DEFAULT_TIMEZONE,
    ENABLE_AI,
    ENABLE_BACKGROUND_SCANS,
    ENABLE_PQC,
    HOST,
    LOG_FILE,
    LOG_LEVEL,
    MAX_CONCURRENT_SCANS,
    MAX_REDIRECTS,
    OQS_INSTALL_PATH,
    PORT,
    PROJECT_ROOT,
    REDIS_URL,
    REPORT_DIR,
    REPORT_RETENTION_DAYS,
    RELOAD,
    SECRET_KEY,
    SUPPORTED_FRAMEWORKS,
    TEMP_DIR,
    USER_AGENT,
)


class Settings(BaseSettings):
    """
    Central runtime settings.

    Values are loaded from:

    1. Environment Variables
    2. .env file (if present)
    3. Defaults from app.config
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    app_name: str = APP_NAME
    app_version: str = APP_VERSION
    api_prefix: str = API_PREFIX

    debug: bool = DEBUG
    reload: bool = RELOAD

    host: str = HOST
    port: int = PORT

    # ------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------

    secret_key: str = Field(default=SECRET_KEY)
    access_token_expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    database_url: str = DATABASE_URL

    # ------------------------------------------------------------------
    # Redis
    # ------------------------------------------------------------------

    redis_url: str = REDIS_URL

    # ------------------------------------------------------------------
    # Scanner
    # ------------------------------------------------------------------

    default_timeout: int = DEFAULT_TIMEOUT_SECONDS
    max_redirects: int = MAX_REDIRECTS
    max_concurrent_scans: int = MAX_CONCURRENT_SCANS

    user_agent: str = USER_AGENT

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    log_level: str = LOG_LEVEL
    log_file: Path = LOG_FILE

    # ------------------------------------------------------------------
    # Directories
    # ------------------------------------------------------------------

    project_root: Path = PROJECT_ROOT
    data_dir: Path = DATA_DIR
    report_dir: Path = REPORT_DIR
    temp_dir: Path = TEMP_DIR

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------

    report_retention_days: int = REPORT_RETENTION_DAYS

    # ------------------------------------------------------------------
    # OQS
    # ------------------------------------------------------------------

    oqs_install_path: str = OQS_INSTALL_PATH

    # ------------------------------------------------------------------
    # Features
    # ------------------------------------------------------------------

    enable_pqc: bool = ENABLE_PQC
    enable_ai: bool = ENABLE_AI
    enable_background_scans: bool = ENABLE_BACKGROUND_SCANS

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    timezone: str = DEFAULT_TIMEZONE
    date_format: str = DATE_FORMAT

    supported_frameworks: tuple[str, ...] = SUPPORTED_FRAMEWORKS


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Returns a singleton Settings instance.

    Using an LRU cache ensures that configuration is loaded only once
    during the application lifetime.
    """
    return Settings()


settings = get_settings()