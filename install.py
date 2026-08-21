#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

WORKFLOW = """name: Normalize Markdown

on:
  push:
    paths: ['**/*.md', '**/*.markdown']

permissions:
  contents: write

jobs:
  normalize:
    uses: leo-grayrat/markdown-github-normalizer/.github/workflows/normalize.yml@main
"""


def _ensure_unicode_output(stream) -> None:
    encoding = getattr(stream, "encoding", None)
    if not encoding:
        return
    try:
        "中文".encode(encoding)
    except (UnicodeEncodeError, LookupError):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


def main() -> int:
    _ensure_unicode_output(sys.stdout)
    _ensure_unicode_output(sys.stderr)

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        print("未找到 Git。 / Git not found.", file=sys.stderr)
        return 1

    if result.returncode != 0:
        print(
            "请在 Git 仓库中运行此命令。 / Run this command inside a Git repository.",
            file=sys.stderr,
        )
        return 1

    repo_root = Path(result.stdout.strip())
    workflow_file = repo_root / ".github" / "workflows" / "normalize-markdown.yml"
    workflow_file.parent.mkdir(parents=True, exist_ok=True)
    with workflow_file.open("w", encoding="utf-8", newline="\n") as file:
        file.write(WORKFLOW)

    print(f"已安装 / Installed: {workflow_file.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
