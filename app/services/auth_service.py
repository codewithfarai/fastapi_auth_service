from fastapi import Depends, HTTPException, status
from typing import Tuple # For type hint of tuple return

from app.core.auth.auth0_client import Auth0Client
from app.core.auth.jwt_handler import JWTHandler
from app.db.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse # Renamed UserSchema to UserResponse for clarity
from app.models.user import User as UserModel # SQLAlchemy model
from app.config import Settings, get_settings
from app.models.user import UserRole # Ensure UserRole is available for mapping

class AuthService:
    def __init__(self,
                 auth0_client: Auth0Client = Depends(),
                 jwt_handler: JWTHandler = Depends(),
                 user_repository: UserRepository = Depends(),
                 settings: Settings = Depends(get_settings)):
        self.auth0_client = auth0_client
        self.jwt_handler = jwt_handler
        self.user_repository = user_repository
        self.settings = settings

    async def login_or_register_via_auth0(self, auth0_token: str) -> Tuple[str, UserResponse]:
        try:
            auth0_user_data = await self.auth0_client.get_user_info(auth0_token)
        except HTTPException as e: # Catch HTTPExceptions from auth0_client
            # Assuming auth0_client might raise 401/403 for bad tokens or connection issues
            raise HTTPException(
                status_code=e.status_code,
                detail=f"Auth0 validation failed: {e.detail}"
            )
        except Exception as e: # Catch other errors like httpx.RequestError
            # Log the original exception e
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to fetch user info from Auth0: {str(e)}"
            )

        auth0_id = auth0_user_data.get("sub")
        if not auth0_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Auth0 user ID (sub) missing in token payload")

        user = await self.user_repository.get_user_by_auth0_id(auth0_id)

        if not user:
            email = auth0_user_data.get("email")
            if not email:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email missing in Auth0 user data")

            # Basic role mapping based on Auth0 roles or default
            # This is a simplified example. Real role mapping might be more complex.
            auth0_roles = auth0_user_data.get("roles", [])
            # Example: if "admin" in auth0_roles, assign UserRole.ADMIN, else UserRole.CUSTOMER
            # This requires your Auth0 token to include a "roles" claim.
            # For now, default to CUSTOMER or determine from permissions if roles claim isn't standard.
            # The test_user_data has "roles": ["customer"]

            # Determine role. This is a placeholder for more complex logic.
            # If roles are passed from Auth0 and match UserRole enum:
            final_role = UserRole.CUSTOMER # Default
            if auth0_roles:
                # Naive: takes the first role that's valid in our system
                for r_str in auth0_roles:
                    try:
                        valid_role = UserRole(r_str)
                        final_role = valid_role
                        break
                    except ValueError:
                        continue # This role from Auth0 is not recognized in our system

            user_create_data = UserCreate(
                auth0_id=auth0_id,
                email=email,
                name=auth0_user_data.get("name", "Unnamed User"),
                role=final_role, # Assign role
            )
            try:
                user = await self.user_repository.create_user(user_create_data)
            except Exception as e: # Catch potential DB errors
                # Log e
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not create user: {str(e)}")
            if not user: # Should be caught by the exception above ideally
                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user in database")

        # User exists or was created, now issue internal token
        # Ensure user.role is the enum value, not the DB string if there's a difference
        internal_token_payload = {
            "sub": str(user.id), # Use internal user ID as subject
            "roles": [user.role.value if isinstance(user.role, UserRole) else user.role],
            "permissions": auth0_user_data.get("permissions", []) # Pass permissions from Auth0
        }
        internal_access_token = self.jwt_handler.encode_token(internal_token_payload)

        return internal_access_token, UserResponse.model_validate(user) # Use model_validate for Pydantic v2

    async def get_user_from_internal_token(self, internal_token: str) -> UserResponse:
        try:
            payload = self.jwt_handler.decode_token(internal_token)
        except HTTPException as e: # Re-raise if decode_token raised HTTPException (e.g. 401)
            raise
        except Exception as e: # Catch other decode errors not wrapped in HTTPException by jwt_handler
            # Log e
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid internal token: {str(e)}")

        if not payload or "sub" not in payload: # Should be caught by jwt_handler if 'sub' is mandatory there
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal token payload: 'sub' missing")

        user_id_str = payload["sub"]
        try:
            user_id = int(user_id_str)
        except ValueError:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user ID format in token subject")

        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found for token")

        return UserResponse.model_validate(user)
