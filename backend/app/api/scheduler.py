"""
QShield Enterprise
==================

Scheduler API

Enterprise Task Scheduling Management Endpoints.

Responsibilities:

- Scheduled job creation
- Schedule management
- Manual execution
- Pause/resume scheduling
- Scheduled task monitoring
- Scheduler analytics

Integrates with:

- Scheduler Service
- Queue Service
- Event Service
- Audit Service

"""

from __future__ import annotations


import logging


from typing import Any


from uuid import UUID


from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status


from pydantic import BaseModel


from sqlalchemy.orm import Session


from app.core.database import get_db


from app.services.scheduler_service import SchedulerService



logger = logging.getLogger(__name__)



# ============================================================
# Router
# ============================================================


router = APIRouter(

    prefix="/scheduler",

)



# ============================================================
# Request Schemas
# ============================================================


class ScheduledJobCreateRequest(
    BaseModel,
):
    """
    Scheduled job creation payload.
    """

    name: str

    task_type: str

    schedule_expression: str

    payload: dict[str, Any] | None = None



class ScheduledJobUpdateRequest(
    BaseModel,
):
    """
    Scheduled job update payload.
    """

    name: str | None = None

    schedule_expression: str | None = None

    payload: dict[str, Any] | None = None

    is_active: bool | None = None



class ManualExecutionRequest(
    BaseModel,
):
    """
    Manual execution payload.
    """

    parameters: dict[str, Any] | None = None



# ============================================================
# Scheduler Lifecycle
# ============================================================


@router.post(
    "/jobs",
    status_code=status.HTTP_201_CREATED,
)
async def create_scheduled_job(
    request: ScheduledJobCreateRequest,
    db: Session = Depends(
        get_db
    ),
) -> dict[str, Any]:
    """
    Create scheduled task.
    """

    service = SchedulerService(
        db
    )


    try:

        return await service.create_schedule(

            name=request.name,

            task_type=request.task_type,

            schedule_expression=
                request.schedule_expression,

            payload=request.payload,

        )


    except Exception as exc:

        logger.exception(
            "Scheduled job creation failed."
        )


        raise HTTPException(

            status_code=400,

            detail=str(exc),

        )



@router.get(
    "/jobs",
)
async def list_scheduled_jobs(
    db: Session = Depends(
        get_db
    ),
):
    """
    List scheduled jobs.
    """

    service = SchedulerService(
        db
    )


    return await service.list_schedules()



@router.get(
    "/jobs/{job_id}",
)
async def get_scheduled_job(
    job_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Retrieve scheduled job.
    """

    service = SchedulerService(
        db
    )


    job = await service.get_schedule(

        job_id

    )


    if not job:

        raise HTTPException(

            status_code=404,

            detail="Scheduled job not found.",

        )


    return job



@router.put(
    "/jobs/{job_id}",
)
async def update_scheduled_job(
    job_id: UUID,
    request: ScheduledJobUpdateRequest,
    db: Session = Depends(
        get_db
    ),
):
    """
    Update scheduled task.
    """

    service = SchedulerService(
        db
    )


    return await service.update_schedule(

        schedule_id=job_id,

        updates=request.model_dump(

            exclude_none=True

        ),

    )



@router.delete(
    "/jobs/{job_id}",
)
async def delete_scheduled_job(
    job_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Delete scheduled task.
    """

    service = SchedulerService(
        db
    )


    return await service.delete_schedule(

        job_id

    )



# ============================================================
# Execution Control
# ============================================================


@router.post(
    "/jobs/{job_id}/run",
)
async def execute_job(
    job_id: UUID,
    request: ManualExecutionRequest,
    db: Session = Depends(
        get_db
    ),
):
    """
    Execute scheduled job immediately.
    """

    service = SchedulerService(
        db
    )


    return await service.execute_now(

        schedule_id=job_id,

        parameters=request.parameters,

    )



@router.post(
    "/jobs/{job_id}/pause",
)
async def pause_job(
    job_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Pause scheduler job.
    """

    service = SchedulerService(
        db
    )


    return await service.pause_schedule(

        job_id

    )



@router.post(
    "/jobs/{job_id}/resume",
)
async def resume_job(
    job_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Resume scheduler job.
    """

    service = SchedulerService(
        db
    )


    return await service.resume_schedule(

        job_id

    )



# ============================================================
# Scheduler Monitoring
# ============================================================


@router.get(
    "/jobs/{job_id}/history",
)
async def execution_history(
    job_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Retrieve execution history.
    """

    service = SchedulerService(
        db
    )


    return await service.execution_history(

        job_id

    )



@router.get(
    "/workers",
)
async def scheduler_workers(
    db: Session = Depends(
        get_db
    ),
):
    """
    Scheduler worker status.
    """

    service = SchedulerService(
        db
    )


    return await service.worker_status()



# ============================================================
# Analytics
# ============================================================


@router.get(
    "/statistics",
)
async def scheduler_statistics(
    db: Session = Depends(
        get_db
    ),
):
    """
    Scheduler analytics.
    """

    service = SchedulerService(
        db
    )


    return await service.scheduler_statistics()



@router.get(
    "/health",
)
async def scheduler_health():
    """
    Scheduler health check.
    """

    return {

        "scheduler":

            {

                "status":

                    "healthy",


                "engine":

                    "running",


                "jobs":

                    "enabled",

            }

    }
