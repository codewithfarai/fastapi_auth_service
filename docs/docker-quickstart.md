# Docker Quick Start & Usage Guide

## 🚀 Getting Started in 3 Steps

```bash
# 1. Ensure Docker Desktop is running (Windows/Mac)

# 2. Set up environment
make env-example
cp .env.example .env

# 3. Start development
make dev
```

## 📍 Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| FastAPI App | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| pgAdmin | http://localhost:5050 | dev@example.com / dev_password |
| Redis Commander | http://localhost:8081 | - |
| MailHog | http://localhost:8025 | - |

## 🎯 Common Workflows

### Starting Your Day
```bash
# Start all services
make up-dev

# Check everything is running
make ps
make health-dev

# View logs in separate terminal
make logs-dev
```

### During Development
```bash
# Your code auto-reloads on save!
# Just edit files in app/ directory

# Access container for debugging
make shell-dev

# Check logs for errors
make logs-dev | grep ERROR
```

### Running Tests
```bash
# Quick test run
make test-dev

# With coverage report
make test-cov

# Run specific test
docker exec -it fastapi-auth-app-dev pytest tests/test_main.py -v
```

### Database Tasks
```bash
# PostgreSQL shell
make db-shell-dev

# Common SQL commands
SELECT * FROM users;
\dt                    # List all tables
\d+ table_name        # Describe table
\q                    # Exit

# Run migrations
make migrate-dev
```

### Ending Your Day
```bash
# Stop all services
make down-dev

# Or keep data and just stop
docker compose -f docker-compose.dev.yml stop
```

## 🛠️ Troubleshooting

### Container Won't Start
```bash
# Check what's running
docker ps -a

# View detailed logs
docker logs fastapi-auth-app-dev

# Rebuild if needed
make build-dev
```

### Port Already in Use
```bash
# Find what's using the port
lsof -i :8000  # or :5432, :6379

# Kill the process
kill -9 <PID>

# Or change the port in docker-compose.dev.yml
```

### Database Connection Issues
```bash
# Verify PostgreSQL is healthy
docker exec fastapi-auth-postgres-dev pg_isready

# Check connection from app
make shell-dev
python -c "from app.config import settings; print(settings.DATABASE_URL)"
```

### Clean Start
```bash
# Remove everything and start fresh
make clean
make dev
```

## 🔑 Environment Variables

Edit `.env` file for configuration:

```env
# Development defaults (already set)
SECRET_KEY=dev-secret-key-not-for-production
DATABASE_URL=postgresql://auth_user:auth_password@postgres:5432/auth_db
REDIS_URL=redis://redis:6379/0

# Add your Auth0 config (optional)
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_CLIENT_ID=your-client-id
```

## 📝 Quick Tips

1. **Hot Reload**: Code changes in `app/` directory automatically reload
2. **Logs**: Always check logs when something goes wrong: `make logs-dev`
3. **Shell Access**: Use `make shell-dev` to debug inside container
4. **Database GUI**: Use pgAdmin at http://localhost:5050 for visual DB management
5. **Email Testing**: All emails go to MailHog at http://localhost:8025

## 🚨 Emergency Commands

```bash
# Everything is broken, start over
make clean-all
make dev

# Can't connect to Docker
docker info  # Check Docker daemon
# Restart Docker Desktop if needed

# Remove all Docker data (nuclear option)
docker system prune -af --volumes
```
