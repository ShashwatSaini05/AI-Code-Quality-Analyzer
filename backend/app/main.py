"""
CodeSage AI — FastAPI Application Entry Point
AI-Powered Intelligent Code Quality Analyzer

This module initializes the FastAPI application with all middleware,
routes, and lifecycle events configured.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.config import get_settings
from app.database import init_db, close_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    # ── Startup ──────────────────────────────────────────
    print("[+] Starting CodeSage AI...")
    await init_db()
    print("[+] Database initialized")
    print(f"[*] Environment: {settings.app_env}")
    print(f"[*] API Docs: http://localhost:8000/docs")

    yield

    # ── Shutdown ─────────────────────────────────────────
    print("[-] Shutting down CodeSage AI...")
    await close_db()


# ── Create FastAPI Application ────────────────────────────────
app = FastAPI(
    title="CodeSage AI",
    description=(
        "AI-Powered Intelligent Code Quality Analyzer.\n\n"
        "Provides comprehensive code analysis including quality scoring, "
        "security scanning, performance optimization, bug prediction, "
        "and AI-powered explanations."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS Middleware ───────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handler ─────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler for unhandled errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal error occurred",
            "type": type(exc).__name__,
        },
    )


# ── Include API Routes ───────────────────────────────────────
app.include_router(api_router)


# ── Health Check ──────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "CodeSage AI",
        "version": "1.0.0",
        "environment": settings.app_env,
    }


@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "CodeSage AI",
        "description": "AI-Powered Intelligent Code Quality Analyzer",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "api": "/api/v1",
    }
