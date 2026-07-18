"""
QShield Enterprise
==================

Logging Infrastructure.

Responsibilities:

- Application logging configuration
- Structured logging
- Security event logging
- Audit compatible logs
- Request correlation support
- Production log formatting

"""

from __future__ import annotations


import json


import logging


import sys


from datetime import datetime, timezone


from typing import Any



from app.core.config import settings



# ============================================================
# Custom JSON Formatter
# ============================================================


class JSONFormatter(
    logging.Formatter
):
    """
    JSON structured log formatter.

    Designed for:

    - SIEM systems
    - Log aggregation
    - Security monitoring
    """

    def format(
        self,
        record: logging.LogRecord
    ) -> str:

        payload = {

            "timestamp":

                datetime.now(
                    timezone.utc
                ).isoformat(),


            "level":

                record.levelname,


            "logger":

                record.name,


            "message":

                record.getMessage(),


            "application":

                settings.APP_NAME,


            "environment":

                settings.ENVIRONMENT,

        }



        if hasattr(
            record,
            "request_id"
        ):

            payload["request_id"] = (

                record.request_id

            )



        if hasattr(
            record,
            "user_id"
        ):

            payload["user_id"] = (

                record.user_id

            )



        if record.exc_info:

            payload["exception"] = (

                self.formatException(

                    record.exc_info

                )

            )



        return json.dumps(

            payload

        )



# ============================================================
# Logger Configuration
# ============================================================


def configure_logging():
    """
    Configure application logging.

    Called during application startup.
    """

    root_logger = logging.getLogger()


    root_logger.setLevel(

        settings.LOG_LEVEL.upper()

    )



    root_logger.handlers.clear()



    handler = logging.StreamHandler(

        sys.stdout

    )



    if settings.LOG_FORMAT == "json":

        handler.setFormatter(

            JSONFormatter()

        )


    else:

        handler.setFormatter(

            logging.Formatter(

                "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

            )

        )



    root_logger.addHandler(

        handler

    )



    logging.getLogger(

        "uvicorn"

    ).handlers = root_logger.handlers



    logging.getLogger(

        "sqlalchemy"

    ).setLevel(

        logging.WARNING

    )



    return root_logger



# ============================================================
# Application Logger
# ============================================================


def get_logger(
    name: str
) -> logging.Logger:
    """
    Retrieve application logger.

    Usage:

        logger = get_logger(__name__)

    """

    return logging.getLogger(

        name

    )



# ============================================================
# Security Logging
# ============================================================


class SecurityLogger:
    """
    Security event logger.

    Used for:

    - Authentication events
    - Permission changes
    - Key operations
    - Threat events

    """

    def __init__(
        self
    ):

        self.logger = logging.getLogger(

            "security"

        )



    def log_event(
        self,
        event: str,
        details: dict[str, Any],
    ):
        """
        Record security event.
        """

        self.logger.info(

            event,

            extra={

                "security_event":

                    True,


                "details":

                    details,

            },

        )



    def log_warning(
        self,
        event: str,
        details: dict[str, Any],
    ):
        """
        Record security warning.
        """

        self.logger.warning(

            event,

            extra={

                "security_event":

                    True,


                "details":

                    details,

            },

        )



    def log_failure(
        self,
        event: str,
        details: dict[str, Any],
    ):
        """
        Record security failure.
        """

        self.logger.error(

            event,

            extra={

                "security_event":

                    True,


                "details":

                    details,

            },

        )



# ============================================================
# Audit Logger
# ============================================================


class AuditLogger:
    """
    Enterprise audit logger.

    Tracks:

    - User actions
    - Data access
    - Configuration changes
    """

    def __init__(
        self
    ):

        self.logger = logging.getLogger(

            "audit"

        )



    def record(
        self,
        action: str,
        actor: str | None = None,
        resource: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Record audit event.
        """

        self.logger.info(

            action,

            extra={

                "audit_event":

                    True,


                "actor":

                    actor,


                "resource":

                    resource,


                "metadata":

                    metadata or {},

            },

        )



# ============================================================
# Default Instances
# ============================================================


security_logger = SecurityLogger()


audit_logger = AuditLogger()