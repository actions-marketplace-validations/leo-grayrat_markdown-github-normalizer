#!/usr/bin/env python3
"""Runtime entry point for the composite GitHub Action."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

ACTION_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ACTION_ROOT / "src"))

from mdgithub_normalizer.cli import process_file  # noqa: E402
from mdgithub_normalizer.policy import is_generated_path  # noqa: E402


def git(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=cwd, text=True, capture_output=True, check=check
    )


def _existing_commit(repo: Path, ref: str) -> bool:
    if not ref or set(ref) == {"0"}:
        return False
    return git("cat-file", "-e", f"{ref}^{{commit}}", cwd=repo, check=False).returncode == 0


def discover_changed_paths(repo: Path, before: str = "") -> list[Path]:
    if _existing_commit(repo, before):
        result = subprocess.run(
            ["git", "diff", "--name-only", "-z", before, "HEAD", "--"],
            cwd=repo,
            capture_output=True,
            check=True,
        )
    else:
        result = subprocess.run(
            ["git", "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", "-z", "HEAD"],
            cwd=repo,
            capture_output=True,
            check=True,
        )
    return [Path(item.decode("utf-8")) for item in result.stdout.split(b"\0") if item]


def markdown_paths(repo: Path, paths: list[Path]) -> list[Path]:
    result: list[Path] = []
    for path in paths:
        if path.suffix.lower() not in {".md", ".markdown"}:
            continue
        if is_generated_path(path):
            continue
        if (repo / path).is_file():
            result.append(path)
    return result


def all_markdown_paths(repo: Path) -> list[Path]:
    result: list[Path] = []
    for path in repo.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        relative = path.relative_to(repo)
        if relative.suffix.lower() in {".md", ".markdown"} and not is_generated_path(relative):
            result.append(relative)
    return sorted(result)


def main() -> int:
    repo = Path(os.environ.get("GITHUB_WORKSPACE", Path.cwd())).resolve()
    actor = os.environ.get("GITHUB_ACTOR", "")
    if actor == "github-actions[bot]":
        print("skip: normalization commit triggered this run")
        return 0

    commit_message = git("log", "-1", "--pretty=%B", cwd=repo).stdout
    if "[skip md-normalizer]" in commit_message.lower():
        print("skip: commit requested md-normalizer skip")
        return 0

    explicit_files = os.environ.get("INPUT_FILES", "").strip()
    if explicit_files:
        candidates = [Path(line.strip()) for line in explicit_files.splitlines() if line.strip()]
    else:
        candidates = discover_changed_paths(repo, os.environ.get("NORMALIZER_BEFORE", ""))

    config_relative = Path(os.environ.get("INPUT_CONFIG", ".markdown-github-normalizer.toml"))
    if config_relative in candidates:
        candidates = all_markdown_paths(repo)

    files = markdown_paths(repo, candidates)
    if not files:
        print("clean: no Markdown inputs")
        return 0

    mode = os.environ.get("INPUT_MODE", "auto")
    config_path = repo / config_relative
    changed_outputs: list[Path] = []

    for relative in files:
        result = process_file(
            relative,
            explicit_mode=mode,
            commit_message=commit_message,
            config_path=config_path,
            repo_root=repo,
        )
        output_relative = result.output_path.relative_to(repo)
        print(
            f"{'write' if result.changed else 'clean'}: {relative} -> "
            f"{output_relative} ({result.mode})"
        )
        if result.changed:
            changed_outputs.append(output_relative)

    if not changed_outputs:
        print("clean: no repository changes")
        return 0

    git("config", "user.name", "github-actions[bot]", cwd=repo)
    git(
        "config",
        "user.email",
        "41898282+github-actions[bot]@users.noreply.github.com",
        cwd=repo,
    )
    git("add", "--", *(path.as_posix() for path in changed_outputs), cwd=repo)
    git("commit", "-m", "chore: normalize markdown [skip md-normalizer]", cwd=repo)
    push = git("push", cwd=repo, check=False)
    if push.returncode != 0:
        sys.stderr.write(push.stderr)
        return push.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
