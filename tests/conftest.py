import asyncio
import os
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator, Dict, Generator, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings

# from app.core.auth.jwt_handler import JWTVerifier
from app.db.database import Base, get_db
from app.main import app as create_application
from app.models.user import User, UserRole
from app.schemas.user import UserCreate

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_SYNC_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Override settings for testing."""
    return Settings(
        environment="test",
        database_url=TEST_DATABASE_URL,
        secret_key="test-secret-key-for-testing-only",
        auth0_domain="test.auth0.com",
        auth0_api_audience="https://test-api.example.com",
        auth0_algorithms=["RS256"],
        redis_url="redis://localhost:6379/1",
        cors_origins=["http://localhost:3000", "http://testserver"],
        debug=True,
    )


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session_maker = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def app(test_settings, test_db) -> FastAPI:
    """Create test FastAPI application."""

    def override_settings():
        return test_settings

    async def override_get_db():
        yield test_db

    app = create_application()
    app.dependency_overrides[get_settings] = override_settings
    app.dependency_overrides[get_db] = override_get_db

    return app


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_jwt_verifier():
    """Mock JWT verifier for testing."""
    with patch("app.core.auth.jwt_handler.JWTVerifier") as mock:
        verifier = MagicMock()
        mock.return_value = verifier
        yield verifier


@pytest.fixture
def mock_auth0_client(test_user_data): # Added test_user_data
    """Mock Auth0 client for testing."""
    with patch("app.core.auth.auth0_client.Auth0Client") as mock:
        client_instance = AsyncMock()

        # Mock for get_user_info method
        mock_get_user_info = AsyncMock(return_value=test_user_data.copy())
        client_instance.get_user_info = mock_get_user_info

        # Mock for get_public_key method
        # Sample JWKS structure. In a real scenario, 'n' and 'e' would be valid RSA public key components.
        sample_jwks = {
            "keys": [
                {
                    "alg": "RS256",
                    "kty": "RSA",
                    "use": "sig",
                    "kid": "testkey-rs256",
                    "n": "some-modulus-value-n", # In real JWKS, this is a Base64URLUInt-encoded value
                    "e": "AQAB", # In real JWKS, this is a Base64URLUInt-encoded value (exponent)
                }
            ]
        }
        mock_get_public_key = AsyncMock(return_value=sample_jwks)
        client_instance.get_public_key = mock_get_public_key

        # Mock for get_user_by_id method
        mock_get_user_by_id = AsyncMock(return_value=test_user_data.copy())
        client_instance.get_user_by_id = mock_get_user_by_id

        mock.return_value = client_instance
        yield client_instance


@pytest.fixture
def test_user_data() -> Dict[str, any]:
    """Test user data."""
    return {
        "sub": "auth0|123456789",
        "email": "test@example.com",
        "name": "Test User",
        "picture": "https://example.com/picture.jpg",
        "roles": ["customer"],
        "permissions": ["read:profile", "update:profile"],
    }


@pytest.fixture
def test_provider_data() -> Dict[str, any]:
    """Test service provider data."""
    return {
        "sub": "auth0|987654321",
        "email": "provider@example.com",
        "name": "Test Provider",
        "picture": "https://example.com/provider.jpg",
        "roles": ["service_provider"],
        "permissions": ["read:services", "create:services", "update:services"],
    }


@pytest.fixture
def test_admin_data() -> Dict[str, any]:
    """Test admin data."""
    return {
        "sub": "auth0|111111111",
        "email": "admin@example.com",
        "name": "Test Admin",
        "picture": "https://example.com/admin.jpg",
        "roles": ["admin"],
        "permissions": ["read:users", "update:users", "delete:users"],
    }


@pytest.fixture
def create_test_token():
    """Factory for creating test JWT tokens."""

    def _create_token(
        user_data: Dict[str, any],
        expires_delta: Optional[timedelta] = None,
        secret_key: str = "test-secret",
        algorithm: str = "HS256",
    ) -> str:
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(hours=1)

        payload = {
            **user_data,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "iss": "https://test.auth0.com/",
            "aud": "https://test-api.example.com",
        }

        return jwt.encode(payload, secret_key, algorithm=algorithm)

    return _create_token


@pytest.fixture
def auth_headers(create_test_token, test_user_data):
    """Create authorization headers with valid token."""
    token = create_test_token(test_user_data)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def expired_auth_headers(create_test_token, test_user_data):
    """Create authorization headers with an expired token."""
    token = create_test_token(test_user_data, expires_delta=timedelta(seconds=-3600))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def invalid_signature_auth_headers(create_test_token, test_user_data):
    """Create authorization headers with a token signed with a wrong secret key."""
    token = create_test_token(test_user_data, secret_key="wrong-secret-key")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def invalid_issuer_auth_headers(create_test_token, test_user_data):
    """Create authorization headers with a token having an invalid issuer."""
    # The create_test_token normally uses "https://test.auth0.com/"
    # To make it invalid, we need to modify the payload directly after creation,
    # or modify create_test_token to accept an issuer.
    # For simplicity here, let's assume create_test_token can be temporarily adjusted
    # or we craft a token with a different issuer.
    # A more robust way would be to allow create_test_token to take issuer as a parameter.
    # For now, we'll encode it with a bad issuer by overriding the 'iss' in user_data for the token creation.

    custom_user_data = test_user_data.copy()
    # The 'iss' is added inside create_test_token, so we need to modify it there.
    # Let's make a small helper within this fixture for clarity or accept an 'iss' in `create_test_token`.
    # Re-defining a minimal version of create_test_token logic here for custom 'iss'

    payload = {
        **test_user_data,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
        "iss": "https://invalid.auth0.com/", # Invalid issuer
        "aud": "https://test-api.example.com",
    }
    token = jwt.encode(payload, "test-secret", algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def insufficient_permissions_auth_headers(create_test_token, test_user_data):
    """Create authorization headers with a token having insufficient permissions."""
    user_data_insufficient_perms = test_user_data.copy()
    user_data_insufficient_perms["permissions"] = ["read:nothing_important"]
    token = create_test_token(user_data_insufficient_perms)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def missing_roles_auth_headers(create_test_token, test_user_data):
    """Create authorization headers with a token missing roles."""
    user_data_no_roles = test_user_data.copy()
    user_data_no_roles.pop("roles", None) # Remove roles key
    # Alternatively, set roles to empty list: user_data_no_roles["roles"] = []
    token = create_test_token(user_data_no_roles)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def provider_auth_headers(create_test_token, test_provider_data):
    """Create authorization headers for service provider."""
    token = create_test_token(test_provider_data)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(create_test_token, test_admin_data):
    """Create authorization headers for admin."""
    token = create_test_token(test_admin_data)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    with patch("redis.asyncio.Redis") as mock:
        redis_client = AsyncMock()
        redis_client.get = AsyncMock(return_value=None)
        redis_client.set = AsyncMock(return_value=True)
        redis_client.delete = AsyncMock(return_value=1)
        redis_client.exists = AsyncMock(return_value=0)
        redis_client.expire = AsyncMock(return_value=True)
        mock.from_url.return_value = redis_client
        yield redis_client


@pytest.fixture
async def test_customer_user(test_db: AsyncSession) -> User:
    """Create test customer user in database."""
    user = User(
        auth0_id="auth0|123456789",
        email="customer@example.com",
        name="Test Customer",
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
async def test_provider_user(test_db: AsyncSession) -> User:
    """Create test service provider user in database."""
    user = User(
        auth0_id="auth0|987654321",
        email="provider@example.com",
        name="Test Provider",
        role=UserRole.SERVICE_PROVIDER,
        is_active=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
def mock_notification_service():
    """Mock notification service."""
    with patch("app.services.notification_service.NotificationService") as mock:
        service = AsyncMock()
        service.send_email = AsyncMock(return_value=True)
        service.send_sms = AsyncMock(return_value=True)
        mock.return_value = service
        yield service
