"""
QShield Enterprise
==================

Background Workers Package.

This package contains asynchronous workers responsible for:

- Security scan execution
- Report generation
- Backup operations
- PQC key lifecycle management
- Compliance assessments
- Analytics processing
- Notifications
- System cleanup

Workers execute outside the API request lifecycle.

Architecture:

API
 |
 v
Queue / Scheduler
 |
 v
Workers
 |
 +----------------+
 |                |
 v                v

Database       External Systems

"""



__version__ = "1.0.0"



__author__ = "QShield Enterprise"



__all__ = [

    "worker_manager",

    "task_queue",

    "scheduler",

    "scan_worker",

    "report_worker",

    "backup_worker",

    "key_rotation_worker",

    "compliance_worker",

    "analytics_worker",

    "notification_worker",

    "cleanup_worker",

]