"""
CodeSage AI — JavaScript/TypeScript Analyzer
JavaScript and TypeScript code analysis using regex-based parsing.
"""

import re

from app.analyzers.base import BaseAnalyzer, ClassInfo, FunctionInfo


class JavaScriptAnalyzer(BaseAnalyzer):
    """Analyzer for JavaScript and TypeScript source code."""

    SUPPORTED_LANGUAGE = "javascript"

    def parse_functions(self, code: str) -> list[FunctionInfo]:
        """Extract JS/TS function definitions (function declarations, arrow functions, methods)."""
        functions: list[FunctionInfo] = []
        lines = code.split("\n")

        patterns = [
            # Standard function declaration
            re.compile(r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)'),
            # Arrow function assigned to variable
            re.compile(r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>'),
            # Method in class/object
            re.compile(r'^\s*(?:async\s+)?(\w+)\s*\(([^)]*)\)\s*\{'),
        ]

        for i, line in enumerate(lines):
            for pattern in patterns:
                match = pattern.search(line)
                if match:
                    name = match.group(1)
                    params_str = match.group(2).strip()

                    # Skip common false positives
                    if name in ('if', 'for', 'while', 'switch', 'catch', 'return', 'new'):
                        continue

                    params = [p.strip() for p in params_str.split(",") if p.strip()]
                    param_count = len(params)

                    # Find function end by counting braces
                    end_line = self._find_block_end(lines, i)

                    # Check for JSDoc
                    has_docstring = False
                    if i > 0 and lines[i - 1].strip().endswith("*/"):
                        has_docstring = True

                    # Complexity
                    func_code = "\n".join(lines[i:end_line + 1])
                    func_complexity = 1
                    for cp in [r'\bif\b', r'\belse\s+if\b', r'\bfor\b', r'\bwhile\b',
                               r'\bcatch\b', r'\bcase\b', r'&&', r'\|\|', r'\?\s*:']:
                        func_complexity += len(re.findall(cp, func_code))

                    functions.append(FunctionInfo(
                        name=name,
                        start_line=i + 1,
                        end_line=end_line + 1,
                        parameters=param_count,
                        lines_of_code=end_line - i + 1,
                        complexity=func_complexity,
                        has_docstring=has_docstring,
                    ))
                    break  # Only match first pattern per line

        return functions

    def parse_classes(self, code: str) -> list[ClassInfo]:
        """Extract JS/TS class definitions."""
        classes: list[ClassInfo] = []
        lines = code.split("\n")

        class_pattern = re.compile(
            r'(?:export\s+)?class\s+(\w+)\s*(?:extends\s+(\w+))?\s*\{'
        )

        for i, line in enumerate(lines):
            match = class_pattern.search(line)
            if match:
                name = match.group(1)
                parent = match.group(2)
                parent_classes = [parent] if parent else []

                end_line = self._find_block_end(lines, i)

                # Parse methods within class
                class_code = "\n".join(lines[i:end_line + 1])
                methods = self.parse_functions(class_code)

                # Check for JSDoc before class
                has_docstring = i > 0 and lines[i - 1].strip().endswith("*/")

                classes.append(ClassInfo(
                    name=name,
                    start_line=i + 1,
                    end_line=end_line + 1,
                    methods=methods,
                    has_docstring=has_docstring,
                    parent_classes=parent_classes,
                ))

        return classes

    def parse_imports(self, code: str) -> list[str]:
        """Extract import/require statements."""
        imports: list[str] = []
        for line in code.split("\n"):
            stripped = line.strip()
            if stripped.startswith("import ") or "require(" in stripped:
                imports.append(stripped)
        return imports

    def count_lines(self, code: str) -> dict[str, int]:
        """Count JS/TS lines with comment detection."""
        lines = code.split("\n")
        total = len(lines)
        blank = 0
        comment = 0
        in_block_comment = False

        for line in lines:
            stripped = line.strip()

            if not stripped:
                blank += 1
                continue

            if in_block_comment:
                comment += 1
                if "*/" in stripped:
                    in_block_comment = False
                continue

            if stripped.startswith("/*"):
                comment += 1
                if "*/" not in stripped:
                    in_block_comment = True
                continue

            if stripped.startswith("//"):
                comment += 1
                continue

        return {
            "total": total,
            "blank": blank,
            "comment": comment,
            "code": total - blank - comment,
        }

    def _find_block_end(self, lines: list[str], start: int) -> int:
        """Find the end of a brace-delimited block."""
        depth = 0
        for i in range(start, len(lines)):
            depth += lines[i].count("{") - lines[i].count("}")
            if depth <= 0 and i > start:
                return i
        return len(lines) - 1


class TypeScriptAnalyzer(JavaScriptAnalyzer):
    """TypeScript analyzer — extends JavaScript analyzer with TS-specific patterns."""
    SUPPORTED_LANGUAGE = "typescript"
