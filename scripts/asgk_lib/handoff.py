"""Typed, dependency-free validation for ASGK handoff packets."""

from __future__ import annotations

import json
import re
from pathlib import Path

from asgk_lib.common import has_see_chat, normalize_repo_path, rel

CORE_HANDOFF_ROOT = "handoff_packet"
COMPACT_HANDOFF_ROOT = "compact_handoff"
VALIDATION_STATUS_VALUES = {"pass", "fail", "blocked", "not_run"}
NON_MATERIAL_PATTERN = re.compile(
    r"\s*(?:pending|unknown|todo|tbd|none|null|n[.]*/?[.]*a|"
    r"not[\s_.-]*applicable)[.!?,:;]*\s*",
)
ASCII_LOWER_TRANSLATION = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "abcdefghijklmnopqrstuvwxyz",
)
FORBIDDEN_HANDOFF_CHARACTER_PATTERN_SOURCE = (
    r"[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F-\u009F"
    r"\u00AD\u061C\u180E\u200B-\u200F\u202A-\u202E"
    r"\u2060-\u206F\uD800-\uDFFF\uFEFF\uFFF9-\uFFFB]"
)
FORBIDDEN_HANDOFF_CHARACTER_PATTERN = re.compile(
    FORBIDDEN_HANDOFF_CHARACTER_PATTERN_SOURCE
)
UNSUPPORTED_YAML_CHARACTER_PATTERN = re.compile(
    r"[\u0000-\u0008\u000B\u000C\u000E-\u001F"
    r"\u007F-\u009F\uD800-\uDFFF]"
)

CORE_SCALAR_FIELDS = (
    "active_issue",
    "active_pr",
    "branch",
    "objective",
    "current_state",
    "next_safe_action",
)
CORE_LIST_FIELDS = (
    "durable_source_of_truth",
    "remaining",
    "allowed_paths",
    "modified_files",
    "non_goals",
    "must_not_do",
    "must_read",
    "blockers",
)
CORE_REQUIRED_FIELDS = (
    *CORE_SCALAR_FIELDS,
    *CORE_LIST_FIELDS,
    "validation_status",
)
VALIDATION_STATUS_FIELDS = ("status", "evidence", "reason")
ALLOWED_FIXTURE_METADATA_ROOTS = {"positive_case", "negative_case"}

PROOF_BOUNDARY = (
    "A passing handoff check proves only that the supplied file has one expected "
    "root, the required typed fields contain material values, validation status "
    "uses the supported enum, and the checked chat/TODO markers are absent. It "
    "does not prove that statements are true, GitHub references are live, paths "
    "are authorized, validation commands ran, work is complete, or a human gate "
    "or merge decision is satisfied."
)


class HandoffParseError(ValueError):
    """Raised when the supported YAML subset is ambiguous or malformed."""


def _finding(
    code: str,
    field: str,
    reason: str,
    *,
    blocking: bool = True,
) -> dict[str, object]:
    return {
        "code": code,
        "field": field,
        "reason": reason,
        "blocking": blocking,
    }


