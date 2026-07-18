"""
QShield Enterprise
==================

Worker Test Package.

Contains automated tests for
background processing workers.

Worker Testing Scope:

- Scan Worker
- Backup Worker
- Report Worker
- Scheduler Worker
- Notification Worker
- Cleanup Worker
- Compliance Worker
- Analytics Worker
- Key Rotation Worker

Testing Strategy:

- Job execution validation
- Queue processing
- Retry handling
- Failure recovery
- Scheduled execution
- Worker lifecycle management

Architecture:

tests/

    workers/

        |

        +----------------+

        |                |

    Processing        Maintenance

        |                |

        v                v

 Scan/Report      Backup/Cleanup


"""



__version__ = "1.0.0"



__author__ = "QShield Enterprise"



__all__ = [

    "test_scan_worker",

    "test_backup_worker",

    "test_report_worker",

    "test_scheduler",

    "test_notification_worker",

    "test_cleanup_worker",

    "test_compliance_worker",

    "test_analytics_worker",

    "test_key_rotation_worker",

]