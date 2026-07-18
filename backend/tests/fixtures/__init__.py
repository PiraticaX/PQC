"""
QShield Enterprise
==================

Test Fixtures Package.

Contains reusable test data
and mock objects used across
the QShield test suite.

Fixture Categories:

- Users
- Assets
- Security Scans
- Security Events

Used by:

- Unit Tests
- API Tests
- Service Tests
- Integration Tests

Architecture:

tests/

   |

   v

fixtures/

   |

   +------------+------------+

   |            |            |

 Users       Assets       Security


"""



__version__ = "1.0.0"



__author__ = "QShield Enterprise"



__all__ = [

    "users",

    "assets",

    "scans",

    "security_events",

]