import pytest
from unittest.mock import AsyncMock, MagicMock # AsyncMock for repo, MagicMock for JWTHandler
from fastapi import HTTPException, status
import httpx # For simulating Auth0 client errors

from app.services.auth_service import AuthService
from app.core.auth.auth0_client import Auth0Client # For type hinting mock_auth0_client
from app.core.auth.jwt_handler import JWTHandler
from app.db.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User as UserModel, UserRole # SQLAlchemy model
from app.config import Settings


@pytest.fixture
def mock_jwt_handler_service() -> MagicMock: # JWTHandler methods are sync
    mock = MagicMock(spec=JWTHandler)
    mock.encode_token.return_value = "test.internal.token"
    # decode_token will be configured per test
    return mock

@pytest.fixture
def mock_user_repository_service() -> AsyncMock:
    mock = AsyncMock(spec=UserRepository)
    # get_user_by_auth0_id, create_user, get_user_by_id will be configured per test
    return mock

@pytest.fixture
def auth_service(
    mock_auth0_client: Auth0Client, # This is already AsyncMock from conftest.py
    mock_jwt_handler_service: MagicMock,
    mock_user_repository_service: AsyncMock,
    test_settings: Settings
) -> AuthService:
    return AuthService(
        auth0_client=mock_auth0_client,
        jwt_handler=mock_jwt_handler_service,
        user_repository=mock_user_repository_service,
        settings=test_settings
    )

# --- Tests for login_or_register_via_auth0 ---

@pytest.mark.asyncio
async def test_login_or_register_existing_user(
    auth_service: AuthService,
    mock_auth0_client: AsyncMock, # Use specific mock for configuration ease
    mock_user_repository_service: AsyncMock,
    mock_jwt_handler_service: MagicMock,
    test_user_data: dict # Auth0 response
):
    # Arrange
    auth0_token = "valid.auth0.token"

    # Mock Auth0 client
    mock_auth0_client.get_user_info = AsyncMock(return_value=test_user_data.copy())

    # Mock UserRepository to return an existing user
    existing_user_model = UserModel(
        id=1,
        auth0_id=test_user_data["sub"],
        email=test_user_data["email"],
        name=test_user_data["name"],
        role=UserRole.CUSTOMER # from test_user_data's roles
    )
    mock_user_repository_service.get_user_by_auth0_id = AsyncMock(return_value=existing_user_model)

    # Act
    internal_token, user_response = await auth_service.login_or_register_via_auth0(auth0_token)

    # Assert
    mock_auth0_client.get_user_info.assert_called_once_with(auth0_token)
    mock_user_repository_service.get_user_by_auth0_id.assert_called_once_with(test_user_data["sub"])
    mock_user_repository_service.create_user.assert_not_called() # Should not create new user

    expected_token_payload = {
        "sub": str(existing_user_model.id),
        "roles": [existing_user_model.role.value],
        "permissions": test_user_data.get("permissions", [])
    }
    mock_jwt_handler_service.encode_token.assert_called_once_with(expected_token_payload)
    assert internal_token == "test.internal.token"

    assert user_response.id == existing_user_model.id
    assert user_response.email == existing_user_model.email
    assert user_response.auth0_id == existing_user_model.auth0_id

