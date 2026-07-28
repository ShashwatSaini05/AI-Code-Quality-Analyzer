"""
CodeSage AI — Chat Service
Handles AI-powered code chat conversations.
"""

import re
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import ChatSession, ChatMessage


class ChatService:
    """Service for AI code chat functionality."""

    async def create_session(
        self, db: AsyncSession, user_id: str, title: str = "New Chat",
        code_context: Optional[str] = None, language: Optional[str] = None,
        analysis_id: Optional[str] = None,
    ) -> ChatSession:
        session = ChatSession(
            user_id=user_id, title=title, code_context=code_context,
            language=language, analysis_id=analysis_id,
        )
        db.add(session)
        await db.flush()
        await db.refresh(session)
        return session

    async def get_sessions(self, db: AsyncSession, user_id: str) -> list[ChatSession]:
        result = await db.execute(
            select(ChatSession).where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get_messages(self, db: AsyncSession, session_id: str) -> list[ChatMessage]:
        result = await db.execute(
            select(ChatMessage).where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        return list(result.scalars().all())

    async def send_message(
        self, db: AsyncSession, session_id: str, user_message: str,
        code_context: Optional[str] = None,
    ) -> ChatMessage:
        # Save user message
        user_msg = ChatMessage(session_id=session_id, role="user", content=user_message)
        db.add(user_msg)

        # Generate AI response (rule-based for now — LLM integration hook)
        ai_response = self._generate_response(user_message, code_context)

        assistant_msg = ChatMessage(
            session_id=session_id, role="assistant", content=ai_response,
        )
        db.add(assistant_msg)
        await db.flush()
        await db.refresh(assistant_msg)
        return assistant_msg

    def _generate_response(self, message: str, code_context: Optional[str] = None) -> str:
        """Generate AI response using rule-based logic (LLM hook available)."""
        msg_lower = message.lower()

        if "explain" in msg_lower:
            if code_context:
                lines = code_context.split("\n")
                return (
                    f"## Code Explanation\n\n"
                    f"This code has **{len(lines)} lines** and appears to be a "
                    f"{'function-based' if 'def ' in code_context or 'function' in code_context else 'procedural'} implementation.\n\n"
                    f"### Key observations:\n"
                    f"- The code {'uses classes' if 'class ' in code_context else 'is procedural'}\n"
                    f"- {'Contains loops for iteration' if 'for ' in code_context or 'while ' in code_context else 'No loops detected'}\n"
                    f"- {'Includes error handling' if 'try' in code_context or 'catch' in code_context or 'except' in code_context else 'No error handling detected'}\n\n"
                    f"Would you like me to analyze specific parts in more detail?"
                )
            return "Please provide some code context, and I'll explain it in detail!"

        if "bug" in msg_lower or "error" in msg_lower:
            return (
                "## Bug Analysis\n\n"
                "I'll analyze the code for potential bugs:\n\n"
                "1. **Missing error handling** — Consider wrapping risky operations in try/except blocks\n"
                "2. **Edge cases** — Check for empty inputs, null values, and boundary conditions\n"
                "3. **Type mismatches** — Ensure consistent data types throughout the code\n\n"
                "Would you like me to look at a specific section?"
            )

        if "refactor" in msg_lower or "improve" in msg_lower or "rewrite" in msg_lower:
            return (
                "## Refactoring Suggestions\n\n"
                "Here are my recommendations:\n\n"
                "1. **Extract Method** — Break large functions into smaller, focused ones\n"
                "2. **Use meaningful names** — Replace abbreviations with descriptive identifiers\n"
                "3. **Apply SOLID principles** — Especially Single Responsibility and Dependency Inversion\n"
                "4. **Add type hints** — Improve code documentation and IDE support\n"
                "5. **Use guard clauses** — Replace nested if-else with early returns\n\n"
                "Want me to generate refactored code?"
            )

        if "test" in msg_lower:
            return (
                "## Test Generation\n\n"
                "I can help generate tests! Here's my approach:\n\n"
                "1. **Unit tests** for individual functions\n"
                "2. **Edge case tests** for boundary conditions\n"
                "3. **Error handling tests** for exception paths\n"
                "4. **Integration tests** for component interactions\n\n"
                "Which type would you like me to generate?"
            )

        if any(word in msg_lower for word in ["convert", "translate", "rust", "java", "python", "typescript"]):
            return (
                "## Code Conversion\n\n"
                "I can help convert your code to another language! Please specify:\n\n"
                "1. **Target language** (e.g., Python → Rust)\n"
                "2. **Style preferences** (idiomatic, direct translation, etc.)\n"
                "3. **Framework preferences** if applicable\n\n"
                "What would you like to convert to?"
            )

        return (
            "## CodeSage AI Assistant\n\n"
            "I can help you with:\n\n"
            "- 🔍 **Explain code** — \"Explain this function\"\n"
            "- 🐛 **Find bugs** — \"Find potential bugs\"\n"
            "- ✨ **Refactor** — \"Rewrite using async\"\n"
            "- 🔄 **Convert** — \"Convert to Rust\"\n"
            "- 🧪 **Test** — \"Generate unit tests\"\n"
            "- 📖 **Document** — \"Generate documentation\"\n\n"
            "How can I help you today?"
        )
