from __future__ import annotations

import re
from collections.abc import Iterable

from asgk_lib.common import yaml_dedent


class TaskFieldAmbiguityError(ValueError):
    """Raised when a task-field source has more than one possible meaning."""

    def __init__(self, reasons: Iterable[str]):
        self.reasons = tuple(dict.fromkeys(str(reason) for reason in reasons))
        super().__init__("; ".join(self.reasons))


def normalized_task_field_label(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", label.strip().lower()).strip("_")


def _visible_markdown_headings(
    lines: list[str],
) -> list[tuple[int, int, str, str]]:
    headings: list[tuple[int, int, str, str]] = []
    visible_lines = [False] * len(lines)
    fence_character: str | None = None
    fence_length = 0

    for index, line in enumerate(lines):
        if fence_character is not None:
            closing = re.match(
                rf"^ {{0,3}}{re.escape(fence_character)}"
                rf"{{{fence_length},}}[ \t]*$",
                line,
            )
            if closing:
                fence_character = None
                fence_length = 0
            continue

        opening = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if opening:
            delimiter = opening.group(1)
            fence_character = delimiter[0]
            fence_length = len(delimiter)
            continue
        visible_lines[index] = True

    setext_underlines: set[int] = set()
    for index, line in enumerate(lines):
        if not visible_lines[index] or index in setext_underlines:
            continue
        heading = re.match(r"^ {0,3}(#{1,6})[ \t]+(.+?)\s*$", line)
        if heading:
            label = re.sub(
                r"[ \t]+#+[ \t]*$",
                "",
                heading.group(2),
            ).strip()
            headings.append(
                (index, len(heading.group(1)), label, "atx")
            )
            continue

        if index + 1 >= len(lines) or not visible_lines[index + 1]:
            continue
        underline = re.match(r"^ {0,3}(=+|-+)[ \t]*$", lines[index + 1])
        label = line.strip()
        if not underline or not label:
            continue
        headings.append(
            (
                index,
                1 if underline.group(1).startswith("=") else 2,
                label,
                "setext",
            )
        )
        setext_underlines.add(index + 1)

    return headings


def _section_end(
    headings: list[tuple[int, int, str, str]],
    position: int,
    line_count: int,
    *,
    same_or_higher_only: bool,
) -> int:
    line_index, level, _, _ = headings[position]
    for next_line, next_level, _, _ in headings[position + 1 :]:
        if next_line <= line_index:
            continue
        if not same_or_higher_only or next_level <= level:
            return next_line
    return line_count


def _heading_content_start(
    heading: tuple[int, int, str, str],
) -> int:
    line_index, _, _, style = heading
    return line_index + (2 if style == "setext" else 1)


def _section_content(
    lines: list[str],
    headings: list[tuple[int, int, str, str]],
    position: int,
    end: int,
) -> str:
    start = _heading_content_start(headings[position])
    nested_setext_underlines = {
        line_index + 1
        for line_index, _, _, style in headings[position + 1 :]
        if style == "setext" and start <= line_index < end
    }
    return "\n".join(
        line
        for index, line in enumerate(lines[start:end], start=start)
        if index not in nested_setext_underlines
    ).strip()


def parse_markdown_task_field_sections(text: str) -> dict[str, object]:
    """Parse visible Markdown heading sections.

    This compatibility helper ignores headings inside fenced code. Authority
    callers should use ``parse_visible_task_fields`` so ambiguity is rejected.
    """

    lines = text.splitlines()
    headings = _visible_markdown_headings(lines)
    fields: dict[str, object] = {}
    for position, heading in enumerate(headings):
        _, _, label, _ = heading
        field = normalized_task_field_label(label)
        if not field:
            continue
        end = _section_end(
            headings,
            position,
            len(lines),
            same_or_higher_only=False,
        )
        content = _section_content(lines, headings, position, end)
        if not content or content in {"_No response_", "No response"}:
            continue
        fields[field] = content
    return fields


def material_items(value: object) -> list[str]:
    if isinstance(value, list):
        return [
            str(item).strip().strip('"').strip("'")
            for item in value
            if str(item).strip().strip('"').strip("'")
        ]
    if not isinstance(value, str):
        return []
    items: list[str] = []
    for line in value.splitlines():
        cleaned = line.strip()
        if not cleaned or cleaned in {"```", "```yaml", "```text"}:
            continue
        cleaned = re.sub(r"^[-*]\s+", "", cleaned)
        cleaned = re.sub(r"^- \[[ xX]\]\s+", "", cleaned)
        cleaned = cleaned.strip().strip('"').strip("'")
        if cleaned:
            items.append(cleaned)
    return items


def task_packet_yaml_source(text: str) -> str:
    source, ambiguity_reasons = task_packet_yaml_source_checked(text, ())
    if ambiguity_reasons:
        raise TaskFieldAmbiguityError(ambiguity_reasons)
    return source


def _top_level_field_block(text: str, field: str) -> tuple[list[str], str]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(
            rf"^{re.escape(field)}[ \t]*:[ \t]*(.*?)\s*$",
            line,
        )
        if not match:
            continue
        block: list[str] = []
        for child in lines[index + 1 :]:
            if (
                child.strip()
                and not child.startswith((" ", "\t"))
                and re.match(r"^[A-Za-z0-9_\-]+[ \t]*:", child)
            ):
                break
            block.append(child)
        return block, match.group(1).strip()
    return [], ""


def task_packet_yaml_source_checked(
    text: str,
    packet_fields: Iterable[str],
) -> tuple[str, list[str]]:
    document_fields, reasons = parse_simple_task_packet_yaml_checked(text)
    wrappers = [
        field
        for field in ("bad_input", "task_packet")
        if field in document_fields
    ]
    if len(wrappers) > 1:
        reasons.append(
            "multiple task-packet wrapper fields: " + ", ".join(wrappers)
        )

    nested_wrappers = [
        line.strip().split(":", 1)[0]
        for line in text.splitlines()
        if re.match(r"^[ \t]+(?:bad_input|task_packet)[ \t]*:", line)
    ]
    if nested_wrappers:
        reasons.append(
            "nested task-packet wrapper fields are not supported: "
            + ", ".join(dict.fromkeys(nested_wrappers))
        )

    if not wrappers:
        return text, list(dict.fromkeys(reasons))

    wrapper = wrappers[0]
    normalized_packet_fields = {
        normalized_task_field_label(field)
        for field in packet_fields
    }
    raw_fields = [
        field
        for field in document_fields
        if (
            normalized_task_field_label(field) in normalized_packet_fields
            and field not in {"bad_input", "task_packet"}
        )
    ]
    if raw_fields:
        reasons.append(
            "raw task-packet fields cannot accompany a wrapper: "
            + ", ".join(raw_fields)
        )
    unexpected_top_level = [
        field
        for field in document_fields
        if field not in {wrapper, "negative_case"}
        and field not in raw_fields
    ]
    if unexpected_top_level:
        reasons.append(
            "unexpected top-level fields accompany task-packet wrapper: "
            + ", ".join(unexpected_top_level)
        )

    block, inline_value = _top_level_field_block(text, wrapper)
    if inline_value:
        reasons.append(
            f"{wrapper} wrapper must contain one indented packet object"
        )
    if not block:
        reasons.append(f"{wrapper} wrapper has no packet content")
    return yaml_dedent(block), list(dict.fromkeys(reasons))


def _simple_yaml_scalar(value: str) -> object:
    stripped = value.strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in {
        '"',
        "'",
    }:
        return stripped[1:-1]

    token = re.split(r"[ \t]+#", stripped, maxsplit=1)[0].strip()
    lowered = token.lower()
    if lowered in {"null", "~"}:
        return None
    if lowered in {"true", "yes", "on"}:
        return True
    if lowered in {"false", "no", "off"}:
        return False
    numeric = token.replace("_", "")
    if re.fullmatch(
        r"[+-]?0(?:[bB][01]+|[oO][0-7]+|[xX][0-9a-fA-F]+)",
        numeric,
    ):
        try:
            return int(numeric, 0)
        except ValueError:
            return 0
    if re.fullmatch(r"[+-]?\d+", numeric):
        try:
            return int(numeric, 10)
        except ValueError:
            return 0
    if (
        re.fullmatch(
            r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?",
            numeric,
        )
        or re.fullmatch(r"[+-]?\.(?:inf|nan)", lowered)
    ):
        try:
            return float(numeric)
        except ValueError:
            return float("nan")
    return stripped


def parse_simple_task_packet_yaml_checked(
    text: str,
) -> tuple[dict[str, object], list[str]]:
    """Parse the repository's dependency-free task-packet YAML subset.

    This is not a general YAML parser. It covers the canonical task-packet shape:
    top-level scalar fields and top-level list fields. For full YAML features,
    keep the source in JSON or add a separately approved dependency.
    """

    packet: dict[str, object] = {}
    seen_fields: dict[str, str] = {}
    ambiguity_reasons: list[str] = []
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            index += 1
            continue
        quoted_key = re.match(
            r"^([\"'])([^\"']+)\1[ \t]*:[ \t]*(.*?)\s*$",
            line,
        )
        if quoted_key:
            ambiguity_reasons.append(
                "quoted top-level task fields are unsupported: "
                + quoted_key.group(2)
            )
            index += 1
            continue
        match = re.match(r"^([A-Za-z0-9_\-]+)[ \t]*:[ \t]*(.*?)\s*$", line)
        if not match:
            index += 1
            continue
        field = match.group(1)
        normalized_field = normalized_task_field_label(field)
        if normalized_field in seen_fields:
            ambiguity_reasons.append(
                "duplicate top-level task field: "
                f"{field} (first declared as {seen_fields[normalized_field]})"
            )
        else:
            seen_fields[normalized_field] = field
        value = match.group(2).strip()
        if value:
            packet[field] = _simple_yaml_scalar(value)
            index += 1
            continue

        children: list[object] = []
        index += 1
        while index < len(lines):
            child = lines[index]
            child_stripped = child.strip()
            if (
                child_stripped
                and not child.startswith((" ", "\t"))
                and (
                    re.match(
                        r"^[A-Za-z0-9_\-]+[ \t]*:",
                        child_stripped,
                    )
                    or re.match(
                        r"^([\"'])[^\"']+\1[ \t]*:",
                        child_stripped,
                    )
                )
            ):
                break
            if child_stripped:
                item = re.match(r"^[ \t]*-[ \t]*(.*?)\s*$", child)
                if item:
                    raw_item_value = item.group(1).strip()
                    if raw_item_value:
                        children.append(_simple_yaml_scalar(raw_item_value))
            index += 1
        packet[field] = children
    return packet, list(dict.fromkeys(ambiguity_reasons))


def parse_simple_task_packet_yaml(text: str) -> dict[str, object]:
    packet, ambiguity_reasons = parse_simple_task_packet_yaml_checked(text)
    if ambiguity_reasons:
        raise TaskFieldAmbiguityError(ambiguity_reasons)
    return packet


def _canonical_task_field_source(
    section_lines: list[str],
) -> tuple[str, list[str]]:
    blocks: list[tuple[str, list[str]]] = []
    outside_lines: list[str] = []
    active_character: str | None = None
    active_length = 0
    active_info = ""
    active_lines: list[str] = []

    for line in section_lines:
        if active_character is not None:
            closing = re.match(
                rf"^ {{0,3}}{re.escape(active_character)}"
                rf"{{{active_length},}}[ \t]*$",
                line,
            )
            if closing:
                blocks.append((active_info, active_lines))
                active_character = None
                active_length = 0
                active_info = ""
                active_lines = []
            else:
                active_lines.append(line)
            continue

        opening = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if opening:
            delimiter = opening.group(1)
            active_character = delimiter[0]
            active_length = len(delimiter)
            info = opening.group(2).strip()
            active_info = info.split(maxsplit=1)[0].lower() if info else ""
            active_lines = []
            continue
        outside_lines.append(line)

    reasons: list[str] = []
    if active_character is not None:
        reasons.append("unterminated fenced block in Required Task Fields section")
    if len(blocks) > 1:
        reasons.append(
            "multiple fenced blocks in Required Task Fields section"
        )
    if blocks:
        info, block_lines = blocks[0]
        if info not in {"", "yaml", "yml"}:
            reasons.append(
                "Required Task Fields fence must be unlabeled, yaml, or yml"
            )
        outside_packet, outside_reasons = parse_simple_task_packet_yaml_checked(
            "\n".join(outside_lines)
        )
        reasons.extend(outside_reasons)
        if outside_packet:
            reasons.append(
                "task fields appear both inside and outside the canonical YAML fence"
            )
        return "\n".join(block_lines), reasons
    return "\n".join(section_lines), reasons


def parse_visible_task_fields(
    text: str,
    recognized_fields: Iterable[str],
) -> tuple[dict[str, object], list[str]]:
    """Parse one visible, unambiguous task-field representation.

    Supported representations are individual visible Markdown task-field
    headings, or one visible ``Required Task Fields`` section containing the
    dependency-free YAML subset. Fenced examples outside that canonical section
    never participate in authority parsing.
    """

    recognized = set(recognized_fields)
    lines = text.splitlines()
    headings = _visible_markdown_headings(lines)
    canonical_positions: list[int] = []
    individual_positions: dict[str, list[int]] = {}

    malformed_canonical_headings: list[str] = []
    for position, (_, level, label, style) in enumerate(headings):
        field = normalized_task_field_label(label)
        if field == "required_task_fields":
            if (
                label == "Required Task Fields"
                and level == 2
                and style == "atx"
            ):
                canonical_positions.append(position)
            else:
                malformed_canonical_headings.append(
                    "Required Task Fields must use the exact ATX H2 heading"
                )
        elif field in recognized:
            individual_positions.setdefault(field, []).append(position)

    reasons: list[str] = list(malformed_canonical_headings)
    if len(canonical_positions) > 1:
        reasons.append("multiple visible Required Task Fields sections")
    for field, positions in individual_positions.items():
        if len(positions) > 1:
            reasons.append(f"duplicate visible task-field heading: {field}")
    if canonical_positions and individual_positions:
        reasons.append(
            "mixed Required Task Fields and individual task-field headings"
        )
    if reasons:
        return {}, list(dict.fromkeys(reasons))

    if canonical_positions:
        position = canonical_positions[0]
        heading = headings[position]
        end = _section_end(
            headings,
            position,
            len(lines),
            same_or_higher_only=True,
        )
        source, source_reasons = _canonical_task_field_source(
            lines[_heading_content_start(heading) : end]
        )
        packet, yaml_reasons = parse_simple_task_packet_yaml_checked(source)
        reasons.extend(source_reasons)
        reasons.extend(yaml_reasons)
        if reasons:
            return {}, list(dict.fromkeys(reasons))
        return {
            field: value
            for field, value in packet.items()
            if field in recognized
        }, []

    fields: dict[str, object] = {}
    for field, positions in individual_positions.items():
        position = positions[0]
        heading = headings[position]
        end = _section_end(
            headings,
            position,
            len(lines),
            same_or_higher_only=True,
        )
        content = _section_content(lines, headings, position, end)
        if not content or content in {"_No response_", "No response"}:
            continue
        fields[field] = content
    return fields, []
