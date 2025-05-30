import pytest
import httpx

from app.core.auth.auth0_client import Auth0Client
from app.config import Settings # Settings is used by Auth0Client
# test_settings fixture will be automatically injected by pytest if defined in conftest.py

# A sample JWKS for mocking responses
SAMPLE_JWKS = {"keys": [{"kid": "test_kid_123", "kty": "RSA", "use": "sig", "n": "some_modulus", "e": "AQAB"}]}
USER_INFO_SAMPLE = {"sub": "auth0|123456789", "email": "test@example.com", "name": "Test User"}

# Test get_public_key
async def test_get_public_key_success(test_settings: Settings, httpx_mock):
    auth0_client = Auth0Client(settings=test_settings)
    httpx_mock.add_response(url=auth0_client.jwks_url, json=SAMPLE_JWKS)

    jwks = await auth0_client.get_public_key()
    assert jwks == SAMPLE_JWKS

async def test_get_public_key_http_error(test_settings: Settings, httpx_mock):
    auth0_client = Auth0Client(settings=test_settings)
    httpx_mock.add_response(url=auth0_client.jwks_url, status_code=500)

    with pytest.raises(httpx.HTTPStatusError) as excinfo:
        await auth0_client.get_public_key()
    assert excinfo.value.response.status_code == 500

async def test_get_public_key_request_error(test_settings: Settings, httpx_mock):
    auth0_client = Auth0Client(settings=test_settings)
    def raise_connect_error(request, extensions):
        raise httpx.ConnectError("Connection failed", request=request)

    httpx_mock.add_callback(raise_connect_error, url=auth0_client.jwks_url)

    with pytest.raises(httpx.RequestError): # More specifically httpx.ConnectError
        await auth0_client.get_public_key()

# Test get_user_info
async def test_get_user_info_success(test_settings: Settings, httpx_mock):
    auth0_client = Auth0Client(settings=test_settings)
    token = "test_access_token"
    httpx_mock.add_response(url=auth0_client.userinfo_url, json=USER_INFO_SAMPLE)

    user_info = await auth0_client.get_user_info(token=token)
    assert user_info == USER_INFO_SAMPLE
    # Check if headers were passed (optional, httpx_mock usually allows inspecting the request)
    request = httpx_mock.get_requests()[0]
    assert request.headers["Authorization"] == f"Bearer {token}"


async def test_get_user_info_http_error(test_settings: Settings, httpx_mock):
    auth0_client = Auth0Client(settings=test_settings)
    token = "test_access_token"
    httpx_mock.add_response(url=auth0_client.userinfo_url, status_code=401)

    with pytest.raises(httpx.HTTPStatusError) as excinfo:
        await auth0_client.get_user_info(token=token)
    assert excinfo.value.response.status_code == 401

async def test_get_user_info_request_error(test_settings: Settings, httpx_mock):
    auth0_client = Auth0Client(settings=test_settings)
    token = "test_access_token"
    def raise_connect_error(request, extensions):
        raise httpx.ConnectError("Connection failed", request=request)

    httpx_mock.add_callback(raise_connect_error, url=auth0_client.userinfo_url)

    with pytest.raises(httpx.RequestError): # More specifically httpx.ConnectError
        await auth0_client.get_user_info(token=token)

# Test get_user_by_id (testing the placeholder implementation)
async def test_get_user_by_id_success(test_settings: Settings, httpx_mock): # httpx_mock not strictly needed due to current placeholder
    auth0_client = Auth0Client(settings=test_settings)
    user_id = "auth0|123456789"

    # The current implementation of get_user_by_id does not use httpx_mock for success path
    # if it did, we would mock the management_api_url like:
    # expected_response = {"sub": user_id, "email": "test@example.com", "name": "Test User From API"}
    # httpx_mock.add_response(url=f"{auth0_client.base_url}/api/v2/users/{user_id}", json=expected_response)

    user_data = await auth0_client.get_user_by_id(user_id)
    assert user_data == {"sub": user_id, "email": "test@example.com", "name": "Test User From API"}

async def test_get_user_by_id_not_found(test_settings: Settings, httpx_mock): # httpx_mock not strictly needed
    auth0_client = Auth0Client(settings=test_settings)
    user_id = "auth0|unknown_user"

    # The current implementation of get_user_by_id raises HTTPStatusError directly for not found
    # if it used httpx for a real call that returned 404, the mock would be:
    # httpx_mock.add_response(url=f"{auth0_client.base_url}/api/v2/users/{user_id}", status_code=404)

    with pytest.raises(httpx.HTTPStatusError) as excinfo:
        await auth0_client.get_user_by_id(user_id)

    assert excinfo.value.response.status_code == 404
    assert str(excinfo.value.request.url) == f"{auth0_client.base_url}/api/v2/users/{user_id}"

# Test __init__ method for correct URL setup
def test_auth0_client_init(test_settings: Settings):
    client = Auth0Client(settings=test_settings)
    expected_base_url = f"https://{test_settings.auth0_domain}"
    assert client.base_url == expected_base_url
    assert client.jwks_url == f"{expected_base_url}/.well-known/jwks.json"
    assert client.userinfo_url == f"{expected_base_url}/userinfo"

    # Test with default settings (requires mocking get_settings or ensuring it runs in test mode)
    # This is more complex to set up if Depends(get_settings) is used directly in __init__
    # For now, always passing test_settings is simpler and more common for unit tests.
    # If get_settings() was called inside methods, it would be easier to mock.
    # Since it's in __init__ default, direct instantiation `Auth0Client()` would try to use live settings.
    # Test cases here always provide `test_settings`, so this is fine.
