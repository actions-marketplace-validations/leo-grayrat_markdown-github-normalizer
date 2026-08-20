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


def main() -> int:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        print("未找到 Git。", file=sys.stderr)
        return 1

    if result.returncode != 0:
        print("请在 Git 仓库中运行此命令。", file=sys.stderr)
        return 1

    repo_root = Path(result.stdout.strip())
    workflow_file = repo_root / ".github" / "workflows" / "normalize-markdown.yml"
    workflow_file.parent.mkdir(parents=True, exist_ok=True)
    with workflow_file.open("w", encoding="utf-8", newline="\n") as file:
        file.write(WORKFLOW)

    print(f"已安装：{workflow_file.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
