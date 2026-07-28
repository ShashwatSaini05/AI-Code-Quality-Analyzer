"""
CodeSage AI — Authentication API Routes
Endpoints for registration, login, OAuth, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserLogin, UserRegister, UserResponse, TokenResponse
from app.services.auth_service import AuthService
from app.core import AuthenticationError

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    try:
        result = await auth_service.register(
            db, email=data.email, username=data.username,
            password=data.password, full_name=data.full_name,
        )
        return result
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate with email and password."""
    try:
        result = await auth_service.login(db, email=data.email, password=data.password)
        return result
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)


@router.get("/me", response_model=UserResponse)
async def get_profile(user: User = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return user


@router.get("/github/login")
async def github_login():
    """Redirect URL for GitHub OAuth login."""
    from app.config import get_settings
    settings = get_settings()
    if not settings.github_client_id:
        raise HTTPException(status_code=501, detail="GitHub OAuth not configured")
    url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.github_client_id}"
        f"&redirect_uri={settings.github_redirect_uri}"
        f"&scope=user:email,repo"
    )
    return {"authorization_url": url}


@router.get("/google/login")
async def google_login():
    """Redirect URL for Google OAuth login."""
    from app.config import get_settings
    settings = get_settings()
    if not settings.google_client_id:
        raise HTTPException(status_code=501, detail="Google OAuth not configured")
    url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.google_client_id}"
        f"&redirect_uri={settings.google_redirect_uri}"
        f"&response_type=code"
        f"&scope=email%20profile"
    )
    return {"authorization_url": url}
