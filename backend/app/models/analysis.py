"""
CodeSage AI — Analysis Models
Stores code analysis results and detailed metrics.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Analysis(Base):
    """Primary analysis result for a code submission."""

    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # Code info
    code_content: Mapped[str] = mapped_column(Text, nullable=False)
    code_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    filename: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Line counts
    total_lines: Mapped[int] = mapped_column(Integer, default=0)
    code_lines: Mapped[int] = mapped_column(Integer, default=0)
    comment_lines: Mapped[int] = mapped_column(Integer, default=0)
    blank_lines: Mapped[int] = mapped_column(Integer, default=0)

    # ── Scores (0-100) ──────────────────────────────────────
    overall_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    readability_score: Mapped[float] = mapped_column(Float, default=0.0)
    maintainability_score: Mapped[float] = mapped_column(Float, default=0.0)
    performance_score: Mapped[float] = mapped_column(Float, default=0.0)
    security_score: Mapped[float] = mapped_column(Float, default=0.0)
    scalability_score: Mapped[float] = mapped_column(Float, default=0.0)
    documentation_score: Mapped[float] = mapped_column(Float, default=0.0)
    architecture_score: Mapped[float] = mapped_column(Float, default=0.0)

    # ── Complexity Metrics ──────────────────────────────────
    cyclomatic_complexity: Mapped[float | None] = mapped_column(Float, nullable=True)
    cognitive_complexity: Mapped[float | None] = mapped_column(Float, nullable=True)
    maintainability_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_nesting_depth: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_function_length: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Halstead Metrics ────────────────────────────────────
    halstead_vocabulary: Mapped[float | None] = mapped_column(Float, nullable=True)
    halstead_length: Mapped[float | None] = mapped_column(Float, nullable=True)
    halstead_difficulty: Mapped[float | None] = mapped_column(Float, nullable=True)
    halstead_effort: Mapped[float | None] = mapped_column(Float, nullable=True)
    halstead_volume: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Time/Space Complexity ───────────────────────────────
    time_complexity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    space_complexity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    time_complexity_worst: Mapped[str | None] = mapped_column(String(50), nullable=True)
    time_complexity_best: Mapped[str | None] = mapped_column(String(50), nullable=True)
    time_complexity_avg: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # ── Bug Prediction ──────────────────────────────────────
    bug_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    defect_risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Technical Debt ──────────────────────────────────────
    tech_debt_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_fix_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── AI Explanations (JSON stored as text) ───────────────
    issues_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggestions_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    security_findings_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    performance_issues_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    refactoring_suggestions_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_docs_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_tests_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Processing ──────────────────────────────────────────
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, processing, completed, failed
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Foreign Keys ────────────────────────────────────────
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="analyses")
    project = relationship("Project", back_populates="analyses")
    security_findings = relationship(
        "SecurityFinding", back_populates="analysis", cascade="all, delete-orphan"
    )
    bug_predictions = relationship(
        "BugPrediction", back_populates="analysis", cascade="all, delete-orphan"
    )
    metrics = relationship(
        "AnalysisMetric", back_populates="analysis", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Analysis(id={self.id}, language={self.language}, score={self.overall_quality_score})>"


class AnalysisMetric(Base):
    """Detailed per-function or per-class metrics for an analysis."""

    __tablename__ = "analysis_metrics"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # What this metric is for
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # function, class, module
    entity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_line: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Metrics
    complexity: Mapped[float | None] = mapped_column(Float, nullable=True)
    lines_of_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parameters: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nesting_depth: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cognitive_complexity: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationship
    analysis = relationship("Analysis", back_populates="metrics")

    def __repr__(self) -> str:
        return f"<AnalysisMetric(entity={self.entity_name}, complexity={self.complexity})>"
