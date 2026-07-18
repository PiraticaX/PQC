"""
QShield Enterprise
==================

IBM Quantum Integration.

Responsibilities:

- IBM Quantum Runtime connection
- Backend selection
- Quantum circuit execution
- Job monitoring
- Quantum hardware health checks

Integrates with:

- Qiskit Runtime
- IBM Quantum Platform
- Quantum Manager

"""

from __future__ import annotations


import logging


from typing import Any



from app.integrations.quantum.quantum_manager import QuantumBackend



logger = logging.getLogger(__name__)



# ============================================================
# Optional Qiskit Imports
# ============================================================


try:

    from qiskit import QuantumCircuit

    from qiskit_ibm_runtime import (

        QiskitRuntimeService,

        SamplerV2,

        EstimatorV2,

    )


    QISKIT_AVAILABLE = True


except ImportError:

    QISKIT_AVAILABLE = False



# ============================================================
# IBM Quantum Connector
# ============================================================


class IBMQuantumBackend(
    QuantumBackend
):
    """
    IBM Quantum Runtime connector.

    Supports:

    - Real quantum hardware
    - IBM simulators
    - Runtime primitives

    """



    def __init__(
        self,
        token: str | None = None,
        backend_name: str = "ibm_brisbane",
    ):

        self.token = token

        self.backend_name = backend_name

        self.service = None

        self.backend = None

        self.connected = False



    # --------------------------------------------------------
    # Connect
    # --------------------------------------------------------


    async def connect(
        self,
    ) -> bool:
        """
        Connect to IBM Quantum.
        """

        if not QISKIT_AVAILABLE:

            logger.warning(

                "Qiskit not installed. Using simulation mode."

            )


            self.connected = True


            return True



        try:

            self.service = QiskitRuntimeService(

                channel="ibm_quantum",

                token=self.token,

            )


            self.backend = (

                self.service.backend(

                    self.backend_name

                )

            )


            self.connected = True



            logger.info(

                "Connected to IBM Quantum backend %s",

                self.backend_name,

            )



            return True



        except Exception as exc:

            logger.exception(

                "IBM Quantum connection failed: %s",

                exc,

            )


            return False



    # --------------------------------------------------------
    # Execute Circuit
    # --------------------------------------------------------


    async def execute(
        self,
        circuit: Any,
    ) -> dict[str, Any]:
        """
        Execute quantum circuit.

        Uses:

        - Sampler primitive
        - Runtime execution

        """

        if not self.connected:

            await self.connect()



        try:

            if not QISKIT_AVAILABLE:

                return {

                    "provider":

                        "IBM Quantum",

                    "mode":

                        "simulation",

                    "result":

                        {

                            "status":

                                "completed"

                        }

                }



            sampler = SamplerV2(

                mode=self.backend

            )


            job = sampler.run(

                [

                    circuit

                ]

            )


            result = job.result()



            return {

                "provider":

                    "ibm_quantum",


                "backend":

                    self.backend_name,


                "job_id":

                    job.job_id(),


                "result":

                    str(result),

            }



        except Exception as exc:

            logger.exception(

                "IBM execution failed: %s",

                exc,

            )


            raise



    # --------------------------------------------------------
    # Health Check
    # --------------------------------------------------------


    async def health_check(
        self,
    ) -> dict[str, Any]:
        """
        IBM Quantum health.
        """

        return {

            "provider":

                "IBM Quantum",


            "backend":

                self.backend_name,


            "connected":

                self.connected,


            "available":

                QISKIT_AVAILABLE,

        }



# ============================================================
# Factory
# ============================================================


def create_ibm_quantum_backend(
    token: str | None = None,
    backend_name: str = "ibm_brisbane",
):
    """
    Create IBM Quantum backend.
    """

    return IBMQuantumBackend(

        token=token,

        backend_name=backend_name,

    )