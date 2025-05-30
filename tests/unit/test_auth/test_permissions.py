import pytest
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional

from app.core.auth.permissions import (
    check_user_permissions,
    check_user_role,
    RequirePermissions,
    require_role,
    UserPayload # Import UserPayload for type hinting test data
)

# --- Test Data Payloads (based on conftest.py fixtures but simplified for direct use) ---

@pytest.fixture
def user_payload_customer(test_user_data: Dict[str, Any]) -> UserPayload:
    """Simulates a customer user payload."""
    return test_user_data.copy() # roles: ["customer"], perms: ["read:profile", "update:profile"]

@pytest.fixture
def user_payload_provider(test_provider_data: Dict[str, Any]) -> UserPayload:
    """Simulates a provider user payload."""
    return test_provider_data.copy() # roles: ["service_provider"], perms: ["read:services", "create:services", "update:services"]

@pytest.fixture
def user_payload_admin(test_admin_data: Dict[str, Any]) -> UserPayload:
    """Simulates an admin user payload."""
    return test_admin_data.copy() # roles: ["admin"], perms: ["read:users", "update:users", "delete:users"]

@pytest.fixture
def user_payload_no_permissions() -> UserPayload:
    return {"sub": "user_no_perms", "roles": ["customer"], "permissions": []}

@pytest.fixture
def user_payload_no_roles() -> UserPayload:
    return {"sub": "user_no_roles", "roles": [], "permissions": ["read:profile"]}

@pytest.fixture
def user_payload_none_permissions() -> UserPayload:
    return {"sub": "user_none_perms", "roles": ["customer"], "permissions": None} # type: ignore

@pytest.fixture
def user_payload_none_roles() -> UserPayload:
    return {"sub": "user_none_roles", "roles": None, "permissions": ["read:profile"]} # type: ignore

@pytest.fixture
def user_payload_missing_permissions_key() -> UserPayload:
    return {"sub": "user_missing_perms_key", "roles": ["customer"]} # No 'permissions' key

@pytest.fixture
def user_payload_missing_roles_key() -> UserPayload:
    return {"sub": "user_missing_roles_key", "permissions": ["read:profile"]} # No 'roles' key

@pytest.fixture
def user_payload_invalid_permissions_type() -> UserPayload:
    return {"sub": "user_invalid_perms", "roles": ["customer"], "permissions": "not-a-list"} # type: ignore

@pytest.fixture
def user_payload_invalid_roles_type() -> UserPayload:
    return {"sub": "user_invalid_roles", "roles": "not-a-list", "permissions": ["read:profile"]} # type: ignore


# --- Tests for check_user_permissions ---

@pytest.mark.parametrize("required, user_perms, expected", [
    (["read:item"], ["read:item", "write:item"], True),
    (["read:item", "write:item"], ["read:item", "write:item"], True),
    (["read:item"], ["write:item"], False),
    (["read:item", "delete:item"], ["read:item", "write:item"], False),
    ([], ["read:item"], True), # No specific permissions required
    (["read:item"], [], False), # User has no permissions
    ([], [], True), # No required, user has none
])
def test_check_user_permissions(required: List[str], user_perms: List[str], expected: bool):
    assert check_user_permissions(required, user_perms) == expected

# --- Tests for check_user_role ---

@pytest.mark.parametrize("required_role, user_r, expected", [
    ("admin", ["admin", "user"], True),
    ("user", ["admin", "user"], True),
    ("editor", ["admin", "user"], False),
    ("admin", ["admin"], True),
    ("admin", [], False), # User has no roles
    ("", ["admin"], True), # No specific role required (edge case, depends on desired logic)
    ("", [], True), # No role required, user has none
])
def test_check_user_role(required_role: str, user_r: List[str], expected: bool):
    assert check_user_role(required_role, user_r) == expected


# --- Tests for RequirePermissions dependency ---

@pytest.mark.asyncio
async def test_require_permissions_dependency_has_permission(user_payload_customer: UserPayload):
    checker = RequirePermissions(required_permissions=["read:profile"])
    # Simulate FastAPI calling the dependency instance
    result_payload = await checker.__call__(user_payload=user_payload_customer)
    assert result_payload == user_payload_customer

@pytest.mark.asyncio
async def test_require_permissions_dependency_has_all_permissions(user_payload_provider: UserPayload):
    checker = RequirePermissions(required_permissions=["read:services", "create:services"])
    result_payload = await checker.__call__(user_payload=user_payload_provider)
    assert result_payload == user_payload_provider