def _parse_scalar(source: str) -> object:
    value = source.strip()
    if not value:
        return None
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise HandoffParseError(f"invalid quoted scalar: {value}") from exc
        if not isinstance(parsed, str):
            raise HandoffParseError(f"quoted scalar is not text: {value}")
        if UNSUPPORTED_YAML_CHARACTER_PATTERN.search(parsed):
            raise HandoffParseError(
                "quoted scalar contains a control, surrogate, or format character "
                "outside the supported YAML subset"
            )
        return parsed
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise HandoffParseError(f"invalid single-quoted scalar: {value}")
        inner = value[1:-1]
        if "'" in inner.replace("''", ""):
            raise HandoffParseError(f"invalid single-quoted scalar: {value}")
        return inner.replace("''", "'")

    if re.search(r"\s+#", value):
        raise HandoffParseError(
            f"inline comments are not supported in unquoted scalars: {value}"
        )
    if value == "[]":
        return []
    if value == "{}":
        return {}
    if (
        value.startswith(
            ("#", "&", "*", "!", "%", "|", ">", "[", "{", ",", "]", "}", "@", "`")
        )
        or value in {"-", "?"}
        or value.startswith(("- ", "? "))
        or re.search(r":(?:\s|$)", value)
    ):
        raise HandoffParseError(f"advanced or ambiguous YAML scalar is unsupported: {value}")

    lowered = value.lower()
    if lowered in {"null", "~"}:
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    numeric = value.replace("_", "")
    if re.fullmatch(r"[-+]?0[xX][0-9a-fA-F]+", numeric):
        return int(numeric, 16)
    if re.fullmatch(r"[-+]?0[oO][0-7]+", numeric):
        return int(numeric, 8)
    if re.fullmatch(r"[-+]?0[bB][01]+", numeric):
        return int(numeric, 2)
    if re.fullmatch(r"[-+]?[0-9]+", numeric):
        return int(numeric)
    if re.fullmatch(
        r"[-+]?(?:(?:[0-9]+\.[0-9]*)|(?:\.[0-9]+)|(?:[0-9]+))"
        r"(?:[eE][-+]?[0-9]+)?",
        numeric,
    ):
        return float(numeric)
    if lowered in {".inf", "+.inf", "-.inf", ".nan"}:
        return float(lowered.replace(".", "", 1))
    if re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}(?:[Tt ][0-9:.+-]+[Zz]?)?",
        value,
    ):
        return ("yaml_timestamp", value)
    return value


def parse_yaml_subset(text: str) -> dict[str, object]:
    """Parse the mapping/list/scalar subset emitted by handoff-template.

    The parser intentionally rejects advanced YAML features instead of guessing.
    This keeps the core checker dependency-free and makes its proof boundary
    explicit.
    """

    forbidden_control = re.search(
        r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f\ud800-\udfff]",
        text,
    )
    if forbidden_control:
        raise HandoffParseError(
            "document contains a control character outside the supported YAML subset"
        )

    lines: list[tuple[int, int, str]] = []
    for number, raw in enumerate(text.splitlines(), start=1):
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise HandoffParseError(f"line {number}: tabs are not supported for indentation")
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        lines.append((number, indent, raw[indent:]))

    if not lines:
        raise HandoffParseError("document is empty")

    def parse_node(index: int, indent: int) -> tuple[object, int]:
        number, actual_indent, content = lines[index]
        if actual_indent != indent:
            raise HandoffParseError(
                f"line {number}: expected indentation {indent}, found {actual_indent}"
            )

        if content.startswith("-"):
            result_list: list[object] = []
            while index < len(lines):
                line_number, line_indent, line_content = lines[index]
                if line_indent < indent:
                    break
                if line_indent > indent:
                    raise HandoffParseError(
                        f"line {line_number}: unexpected nested list indentation"
                    )
                if not re.match(r"^-(?:\s|$)", line_content):
                    break
                item_source = line_content[1:].strip()
                index += 1
                if item_source:
                    result_list.append(_parse_scalar(item_source))
                elif index < len(lines) and lines[index][1] > indent:
                    child_indent = lines[index][1]
                    child, index = parse_node(index, child_indent)
                    result_list.append(child)
                else:
                    result_list.append(None)
            return result_list, index

        result_map: dict[str, object] = {}
        while index < len(lines):
            line_number, line_indent, line_content = lines[index]
            if line_indent < indent:
                break
            if line_indent > indent:
                raise HandoffParseError(
                    f"line {line_number}: unexpected mapping indentation"
                )
            if line_content.startswith("-"):
                break
            match = re.fullmatch(
                r"([A-Za-z_][A-Za-z0-9_-]*):(?:[ ]+(.*))?",
                line_content,
            )
            if not match:
                raise HandoffParseError(
                    f"line {line_number}: expected a simple key/value mapping"
                )
            key, scalar_source = match.groups()
            if key in result_map:
                raise HandoffParseError(f"line {line_number}: duplicate key: {key}")
            index += 1
            if scalar_source is not None:
                result_map[key] = _parse_scalar(scalar_source)
            elif index < len(lines) and lines[index][1] > indent:
                child_indent = lines[index][1]
                child, index = parse_node(index, child_indent)
                result_map[key] = child
            else:
                result_map[key] = None
        return result_map, index

    root_indent = lines[0][1]
    parsed, next_index = parse_node(0, root_indent)
    if next_index != len(lines):
        number = lines[next_index][0]
        raise HandoffParseError(f"line {number}: document contains an ambiguous block")
    if not isinstance(parsed, dict):
        raise HandoffParseError("document root must be a mapping")
    return parsed


