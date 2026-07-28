"""
CodeSage AI — Authentication Service
Handles user registration, login, and OAuth flows.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.core import AuthenticationError
from app.models.user import User, AuthProvider


class AuthService:
    """Service for authentication operations."""

    async def register(
        self,
        db: AsyncSession,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
    ) -> dict:
        """Register a new user with email/password."""
        # Check for existing user
        existing = await db.execute(
            select(User).where((User.email == email) | (User.username == username))
        )
        if existing.scalar_one_or_none():
            raise AuthenticationError("User with this email or username already exists")

        # Create user
        user = User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=hash_password(password),
            auth_provider=AuthProvider.LOCAL.value,
            is_verified=True,  # Auto-verify for demo
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)

        # Generate tokens
        tokens = self._generate_tokens(user)

        return {
            **tokens,
            "user": self._user_to_dict(user),
        }

    async def login(self, db: AsyncSession, email: str, password: str) -> dict:
        """Authenticate user with email/password."""
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not user.hashed_password:
            raise AuthenticationError("Invalid email or password")

        if not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("Account is deactivated")

        # Update last login
        user.last_login_at = datetime.now(timezone.utc)
        await db.flush()

        tokens = self._generate_tokens(user)
        return {
            **tokens,
            "user": self._user_to_dict(user),
        }

    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> Optional[User]:
        """Get a user by their ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def oauth_login(
        self,
        db: AsyncSession,
        provider: str,
        provider_id: str,
        email: str,
        username: str,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> dict:
        """Handle OAuth login/registration."""
        # Check if user exists by provider ID
        result = await db.execute(
            select(User).where(
                (User.provider_id == provider_id) & (User.auth_provider == provider)
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            # Check by email
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()

        if user:
            # Update OAuth details
            user.provider_id = provider_id
            user.last_login_at = datetime.now(timezone.utc)
            if avatar_url:
                user.avatar_url = avatar_url
            if access_token and provider == "github":
                user.github_access_token = access_token
        else:
            # Create new user
            user = User(
                email=email,
                username=username,
                full_name=full_name,
                avatar_url=avatar_url,
                auth_provider=provider,
                provider_id=provider_id,
                is_verified=True,
                github_access_token=access_token if provider == "github" else None,
            )
            db.add(user)

        await db.flush()
        await db.refresh(user)

        tokens = self._generate_tokens(user)
        return {
            **tokens,
            "user": self._user_to_dict(user),
        }

    def _generate_tokens(self, user: User) -> dict:
        """Generate JWT access and refresh tokens."""
        token_data = {"sub": user.id, "email": user.email, "role": user.role}
        return {
            "access_token": create_access_token(token_data),
            "refresh_token": create_refresh_token(token_data),
            "token_type": "bearer",
            "expires_in": 86400,
        }

    def _user_to_dict(self, user: User) -> dict:
        """Convert user model to dictionary."""
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "role": user.role,
            "auth_provider": user.auth_provider,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "organization_name": user.organization_name,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        }
