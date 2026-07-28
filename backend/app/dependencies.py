"""
CodeSage AI — Dependencies
Provides a default mock user so no authentication is required.
"""

from app.models.user import User


# Default mock user — all endpoints use this automatically
_mock_user = User(
    id="default-user",
    email="developer@codesage.ai",
    username="Developer",
    full_name="CodeSage Developer",
    role="admin",
    auth_provider="local",
    is_active=True,
    is_verified=True,
)


async def get_current_user() -> User:
    """Return a default user — authentication is disabled."""
    return _mock_user


async def get_optional_user() -> User:
    """Return a default user — authentication is disabled."""
    return _mock_user
