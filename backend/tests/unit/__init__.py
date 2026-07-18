"""
QShield Enterprise
==================

Unit Test Package.

Contains isolated tests for
individual backend components.

Unit Testing Scope:

- Utility functions
- Security modules
- Cryptographic operations
- Validation logic
- Serialization logic
- Core business rules

Testing Principle:

Each component is tested independently
with mocked external dependencies.

Architecture:

tests/

    unit/

        |

        +----------------+

        |                |

     Security          Utils

        |

        v

 Crypto / PQC / Auth


"""



__version__ = "1.0.0"



__author__ = "QShield Enterprise"



__all__ = [

    "test_auth",

    "test_security",

    "test_encryption",

    "test_hashing",

    "test_validators",

    "test_serializers",

    "test_utils",

]