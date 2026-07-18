"""
QShield Enterprise
==================

API Test Package.

Contains integration tests for
FastAPI REST endpoints.

API Testing Scope:

- Authentication APIs
- User APIs
- Asset APIs
- Security Scan APIs
- Report APIs
- Compliance APIs

Testing Strategy:

- Request validation
- Response validation
- Authentication flows
- Authorization checks
- Error handling
- API contracts

Architecture:

tests/

    api/

        |

        +----------------+

        |                |

   Authentication     Resources

        |                |

        v                v

      Auth            CRUD APIs


"""



__version__ = "1.0.0"



__author__ = "QShield Enterprise"



__all__ = [

    "test_auth_api",

    "test_users_api",

    "test_assets_api",

    "test_scans_api",

    "test_reports_api",

    "test_compliance_api",

]