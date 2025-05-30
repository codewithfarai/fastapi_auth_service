import httpx
from fastapi import Depends

from app.config import Settings, get_settings


class Auth0Client:
    def __init__(self, settings: Settings = Depends(get_settings)):
        self.settings = settings
        self.base_url = f"https://{self.settings.auth0_domain}"
        self.jwks_url = f"{self.base_url}/.well-known/jwks.json"
        self.userinfo_url = f"{self.base_url}/userinfo"
        # Note: Management API client would be more complex, involving token fetching.
        # For now, get_user_by_id will be a simplified placeholder or use a pre-configured token if available.

    async def get_public_key(self) -> dict:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.jwks_url)
                response.raise_for_status()  # Raise an exception for HTTP errors
                return response.json()
            except httpx.HTTPStatusError as e:
                # Log error or raise custom exception
                # print(f"HTTP error fetching JWKS: {e}")
                raise
            except httpx.RequestError as e:
                # Log error or raise custom exception
                # print(f"Request error fetching JWKS: {e}")
                raise

    async def get_user_info(self, token: str) -> dict:
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.userinfo_url, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # print(f"HTTP error fetching user info: {e}")
                raise
            except httpx.RequestError as e:
                # print(f"Request error fetching user info: {e}")
                raise

    async def get_user_by_id(self, user_id: str) -> dict:
        # This is a simplified placeholder.
        # A real implementation would use the Auth0 Management API,
        # which requires its own token with specific permissions.
        # For now, we'll assume it might make a conceptual call that can be mocked.
        # Or, it might not be implemented if not strictly needed by other services yet.
        # For testing purposes, we can simulate its behavior.
        # Let's make it call a dummy endpoint for now to allow mocking with httpx_mock.
        management_api_url = f"{self.base_url}/api/v2/users/{user_id}"
        # management_api_token = self.settings.auth0_management_api_token # Assuming this exists
        # headers = {"Authorization": f"Bearer {management_api_token}"}
        headers = {} # No actual auth for this placeholder

        async with httpx.AsyncClient() as client:
            try:
                # This is a placeholder for a potential Management API call
                # response = await client.get(management_api_url, headers=headers)
                # response.raise_for_status()
                # return response.json()
                # For now, to make it testable without full Management API setup:
                if user_id == "auth0|123456789": # Simulate finding a user
                    return {"sub": user_id, "email": "test@example.com", "name": "Test User From API"}
                else: # Simulate not finding
                    raise httpx.HTTPStatusError(
                        "User not found",
                        request=httpx.Request('GET', management_api_url),
                        response=httpx.Response(404, request=httpx.Request('GET', management_api_url))
                    )

            except httpx.HTTPStatusError as e:
                # print(f"HTTP error fetching user by ID: {e}")
                raise
            except httpx.RequestError as e:
                # print(f"Request error fetching user by ID: {e}")
                raise
