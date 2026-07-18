"""
QShield Enterprise
==================

Background Job Scheduler.

Responsibilities:

- Scheduled task execution
- Recurring job management
- Cron-style scheduling
- Security automation workflows
- Periodic maintenance tasks

Supports:

- Scan scheduling
- Report scheduling
- Backup scheduling
- PQC key rotation
- Compliance assessments

"""

from __future__ import annotations


import asyncio


import logging


import uuid


from dataclasses import dataclass
from dataclasses import field


from datetime import datetime
from datetime import timedelta
from datetime import timezone


from enum import Enum


from typing import Any
from typing import Awaitable
from typing import Callable



from app.workers.task_queue import enqueue
from app.workers.task_queue import JobPriority



logger = logging.getLogger(__name__)



# ============================================================
# Schedule Types
# ============================================================


class ScheduleType(
    str,
    Enum
):

    ONCE = "once"

    INTERVAL = "interval"

    DAILY = "daily"

    WEEKLY = "weekly"

    CRON = "cron"



# ============================================================
# Scheduled Job Model
# ============================================================


@dataclass
class ScheduledJob:
    """
    Scheduled background job.
    """

    schedule_id: str

    name: str

    function: Callable[..., Awaitable[Any]]

    schedule_type: ScheduleType

    interval_seconds: int | None = None

    next_run: datetime | None = None

    enabled: bool = True

    args: tuple = field(

        default_factory=tuple

    )

    kwargs: dict[str, Any] = field(

        default_factory=dict

    )

    executions: int = 0

    last_execution: datetime | None = None



# ============================================================
# Scheduler Engine
# ============================================================


class Scheduler:
    """
    Async task scheduler.

    Executes recurring jobs and
    pushes them into task queue.

    """

    def __init__(self):

        self.jobs: dict[str, ScheduledJob] = {}

        self.running = False

        self.task: asyncio.Task | None = None



    # --------------------------------------------------------
    # Register Job
    # --------------------------------------------------------


    def add_job(
        self,
        name: str,
        function: Callable[..., Awaitable[Any]],
        schedule_type: ScheduleType,
        interval_seconds: int | None = None,
        args: tuple = (),
        kwargs: dict[str, Any] | None = None,
    ) -> str:
        """
        Register scheduled job.
        """

        schedule_id = str(

            uuid.uuid4()

        )


        job = ScheduledJob(

            schedule_id=schedule_id,

            name=name,

            function=function,

            schedule_type=schedule_type,

            interval_seconds=interval_seconds,

            next_run=datetime.now(

                timezone.utc

            ),

            args=args,

            kwargs=kwargs or {},

        )


        self.jobs[schedule_id] = job



        logger.info(

            "Scheduled job registered: %s",

            name,

        )



        return schedule_id



    # --------------------------------------------------------
    # Remove Job
    # --------------------------------------------------------


    def remove_job(
        self,
        schedule_id: str,
    ):
        """
        Remove scheduled task.
        """

        self.jobs.pop(

            schedule_id,

            None

        )



    # --------------------------------------------------------
    # Scheduler Loop
    # --------------------------------------------------------


    async def run(
        self,
    ):
        """
        Main scheduler loop.
        """

        self.running = True



        while self.running:

            now = datetime.now(

                timezone.utc

            )



            for job in self.jobs.values():

                if not job.enabled:

                    continue



                if (

                    job.next_run

                    and

                    now >= job.next_run

                ):

                    await self.execute_job(

                        job

                    )



            await asyncio.sleep(

                1

            )



    async def execute_job(
        self,
        job: ScheduledJob,
    ):
        """
        Push scheduled job to queue.
        """

        try:

            await enqueue(

                job.name,

                job.function,

                *job.args,

                priority=

                    JobPriority.NORMAL,

                **job.kwargs,

            )


            job.executions += 1


            job.last_execution = datetime.now(

                timezone.utc

            )


            self.update_next_run(

                job

            )



        except Exception as exc:

            logger.exception(

                "Scheduled job failed: %s",

                exc,

            )



    # --------------------------------------------------------
    # Next Execution
    # --------------------------------------------------------


    def update_next_run(
        self,
        job: ScheduledJob,
    ):
        """
        Calculate next execution time.
        """

        now = datetime.now(

            timezone.utc

        )



        if job.schedule_type == ScheduleType.ONCE:

            job.enabled = False


            job.next_run = None



        elif job.schedule_type == ScheduleType.INTERVAL:

            job.next_run = (

                now

                +

                timedelta(

                    seconds=

                    job.interval_seconds or 60

                )

            )



        elif job.schedule_type == ScheduleType.DAILY:

            job.next_run = (

                now

                +

                timedelta(

                    days=1

                )

            )



        elif job.schedule_type == ScheduleType.WEEKLY:

            job.next_run = (

                now

                +

                timedelta(

                    weeks=1

                )

            )



    # --------------------------------------------------------
    # Lifecycle
    # --------------------------------------------------------


    async def start(
        self,
    ):
        """
        Start scheduler.
        """

        if self.task:

            return



        self.task = asyncio.create_task(

            self.run()

        )



        logger.info(

            "Scheduler started"

        )



    async def stop(
        self,
    ):
        """
        Stop scheduler.
        """

        self.running = False



        if self.task:

            self.task.cancel()



    # --------------------------------------------------------
    # Monitoring
    # --------------------------------------------------------


    def status(
        self,
    ) -> dict[str, Any]:
        """
        Scheduler health.
        """

        return {

            "running":

                self.running,


            "jobs":

                len(

                    self.jobs

                ),


            "scheduled":

                [

                    {

                        "id":

                            job.schedule_id,


                        "name":

                            job.name,


                        "enabled":

                            job.enabled,


                        "executions":

                            job.executions,

                    }

                    for job

                    in self.jobs.values()

                ]

        }



# ============================================================
# Global Scheduler
# ============================================================


scheduler = Scheduler()



# ============================================================
# Lifecycle Helpers
# ============================================================


async def start_scheduler():
    """
    Application startup hook.
    """

    await scheduler.start()



async def stop_scheduler():
    """
    Application shutdown hook.
    """

    await scheduler.stop()