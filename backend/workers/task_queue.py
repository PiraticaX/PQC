"""
QShield Enterprise
==================

Task Queue Infrastructure.

Responsibilities:

- Background job registration
- Async task execution
- Queue management
- Retry handling
- Job status tracking
- Priority management
- Worker communication

Designed to support:

- Redis Queue
- Celery migration
- Distributed workers

"""

from __future__ import annotations


import asyncio


import logging


import uuid


from dataclasses import dataclass
from dataclasses import field


from datetime import datetime
from datetime import timezone


from enum import Enum


from typing import Any
from typing import Awaitable
from typing import Callable



logger = logging.getLogger(__name__)



# ============================================================
# Job Status
# ============================================================


class JobStatus(
    str,
    Enum
):

    PENDING = "pending"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"

    RETRYING = "retrying"



# ============================================================
# Job Priority
# ============================================================


class JobPriority(
    int,
    Enum
):

    LOW = 10

    NORMAL = 50

    HIGH = 80

    CRITICAL = 100



# ============================================================
# Job Model
# ============================================================


@dataclass
class Job:
    """
    Background task definition.
    """

    task_id: str

    task_name: str

    function: Callable[..., Awaitable[Any]]

    args: tuple = field(

        default_factory=tuple

    )

    kwargs: dict[str, Any] = field(

        default_factory=dict

    )

    priority: JobPriority = JobPriority.NORMAL

    status: JobStatus = JobStatus.PENDING

    retries: int = 0

    max_retries: int = 3

    result: Any = None

    error: str | None = None

    created_at: datetime = field(

        default_factory=lambda:

            datetime.now(

                timezone.utc

            )

    )

    started_at: datetime | None = None

    completed_at: datetime | None = None



# ============================================================
# Task Registry
# ============================================================


class TaskQueue:
    """
    Async in-memory task queue.

    Provides:

    - Submit jobs
    - Execute workers
    - Track status

    """

    def __init__(self):

        self.jobs: dict[str, Job] = {}

        self.queue: asyncio.PriorityQueue = (

            asyncio.PriorityQueue()

        )

        self.running = False



    # --------------------------------------------------------
    # Submit Task
    # --------------------------------------------------------


    async def submit(
        self,
        task_name: str,
        function: Callable[..., Awaitable[Any]],
        *args,
        priority: JobPriority = JobPriority.NORMAL,
        **kwargs,
    ) -> str:
        """
        Submit background job.
        """

        task_id = str(

            uuid.uuid4()

        )


        job = Job(

            task_id=task_id,

            task_name=task_name,

            function=function,

            args=args,

            kwargs=kwargs,

            priority=priority,

        )



        self.jobs[task_id] = job



        await self.queue.put(

            (

                -priority.value,

                task_id,

                job,

            )

        )



        logger.info(

            "Task queued: %s",

            task_name,

        )


        return task_id



    # --------------------------------------------------------
    # Worker Loop
    # --------------------------------------------------------


    async def worker_loop(
        self,
    ):
        """
        Execute queued jobs.
        """

        self.running = True



        while self.running:

            try:

                (

                    _priority,

                    _task_id,

                    job

                ) = await self.queue.get()



                await self.execute(

                    job

                )



                self.queue.task_done()



            except asyncio.CancelledError:

                break



            except Exception as exc:

                logger.exception(

                    "Worker execution error: %s",

                    exc,

                )



    # --------------------------------------------------------
    # Execute Job
    # --------------------------------------------------------


    async def execute(
        self,
        job: Job,
    ):
        """
        Execute single job.
        """

        job.status = JobStatus.RUNNING


        job.started_at = datetime.now(

            timezone.utc

        )



        try:

            job.result = await job.function(

                *job.args,

                **job.kwargs,

            )


            job.status = JobStatus.COMPLETED



        except Exception as exc:

            job.error = str(exc)



            if job.retries < job.max_retries:

                job.retries += 1

                job.status = JobStatus.RETRYING



                await self.queue.put(

                    (

                        -job.priority.value,

                        job.task_id,

                        job,

                    )

                )



            else:

                job.status = JobStatus.FAILED



        finally:

            job.completed_at = datetime.now(

                timezone.utc

            )



    # --------------------------------------------------------
    # Job Status
    # --------------------------------------------------------


    def get_job(
        self,
        task_id: str,
    ) -> Job | None:
        """
        Retrieve task status.
        """

        return self.jobs.get(

            task_id

        )



    def cancel(
        self,
        task_id: str,
    ) -> bool:
        """
        Cancel pending job.
        """

        job = self.jobs.get(

            task_id

        )


        if not job:

            return False



        job.status = JobStatus.CANCELLED


        return True



    async def shutdown(
        self,
    ):
        """
        Stop workers.
        """

        self.running = False



# ============================================================
# Global Queue Instance
# ============================================================


task_queue = TaskQueue()



# ============================================================
# Helper Function
# ============================================================


async def enqueue(
    task_name: str,
    function: Callable[..., Awaitable[Any]],
    *args,
    **kwargs,
) -> str:
    """
    Convenience task submission.

    """

    return await task_queue.submit(

        task_name,

        function,

        *args,

        **kwargs,

    )