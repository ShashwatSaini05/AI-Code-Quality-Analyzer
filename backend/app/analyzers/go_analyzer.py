"""
CodeSage AI — Go Analyzer
"""
import re
from app.analyzers.base import BaseAnalyzer, ClassInfo, FunctionInfo


class GoAnalyzer(BaseAnalyzer):
    SUPPORTED_LANGUAGE = "go"

    def parse_functions(self, code: str) -> list[FunctionInfo]:
        functions: list[FunctionInfo] = []
        lines = code.split("\n")
        pattern = re.compile(r'^func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(([^)]*)\)')
        for i, line in enumerate(lines):
            match = pattern.match(line)
            if match:
                name = match.group(1)
                params = [p for p in match.group(2).split(",") if p.strip()] if match.group(2).strip() else []
                end_line = self._find_block_end(lines, i)
                func_code = "\n".join(lines[i:end_line+1])
                complexity = 1
                for cp in [r'\bif\b', r'\bfor\b', r'\bswitch\b', r'\bcase\b', r'&&', r'\|\|']:
                    complexity += len(re.findall(cp, func_code))
                functions.append(FunctionInfo(name=name, start_line=i+1, end_line=end_line+1, parameters=len(params), complexity=complexity))
        return functions

    def parse_classes(self, code: str) -> list[ClassInfo]:
        structs: list[ClassInfo] = []
        lines = code.split("\n")
        pattern = re.compile(r'type\s+(\w+)\s+struct\s*\{')
        for i, line in enumerate(lines):
            match = pattern.search(line)
            if match:
                end_line = self._find_block_end(lines, i)
                structs.append(ClassInfo(name=match.group(1), start_line=i+1, end_line=end_line+1))
        return structs

    def parse_imports(self, code: str) -> list[str]:
        imports = []
        in_import = False
        for line in code.split("\n"):
            s = line.strip()
            if s.startswith("import ("):
                in_import = True; continue
            if in_import:
                if s == ")": in_import = False
                elif s: imports.append(s.strip('"'))
            elif s.startswith("import "):
                imports.append(s)
        return imports

    def count_lines(self, code: str) -> dict[str, int]:
        lines = code.split("\n")
        total = len(lines)
        blank = sum(1 for l in lines if not l.strip())
        comment = sum(1 for l in lines if l.strip().startswith("//"))
        return {"total": total, "blank": blank, "comment": comment, "code": total - blank - comment}

    def _find_block_end(self, lines, start):
        depth = 0
        for i in range(start, len(lines)):
            depth += lines[i].count("{") - lines[i].count("}")
            if depth <= 0 and i > start: return i
        return len(lines) - 1
