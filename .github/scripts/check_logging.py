import os
import subprocess
import sys
import ast
from typing import List, Tuple

def get_changed_files(diff_range: str) -> List[str]:
    """Return a list of changed Python files in the given diff range."""
    result = subprocess.run(
        ["git", "diff", "--name-only", diff_range],
        stdout=subprocess.PIPE,
        text=True,
        check=True
    )
    return [f.strip() for f in result.stdout.splitlines() if f.endswith(".py")]

def parse_diff(filepath: str, diff_range: str) -> List[Tuple[int, str]]:
    """Parse the diff to get added or changed lines with line numbers."""
    result = subprocess.run(
        ["git", "diff", diff_range, "--", filepath],
        stdout=subprocess.PIPE,
        text=True,
        check=True
    )

    added_lines = []
    lines = result.stdout.splitlines()

    print(lines)
    current_line = None
    for line in lines:
        if line.startswith("@@"):
            # Parse hunk header to get starting line number
            parts = line.split(" ")
            new_file_range = parts[2]  # e.g., "+12,7"
            start_line = int(new_file_range.split(",")[0][1:])
            current_line = start_line
        elif line.startswith("+") and not line.startswith("+++"):
            added_lines.append((current_line, line[1:]))  # remove '+' prefix
            current_line += 1
        elif not line.startswith("-"):
            current_line += 1  # move to next line even if it's context

    return added_lines

def check_logging_info(filepath: str, diff_range: str) -> bool:
    """Check for logging.info in added lines of a given file."""
    found = False
    try:
        added_lines = parse_diff(filepath, diff_range)
        for line_number, content in added_lines:
            # Skip ignored lines
            if content.strip().endswith("#--- IGNORE ---"):
                continue

            # Use AST to detect logging.info(...)
            try:
                node = ast.parse(content, mode="exec")
                for stmt in ast.walk(node):
                    if (
                        isinstance(stmt, ast.Call)
                        and isinstance(stmt.func, ast.Attribute)
                        and stmt.func.attr == "info"
                        and getattr(stmt.func.value, "id", "") == "logging"
                    ):
                        print(f"::error file={filepath},line={line_number}::Avoid using logging.info in production code.")
                        found = True
            except SyntaxError:
                continue
    except subprocess.CalledProcessError as e:
        print(f"Failed to parse diff for {filepath}: {e}", file=sys.stderr)
    return found

def main():
    diff_range = os.environ.get("DIFF_RANGE", "HEAD^..HEAD")
    changed_files = get_changed_files(diff_range)

    had_error = False
    for file in changed_files:
        if os.path.exists(file):
            if check_logging_info(file, diff_range):
                had_error = True

    if had_error:
        sys.exit(1)

if __name__ == "__main__":
    main()