@pytest.mark.asyncio
async def test_login_or_register_new_user(
    auth_service: AuthService,
    mock_auth0_client: AsyncMock,
    mock_user_repository_service: AsyncMock,
    mock_jwt_handler_service: MagicMock,
    test_user_data: dict # Auth0 response
):
    # Arrange
    auth0_token = "valid.auth0.token.new.user"
    auth0_user_info = test_user_data.copy()
    auth0_user_info["name"] = "New Test User" # Ensure it uses data from Auth0

    mock_auth0_client.get_user_info = AsyncMock(return_value=auth0_user_info)

    # Mock UserRepository: no existing user, then successful creation
    mock_user_repository_service.get_user_by_auth0_id = AsyncMock(return_value=None)

    newly_created_user_model = UserModel(
        id=2, # New ID
        auth0_id=auth0_user_info["sub"],
        email=auth0_user_info["email"],
        name=auth0_user_info["name"],
        role=UserRole.CUSTOMER # Default or mapped from auth0_user_info["roles"]
    )
    mock_user_repository_service.create_user = AsyncMock(return_value=newly_created_user_model)

    # Act
    internal_token, user_response = await auth_service.login_or_register_via_auth0(auth0_token)

    # Assert
    mock_auth0_client.get_user_info.assert_called_once_with(auth0_token)
    mock_user_repository_service.get_user_by_auth0_id.assert_called_once_with(auth0_user_info["sub"])

    # Check that create_user was called with correct UserCreate data
    # The role mapping in AuthService is basic, assumes "customer" if not admin from auth0_roles
    # test_user_data has "roles": ["customer"]
    expected_user_create_arg = UserCreate(
        auth0_id=auth0_user_info["sub"],
        email=auth0_user_info["email"],
        name=auth0_user_info["name"],
        role=UserRole.CUSTOMER # Based on logic in AuthService and test_user_data
    )
    mock_user_repository_service.create_user.assert_called_once()
    # Deep comparison of Pydantic models can be tricky with mocks. Check key fields.
    call_arg = mock_user_repository_service.create_user.call_args[0][0]
    assert call_arg.auth0_id == expected_user_create_arg.auth0_id
    assert call_arg.email == expected_user_create_arg.email
    assert call_arg.name == expected_user_create_arg.name
    assert call_arg.role == expected_user_create_arg.role

    expected_token_payload = {
        "sub": str(newly_created_user_model.id),
        "roles": [newly_created_user_model.role.value],
        "permissions": auth0_user_info.get("permissions", [])
    }
    mock_jwt_handler_service.encode_token.assert_called_once_with(expected_token_payload)
    assert internal_token == "test.internal.token"

    assert user_response.id == newly_created_user_model.id
    assert user_response.email == newly_created_user_model.email
    assert user_response.name == newly_created_user_model.name


@pytest.mark.asyncio
async def test_login_or_register_auth0_info_fetch_fails(auth_service: AuthService, mock_auth0_client: AsyncMock):
    auth0_token = "invalid.auth0.token"
    # Simulate Auth0 client raising an HTTP error (e.g., 401 from Auth0)
    mock_auth0_client.get_user_info = AsyncMock(
        side_effect=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Auth0 said no")
    )

    with pytest.raises(HTTPException) as excinfo:
        await auth_service.login_or_register_via_auth0(auth0_token)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Auth0 validation failed: Auth0 said no" in excinfo.value.detail

@pytest.mark.asyncio
async def test_login_or_register_auth0_info_fetch_network_error(auth_service: AuthService, mock_auth0_client: AsyncMock):
    auth0_token = "valid.auth0.token.network.error"
    # Simulate Auth0 client raising a non-HTTPException (e.g. httpx.RequestError)
    mock_auth0_client.get_user_info = AsyncMock(
        side_effect=httpx.ConnectError("Connection to Auth0 failed", request=None) # type: ignore
    )

    with pytest.raises(HTTPException) as excinfo:
        await auth_service.login_or_register_via_auth0(auth0_token)

    assert excinfo.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Failed to fetch user info from Auth0: Connection to Auth0 failed" in excinfo.value.detail


@pytest.mark.asyncio
async def test_login_or_register_auth0_sub_missing(auth_service: AuthService, mock_auth0_client: AsyncMock, test_user_data: dict):
    auth0_token = "auth0.token.no.sub"
    auth0_user_info_no_sub = test_user_data.copy()
    del auth0_user_info_no_sub["sub"]
    mock_auth0_client.get_user_info = AsyncMock(return_value=auth0_user_info_no_sub)

    with pytest.raises(HTTPException) as excinfo:
        await auth_service.login_or_register_via_auth0(auth0_token)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Auth0 user ID (sub) missing" in excinfo.value.detail

@pytest.mark.asyncio
async def test_login_or_register_new_user_email_missing(
    auth_service: AuthService, mock_auth0_client: AsyncMock, test_user_data: dict
):
    auth0_token = "auth0.token.new.user.no.email"
    auth0_user_info_no_email = test_user_data.copy()
    del auth0_user_info_no_email["email"] # Remove email

    mock_auth0_client.get_user_info = AsyncMock(return_value=auth0_user_info_no_email)
    mock_user_repository_service.get_user_by_auth0_id = AsyncMock(return_value=None) # New user

    with pytest.raises(HTTPException) as excinfo:
        await auth_service.login_or_register_via_auth0(auth0_token)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email missing in Auth0 user data" in excinfo.value.detail


