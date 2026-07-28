"""
CodeSage AI — Java Analyzer
Java code analysis using regex-based parsing.
"""

import re
from app.analyzers.base import BaseAnalyzer, ClassInfo, FunctionInfo


class JavaAnalyzer(BaseAnalyzer):
    """Analyzer for Java source code."""
    SUPPORTED_LANGUAGE = "java"

    def parse_functions(self, code: str) -> list[FunctionInfo]:
        functions: list[FunctionInfo] = []
        lines = code.split("\n")
        pattern = re.compile(
            r'^\s*(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*'
            r'(?:\w+(?:<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+\w+(?:,\s*\w+)*)?\s*\{'
        )
        for i, line in enumerate(lines):
            match = pattern.match(line)
            if match:
                name = match.group(1)
                params_str = match.group(2).strip()
                params = [p.strip().split()[-1] for p in params_str.split(",") if p.strip()] if params_str else []
                end_line = self._find_block_end(lines, i)
                func_code = "\n".join(lines[i:end_line + 1])
                complexity = 1
                for cp in [r'\bif\b', r'\belse\s+if\b', r'\bfor\b', r'\bwhile\b', r'\bcatch\b', r'\bcase\b', r'&&', r'\|\|']:
                    complexity += len(re.findall(cp, func_code))
                has_doc = i > 0 and lines[i - 1].strip().endswith("*/")
                functions.append(FunctionInfo(name=name, start_line=i+1, end_line=end_line+1, parameters=len(params), complexity=complexity, has_docstring=has_doc))
        return functions

    def parse_classes(self, code: str) -> list[ClassInfo]:
        classes: list[ClassInfo] = []
        lines = code.split("\n")
        pattern = re.compile(r'(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+(\w+)\s*(?:extends\s+(\w+))?\s*(?:implements\s+([^{]+))?\s*\{')
        for i, line in enumerate(lines):
            match = pattern.search(line)
            if match:
                name = match.group(1)
                parents = []
                if match.group(2): parents.append(match.group(2))
                if match.group(3): parents.extend([p.strip() for p in match.group(3).split(",")])
                end_line = self._find_block_end(lines, i)
                class_code = "\n".join(lines[i:end_line+1])
                methods = self.parse_functions(class_code)
                has_doc = i > 0 and lines[i-1].strip().endswith("*/")
                classes.append(ClassInfo(name=name, start_line=i+1, end_line=end_line+1, methods=methods, has_docstring=has_doc, parent_classes=parents))
        return classes

    def parse_imports(self, code: str) -> list[str]:
        return [l.strip() for l in code.split("\n") if l.strip().startswith("import ")]

    def count_lines(self, code: str) -> dict[str, int]:
        lines = code.split("\n")
        total = len(lines)
        blank = sum(1 for l in lines if not l.strip())
        comment = 0
        in_block = False
        for line in lines:
            s = line.strip()
            if in_block:
                comment += 1
                if "*/" in s: in_block = False
                continue
            if s.startswith("/*"):
                comment += 1
                if "*/" not in s: in_block = True
            elif s.startswith("//"):
                comment += 1
        return {"total": total, "blank": blank, "comment": comment, "code": total - blank - comment}

    def _find_block_end(self, lines: list[str], start: int) -> int:
        depth = 0
        for i in range(start, len(lines)):
            depth += lines[i].count("{") - lines[i].count("}")
            if depth <= 0 and i > start: return i
        return len(lines) - 1
