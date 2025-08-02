from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from datetime import timedelta
import uvicorn
import logging
from sqlalchemy.orm import Session
from typing import Optional

from models import (
    UserLogin, Token, UserInfo, UserRegister, UserProfileCreate, UserProfileResponse, 
    UserProfileUpdate, UserStatusResponse, PasswordResetRequest, PasswordResetResponse,
    PasswordChangeRequest, PasswordChangeResponse
)
from auth import (
    authenticate_user, create_access_token, get_current_user, require_user_role, 
    create_user_in_keycloak, send_password_reset_email, change_user_password
)
from database import get_db
from db_models import User
from user_service import (
    get_user_by_keycloak_id, 
    create_user_profile, 
    update_user_profile
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="User Authentication API",
    description="Backend service for user authentication with Keycloak integration and password reset functionality",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://localhost:5173"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "User Authentication API", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "user-auth-api"}


# Authentication endpoints
@app.post("/auth/login", response_model=Token)
async def login(user_login: UserLogin):
    """Authenticate user with Keycloak and return JWT token"""
    try:
        # Authenticate with Keycloak
        user_info = await authenticate_user(user_login.username, user_login.password)
        
        # Create JWT token with user info
        token_data = {
            "sub": user_info.username,
            "username": user_info.username,
            "email": user_info.email,
            "first_name": user_info.first_name,
            "last_name": user_info.last_name,
            "roles": user_info.roles,
            "user_id": user_info.user_id
        }
        
        access_token = create_access_token(token_data)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=1800  # 30 minutes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )


# Registration endpoint
@app.post("/auth/register")
async def register(user: UserRegister):
    """Register a new user and assign role in Keycloak"""
    try:
        user_id = create_user_in_keycloak(user.dict())
        return {"user_id": user_id, "message": "User registered successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )


# Password Reset endpoints
@app.post("/auth/password-reset", response_model=PasswordResetResponse)
async def request_password_reset(request: PasswordResetRequest):
    """Request password reset email"""
    try:
        success = send_password_reset_email(request.email)
        
        # Always return success for security (don't reveal if email exists)
        return PasswordResetResponse(
            success=True,
            message="If the email address exists in our system, a password reset link has been sent."
        )
        
    except Exception as e:
        logger.error(f"Password reset request error: {str(e)}")
        # Still return success for security
        return PasswordResetResponse(
            success=True,
            message="If the email address exists in our system, a password reset link has been sent."
        )


@app.post("/auth/change-password", response_model=PasswordChangeResponse)
async def change_password(
    request: PasswordChangeRequest,
    current_user: UserInfo = Depends(get_current_user)
):
    """Change user password (requires current password)"""
    try:
        success = change_user_password(
            current_user.user_id, 
            request.current_password, 
            request.new_password
        )
        
        if success:
            return PasswordChangeResponse(
                success=True,
                message="Password changed successfully"
            )
        else:
            return PasswordChangeResponse(
                success=False,
                message="Failed to change password"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during password change"
        )


@app.get("/auth/me", response_model=UserInfo)
async def get_user_profile(current_user: UserInfo = Depends(get_current_user)):
    """Get current user profile"""
    return current_user


@app.get("/auth/me/roles")
async def get_user_roles_detailed(current_user: UserInfo = Depends(get_current_user)):
    """Get detailed user roles and permissions for frontend access control"""
    try:
        # Import here to avoid circular imports
        from role_management import get_roles_for_frontend, get_user_permissions_from_roles
        
        # Get basic roles
        user_roles = current_user.roles
        
        # Get permissions from roles
        permissions = get_user_permissions_from_roles(user_roles)
        
        # Calculate access levels for common UI checks
        access_levels = {
            "can_view_admin": "admin" in user_roles,
            "can_manage_users": "admin" in user_roles,
            "can_moderate": "moderator" in user_roles or "admin" in user_roles,
            "can_view_analytics": any(role in ["admin", "analyst", "dashboard-admin"] for role in user_roles),
            "can_export_data": any(role in ["admin", "dashboard-admin"] for role in user_roles),
            "can_access_api": any(role in ["admin", "api-consumer", "developer"] for role in user_roles),
            "is_admin": "admin" in user_roles,
            "is_moderator": "moderator" in user_roles,
            "is_standard_user": "user" in user_roles,
        }
        
        return {
            "user_id": current_user.user_id,
            "username": current_user.username,
            "roles": user_roles,  # Simple role names for backward compatibility
            "permissions": permissions,  # Specific permissions
            "access_levels": access_levels,  # Boolean flags for frontend
            "role_details": [
                {
                    "name": role,
                    "type": "realm",  # You could enhance this to detect client roles
                    "description": f"{role.title()} role"
                }
                for role in user_roles
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting user roles: {str(e)}")
        # Fallback to basic role information
        return {
            "user_id": current_user.user_id,
            "username": current_user.username,
            "roles": current_user.roles,
            "permissions": [],
            "access_levels": {
                "is_admin": "admin" in current_user.roles,
                "is_standard_user": "user" in current_user.roles
            },
            "role_details": []
        }


@app.get("/auth/status", response_model=UserStatusResponse)
async def get_user_status(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user status - tells frontend what to render"""
    try:
        # Get user profile from database
        user = get_user_by_keycloak_id(db, current_user.user_id)
        
        if not user:
            # User authenticated but no profile
            return UserStatusResponse(
                has_profile=False,
                profile_complete=False,
                next_step="complete_profile",
                user_info={
                    "username": current_user.username,
                    "email": current_user.email,
                    "first_name": current_user.first_name,
                    "last_name": current_user.last_name
                }
            )
        
        # User has profile - check if it's complete
        return UserProfileResponse(
            id=user.id,
            keycloak_id=str(user.keycloak_id),
            full_name=user.full_name,
            phone=user.phone,
            address=user.address,
            city=user.city,
            country=user.country,
            timezone=user.timezone,
            created_at=user.created_at.isoformat()
        )
        
        # Profile exists and is complete
        return UserStatusResponse(
            has_profile=True,
            profile_complete=True,
            next_step="dashboard",
            user_info={
                "username": current_user.username,
                "email": current_user.email,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name
            },
            profile_data=UserProfileResponse(
                id=user.id,
                keycloak_id=str(user.keycloak_id),
                full_name=user.full_name,
                phone=user.phone,
                address=user.address,
                city=user.city,
                country=user.country,
                timezone=user.timezone,
                created_at=user.created_at.isoformat()
            )
        )
        
    except Exception as e:
        logger.error(f"Error getting user status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user status"
        )


# User Profile endpoints
@app.get("/users/me", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile from database"""
    try:
        user = get_user_by_keycloak_id(db, current_user.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found. Please complete your profile."
        )
        
        return UserProfileResponse(
            id=user.id,
            keycloak_id=str(user.keycloak_id),
            full_name=user.full_name,
            phone=user.phone,
            address=user.address,
            city=user.city,
            country=user.country,
            timezone=user.timezone,
            created_at=user.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user profile"
        )


@app.post("/users/me", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_my_profile(
    profile_data: UserProfileCreate,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create current user's profile"""
    try:
        # Check if profile already exists
        existing_user = get_user_by_keycloak_id(db, current_user.user_id)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User profile already exists. Use PUT to update."
            )
        
        # Create new profile
        user = create_user_profile(db, current_user.user_id, profile_data)
        
        return UserProfileResponse(
            id=user.id,
            keycloak_id=str(user.keycloak_id),
            full_name=user.full_name,
            phone=user.phone,
            address=user.address,
            city=user.city,
            country=user.country,
            timezone=user.timezone,
            created_at=user.created_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user profile"
        )


@app.put("/users/me", response_model=UserProfileResponse)
async def update_my_profile(
    profile_data: UserProfileUpdate,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    try:
        user = get_user_by_keycloak_id(db, current_user.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found. Create profile first."
            )
        
        # Update profile
        updated_user = update_user_profile(db, user, profile_data)
        
        return UserProfileResponse(
            id=updated_user.id,
            keycloak_id=str(updated_user.keycloak_id),
            full_name=updated_user.full_name,
            phone=updated_user.phone,
            address=updated_user.address,
            city=updated_user.city,
            country=updated_user.country,
            timezone=updated_user.timezone,
            created_at=updated_user.created_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user profile"
        )


# Example protected endpoint - you can extend this for your specific use case
@app.get("/protected-example")
async def protected_example(current_user: UserInfo = Depends(get_current_user)):
    """Example protected endpoint - replace with your business logic"""
    return {
        "message": f"Hello {current_user.username}! This is a protected endpoint.",
        "user_roles": current_user.roles,
        "timestamp": "2025-08-02"
    }


# Role-based access examples
@app.get("/admin/users")
async def get_all_users_admin(current_user: UserInfo = Depends(get_current_user)):
    """Admin-only endpoint - list all users"""
    if "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    
    # Your admin logic here
    return {
        "message": "Admin access granted",
        "users": ["user1", "user2", "user3"],  # Replace with actual user data
        "admin_user": current_user.username
    }


@app.get("/moderator/content")
async def moderate_content(current_user: UserInfo = Depends(get_current_user)):
    """Moderator or Admin access - content moderation"""
    if not any(role in current_user.roles for role in ["admin", "moderator"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator or Admin role required"
        )
    
    return {
        "message": "Moderation access granted",
        "pending_items": ["item1", "item2"],  # Replace with actual content
        "moderator": current_user.username
    }


@app.get("/analytics/dashboard")
async def view_analytics(current_user: UserInfo = Depends(get_current_user)):
    """Analytics access - multiple roles allowed"""
    allowed_roles = ["admin", "analyst", "dashboard-user", "dashboard-admin"]
    if not any(role in current_user.roles for role in allowed_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analytics access role required"
        )
    
    # Different data based on role
    is_admin = "admin" in current_user.roles
    can_export = any(role in current_user.roles for role in ["admin", "dashboard-admin"])
    
    return {
        "message": "Analytics access granted",
        "analytics_data": {"views": 1234, "users": 567},
        "user_permissions": {
            "can_view": True,
            "can_export": can_export,
            "is_admin": is_admin
        },
        "user": current_user.username
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
