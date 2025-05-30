[![CI Pipeline Status](https://github.com/project-owner/auth-service/actions/workflows/fauth_service_ci.yml/badge.svg)](https://github.com/project-owner/auth-service/actions/workflows/fauth_service_ci.yml)

# FastAPI Authentication Service

A production-ready authentication service with Auth0 integration, role-based access control, and async support.

## Table of Contents

- [Installation](#installation)
- [Development Setup](#development-setup)
- [Docker Setup](#docker-setup)
- [VS Code Configuration](#vs-code-configuration)
- [Pre-commit Hooks](#pre-commit-hooks)
- [Running the Application](#running-the-application)
- [Testing](#testing)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd fastapi_auth_service

# Install dependencies with Poetry
poetry install

# Copy environment file
cp .env.example .env
# Edit .env with your configuration
```

## Development Setup

This project uses Poetry for dependency management and includes comprehensive development tooling.

### Prerequisites

- Python 3.12+
- Poetry
- VS Code (recommended)
- Docker & Docker Compose (for containerized development)

## Docker Setup

The project includes comprehensive Docker support for both development and production environments.

### 🚀 **Quick Start with Docker**

```bash
# Create environment file
make env-example
cp .env.example .env

# Start development environment
make dev

# Or for production
make prod
```

### 🐳 **Docker Features**

- **Multi-stage Dockerfile**: Optimized builds for development and production
- **Docker Compose configurations**: Separate configs for dev and production
- **PostgreSQL 16**: Database with persistent storage
- **Redis 7**: Caching layer with optional authentication
- **Development tools**: pgAdmin, Redis Commander, MailHog
- **Health checks**: All services include proper health monitoring
- **Hot reload**: Code changes reflect immediately in development

### 📦 **Available Services**

#### Development Environment
- **FastAPI app**: http://localhost:8000
- **API docs**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050 (dev@example.com / dev_password)
- **Redis Commander**: http://localhost:8081
- **MailHog**: http://localhost:8025

### 🛠️ **Docker Commands**

```bash
# Development commands
make build-dev      # Build development images
make up-dev         # Start development containers
make down-dev       # Stop development containers
make logs-dev       # View development logs
make shell-dev      # Access app container shell
make test-dev       # Run tests in container

# Production commands
make build          # Build production images
make up             # Start production containers
make down           # Stop production containers
make health         # Check services health

# Database commands
make db-shell-dev   # Access PostgreSQL shell
make migrate-dev    # Run database migrations

# Cleanup
make clean          # Clean up containers and volumes
make clean-all      # Deep clean including images
```

For detailed Docker documentation, see [docs/docker-setup.md](docs/docker-setup.md).

## VS Code Configuration

The project includes a comprehensive VS Code configuration in `.vscode/settings.json` that provides:

### 🐍 **Python Configuration**

- **Interpreter**: Automatically uses `.venv/bin/python`
- **Environment**: Activates virtual environment in terminal
- **PYTHONPATH**: Set to workspace folder for proper imports

### 🎨 **Code Formatting**

- **Black**: Primary code formatter (88 character line length)
- **Format on Save**: Enabled for consistent code style
- **Import Organization**: Automatic import sorting with isort

### 🔍 **Linting & Type Checking**

- **Flake8**: Enabled for code quality checks
- **MyPy**: Enabled for static type checking
- **Pylint**: Disabled (using Flake8 instead)

### 🧪 **Testing Configuration**

- **Pytest**: Configured as primary test runner
- **Test Discovery**: Automatic detection in `tests/` directory
- **Test Args**: `tests` directory specified

### 📁 **File Management**

- **Exclusions**: `__pycache__`, `.pytest_cache`, `.mypy_cache`, `node_modules`, `.venv`
- **Search Exclusions**: Same as above plus `poetry.lock`
- **File Associations**: `.env` files treated as properties

### ⚙️ **Editor Settings**

- **Line Length**: 88 characters (ruler displayed)
- **Tab Size**: 4 spaces
- **Insert Spaces**: Enabled
- **Type Checking**: Strict mode

## Pre-commit Hooks

The project uses strict pre-commit hooks located in `tools/.pre-commit-config.yaml` to ensure code quality.

### 🔧 **Installation**

```bash
# Install pre-commit hooks
poetry run pre-commit install --config tools/.pre-commit-config.yaml

# Run on all files (optional)
poetry run pre-commit run --config tools/.pre-commit-config.yaml --all-files
```

### 📋 **Hook Categories**

#### **File Management**

- ✅ `trailing-whitespace` - Removes trailing whitespace
- ✅ `end-of-file-fixer` - Ensures files end with newline
- ✅ `check-yaml` - Validates YAML syntax
- ✅ `check-toml` - Validates TOML syntax
- ✅ `check-json` - Validates JSON syntax
- ✅ `check-added-large-files` - Prevents files >500KB
- ✅ `check-merge-conflict` - Detects merge conflict markers
- ✅ `check-case-conflict` - Prevents case-sensitive filename conflicts
- ✅ `debug-statements` - Catches leftover debug code

#### **Code Formatting (Auto-fix)**

- 🎨 `black` - Code formatting (88 char line length)
- 🎨 `isort` - Import sorting (black profile)

#### **Code Quality (Strict)**

- 🔍 `flake8` - Comprehensive linting with plugins:
  - `flake8-docstrings` - Documentation standards
  - `flake8-comprehensions` - Better comprehensions
  - `flake8-bugbear` - Bug and design problems
  - Max complexity: 10
  - Line length: 88

#### **Type Checking (Strict)**

- 🔍 `mypy` - Static type checking:
  - Strict mode enabled
  - Specific type stubs for FastAPI ecosystem
  - Excludes: `tests/`, `migrations/`

#### **Security**

- 🔒 `bandit` - Security vulnerability scanner
- 🔒 Scans `app/` directory
- 🔒 Excludes: `tests/`

#### **Testing**

- 🧪 `pytest` - Runs test suite on commit
- 🧪 Verbose output with short traceback

#### **Documentation**

- 📚 `pydocstyle` - Google-style docstring enforcement
- 📚 Excludes: `tests/`, `migrations/`

### 🚫 **Exclusions**

All hooks ignore the `.vscode/` folder to prevent interference with VS Code configuration files.

### 🛠️ **Manual Commands**

```bash
# Run specific hook
poetry run pre-commit run black --config tools/.pre-commit-config.yaml

# Run on specific files
poetry run pre-commit run --config tools/.pre-commit-config.yaml --files app/main.py

# Skip hooks temporarily
git commit --no-verify -m "Quick fix"

# Run individual tools manually
poetry run black app/
poetry run isort app/
poetry run flake8 app/
poetry run mypy app/
poetry run bandit -r app/
poetry run pytest
```

### 📊 **Hook Success Tips**

1. **Start Small**: Test hooks on individual files first
2. **Fix Incrementally**: Address one type of issue at a time
3. **Use Auto-fix**: Black and isort will fix formatting automatically
4. **Check Types**: Ensure proper type annotations for mypy
5. **Write Tests**: Pytest must pass for commits to succeed

## Running the Application

```bash
# Development server
poetry run python run_dev_server.py

# Or with uvicorn directly
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run specific test file
poetry run pytest tests/test_main.py

# Run with verbose output
poetry run pytest -v
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Application
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
DEBUG=true

# Auth0 Configuration
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
AUTH0_AUDIENCE=your-api-audience

# Optional Services
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

## Contributing

1. Follow the pre-commit hooks - they enforce our code standards
2. Write tests for new features
3. Update documentation as needed
4. Ensure all hooks pass before submitting PRs

## License

[Your License Here]


## Branch Protection Rules

To ensure repository stability and code quality, the following branch protection rules should be configured in the GitHub repository settings for the `main` and `develop` branches:

1.  **Require a pull request before merging:**
    *   Enable "Require a pull request before merging".
    *   Enable "Require approvals" (set to at least 1).
    *   Optional: Enable "Dismiss stale pull request approvals when new commits are pushed".
    *   Optional: Enable "Require review from Code Owners".

2.  **Require status checks to pass before merging:**
    *   Enable "Require status checks to pass before merging".
    *   Enable "Require branches to be up to date before merging".
    *   Select the following status checks (ensure these names match the job names in your GitHub Actions workflows):
        *   From CI Pipeline (`.github/workflows/fauth_service_ci.yml`):
            *   `Lint, Format, Type Check` (or the exact name of your lint/format/type job)
            *   `Test Suite` (or the exact name of your test job)
            *   `Dependency Review`
        *   From Security Scan (`.github/workflows/fauth_service_security_scan.yml`):
            *   `CodeQL Analysis` (or the exact name of your CodeQL job, e.g., `codeql-analysis`)
            *   `Snyk Vulnerability Scan` (or the exact name of your Snyk job)

3.  **Require signed commits (Optional but Recommended):**
    *   Enable "Require signed commits".

4.  **Include administrators:**
    *   Enforce these rules for administrators as well.

5.  **Restrict who can push to matching branches (Recommended):**
    *   Enable this and specify teams or people allowed to push (often, direct pushes are disallowed entirely in favor of PRs).

These rules help maintain a high quality bar for code merged into critical branches.
