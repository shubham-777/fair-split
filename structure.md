fairsplit-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Environment & app configuration
│   ├── database.py                # Database connection & session
│   ├── dependencies.py            # Shared dependencies (auth, db)
│   │
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── group.py
│   │   ├── expense.py
│   │   ├── settlement.py
│   │   └── notification.py
│   │
│   ├── schemas/                   # Pydantic models (request/response)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── group.py
│   │   ├── expense.py
│   │   ├── settlement.py
│   │   └── notification.py
│   │
│   ├── api/                       # API routes
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── groups.py
│   │   │   ├── expenses.py
│   │   │   ├── settlements.py
│   │   │   └── notifications.py
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── balance_service.py
│   │   ├── debt_simplifier.py
│   │   └── notification_service.py
│   │
│   ├── utils/                     # Utility functions
│   │   ├── __init__.py
│   │   ├── security.py           # JWT, password hashing
│   │   └── helpers.py
│   │
│   └── tests/                     # Pytest tests
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_groups.py
│       └── test_expenses.py
│
├── alembic/                       # Database migrations
│   ├── versions/
│   └── env.py
│
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── alembic.ini
└── README.md