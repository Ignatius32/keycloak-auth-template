from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, date, time


class UserLogin(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    username: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: list[str] = []
    user_id: str


# Model for user registration
class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = "user"  # Changed from "astro-user" to generic "user"


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


# User Profile Models
class UserProfileCreate(BaseModel):
    """Model for creating a new user profile"""
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None  # Keep timezone for general app usage


class UserProfileResponse(BaseModel):
    """Model for user profile response"""
    id: int
    keycloak_id: str
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True  # For SQLAlchemy compatibility


class UserProfileUpdate(BaseModel):
    """Model for updating user profile (all fields optional)"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None


class UserStatusResponse(BaseModel):
    """Model for user status response - tells frontend what to render"""
    has_profile: bool
    profile_complete: bool
    next_step: str  # "dashboard", "complete_profile", "login"
    user_info: Optional[Dict[str, Any]] = None
    profile_data: Optional[UserProfileResponse] = None


# Password Reset Models
class PasswordResetRequest(BaseModel):
    email: str


class PasswordResetResponse(BaseModel):
    success: bool
    message: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class PasswordChangeResponse(BaseModel):
    success: bool
    message: str
