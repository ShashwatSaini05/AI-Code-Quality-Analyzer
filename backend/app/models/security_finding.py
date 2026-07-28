"""
CodeSage AI — Security & Bug Prediction Models
Stores security vulnerabilities, bug predictions, and technical debt records.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SecurityFinding(Base):
    """Security vulnerability found during analysis."""

    __tablename__ = "security_findings"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # Vulnerability details
    vulnerability_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # critical, high, medium, low, info
    cvss_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    cwe_id: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Location
    line_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    code_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Description
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    real_world_example: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    is_false_positive: Mapped[bool] = mapped_column(default=False)
    is_resolved: Mapped[bool] = mapped_column(default=False)

    # Foreign keys
    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    analysis = relationship("Analysis", back_populates="security_findings")

    def __repr__(self) -> str:
        return f"<SecurityFinding(type={self.vulnerability_type}, severity={self.severity})>"


class BugPrediction(Base):
    """ML-based bug prediction result for a code entity."""

    __tablename__ = "bug_predictions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # Entity info
    entity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # function, class, module

    # Predictions
    bug_probability: Mapped[float] = mapped_column(Float, nullable=False)
    maintainability_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    defect_likelihood: Mapped[str | None] = mapped_column(String(20), nullable=True)  # low, medium, high
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Feature importances (JSON)
    feature_importances_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Foreign keys
    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    analysis = relationship("Analysis", back_populates="bug_predictions")

    def __repr__(self) -> str:
        return f"<BugPrediction(entity={self.entity_name}, probability={self.bug_probability})>"


class TechDebtRecord(Base):
    """Technical debt estimation for an analysis."""

    __tablename__ = "tech_debt_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # Debt metrics
    debt_score: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_fix_hours: Mapped[float] = mapped_column(Float, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)  # critical, high, medium, low
    business_impact: Mapped[str] = mapped_column(String(20), nullable=False)  # high, medium, low
    developer_effort: Mapped[str] = mapped_column(String(20), nullable=False)  # high, medium, low

    # Details
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Foreign keys
    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self) -> str:
        return f"<TechDebtRecord(score={self.debt_score}, hours={self.estimated_fix_hours})>"
