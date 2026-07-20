"""
QShield Enterprise
==================

Analytics API

Enterprise Security Analytics & Intelligence Endpoints.

Responsibilities:

- Security dashboards
- Risk analytics
- Compliance analytics
- Usage intelligence
- Executive reporting
- Metrics aggregation

Integrates with:

- Analytics Service
- Risk Service
- Compliance Service
- Report Service
- Audit Service

"""

from __future__ import annotations


import logging


from uuid import UUID


from fastapi import APIRouter
from fastapi import Depends


from sqlalchemy.orm import Session


from app.core.database import get_db


from app.services.analytics_service import AnalyticsService



logger = logging.getLogger(__name__)



# ============================================================
# Router
# ============================================================


router = APIRouter(

    prefix="/analytics",

)



# ============================================================
# Security Analytics
# ============================================================


@router.get(
    "/dashboard",
)
async def security_dashboard(
    organization_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Generate security analytics dashboard.

    Includes:

    - Threat posture
    - Security events
    - Risk score
    - Critical findings

    """

    service = AnalyticsService(
        db
    )


    return await service.security_dashboard(

        organization_id

    )



@router.get(
    "/security",
)
async def security_analytics(
    organization_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Security intelligence summary.
    """

    service = AnalyticsService(
        db
    )


    return await service.threat_summary(

        organization_id

    )



@router.get(
    "/risk",
)
async def risk_analysis(
    organization_id: UUID,
    period: str = "daily",
    db: Session = Depends(
        get_db
    ),
):
    """
    Risk trend analytics.
    """

    service = AnalyticsService(
        db
    )


    return await service.risk_trend_analysis(

        organization_id=

            organization_id,

        period=

            period,

    )



# ============================================================
# Compliance Analytics
# ============================================================


@router.get(
    "/compliance",
)
async def compliance_dashboard(
    organization_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Compliance posture analytics.
    """

    service = AnalyticsService(
        db
    )


    return await service.compliance_dashboard(

        organization_id

    )



@router.get(
    "/executive-report",
)
async def executive_report(
    organization_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Executive security report.

    Used by:

    - CISOs
    - Security teams
    - Compliance teams

    """

    service = AnalyticsService(
        db
    )


    return await service.generate_executive_report(

        organization_id

    )



# ============================================================
# User & Platform Analytics
# ============================================================


@router.get(
    "/users/{user_id}",
)
async def user_activity(
    user_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    User behaviour analytics.
    """

    service = AnalyticsService(
        db
    )


    return await service.user_activity_analytics(

        user_id

    )



@router.get(
    "/usage",
)
async def platform_usage(
    db: Session = Depends(
        get_db
    ),
):
    """
    Platform usage metrics.
    """

    service = AnalyticsService(
        db
    )


    return await service.service_usage_metrics()



# ============================================================
# Metrics Engine
# ============================================================


@router.get(
    "/metrics/{metric_type}",
)
async def aggregate_metrics(
    metric_type: str,
    window: str = "daily",
    db: Session = Depends(
        get_db
    ),
):
    """
    Aggregate analytics metrics.
    """

    service = AnalyticsService(
        db
    )


    return await service.aggregate_metrics(

        metric_type=metric_type,

        window=window,

    )



@router.get(
    "/report",
)
async def analytics_report(
    db: Session = Depends(
        get_db
    ),
):
    """
    Generate complete analytics report.
    """

    service = AnalyticsService(
        db
    )


    return await service.generate_analytics_report()



# ============================================================
# Health
# ============================================================


@router.get(
    "/health",
)
async def analytics_health():
    """
    Analytics engine health.
    """

    return {

        "analytics":

            {

                "status":

                    "healthy",


                "engines":

                    [

                        "Security Analytics",

                        "Risk Intelligence",

                        "Compliance Analytics",

                        "Usage Analytics",

                    ],

            }

    }
