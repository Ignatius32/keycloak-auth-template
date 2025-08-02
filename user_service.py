# User service functions for authentication system

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db_models import User
from models import UserProfileCreate, UserProfileUpdate
from datetime import datetime, date, time
from typing import Optional
import uuid


def get_user_by_keycloak_id(db: Session, keycloak_id: str) -> Optional[User]:
    """Get user by Keycloak ID"""
    return db.query(User).filter(User.keycloak_id == keycloak_id).first()


def create_user_profile(db: Session, keycloak_id: str, profile_data: UserProfileCreate) -> User:
    """Create a new user profile"""
    try:
        # Create user object
        db_user = User(
            keycloak_id=uuid.UUID(keycloak_id),
            full_name=profile_data.full_name,
            phone=profile_data.phone,
            address=profile_data.address,
            city=profile_data.city,
            country=profile_data.country,
            timezone=profile_data.timezone
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
        
    except IntegrityError:
        db.rollback()
        raise ValueError("User profile already exists")
    except ValueError as e:
        db.rollback()
        raise ValueError(f"Invalid data format: {str(e)}")


def update_user_profile(db: Session, user: User, profile_data: UserProfileUpdate) -> User:
    """Update existing user profile"""
    try:
        # Update only provided fields
        if profile_data.full_name is not None:
            user.full_name = profile_data.full_name
        if profile_data.phone is not None:
            user.phone = profile_data.phone
        if profile_data.address is not None:
            user.address = profile_data.address
        if profile_data.city is not None:
            user.city = profile_data.city
        if profile_data.country is not None:
            user.country = profile_data.country
        if profile_data.timezone is not None:
            user.timezone = profile_data.timezone
        
        db.commit()
        db.refresh(user)
        return user
        
    except ValueError as e:
        db.rollback()
        raise ValueError(f"Invalid data format: {str(e)}")
