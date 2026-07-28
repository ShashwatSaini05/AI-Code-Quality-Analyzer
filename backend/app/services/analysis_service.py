"""
CodeSage AI — Analysis Service
Main orchestrator that coordinates all analyzers and produces the final analysis result.
"""

import json
import time
from typing import Any, Optional

from app.analyzers.base import BaseAnalyzer
from app.analyzers.python_analyzer import PythonAnalyzer
from app.analyzers.javascript_analyzer import JavaScriptAnalyzer, TypeScriptAnalyzer
from app.analyzers.java_analyzer import JavaAnalyzer
from app.analyzers.cpp_analyzer import CppAnalyzer, CAnalyzer
from app.analyzers.go_analyzer import GoAnalyzer
from app.analyzers.rust_analyzer import RustAnalyzer
from app.analyzers.php_analyzer import PHPAnalyzer
from app.services.security_analyzer import SecurityAnalyzerService
from app.services.performance_analyzer import PerformanceAnalyzerService
from app.core.utils import detect_language, compute_hash, sanitize_code


# ── Analyzer Registry ────────────────────────────────────────
# Maps language name to analyzer class — easy to extend

ANALYZER_REGISTRY: dict[str, type[BaseAnalyzer]] = {
    "python": PythonAnalyzer,
    "javascript": JavaScriptAnalyzer,
    "typescript": TypeScriptAnalyzer,
    "java": JavaAnalyzer,
    "c": CAnalyzer,
    "cpp": CppAnalyzer,
    "go": GoAnalyzer,
    "rust": RustAnalyzer,
    "php": PHPAnalyzer,
}


