"""
QShield Enterprise
==================

Queue API

Enterprise Job Queue Management Endpoints.

Responsibilities:

- Job submission
- Queue monitoring
- Job retrieval
- Job retry
- Job cancellation
- Queue analytics

Integrates with:

- Queue Service
- Event Service
- Scheduler Service
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


from sqlalchemy.ext.asyncio import AsyncSession


from app.core.database import get_db


from app.services.queue_service import QueueService



logger = logging.getLogger(__name__)



# ============================================================
# Router
# ============================================================


router = APIRouter(

    prefix="/queue",

)



# ============================================================
# Request Schemas
# ============================================================


class QueueJobCreateRequest(
    BaseModel,
):
    """
    Queue job creation payload.
    """

    job_type: str

    payload: dict[str, Any]

    priority: str = "normal"

    delay_seconds: int = 0



class QueueRetryRequest(
    BaseModel,
):
    """
    Retry configuration.
    """

    reason: str | None = None



# ============================================================
# Queue Job Management
# ============================================================


@router.post(
    "/jobs",
    status_code=status.HTTP_201_CREATED,
)
async def create_job(
    request: QueueJobCreateRequest,
    db: AsyncSession = Depends(
        get_db
    ),
) -> dict[str, Any]:
    """
    Submit job to queue.
    """

    service = QueueService(
        db
    )


    try:

        return await service.enqueue_job(

            job_type=request.job_type,

            payload=request.payload,

            priority=request.priority,

            delay_seconds=request.delay_seconds,

        )


    except Exception as exc:

        logger.exception(
            "Queue job creation failed."
        )


        raise HTTPException(

            status_code=400,

            detail=str(exc),

        )



@router.get(
    "/jobs",
)
async def list_jobs(
    status: str | None = None,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    List queued jobs.
    """

    service = QueueService(
        db
    )


    return await service.list_jobs(

        status=status

    )



@router.get(
    "/jobs/{job_id}",
)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Retrieve queue job.
    """

    service = QueueService(
        db
    )


    job = await service.get_job(

        job_id

    )


    if not job:

        raise HTTPException(

            status_code=404,

            detail="Job not found.",

        )


    return job



# ============================================================
# Job Actions
# ============================================================


@router.post(
    "/jobs/{job_id}/retry",
)
async def retry_job(
    job_id: UUID,
    request: QueueRetryRequest,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Retry failed job.
    """

    service = QueueService(
        db
    )


    return await service.retry_job(

        job_id=job_id,

        reason=request.reason,

    )



@router.post(
    "/jobs/{job_id}/cancel",
)
async def cancel_job(
    job_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Cancel queued job.
    """

    service = QueueService(
        db
    )


    return await service.cancel_job(

        job_id

    )



@router.post(
    "/jobs/{job_id}/pause",
)
async def pause_job(
    job_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Pause running job.
    """

    service = QueueService(
        db
    )


    return await service.pause_job(

        job_id

    )



@router.post(
    "/jobs/{job_id}/resume",
)
async def resume_job(
    job_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Resume paused job.
    """

    service = QueueService(
        db
    )


    return await service.resume_job(

        job_id

    )



# ============================================================
# Queue Workers
# ============================================================


@router.get(
    "/workers",
)
async def worker_status(
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Retrieve worker status.
    """

    service = QueueService(
        db
    )


    return await service.worker_status()



@router.post(
    "/workers/{worker_id}/restart",
)
async def restart_worker(
    worker_id: str,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Restart queue worker.
    """

    service = QueueService(
        db
    )


    return await service.restart_worker(

        worker_id

    )



# ============================================================
# Queue Monitoring
# ============================================================


@router.get(
    "/statistics",
)
async def queue_statistics(
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Queue metrics.
    """

    service = QueueService(
        db
    )


    return await service.queue_statistics()



@router.get(
    "/health",
)
async def queue_health():
    """
    Queue system health.
    """

    return {

        "queue":

            {

                "status":

                    "healthy",


                "workers":

                    "available",


                "processing":

                    True,

            }

    }