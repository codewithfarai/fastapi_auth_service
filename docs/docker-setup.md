# Docker Setup Guide

This guide covers the Docker setup for the FastAPI Authentication Service, including development and production configurations.

## Overview

The Docker setup includes:
- Multi-stage Dockerfile for optimized builds
- Development and production Docker Compose configurations
- PostgreSQL database
- Redis cache
- Development tools (pgAdmin, Redis Commander, MailHog)
- Health checks for all services
- Makefile for easy management

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Make (optional, for using Makefile commands)

### WSL2 Setup (Windows Users)

If you're using WSL2 on Windows, follow these steps:

1. **Install Docker Desktop for Windows**:
   - Download from [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Install and restart your computer

2. **Enable WSL2 Integration**:
   - Open Docker Desktop Settings
   - Go to Resources → WSL Integration
   - Enable integration with your WSL2 distro
   - Apply & Restart

3. **Verify Installation**:
   ```bash
   # In WSL2 terminal
   docker --version
   docker compose version
   ```

4. **Common WSL2 Issues**:
   - If `docker` command not found: Restart WSL2 terminal after enabling integration
   - Permission issues: Add your user to docker group: `sudo usermod -aG docker $USER`
   - Performance: Store project files in WSL2 filesystem (`/home/user/`) not Windows filesystem (`/mnt/c/`)

## Quick Start

### Development Environment

1. Create a `.env` file from the example:
```bash
make env-example
cp .env.example .env
```

2. Start the development environment:
```bash
make dev
```

This will:
- Build the development Docker images
- Start all services with hot reload
- Display service URLs
- Show logs

3. Access the services:
- FastAPI app: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- pgAdmin: http://localhost:5050 (dev@example.com / dev_password)
- Redis Commander: http://localhost:8081
- MailHog: http://localhost:8025

### Production Environment

1. Set up production environment variables:
```bash
export SECRET_KEY="your-production-secret-key"
export AUTH0_DOMAIN="your-auth0-domain"
# ... other production variables
```

2. Start production services:
```bash
make prod
```

## Docker Configuration

### Dockerfile

The multi-stage Dockerfile includes:

1. **python-base**: Base Python 3.12 slim image with system dependencies
2. **poetry-base**: Poetry installation stage
3. **development**: Full development environment with all dependencies
4. **production-deps**: Production dependencies only
5. **production**: Optimized production image with non-root user

### Docker Compose Files

#### docker-compose.yml (Production)
- FastAPI application with 4 workers
- PostgreSQL 16 with persistent storage
- Redis 7 with authentication
- Proper health checks
- Secure networking

#### docker-compose.dev.yml (Development)
- FastAPI with hot reload
- Volume mounts for live code updates
- Additional development tools
- Debug-friendly configuration

## Available Commands

### Basic Operations

```bash
# Development
make build-dev      # Build development images
make up-dev         # Start development containers
make down-dev       # Stop development containers
make logs-dev       # View development logs
make restart-dev    # Restart development containers

# Production
make build          # Build production images
make up             # Start production containers
make down           # Stop production containers
make logs           # View production logs
make restart        # Restart production containers
```

### Container Access

```bash
make shell-dev      # Access development app container
make shell          # Access production app container
make db-shell-dev   # Access development PostgreSQL
make db-shell       # Access production PostgreSQL
```

### Testing & Quality

```bash
make test-dev       # Run tests in development
make test-cov       # Run tests with coverage
make lint           # Run linting checks
make format         # Format code
```

### Health Checks

```bash
make health-dev     # Check development services
make health         # Check production services
```

### Cleanup

```bash
make clean          # Clean up containers and volumes
make clean-all      # Deep clean including images
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| SECRET_KEY | JWT signing key | `your-secret-key` |
| DATABASE_URL | PostgreSQL connection | `postgresql://user:pass@host:5432/db` |
| REDIS_URL | Redis connection | `redis://redis:6379/0` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| ENVIRONMENT | Environment name | `development` |
| DEBUG | Debug mode | `false` |
| AUTH0_DOMAIN | Auth0 domain | - |
| AUTH0_CLIENT_ID | Auth0 client ID | - |
| AUTH0_CLIENT_SECRET | Auth0 client secret | - |
| AUTH0_AUDIENCE | Auth0 API audience | - |

## Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Check if ports are in use
   lsof -i :8000
   lsof -i :5432
   lsof -i :6379
   ```

2. **Container won't start**
   ```bash
   # Check logs
   make logs-dev

   # Check container status
   docker-compose -f docker-compose.dev.yml ps
   ```

3. **Database connection issues**
   ```bash
   # Verify database is running
   make health-dev

   # Check database logs
   docker logs fastapi-auth-postgres-dev
   ```

4. **Permission issues**
   ```bash
   # Fix ownership
   sudo chown -R $USER:$USER .
   ```

### Debugging

1. **Enable debug logging**:
   - Set `DEBUG=true` in `.env`
   - Restart containers: `make restart-dev`

2. **Access container shell**:
   ```bash
   make shell-dev
   # Inside container
   python -m app.main
   ```

3. **Check service health**:
   ```bash
   curl http://localhost:8000/health
   ```

## Best Practices

1. **Development**:
   - Use `docker-compose.dev.yml` for local development
   - Mount code volumes for hot reload
   - Use development tools (pgAdmin, Redis Commander)

2. **Production**:
   - Always use specific image tags
   - Set strong passwords and secrets
   - Enable Redis authentication
   - Use health checks for orchestration
   - Run as non-root user

3. **Security**:
   - Never commit `.env` files
   - Use secrets management in production
   - Regularly update base images
   - Scan images for vulnerabilities

## Performance Optimization

1. **Build optimization**:
   - Use `.dockerignore` to exclude unnecessary files
   - Leverage Docker build cache
   - Use multi-stage builds

2. **Runtime optimization**:
   - Set appropriate worker counts
   - Configure connection pools
   - Use volume mount options (`:delegated` for macOS)

## Deployment

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml fastapi-auth
```

### Using Kubernetes

See `deployment/k8s/` for Kubernetes manifests.

## Monitoring

The setup includes health endpoints:
- `/health` - Application health
- `/ready` - Readiness probe
- `/live` - Liveness probe

Use these with your monitoring solution (Prometheus, Datadog, etc.).

## Updates and Maintenance

1. **Update dependencies**:
   ```bash
   # Update Poetry lock file
   poetry update

   # Rebuild images
   make build-dev
   ```

2. **Database migrations**:
   ```bash
   make migrate-dev
   ```

3. **Backup data**:
   ```bash
   # Backup PostgreSQL
   docker exec fastapi-auth-postgres-dev pg_dump -U auth_user auth_db > backup.sql
   ```

## Support

For issues or questions:
1. Check the logs: `make logs-dev`
2. Verify health: `make health-dev`
3. Review this documentation
4. Check Docker and Docker Compose documentation
