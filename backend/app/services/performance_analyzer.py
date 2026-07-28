"""
CodeSage AI — Performance Analyzer Service
Detects performance anti-patterns, estimates time/space complexity,
and suggests optimized alternatives.
"""

import re
from dataclasses import dataclass


@dataclass
class PerformanceIssueDetail:
    """Detected performance issue."""
    type: str
    severity: str
    title: str
    description: str
    current_approach: str = ""
    suggested_approach: str = ""
    current_complexity: str = ""
    suggested_complexity: str = ""
    memory_impact: str = ""
    line_number: int | None = None


ALGORITHM_SUGGESTIONS = {
    "bubble_sort": {
        "name": "Bubble Sort",
        "current": "O(n²)",
        "suggested_algo": "Merge Sort / Tim Sort",
        "suggested_complexity": "O(n log n)",
        "memory": "O(1) → O(n)",
    },
    "selection_sort": {
        "name": "Selection Sort",
        "current": "O(n²)",
        "suggested_algo": "Quick Sort / Heap Sort",
        "suggested_complexity": "O(n log n)",
        "memory": "O(1) → O(log n)",
    },
    "linear_search": {
        "name": "Linear Search in sorted data",
        "current": "O(n)",
        "suggested_algo": "Binary Search",
        "suggested_complexity": "O(log n)",
        "memory": "No change",
    },
    "string_concat_loop": {
        "name": "String concatenation in loop",
        "current": "O(n²)",
        "suggested_algo": "StringBuilder / join()",
        "suggested_complexity": "O(n)",
        "memory": "Reduced allocations",
    },
}