class AnalysisService:
    """
    Orchestrates the complete code analysis pipeline.
    Coordinates language-specific analyzers, security scanning,
    performance analysis, and score computation.
    """

    def __init__(self) -> None:
        self.security_analyzer = SecurityAnalyzerService()
        self.performance_analyzer = PerformanceAnalyzerService()

    def get_analyzer(self, language: str) -> BaseAnalyzer:
        """Get the appropriate analyzer for a language."""
        analyzer_class = ANALYZER_REGISTRY.get(language)
        if not analyzer_class:
            # Fallback to Python analyzer for unknown languages
            analyzer_class = PythonAnalyzer
        return analyzer_class()

    def analyze_code(
        self,
        code: str,
        language: Optional[str] = None,
        filename: Optional[str] = None,
        options: Optional[dict[str, bool]] = None,
    ) -> dict[str, Any]:
        """
        Run the complete analysis pipeline on the given code.

        Returns a comprehensive result dictionary with scores,
        metrics, issues, suggestions, and generated content.
        """
        start_time = time.perf_counter()

        # Sanitize input
        code = sanitize_code(code)

        # Detect language
        if not language or language == "auto":
            language = detect_language(code, filename)

        # Default options — all features enabled
        opts = options or {
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

        # ── Step 1: Static Analysis ─────────────────────────
        analyzer = self.get_analyzer(language)
        static_results = analyzer.analyze(code)

        # ── Step 2: Security Analysis ───────────────────────
        security_issues = []
        security_score = 100.0
        if opts.get("security", True):
            security_issues = self.security_analyzer.analyze(code, language)
            security_score = self.security_analyzer.calculate_security_score(security_issues)

        # Update security score in static results
        if "scores" in static_results and "security" in static_results["scores"]:
            static_results["scores"]["security"]["score"] = security_score

        # ── Step 3: Performance Analysis ────────────────────
        perf_results = {}
        if opts.get("performance", True):
            perf_results = self.performance_analyzer.analyze(code, language)

        # ── Step 4: Bug Prediction ──────────────────────────
        bug_prediction = None
        if opts.get("bug_prediction", True):
            bug_prediction = self._predict_bugs(static_results)

        # ── Step 5: Tech Debt Estimation ────────────────────
        tech_debt = None
        if opts.get("tech_debt", True):
            tech_debt = self._estimate_tech_debt(static_results, security_issues)

        # ── Step 6: Refactoring Suggestions ─────────────────
        refactoring = []
        if opts.get("refactoring", True):
            refactoring = self._generate_refactoring_suggestions(static_results, code, language)

        # ── Step 7: Documentation Generation ────────────────
        documentation = None
        if opts.get("documentation", True):
            documentation = self._generate_documentation(static_results, code, language)

        # ── Step 8: Test Generation ─────────────────────────
        tests = None
        if opts.get("test_generation", True):
            tests = self._generate_tests(static_results, code, language)

        # ── Step 9: Compute Overall Score ───────────────────
        scores = static_results.get("scores", {})
        overall_score = self._compute_overall_score(scores, security_score)

        # ── Step 10: Generate Issues List ───────────────────
        issues = self._generate_issues(static_results, code, language)

        # Calculate processing time
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)

        return {
            "language": language,
            "filename": filename,
            "code_hash": compute_hash(code),
            "status": "completed",

            # Line counts
            "line_counts": static_results.get("line_counts", {}),

            # Scores
            "overall_quality_score": overall_score,
            "scores": scores,

            # Complexity metrics
            "complexity_metrics": static_results.get("complexity", {}),

            # Time/Space complexity
            "time_space_complexity": perf_results.get("time_complexity", {}),

            # Memory analysis
            "memory_analysis": perf_results.get("memory_analysis", {}),

            # Issues & findings
            "issues": issues,
            "security_vulnerabilities": [
                {
                    "type": s.vulnerability_type,
                    "severity": s.severity,
                    "cvss_score": s.cvss_score,
                    "cwe_id": s.cwe_id,
                    "title": s.title,
                    "description": s.description,
                    "line_number": s.line_number,
                    "code_snippet": s.code_snippet,
                    "recommendation": s.recommendation,
                    "real_world_example": s.real_world_example,
                }
                for s in security_issues
            ],
            "performance_issues": [
                {
                    "type": p.type,
                    "severity": p.severity,
                    "title": p.title,
                    "description": p.description,
                    "current_approach": p.current_approach,
                    "suggested_approach": p.suggested_approach,
                    "current_complexity": p.current_complexity,
                    "suggested_complexity": p.suggested_complexity,
                    "memory_impact": p.memory_impact,
                    "line_number": p.line_number,
                }
                for p in perf_results.get("issues", [])
            ],
            "refactoring_suggestions": refactoring,

            # Predictions
            "bug_prediction": bug_prediction,
            "tech_debt": tech_debt,

            # Generated content
            "documentation": documentation,
            "generated_tests": tests,

            # Functions & classes info
            "functions": static_results.get("functions", []),
            "classes": static_results.get("classes", []),

            # Processing info
            "processing_time_ms": processing_time_ms,
        }

    def _compute_overall_score(self, scores: dict, security_score: float) -> float:
        """Compute weighted overall quality score."""
        weights = {
            "readability": 0.15,
            "maintainability": 0.20,
            "performance": 0.15,
            "security": 0.20,
            "scalability": 0.10,
            "documentation": 0.10,
            "architecture": 0.10,
        }

        total = 0.0
        total_weight = 0.0

        for key, weight in weights.items():
            if key in scores:
                score = scores[key].get("score", 0) if isinstance(scores[key], dict) else 0
                if key == "security":
                    score = security_score
                total += score * weight
                total_weight += weight

        if total_weight > 0:
            return round(total / total_weight, 1)
        return 50.0

    def _predict_bugs(self, static_results: dict) -> dict:
        """Predict bug probability based on code metrics."""
        complexity = static_results.get("complexity", {})

        cc = complexity.get("cyclomatic_complexity", 1)
        cog = complexity.get("cognitive_complexity", 0)
        mi = complexity.get("maintainability_index", 100)
        nesting = complexity.get("max_nesting_depth", 0)
        avg_func = complexity.get("avg_function_length", 0)
        halstead_effort = complexity.get("halstead_effort", 0)

        # Simple heuristic model (in production, use the trained XGBoost model)
        # Higher complexity → higher bug probability
        raw_probability = (
            min(cc / 50, 1.0) * 0.25 +
            min(cog / 100, 1.0) * 0.20 +
            (1 - mi / 100) * 0.20 +
            min(nesting / 10, 1.0) * 0.15 +
            min(avg_func / 100, 1.0) * 0.10 +
            min(halstead_effort / 100000, 1.0) * 0.10
        )

        bug_probability = round(min(raw_probability, 0.99), 3)
        risk_score = round(bug_probability * 100, 1)

        if bug_probability < 0.3:
            defect_likelihood = "low"
        elif bug_probability < 0.6:
            defect_likelihood = "medium"
        else:
            defect_likelihood = "high"

        return {
            "bug_probability": bug_probability,
            "maintainability_score": round(mi, 1),
            "defect_likelihood": defect_likelihood,
            "risk_score": risk_score,
            "confidence": round(0.85 - bug_probability * 0.2, 2),
            "top_risk_factors": [
                {"factor": "Cyclomatic Complexity", "value": cc, "impact": "high" if cc > 10 else "medium" if cc > 5 else "low"},
                {"factor": "Cognitive Complexity", "value": cog, "impact": "high" if cog > 20 else "medium" if cog > 10 else "low"},
                {"factor": "Maintainability Index", "value": mi, "impact": "high" if mi < 40 else "medium" if mi < 65 else "low"},
                {"factor": "Nesting Depth", "value": nesting, "impact": "high" if nesting > 4 else "medium" if nesting > 2 else "low"},
                {"factor": "Function Length", "value": avg_func, "impact": "high" if avg_func > 50 else "medium" if avg_func > 20 else "low"},
            ],
        }

    def _estimate_tech_debt(self, static_results: dict, security_issues: list) -> dict:
        """Estimate technical debt based on analysis results."""
        complexity = static_results.get("complexity", {})
        cc = complexity.get("cyclomatic_complexity", 1)
        mi = complexity.get("maintainability_index", 100)
        nesting = complexity.get("max_nesting_depth", 0)

        # Calculate debt score (0-100, higher = more debt)
        debt_score = max(0, min(100, 100 - mi))

        # Estimate fix hours
        fix_hours = round(
            cc * 0.5 +
            nesting * 1.0 +
            len(security_issues) * 2.0 +
            (100 - mi) * 0.1,
            1
        )

        # Priority
        if debt_score > 70 or any(s.severity == "critical" for s in security_issues):
            priority = "critical"
        elif debt_score > 50:
            priority = "high"
        elif debt_score > 30:
            priority = "medium"
        else:
            priority = "low"

        # Business impact
        business_impact = "high" if debt_score > 60 else "medium" if debt_score > 30 else "low"
        developer_effort = "high" if fix_hours > 20 else "medium" if fix_hours > 5 else "low"

        breakdown = []
        if cc > 10:
            breakdown.append({"category": "Complexity", "hours": round(cc * 0.3, 1), "description": "Reduce cyclomatic complexity by extracting methods"})
        if nesting > 3:
            breakdown.append({"category": "Nesting", "hours": round(nesting * 0.5, 1), "description": "Flatten nested structures using early returns or guard clauses"})
        if len(security_issues) > 0:
            breakdown.append({"category": "Security", "hours": round(len(security_issues) * 1.5, 1), "description": "Fix security vulnerabilities"})
        if mi < 65:
            breakdown.append({"category": "Maintainability", "hours": round((65 - mi) * 0.1, 1), "description": "Improve code structure and documentation"})

        return {
            "debt_score": round(debt_score, 1),
            "estimated_fix_hours": fix_hours,
            "priority": priority,
            "business_impact": business_impact,
            "developer_effort": developer_effort,
            "breakdown": breakdown,
        }

    def _generate_refactoring_suggestions(self, static_results: dict, code: str, language: str) -> list[dict]:
        """Generate refactoring suggestions based on analysis."""
        suggestions = []
        complexity = static_results.get("complexity", {})
        functions = static_results.get("functions", [])

        # Long functions
        for func in functions:
            loc = func.get("lines_of_code", 0)
            if loc > 30:
                suggestions.append({
                    "type": "long_function",
                    "title": f"Function '{func['name']}' is too long ({loc} lines)",
                    "description": f"Functions longer than 30 lines are harder to understand and maintain.",
                    "principle": "Single Responsibility Principle",
                    "benefit": "Improved readability and testability",
                    "effort": "medium",
                    "priority": "high" if loc > 50 else "medium",
                })

        # High complexity functions
        for func in functions:
            cc = func.get("complexity", 1)
            if cc > 10:
                suggestions.append({
                    "type": "high_complexity",
                    "title": f"Function '{func['name']}' has high complexity ({cc})",
                    "description": "Cyclomatic complexity above 10 indicates the function does too much.",
                    "principle": "Single Responsibility Principle",
                    "benefit": "Reduced bug risk and easier testing",
                    "effort": "high",
                    "priority": "high",
                })

        # Deep nesting
        nesting = complexity.get("max_nesting_depth", 0)
        if nesting > 3:
            suggestions.append({
                "type": "deep_nesting",
                "title": f"Code has deep nesting (depth: {nesting})",
                "description": "Deep nesting makes code hard to follow. Use early returns, guard clauses, or extract methods.",
                "principle": "Clean Code — Flat is better than nested",
                "benefit": "Improved readability and reduced cognitive load",
                "effort": "medium",
                "priority": "high",
            })

        # Missing documentation
        for func in functions:
            if not func.get("has_docstring", False):
                suggestions.append({
                    "type": "missing_docs",
                    "title": f"Function '{func['name']}' lacks documentation",
                    "description": "Public functions should have docstrings explaining purpose, parameters, and return values.",
                    "principle": "Self-documenting Code",
                    "benefit": "Easier onboarding and maintenance",
                    "effort": "low",
                    "priority": "low",
                })

        return suggestions

    def _generate_documentation(self, static_results: dict, code: str, language: str) -> dict:
        """Generate documentation for the code."""
        functions = static_results.get("functions", [])
        classes = static_results.get("classes", [])

        func_docs = []
        for func in functions:
            func_docs.append({
                "name": func["name"],
                "doc": f"Function '{func['name']}' — {func.get('parameters', 0)} parameters, "
                       f"{func.get('lines_of_code', 0)} lines, complexity: {func.get('complexity', 1)}.",
            })

        class_docs = []
        for cls in classes:
            class_docs.append({
                "name": cls["name"],
                "doc": f"Class '{cls['name']}' — {cls.get('methods', 0)} methods, "
                       f"{'inherits from ' + ', '.join(cls.get('parent_classes', [])) if cls.get('parent_classes') else 'no inheritance'}.",
            })

        return {
            "function_docs": func_docs,
            "class_docs": class_docs,
            "readme": f"# Code Documentation\n\nLanguage: {language}\n\n"
                      f"## Functions ({len(func_docs)})\n" +
                      "\n".join(f"- **{f['name']}**: {f['doc']}" for f in func_docs) +
                      f"\n\n## Classes ({len(class_docs)})\n" +
                      "\n".join(f"- **{c['name']}**: {c['doc']}" for c in class_docs),
        }

    def _generate_tests(self, static_results: dict, code: str, language: str) -> dict:
        """Generate unit test skeletons."""
        functions = static_results.get("functions", [])

        framework_map = {
            "python": "pytest",
            "javascript": "jest",
            "typescript": "jest",
            "java": "junit",
            "php": "phpunit",
            "go": "testing",
            "rust": "cargo test",
        }

        framework = framework_map.get(language, "generic")
        test_lines = []
        test_count = 0

        if language == "python":
            test_lines.append('"""Auto-generated tests by CodeSage AI"""')
            test_lines.append("import pytest\n")
            for func in functions:
                name = func["name"]
                test_lines.append(f"\ndef test_{name}_basic():")
                test_lines.append(f'    """Test {name} with valid input."""')
                test_lines.append(f"    # TODO: Add test implementation")
                test_lines.append(f"    pass\n")
                test_lines.append(f"\ndef test_{name}_edge_case():")
                test_lines.append(f'    """Test {name} with edge cases."""')
                test_lines.append(f"    # TODO: Test with empty input, None, boundary values")
                test_lines.append(f"    pass\n")
                test_lines.append(f"\ndef test_{name}_invalid_input():")
                test_lines.append(f'    """Test {name} with invalid input."""')
                test_lines.append(f"    # TODO: Test with wrong types, out-of-range values")
                test_lines.append(f"    pass\n")
                test_count += 3
        elif language in ("javascript", "typescript"):
            test_lines.append('// Auto-generated tests by CodeSage AI\n')
            for func in functions:
                name = func["name"]
                test_lines.append(f"describe('{name}', () => {{")
                test_lines.append(f"  test('should handle valid input', () => {{")
                test_lines.append(f"    // TODO: Add test implementation")
                test_lines.append(f"  }});\n")
                test_lines.append(f"  test('should handle edge cases', () => {{")
                test_lines.append(f"    // TODO: Test with empty arrays, null, undefined")
                test_lines.append(f"  }});\n")
                test_lines.append(f"  test('should throw on invalid input', () => {{")
                test_lines.append(f"    // TODO: Test with wrong types")
                test_lines.append(f"  }});\n")
                test_lines.append(f"}});\n")
                test_count += 3
        else:
            test_lines.append(f"// Auto-generated test skeletons for {language}")
            for func in functions:
                test_lines.append(f"\n// Test: {func['name']}")
                test_lines.append(f"// TODO: Implement basic, edge case, and invalid input tests")
                test_count += 1

        coverage_areas = ["basic functionality", "edge cases", "invalid inputs", "boundary values"]

        return {
            "test_code": "\n".join(test_lines),
            "framework": framework,
            "test_count": test_count,
            "coverage_areas": coverage_areas,
        }

    def _generate_issues(self, static_results: dict, code: str, language: str) -> list[dict]:
        """Generate code quality issues with AI explanations."""
        issues = []
        complexity = static_results.get("complexity", {})
        functions = static_results.get("functions", [])

        # High overall complexity
        cc = complexity.get("cyclomatic_complexity", 1)
        if cc > 15:
            issues.append({
                "type": "smell",
                "severity": "high",
                "title": "High Cyclomatic Complexity",
                "description": f"Code has a cyclomatic complexity of {cc}, which exceeds the recommended threshold of 10.",
                "explanation": "Cyclomatic complexity measures the number of independent execution paths. High values indicate code that is difficult to test and maintain.",
                "why_it_matters": "Each additional execution path requires a separate test case. Complex code is more likely to contain bugs.",
                "how_to_fix": "Break down complex functions into smaller, focused functions. Use polymorphism instead of long if-else chains.",
                "expected_improvement": "Reduced bug density, easier testing, and improved maintainability.",
            })

        # Functions without docstrings
        undocumented = [f for f in functions if not f.get("has_docstring", False)]
        if undocumented and len(undocumented) > len(functions) * 0.5:
            issues.append({
                "type": "style",
                "severity": "medium",
                "title": "Insufficient Documentation",
                "description": f"{len(undocumented)} of {len(functions)} functions lack documentation.",
                "explanation": "Documentation helps other developers understand the purpose, parameters, and return values of functions.",
                "why_it_matters": "Undocumented code increases onboarding time and makes maintenance harder.",
                "how_to_fix": f"Add docstrings to: {', '.join(f['name'] for f in undocumented[:5])}{'...' if len(undocumented) > 5 else ''}",
                "expected_improvement": "Faster onboarding, fewer misunderstandings, better IDE support.",
            })

        # Deep nesting
        nesting = complexity.get("max_nesting_depth", 0)
        if nesting > 3:
            issues.append({
                "type": "smell",
                "severity": "medium",
                "title": f"Deep Nesting Detected (depth: {nesting})",
                "description": "Code contains deeply nested structures that harm readability.",
                "explanation": "Deep nesting forces developers to keep track of multiple conditions simultaneously, increasing cognitive load.",
                "why_it_matters": "Nested code is harder to understand, test, and debug. It often indicates missing abstractions.",
                "how_to_fix": "Use guard clauses (early returns), extract helper methods, or use the strategy pattern.",
                "expected_improvement": "Reduced cognitive complexity, flatter code structure, easier testing.",
            })

        return issues
