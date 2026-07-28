"""
CodeSage AI — ML Dataset Generator
Generates synthetic code metrics dataset for training the bug prediction model.
"""

import csv
import random
import os


def generate_dataset(output_path: str, num_samples: int = 5000) -> None:
    """Generate a synthetic dataset of code metrics with bug labels."""

    headers = [
        "cyclomatic_complexity", "cognitive_complexity", "lines_of_code",
        "comment_ratio", "function_count", "class_count", "max_nesting_depth",
        "avg_function_length", "parameters_per_function", "halstead_difficulty",
        "halstead_effort", "halstead_volume", "maintainability_index",
        "duplicate_ratio", "coupling_score", "import_count",
        "has_error_handling", "has_type_hints", "test_coverage",
        "has_bug"  # Target variable
    ]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for _ in range(num_samples):
            cc = random.randint(1, 50)
            cog = random.randint(0, 80)
            loc = random.randint(10, 2000)
            comment_ratio = round(random.uniform(0, 0.5), 3)
            func_count = random.randint(1, 30)
            class_count = random.randint(0, 10)
            nesting = random.randint(0, 8)
            avg_func_len = round(random.uniform(3, 100), 1)
            params = round(random.uniform(0, 8), 1)
            halstead_diff = round(random.uniform(1, 100), 2)
            halstead_effort = round(random.uniform(100, 500000), 2)
            halstead_vol = round(random.uniform(50, 10000), 2)
            mi = round(random.uniform(10, 100), 2)
            dup_ratio = round(random.uniform(0, 0.5), 3)
            coupling = round(random.uniform(0, 20), 1)
            imports = random.randint(0, 30)
            error_handling = random.choice([0, 1])
            type_hints = random.choice([0, 1])
            test_cov = round(random.uniform(0, 100), 1)

            # Bug probability heuristic — higher complexity, less docs/tests → more bugs
            bug_score = (
                cc * 0.03 +
                cog * 0.02 +
                nesting * 0.05 +
                avg_func_len * 0.01 +
                (1 - comment_ratio) * 0.1 +
                (1 - mi / 100) * 0.3 +
                dup_ratio * 0.2 +
                (1 - error_handling) * 0.1 +
                (1 - test_cov / 100) * 0.2
            )

            # Add noise
            bug_score += random.gauss(0, 0.15)
            has_bug = 1 if bug_score > 0.5 else 0

            writer.writerow([
                cc, cog, loc, comment_ratio, func_count, class_count,
                nesting, avg_func_len, params, halstead_diff, halstead_effort,
                halstead_vol, mi, dup_ratio, coupling, imports,
                error_handling, type_hints, test_cov, has_bug,
            ])

    print(f"[+] Generated {num_samples} samples -> {output_path}")


if __name__ == "__main__":
    generate_dataset("ml/datasets/sample_code_metrics.csv", num_samples=5000)
