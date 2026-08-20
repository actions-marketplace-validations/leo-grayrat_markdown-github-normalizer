"""Markdown normalization for reliable GitHub rendering."""

from __future__ import annotations

import re

_FENCE = re.compile(r"^\s*(```+|~~~+)")
_LIST = re.compile(r"^\s*(?:[-+*]|\d+[.)])\s+")
_HEADING = re.compile(r"^\s{0,3}#{1,6}(?:\s+|$)")
_HRULE = re.compile(r"^\s{0,3}(?:(?:-\s*){3,}|(?:\*\s*){3,}|(?:_\s*){3,})$")
_INLINE_CODE = re.compile(r"(`[^`\n]*`)")
_INLINE_MATH = re.compile(r"\\\((.+?)\\\)")


def _convert_inline_math(line: str) -> str:
    """Convert MathJax-style inline delimiters outside inline code spans."""
    parts = _INLINE_CODE.split(line)
    for index in range(0, len(parts), 2):
        parts[index] = _INLINE_MATH.sub(lambda match: f"${match.group(1)}$", parts[index])
    return "".join(parts)


def _is_structured(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if _HEADING.match(line) or _LIST.match(line) or _HRULE.match(line):
        return True
    if line[:1].isspace():
        return True
    if stripped.startswith((">", "<", "![](", "![")):
        return True
    if "|" in line:
        return True
    return False


def _convert_delimiters(lines: list[str]) -> list[str]:
    output: list[str] = []
    in_fence = False
    fence_token = ""

    for line in lines:
        fence = _FENCE.match(line)
        if fence:
            token = fence.group(1)
            if not in_fence:
                in_fence = True
                fence_token = token[0]
            elif token[0] == fence_token:
                in_fence = False
                fence_token = ""
            output.append(line)
            continue

        if in_fence:
            output.append(line)
            continue

        prefix_match = re.match(r"^(?P<prefix>\s*(?:>\s*)*)\\([\[\]])\s*$", line)
        if prefix_match:
            output.append(prefix_match.group("prefix") + "$$")
            continue

        output.append(_convert_inline_math(line))

    return output


def normalize_markdown(text: str) -> str:
    """Normalize common Typora/GPT Markdown forms for GitHub rendering."""
    had_trailing_newline = text.endswith("\n")
    lines = _convert_delimiters(text.splitlines())

    output: list[str] = []
    in_fence = False
    fence_token = ""
    in_math = False
    previous_plain = False
    pending_blank_after_math = False

    for line in lines:
        fence = _FENCE.match(line)
        if fence:
            token = fence.group(1)
            if not in_fence:
                in_fence = True
                fence_token = token[0]
            elif token[0] == fence_token:
                in_fence = False
                fence_token = ""
            if pending_blank_after_math and line.strip() and output and output[-1] != "":
                output.append("")
            pending_blank_after_math = False
            output.append(line)
            previous_plain = False
            continue

        if in_fence:
            output.append(line)
            previous_plain = False
            continue

        if line.strip() == "$$" and line == line.lstrip():
            if not in_math:
                if output and output[-1] != "":
                    output.append("")
                in_math = True
                output.append(line)
            else:
                output.append(line)
                in_math = False
                pending_blank_after_math = True
            previous_plain = False
            continue

        if in_math:
            output.append(line)
            previous_plain = False
            continue

        if pending_blank_after_math:
            if line.strip() and output and output[-1] != "":
                output.append("")
            pending_blank_after_math = False

        if not line.strip():
            if not output or output[-1] != "":
                output.append("")
            previous_plain = False
            continue

        current_plain = not _is_structured(line)
        if current_plain and previous_plain and output and output[-1] != "":
            output.append("")
        output.append(line)
        previous_plain = current_plain

    result = "\n".join(output)
    if had_trailing_newline:
        result += "\n"
    return result
