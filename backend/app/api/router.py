"""
CodeSage AI — API Router
Aggregates all v1 API routes.
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.chat import router as chat_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(analysis_router)
api_router.include_router(chat_router)
