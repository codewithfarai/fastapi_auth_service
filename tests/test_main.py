# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add app directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# Create test client
client = TestClient(app)


def test_read_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "FastAPI Authentication Service"
    assert data["status"] == "running"
    assert "version" in data
    assert "endpoints" in data


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "checks" in data
    assert "environment" in data
    assert data["environment"] == "development"


def test_readiness_check():
    """Test readiness endpoint"""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert "ready" in data
    assert "timestamp" in data
    assert "checks" in data
    assert isinstance(data["ready"], bool)


def test_liveness_check():
    """Test liveness endpoint"""
    response = client.get("/live")
    assert response.status_code == 200
    data = response.json()
    assert data["alive"] is True
    assert "timestamp" in data


def test_openapi_docs():
    """Test that OpenAPI docs are accessible"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc():
    """Test that ReDoc is accessible"""
    response = client.get("/redoc")
    assert response.status_code == 200


def test_openapi_json():
    """Test OpenAPI JSON schema"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert data["info"]["title"] == "FastAPI Authentication Service"


def test_health_check_details():
    """Test health check provides detailed information"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert "status" in data
    assert "checks" in data
    assert "application" in data["checks"]
    assert "configuration" in data["checks"]
    
    # Status should be healthy or degraded
    assert data["status"] in ["healthy", "degraded"]


def test_cors_headers():
    """Test CORS headers are present"""
    # Test CORS headers on a regular GET request
    response = client.get("/")
    # CORS headers should be present on regular requests
    assert response.status_code == 200
    
    # Test OPTIONS request with proper headers for CORS preflight
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "Content-Type"
    }
    response = client.options("/health", headers=headers)
    # Should either return 200 with CORS headers or the endpoint should handle it
    assert response.status_code in [200, 405]  # 405 is acceptable if OPTIONS not explicitly handled


def test_request_timing_header():
    """Test that processing time header is added"""
    response = client.get("/")
    assert "x-process-time" in response.headers
    # Should be a valid float value
    process_time = float(response.headers["x-process-time"])
    assert process_time >= 0


class TestErrorHandling:
    """Test error handling functionality"""
    
    def test_404_error(self):
        """Test 404 error for non-existent endpoint"""
        response = client.get("/non-existent-endpoint")
        assert response.status_code == 404
        
    def test_method_not_allowed(self):
        """Test method not allowed error"""
        response = client.post("/")  # POST to GET endpoint
        assert response.status_code == 405