"""
QShield Enterprise
==================

Backend Test Suite.

This package contains the complete
automated testing framework for QShield.

Testing Layers:

- Unit Tests
- API Tests
- Service Tests
- Worker Tests
- Integration Tests
- Security Tests
- Performance Tests

Architecture:

QShield Backend

        |

        v

      tests/

        |

 +------+------+------+------+

 |      |      |      |      |

Unit   API  Service Worker Security


"""



__version__ = "1.0.0"



__author__ = "QShield Enterprise"



__all__ = [

    "fixtures",

    "unit",

    "api",

    "services",

    "workers",

    "integrations",

    "security",

    "performance",

]