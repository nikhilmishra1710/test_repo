import os
import subprocess
import sys

def get_changed_files(diff_range):
    result = subprocess.run(
        ["git", "diff", "--name-only", diff_range],
        stdout=subprocess.PIPE,
        text=True,
        check=True
    )
    return [f.strip() for f in result.stdout.splitlines() if f.endswith(".py")]

def check_logging_info(filepath):
    found = False
    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if "logging.info" in line:
                print(f"::error file={filepath},line={i}::Avoid using logging.info in production code.")
                found = True
    return found

def main():
    diff_range = os.environ.get("DIFF_RANGE", "HEAD^..HEAD")
    changed_files = get_changed_files(diff_range)

    had_error = False
    for file in changed_files:
        if os.path.exists(file):
            if check_logging_info(file):
                had_error = True

    if had_error:
        sys.exit(1)

if __name__ == "__main__":
    main()
