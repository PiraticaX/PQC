"""
QShield Enterprise
==================

Service Test Package.

Contains unit and integration
tests for backend service layers.

Service Testing Scope:

- Scan Service
- Report Service
- Backup Service
- Compliance Service
- Analytics Service
- Notification Service

Testing Strategy:

- Business logic validation
- Service workflows
- Dependency mocking
- Error handling
- Data processing
- Integration behaviour

Architecture:

tests/

    services/

        |

        +----------------+

        |                |

     Security         Operations

        |                |

        v                v

   Scan Engine      Reports/Backup


"""



__version__ = "1.0.0"



__author__ = "QShield Enterprise"



__all__ = [

    "test_scan_service",

    "test_report_service",

    "test_backup_service",

    "test_compliance_service",

    "test_analytics_service",

]