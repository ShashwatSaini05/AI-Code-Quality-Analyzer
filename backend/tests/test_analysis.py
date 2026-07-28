"""
CodeSage AI — Backend Tests
Tests for the analysis engine and API endpoints.
"""

import pytest
from app.analyzers.python_analyzer import PythonAnalyzer
from app.analyzers.javascript_analyzer import JavaScriptAnalyzer
from app.services.security_analyzer import SecurityAnalyzerService
from app.services.performance_analyzer import PerformanceAnalyzerService
from app.services.analysis_service import AnalysisService
from app.core.utils import detect_language, compute_hash, count_lines


# ── Language Detection Tests ─────────────────────────────────

class TestLanguageDetection:
    def test_detect_python(self):
        code = "def hello():\n    print('world')"
        assert detect_language(code) == "python"

    def test_detect_javascript(self):
        code = "const x = 5;\nfunction hello() { return x; }"
        assert detect_language(code) == "javascript"

    def test_detect_from_filename(self):
        assert detect_language("", "app.py") == "python"
        assert detect_language("", "index.ts") == "typescript"
        assert detect_language("", "Main.java") == "java"
        assert detect_language("", "main.go") == "go"
        assert detect_language("", "lib.rs") == "rust"

    def test_detect_unknown(self):
        assert detect_language("hello world") == "unknown"


# ── Utility Tests ────────────────────────────────────────────

class TestUtilities:
    def test_compute_hash(self):
        h1 = compute_hash("hello")
        h2 = compute_hash("hello")
        h3 = compute_hash("world")
        assert h1 == h2
        assert h1 != h3

    def test_count_lines(self):
        code = "line1\n\nline3\n# comment\nline5"
        result = count_lines(code)
        assert result["total"] == 5
        assert result["blank"] == 1
        assert result["comment"] == 1
        assert result["code"] == 3


# ── Python Analyzer Tests ────────────────────────────────────

class TestPythonAnalyzer:
    def setup_method(self):
        self.analyzer = PythonAnalyzer()

    def test_parse_functions(self):
        code = "def hello(name):\n    return f'Hello {name}'\n\ndef world():\n    pass"
        functions = self.analyzer.parse_functions(code)
        assert len(functions) == 2
        assert functions[0].name == "hello"
        assert functions[0].parameters == 1
        assert functions[1].name == "world"

    def test_parse_classes(self):
        code = "class MyClass:\n    def __init__(self):\n        self.x = 0\n\n    def method(self):\n        pass"
        classes = self.analyzer.parse_classes(code)
        assert len(classes) == 1
        assert classes[0].name == "MyClass"

    def test_parse_imports(self):
        code = "import os\nfrom pathlib import Path\nimport sys"
        imports = self.analyzer.parse_imports(code)
        assert len(imports) == 3

    def test_count_lines(self):
        code = "# Comment\n\ndef hello():\n    pass"
        result = self.analyzer.count_lines(code)
        assert result["comment"] == 1
        assert result["blank"] == 1

    def test_full_analysis(self):
        code = "def add(a, b):\n    return a + b"
        result = self.analyzer.analyze(code)
        assert "complexity" in result
        assert "scores" in result
        assert result["complexity"]["cyclomatic_complexity"] >= 1


# ── JavaScript Analyzer Tests ────────────────────────────────

class TestJavaScriptAnalyzer:
    def setup_method(self):
        self.analyzer = JavaScriptAnalyzer()

    def test_parse_functions(self):
        code = "function greet(name) {\n  return `Hello ${name}`;\n}"
        functions = self.analyzer.parse_functions(code)
        assert len(functions) >= 1
        assert functions[0].name == "greet"

    def test_parse_imports(self):
        code = "import React from 'react';\nconst express = require('express');"
        imports = self.analyzer.parse_imports(code)
        assert len(imports) == 2


# ── Security Analyzer Tests ──────────────────────────────────

class TestSecurityAnalyzer:
    def setup_method(self):
        self.analyzer = SecurityAnalyzerService()

    def test_detect_sql_injection(self):
        code = 'cursor.execute("SELECT * FROM users WHERE name = \'" + user_input + "\'")'
        issues = self.analyzer.analyze(code, "python")
        sql_issues = [i for i in issues if i.vulnerability_type == "sql_injection"]
        assert len(sql_issues) > 0

    def test_detect_hardcoded_password(self):
        code = 'password = "admin123"'
        issues = self.analyzer.analyze(code, "python")
        cred_issues = [i for i in issues if i.vulnerability_type == "hardcoded_credentials"]
        assert len(cred_issues) > 0

    def test_detect_eval(self):
        code = "result = eval(user_input)"
        issues = self.analyzer.analyze(code, "python")
        cmd_issues = [i for i in issues if i.vulnerability_type == "command_injection"]
        assert len(cmd_issues) > 0

    def test_clean_code(self):
        code = "def add(a, b):\n    return a + b"
        issues = self.analyzer.analyze(code, "python")
        critical = [i for i in issues if i.severity == "critical"]
        assert len(critical) == 0

    def test_security_score(self):
        assert self.analyzer.calculate_security_score([]) == 100.0


# ── Performance Analyzer Tests ───────────────────────────────

class TestPerformanceAnalyzer:
    def setup_method(self):
        self.analyzer = PerformanceAnalyzerService()

    def test_detect_nested_loops(self):
        code = "for i in range(n):\n    for j in range(n):\n        pass"
        result = self.analyzer.analyze(code, "python")
        assert len(result["issues"]) > 0

    def test_estimate_complexity(self):
        code = "for i in range(n):\n    for j in range(n):\n        pass"
        result = self.analyzer.analyze(code, "python")
        assert "n²" in result["time_complexity"]["time_complexity"] or "n^2" in result["time_complexity"]["time_complexity"]

    def test_constant_complexity(self):
        code = "x = 5\ny = x + 3"
        result = self.analyzer.analyze(code, "python")
        assert result["time_complexity"]["time_complexity"] == "O(1)"


# ── Integration Test ─────────────────────────────────────────

class TestAnalysisService:
    def setup_method(self):
        self.service = AnalysisService()

    def test_full_analysis_pipeline(self):
        code = """
def process_data(items):
    result = []
    for item in items:
        if item > 0:
            result.append(item * 2)
    return result

class Calculator:
    def add(self, a, b):
        return a + b

    def divide(self, a, b):
        return a / b
"""
        result = self.service.analyze_code(code, language="python")

        assert result["language"] == "python"
        assert result["status"] == "completed"
        assert "overall_quality_score" in result
        assert result["overall_quality_score"] > 0
        assert "scores" in result
        assert "complexity_metrics" in result
        assert "processing_time_ms" in result

    def test_security_analysis(self):
        code = 'password = "secret123"\neval(user_input)'
        result = self.service.analyze_code(code, language="python")
        assert len(result["security_vulnerabilities"]) > 0

    def test_auto_language_detection(self):
        code = "def hello():\n    pass"
        result = self.service.analyze_code(code)
        assert result["language"] == "python"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
