"""Pydantic schemas for user-related operations."""
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    role: UserRole = Field(default=UserRole.STAFF)
    is_active: bool = Field(default=True)


class UserCreate(UserBase):
    """Schema for creating a new user.
    
    Used for user registration by admins.
    """
    password: str = Field(..., min_length=8, max_length=100)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "password": "securepassword123",
                "role": "staff",
                "is_active": True
            }
        }
    )


class UserUpdate(BaseModel):
    """Schema for updating user information.
    
    All fields are optional for partial updates.
    """
    username: str | None = Field(None, min_length=3, max_length=50)
    role: UserRole | None = None
    is_active: bool | None = None
    password: str | None = Field(None, min_length=8, max_length=100)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "role": "admin",
                "is_active": True
            }
        }
    )


class UserResponse(UserBase):
    """Schema for user data in responses.
    
    Excludes sensitive information like password hash.
    """
    id: int
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "johndoe",
                "role": "staff",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }
    )


class UserLogin(BaseModel):
    """Schema for user login requests."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "password": "securepassword123"
            }
        }
    )


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 28800
            }
        }
    )


class TokenData(BaseModel):
    """Schema for token payload data.
    
    Used internally for decoding JWT tokens.
    """
    username: str | None = None
    user_id: int | None = None
    role: UserRole | None = None


class PasswordChange(BaseModel):
    """Schema for password change requests."""
    current_password: str = Field(..., min_length=1, max_length=100)
    new_password: str = Field(..., min_length=8, max_length=100)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newsecurepassword456"
            }
        }
    )
