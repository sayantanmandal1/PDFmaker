"""
Pydantic schemas for authentication endpoints.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional
from uuid import UUID
from validators import (
    validate_password_strength,
    validate_email_domain,
    ValidationMixin,
    create_field_with_validation
)


class UserRegister(BaseModel, ValidationMixin):
    """Schema for user registration request."""
    email: EmailStr = create_field_with_validation(
        description="Valid email address"
    )
    password: str = create_field_with_validation(
        min_length=6,
        max_length=128,
        description="Password must be at least 6 characters with letters and numbers/symbols"
    )
    name: str = create_field_with_validation(
        min_length=1,
        max_length=255,
        description="Full name"
    )
    
    @validator('email')
    def validate_email(cls, v):
        return validate_email_domain(v)
    
    @validator('password')
    def validate_password(cls, v):
        return validate_password_strength(v)
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class UserLogin(BaseModel, ValidationMixin):
    """Schema for user login request."""
    email: EmailStr = create_field_with_validation(
        description="Email address"
    )
    password: str = create_field_with_validation(
        min_length=1,
        max_length=128,
        description="Password"
    )


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: UUID
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegisterResponse(BaseModel):
    """Schema for registration response."""
    message: str
    user_id: UUID
