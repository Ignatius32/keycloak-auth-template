from keycloak import KeycloakOpenID, KeycloakAdmin
from keycloak.exceptions import KeycloakAuthenticationError
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from models import UserInfo, Token
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Keycloak configuration
KEYCLOAK_BASE_URL = os.getenv("KEYCLOAK_BASE_URL", "http://localhost:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "ASTRO")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "account")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "")

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Security scheme
security = HTTPBearer()


# Initialize Keycloak clients
try:
    keycloak_openid = KeycloakOpenID(
        server_url=KEYCLOAK_BASE_URL,
        client_id=KEYCLOAK_CLIENT_ID,
        realm_name=KEYCLOAK_REALM,
        client_secret_key=KEYCLOAK_CLIENT_SECRET
    )
    keycloak_admin = KeycloakAdmin(
        server_url=KEYCLOAK_BASE_URL,
        username=os.getenv("KEYCLOAK_ADMIN_USER", "admin"),
        password=os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin"),
        realm_name=KEYCLOAK_REALM,
        client_id=KEYCLOAK_CLIENT_ID,
        client_secret_key=KEYCLOAK_CLIENT_SECRET,
        verify=True
    )
    logger.info(f"Keycloak clients initialized for realm {KEYCLOAK_REALM}")
except Exception as e:
    logger.error(f"Failed to initialize Keycloak clients: {e}")
    keycloak_openid = None
    keycloak_admin = None


# Function to create user in Keycloak and assign role
def create_user_in_keycloak(user_data):
    """
    Create a new user in Keycloak and assign the specified role.
    user_data: dict with keys username, password, email, first_name, last_name, role
    """
    if not keycloak_admin:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Keycloak admin client not initialized"
        )
    try:
        # Create user with email verification required
        user_id = keycloak_admin.create_user({
            "username": user_data["username"],
            "email": user_data.get("email"),
            "firstName": user_data.get("first_name"),
            "lastName": user_data.get("last_name"),
            "enabled": True,
            "emailVerified": False,  # Force email verification
            "requiredActions": ["VERIFY_EMAIL"],  # Require email verification on first login
            "credentials": [{
                "type": "password",
                "value": user_data["password"],
                "temporary": False
            }]
        })
        
        # Assign role
        role_name = user_data.get("role", "user")
        role = keycloak_admin.get_realm_role(role_name)
        keycloak_admin.assign_realm_roles(user_id, [role])
        
        # Send verification email
        try:
            keycloak_admin.send_verify_email(user_id)
            logger.info(f"Verification email sent to {user_data.get('email')}")
        except Exception as email_error:
            logger.warning(f"Failed to send verification email: {str(email_error)}")
            # Don't fail user creation if email sending fails
        
        logger.info(f"User {user_data['username']} created with role {role_name} and email verification required")
        return user_id
    except Exception as e:
        logger.error(f"Error creating user in Keycloak: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def authenticate_user(username: str, password: str) -> UserInfo:
    """Authenticate user with Keycloak"""
    if not keycloak_openid:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Keycloak client not initialized"
        )
    
    try:
        # Get token from Keycloak
        token = keycloak_openid.token(username, password)
        access_token = token["access_token"]
        
        # Get user info from token
        userinfo = keycloak_openid.userinfo(access_token)
        
        # Get user roles
        token_info = keycloak_openid.introspect(access_token)
        roles = []
        
        # Try different places where roles might be stored
        if "realm_access" in token_info:
            realm_roles = token_info["realm_access"].get("roles", [])
            # Filter out default Keycloak roles
            filtered_realm_roles = [role for role in realm_roles 
                                  if role not in ["default-roles-master", "offline_access", "uma_authorization"]]
            roles.extend(filtered_realm_roles)
            
        if "resource_access" in token_info:
            for client_id, client_access in token_info["resource_access"].items():
                client_roles = client_access.get("roles", [])
                # Filter out default client roles
                filtered_client_roles = [role for role in client_roles 
                                       if role not in ["uma_protection"]]
                roles.extend(filtered_client_roles)
        
        # For development, if no user role found, add it for the test user
        if username == "37099475" and "user" not in roles:
            logger.warning("Adding user role for development user")
            roles.append("user")
        
        # Check if user has required role (optional - remove if you don't want role checking)
        # if "user" not in roles:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="User does not have required role 'user'"
        #     )
        
        user_info = UserInfo(
            username=userinfo.get("preferred_username", username),
            email=userinfo.get("email"),
            first_name=userinfo.get("given_name"),
            last_name=userinfo.get("family_name"),
            roles=roles,
            user_id=userinfo.get("sub")
        )
        
        logger.info(f"User {username} authenticated successfully")
        return user_info
        
    except KeycloakAuthenticationError as e:
        logger.error(f"Authentication failed for user {username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {str(e)}")
        # Check if it's a client configuration error
        if "unauthorized_client" in str(e):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Keycloak client configuration error. Please check KEYCLOAK_SETUP.md for configuration instructions."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInfo:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # In a real application, you would fetch user info from database
    # For now, we'll decode it from the token payload
    user_info = UserInfo(
        username=payload.get("username", ""),
        email=payload.get("email"),
        first_name=payload.get("first_name"),
        last_name=payload.get("last_name"),
        roles=payload.get("roles", []),
        user_id=payload.get("user_id", "")
    )
    
    return user_info


async def require_user_role(current_user: UserInfo = Depends(get_current_user)):
    """Require user role - you can customize this or add more specific role requirements"""
    if "user" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required role: user"
        )
    return current_user


def send_password_reset_email(email: str):
    """
    Send password reset email to user by email address.
    Returns True if email was sent successfully.
    """
    if not keycloak_admin:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Keycloak admin client not initialized"
        )
    
    try:
        # First, find the user by email
        users = keycloak_admin.get_users({"email": email})
        
        if not users:
            # For security, we don't reveal if email exists or not
            logger.warning(f"Password reset requested for non-existent email: {email}")
            return True  # Return True anyway for security
        
        user = users[0]  # Get first matching user
        user_id = user["id"]
        
        # Send password reset email using UPDATE_PASSWORD action
        keycloak_admin.send_update_account(
            user_id=user_id,
            payload=["UPDATE_PASSWORD"],
            lifespan=3600  # Token expires in 1 hour
        )
        
        logger.info(f"Password reset email sent to: {email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending password reset email: {str(e)}")
        # Don't expose internal errors to user
        return True  # Return True anyway for security


def change_user_password(user_id: str, current_password: str, new_password: str):
    """
    Change user password after verifying current password.
    """
    if not keycloak_admin:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Keycloak admin client not initialized"
        )
    
    try:
        # First verify current password by attempting login
        user = keycloak_admin.get_user(user_id)
        username = user.get("username")
        
        if not username:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        try:
            keycloak_openid.token(username, current_password)
        except KeycloakAuthenticationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Set new password
        keycloak_admin.set_user_password(
            user_id=user_id,
            password=new_password,
            temporary=False
        )
        
        logger.info(f"Password changed for user: {username}")
        return True
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error changing password"
        )
