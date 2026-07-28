"""
CodeSage AI — Chat API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import (
    ChatMessageRequest, ChatMessageResponse, ChatSessionCreate,
    ChatSessionResponse, ChatResponse,
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["AI Chat"])
chat_service = ChatService()


@router.post("/sessions", response_model=ChatSessionResponse, status_code=201)
async def create_session(
    data: ChatSessionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new chat session."""
    session = await chat_service.create_session(
        db, user_id=user.id, title=data.title or "New Chat",
        code_context=data.code_context, language=data.language,
        analysis_id=data.analysis_id,
    )
    return ChatSessionResponse(
        id=session.id, title=session.title, language=session.language,
        message_count=0, created_at=session.created_at, updated_at=session.updated_at,
    )


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_sessions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all chat sessions for the current user."""
    sessions = await chat_service.get_sessions(db, user.id)
    return [
        ChatSessionResponse(
            id=s.id, title=s.title, language=s.language,
            message_count=0, created_at=s.created_at, updated_at=s.updated_at,
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
async def get_messages(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all messages in a chat session."""
    messages = await chat_service.get_messages(db, session_id)
    return [
        ChatMessageResponse(
            id=m.id, role=m.role, content=m.content,
            code_snippet=m.code_snippet, created_at=m.created_at,
        )
        for m in messages
    ]


@router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(
    session_id: str,
    data: ChatMessageRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message and get an AI response."""
    assistant_msg = await chat_service.send_message(
        db, session_id=session_id, user_message=data.message,
        code_context=data.code_context,
    )
    return ChatResponse(
        session_id=session_id,
        message=ChatMessageResponse(
            id=assistant_msg.id, role=assistant_msg.role,
            content=assistant_msg.content, code_snippet=assistant_msg.code_snippet,
            created_at=assistant_msg.created_at,
        ),
        suggestions=["Explain this code", "Find bugs", "Generate tests", "Refactor this"],
    )
