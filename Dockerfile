# Multi-stage Dockerfile for FastAPI Authentication Service

# Stage 1: Base Python image with system dependencies
FROM python:3.12-slim AS python-base

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# Add poetry to PATH
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Install system dependencies
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Poetry installation
FROM python-base AS poetry-base

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy poetry files
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# Stage 3: Development dependencies
FROM poetry-base AS development

# Install all dependencies including dev
RUN poetry install --no-root

# Copy application code
WORKDIR /app
COPY . .

# Install the application
RUN poetry install

# Expose port
EXPOSE 8000

# Development command with hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage 4: Production dependencies only
FROM poetry-base AS production-deps

# Install only production dependencies
RUN poetry install --no-root --no-dev

# Stage 5: Production runtime
FROM python-base AS production

# Install curl for health checks
RUN apt-get update \
    && apt-get install --no-install-recommends -y curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from production-deps stage
COPY --from=production-deps $PYSETUP_PATH $PYSETUP_PATH

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
