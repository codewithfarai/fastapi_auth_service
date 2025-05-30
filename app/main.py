import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import configuration
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 FastAPI Authentication Service starting up...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info("✅ Application startup completed")

    yield

    # Shutdown
    logger.info("🛑 FastAPI Authentication Service shutting down...")
    logger.info("✅ Application shutdown completed")


# Create FastAPI application
app = FastAPI(
    title="FastAPI Authentication Service",
    description="Authentication service with Auth0 integration and role-based access control",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Request/Response logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and responses"""
    start_time = time.time()

    # Log request
    logger.info(f"Incoming request: {request.method} {request.url}")

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url} - "
            f"Status: {response.status_code} - "
            f"Duration: {process_time:.3f}s"
        )

        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url} - "
            f"Error: {str(e)} - "
            f"Duration: {process_time:.3f}s"
        )
        raise


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception for {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "path": str(request.url.path),
            "method": request.method,
        },
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def read_root() -> Dict[str, Any]:
    """
    Root endpoint with service information
    """
    return {
        "service": "FastAPI Authentication Service",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.environment,
        "auth_provider": "Auth0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        },
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring and load balancers

    Returns:
        Dict containing health status information
    """
    try:
        # Basic health indicators
        health_data = {
            "status": "healthy",
            "timestamp": time.time(),
            "environment": settings.environment,
            "version": "1.0.0",
            "uptime": time.time(),  # In a real app, calculate actual uptime
            "checks": {"application": "ok", "configuration": "ok"},
        }

        # Check if critical settings are available
        if not settings.auth0_domain:
            health_data["checks"]["auth0_config"] = "warning - not configured"
        else:
            health_data["checks"]["auth0_config"] = "ok"

        # Overall status
        failed_checks = [k for k, v in health_data["checks"].items() if v != "ok"]
        if failed_checks:
            health_data["status"] = "degraded"
            health_data["issues"] = failed_checks

        logger.info("Health check completed successfully")
        return health_data

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "timestamp": time.time(), "error": str(e)}


# Readiness probe endpoint
@app.get("/ready", tags=["Health"])
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check for Kubernetes deployments

    Returns:
        Dict indicating if the service is ready to receive traffic
    """
    try:
        # Check if application is ready to serve requests
        ready_checks = {"application": True, "configuration": bool(settings.secret_key)}

        all_ready = all(ready_checks.values())

        return {"ready": all_ready, "timestamp": time.time(), "checks": ready_checks}

    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"ready": False, "timestamp": time.time(), "error": str(e)}


# Liveness probe endpoint
@app.get("/live", tags=["Health"])
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check for Kubernetes deployments

    Returns:
        Dict indicating if the service is alive
    """
    return {"alive": True, "timestamp": time.time()}


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting development server...")
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
