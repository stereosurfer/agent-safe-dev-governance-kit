from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def rel(path: str | Path) -> Path:
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def read_text(path: str | Path) -> str:
    return rel(path).read_text(encoding="utf-8")


def has_see_chat(text: str) -> bool:
    return bool(re.search(r"\bsee\s+chat\b", text, flags=re.IGNORECASE))


def has_unresolved_todo(text: str) -> bool:
    return bool(re.search(r"\b(?:AI_TODO|TODO)\b", text))


def strip_html_comments(text: str) -> str:
    """Remove Markdown content hidden by HTML comments, including an unclosed tail."""

    return re.sub(r"<!--.*?(?:-->|\Z)", "", text, flags=re.DOTALL)


def _visible_level_two_heading_positions(text: str) -> tuple[str, list[tuple[int, str]]]:
    """Return comment-free Markdown and visible level-two heading line indexes."""

    visible = strip_html_comments(text)
    positions: list[tuple[int, str]] = []
    fence_character = ""
    fence_length = 0
    for index, line in enumerate(visible.splitlines()):
        if fence_character:
            if re.match(
                rf"^[ \t]{{0,3}}{re.escape(fence_character)}"
                rf"{{{fence_length},}}[ \t]*$",
                line,
            ):
                fence_character = ""
                fence_length = 0
            continue

        fence = re.match(r"^[ \t]{0,3}(`{3,}|~{3,}).*$", line)
        if fence:
            delimiter = fence.group(1)
            fence_character = delimiter[0]
            fence_length = len(delimiter)
            continue

        heading = re.match(r"^##[ \t]+(.+?)[ \t]*$", line)
        if heading:
            positions.append((index, heading.group(1).strip()))
    return visible, positions


def markdown_heading_occurrences(text: str) -> list[str]:
    _visible, positions = _visible_level_two_heading_positions(text)
    return [heading for _index, heading in positions]


def markdown_headings(text: str) -> set[str]:
    return set(markdown_heading_occurrences(text))


def markdown_section(text: str, heading: str) -> str:
    visible, positions = _visible_level_two_heading_positions(text)
    lines = visible.splitlines()
    for position_index, (line_index, found_heading) in enumerate(positions):
        if found_heading != heading:
            continue
        end_index = (
            positions[position_index + 1][0]
            if position_index + 1 < len(positions)
            else len(lines)
        )
        return "\n".join(lines[line_index + 1:end_index]).strip()
    return ""


def line_field_exists(text: str, field: str) -> bool:
    return bool(re.search(rf"^[ \t]*{re.escape(field)}[ \t]*:", text, flags=re.MULTILINE))


def raw_field_value(text: str, field: str) -> str | None:
    """Return an uncoerced same-line scalar for exact-token validation."""

    match = re.search(
        rf"^[ \t]*{re.escape(field)}[ \t]*:[ \t]*(.*?)[ \t]*$",
        text,
        flags=re.MULTILINE,
    )
    if not match:
        return None
    return match.group(1).strip()


def field_value(text: str, field: str) -> str | None:
    """Return a quote-normalized scalar value for prose-like lightweight YAML."""

    value = raw_field_value(text, field)
    if value is None:
        return None
    return value.strip('"').strip("'")


def normalized_field_value(text: str, field: str) -> str:
    value = field_value(text, field)
    if value is None:
        return ""
    return value.strip().strip('"').strip("'").lower()


def field_block_lines(text: str, field: str) -> list[str] | None:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(rf"^([ \t]*){re.escape(field)}[ \t]*:", line)
        if not match:
            continue
        field_indent = len(match.group(1).replace("\t", "    "))
        block: list[str] = []
        for child in lines[index + 1:]:
            stripped = child.strip()
            if not stripped:
                continue
            child_indent = len(re.match(r"^[ \t]*", child).group(0).replace("\t", "    "))
            if child_indent <= field_indent and re.match(r"^[A-Za-z0-9_\-]+[ \t]*:", stripped):
                break
            if child_indent > field_indent:
                block.append(child)
        return block
    return None


def list_field_has_material_item(text: str, field: str) -> bool:
    value = field_value(text, field)
    if value:
        return True
    block = field_block_lines(text, field)
    if block is None:
        return False
    for line in block:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        item = re.match(r"^-\s*(.*?)\s*$", stripped)
        if item and item.group(1).strip().strip('"').strip("'"):
            return True
    return False


def field_block_text(text: str, field: str) -> str:
    block = field_block_lines(text, field)
    return "\n".join(block or [])


def yaml_dedent(lines: list[str]) -> str:
    material = [line for line in lines if line.strip()]
    if not material:
        return ""
    min_indent = min(len(re.match(r"^[ \t]*", line).group(0).replace("\t", "    ")) for line in material)
    return "\n".join(line[min_indent:] if len(line) >= min_indent else line for line in lines)


def read_changed_paths(path: str | Path) -> set[str]:
    return {
        line.strip()
        for line in read_text(path).splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def normalize_repo_path(path: str) -> str:
    cleaned = path.strip().strip("`").strip('"').strip("'").replace("\\", "/")
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    return cleaned


def same_repo_path(left: str, right: str) -> bool:
    return normalize_repo_path(left) == normalize_repo_path(right)
