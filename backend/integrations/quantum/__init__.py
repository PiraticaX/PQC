"""
QShield Enterprise
==================

Quantum Integration Layer.

This package provides connectors
to quantum computing platforms.

Supported:

- IBM Quantum
- Qiskit Runtime
- D-Wave Quantum
- Hybrid Quantum Workflows

Purpose:

Enable QShield security and optimization
services to interact with quantum backends.

Architecture:

QShield

  |

  v

Quantum Integration Layer

  |

  +----------------+

  |                |

  v                v

IBM Quantum     D-Wave

Qiskit          Quantum Annealing

"""



__version__ = "1.0.0"



__author__ = "QShield Enterprise"



__all__ = [

    "quantum_manager",

    "ibm_quantum",

    "dwave",

    "qiskit_adapter",

]