@pytest.mark.asyncio
async def test_require_permissions_dependency_lacks_permission(user_payload_customer: UserPayload):
    checker = RequirePermissions(required_permissions=["delete:profile"])
    with pytest.raises(HTTPException) as excinfo:
        await checker.__call__(user_payload=user_payload_customer)
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    assert "User lacks required permissions: delete:profile" in excinfo.value.detail

@pytest.mark.asyncio
async def test_require_permissions_dependency_no_user_payload():
    checker = RequirePermissions(required_permissions=["read:item"])
    with pytest.raises(HTTPException) as excinfo:
        await checker.__call__(user_payload=None)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in excinfo.value.detail

@pytest.mark.asyncio
async def test_require_permissions_dependency_user_has_no_permissions(user_payload_no_permissions: UserPayload):
    checker = RequirePermissions(required_permissions=["read:profile"])
    with pytest.raises(HTTPException) as excinfo:
        await checker.__call__(user_payload=user_payload_no_permissions)
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_require_permissions_dependency_user_permissions_is_none(user_payload_none_permissions: UserPayload):
    checker = RequirePermissions(required_permissions=["read:profile"])
    with pytest.raises(HTTPException) as excinfo:
        await checker.__call__(user_payload=user_payload_none_permissions)
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_require_permissions_dependency_user_permissions_key_missing(user_payload_missing_permissions_key: UserPayload):
    checker = RequirePermissions(required_permissions=["read:profile"])
    # The implementation defaults to [] if key is missing, so it should behave like no permissions
    with pytest.raises(HTTPException) as excinfo:
        await checker.__call__(user_payload=user_payload_missing_permissions_key)
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_require_permissions_dependency_invalid_permissions_type(user_payload_invalid_permissions_type: UserPayload):
    checker = RequirePermissions(required_permissions=["read:profile"])
    with pytest.raises(HTTPException) as excinfo:
        await checker.__call__(user_payload=user_payload_invalid_permissions_type)
    assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR # As per current implementation
    assert "Invalid 'permissions' format" in excinfo.value.detail


# --- Tests for require_role functional dependency ---

@pytest.mark.asyncio
async def test_require_role_dependency_has_role(user_payload_admin: UserPayload):
    # Simulate FastAPI calling the dependency function
    result_payload = await require_role(role="admin", user_payload=user_payload_admin)
    assert result_payload == user_payload_admin

@pytest.mark.asyncio
async def test_require_role_dependency_lacks_role(user_payload_customer: UserPayload):
    with pytest.raises(HTTPException) as excinfo:
        await require_role(role="admin", user_payload=user_payload_customer)
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    assert "User lacks required role: admin" in excinfo.value.detail

@pytest.mark.asyncio
async def test_require_role_dependency_no_user_payload():
    with pytest.raises(HTTPException) as excinfo:
        await require_role(role="user", user_payload=None)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_require_role_dependency_user_has_no_roles(user_payload_no_roles: UserPayload):
    with pytest.raises(HTTPException) as excinfo:
        await require_role(role="customer", user_payload=user_payload_no_roles)
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_require_role_dependency_user_roles_is_none(user_payload_none_roles: UserPayload):
    with pytest.raises(HTTPException) as excinfo:
        await require_role(role="customer", user_payload=user_payload_none_roles)
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_require_role_dependency_user_roles_key_missing(user_payload_missing_roles_key: UserPayload):
    # Implementation defaults to [] if key is missing
    with pytest.raises(HTTPException) as excinfo:
        await require_role(role="customer", user_payload=user_payload_missing_roles_key)
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_require_role_dependency_invalid_roles_type(user_payload_invalid_roles_type: UserPayload):
    with pytest.raises(HTTPException) as excinfo:
        await require_role(role="customer", user_payload=user_payload_invalid_roles_type)
    assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR # As per current implementation
    assert "Invalid 'roles' format" in excinfo.value.detail

@pytest.mark.asyncio
async def test_require_permissions_empty_required_allows_any_authed_user(user_payload_customer: UserPayload):
    """If no permissions are required, any authenticated user should pass."""
    checker = RequirePermissions(required_permissions=[])
    result_payload = await checker.__call__(user_payload=user_payload_customer)
    assert result_payload == user_payload_customer

@pytest.mark.asyncio
async def test_require_permissions_empty_required_user_no_permissions(user_payload_no_permissions: UserPayload):
    """If no permissions are required, even a user with no permissions should pass (if authenticated)."""
    checker = RequirePermissions(required_permissions=[])
    result_payload = await checker.__call__(user_payload=user_payload_no_permissions)
    assert result_payload == user_payload_no_permissions
