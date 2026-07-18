"""
QShield Enterprise
==================

Core Configuration Management.

Responsibilities:

- Environment configuration
- Application settings
- Database configuration
- Security configuration
- JWT configuration
- Cryptographic settings
- External service configuration
- Feature flags

Uses:

- Pydantic Settings
- Environment variables

"""

from __future__ import annotations


import os


from functools import lru_cache


from typing import Any


from pydantic import Field


from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict



# ============================================================
# Application Settings
# ============================================================


class Settings(
    BaseSettings
):
    """
    Global application configuration.

    Values are loaded from:

    - Environment variables
    - .env file

    """



    # --------------------------------------------------------
    # Application
    # --------------------------------------------------------


    APP_NAME: str = "QShield Enterprise"


    APP_VERSION: str = "1.0.0"


    ENVIRONMENT: str = "development"


    DEBUG: bool = True


    API_PREFIX: str = "/api/v1"



    # --------------------------------------------------------
    # Server
    # --------------------------------------------------------


    HOST: str = "0.0.0.0"


    PORT: int = 8000



    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------


    DATABASE_URL: str = Field(

        default=
            "sqlite+aiosqlite:///./qshield.db"

    )


    DATABASE_POOL_SIZE: int = 20


    DATABASE_MAX_OVERFLOW: int = 40



    # --------------------------------------------------------
    # Redis / Cache
    # --------------------------------------------------------


    REDIS_URL: str = "redis://localhost:6379/0"


    CACHE_ENABLED: bool = True


    CACHE_TIMEOUT: int = 300



    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------


    JWT_SECRET_KEY: str = Field(

        default="CHANGE_THIS_SECRET"

    )


    JWT_ALGORITHM: str = "HS256"


    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30



    # --------------------------------------------------------
    # Password Security
    # --------------------------------------------------------


    PASSWORD_MIN_LENGTH: int = 12


    PASSWORD_HASH_ALGORITHM: str = "bcrypt"



    # --------------------------------------------------------
    # Encryption
    # --------------------------------------------------------


    ENCRYPTION_KEY: str | None = None


    DEFAULT_ENCRYPTION_ALGORITHM: str = "AES-256"


    ENABLE_ENCRYPTION: bool = True



    # --------------------------------------------------------
    # PQC Configuration
    # --------------------------------------------------------


    ENABLE_PQC: bool = True


    PQC_DEFAULT_KEM: str = "CRYSTALS-KYBER"


    PQC_DEFAULT_SIGNATURE: str = "CRYSTALS-DILITHIUM"



    # --------------------------------------------------------
    # API Security
    # --------------------------------------------------------


    CORS_ORIGINS: list[str] = [

        "*"

    ]


    RATE_LIMIT_ENABLED: bool = True


    RATE_LIMIT_REQUESTS: int = 100


    RATE_LIMIT_WINDOW_SECONDS: int = 60



    # --------------------------------------------------------
    # Logging
    # --------------------------------------------------------


    LOG_LEVEL: str = "INFO"


    LOG_FORMAT: str = "json"



    # --------------------------------------------------------
    # Storage
    # --------------------------------------------------------


    STORAGE_TYPE: str = "local"


    STORAGE_PATH: str = "./storage"



    # --------------------------------------------------------
    # External Services
    # --------------------------------------------------------


    AWS_ACCESS_KEY_ID: str | None = None


    AWS_SECRET_ACCESS_KEY: str | None = None


    AWS_BUCKET_NAME: str | None = None


    AWS_REGION: str = "ap-south-1"



    # --------------------------------------------------------
    # Monitoring
    # --------------------------------------------------------


    ENABLE_METRICS: bool = True


    ENABLE_AUDIT_LOGGING: bool = True



    # --------------------------------------------------------
    # Feature Flags
    # --------------------------------------------------------


    ENABLE_BACKGROUND_WORKERS: bool = True


    ENABLE_SCHEDULER: bool = True


    ENABLE_WEBHOOKS: bool = True



    # --------------------------------------------------------
    # Pydantic Configuration
    # --------------------------------------------------------


    model_config = SettingsConfigDict(

        env_file=".env",

        env_file_encoding="utf-8",

        case_sensitive=True,

        extra="ignore",

    )



# ============================================================
# Settings Singleton
# ============================================================


@lru_cache()
def get_settings() -> Settings:
    """
    Return cached application settings.
    """

    return Settings()



settings = get_settings()



# ============================================================
# Environment Helpers
# ============================================================


def is_production() -> bool:
    """
    Check production environment.
    """

    return (

        settings.ENVIRONMENT.lower()

        ==

        "production"

    )



def is_development() -> bool:
    """
    Check development environment.
    """

    return (

        settings.ENVIRONMENT.lower()

        ==

        "development"

    )



def get_environment_info() -> dict[str, Any]:
    """
    Return safe environment metadata.
    """

    return {

        "application":

            settings.APP_NAME,


        "version":

            settings.APP_VERSION,


        "environment":

            settings.ENVIRONMENT,


        "debug":

            settings.DEBUG,


        "pqc_enabled":

            settings.ENABLE_PQC,


        "encryption_enabled":

            settings.ENABLE_ENCRYPTION,

    }