class PerformanceAnalyzerService:
    """Analyzes code for performance issues and suggests optimizations."""

    def analyze(self, code: str, language: str) -> dict:
        """Run full performance analysis."""
        issues = self._detect_issues(code, language)
        complexity = self._estimate_complexity(code, language)
        memory = self._estimate_memory(code, language)

        return {
            "issues": issues,
            "time_complexity": complexity,
            "memory_analysis": memory,
        }

    def _detect_issues(self, code: str, language: str) -> list[PerformanceIssueDetail]:
        """Detect performance anti-patterns."""
        issues: list[PerformanceIssueDetail] = []
        lines = code.split("\n")

        # ── Nested loops ──────────────────────────────────────
        loop_keywords = [r'\bfor\b', r'\bwhile\b']
        loop_depth = 0
        loop_start: int | None = None

        for i, line in enumerate(lines):
            stripped = line.strip()
            is_loop = any(re.search(kw, stripped) for kw in loop_keywords)

            if is_loop:
                loop_depth += 1
                if loop_depth == 1:
                    loop_start = i

                if loop_depth >= 2:
                    issues.append(PerformanceIssueDetail(
                        type="nested_loop",
                        severity="high" if loop_depth >= 3 else "medium",
                        title=f"Nested loop detected (depth: {loop_depth})",
                        description=f"A loop nested {loop_depth} levels deep was found. This creates O(n^{loop_depth}) complexity.",
                        current_approach=f"Nested loop (depth {loop_depth})",
                        suggested_approach="Consider using hash maps, sorting + binary search, or divide-and-conquer.",
                        current_complexity=f"O(n^{loop_depth})",
                        suggested_complexity="O(n log n) or O(n)",
                        memory_impact="May increase memory usage for lookup tables",
                        line_number=i + 1,
                    ))

            # Reset depth when block ends
            if stripped in ('}', 'end', '') and loop_depth > 0:
                if language == "python" and stripped == '' and loop_depth > 0:
                    pass  # Python uses indentation
                elif stripped == '}':
                    loop_depth = max(0, loop_depth - 1)

        # ── Expensive recursion ───────────────────────────────
        func_pattern = re.compile(r'(?:def|function|fn)\s+(\w+)')
        for i, line in enumerate(lines):
            match = func_pattern.search(line)
            if match:
                func_name = match.group(1)
                # Check if function calls itself (recursion)
                remaining = "\n".join(lines[i+1:min(i+50, len(lines))])
                recursive_calls = len(re.findall(rf'\b{func_name}\s*\(', remaining))
                if recursive_calls >= 2:
                    issues.append(PerformanceIssueDetail(
                        type="expensive_recursion",
                        severity="high",
                        title=f"Multiple recursive calls in '{func_name}'",
                        description="Multiple recursive calls suggest exponential time complexity (like Fibonacci without memoization).",
                        current_approach="Recursive without memoization",
                        suggested_approach="Add memoization (@lru_cache), use dynamic programming, or convert to iterative.",
                        current_complexity="O(2^n)",
                        suggested_complexity="O(n) with memoization",
                        line_number=i + 1,
                    ))

        # ── String concatenation in loops ─────────────────────
        for i, line in enumerate(lines):
            if re.search(r'["\'].*?\+\s*=|str\s*\+\s*=|\+=\s*["\']', line):
                # Check if inside a loop
                context_above = "\n".join(lines[max(0, i-5):i])
                if any(re.search(kw, context_above) for kw in loop_keywords):
                    issues.append(PerformanceIssueDetail(
                        type="string_concat_loop",
                        severity="medium",
                        title="String concatenation inside loop",
                        description="Concatenating strings in a loop creates O(n²) time complexity due to immutable string reallocation.",
                        current_approach="String concatenation with +=",
                        suggested_approach="Use list append + join(), StringBuilder, or f-strings",
                        current_complexity="O(n²)",
                        suggested_complexity="O(n)",
                        memory_impact="Significant reduction in memory allocations",
                        line_number=i + 1,
                    ))

        # ── Large object creation in loops ────────────────────
        for i, line in enumerate(lines):
            if re.search(r'(?:new\s+\w+|(?:dict|list|set|map|Map|Set|Array)\s*\()', line):
                context_above = "\n".join(lines[max(0, i-3):i])
                if any(re.search(kw, context_above) for kw in loop_keywords):
                    issues.append(PerformanceIssueDetail(
                        type="object_creation_loop",
                        severity="medium",
                        title="Object creation inside loop",
                        description="Creating new objects inside a loop can be expensive. Consider pre-allocating or reusing objects.",
                        current_approach="New object per iteration",
                        suggested_approach="Pre-allocate outside loop or use object pooling",
                        memory_impact="High - creates garbage collection pressure",
                        line_number=i + 1,
                    ))

        # ── Blocking operations ───────────────────────────────
        blocking_patterns = [
            (r'time\.sleep\s*\(', "time.sleep() blocks the thread"),
            (r'Thread\.sleep\s*\(', "Thread.sleep() blocks the thread"),
            (r'input\s*\(', "Blocking input() call"),
            (r'\.read\s*\(\s*\)', "Unbounded .read() may load entire file into memory"),
        ]
        for i, line in enumerate(lines):
            for pattern, desc in blocking_patterns:
                if re.search(pattern, line):
                    issues.append(PerformanceIssueDetail(
                        type="blocking_operation",
                        severity="low",
                        title=f"Blocking operation: {desc}",
                        description=f"Detected blocking call on line {i+1}. In async/concurrent contexts, this can bottleneck performance.",
                        suggested_approach="Use async/await alternatives or run in a thread pool",
                        line_number=i + 1,
                    ))

        return issues

    def _estimate_complexity(self, code: str, language: str) -> dict:
        """Estimate time and space complexity of the code."""
        lines = code.split("\n")

        # Count nesting of loops
        max_loop_depth = 0
        current_depth = 0
        has_recursion = False
        has_sorting = False
        has_binary_search = False

        loop_keywords = [r'\bfor\b', r'\bwhile\b']
        for line in lines:
            stripped = line.strip()
            if any(re.search(kw, stripped) for kw in loop_keywords):
                current_depth += 1
                max_loop_depth = max(max_loop_depth, current_depth)
            if stripped in ('}', '') and current_depth > 0:
                current_depth = max(0, current_depth - 1)

        # Check for recursion
        func_pattern = re.compile(r'(?:def|function|fn|func)\s+(\w+)')
        for match in func_pattern.finditer(code):
            func_name = match.group(1)
            if re.search(rf'\b{func_name}\s*\(', code[match.end():]):
                has_recursion = True

        # Check for built-in sort
        if re.search(r'\.sort\s*\(|sorted\s*\(|Arrays\.sort|Collections\.sort', code):
            has_sorting = True

        # Determine complexity
        if has_recursion and max_loop_depth == 0:
            time_worst = "O(2^n)"
            time_avg = "O(2^n)"
            time_best = "O(n)"
            space = "O(n)"  # stack depth
            explanation = "Recursive algorithm detected. Without memoization, may have exponential time complexity."
        elif max_loop_depth >= 3:
            time_worst = f"O(n^{max_loop_depth})"
            time_avg = f"O(n^{max_loop_depth})"
            time_best = f"O(n^{max_loop_depth - 1})"
            space = "O(1)"
            explanation = f"Deeply nested loops ({max_loop_depth} levels) create polynomial time complexity."
        elif max_loop_depth == 2:
            time_worst = "O(n²)"
            time_avg = "O(n²)"
            time_best = "O(n)"
            space = "O(1)"
            explanation = "Nested loop detected, resulting in quadratic time complexity."
        elif max_loop_depth == 1:
            if has_sorting:
                time_worst = "O(n log n)"
                time_avg = "O(n log n)"
                time_best = "O(n)"
                space = "O(n)"
                explanation = "Linear iteration with sorting operation."
            else:
                time_worst = "O(n)"
                time_avg = "O(n)"
                time_best = "O(1)"
                space = "O(1)"
                explanation = "Single loop iteration — linear time complexity."
        else:
            time_worst = "O(1)"
            time_avg = "O(1)"
            time_best = "O(1)"
            space = "O(1)"
            explanation = "No loops or recursion detected — constant time complexity."

        suggestions = []
        if max_loop_depth >= 2:
            suggestions.append("Consider using hash maps to reduce nested loop complexity to O(n).")
        if has_recursion:
            suggestions.append("Add memoization or convert to iterative approach for better performance.")
        if has_sorting:
            suggestions.append("Ensure you're using the optimal sorting algorithm for your data characteristics.")

        return {
            "time_complexity": time_avg,
            "space_complexity": space,
            "worst_case": time_worst,
            "average_case": time_avg,
            "best_case": time_best,
            "explanation": explanation,
            "suggestions": suggestions,
        }

    def _estimate_memory(self, code: str, language: str) -> dict:
        """Estimate memory usage characteristics."""
        lines = code.split("\n")

        # Count object creations
        object_patterns = [
            r'new\s+\w+', r'\w+\s*=\s*\[\]', r'\w+\s*=\s*\{\}',
            r'\w+\s*=\s*(?:list|dict|set|map)\s*\(', r'(?:malloc|calloc|realloc)\s*\(',
            r'(?:Vec::new|HashMap::new|BTreeMap::new)\s*\(', r'make\s*\(',
        ]
        object_count = sum(len(re.findall(p, code)) for p in object_patterns)

        # Estimate recursive depth
        recursive_depth = 0
        func_pattern = re.compile(r'(?:def|function|fn|func)\s+(\w+)')
        for match in func_pattern.finditer(code):
            func_name = match.group(1)
            if re.search(rf'\b{func_name}\s*\(', code[match.end():]):
                recursive_depth = max(recursive_depth, 1)

        # Estimate stack usage
        stack_depth = max(1, len(re.findall(r'(?:def|function|fn|func)\s+\w+', code)))

        # Memory classification
        if object_count > 20:
            estimated_memory = "High"
            heap_usage = "Significant"
        elif object_count > 5:
            estimated_memory = "Moderate"
            heap_usage = "Moderate"
        else:
            estimated_memory = "Low"
            heap_usage = "Minimal"

        suggestions = []
        if object_count > 10:
            suggestions.append("Consider object pooling or reuse to reduce heap allocations.")
        if recursive_depth > 0:
            suggestions.append("Monitor recursive depth to avoid stack overflow.")
        if re.search(r'\.read\s*\(\s*\)', code):
            suggestions.append("Use streaming/chunked reads instead of loading entire files into memory.")

        return {
            "estimated_memory": estimated_memory,
            "object_creation_count": object_count,
            "stack_depth": stack_depth,
            "heap_usage": heap_usage,
            "recursive_depth": recursive_depth if recursive_depth > 0 else None,
            "suggestions": suggestions,
        }
