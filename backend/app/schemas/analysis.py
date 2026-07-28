"""
CodeSage AI — Analysis Schemas
Pydantic models for code analysis request/response validation.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ── Issue / Finding Schemas ──────────────────────────────────

class CodeIssue(BaseModel):
    """Schema for a single code issue with AI explanation."""
    id: str = ""
    type: str  # bug, smell, vulnerability, performance, style
    severity: str  # critical, high, medium, low, info
    title: str
    description: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    explanation: str  # Plain English explanation
    why_it_matters: str
    real_world_example: Optional[str] = None
    how_to_fix: str
    expected_improvement: Optional[str] = None


class SecurityVulnerability(BaseModel):
    """Schema for a security vulnerability."""
    type: str
    severity: str
    cvss_score: Optional[float] = None
    cwe_id: Optional[str] = None
    title: str
    description: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: str
    real_world_example: Optional[str] = None


class PerformanceIssue(BaseModel):
    """Schema for a performance issue."""
    type: str  # nested_loop, expensive_recursion, memory_leak, etc.
    severity: str
    title: str
    description: str
    current_approach: Optional[str] = None
    suggested_approach: Optional[str] = None
    current_complexity: Optional[str] = None
    suggested_complexity: Optional[str] = None
    memory_impact: Optional[str] = None
    line_number: Optional[int] = None


class RefactoringSuggestion(BaseModel):
    """Schema for a refactoring suggestion."""
    type: str  # naming, design_pattern, duplication, solid, clean_arch
    title: str
    description: str
    current_code: Optional[str] = None
    suggested_code: Optional[str] = None
    principle: Optional[str] = None
    benefit: str
    effort: str  # low, medium, high
    priority: str  # low, medium, high


class ComplexityMetrics(BaseModel):
    """Schema for complexity metrics."""
    cyclomatic_complexity: float = 0
    cognitive_complexity: float = 0
    maintainability_index: float = 0
    halstead_vocabulary: float = 0
    halstead_length: float = 0
    halstead_difficulty: float = 0
    halstead_effort: float = 0
    halstead_volume: float = 0
    max_nesting_depth: int = 0
    avg_function_length: float = 0
    total_functions: int = 0
    total_classes: int = 0


class TimeSpaceComplexity(BaseModel):
    """Schema for time/space complexity estimation."""
    time_complexity: str = "O(1)"
    space_complexity: str = "O(1)"
    worst_case: str = "O(1)"
    average_case: str = "O(1)"
    best_case: str = "O(1)"
    explanation: str = ""
    suggestions: list[str] = []


class MemoryAnalysis(BaseModel):
    """Schema for memory usage analysis."""
    estimated_memory: str = "Low"
    object_creation_count: int = 0
    stack_depth: int = 0
    heap_usage: str = "Minimal"
    recursive_depth: Optional[int] = None
    suggestions: list[str] = []


class BugPredictionResult(BaseModel):
    """Schema for bug prediction results."""
    bug_probability: float = 0.0
    maintainability_score: float = 0.0
    defect_likelihood: str = "low"
    risk_score: float = 0.0
    confidence: float = 0.0
    top_risk_factors: list[dict[str, Any]] = []


class TechDebtEstimation(BaseModel):
    """Schema for technical debt estimation."""
    debt_score: float = 0.0
    estimated_fix_hours: float = 0.0
    priority: str = "low"
    business_impact: str = "low"
    developer_effort: str = "low"
    breakdown: list[dict[str, Any]] = []


class DocumentationResult(BaseModel):
    """Schema for generated documentation."""
    function_docs: list[dict[str, str]] = []
    class_docs: list[dict[str, str]] = []
    readme: Optional[str] = None
    api_docs: Optional[str] = None


class TestGenerationResult(BaseModel):
    """Schema for generated unit tests."""
    test_code: str = ""
    framework: str = ""
    test_count: int = 0
    coverage_areas: list[str] = []


class SimilarityResult(BaseModel):
    """Schema for code similarity detection."""
    has_duplicates: bool = False
    duplicate_blocks: list[dict[str, Any]] = []
    overall_similarity: float = 0.0


# ── Request Schemas ──────────────────────────────────────────

class AnalysisRequest(BaseModel):
    """Schema for submitting code for analysis."""
    code: str = Field(..., min_length=1, max_length=1_000_000)
    language: Optional[str] = None  # Auto-detect if None
    filename: Optional[str] = None
    project_id: Optional[str] = None
    options: Optional[dict[str, bool]] = Field(
        default_factory=lambda: {
            "quality": True,
            "security": True,
            "performance": True,
            "complexity": True,
            "refactoring": True,
            "bug_prediction": True,
            "documentation": True,
            "test_generation": True,
            "similarity": True,
            "tech_debt": True,
        }
    )


# ── Response Schemas ─────────────────────────────────────────

class ScoreBreakdown(BaseModel):
    """Schema for an individual score with explanation."""
    score: float
    grade: str  # A, B, C, D, F
    label: str
    explanation: str
    color: str  # CSS color for UI


class AnalysisResponse(BaseModel):
    """Complete analysis response with all metrics and findings."""
    id: str
    language: str
    filename: Optional[str] = None
    status: str

    # Line counts
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0

    # Scores
    overall_quality_score: float = 0
    scores: dict[str, ScoreBreakdown] = {}

    # Metrics
    complexity_metrics: Optional[ComplexityMetrics] = None
    time_space_complexity: Optional[TimeSpaceComplexity] = None
    memory_analysis: Optional[MemoryAnalysis] = None

    # Issues & Findings
    issues: list[CodeIssue] = []
    security_vulnerabilities: list[SecurityVulnerability] = []
    performance_issues: list[PerformanceIssue] = []
    refactoring_suggestions: list[RefactoringSuggestion] = []

    # Predictions
    bug_prediction: Optional[BugPredictionResult] = None
    tech_debt: Optional[TechDebtEstimation] = None

    # Generated content
    documentation: Optional[DocumentationResult] = None
    generated_tests: Optional[TestGenerationResult] = None
    similarity: Optional[SimilarityResult] = None

    # Processing info
    processing_time_ms: int = 0
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AnalysisListItem(BaseModel):
    """Compact analysis item for list views."""
    id: str
    language: str
    filename: Optional[str] = None
    overall_quality_score: float
    security_score: float
    total_lines: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisHistoryResponse(BaseModel):
    """Paginated analysis history."""
    items: list[AnalysisListItem]
    total: int
    page: int
    page_size: int
