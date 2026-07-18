"""
QShield Enterprise
==================

Worker Manager.

Responsibilities:

- Worker lifecycle management
- Worker startup/shutdown
- Background task orchestration
- Worker health monitoring
- Queue supervision
- Graceful termination

Integrates with:

- Task Queue
- Scheduler
- FastAPI Lifespan
- Monitoring System

"""

from __future__ import annotations


import asyncio


import logging


from datetime import datetime
from datetime import timezone


from dataclasses import dataclass
from dataclasses import field


from typing import Any



from app.workers.task_queue import task_queue
from app.workers.task_queue import TaskQueue



logger = logging.getLogger(__name__)



# ============================================================
# Worker Status
# ============================================================


@dataclass
class WorkerStatus:
    """
    Worker runtime information.
    """

    name: str

    running: bool = False

    started_at: datetime | None = None

    stopped_at: datetime | None = None

    tasks_processed: int = 0

    last_error: str | None = None



# ============================================================
# Worker Manager
# ============================================================


class WorkerManager:
    """
    Controls background workers.

    Responsibilities:

    - Start workers
    - Monitor workers
    - Stop workers
    - Track health

    """

    def __init__(
        self,
        queue: TaskQueue,
    ):

        self.queue = queue


        self.workers: dict[str, asyncio.Task] = {}


        self.status: dict[str, WorkerStatus] = {}


        self.running = False



    # --------------------------------------------------------
    # Register Worker
    # --------------------------------------------------------


    def register_worker(
        self,
        name: str,
    ):
        """
        Register worker instance.
        """

        if name not in self.status:

            self.status[name] = WorkerStatus(

                name=name

            )



    # --------------------------------------------------------
    # Start Workers
    # --------------------------------------------------------


    async def start_worker(
        self,
        name: str,
    ):
        """
        Start queue worker.

        """

        if name in self.workers:

            return



        self.register_worker(

            name

        )


        worker_status = self.status[name]



        worker_status.running = True


        worker_status.started_at = datetime.now(

            timezone.utc

        )



        task = asyncio.create_task(

            self.queue.worker_loop()

        )



        self.workers[name] = task



        logger.info(

            "Worker started: %s",

            name,

        )



    async def start_all(
        self,
        count: int = 1,
    ):
        """
        Start multiple workers.
        """

        self.running = True



        for index in range(

            count

        ):

            await self.start_worker(

                f"worker-{index+1}"

            )



    # --------------------------------------------------------
    # Stop Workers
    # --------------------------------------------------------


    async def stop_worker(
        self,
        name: str,
    ):
        """
        Stop specific worker.
        """

        task = self.workers.get(

            name

        )


        if not task:

            return



        task.cancel()



        try:

            await task


        except asyncio.CancelledError:

            pass



        self.status[name].running = False


        self.status[name].stopped_at = datetime.now(

            timezone.utc

        )



        del self.workers[name]



    async def stop_all(
        self,
    ):
        """
        Stop all workers.
        """

        for name in list(

            self.workers.keys()

        ):

            await self.stop_worker(

                name

            )



        await self.queue.shutdown()



        self.running = False



        logger.info(

            "All workers stopped"

        )



    # --------------------------------------------------------
    # Monitoring
    # --------------------------------------------------------


    def health(
        self,
    ) -> dict[str, Any]:
        """
        Worker health status.
        """

        return {

            "manager":

                {

                    "running":

                        self.running,


                    "workers":

                        len(

                            self.workers

                        ),

                },


            "instances":

                {

                    name:

                        {

                            "running":

                                worker.running,


                            "started":

                                worker.started_at,

                            "tasks":

                                worker.tasks_processed,

                            "error":

                                worker.last_error,

                        }


                    for name, worker

                    in self.status.items()

                }

        }



    # --------------------------------------------------------
    # Queue Information
    # --------------------------------------------------------


    def queue_status(
        self,
    ) -> dict[str, Any]:
        """
        Retrieve queue metrics.
        """

        return {

            "queued_tasks":

                self.queue.queue.qsize(),


            "registered_jobs":

                len(

                    self.queue.jobs

                ),

        }



# ============================================================
# Global Worker Manager
# ============================================================


worker_manager = WorkerManager(

    task_queue

)



# ============================================================
# Lifecycle Helpers
# ============================================================


async def start_workers():
    """
    Application startup hook.
    """

    await worker_manager.start_all(

        count=2

    )



async def stop_workers():
    """
    Application shutdown hook.
    """

    await worker_manager.stop_all()



def worker_health():
    """
    External health endpoint helper.
    """

    return worker_manager.health()