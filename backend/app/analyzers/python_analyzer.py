"""
CodeSage AI — Python Analyzer
Python-specific code analysis using regex-based AST parsing.
"""

import re
from typing import Any

from app.analyzers.base import BaseAnalyzer, ClassInfo, FunctionInfo


class PythonAnalyzer(BaseAnalyzer):
    """Analyzer for Python source code."""

    SUPPORTED_LANGUAGE = "python"

    def parse_functions(self, code: str) -> list[FunctionInfo]:
        """Extract Python function definitions."""
        functions: list[FunctionInfo] = []
        lines = code.split("\n")

        # Match def/async def declarations
        func_pattern = re.compile(
            r'^(\s*)(async\s+)?def\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*(\S+))?\s*:'
        )

        for i, line in enumerate(lines):
            match = func_pattern.match(line)
            if match:
                indent = len(match.group(1))
                name = match.group(3)
                params_str = match.group(4).strip()
                return_type = match.group(5)

                # Count parameters (excluding self, cls)
                params = [p.strip() for p in params_str.split(",") if p.strip()]
                params = [p for p in params if p not in ("self", "cls")]
                param_count = len(params)

                # Find function end (next line with same or less indentation)
                end_line = i
                for j in range(i + 1, len(lines)):
                    stripped = lines[j].strip()
                    if not stripped:
                        continue
                    line_indent = len(lines[j]) - len(lines[j].lstrip())
                    if line_indent <= indent and stripped:
                        break
                    end_line = j

                # Check for docstring
                has_docstring = False
                if i + 1 < len(lines):
                    next_stripped = lines[i + 1].strip()
                    if next_stripped.startswith(('"""', "'''", '"', "'")):
                        has_docstring = True

                # Calculate nesting depth within function
                max_nesting = 0
                for j in range(i + 1, end_line + 1):
                    func_indent = len(lines[j]) - len(lines[j].lstrip()) if lines[j].strip() else 0
                    relative_nesting = max(0, (func_indent - indent - 4) // 4)
                    max_nesting = max(max_nesting, relative_nesting)

                # Calculate complexity for this function
                func_code = "\n".join(lines[i:end_line + 1])
                func_complexity = 1
                for pattern in [r'\bif\b', r'\belif\b', r'\bfor\b', r'\bwhile\b',
                                r'\bexcept\b', r'\band\b', r'\bor\b']:
                    func_complexity += len(re.findall(pattern, func_code))

                functions.append(FunctionInfo(
                    name=name,
                    start_line=i + 1,
                    end_line=end_line + 1,
                    parameters=param_count,
                    lines_of_code=end_line - i + 1,
                    complexity=func_complexity,
                    nesting_depth=max_nesting,
                    has_docstring=has_docstring,
                    return_type=return_type,
                ))

        return functions

    def parse_classes(self, code: str) -> list[ClassInfo]:
        """Extract Python class definitions."""
        classes: list[ClassInfo] = []
        lines = code.split("\n")

        class_pattern = re.compile(r'^(\s*)class\s+(\w+)\s*(?:\(([^)]*)\))?\s*:')

        for i, line in enumerate(lines):
            match = class_pattern.match(line)
            if match:
                indent = len(match.group(1))
                name = match.group(2)
                parents_str = match.group(3) or ""
                parent_classes = [p.strip() for p in parents_str.split(",") if p.strip()]

                # Find class end
                end_line = i
                for j in range(i + 1, len(lines)):
                    stripped = lines[j].strip()
                    if not stripped:
                        continue
                    line_indent = len(lines[j]) - len(lines[j].lstrip())
                    if line_indent <= indent and stripped:
                        break
                    end_line = j

                # Check for docstring
                has_docstring = False
                if i + 1 < len(lines):
                    next_stripped = lines[i + 1].strip()
                    if next_stripped.startswith(('"""', "'''", '    """', "    '''")):
                        has_docstring = True

                # Count methods and attributes
                class_code = "\n".join(lines[i:end_line + 1])
                methods = self.parse_functions(class_code)
                attr_count = len(re.findall(r'self\.(\w+)\s*=', class_code))

                classes.append(ClassInfo(
                    name=name,
                    start_line=i + 1,
                    end_line=end_line + 1,
                    methods=methods,
                    attributes=attr_count,
                    has_docstring=has_docstring,
                    parent_classes=parent_classes,
                ))

        return classes

    def parse_imports(self, code: str) -> list[str]:
        """Extract Python import statements."""
        imports: list[str] = []
        for line in code.split("\n"):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                imports.append(stripped)
        return imports

    def count_lines(self, code: str) -> dict[str, int]:
        """Count Python lines with comment detection."""
        lines = code.split("\n")
        total = len(lines)
        blank = 0
        comment = 0
        in_multiline = False

        for line in lines:
            stripped = line.strip()

            if not stripped:
                blank += 1
                continue

            # Multi-line string/comment handling
            if in_multiline:
                comment += 1
                if '"""' in stripped or "'''" in stripped:
                    in_multiline = False
                continue

            if stripped.startswith(('"""', "'''")):
                comment += 1
                if stripped.count('"""') == 1 or stripped.count("'''") == 1:
                    in_multiline = True
                continue

            if stripped.startswith("#"):
                comment += 1
                continue

        return {
            "total": total,
            "blank": blank,
            "comment": comment,
            "code": total - blank - comment,
        }
