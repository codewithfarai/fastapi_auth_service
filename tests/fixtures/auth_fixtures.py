"""
Authentication-specific test fixtures.
"""
from datetime import datetime, timedelta, timezone
from typing import Dict
from unittest.mock import MagicMock

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwt


@pytest.fixture
def rsa_key_pair():
    """Generate RSA key pair for testing JWT signatures."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    return private_pem, public_pem


@pytest.fixture
def mock_jwks_response(rsa_key_pair):
    """Mock JWKS endpoint response."""
    _, public_key = rsa_key_pair
    
    # Convert public key to JWK format
    from jose import jwk
    key_data = jwk.construct(public_key, algorithm="RS256")
    
    return {
        "keys": [
            {
                **key_data.to_dict(),
                "kid": "test-key-id",
                "use": "sig",
                "alg": "RS256",
            }
        ]
    }


@pytest.fixture
def create_signed_token(rsa_key_pair):
    """Create properly signed JWT token."""
    private_key, _ = rsa_key_pair
    
    def _create_token(
        claims: Dict[str, any],
        kid: str = "test-key-id",
        expires_in: int = 3600,
    ) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            **claims,
            "exp": now + timedelta(seconds=expires_in),
            "iat": now,
            "iss": "https://test.auth0.com/",
            "aud": "https://test-api.example.com",
        }
        
        headers = {"kid": kid}
        
        return jwt.encode(
            payload,
            private_key,
            algorithm="RS256",
            headers=headers
        )
    
    return _create_token


@pytest.fixture
def expired_token(create_signed_token, test_user_data):
    """Create expired JWT token."""
    return create_signed_token(test_user_data, expires_in=-3600)


@pytest.fixture
def invalid_audience_token(create_signed_token, test_user_data):
    """Create token with invalid audience."""
    claims = {**test_user_data, "aud": "https://wrong-api.example.com"}
    return create_signed_token(claims)


@pytest.fixture
def invalid_issuer_token(create_signed_token, test_user_data):
    """Create token with invalid issuer."""
    claims = {**test_user_data, "iss": "https://wrong.auth0.com/"}
    return create_signed_token(claims)


@pytest.fixture
def malformed_token():
    """Create malformed JWT token."""
    return "not.a.valid.jwt.token"


@pytest.fixture
def mock_auth0_management_api():
    """Mock Auth0 Management API responses."""
    mock_api = MagicMock()
    
    # Mock user management
    mock_api.get_user = MagicMock(return_value={
        "user_id": "auth0|123456789",
        "email": "test@example.com",
        "name": "Test User",
        "app_metadata": {
            "roles": ["customer"],
            "permissions": ["read:profile", "update:profile"]
        }
    })
    
    mock_api.update_user = MagicMock(return_value={"success": True})
    mock_api.delete_user = MagicMock(return_value={"success": True})
    
    # Mock role management
    mock_api.get_user_roles = MagicMock(return_value=[
        {"id": "rol_123", "name": "customer", "description": "Customer role"}
    ])
    
    mock_api.assign_roles_to_user = MagicMock(return_value={"success": True})
    mock_api.remove_roles_from_user = MagicMock(return_value={"success": True})
    
    return mock_api
