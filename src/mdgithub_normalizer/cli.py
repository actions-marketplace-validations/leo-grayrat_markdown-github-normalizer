"""Command-line interface for Markdown normalization."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from .normalize import normalize_markdown
from .policy import is_generated_path, load_config, output_path_for_copy, resolve_mode


@dataclass(frozen=True)
class ProcessResult:
    source_path: Path
    output_path: Path
    mode: str
    changed: bool
    skipped: bool = False


def process_file(
    path: Path,
    *,
    explicit_mode: str = "auto",
    commit_message: str = "",
    config_path: Path | None = None,
    repo_root: Path | None = None,
) -> ProcessResult:
    repo_root = (repo_root or Path.cwd()).resolve()
    path = path if path.is_absolute() else repo_root / path
    path = path.resolve()

    if is_generated_path(path):
        return ProcessResult(path, path, "copy", changed=False, skipped=True)
    if path.suffix.lower() not in {".md", ".markdown"}:
        return ProcessResult(path, path, "copy", changed=False, skipped=True)
    if not path.is_file():
        raise FileNotFoundError(path)

    config_file = config_path or repo_root / ".markdown-github-normalizer.toml"
    config = load_config(config_file)
    try:
        relative = path.relative_to(repo_root)
    except ValueError:
        relative = path
    mode = resolve_mode(
        relative,
        config=config,
        explicit_mode=explicit_mode,
        commit_message=commit_message,
    )

    source = path.read_text(encoding="utf-8")
    normalized = normalize_markdown(source)
    output_path = path if mode == "replace" else output_path_for_copy(path)
    previous = output_path.read_text(encoding="utf-8") if output_path.is_file() else None
    changed = previous != normalized
    if changed:
        output_path.write_text(normalized, encoding="utf-8", newline="\n")

    return ProcessResult(path, output_path, mode, changed=changed)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Normalize Markdown for GitHub rendering.")
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--mode", choices=("auto", "copy", "replace"), default="auto")
    parser.add_argument("--commit-message", default="")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    for file_path in args.files:
        result = process_file(
            file_path,
            explicit_mode=args.mode,
            commit_message=args.commit_message,
            config_path=args.config,
            repo_root=args.repo_root,
        )
        status = "skip" if result.skipped else ("write" if result.changed else "clean")
        print(f"{status}: {result.source_path} -> {result.output_path} ({result.mode})")
    return 0
