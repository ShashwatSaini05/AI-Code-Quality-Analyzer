"""
CodeSage AI — Chat Schemas
Pydantic models for AI chat request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    """Schema for sending a chat message."""
    message: str = Field(..., min_length=1, max_length=10000)
    code_context: Optional[str] = None
    language: Optional[str] = None


class ChatMessageResponse(BaseModel):
    """Schema for a single chat message response."""
    id: str
    role: str  # user, assistant, system
    content: str
    code_snippet: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionResponse(BaseModel):
    """Schema for a chat session."""
    id: str
    title: str
    language: Optional[str] = None
    message_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionCreate(BaseModel):
    """Schema for creating a new chat session."""
    title: Optional[str] = "New Chat"
    code_context: Optional[str] = None
    language: Optional[str] = None
    analysis_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Schema for the AI chat response."""
    session_id: str
    message: ChatMessageResponse
    suggestions: list[str] = []
