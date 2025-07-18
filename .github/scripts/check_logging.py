import os
import re
import subprocess
import sys

def check_for_logging_info():
    # Get staged files
    diff_range = os.environ.get("DIFF_RANGE", "HEAD^..HEAD")
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM', diff_range],
        stdout=subprocess.PIPE,
        text=True
    )
    staged_files = result.stdout.splitlines()

    # Filter for Python files
    python_files = [f for f in staged_files if f.endswith('.py')]

    if not python_files:
        return 0  # No Python files changed, success

    pattern = re.compile(r'logging\.info\(')
    violations = []

    for file_path in python_files:
        # Get the diff for this file
        diff_result = subprocess.run(
            ['git', 'diff', '--cached', '--', file_path],
            stdout=subprocess.PIPE,
            text=True
        )
        diff = diff_result.stdout

        # Check each added line in the diff
        for line in diff.split('\n'):
            print(f"Checking line: {line.strip()} in {file_path}")
            if line.startswith('+') and not line.startswith('+++'):
                if pattern.search(line) and not line.endswith('#--- IGNORE ---'):
                    violations.append((file_path, line.strip()))

    if violations:
        print("\nERROR: Found logging.info statements in changes:")
        for file_path, line in violations:
            print(f"::error file={file_path},line={line}::  Avoid logging.info")
        print("\nPlease remove logging.info statements before committing.")
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(check_for_logging_info())