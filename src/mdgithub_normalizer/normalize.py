"""Markdown normalization for reliable GitHub rendering."""

from __future__ import annotations

import re

_FENCE = re.compile(r"^(?P<prefix>\s*(?:>\s*)*)(?P<mark>```+|~~~+)(?P<info>.*)$")
_DISPLAY = re.compile(r"^(?P<prefix>\s*(?:>\s*)*)(?P<delim>\$\$|\\\[|\\\])\s*$")
_INLINE_CODE = re.compile(r"(`+)(.*?)\1")
_PROTECTED_MATH = re.compile(r"\$`([^`\n]+)`\$")
_DOLLAR_MATH = re.compile(r"(?<!\\)\$(?!\$|`)(?=\S)([^$\n]*?\S)\$(?!\$)")
_PAREN_MATH = re.compile(r"(?<!\\)\\\((.+?)\\\)")
_BOLD = re.compile(r"(?<![\\*])\*\*(?!\*)(.+?)(?<![\\*])\*\*(?!\*)")
_OPERATORNAME = re.compile(r"\\operatorname\{([^{}\\]+)\}")
_CROSS = re.compile(r"\\cross(?![A-Za-z])")
_ESCAPED_SUBSCRIPT = re.compile(r"\\_\{")
_THIN_SPACE = re.compile(r"\\,[ \t]*")
_THICK_SPACE = re.compile(r"\\;[ \t]*")
_LIST = re.compile(r"^\s*(?:[-+*]|\d+[.)])\s+")
_HEADING = re.compile(r"^\s{0,3}#{1,6}(?:\s+|$)")
_HRULE = re.compile(r"^\s{0,3}(?:(?:-\s*){3,}|(?:\*\s*){3,}|(?:_\s*){3,})$")


def _fence(line: str) -> tuple[str, str, str] | None:
    match = _FENCE.match(line)
    if not match:
        return None
    return match.group("prefix"), match.group("mark"), match.group("info")


def _display(line: str) -> tuple[str, str] | None:
    match = _DISPLAY.match(line)
    if not match:
        return None
    return match.group("prefix"), match.group("delim")


def _balanced_brace_end(text: str, start: int) -> int | None:
    depth = 0
    index = start
    while index < len(text):
        char = text[index]
        escaped = index > 0 and text[index - 1] == "\\"
        if char == "{" and not escaped:
            depth += 1
        elif char == "}" and not escaped:
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def _replace_makebox(text: str) -> str:
    command = r"\makebox"
    output: list[str] = []
    cursor = 0

    while True:
        start = text.find(command, cursor)
        if start < 0:
            output.append(text[cursor:])
            return "".join(output)

        output.append(text[cursor:start])
        after_command = start + len(command)
        if after_command < len(text) and text[after_command].isalpha():
            output.append(command)
            cursor = after_command
            continue

        position = after_command
        while position < len(text) and text[position].isspace():
            position += 1

        valid = True
        for _ in range(2):
            if position >= len(text) or text[position] != "[":
                break
            close = text.find("]", position + 1)
            if close < 0:
                valid = False
                break
            position = close + 1
            while position < len(text) and text[position].isspace():
                position += 1

        if not valid or position >= len(text) or text[position] != "{":
            output.append(command)
            cursor = after_command
            continue

        close = _balanced_brace_end(text, position)
        if close is None:
            output.append(command)
            cursor = after_command
            continue

        body = _replace_makebox(text[position + 1 : close])
        output.append(r"\mbox{" + body + "}")
        cursor = close + 1


def _is_fence_close(line: str, char: str, minimum: int) -> bool:
    match = _fence(line)
    return bool(match and match[1][0] == char and len(match[1]) >= minimum and not match[2].strip())


def _convert_display_math(lines: list[str]) -> list[str]:
    output: list[str] = []
    index = 0
    fence_char = ""
    fence_len = 0
    while index < len(lines):
        line = lines[index]
        if fence_char:
            output.append(line)
            if _is_fence_close(line, fence_char, fence_len):
                fence_char = ""
                fence_len = 0
            index += 1
            continue
        current_fence = _fence(line)
        if current_fence:
            output.append(line)
            fence_char = current_fence[1][0]
            fence_len = len(current_fence[1])
            index += 1
            continue
        opener = _display(line)
        if not opener or opener[1] == r"\]":
            output.append(line)
            index += 1
            continue
        closer = "$$" if opener[1] == "$$" else r"\]"
        close_index = index + 1
        while close_index < len(lines):
            candidate = _display(lines[close_index])
            if candidate and candidate[1] == closer:
                break
            close_index += 1
        if close_index == len(lines):
            output.append(line)
            index += 1
            continue
        close_prefix, _ = _display(lines[close_index]) or (opener[0], closer)
        output.append(f"{opener[0]}```math")
        output.extend(lines[index + 1 : close_index])
        output.append(f"{close_prefix}```")
        index = close_index + 1
    return output


