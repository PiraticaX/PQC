"""
QShield Enterprise
==================

Health API

System Health Monitoring Endpoints.

Responsibilities:

- Application health checks
- Service availability checks
- Dependency monitoring
- Readiness verification
- Liveness verification

Used by:

- Kubernetes probes
- Load balancers
- Monitoring systems
- DevOps pipelines

"""

from __future__ import annotations


import logging


from datetime import datetime


from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.database import get_db


from app.services.auth_service import AuthService
from app.services.permission_service import PermissionService
from app.services.storage_service import StorageService
from app.services.queue_service import QueueService


logger = logging.getLogger(__name__)



# ============================================================
# Router
# ============================================================


router = APIRouter(

    prefix="/health",

)



# ============================================================
# Utilities
# ============================================================


def timestamp() -> str:
    """
    UTC timestamp.
    """

    return (
        datetime.utcnow()
        .isoformat()
    )



# ============================================================
# Basic Health
# ============================================================


@router.get(
    "",
    status_code=status.HTTP_200_OK,
)
async def health_check():
    """
    Basic application health.

    Used for:

    - Load balancers
    - Container probes

    """

    return {

        "service":

            "qshield_backend",


        "status":

            "healthy",


        "timestamp":

            timestamp(),

    }



# ============================================================
# Liveness Probe
# ============================================================


@router.get(
    "/live",
)
async def liveness_check():
    """
    Liveness endpoint.

    Indicates:

    Application process is running.

    """

    return {

        "alive":

            True,


        "timestamp":

            timestamp(),

    }



# ============================================================
# Readiness Probe
# ============================================================


@router.get(
    "/ready",
)
async def readiness_check(
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Readiness endpoint.

    Checks:

    - Database connectivity
    - Application readiness

    """

    try:

        await db.execute(
            text("SELECT 1")
        )


        return {

            "ready":

                True,


            "database":

                "connected",


            "timestamp":

                timestamp(),

        }


    except Exception as exc:

        logger.exception(
            "Readiness check failed."
        )


        return {

            "ready":

                False,


            "database":

                "unavailable",


            "error":

                str(exc),


            "timestamp":

                timestamp(),

        }



# ============================================================
# Service Health
# ============================================================


@router.get(
    "/services",
)
async def service_health(
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Check internal service health.

    """

    services = {}



    try:

        services["authentication"] = (
            await AuthService(
                db
            )
            .health_check()
        )


    except Exception as exc:

        services["authentication"] = {

            "status":

                "unhealthy",

            "error":

                str(exc),

        }



    try:

        services["authorization"] = (
            await PermissionService(
                db
            )
            .health_check()
        )


    except Exception as exc:

        services["authorization"] = {

            "status":

                "unhealthy",

            "error":

                str(exc),

        }



    try:

        services["storage"] = (
            await StorageService(
                db
            )
            .health_check()
        )


    except Exception as exc:

        services["storage"] = {

            "status":

                "unhealthy",

            "error":

                str(exc),

        }



    try:

        services["queue"] = (
            await QueueService(
                db
            )
            .health_check()
        )


    except Exception as exc:

        services["queue"] = {

            "status":

                "unhealthy",

            "error":

                str(exc),

        }



    return {

        "system":

            "QShield Enterprise",


        "services":

            services,


        "timestamp":

            timestamp(),

    }



# ============================================================
# Detailed Status
# ============================================================


@router.get(
    "/status",
)
async def detailed_status():
    """
    Detailed platform status.

    """

    return {

        "application":

            {

                "name":

                    "QShield Enterprise",


                "version":

                    "1.0.0",


                "environment":

                    "production",

            },


        "components":

            {

                "api":

                    "operational",


                "database":

                    "operational",


                "security":

                    "operational",


                "event_bus":

                    "operational",

            },


        "timestamp":

            timestamp(),

    }