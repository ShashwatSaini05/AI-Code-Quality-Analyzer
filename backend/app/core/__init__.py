"""
CodeSage AI — Core Exceptions
Custom exception classes for structured error handling.
"""

from typing import Any, Optional


class CodeSageError(Exception):
    """Base exception for all CodeSage errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(CodeSageError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(CodeSageError):
    """Raised when user lacks required permissions."""
    pass


class AnalysisError(CodeSageError):
    """Raised when code analysis fails."""
    pass


class UnsupportedLanguageError(CodeSageError):
    """Raised when an unsupported programming language is provided."""
    pass


class RateLimitError(CodeSageError):
    """Raised when rate limit is exceeded."""
    pass


class ExternalServiceError(CodeSageError):
    """Raised when an external service (GitHub, LLM, etc.) fails."""
    pass


class ValidationError(CodeSageError):
    """Raised when input validation fails."""
    pass


class ModelNotFoundError(CodeSageError):
    """Raised when an ML model file is not found."""
    pass
