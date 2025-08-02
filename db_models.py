"""
SQLAlchemy models for User Authentication System
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    keycloak_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    city = Column(String(255))
    country = Column(String(255))
    timezone = Column(String(100))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)
    sessions = relationship("UserSession", back_populates="user")


class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    preferred_timezone = Column(String(100))
    theme = Column(String(50), default="light")  # light, dark
    language = Column(String(10), default="en")  # en, es, fr, etc.
    notifications_enabled = Column(Boolean, default=True)
    app_preferences = Column(JSONB)  # Store any app-specific preferences as JSON
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="preferences")


class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_accessed = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")