@pytest.mark.asyncio
async def test_login_or_register_db_create_user_fails(
    auth_service: AuthService, mock_auth0_client: AsyncMock, mock_user_repository_service: AsyncMock, test_user_data: dict
):
    auth0_token = "auth0.token.db.fail"
    mock_auth0_client.get_user_info = AsyncMock(return_value=test_user_data.copy())
    mock_user_repository_service.get_user_by_auth0_id = AsyncMock(return_value=None) # New user
    mock_user_repository_service.create_user = AsyncMock(side_effect=Exception("DB unique constraint failed")) # Simulate DB error

    with pytest.raises(HTTPException) as excinfo:
        await auth_service.login_or_register_via_auth0(auth0_token)
    assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Could not create user: DB unique constraint failed" in excinfo.value.detail


# --- Tests for get_user_from_internal_token ---

@pytest.mark.asyncio
async def test_get_user_from_internal_token_success(
    auth_service: AuthService, mock_jwt_handler_service: MagicMock, mock_user_repository_service: AsyncMock
):
    internal_token = "valid.internal.token"
    decoded_payload = {"sub": "1", "roles": ["customer"], "permissions": []}
    mock_jwt_handler_service.decode_token = MagicMock(return_value=decoded_payload)

    expected_user = UserModel(id=1, email="user@example.com", name="Test User", role=UserRole.CUSTOMER)
    mock_user_repository_service.get_user_by_id = AsyncMock(return_value=expected_user)

    user_response = await auth_service.get_user_from_internal_token(internal_token)

    mock_jwt_handler_service.decode_token.assert_called_once_with(internal_token)
    mock_user_repository_service.get_user_by_id.assert_called_once_with(1) # user_id from payload "sub"
    assert user_response.id == expected_user.id
    assert user_response.email == expected_user.email

@pytest.mark.asyncio
async def test_get_user_from_internal_token_decode_fails_http_exception(
    auth_service: AuthService, mock_jwt_handler_service: MagicMock
):
    internal_token = "expired.internal.token"
    # Simulate JWTHandler raising its own HTTPException (e.g., for expired token)
    mock_jwt_handler_service.decode_token = MagicMock(
        side_effect=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired.")
    )

    with pytest.raises(HTTPException) as excinfo:
        await auth_service.get_user_from_internal_token(internal_token)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Token has expired" in excinfo.value.detail

@pytest.mark.asyncio
async def test_get_user_from_internal_token_decode_fails_general_exception(
    auth_service: AuthService, mock_jwt_handler_service: MagicMock
):
    internal_token = "malformed.internal.token"
    # Simulate JWTHandler raising a generic JWTError
    mock_jwt_handler_service.decode_token = MagicMock(side_effect=JWTError("Some JWT parsing error")) # type: ignore

    with pytest.raises(HTTPException) as excinfo:
        await auth_service.get_user_from_internal_token(internal_token)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid internal token: Some JWT parsing error" in excinfo.value.detail


@pytest.mark.asyncio
async def test_get_user_from_internal_token_payload_sub_missing(
    auth_service: AuthService, mock_jwt_handler_service: MagicMock
):
    internal_token = "token.no.sub"
    decoded_payload_no_sub = {"roles": ["customer"]} # No "sub"
    mock_jwt_handler_service.decode_token = MagicMock(return_value=decoded_payload_no_sub)

    with pytest.raises(HTTPException) as excinfo:
        await auth_service.get_user_from_internal_token(internal_token)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid internal token payload: 'sub' missing" in excinfo.value.detail

@pytest.mark.asyncio
async def test_get_user_from_internal_token_sub_not_int(
    auth_service: AuthService, mock_jwt_handler_service: MagicMock
):
    internal_token = "token.sub.not.int"
    decoded_payload_sub_not_int = {"sub": "not-an-integer", "roles": ["customer"]}
    mock_jwt_handler_service.decode_token = MagicMock(return_value=decoded_payload_sub_not_int)

    with pytest.raises(HTTPException) as excinfo:
        await auth_service.get_user_from_internal_token(internal_token)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid user ID format in token subject" in excinfo.value.detail


@pytest.mark.asyncio
async def test_get_user_from_internal_token_user_not_found_in_db(
    auth_service: AuthService, mock_jwt_handler_service: MagicMock, mock_user_repository_service: AsyncMock
):
    internal_token = "valid.token.user.not.found"
    decoded_payload = {"sub": "999", "roles": ["customer"]} # User ID 999
    mock_jwt_handler_service.decode_token = MagicMock(return_value=decoded_payload)
    mock_user_repository_service.get_user_by_id = AsyncMock(return_value=None) # User not found

    with pytest.raises(HTTPException) as excinfo:
        await auth_service.get_user_from_internal_token(internal_token)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "User not found for token" in excinfo.value.detail
from jose import JWTError # Add this import if not already present at the top
