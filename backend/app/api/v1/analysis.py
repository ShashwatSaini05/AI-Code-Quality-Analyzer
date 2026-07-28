"""
CodeSage AI — Analysis API Routes
Endpoints for submitting code analysis and retrieving results.
"""

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.analysis import Analysis
from app.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisHistoryResponse,
    AnalysisListItem,
)
from app.services.analysis_service import AnalysisService
from app.core.utils import compute_hash

router = APIRouter(prefix="/analysis", tags=["Code Analysis"])
analysis_service = AnalysisService()


@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_code(
    request: AnalysisRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit code for comprehensive AI analysis.
    Returns quality scores, security findings, performance metrics,
    bug predictions, and refactoring suggestions.
    """
    try:
        # Run analysis pipeline
        result = analysis_service.analyze_code(
            code=request.code,
            language=request.language,
            filename=request.filename,
            options=request.options,
        )

        # Persist to database
        line_counts = result.get("line_counts", {})
        complexity = result.get("complexity_metrics", {})
        scores = result.get("scores", {})
        time_space = result.get("time_space_complexity", {})

        analysis = Analysis(
            code_content=request.code,
            code_hash=result.get("code_hash", compute_hash(request.code)),
            language=result.get("language", "unknown"),
            filename=request.filename,
            total_lines=line_counts.get("total", 0),
            code_lines=line_counts.get("code", 0),
            comment_lines=line_counts.get("comment", 0),
            blank_lines=line_counts.get("blank", 0),
            overall_quality_score=result.get("overall_quality_score", 0),
            readability_score=scores.get("readability", {}).get("score", 0),
            maintainability_score=scores.get("maintainability", {}).get("score", 0),
            performance_score=scores.get("performance", {}).get("score", 0),
            security_score=scores.get("security", {}).get("score", 0),
            scalability_score=scores.get("scalability", {}).get("score", 0),
            documentation_score=scores.get("documentation", {}).get("score", 0),
            architecture_score=scores.get("architecture", {}).get("score", 0),
            cyclomatic_complexity=complexity.get("cyclomatic_complexity"),
            cognitive_complexity=complexity.get("cognitive_complexity"),
            maintainability_index=complexity.get("maintainability_index"),
            max_nesting_depth=complexity.get("max_nesting_depth"),
            avg_function_length=complexity.get("avg_function_length"),
            halstead_vocabulary=complexity.get("halstead_vocabulary"),
            halstead_length=complexity.get("halstead_length"),
            halstead_difficulty=complexity.get("halstead_difficulty"),
            halstead_effort=complexity.get("halstead_effort"),
            halstead_volume=complexity.get("halstead_volume"),
            time_complexity=time_space.get("time_complexity"),
            space_complexity=time_space.get("space_complexity"),
            time_complexity_worst=time_space.get("worst_case"),
            time_complexity_best=time_space.get("best_case"),
            time_complexity_avg=time_space.get("average_case"),
            bug_probability=result.get("bug_prediction", {}).get("bug_probability") if result.get("bug_prediction") else None,
            defect_risk_score=result.get("bug_prediction", {}).get("risk_score") if result.get("bug_prediction") else None,
            tech_debt_score=result.get("tech_debt", {}).get("debt_score") if result.get("tech_debt") else None,
            estimated_fix_hours=result.get("tech_debt", {}).get("estimated_fix_hours") if result.get("tech_debt") else None,
            issues_json=json.dumps(result.get("issues", [])),
            suggestions_json=json.dumps(result.get("refactoring_suggestions", [])),
            security_findings_json=json.dumps(result.get("security_vulnerabilities", [])),
            performance_issues_json=json.dumps(result.get("performance_issues", [])),
            refactoring_suggestions_json=json.dumps(result.get("refactoring_suggestions", [])),
            generated_docs_json=json.dumps(result.get("documentation")) if result.get("documentation") else None,
            generated_tests_json=json.dumps(result.get("generated_tests")) if result.get("generated_tests") else None,
            status="completed",
            processing_time_ms=result.get("processing_time_ms", 0),
            user_id=user.id,
            project_id=request.project_id,
        )

        db.add(analysis)
        await db.flush()
        await db.refresh(analysis)

        # Build response
        return AnalysisResponse(
            id=analysis.id,
            language=result["language"],
            filename=request.filename,
            status="completed",
            total_lines=line_counts.get("total", 0),
            code_lines=line_counts.get("code", 0),
            comment_lines=line_counts.get("comment", 0),
            blank_lines=line_counts.get("blank", 0),
            overall_quality_score=result.get("overall_quality_score", 0),
            scores={k: {"score": v.get("score", 0), "grade": v.get("grade", "C"), "label": v.get("label", k), "explanation": v.get("explanation", ""), "color": v.get("color", "#666")} for k, v in scores.items()},
            complexity_metrics=complexity,
            time_space_complexity=time_space,
            memory_analysis=result.get("memory_analysis"),
            issues=result.get("issues", []),
            security_vulnerabilities=result.get("security_vulnerabilities", []),
            performance_issues=result.get("performance_issues", []),
            refactoring_suggestions=result.get("refactoring_suggestions", []),
            bug_prediction=result.get("bug_prediction"),
            tech_debt=result.get("tech_debt"),
            documentation=result.get("documentation"),
            generated_tests=result.get("generated_tests"),
            processing_time_ms=result.get("processing_time_ms", 0),
            created_at=analysis.created_at,
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/history", response_model=AnalysisHistoryResponse)
async def get_analysis_history(
    page: int = 1,
    page_size: int = 20,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated analysis history for the current user."""
    offset = (page - 1) * page_size

    # Count total
    count_result = await db.execute(
        select(func.count(Analysis.id)).where(Analysis.user_id == user.id)
    )
    total = count_result.scalar() or 0

    # Fetch page
    result = await db.execute(
        select(Analysis)
        .where(Analysis.user_id == user.id)
        .order_by(desc(Analysis.created_at))
        .offset(offset)
        .limit(page_size)
    )
    analyses = result.scalars().all()

    return AnalysisHistoryResponse(
        items=[
            AnalysisListItem(
                id=a.id,
                language=a.language,
                filename=a.filename,
                overall_quality_score=a.overall_quality_score,
                security_score=a.security_score,
                total_lines=a.total_lines,
                status=a.status,
                created_at=a.created_at,
            )
            for a in analyses
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific analysis result by ID."""
    result = await db.execute(
        select(Analysis).where(
            (Analysis.id == analysis_id) & (Analysis.user_id == user.id)
        )
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")

    # Rebuild response from stored data
    scores = {}
    for key in ["readability", "maintainability", "performance", "security", "scalability", "documentation", "architecture"]:
        score_val = getattr(analysis, f"{key}_score", 0)
        grade = "A" if score_val >= 90 else "B" if score_val >= 80 else "C" if score_val >= 70 else "D" if score_val >= 60 else "F"
        scores[key] = {"score": score_val, "grade": grade, "label": key.title(), "explanation": "", "color": "#10b981" if score_val >= 80 else "#f59e0b" if score_val >= 60 else "#ef4444"}

    return AnalysisResponse(
        id=analysis.id,
        language=analysis.language,
        filename=analysis.filename,
        status=analysis.status,
        total_lines=analysis.total_lines,
        code_lines=analysis.code_lines,
        comment_lines=analysis.comment_lines,
        blank_lines=analysis.blank_lines,
        overall_quality_score=analysis.overall_quality_score,
        scores=scores,
        complexity_metrics={
            "cyclomatic_complexity": analysis.cyclomatic_complexity or 0,
            "cognitive_complexity": analysis.cognitive_complexity or 0,
            "maintainability_index": analysis.maintainability_index or 0,
            "max_nesting_depth": analysis.max_nesting_depth or 0,
            "avg_function_length": analysis.avg_function_length or 0,
            "halstead_vocabulary": analysis.halstead_vocabulary or 0,
            "halstead_length": analysis.halstead_length or 0,
            "halstead_difficulty": analysis.halstead_difficulty or 0,
            "halstead_effort": analysis.halstead_effort or 0,
            "halstead_volume": analysis.halstead_volume or 0,
        },
        issues=json.loads(analysis.issues_json) if analysis.issues_json else [],
        security_vulnerabilities=json.loads(analysis.security_findings_json) if analysis.security_findings_json else [],
        performance_issues=json.loads(analysis.performance_issues_json) if analysis.performance_issues_json else [],
        refactoring_suggestions=json.loads(analysis.refactoring_suggestions_json) if analysis.refactoring_suggestions_json else [],
        processing_time_ms=analysis.processing_time_ms or 0,
        created_at=analysis.created_at,
    )


@router.get("/stats/dashboard")
async def get_dashboard_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard statistics for the current user."""
    # Total analyses
    count_result = await db.execute(
        select(func.count(Analysis.id)).where(Analysis.user_id == user.id)
    )
    total_analyses = count_result.scalar() or 0

    # Average quality score
    avg_result = await db.execute(
        select(func.avg(Analysis.overall_quality_score)).where(Analysis.user_id == user.id)
    )
    avg_quality = round(avg_result.scalar() or 0, 1)

    # Recent analyses
    recent_result = await db.execute(
        select(Analysis)
        .where(Analysis.user_id == user.id)
        .order_by(desc(Analysis.created_at))
        .limit(5)
    )
    recent = [
        {
            "id": a.id,
            "language": a.language,
            "filename": a.filename,
            "score": a.overall_quality_score,
            "created_at": a.created_at.isoformat(),
        }
        for a in recent_result.scalars().all()
    ]

    # Language distribution
    lang_result = await db.execute(
        select(Analysis.language, func.count(Analysis.id))
        .where(Analysis.user_id == user.id)
        .group_by(Analysis.language)
    )
    languages = {row[0]: row[1] for row in lang_result.all()}

    return {
        "total_analyses": total_analyses,
        "avg_quality_score": avg_quality,
        "recent_analyses": recent,
        "language_distribution": languages,
        "total_lines_analyzed": 0,
        "security_issues_found": 0,
    }
