"""
Authentication router with registration, login, and user info endpoints.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from services.auth_service import AuthService
from schemas.auth_schemas import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    RegisterResponse
)
from dependencies.auth import get_current_user
from models.user import User
from exceptions import (
    ConflictException,
    AuthenticationException
)

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Args:
        user_data: User registration data (email, password, name)
        db: Database session
        
    Returns:
        Registration confirmation with user_id
        
    Raises:
        HTTPException 409: If email already exists
    """
    try:
        user = AuthService.register_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            name=user_data.name
        )
        return RegisterResponse(
            message="User registered successfully",
            user_id=user.id
        )
    except ValueError as e:
        raise ConflictException(str(e))


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.
    
    Args:
        credentials: User login credentials (email, password)
        db: Database session
        
    Returns:
        JWT access token and user information
        
    Raises:
        HTTPException 401: If credentials are invalid
    """
    user = AuthService.authenticate_user(
        db=db,
        email=credentials.email,
        password=credentials.password
    )
    
    if not user:
        raise AuthenticationException("Invalid email or password")
    
    # Create access token with user_id as subject
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id)}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user from JWT token
        
    Returns:
        Current user information
    """
    return UserResponse.model_validate(current_user)
