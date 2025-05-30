.PHONY: help build build-dev up up-dev down down-dev logs logs-dev ps clean test lint format

# Default target
.DEFAULT_GOAL := help

# Auto-detect docker compose command
DOCKER_COMPOSE_CMD := $(shell command -v docker-compose 2> /dev/null)
ifeq ($(DOCKER_COMPOSE_CMD),)
    DOCKER_COMPOSE = docker compose
else
    DOCKER_COMPOSE = docker-compose
endif

# Variables
DOCKER_COMPOSE_DEV = $(DOCKER_COMPOSE) -f docker-compose.dev.yml
APP_CONTAINER = fastapi-auth-app
APP_CONTAINER_DEV = fastapi-auth-app-dev

# Help command
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Docker commands for production
build: ## Build production Docker images
	$(DOCKER_COMPOSE) build

up: ## Start production containers
	$(DOCKER_COMPOSE) up -d

down: ## Stop production containers
	$(DOCKER_COMPOSE) down

logs: ## View production logs
	$(DOCKER_COMPOSE) logs -f

ps: ## List running production containers
	$(DOCKER_COMPOSE) ps

# Docker commands for development
build-dev: ## Build development Docker images
	$(DOCKER_COMPOSE_DEV) build

up-dev: ## Start development containers with hot reload
	$(DOCKER_COMPOSE_DEV) up -d
	@echo "Services started:"
	@echo "  - FastAPI app: http://localhost:8000"
	@echo "  - API docs: http://localhost:8000/docs"
	@echo "  - pgAdmin: http://localhost:5050 (dev@example.com / dev_password)"
	@echo "  - Redis Commander: http://localhost:8081"
	@echo "  - MailHog: http://localhost:8025"

down-dev: ## Stop development containers
	$(DOCKER_COMPOSE_DEV) down

logs-dev: ## View development logs
	$(DOCKER_COMPOSE_DEV) logs -f

# Container management
shell: ## Access app container shell
	docker exec -it $(APP_CONTAINER) /bin/bash

shell-dev: ## Access development app container shell
	docker exec -it $(APP_CONTAINER_DEV) /bin/bash

restart: ## Restart production containers
	$(DOCKER_COMPOSE) restart

restart-dev: ## Restart development containers
	$(DOCKER_COMPOSE_DEV) restart

# Database management
db-shell: ## Access PostgreSQL shell
	docker exec -it fastapi-auth-postgres psql -U auth_user -d auth_db

db-shell-dev: ## Access development PostgreSQL shell
	docker exec -it fastapi-auth-postgres-dev psql -U auth_user -d auth_db

migrate: ## Run database migrations
	docker exec -it $(APP_CONTAINER) alembic upgrade head

migrate-dev: ## Run database migrations in development
	docker exec -it $(APP_CONTAINER_DEV) alembic upgrade head

# Testing
test: ## Run tests in Docker
	docker exec -it $(APP_CONTAINER) pytest

test-dev: ## Run tests in development container
	docker exec -it $(APP_CONTAINER_DEV) pytest -v

test-cov: ## Run tests with coverage in development
	docker exec -it $(APP_CONTAINER_DEV) pytest --cov=app --cov-report=html

# Code quality
lint: ## Run linting in development container
	docker exec -it $(APP_CONTAINER_DEV) flake8 app tests
	docker exec -it $(APP_CONTAINER_DEV) mypy app
	docker exec -it $(APP_CONTAINER_DEV) bandit -r app

format: ## Format code in development container
	docker exec -it $(APP_CONTAINER_DEV) black app tests
	docker exec -it $(APP_CONTAINER_DEV) isort app tests

# Cleanup
clean: ## Clean up containers, volumes, and networks
	$(DOCKER_COMPOSE) down -v --remove-orphans
	$(DOCKER_COMPOSE_DEV) down -v --remove-orphans
	docker system prune -f

clean-all: ## Deep clean including all images
	$(DOCKER_COMPOSE) down -v --remove-orphans --rmi all
	$(DOCKER_COMPOSE_DEV) down -v --remove-orphans --rmi all
	docker system prune -af --volumes

# Development workflow
dev: ## Full development setup
	@make build-dev
	@make up-dev
	@make logs-dev

prod: ## Full production setup
	@make build
	@make up
	@make logs

# Health checks
health: ## Check health of all services
	@echo "Checking production services health..."
	@curl -f http://localhost:8000/health || echo "App health check failed"
	@docker exec fastapi-auth-postgres pg_isready || echo "PostgreSQL health check failed"
	@docker exec fastapi-auth-redis redis-cli ping || echo "Redis health check failed"

health-dev: ## Check health of development services
	@echo "Checking development services health..."
	@curl -f http://localhost:8000/health || echo "App health check failed"
	@docker exec fastapi-auth-postgres-dev pg_isready || echo "PostgreSQL health check failed"
	@docker exec fastapi-auth-redis-dev redis-cli ping || echo "Redis health check failed"

# Docker image management
push: ## Push Docker images to registry
	$(DOCKER_COMPOSE) push

pull: ## Pull Docker images from registry
	$(DOCKER_COMPOSE) pull

# Environment setup
env-example: ## Create example .env file
	@echo "Creating .env.example file..."
	@echo "# FastAPI Authentication Service Environment Variables" > .env.example
	@echo "SECRET_KEY=your-secret-key-here" >> .env.example
	@echo "AUTH0_DOMAIN=your-auth0-domain" >> .env.example
	@echo "AUTH0_CLIENT_ID=your-client-id" >> .env.example
	@echo "AUTH0_CLIENT_SECRET=your-client-secret" >> .env.example
	@echo "AUTH0_AUDIENCE=your-api-audience" >> .env.example
	@echo "DATABASE_URL=postgresql://auth_user:auth_password@postgres:5432/auth_db" >> .env.example
	@echo "REDIS_URL=redis://redis:6379/0" >> .env.example
