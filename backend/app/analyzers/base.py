"""
CodeSage AI — Base Analyzer
Abstract base class for all language-specific analyzers.
Provides common metrics computation and a pluggable architecture for new languages.
"""

import math
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class FunctionInfo:
    """Metadata about a function/method extracted from the AST."""
    name: str
    start_line: int
    end_line: int
    parameters: int = 0
    lines_of_code: int = 0
    complexity: int = 1
    cognitive_complexity: int = 0
    nesting_depth: int = 0
    has_docstring: bool = False
    return_type: Optional[str] = None


@dataclass
class ClassInfo:
    """Metadata about a class extracted from the AST."""
    name: str
    start_line: int
    end_line: int
    methods: list[FunctionInfo] = field(default_factory=list)
    attributes: int = 0
    has_docstring: bool = False
    parent_classes: list[str] = field(default_factory=list)


@dataclass
class AnalysisContext:
    """Shared context for a single analysis pass."""
    code: str
    language: str
    lines: list[str] = field(default_factory=list)
    functions: list[FunctionInfo] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    global_variables: list[str] = field(default_factory=list)
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0


class BaseAnalyzer(ABC):
    """
    Abstract base class for language-specific code analyzers.
    Subclasses implement language-specific parsing while inheriting
    common metric calculations.
    """

    SUPPORTED_LANGUAGE: str = "unknown"

    def __init__(self) -> None:
        self.context: Optional[AnalysisContext] = None

    # ── Abstract Methods (must be implemented per language) ──

    @abstractmethod
    def parse_functions(self, code: str) -> list[FunctionInfo]:
        """Extract function/method information from the code."""
        ...

    @abstractmethod
    def parse_classes(self, code: str) -> list[ClassInfo]:
        """Extract class information from the code."""
        ...

    @abstractmethod
    def parse_imports(self, code: str) -> list[str]:
        """Extract import statements from the code."""
        ...

    @abstractmethod
    def count_lines(self, code: str) -> dict[str, int]:
        """Count total, code, comment, and blank lines."""
        ...

    # ── Common Metrics ──────────────────────────────────────

    def analyze(self, code: str) -> dict[str, Any]:
        """
        Run the full analysis pipeline on the given code.
        Returns a comprehensive metrics dictionary.
        """
        # Build context
        line_counts = self.count_lines(code)
        functions = self.parse_functions(code)
        classes = self.parse_classes(code)
        imports = self.parse_imports(code)

        self.context = AnalysisContext(
            code=code,
            language=self.SUPPORTED_LANGUAGE,
            lines=code.split("\n"),
            functions=functions,
            classes=classes,
            imports=imports,
            total_lines=line_counts["total"],
            code_lines=line_counts["code"],
            comment_lines=line_counts["comment"],
            blank_lines=line_counts["blank"],
        )

        # Compute all metrics
        complexity = self.compute_cyclomatic_complexity()
        cognitive = self.compute_cognitive_complexity()
        halstead = self.compute_halstead_metrics(code)
        mi = self.compute_maintainability_index(complexity, halstead, line_counts["code"])
        nesting = self.compute_max_nesting(code)
        avg_func_len = self.compute_avg_function_length()

        return {
            "line_counts": line_counts,
            "functions": [self._func_to_dict(f) for f in functions],
            "classes": [self._class_to_dict(c) for c in classes],
            "imports": imports,
            "complexity": {
                "cyclomatic_complexity": complexity,
                "cognitive_complexity": cognitive,
                "maintainability_index": mi,
                "halstead_vocabulary": halstead["vocabulary"],
                "halstead_length": halstead["length"],
                "halstead_difficulty": halstead["difficulty"],
                "halstead_effort": halstead["effort"],
                "halstead_volume": halstead["volume"],
                "max_nesting_depth": nesting,
                "avg_function_length": avg_func_len,
                "total_functions": len(functions),
                "total_classes": len(classes),
            },
            "scores": self.compute_scores(complexity, cognitive, mi, halstead, nesting, line_counts),
        }

    def compute_cyclomatic_complexity(self) -> float:
        """
        Compute the total cyclomatic complexity.
        M = E - N + 2P, approximated from control-flow keywords.
        """
        if not self.context:
            return 1.0

        complexity = 1  # Base complexity
        control_flow_keywords = [
            r'\bif\b', r'\belif\b', r'\belse\s+if\b', r'\bfor\b', r'\bwhile\b',
            r'\bcase\b', r'\bcatch\b', r'\bexcept\b', r'\b\&\&\b', r'\b\|\|\b',
            r'\band\b', r'\bor\b', r'\b\?\s*:', r'\?\.',
        ]

        for pattern in control_flow_keywords:
            matches = re.findall(pattern, self.context.code)
            complexity += len(matches)

        return float(complexity)

    def compute_cognitive_complexity(self) -> float:
        """
        Compute cognitive complexity based on nesting and control flow.
        Higher weight for deeply nested structures.
        """
        if not self.context:
            return 0.0

        cognitive = 0.0
        nesting_level = 0
        nesting_keywords = {'if', 'for', 'while', 'switch', 'try', 'catch', 'except', 'with'}
        increment_keywords = {'if', 'elif', 'else if', 'for', 'while', 'catch', 'except', '&&', '||', 'and', 'or', '?'}

        for line in self.context.lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Check for nesting increase
            for kw in nesting_keywords:
                if re.search(rf'\b{kw}\b', stripped):
                    nesting_level += 1
                    break

            # Check for cognitive increment
            for kw in increment_keywords:
                if kw in ('&&', '||', '?'):
                    if kw in stripped:
                        cognitive += 1
                elif re.search(rf'\b{kw}\b', stripped):
                    cognitive += 1 + nesting_level
                    break

            # Check for nesting decrease
            if stripped in ('}', 'end', 'fi', 'done') or stripped.startswith(('end ', 'end;')):
                nesting_level = max(0, nesting_level - 1)

        return cognitive

    def compute_halstead_metrics(self, code: str) -> dict[str, float]:
        """
        Compute Halstead complexity metrics.
        Based on operators and operands in the code.
        """
        # Define operators and extract operands
        operators = set()
        operands = set()
        total_operators = 0
        total_operands = 0

        # Common operators
        operator_patterns = [
            r'[+\-*/%]=?', r'[<>=!]=?=?', r'&&|\|\|', r'[&|^~]',
            r'\b(return|if|else|for|while|do|switch|case|break|continue)\b',
            r'\b(class|def|function|import|from|const|let|var|async|await)\b',
            r'[{}()\[\];,.:?]', r'=>', r'->',
        ]

        for pattern in operator_patterns:
            matches = re.findall(pattern, code)
            for match in matches:
                operators.add(match)
                total_operators += 1

        # Operands: identifiers, literals
        operand_matches = re.findall(r'\b[a-zA-Z_]\w*\b', code)
        for op in operand_matches:
            operands.add(op)
            total_operands += 1

        # Numeric literals
        numeric_matches = re.findall(r'\b\d+\.?\d*\b', code)
        for num in numeric_matches:
            operands.add(num)
            total_operands += 1

        n1 = len(operators) or 1  # Unique operators
        n2 = len(operands) or 1   # Unique operands
        N1 = total_operators or 1  # Total operators
        N2 = total_operands or 1   # Total operands

        vocabulary = n1 + n2
        length = N1 + N2
        volume = length * math.log2(vocabulary) if vocabulary > 0 else 0
        difficulty = (n1 / 2) * (N2 / n2) if n2 > 0 else 0
        effort = volume * difficulty

        return {
            "vocabulary": round(vocabulary, 2),
            "length": round(length, 2),
            "volume": round(volume, 2),
            "difficulty": round(difficulty, 2),
            "effort": round(effort, 2),
        }

    def compute_maintainability_index(
        self, complexity: float, halstead: dict[str, float], loc: int
    ) -> float:
        """
        Compute Maintainability Index (MI).
        MI = max(0, (171 - 5.2 * ln(V) - 0.23 * CC - 16.2 * ln(LOC)) * 100 / 171)
        """
        volume = halstead.get("volume", 1)
        loc = max(loc, 1)

        try:
            mi = 171 - 5.2 * math.log(max(volume, 1)) - 0.23 * complexity - 16.2 * math.log(loc)
            mi = max(0, (mi * 100) / 171)
            return round(min(mi, 100), 2)
        except (ValueError, ZeroDivisionError):
            return 50.0

    def compute_max_nesting(self, code: str) -> int:
        """Compute maximum nesting depth by tracking indent levels and braces."""
        max_depth = 0
        current_depth = 0

        for line in code.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue

            # Count opening/closing braces
            current_depth += stripped.count('{') - stripped.count('}')

            # For Python-style (indentation-based)
            if self.SUPPORTED_LANGUAGE == "python":
                indent = len(line) - len(line.lstrip())
                depth = indent // 4  # Assume 4-space indentation
                max_depth = max(max_depth, depth)
            else:
                max_depth = max(max_depth, current_depth)

        return max(max_depth, 0)

    def compute_avg_function_length(self) -> float:
        """Compute average function length in lines of code."""
        if not self.context or not self.context.functions:
            return 0.0
        total = sum(f.end_line - f.start_line + 1 for f in self.context.functions)
        return round(total / len(self.context.functions), 2)

    def compute_scores(
        self,
        complexity: float,
        cognitive: float,
        mi: float,
        halstead: dict[str, float],
        nesting: int,
        line_counts: dict[str, int],
    ) -> dict[str, dict[str, Any]]:
        """Compute all quality sub-scores on a 0-100 scale."""

        def _grade(score: float) -> tuple[str, str]:
            if score >= 90:
                return "A", "#10b981"
            if score >= 80:
                return "B", "#3b82f6"
            if score >= 70:
                return "C", "#f59e0b"
            if score >= 60:
                return "D", "#f97316"
            return "F", "#ef4444"

        # Readability: based on MI, avg function length, naming
        readability = min(100, mi * 0.5 + max(0, 50 - self.compute_avg_function_length()))
        readability = max(0, readability)

        # Maintainability: based on MI directly
        maintainability = mi

        # Performance: inverse of complexity
        perf = max(0, 100 - complexity * 2 - nesting * 5)

        # Security: base 100, deducted by found issues (calculated later)
        security = 100.0

        # Scalability
        scalability = max(0, 100 - complexity * 1.5 - nesting * 3)

        # Documentation
        doc_ratio = (
            line_counts["comment"] / max(line_counts["code"], 1) * 100
            if line_counts.get("code", 0) > 0
            else 0
        )
        documentation = min(100, doc_ratio * 5)

        # Architecture
        architecture = max(0, 100 - complexity * 1 - nesting * 4)

        scores = {}
        for label, value in [
            ("readability", readability),
            ("maintainability", maintainability),
            ("performance", perf),
            ("security", security),
            ("scalability", scalability),
            ("documentation", documentation),
            ("architecture", architecture),
        ]:
            clamped = max(0, min(100, value))
            grade, color = _grade(clamped)
            scores[label] = {
                "score": round(clamped, 1),
                "grade": grade,
                "label": label.title(),
                "explanation": self._score_explanation(label, clamped),
                "color": color,
            }

        return scores

    def _score_explanation(self, category: str, score: float) -> str:
        """Generate a human-readable explanation for a score."""
        explanations = {
            "readability": {
                90: "Excellent readability. Code is clean, well-structured, and easy to understand.",
                70: "Good readability. Minor improvements possible in naming or structure.",
                50: "Average readability. Consider refactoring long functions and improving naming.",
                0: "Poor readability. Functions are too long, naming is unclear, and structure is confusing.",
            },
            "maintainability": {
                90: "Highly maintainable. Low complexity, well-documented, and modular.",
                70: "Good maintainability. Some areas could benefit from simplification.",
                50: "Moderate maintainability. Complexity is manageable but could be improved.",
                0: "Difficult to maintain. High complexity and tight coupling detected.",
            },
            "performance": {
                90: "Excellent performance characteristics. Efficient algorithms and data structures.",
                70: "Good performance. Minor optimizations possible.",
                50: "Average performance. Some inefficient patterns detected.",
                0: "Performance concerns. Nested loops, expensive operations, or memory issues detected.",
            },
            "security": {
                90: "Strong security posture. No vulnerabilities detected.",
                70: "Good security. Minor improvements recommended.",
                50: "Security concerns found. Address medium-severity issues.",
                0: "Critical security vulnerabilities detected. Immediate action required.",
            },
            "scalability": {
                90: "Highly scalable design. Good separation of concerns.",
                70: "Good scalability. Minor improvements possible.",
                50: "Moderate scalability. Some patterns may not scale well.",
                0: "Scalability concerns. Tightly coupled, high complexity.",
            },
            "documentation": {
                90: "Excellent documentation. Well-documented functions and classes.",
                70: "Good documentation. Some functions lack docstrings.",
                50: "Moderate documentation. Consider adding more comments.",
                0: "Insufficient documentation. Most functions lack descriptions.",
            },
            "architecture": {
                90: "Clean architecture. Good modularity and separation of concerns.",
                70: "Good architecture. Minor structural improvements possible.",
                50: "Average architecture. Consider applying design patterns.",
                0: "Poor architecture. High coupling, low cohesion detected.",
            },
        }

        thresholds = explanations.get(category, {})
        for threshold in sorted(thresholds.keys(), reverse=True):
            if score >= threshold:
                return thresholds[threshold]

        return "Score calculated based on code metrics analysis."

    # ── Helpers ──────────────────────────────────────────────

    def _func_to_dict(self, f: FunctionInfo) -> dict[str, Any]:
        return {
            "name": f.name,
            "start_line": f.start_line,
            "end_line": f.end_line,
            "parameters": f.parameters,
            "lines_of_code": f.end_line - f.start_line + 1,
            "complexity": f.complexity,
            "cognitive_complexity": f.cognitive_complexity,
            "nesting_depth": f.nesting_depth,
            "has_docstring": f.has_docstring,
        }

    def _class_to_dict(self, c: ClassInfo) -> dict[str, Any]:
        return {
            "name": c.name,
            "start_line": c.start_line,
            "end_line": c.end_line,
            "methods": len(c.methods),
            "attributes": c.attributes,
            "has_docstring": c.has_docstring,
            "parent_classes": c.parent_classes,
        }
