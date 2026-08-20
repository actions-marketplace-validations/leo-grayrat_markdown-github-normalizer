$ErrorActionPreference = 'Stop'

git rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Error '请在 Git 仓库中运行此命令。'
    exit 1
}

$workflowDir = '.github/workflows'
$workflowFile = Join-Path $workflowDir 'normalize-markdown.yml'
New-Item -ItemType Directory -Force -Path $workflowDir | Out-Null
@'
name: Normalize Markdown

on:
  push:
    paths: ['**/*.md', '**/*.markdown']

permissions:
  contents: write

jobs:
  normalize:
    uses: leo-grayrat/markdown-github-normalizer/.github/workflows/normalize.yml@main
'@ | Set-Content -Path $workflowFile -Encoding utf8

Write-Host "已安装：$workflowFile"
