"""
CodeSage AI — Security Analyzer Service
Detects OWASP Top 10 and common security vulnerabilities using pattern matching.
"""

import re
from dataclasses import dataclass, field


@dataclass
class SecurityIssue:
    """Represents a detected security vulnerability."""
    vulnerability_type: str
    severity: str  # critical, high, medium, low, info
    cvss_score: float
    cwe_id: str
    title: str
    description: str
    line_number: int | None = None
    code_snippet: str | None = None
    recommendation: str = ""
    real_world_example: str = ""


# ── Security Pattern Definitions ─────────────────────────────

SECURITY_PATTERNS: list[dict] = [
    {
        "type": "sql_injection",
        "patterns": [
            r'(?:execute|cursor\.execute|query)\s*\(\s*["\'].*?%s',
            r'(?:execute|query)\s*\(\s*f["\']',
            r'(?:execute|query)\s*\(\s*["\'].*?\+\s*\w+',
            r'\.format\s*\(.*?\).*(?:execute|query)',
            r'SELECT\s+.*?\+\s*\w+',
            r'INSERT\s+INTO.*?\+\s*\w+',
            r'DELETE\s+FROM.*?\+\s*\w+',
            r'UPDATE\s+.*?\+\s*\w+',
        ],
        "severity": "critical",
        "cvss": 9.8,
        "cwe": "CWE-89",
        "title": "SQL Injection Vulnerability",
        "description": "User input is concatenated directly into SQL queries, allowing attackers to execute arbitrary SQL commands.",
        "recommendation": "Use parameterized queries or prepared statements. Never concatenate user input into SQL strings.",
        "example": "In 2017, Equifax's data breach exposed 147 million records due to an SQL injection vulnerability.",
    },
    {
        "type": "command_injection",
        "patterns": [
            r'os\.system\s*\(',
            r'subprocess\.call\s*\(\s*["\']',
            r'subprocess\.Popen\s*\(\s*["\'].*?\+',
            r'exec\s*\(\s*["\'].*?\+',
            r'eval\s*\(',
            r'Runtime\.getRuntime\(\)\.exec',
            r'child_process\.exec\s*\(',
        ],
        "severity": "critical",
        "cvss": 9.8,
        "cwe": "CWE-78",
        "title": "Command Injection Vulnerability",
        "description": "User input may be passed to system commands, allowing remote code execution.",
        "recommendation": "Use subprocess with a list of arguments instead of shell=True. Validate and sanitize all inputs.",
        "example": "Shellshock (2014) exploited command injection in Bash, affecting millions of servers worldwide.",
    },
    {
        "type": "xss",
        "patterns": [
            r'innerHTML\s*=',
            r'document\.write\s*\(',
            r'\.html\s*\(\s*\w+',
            r'dangerouslySetInnerHTML',
            r'v-html\s*=',
            r'\{\{.*?\|safe\}\}',
        ],
        "severity": "high",
        "cvss": 7.5,
        "cwe": "CWE-79",
        "title": "Cross-Site Scripting (XSS) Vulnerability",
        "description": "Unsanitized user input is rendered as HTML, allowing script injection.",
        "recommendation": "Sanitize all user input before rendering. Use textContent instead of innerHTML. Use CSP headers.",
        "example": "In 2018, a stored XSS vulnerability in the British Airways website led to 380,000 payment card details being stolen.",
    },
    {
        "type": "hardcoded_credentials",
        "patterns": [
            r'(?:password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
            r'(?:secret|api_key|apikey|token|auth)\s*=\s*["\'][^"\']+["\']',
            r'(?:AWS_ACCESS_KEY|AWS_SECRET)\s*=\s*["\']',
            r'PRIVATE_KEY\s*=\s*["\']',
            r'(?:DB_PASSWORD|DATABASE_PASSWORD)\s*=\s*["\'][^"\']+["\']',
        ],
        "severity": "high",
        "cvss": 7.5,
        "cwe": "CWE-798",
        "title": "Hardcoded Credentials Detected",
        "description": "Sensitive credentials are hardcoded in the source code, which may be exposed in version control.",
        "recommendation": "Use environment variables or a secrets manager (e.g., AWS Secrets Manager, HashiCorp Vault).",
        "example": "Uber's 2016 breach was partly due to hardcoded AWS credentials found in a GitHub repository.",
    },
    {
        "type": "weak_hashing",
        "patterns": [
            r'(?:md5|MD5)\s*\(',
            r'(?:sha1|SHA1)\s*\(',
            r'hashlib\.md5',
            r'hashlib\.sha1',
            r'MessageDigest\.getInstance\s*\(\s*["\']MD5',
            r'MessageDigest\.getInstance\s*\(\s*["\']SHA-1',
        ],
        "severity": "medium",
        "cvss": 5.5,
        "cwe": "CWE-328",
        "title": "Weak Hashing Algorithm",
        "description": "MD5 or SHA-1 hashing is used, which is cryptographically broken.",
        "recommendation": "Use SHA-256, SHA-3, or bcrypt/scrypt/Argon2 for password hashing.",
        "example": "MD5 collision attacks have been demonstrated since 2004, making it unsuitable for security.",
    },
    {
        "type": "unsafe_deserialization",
        "patterns": [
            r'pickle\.loads?\s*\(',
            r'yaml\.load\s*\(\s*[^,]+\s*\)',
            r'yaml\.unsafe_load',
            r'ObjectInputStream',
            r'unserialize\s*\(',
            r'JSON\.parse\s*\(\s*\w+\s*\)',
        ],
        "severity": "high",
        "cvss": 8.1,
        "cwe": "CWE-502",
        "title": "Unsafe Deserialization",
        "description": "Deserializing untrusted data can lead to remote code execution.",
        "recommendation": "Use safe deserialization methods. For YAML, use yaml.safe_load(). Validate data schemas.",
        "example": "Apache Struts RCE (2017) exploited unsafe deserialization, leading to the Equifax breach.",
    },
    {
        "type": "path_traversal",
        "patterns": [
            r'open\s*\(\s*(?:request|req|input|user)',
            r'os\.path\.join\s*\(\s*\w+\s*,\s*(?:request|req|input)',
            r'file_get_contents\s*\(\s*\$_(?:GET|POST|REQUEST)',
            r'readFile\s*\(\s*(?:req|request)',
        ],
        "severity": "high",
        "cvss": 7.5,
        "cwe": "CWE-22",
        "title": "Path Traversal Vulnerability",
        "description": "User input is used in file paths without sanitization, allowing access to arbitrary files.",
        "recommendation": "Validate and sanitize file paths. Use os.path.realpath() and check against allowed directories.",
        "example": "Path traversal vulnerabilities have been used to read /etc/passwd and other sensitive system files.",
    },
    {
        "type": "insecure_random",
        "patterns": [
            r'\brandom\b\.(?:random|randint|choice|uniform)\s*\(',
            r'Math\.random\s*\(',
            r'java\.util\.Random\b',
            r'rand\s*\(\s*\)',
        ],
        "severity": "low",
        "cvss": 3.5,
        "cwe": "CWE-330",
        "title": "Use of Insecure Random Number Generator",
        "description": "Standard random generators are not cryptographically secure and should not be used for security-sensitive operations.",
        "recommendation": "Use secrets module (Python), crypto.randomBytes (Node.js), or SecureRandom (Java) for security purposes.",
        "example": "Predictable session tokens generated with Math.random() have been exploited in session hijacking attacks.",
    },
    {
        "type": "missing_auth",
        "patterns": [
            r'@app\.route.*methods=.*POST.*\n(?:(?!@login_required|@requires_auth|@authenticated).*\n)*def\s+\w+',
            r'router\.(post|put|delete)\s*\([^)]*\)\s*(?!.*(?:auth|middleware|guard))',
        ],
        "severity": "medium",
        "cvss": 6.5,
        "cwe": "CWE-306",
        "title": "Missing Authentication Check",
        "description": "An endpoint accepts write operations without apparent authentication middleware.",
        "recommendation": "Add authentication middleware to all sensitive endpoints. Implement RBAC.",
        "example": "Missing authentication on admin endpoints has led to unauthorized data access in numerous applications.",
    },
]