def is_material_handoff_text(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    if FORBIDDEN_HANDOFF_CHARACTER_PATTERN.search(value):
        return False
    ascii_lowered = value.translate(ASCII_LOWER_TRANSLATION)
    return NON_MATERIAL_PATTERN.fullmatch(ascii_lowered) is None


def _nested_strings(value: object):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _nested_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _nested_strings(child)


def _validate_material_string_list(
    packet: dict[str, object],
    field: str,
    findings: list[dict[str, object]],
) -> None:
    if field not in packet:
        findings.append(_finding("HP_FIELD_MISSING", field, "required handoff field is missing"))
        return
    value = packet[field]
    if not isinstance(value, list):
        findings.append(
            _finding("HP_FIELD_TYPE_INVALID", field, "field must be a list of strings")
        )
        return
    if not value:
        findings.append(_finding("HP_LIST_EMPTY", field, "required list has no material item"))
        return
    for index, item in enumerate(value):
        if not isinstance(item, str):
            findings.append(
                _finding(
                    "HP_FIELD_TYPE_INVALID",
                    f"{field}[{index}]",
                    "list item must be a string",
                )
            )
        elif not is_material_handoff_text(item):
            findings.append(
                _finding(
                    "HP_FIELD_EMPTY",
                    f"{field}[{index}]",
                    "list item is empty or a generic placeholder",
                )
            )


def evaluate_handoff_text(
    text: str,
    *,
    root_name: str = CORE_HANDOFF_ROOT,
    allowed_extra_fields: set[str] | None = None,
) -> tuple[str, dict[str, object], dict[str, object] | None]:
    """Validate one handoff root and return result, public report, and packet."""

    findings: list[dict[str, object]] = []
    packet: dict[str, object] | None = None
    parse_failed = False
    try:
        document = parse_yaml_subset(text)
    except HandoffParseError as exc:
        findings.append(_finding("HP_PACKET_AMBIGUOUS", root_name, str(exc)))
        document = {}
        parse_failed = True

    present_handoff_roots = [
        name for name in (CORE_HANDOFF_ROOT, COMPACT_HANDOFF_ROOT) if name in document
    ]
    unknown_top_level = sorted(
        set(document)
        - {
            CORE_HANDOFF_ROOT,
            COMPACT_HANDOFF_ROOT,
            *ALLOWED_FIXTURE_METADATA_ROOTS,
        }
    )
    invalid_fixture_metadata = sorted(
        name
        for name in ALLOWED_FIXTURE_METADATA_ROOTS
        if name in document and not isinstance(document[name], dict)
    )
    if parse_failed:
        pass
    elif len(present_handoff_roots) > 1:
        findings.append(
            _finding(
                "HP_PACKET_AMBIGUOUS",
                root_name,
                "document contains more than one handoff packet root",
            )
        )
    elif root_name not in document:
        findings.append(
            _finding(
                "HP_PACKET_ROOT_MISSING",
                root_name,
                f"required root `{root_name}` is missing",
            )
        )
    elif unknown_top_level:
        findings.append(
            _finding(
                "HP_PACKET_AMBIGUOUS",
                root_name,
                "document contains unsupported top-level field(s): "
                + ", ".join(unknown_top_level),
            )
        )
    elif invalid_fixture_metadata:
        findings.append(
            _finding(
                "HP_PACKET_AMBIGUOUS",
                root_name,
                "fixture metadata root(s) must contain mappings: "
                + ", ".join(invalid_fixture_metadata),
            )
        )
    elif not isinstance(document[root_name], dict):
        findings.append(
            _finding(
                "HP_PACKET_TYPE_INVALID",
                root_name,
                "handoff packet root must contain a mapping",
            )
        )
    else:
        packet = document[root_name]

    if packet is not None:
        allowed_fields = set(CORE_REQUIRED_FIELDS) | set(allowed_extra_fields or set())
        for field in sorted(set(packet) - allowed_fields):
            findings.append(
                _finding(
                    "HP_FIELD_UNKNOWN",
                    field,
                    "field is not part of the canonical handoff core",
                )
            )

        for field in CORE_SCALAR_FIELDS:
            if field not in packet:
                findings.append(
                    _finding("HP_FIELD_MISSING", field, "required handoff field is missing")
                )
            elif packet[field] is None:
                findings.append(
                    _finding("HP_FIELD_EMPTY", field, "required string is empty")
                )
            elif not isinstance(packet[field], str):
                findings.append(
                    _finding("HP_FIELD_TYPE_INVALID", field, "field must be a string")
                )
            elif not is_material_handoff_text(packet[field]):
                findings.append(
                    _finding(
                        "HP_FIELD_EMPTY",
                        field,
                        "required string is empty or a generic placeholder",
                    )
                )

        for field in CORE_LIST_FIELDS:
            _validate_material_string_list(packet, field, findings)

        validation = packet.get("validation_status")
        if "validation_status" not in packet:
            findings.append(
                _finding(
                    "HP_FIELD_MISSING",
                    "validation_status",
                    "required handoff field is missing",
                )
            )
        elif not isinstance(validation, dict):
            findings.append(
                _finding(
                    "HP_FIELD_TYPE_INVALID",
                    "validation_status",
                    "validation_status must be a mapping",
                )
            )
        else:
            for field in sorted(set(validation) - set(VALIDATION_STATUS_FIELDS)):
                findings.append(
                    _finding(
                        "HP_FIELD_UNKNOWN",
                        f"validation_status.{field}",
                        "field is not part of canonical validation_status",
                    )
                )

            if "status" not in validation:
                findings.append(
                    _finding(
                        "HP_FIELD_MISSING",
                        "validation_status.status",
                        "required validation status is missing",
                    )
                )
            elif not isinstance(validation["status"], str):
                findings.append(
                    _finding(
                        "HP_FIELD_TYPE_INVALID",
                        "validation_status.status",
                        "status must be a string",
                    )
                )
            elif validation["status"] not in VALIDATION_STATUS_VALUES:
                findings.append(
                    _finding(
                        "HP_VALIDATION_STATUS_INVALID",
                        "validation_status.status",
                        "status must be pass, fail, blocked, or not_run",
                    )
                )

            evidence = validation.get("evidence")
            if "evidence" not in validation or evidence == []:
                findings.append(
                    _finding(
                        "HP_VALIDATION_EVIDENCE_MISSING",
                        "validation_status.evidence",
                        "evidence must be a non-empty list of strings",
                    )
                )
            elif not isinstance(evidence, list):
                findings.append(
                    _finding(
                        "HP_FIELD_TYPE_INVALID",
                        "validation_status.evidence",
                        "evidence must be a list of strings",
                    )
                )
            else:
                for index, item in enumerate(evidence):
                    if not isinstance(item, str):
                        findings.append(
                            _finding(
                                "HP_FIELD_TYPE_INVALID",
                                f"validation_status.evidence[{index}]",
                                "evidence item must be a string",
                            )
                        )
                    elif not is_material_handoff_text(item):
                        findings.append(
                            _finding(
                                "HP_FIELD_EMPTY",
                                f"validation_status.evidence[{index}]",
                                "evidence item is empty or a generic placeholder",
                            )
                        )

            reason = validation.get("reason")
            if "reason" not in validation:
                findings.append(
                    _finding(
                        "HP_FIELD_MISSING",
                        "validation_status.reason",
                        "required validation reason is missing",
                    )
                )
            elif not isinstance(reason, str):
                findings.append(
                    _finding(
                        "HP_FIELD_TYPE_INVALID",
                        "validation_status.reason",
                        "reason must be a string",
                    )
                )
            elif not is_material_handoff_text(reason):
                findings.append(
                    _finding(
                        "HP_FIELD_EMPTY",
                        "validation_status.reason",
                        "reason is empty or a generic placeholder",
                    )
                )

    marker_values = list(_nested_strings(packet)) if packet is not None else []
    if any(has_see_chat(value) for value in marker_values):
        findings.append(
            _finding(
                "HP_CHAT_AUTHORITY_FORBIDDEN",
                root_name,
                "handoff packet contains forbidden chat-only authority phrase: see chat",
            )
        )
    todo_marker = re.compile(
        r"(?<![A-Za-z0-9])(?:AI_TODO|TODO)(?![A-Za-z])",
        flags=re.IGNORECASE | re.ASCII,
    )
    if any(todo_marker.search(value) for value in marker_values):
        findings.append(
            _finding(
                "HP_TODO_UNRESOLVED",
                root_name,
                "handoff packet contains an unresolved TODO or AI_TODO marker",
            )
        )

    mechanically_checked = ["supported YAML-subset parsing"]
    not_checked = [
        "truth or completeness of handoff statements",
        "live state of GitHub issue, PR, branch, or durable links",
        "path authorization or diff containment",
        "whether validation evidence was produced by executed commands",
        "work completion, human approval, merge readiness, or merge authority",
    ]
    if not parse_failed:
        mechanically_checked.append("single expected handoff root")
    else:
        not_checked.append("expected handoff root and packet type")
    if packet is not None:
        mechanically_checked.extend(
            [
                "required core field presence, type, and material content",
                "validation_status enum, evidence list, and material reason",
                "forbidden chat-only authority phrase",
                "unresolved TODO or AI_TODO markers",
            ]
        )
    else:
        not_checked.extend(
            [
                "required core fields and validation_status",
                "chat-only authority and unresolved TODO markers inside a packet",
            ]
        )

    result = "fail" if findings else "pass"
    report: dict[str, object] = {
        "result": result,
        "root": root_name,
        "mechanically_checked": mechanically_checked,
        "not_checked": not_checked,
        "proof_boundary": PROOF_BOUNDARY,
        "findings": findings,
    }
    return result, report, packet


def evaluate_handoff_file(
    handoff_file: str | Path,
    *,
    root_name: str = CORE_HANDOFF_ROOT,
    allowed_extra_fields: set[str] | None = None,
) -> tuple[str, dict[str, object], dict[str, object] | None]:
    path = rel(handoff_file)
    if not path.exists():
        report = {
            "result": "fail",
            "root": root_name,
            "file": normalize_repo_path(str(handoff_file)),
            "mechanically_checked": ["handoff file existence"],
            "not_checked": [
                "handoff packet shape or content",
                "truth, authorization, human approval, or merge state",
            ],
            "proof_boundary": PROOF_BOUNDARY,
            "findings": [
                _finding(
                    "HP_FILE_MISSING",
                    "file",
                    f"handoff file does not exist: {handoff_file}",
                )
            ],
        }
        return "fail", report, None

    if not path.is_file():
        report = {
            "result": "fail",
            "root": root_name,
            "file": normalize_repo_path(str(handoff_file)),
            "mechanically_checked": ["handoff path is a readable file"],
            "not_checked": [
                "handoff packet shape or content",
                "truth, authorization, human approval, or merge state",
            ],
            "proof_boundary": PROOF_BOUNDARY,
            "findings": [
                _finding(
                    "HP_FILE_UNREADABLE",
                    "file",
                    f"handoff path is not a readable file: {handoff_file}",
                )
            ],
        }
        return "fail", report, None
    try:
        source_text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        report = {
            "result": "fail",
            "root": root_name,
            "file": normalize_repo_path(str(handoff_file)),
            "mechanically_checked": ["handoff file readability"],
            "not_checked": [
                "handoff packet shape or content",
                "truth, authorization, human approval, or merge state",
            ],
            "proof_boundary": PROOF_BOUNDARY,
            "findings": [
                _finding(
                    "HP_FILE_UNREADABLE",
                    "file",
                    f"could not read handoff file: {exc}",
                )
            ],
        }
        return "fail", report, None

    result, report, packet = evaluate_handoff_text(
        source_text,
        root_name=root_name,
        allowed_extra_fields=allowed_extra_fields,
    )
    report["file"] = normalize_repo_path(str(handoff_file))
    return result, report, packet
