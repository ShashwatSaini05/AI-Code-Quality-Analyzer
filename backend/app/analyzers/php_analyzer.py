"""
CodeSage AI — PHP Analyzer
"""
import re
from app.analyzers.base import BaseAnalyzer, ClassInfo, FunctionInfo


class PHPAnalyzer(BaseAnalyzer):
    SUPPORTED_LANGUAGE = "php"

    def parse_functions(self, code: str) -> list[FunctionInfo]:
        functions: list[FunctionInfo] = []
        lines = code.split("\n")
        pattern = re.compile(r'(?:public|private|protected|static)?\s*function\s+(\w+)\s*\(([^)]*)\)')
        for i, line in enumerate(lines):
            match = pattern.search(line)
            if match:
                name = match.group(1)
                params = [p for p in match.group(2).split(",") if p.strip()] if match.group(2).strip() else []
                end_line = self._find_block_end(lines, i)
                func_code = "\n".join(lines[i:end_line+1])
                complexity = 1
                for cp in [r'\bif\b', r'\belseif\b', r'\bfor\b', r'\bwhile\b', r'\bcatch\b', r'\bcase\b', r'&&', r'\|\|']:
                    complexity += len(re.findall(cp, func_code))
                functions.append(FunctionInfo(name=name, start_line=i+1, end_line=end_line+1, parameters=len(params), complexity=complexity))
        return functions

    def parse_classes(self, code: str) -> list[ClassInfo]:
        classes: list[ClassInfo] = []
        lines = code.split("\n")
        pattern = re.compile(r'class\s+(\w+)\s*(?:extends\s+(\w+))?\s*(?:implements\s+([^{]+))?\s*\{')
        for i, line in enumerate(lines):
            match = pattern.search(line)
            if match:
                parents = [match.group(2)] if match.group(2) else []
                end_line = self._find_block_end(lines, i)
                classes.append(ClassInfo(name=match.group(1), start_line=i+1, end_line=end_line+1, parent_classes=parents))
        return classes

    def parse_imports(self, code: str) -> list[str]:
        return [l.strip() for l in code.split("\n") if l.strip().startswith(("use ", "require", "include"))]

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
            elif s.startswith("/*"):
                comment += 1
                if "*/" not in s: in_block = True
            elif s.startswith("//") or s.startswith("#"):
                comment += 1
        return {"total": total, "blank": blank, "comment": comment, "code": total - blank - comment}

    def _find_block_end(self, lines, start):
        depth = 0
        for i in range(start, len(lines)):
            depth += lines[i].count("{") - lines[i].count("}")
            if depth <= 0 and i > start: return i
        return len(lines) - 1