def _repair_math(text: str) -> str:
    text = _replace_makebox(text)
    text = _THIN_SPACE.sub(r"\\mkern3mu ", text)
    text = _THICK_SPACE.sub(r"\\mkern5mu ", text)
    text = _CROSS.sub(r"\\times", text)
    text = _ESCAPED_SUBSCRIPT.sub("_{", text)
    return _OPERATORNAME.sub(lambda match: rf"\mathrm{{{match.group(1)}}}", text)


def _protect_math(segment: str) -> str:
    protected: list[str] = []

    def stash(body: str) -> str:
        body = _repair_math(body)
        protected.append(f"$`{body}`$")
        return f"\x00M{len(protected) - 1}\x00"

    segment = _PROTECTED_MATH.sub(lambda match: stash(match.group(1)), segment)
    segment = _PAREN_MATH.sub(lambda match: stash(match.group(1)), segment)
    segment = _DOLLAR_MATH.sub(lambda match: stash(match.group(1)), segment)
    for index, value in enumerate(protected):
        segment = segment.replace(f"\x00M{index}\x00", value)
    return segment


def _normalize_bold(segment: str) -> str:
    def repair(match: re.Match[str]) -> str:
        body = match.group(1)
        trimmed = body.rstrip(" \t")
        if not trimmed:
            return match.group(0)
        return f"**{trimmed}**{body[len(trimmed):]}"

    return _BOLD.sub(repair, segment)


def _space_inline_boundaries(segment: str) -> str:
    inline = r"(?:\$`[^`\n]+`\$|(?<![\\*])\*\*(?!\*).+?(?<![\\*])\*\*(?!\*))"
    segment = re.sub(rf"(?<=\w)({inline})", r" \1", segment)
    segment = re.sub(rf"({inline})(?=\w)", r"\1 ", segment)
    return segment


def _normalize_text_segment(segment: str) -> str:
    segment = _protect_math(segment)
    segment = _normalize_bold(segment)
    return _space_inline_boundaries(segment)


def _normalize_inline_line(line: str) -> str:
    output: list[str] = []
    cursor = 0
    for match in _INLINE_CODE.finditer(line):
        output.append(_normalize_text_segment(line[cursor : match.start()]))
        output.append(match.group(0))
        cursor = match.end()
    output.append(_normalize_text_segment(line[cursor:]))
    return "".join(output)


def _normalize_math_fences_and_inline(lines: list[str]) -> list[str]:
    output: list[str] = []
    fence_char = ""
    fence_len = 0
    math_fence = False
    for line in lines:
        if fence_char:
            if _is_fence_close(line, fence_char, fence_len):
                output.append(line)
                fence_char = ""
                fence_len = 0
                math_fence = False
            elif math_fence:
                output.append(_repair_math(line))
            else:
                output.append(line)
            continue
        current = _fence(line)
        if current:
            output.append(line)
            fence_char = current[1][0]
            fence_len = len(current[1])
            math_fence = current[2].strip().split(maxsplit=1)[0:1] == ["math"]
            continue
        output.append(_normalize_inline_line(line))
    return output


def _is_structured(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped in {"$$", r"\[", r"\]"}:
        return True
    if _HEADING.match(line) or _LIST.match(line) or _HRULE.match(line):
        return True
    if line[:1].isspace() or stripped.startswith((">", "<", "![](", "![")):
        return True
    return "|" in line


def _normalize_layout(lines: list[str]) -> list[str]:
    output: list[str] = []
    fence_char = ""
    fence_len = 0
    math_fence = False
    top_level_math = False
    previous_plain = False
    blank_after_math = False
    for line in lines:
        if fence_char:
            output.append(line)
            if _is_fence_close(line, fence_char, fence_len):
                if math_fence and top_level_math:
                    blank_after_math = True
                fence_char = ""
                fence_len = 0
                math_fence = False
                top_level_math = False
            previous_plain = False
            continue
        current = _fence(line)
        if current:
            math_fence = current[2].strip().split(maxsplit=1)[0:1] == ["math"]
            top_level_math = math_fence and not current[0]
            if top_level_math and output and output[-1] != "":
                output.append("")
            output.append(line)
            fence_char = current[1][0]
            fence_len = len(current[1])
            blank_after_math = False
            previous_plain = False
            continue
        raw_display = _display(line)
        if raw_display and not raw_display[0] and raw_display[1] in {"$$", r"\["}:
            if output and output[-1] != "":
                output.append("")
            previous_plain = False
        if blank_after_math and line.strip():
            if output and output[-1] != "":
                output.append("")
            blank_after_math = False
        if not line.strip():
            output.append(line)
            previous_plain = False
            continue
        current_plain = not _is_structured(line)
        if current_plain and previous_plain and output and output[-1] != "":
            output.append("")
        output.append(line)
        previous_plain = current_plain
    return output


def normalize_markdown(text: str) -> str:
    trailing_newline = text.endswith("\n")
    lines = _convert_display_math(text.splitlines())
    lines = _normalize_math_fences_and_inline(lines)
    lines = _normalize_layout(lines)
    result = "\n".join(lines)
    return result + "\n" if trailing_newline else result
