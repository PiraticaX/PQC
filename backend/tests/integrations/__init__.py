"""
QShield Enterprise
==================

Integration Test Package.

Contains end-to-end workflow tests
covering multiple backend components.

Integration Testing Scope:

- Full Security Scan Pipeline
- Authentication Flow
- PQC Migration Workflow
- Backup and Restore Workflow
- Compliance Pipeline
- Quantum Security Workflow
- Enterprise End-to-End Flow

Testing Strategy:

- Service interaction validation
- Database integration
- API-service communication
- Worker execution flows
- Security lifecycle validation
- Cross-module workflows

Architecture:

tests/

    integration/

        |

        +-----------------------+

        |                       |

    Security Flows          Platform Flows

        |                       |

        v                       v

 Scan/Auth/PQC        Backup/Compliance


"""



__version__ = "1.0.0"



__author__ = "QShield Enterprise"



__all__ = [

    "test_full_scan_pipeline",

    "test_auth_flow",

    "test_pqc_migration_flow",

    "test_backup_restore_flow",

    "test_compliance_pipeline",

    "test_quantum_security_flow",

    "test_end_to_end",

]