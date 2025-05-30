from typing import List, Dict, Any, Optional, Callable

from fastapi import HTTPException, Depends, status

# This would typically be your User model or Pydantic schema for decoded token payload
# For this module, we'll assume it's a dictionary.
UserPayload = Dict[str, Any]

# Mocked dependency to simulate getting a user payload.
# In a real app, this would be your actual JWT decoding dependency.
# For testing permissions directly, we often won't call this mock,
# but rather pass the UserPayload directly to the checker functions or methods.
async def get_current_user_payload_placeholder() -> Optional[UserPayload]:
    # This placeholder should ideally not be used directly in production dependencies
    # if the dependency is meant to be initialized with it.
    # Instead, the dependency that provides the user payload should be injected.
    # However, FastAPI dependencies are called, so this would be called if used.
    # For testing, we'll mock the input to __call__ or the function parameters.
    print("Warning: get_current_user_payload_placeholder was called. This should be mocked or overridden in tests.")
    return None


# --- Permission Checking Logic ---

def check_user_permissions(
    required_permissions: List[str],
    user_permissions: List[str]
) -> bool:
    """
    Checks if the user possesses ALL required permissions.
    """
    if not required_permissions: # No specific permissions required
        return True
    if not user_permissions: # User has no permissions at all
        return False
    return all(perm in user_permissions for perm in required_permissions)

# --- Role Checking Logic ---

def check_user_role(
    required_role: str,
    user_roles: List[str]
) -> bool:
    """
    Checks if the user has the specified role.
    """
    if not required_role: # Should not happen, but if no role is specified, access is not role-dependent
        return True
    if not user_roles: # User has no roles
        return False
    return required_role in user_roles


# --- FastAPI Dependency Classes/Functions ---

class PermissionsDependency:
    """
    FastAPI dependency to check for required permissions.
    Relies on another dependency (user_payload_dependency) to provide the user's payload.
    """
    def __init__(
        self,
        required_permissions: List[str],
        user_payload_dependency: Callable[..., Optional[UserPayload]] = Depends(get_current_user_payload_placeholder)
    ):
        self.required_permissions = required_permissions
        self.user_payload_dependency = user_payload_dependency # Store the dependency function itself

    async def __call__(self, user_payload: Optional[UserPayload] = Depends(get_current_user_payload_placeholder)) -> UserPayload:
        # Note: The user_payload_dependency in __init__ is more for configuration if needed.
        # The actual resolution happens here with Depends(get_current_user_payload_placeholder)
        # or whatever actual dependency is passed during router setup.
        # For testing, we will want to provide user_payload directly to a test instance of this.

        if user_payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated or user information not available.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_perms = user_payload.get("permissions")
        if user_perms is None: # Key exists but is None
             user_perms = []
        elif not isinstance(user_perms, list): # Key exists but is not a list
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid permissions format in token.",
            )

        if not check_user_permissions(self.required_permissions, user_perms):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have all required permissions: {', '.join(self.required_permissions)}",
            )
        return user_payload


def require_role_dependency(
    role: str,
    user_payload: Optional[UserPayload] = Depends(get_current_user_payload_placeholder)
) -> UserPayload:
    """
    FastAPI dependency to check for a specific role.
    """
    if user_payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated or user information not available.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_r = user_payload.get("roles")
    if user_r is None: # Key exists but is None
        user_r = []
    elif not isinstance(user_r, list): # Key exists but is not a list
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid roles format in token.",
        )

    if not check_user_role(role, user_r):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have the required role: {role}",
        )
    return user_payload

# Note: The PermissionsDependency class structure is a bit non-standard for how __init__
# interacts with __call__ regarding user_payload_dependency.
# A more common way for class-based dependencies that need parameters (like required_permissions)
# is:
# router.get("/path", dependencies=[Depends(PermissionChecker(["perm1"]))])
# where PermissionChecker is the class.
# The implementation above is slightly different; it's more like a factory that produces a dependency.
# For direct testing of PermissionChecker logic, we'd instantiate it and call its __call__ with mocked input.
# The provided example `PermissionChecker` was simpler, let's align with that more closely for the dependency.

# Re-simplifying the class-based dependency to match the original example more closely:
class RequirePermissions: # Renamed for clarity
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions

    async def __call__(self, user_payload: Optional[UserPayload] = Depends(get_current_user_payload_placeholder)):
        if user_payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated or user information not available.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_perms = user_payload.get("permissions", []) # Default to empty list if key missing
        if not isinstance(user_perms, list):
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, # Or 403, but indicates bad token structure
                detail="Invalid 'permissions' format in user payload.",
            )

        if not all(perm in user_perms for perm in self.required_permissions):
            missing_perms = [perm for perm in self.required_permissions if perm not in user_perms]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User lacks required permissions: {', '.join(missing_perms)}",
            )
        return user_payload

# Simpler functional dependency for roles, matching the example structure
async def require_role(role: str, user_payload: Optional[UserPayload] = Depends(get_current_user_payload_placeholder)):
    if user_payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated or user information not available.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_roles = user_payload.get("roles", []) # Default to empty list
    if not isinstance(user_roles, list):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, # Or 403
            detail="Invalid 'roles' format in user payload.",
        )

    if role not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User lacks required role: {role}",
        )
    return user_payload

# Removing the helper functions check_user_permissions and check_user_role
# as their logic is now directly inside the dependency classes/functions.
# This makes the dependencies self-contained. If these checks were complex,
# keeping them separate would be better. For this case, inline is fine.
# The final version of the file will use the simplified RequirePermissions class
# and the require_role function.
# (Self-correction during thought process: The prompt asked for testing `check_user_permissions`
# and `check_user_role` if they exist. So, it's better to keep them if they are part of the design,
# or test the logic within the dependencies if they are not separate.
# I will keep the separate helper functions as they are good for direct unit testing
# and then used by the dependencies.)

# Final structure to be written:
# UserPayload type alias
# get_current_user_payload_placeholder (for dependency signature, will be mocked in tests)
# check_user_permissions function
# check_user_role function
# RequirePermissions class (FastAPI dependency using check_user_permissions)
# require_role function (FastAPI dependency using check_user_role)

# Corrected version for the file block:
# (Ensuring the dependencies use the helper functions)
# (Using `permissions: Optional[list] = None` and `roles: Optional[list] = None` in UserPayload for clarity in tests)
# (Defaulting to empty list for user_permissions/user_roles if key is missing OR if value is None)
# (Handling invalid type for permissions/roles in payload)
