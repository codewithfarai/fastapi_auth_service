"""
User-specific test fixtures.
"""
from datetime import datetime
from typing import List

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.schemas.user import UserCreate


@pytest.fixture
def user_create_data() -> UserCreate:
    """User creation data."""
    return UserCreate(
        email="newuser@example.com",
        name="New User",
        role=UserRole.CUSTOMER,
        auth0_id="auth0|newuser123",
    )


@pytest.fixture
def batch_users_data() -> List[Dict[str, any]]:
    """Batch user data for testing."""
    return [
        {
            "auth0_id": f"auth0|user{i}",
            "email": f"user{i}@example.com",
            "name": f"Test User {i}",
            "role": UserRole.CUSTOMER if i % 2 == 0 else UserRole.SERVICE_PROVIDER,
            "is_active": True,
        }
        for i in range(10)
    ]


@pytest.fixture
async def populate_users(test_db: AsyncSession, batch_users_data):
    """Populate database with test users."""
    users = []
    for user_data in batch_users_data:
        user = User(**user_data)
        test_db.add(user)
        users.append(user)
    
    await test_db.commit()
    return users


@pytest.fixture
def mock_user_service():
    """Mock user service."""
    from unittest.mock import AsyncMock
    
    service = AsyncMock()
    service.get_by_auth0_id = AsyncMock()
    service.create = AsyncMock()
    service.update = AsyncMock()
    service.delete = AsyncMock()
    service.list_users = AsyncMock()
    
    return service
