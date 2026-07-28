"""
CodeSage AI — Utility Functions
Shared helper functions used across the application.
"""

import hashlib
import re
import uuid
from datetime import datetime, timezone
from typing import Any


def generate_uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Get current UTC timestamp."""
    return datetime.now(timezone.utc)


def compute_hash(content: str) -> str:
    """Compute SHA-256 hash of content for deduplication."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def detect_language(code: str, filename: str | None = None) -> str:
    """
    Detect programming language from filename extension or code heuristics.
    Returns lowercase language name.
    """
    if filename:
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".java": "java",
            ".c": "c",
            ".h": "c",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".hpp": "cpp",
            ".go": "go",
            ".rs": "rust",
            ".php": "php",
        }
        for ext, lang in ext_map.items():
            if filename.endswith(ext):
                return lang

    # Heuristic-based detection from code content
    heuristics: list[tuple[str, str]] = [
        (r"^(import\s+\w+|from\s+\w+\s+import|def\s+\w+|class\s+\w+.*:)", "python"),
        (r"(function\s+\w+|const\s+\w+\s*=|let\s+\w+|var\s+\w+|=>)", "javascript"),
        (r"(interface\s+\w+|type\s+\w+\s*=|:\s*(string|number|boolean))", "typescript"),
        (r"(public\s+class|private\s+\w+|System\.out\.println)", "java"),
        (r"(#include\s*<|int\s+main\s*\(|printf\s*\()", "c"),
        (r"(std::|cout\s*<<|namespace\s+\w+|template\s*<)", "cpp"),
        (r"(func\s+\w+|package\s+\w+|fmt\.Print)", "go"),
        (r"(fn\s+\w+|let\s+mut|impl\s+\w+|use\s+\w+::)", "rust"),
        (r"(<\?php|\$\w+\s*=|function\s+\w+\s*\(.*\)\s*{)", "php"),
    ]

    for pattern, lang in heuristics:
        if re.search(pattern, code, re.MULTILINE):
            return lang

    return "unknown"


def count_lines(code: str) -> dict[str, int]:
    """Count total, blank, comment, and code lines."""
    lines = code.split("\n")
    total = len(lines)
    blank = sum(1 for line in lines if not line.strip())
    comment = sum(
        1 for line in lines
        if line.strip().startswith(("#", "//", "/*", "*", "'''", '"""'))
    )
    return {
        "total": total,
        "blank": blank,
        "comment": comment,
        "code": total - blank - comment,
    }


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max_length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_score(score: float) -> str:
    """Format a 0-100 score with a letter grade."""
    if score >= 90:
        return f"{score:.1f} (A)"
    elif score >= 80:
        return f"{score:.1f} (B)"
    elif score >= 70:
        return f"{score:.1f} (C)"
    elif score >= 60:
        return f"{score:.1f} (D)"
    else:
        return f"{score:.1f} (F)"


def sanitize_code(code: str) -> str:
    """Basic sanitization of code input."""
    # Remove null bytes
    code = code.replace("\x00", "")
    # Limit size to 1MB
    max_size = 1_000_000
    if len(code) > max_size:
        code = code[:max_size]
    return code


def merge_dicts(*dicts: dict[str, Any]) -> dict[str, Any]:
    """Deep merge multiple dictionaries."""
    result: dict[str, Any] = {}
    for d in dicts:
        for key, value in d.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value
    return result
