"""
Enhanced Role Management for User Authentication BFF
Provides utilities for handling Keycloak realm and client roles
"""
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel


class RoleType(str, Enum):
    """Types of roles in the system"""
    REALM = "realm"
    CLIENT = "client"


class UserRole(BaseModel):
    """Enhanced role model with type and permissions"""
    name: str
    type: RoleType
    client_id: Optional[str] = None  # For client roles
    permissions: List[str] = []  # Custom permissions mapped to this role
    description: Optional[str] = None


class RolePermissions(BaseModel):
    """User's effective permissions"""
    roles: List[UserRole]
    permissions: List[str]  # Flattened list of all permissions
    access_levels: Dict[str, bool]  # Boolean flags for common access checks


def extract_detailed_roles(token_info: Dict[str, Any]) -> List[UserRole]:
    """
    Extract detailed role information from Keycloak token
    Separates realm roles from client roles with additional metadata
    """
    roles = []
    
    # Extract REALM ROLES
    if "realm_access" in token_info:
        realm_roles = token_info["realm_access"].get("roles", [])
        for role_name in realm_roles:
            # Skip default Keycloak roles
            if role_name not in ["default-roles-master", "offline_access", "uma_authorization"]:
                roles.append(UserRole(
                    name=role_name,
                    type=RoleType.REALM,
                    permissions=get_role_permissions(role_name, RoleType.REALM),
                    description=get_role_description(role_name, RoleType.REALM)
                ))
    
    # Extract CLIENT ROLES
    if "resource_access" in token_info:
        for client_id, client_access in token_info["resource_access"].items():
            client_roles = client_access.get("roles", [])
            for role_name in client_roles:
                # Skip default client roles
                if role_name not in ["uma_protection"]:
                    roles.append(UserRole(
                        name=role_name,
                        type=RoleType.CLIENT,
                        client_id=client_id,
                        permissions=get_role_permissions(role_name, RoleType.CLIENT, client_id),
                        description=get_role_description(role_name, RoleType.CLIENT)
                    ))
    
    return roles


def get_role_permissions(role_name: str, role_type: RoleType, client_id: Optional[str] = None) -> List[str]:
    """
    Map roles to specific permissions
    Customize this based on your application's needs
    """
    # Define role-to-permission mappings
    ROLE_PERMISSIONS = {
        # Realm roles
        ("user", RoleType.REALM): [
            "profile:read",
            "profile:update", 
            "preferences:read",
            "preferences:update"
        ],
        ("admin", RoleType.REALM): [
            "profile:read",
            "profile:update",
            "preferences:read", 
            "preferences:update",
            "users:read",
            "users:manage",
            "system:admin"
        ],
        ("moderator", RoleType.REALM): [
            "profile:read",
            "profile:update",
            "preferences:read",
            "preferences:update", 
            "content:moderate",
            "users:read"
        ],
        
        # Client-specific roles (example for different apps)
        ("dashboard-user", RoleType.CLIENT): [
            "dashboard:read",
            "analytics:view"
        ],
        ("dashboard-admin", RoleType.CLIENT): [
            "dashboard:read",
            "dashboard:manage",
            "analytics:view",
            "analytics:export"
        ],
        ("api-consumer", RoleType.CLIENT): [
            "api:read",
            "api:write"
        ]
    }
    
    return ROLE_PERMISSIONS.get((role_name, role_type), [])


def get_role_description(role_name: str, role_type: RoleType) -> str:
    """Get human-readable role descriptions"""
    ROLE_DESCRIPTIONS = {
        ("user", RoleType.REALM): "Standard user with basic access",
        ("admin", RoleType.REALM): "System administrator with full access",
        ("moderator", RoleType.REALM): "Content moderator with limited admin access",
        ("dashboard-user", RoleType.CLIENT): "Dashboard user with read access",
        ("dashboard-admin", RoleType.CLIENT): "Dashboard administrator",
        ("api-consumer", RoleType.CLIENT): "API access for external integrations"
    }
    
    return ROLE_DESCRIPTIONS.get((role_name, role_type), f"{role_name.title()} role")


def calculate_user_permissions(roles: List[UserRole]) -> RolePermissions:
    """
    Calculate effective permissions for a user based on their roles
    """
    all_permissions = set()
    
    # Collect all permissions from all roles
    for role in roles:
        all_permissions.update(role.permissions)
    
    # Calculate access levels for common UI checks
    access_levels = {
        "can_view_admin": any("system:admin" in role.permissions for role in roles),
        "can_manage_users": any("users:manage" in role.permissions for role in roles),
        "can_moderate": any("content:moderate" in role.permissions for role in roles),
        "can_view_analytics": any("analytics:view" in role.permissions for role in roles),
        "can_export_data": any("analytics:export" in role.permissions for role in roles),
        "can_access_api": any("api:read" in role.permissions or "api:write" in role.permissions for role in roles),
        "is_admin": any(role.name == "admin" and role.type == RoleType.REALM for role in roles),
        "is_moderator": any(role.name == "moderator" for role in roles),
    }
    
    return RolePermissions(
        roles=roles,
        permissions=list(all_permissions),
        access_levels=access_levels
    )


def get_roles_for_frontend(token_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get comprehensive role information formatted for frontend consumption
    """
    detailed_roles = extract_detailed_roles(token_info)
    user_permissions = calculate_user_permissions(detailed_roles)
    
    return {
        "roles": [
            {
                "name": role.name,
                "type": role.type.value,
                "client_id": role.client_id,
                "permissions": role.permissions,
                "description": role.description
            }
            for role in detailed_roles
        ],
        "permissions": user_permissions.permissions,
        "access_levels": user_permissions.access_levels,
        "simple_roles": [role.name for role in detailed_roles]  # For backward compatibility
    }


# Example permission decorators for endpoints
from functools import wraps
from fastapi import HTTPException, status
from models import UserInfo

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get('current_user')
            if not current_user or not isinstance(current_user, UserInfo):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Get user permissions (you'd need to implement this)
            user_permissions = get_user_permissions_from_roles(current_user.roles)
            
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission required: {permission}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role_name: str, role_type: RoleType = RoleType.REALM):
    """Decorator to require specific role"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Simple role check (existing functionality)
            if role_name not in current_user.roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: {role_name}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def get_user_permissions_from_roles(role_names: List[str]) -> List[str]:
    """
    Convert simple role names to permissions
    This is a simplified version - in practice you might cache this
    """
    permissions = set()
    
    for role_name in role_names:
        # Try realm role first
        role_permissions = get_role_permissions(role_name, RoleType.REALM)
        if role_permissions:
            permissions.update(role_permissions)
        else:
            # Try as client role
            role_permissions = get_role_permissions(role_name, RoleType.CLIENT)
            permissions.update(role_permissions)
    
    return list(permissions)


# Example usage in endpoints:
"""
from role_management import require_permission, require_role, RoleType

@app.get("/admin/users")
@require_permission("users:manage")
async def get_all_users(current_user: UserInfo = Depends(get_current_user)):
    # Only users with "users:manage" permission can access
    pass

@app.delete("/admin/users/{user_id}")
@require_role("admin", RoleType.REALM)
async def delete_user(user_id: int, current_user: UserInfo = Depends(get_current_user)):
    # Only users with "admin" realm role can access
    pass
"""