class SecurityAnalyzerService:
    """Analyzes code for security vulnerabilities."""

    def analyze(self, code: str, language: str) -> list[SecurityIssue]:
        """
        Scan code for security vulnerabilities using pattern matching.
        Returns a list of SecurityIssue objects.
        """
        issues: list[SecurityIssue] = []
        lines = code.split("\n")

        for rule in SECURITY_PATTERNS:
            for pattern_str in rule["patterns"]:
                try:
                    pattern = re.compile(pattern_str, re.IGNORECASE | re.MULTILINE)
                except re.error:
                    continue

                for i, line in enumerate(lines):
                    if pattern.search(line):
                        # Avoid false positives in comments
                        stripped = line.strip()
                        if stripped.startswith(("#", "//", "/*", "*", "'''", '"""')):
                            continue

                        issues.append(SecurityIssue(
                            vulnerability_type=rule["type"],
                            severity=rule["severity"],
                            cvss_score=rule["cvss"],
                            cwe_id=rule["cwe"],
                            title=rule["title"],
                            description=rule["description"],
                            line_number=i + 1,
                            code_snippet=line.strip()[:200],
                            recommendation=rule["recommendation"],
                            real_world_example=rule.get("example", ""),
                        ))
                        break  # One match per rule per scan to avoid duplicates

        return self._deduplicate(issues)

    def _deduplicate(self, issues: list[SecurityIssue]) -> list[SecurityIssue]:
        """Remove duplicate findings of the same type."""
        seen: set[str] = set()
        unique: list[SecurityIssue] = []
        for issue in issues:
            key = f"{issue.vulnerability_type}:{issue.line_number}"
            if key not in seen:
                seen.add(key)
                unique.append(issue)
        return unique

    def calculate_security_score(self, issues: list[SecurityIssue]) -> float:
        """Calculate security score based on findings."""
        if not issues:
            return 100.0

        deductions = {
            "critical": 30,
            "high": 20,
            "medium": 10,
            "low": 5,
            "info": 2,
        }

        total_deduction = sum(deductions.get(issue.severity, 0) for issue in issues)
        return max(0.0, 100.0 - total_deduction)
