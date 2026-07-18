"""
QShield Enterprise
==================

D-Wave Quantum Integration.

Responsibilities:

- D-Wave quantum annealing connection
- QUBO optimization execution
- Hybrid quantum-classical solving
- Solver health monitoring
- Optimization workload abstraction

Integrates with:

- D-Wave Ocean SDK
- Quantum Manager
- Optimization Engine

"""

from __future__ import annotations


import logging


from typing import Any



from app.integrations.quantum.quantum_manager import QuantumBackend



logger = logging.getLogger(__name__)



# ============================================================
# Optional D-Wave Imports
# ============================================================


try:

    from dwave.system import (

        DWaveSampler,

        EmbeddingComposite,

        LeapHybridSampler,

    )


    DWAVE_AVAILABLE = True



except ImportError:

    DWAVE_AVAILABLE = False



# ============================================================
# D-Wave Backend
# ============================================================


class DWaveBackend(
    QuantumBackend
):
    """
    D-Wave quantum annealing connector.

    Supports:

    - Quantum annealer
    - Hybrid solver
    - QUBO optimization

    """



    def __init__(
        self,
        token: str | None = None,
        solver: str | None = None,
        use_hybrid: bool = True,
    ):

        self.token = token

        self.solver = solver

        self.use_hybrid = use_hybrid

        self.sampler = None

        self.connected = False



    # --------------------------------------------------------
    # Connect
    # --------------------------------------------------------


    async def connect(
        self,
    ) -> bool:
        """
        Connect to D-Wave Leap.
        """

        if not DWAVE_AVAILABLE:

            logger.warning(

                "D-Wave SDK unavailable. Running simulation mode."

            )


            self.connected = True


            return True



        try:

            if self.use_hybrid:

                self.sampler = LeapHybridSampler(

                    token=self.token

                )


            else:

                sampler = DWaveSampler(

                    token=self.token,

                    solver=self.solver,

                )


                self.sampler = EmbeddingComposite(

                    sampler

                )



            self.connected = True



            logger.info(

                "Connected to D-Wave backend"

            )



            return True



        except Exception as exc:

            logger.exception(

                "D-Wave connection failed: %s",

                exc,

            )


            return False



    # --------------------------------------------------------
    # Execute QUBO
    # --------------------------------------------------------


    async def execute(
        self,
        qubo: dict[tuple, float],
    ) -> dict[str, Any]:
        """
        Execute QUBO optimization.

        Input:

            {
                ("x1","x1"): -1,
                ("x1","x2"): 2
            }

        """

        if not self.connected:

            await self.connect()



        try:

            if not DWAVE_AVAILABLE:

                return {

                    "provider":

                        "dwave",


                    "mode":

                        "simulation",


                    "solution":

                        {},


                    "energy":

                        0,

                }



            response = self.sampler.sample_qubo(

                qubo

            )



            best = response.first



            return {

                "provider":

                    "dwave",


                "solver":

                    str(

                        self.sampler.solver

                    ),


                "solution":

                    dict(

                        best.sample

                    ),


                "energy":

                    best.energy,


                "occurrences":

                    best.num_occurrences,

            }



        except Exception as exc:

            logger.exception(

                "D-Wave execution failed: %s",

                exc,

            )


            raise



    # --------------------------------------------------------
    # Hybrid Optimization
    # --------------------------------------------------------


    async def solve_optimization_problem(
        self,
        problem: dict[str, Any],
    ) -> dict[str, Any]:
        """
        High-level optimization interface.

        Used by:

        - Fleet optimization
        - Routing
        - Scheduling
        - Resource allocation

        """

        qubo = problem.get(

            "qubo",

            {}

        )


        return await self.execute(

            qubo

        )



    # --------------------------------------------------------
    # Health
    # --------------------------------------------------------


    async def health_check(
        self,
    ) -> dict[str, Any]:
        """
        D-Wave health status.
        """

        return {

            "provider":

                "D-Wave",


            "connected":

                self.connected,


            "sdk_available":

                DWAVE_AVAILABLE,


            "mode":

                "hybrid"

                if self.use_hybrid

                else

                "quantum_annealer",

        }



# ============================================================
# Factory
# ============================================================


def create_dwave_backend(
    token: str | None = None,
    solver: str | None = None,
):
    """
    Create D-Wave backend.
    """

    return DWaveBackend(

        token=token,

        solver=solver,

    )