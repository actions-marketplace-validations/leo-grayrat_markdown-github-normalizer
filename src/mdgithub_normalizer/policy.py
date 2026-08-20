"""Mode resolution and repository configuration."""

from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path
import re
import tomllib

_VALID_MODES = {"copy", "replace"}
_COMMIT_MODE = re.compile(r"\[md:(copy|replace)\]", re.IGNORECASE)


@dataclass(frozen=True)
class Rule:
    pattern: str
    mode: str


@dataclass(frozen=True)
class Config:
    default_mode: str = "copy"
    rules: tuple[Rule, ...] = ()


def _validate_mode(mode: str) -> str:
    normalized = mode.lower()
    if normalized not in _VALID_MODES:
        raise ValueError(f"unsupported mode: {mode}")
    return normalized


def load_config(path: Path) -> Config:
    if not path.is_file():
        return Config()
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    default_mode = _validate_mode(str(data.get("default_mode", "copy")))
    rules = tuple(
        Rule(pattern=str(item["pattern"]), mode=_validate_mode(str(item["mode"])))
        for item in data.get("rules", [])
    )
    return Config(default_mode=default_mode, rules=rules)


def resolve_mode(
    path: Path,
    *,
    config: Config,
    explicit_mode: str = "auto",
    commit_message: str = "",
) -> str:
    if explicit_mode.lower() != "auto":
        return _validate_mode(explicit_mode)

    matches = _COMMIT_MODE.findall(commit_message)
    if matches:
        return _validate_mode(matches[-1])

    normalized_path = path.as_posix()
    for rule in config.rules:
        if fnmatchcase(normalized_path, rule.pattern):
            return rule.mode

    return config.default_mode


def is_generated_path(path: Path) -> bool:
    return path.stem.endswith("-github") and path.suffix.lower() in {".md", ".markdown"}


def output_path_for_copy(path: Path) -> Path:
    if path.suffix.lower() not in {".md", ".markdown"}:
        raise ValueError(f"not a Markdown path: {path}")
    return path.with_name(f"{path.stem}-github{path.suffix}")
