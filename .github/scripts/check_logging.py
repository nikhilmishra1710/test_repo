import os
import subprocess
import sys
import re
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


def parse_diff_with_line_numbers(filepath: str, diff_range: str) -> List[Tuple[int, str]]:
    """
    Parse the diff for the given file and return added lines with accurate line numbers.
    """
    result = subprocess.run(
        ["git", "diff", "--unified=0", diff_range, "--", filepath],
        stdout=subprocess.PIPE,
        text=True,
        check=True
    )

    added_lines = []
    current_line = None

    for line in result.stdout.splitlines():
        if line.startswith('@@'):
            match = re.search(r'\+(\d+)', line)
            if match:
                current_line = int(match.group(1)) - 1  # initialize before first addition
        elif line.startswith('+') and not line.startswith('+++'):
            if current_line is not None:
                current_line += 1
                added_lines.append((current_line, line[1:].rstrip()))
        elif not line.startswith('-'):
            if current_line is not None:
                current_line += 1  # skip unchanged lines in diff

    return added_lines


def check_logging_info(filepath: str, diff_range: str) -> bool:
    """
    Check for `logging.info(...)` usage in added lines of a given file.
    """
    found = False
    try:
        added_lines = parse_diff_with_line_numbers(filepath, diff_range)
        for lineno, line in added_lines:
            line = line.strip()
            if (
                "logging.info" in line
                and "logging.error" not in line
                and "#--- IGNORE ---" not in line
            ):
                print(f"::error file={filepath},line={lineno}::Avoid using logging.info in production code.")
                found = True
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
