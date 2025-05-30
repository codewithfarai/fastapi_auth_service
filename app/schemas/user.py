from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole

"""Pydantic schemas for user data validation and serialization.

This module contains the Pydantic models used for:
- Validating user input data
- Serializing user data for API responses
- Managing user creation and updates
"""


class UserBase(BaseModel):
    """Base user schema with common attributes."""

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)


class UserCreate(UserBase):
    """Schema for creating a new user."""

    auth0_id: str = Field(..., min_length=1, max_length=255)
    role: UserRole = UserRole.CUSTOMER


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """Schema for user data in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    auth0_id: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None


class UserResponse(UserInDB):
    """Schema for user response."""

    pass
