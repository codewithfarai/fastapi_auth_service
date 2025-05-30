# FastAPI Auth Service - Docker Swarm Complete Project Structure

```
fastapi-auth-service/
├── README.md
├── pyproject.toml
├── poetry.lock
├── .env.example
├── .env
├── .gitignore
├── Dockerfile
├── docker-compose.yml              # Local development
├── docker-compose.prod.yml         # Production Swarm stack
├── docker-compose.override.yml     # Local overrides
├── .dockerignore
├── Makefile
├── requirements.txt (optional - for non-Poetry deployments)
│
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application entry point
│   ├── config.py                   # Configuration settings
│   ├── dependencies.py             # Shared dependencies
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py             # Authentication routes
│   │   │   ├── customer.py         # Customer-specific routes
│   │   │   ├── provider.py         # Service provider routes
│   │   │   ├── shared.py           # Shared routes for both roles
│   │   │   └── admin.py            # Admin routes
│   │   │
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── auth.py             # Authentication middleware
│   │       ├── cors.py             # CORS middleware
│   │       ├── logging.py          # Logging middleware
│   │       └── rate_limiting.py    # Rate limiting middleware
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── jwt_handler.py      # JWT token verification
│   │   │   ├── auth0_client.py     # Auth0 integration
│   │   │   └── permissions.py      # Permission checking logic
│   │   │
│   │   ├── security/
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py     # Security dependencies
│   │   │   ├── roles.py            # Role definitions and checks
│   │   │   └── permissions.py      # Permission definitions
│   │   │
│   │   └── exceptions/
│   │       ├── __init__.py
│   │       ├── auth_exceptions.py  # Authentication exceptions
│   │       ├── base_exceptions.py  # Base exception classes
│   │       └── handlers.py         # Exception handlers
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                 # User models
│   │   ├── auth.py                 # Authentication models
│   │   ├── customer.py             # Customer-specific models
│   │   ├── provider.py             # Service provider models
│   │   └── shared.py               # Shared models
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py                 # User Pydantic schemas
│   │   ├── auth.py                 # Authentication schemas
│   │   ├── customer.py             # Customer schemas
│   │   ├── provider.py             # Service provider schemas
│   │   └── responses.py            # API response schemas
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py         # Authentication business logic
│   │   ├── user_service.py         # User management service
│   │   ├── customer_service.py     # Customer business logic
│   │   ├── provider_service.py     # Provider business logic
│   │   └── notification_service.py # Email/SMS notifications
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py             # Database connection
│   │   ├── models/                 # SQLAlchemy models (if using DB)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── customer.py
│   │   │   └── provider.py
│   │   │
│   │   ├── repositories/           # Data access layer
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user_repository.py
│   │   │   ├── customer_repository.py
│   │   │   └── provider_repository.py
│   │   │
│   │   └── migrations/             # Database migrations
│   │       └── alembic/
│   │           ├── versions/
│   │           ├── env.py
│   │           └── script.py.mako
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logging.py              # Logging utilities
│       ├── helpers.py              # Helper functions
│       ├── validators.py           # Custom validators
│       └── constants.py            # Application constants
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Pytest configuration
│   ├── fixtures/
│   │   ├── __init__.py
│   │   ├── auth_fixtures.py        # Authentication test fixtures
│   │   └── user_fixtures.py        # User test fixtures
│   │
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_auth/
│   │   │   ├── __init__.py
│   │   │   ├── test_jwt_handler.py
│   │   │   ├── test_auth0_client.py
│   │   │   └── test_permissions.py
│   │   │
│   │   ├── test_services/
│   │   │   ├── __init__.py
│   │   │   ├── test_auth_service.py
│   │   │   ├── test_user_service.py
│   │   │   └── test_customer_service.py
│   │   │
│   │   └── test_utils/
│   │       ├── __init__.py
│   │       ├── test_helpers.py
│   │       └── test_validators.py
│   │
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_auth_flow.py       # Full authentication flow tests
│   │   ├── test_api_endpoints.py   # API endpoint integration tests
│   │   └── test_role_access.py     # Role-based access tests
│   │
│   └── e2e/
│       ├── __init__.py
│       ├── test_customer_journey.py # End-to-end customer tests
│       └── test_provider_journey.py # End-to-end provider tests
│
├── scripts/
│   ├── setup.sh                    # Environment setup script
│   ├── deploy-swarm.sh             # Swarm deployment script
│   ├── update-service.sh           # Rolling update script
│   ├── test.sh                     # Test execution script
│   ├── migrate.py                  # Database migration script
│   ├── seed_data.py                # Database seeding script
│   └── swarm-init.sh               # Initialize swarm cluster
│
├── docs/
│   ├── README.md
│   ├── API.md                      # API documentation
│   ├── DEPLOYMENT.md               # Deployment guide
│   ├── CONTRIBUTING.md             # Contributing guidelines
│   ├── CHANGELOG.md                # Version changelog
│   │
│   ├── diagrams/
│   │   ├── user-flow.mmd           # Mermaid diagram source
│   │   ├── sequence-diagram.mmd    # Sequence diagram source
│   │   ├── architecture.png        # Architecture diagrams
│   │   └── auth-flow.png           # Authentication flow diagrams
│   │
│   ├── auth-setup/
│   │   ├── auth0-configuration.md  # Auth0 setup guide
│   │   └── screenshots/            # Setup screenshots
│   │
│   ├── api-examples/
│   │   ├── curl-examples.sh        # cURL API examples
│   │   ├── postman-collection.json # Postman collection
│   │   └── python-client.py        # Python client examples
│   │
│   └── swarm-deployment/           # Swarm-specific docs
│       ├── setup-guide.md
│       ├── scaling-guide.md
│       └── troubleshooting.md
│
├── config/
│   ├── development.yaml            # Development configuration
│   ├── production.yaml             # Production configuration
│   ├── testing.yaml                # Testing configuration
│   ├── logging.yaml                # Logging configuration
│   └── swarm/                      # Swarm configs
│       ├── nginx.conf
│       └── haproxy.cfg
│
├── deployment/
│   ├── swarm/                      # Docker Swarm deployment
│   │   ├── stacks/
│   │   │   ├── auth-service.yml
│   │   │   ├── monitoring.yml
│   │   │   └── networking.yml
│   │   ├── configs/
│   │   │   ├── nginx.conf
│   │   │   └── app-config.yml
│   │   ├── secrets/
│   │   │   └── .gitkeep
│   │   └── volumes/
│   │       └── .gitkeep
│   │
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── modules/
│   │       └── docker-swarm/
│   │
│   └── ansible/                    # Swarm orchestration
│       ├── playbooks/
│       │   ├── deploy-stack.yml
│       │   ├── update-service.yml
│       │   └── setup-swarm.yml
│       └── inventory/
│           └── hosts.yml
│
├── monitoring/
│   ├── prometheus/
│   │   ├── metrics.py              # Custom metrics
│   │   └── prometheus.yml          # Swarm service discovery
│   │
│   ├── grafana/
│   │   └── dashboards/
│   │       └── auth-service.json
│   │
│   ├── alerts/
│   │   └── auth-alerts.yaml
│   │
│   └── docker-compose.monitoring.yml  # Monitoring stack
│
└── tools/
    ├── pre-commit-config.yaml      # Pre-commit hooks
    ├── github-workflows/
    │   ├── ci.yml                  # Continuous Integration
    │   ├── cd.yml                  # Continuous Deployment (Swarm)
    │   └── security-scan.yml       # Security scanning
    │
    └── local-development/
        ├── docker-compose.dev.yml  # Development containers
        └── setup-local-auth0.py    # Local Auth0 setup script
```