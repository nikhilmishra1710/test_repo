#!/usr/bin/env python3
import os
import subprocess
import json
import sys


def get_changed_python_files(diff_range):
    result = subprocess.run(
        ["git", "diff", "--name-only", diff_range],
        stdout=subprocess.PIPE,
        text=True,
        check=True
    )
    return [f.strip() for f in result.stdout.splitlines() if f.endswith(".py")]


def check_logging_info(filepath):
    annotations = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                if "logging.info" in line:
                    annotations.append({
                        "path": filepath,
                        "start_line": i,
                        "end_line": i,
                        "annotation_level": "warning",
                        "message": "Avoid using logging.info in production code."
                    })
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
    return annotations


def main():
    diff_range = os.environ.get("DIFF_RANGE", "HEAD^..HEAD")
    changed_files = get_changed_python_files(diff_range)

    all_annotations = []
    for f in changed_files:
        if os.path.exists(f):
            all_annotations.extend(check_logging_info(f))

    if all_annotations:
        with open("annotations.json", "w") as f:
            json.dump({"annotations": all_annotations}, f)
        sys.exit(1)  # Fail to trigger annotation step
    else:
        print("No logging.info violations found.")


if __name__ == "__main__":
    main()