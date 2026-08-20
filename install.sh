#!/usr/bin/env bash
set -euo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "请在 Git 仓库中运行此命令。" >&2
  exit 1
fi

workflow_dir=".github/workflows"
workflow_file="$workflow_dir/normalize-markdown.yml"
mkdir -p "$workflow_dir"
cat > "$workflow_file" <<'YAML'
name: Normalize Markdown

on:
  push:
    paths: ['**/*.md', '**/*.markdown']

permissions:
  contents: write

jobs:
  normalize:
    uses: leo-grayrat/markdown-github-normalizer/.github/workflows/normalize.yml@main
YAML

echo "已安装：$workflow_file"
