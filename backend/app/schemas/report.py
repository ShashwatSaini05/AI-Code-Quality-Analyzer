"""
CodeSage AI — Report Schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ReportRequest(BaseModel):
    """Schema for requesting a report generation."""
    analysis_id: str
    format: str = "json"  # json, pdf, docx, csv, html
    title: Optional[str] = None
    include_sections: list[str] = [
        "summary", "scores", "issues", "security",
        "performance", "complexity", "suggestions"
    ]


class ReportResponse(BaseModel):
    """Schema for report response."""
    id: str
    title: str
    format: str
    file_path: Optional[str] = None
    content: Optional[str] = None
    file_size: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}
