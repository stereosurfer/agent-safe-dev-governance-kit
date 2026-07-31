from __future__ import annotations

import fnmatch
import re
from pathlib import Path

from asgk_lib.common import (
    ROOT,
    has_see_chat,
    normalize_repo_path,
    strip_html_comments,
)
from asgk_lib.text_fields import (
    material_items,
    parse_visible_task_fields,
)


CANONICAL_TASK_FIELDS = (
    "lane",
    "intelligence_level",
    "reason",
    "durable_source_of_truth",
    "objective",
    "plan",
    "checklist",
    "acceptance_sheet",
    "allowed_paths",
    "expected_output",
    "non_goals",
    "stop_conditions",
    "rollback_expectations",
)

WORK_UNIT_EXECUTION_GATES = (
    "context_read_set",
    "project_specific_validation",
)
ISSUE_PARSE_FIELDS = (
    *CANONICAL_TASK_FIELDS,
    *WORK_UNIT_EXECUTION_GATES,
    "intelligence_level_reason",
)

ISSUE_REFINEMENT_MODE = "issue_refinement"
GITHUB_UNAVAILABLE_FALLBACK_MODE = "github_unavailable_fallback"
TASK_PACKET_MODES = (
    ISSUE_REFINEMENT_MODE,
    GITHUB_UNAVAILABLE_FALLBACK_MODE,
)

TASK_PACKET_REFINEMENT_FIELDS = (
    "mode",
    "durable_source_of_truth",
    "allowed_paths",
    "context_read_set",
    "project_specific_validation",
)

TASK_PACKET_FALLBACK_FIELDS = (
    "mode",
    "github_issue_status",
    *CANONICAL_TASK_FIELDS,
    *WORK_UNIT_EXECUTION_GATES,
)

TASK_PACKET_LIST_FIELDS = {
    "plan",
    "checklist",
    "acceptance_sheet",
    "allowed_paths",
    "non_goals",
    "stop_conditions",
    "context_read_set",
    "project_specific_validation",
}

TASK_PACKET_SCALAR_FIELDS = {
    "mode",
    "github_issue_status",
    "lane",
    "intelligence_level",
    "reason",
    "durable_source_of_truth",
    "objective",
    "expected_output",
    "rollback_expectations",
}

TASK_PACKET_LEGACY_FIELDS = {
    "task_id",
    "intelligence_level_reason",
    "product_context",
    "current_repository_context",
    "files_to_inspect_first",
    "expected_changes",
    "constraints",
    "validation_commands",
    "work_unit_kind",
}

ALLOWED_INTELLIGENCE_LEVELS = {
    "fast_basic",
    "standard",
    "advanced",
    "frontier",
}

CONTEXT_PSEUDO_REFS = {
    "current github issue or pr",
    "current issue or pr",
    "current issue",
    "current pr",
    "current github issue",
    "this github issue",
    "this issue",
}
TASK_PACKET_SELF_REF = "this task packet"

OVERBROAD_CONTEXT_REFS = {
    ".",
    "/",
    "./",
    "all",
    "all files",
    "all repo files",
    "all repository files",
    "all docs",
    "all documents",
    "entire repo",
    "entire repository",
    "everything",
    "every file",
    "every document",
    "full repo",
    "full repository",
    "repo",
    "repository",
    "whole repo",
    "whole repository",
}

NONE_PATH_VALUES = {
    "none",
    "none_for_source_only_release_execution",
}

GLOB_CHARACTERS = "*?[]"

PR_PAYLOAD_MARKERS = {
    "pull_request",
    "merged",
    "mergeable",
    "isDraft",
    "headRefName",
    "baseRefName",
    "mergeStateStatus",
    "reviewDecision",
}

ESCALATION_PATH_PATTERNS = (
    "AGENTS.md",
    "CLAUDE.md",
    ".github/**",
    ".codex/**",
    ".claude/**",
    "docs/control/**",
    "schemas/**",
    "contracts/**",
)


def work_unit_payload_kind(payload: dict[str, object]) -> str:
    explicit = normalized_item(
        payload.get("kind") or payload.get("_asgk_requested_kind")
    ).lower()
    url = normalized_item(payload.get("html_url") or payload.get("url"))
    if (
        explicit == "pr"
        or PR_PAYLOAD_MARKERS.intersection(payload)
        or re.search(r"/pulls?/\d+\b", url, flags=re.IGNORECASE)
    ):
        return "pr"
    if explicit == "issue":
        return "issue"
    return "issue"


def path_matches_allowed(
    path: str,
    allowed_path: str,
    *,
    repo_root: Path = ROOT,
) -> bool:
    path_problem = repo_relative_path_problem(path, repo_root, allow_glob=False)
    allowed_problem = repo_relative_path_problem(
        allowed_path,
        repo_root,
        allow_glob=True,
    )
    if path_problem or allowed_problem:
        return False
    path = normalized_path_item(path)
    allowed = normalized_path_item(allowed_path)
    if not allowed or allowed in NONE_PATH_VALUES:
        return False
    if allowed.endswith("/**"):
        prefix = allowed[:-3].rstrip("/")
        return path == prefix or path.startswith(prefix + "/")
    if allowed.endswith("/"):
        prefix = allowed.rstrip("/")
        return path == prefix or path.startswith(prefix + "/")
    if any(char in allowed for char in "*?[]"):
        return fnmatch.fnmatchcase(path, allowed)
    return path == allowed


def normalized_item(value: object) -> str:
    return (
        str(value)
        .strip()
        .strip('"')
        .strip("'")
        .strip("`")
        .strip()
    )


def normalized_exact_item(value: object) -> str:
    return normalized_item(value)


def normalized_casefold_item(value: object) -> str:
    return re.sub(r"\s+", " ", normalized_item(value)).casefold()


def normalized_path_item(value: object) -> str:
    return normalize_repo_path(normalized_item(value))


def list_items(value: object, *, paths: bool = False) -> list[str]:
    if isinstance(value, list):
        items = [
            normalized_item(item)
            for item in value
            if isinstance(item, str) and normalized_item(item)
        ]
    else:
        items = material_items(value)
    if paths:
        return [normalized_path_item(item) for item in items if normalized_path_item(item)]
    return [normalized_item(item) for item in items if normalized_item(item)]


def parse_issue_fields(
    body: str,
) -> tuple[dict[str, object], list[str]]:
    visible_body = strip_html_comments(body)
    return parse_visible_task_fields(visible_body, ISSUE_PARSE_FIELDS)


def _has_glob(value: str) -> bool:
    return any(character in value for character in GLOB_CHARACTERS)


def _raw_repo_path(value: object) -> str:
    return normalized_item(value).replace("\\", "/")


def _path_anchor(value: str) -> str:
    anchor_parts: list[str] = []
    for part in value.rstrip("/").split("/"):
        if _has_glob(part):
            break
        anchor_parts.append(part)
    return "/".join(anchor_parts)


def repo_relative_path_problem(
    value: object,
    repo_root: Path,
    *,
    allow_glob: bool,
) -> str | None:
    raw = _raw_repo_path(value)
    if not raw:
        return "path is empty"
    if raw in NONE_PATH_VALUES:
        return None
    if any(ord(character) < 32 or ord(character) == 127 for character in raw):
        return "path contains a control character"
    if raw.startswith("/") or re.match(r"^[A-Za-z]:", raw):
        return "path must be repository-relative"
    parts = raw.rstrip("/").split("/")
    if any(part in {".", ".."} for part in parts):
        return "path contains a forbidden dot segment"
    if any(not part for part in parts):
        return "path contains an empty segment"
    if not allow_glob and _has_glob(raw):
        return "path must not contain glob syntax"

    root = repo_root.resolve()
    anchor = _path_anchor(raw) if allow_glob else raw.rstrip("/")
    try:
        candidate = (root / anchor).resolve(strict=False)
        candidate.relative_to(root)
    except (OSError, RuntimeError, ValueError):
        return "path resolves outside the repository root"
    return None


def is_context_pseudo_ref(
    value: object,
    *,
    allow_task_packet_ref: bool = False,
) -> bool:
    text = normalized_item(value)
    lowered = normalized_casefold_item(text)
    if allow_task_packet_ref and lowered == TASK_PACKET_SELF_REF:
        return True
    if lowered in CONTEXT_PSEUDO_REFS:
        return True
    if re.fullmatch(r"#\d+", text):
        return True
    if re.fullmatch(
        r"(?:github\s+)?(?:issue|pr|pull request)\s*#?\s*\d+",
        text,
        flags=re.IGNORECASE,
    ):
        return True
    return bool(re.fullmatch(r"https?://[^\s]+", text, flags=re.IGNORECASE))


def context_read_set_item_problem(
    value: object,
    repo_root: Path = ROOT,
    *,
    allow_task_packet_ref: bool = False,
) -> tuple[str, str] | None:
    ref = normalized_item(value)
    lowered = normalized_casefold_item(ref)
    overbroad_phrase = re.search(
        r"\b(?:all|every|whole|entire|full)\s+(?:the\s+)?"
        r"(?:repo|repository|files?|docs?|documents?)\b",
        lowered,
    )
    if lowered in OVERBROAD_CONTEXT_REFS or overbroad_phrase or _has_glob(ref):
        return ("overbroad", f"context reference is overbroad: {ref}")
    if is_context_pseudo_ref(
        ref,
        allow_task_packet_ref=allow_task_packet_ref,
    ):
        return None
    path_problem = repo_relative_path_problem(ref, repo_root, allow_glob=False)
    if path_problem:
        return ("outside_repo", f"{path_problem}: {ref}")
    candidate = repo_root.resolve() / normalized_path_item(ref)
    try:
        if not candidate.exists():
            return ("invalid", f"context path does not exist: {ref}")
        if candidate.is_dir():
            return ("overbroad", f"context reference names a directory: {ref}")
        if not candidate.is_file():
            return ("invalid", f"context reference is not a regular file: {ref}")
    except OSError:
        return ("outside_repo", f"context reference cannot be safely resolved: {ref}")
    return None


def project_validation_item_problem(value: object) -> str | None:
    normalized = normalized_casefold_item(value)
    match = re.match(
        r"^(?:n\s*/\s*a|na|not[\s_-]*applicable)\b(.*)$",
        normalized,
    )
    if not match:
        return None
    remainder = match.group(1)
    words = [
        word.casefold()
        for word in re.findall(r"[^\W_]+", remainder, flags=re.UNICODE)
        if word.casefold()
        not in {"as", "because", "due", "for", "reason", "since", "to"}
    ]
    if not words:
        return "not_applicable requires a material reason"
    return None


def escalation_boundaries_for_path_scope(value: object) -> list[str]:
    """Return mechanically recognizable escalation boundaries for a path scope."""

    path = normalized_path_item(value)
    if not path:
        return []
    has_glob = _has_glob(path)
    anchor = _path_anchor(path).rstrip("/") if has_glob else path.rstrip("/")
    boundaries: list[str] = []
    for pattern in ESCALATION_PATH_PATTERNS:
        if pattern.endswith("/**"):
            prefix = pattern[:-3].rstrip("/")
            if not has_glob:
                if path == prefix or path.startswith(prefix + "/"):
                    boundaries.append(pattern)
                continue
            if (
                not anchor
                or anchor == prefix
                or anchor.startswith(prefix + "/")
                or prefix.startswith(anchor + "/")
            ):
                boundaries.append(pattern)
            continue
        if (not has_glob and path == pattern) or (
            has_glob and fnmatch.fnmatchcase(pattern, path)
        ):
            boundaries.append(pattern)
    return boundaries


def _finding(code: str, field: str, reason: str) -> dict[str, object]:
    return {
        "code": code,
        "field": field,
        "reason": reason,
        "blocking": True,
    }


def _packet_mode(packet: dict[str, object]) -> str:
    value = packet.get("mode")
    return normalized_item(value) if isinstance(value, str) else ""


def validate_task_packet_shape(
    packet: dict[str, object],
    source_text: str,
    *,
    repo_root: Path = ROOT,
) -> tuple[str, list[dict[str, object]]]:
    findings: list[dict[str, object]] = []
    mode = _packet_mode(packet)

    if "mode" not in packet:
        return "fail", [
            _finding(
                "TP_MODE_MISSING",
                "mode",
                "task packet must declare issue_refinement or github_unavailable_fallback",
            )
        ]
    if not isinstance(packet.get("mode"), str):
        return "fail", [
            _finding("TP_FIELD_TYPE_INVALID", "mode", "mode must be a non-empty scalar")
        ]
    if mode not in TASK_PACKET_MODES:
        return "fail", [
            _finding(
                "TP_MODE_UNSUPPORTED",
                "mode",
                f"unsupported task packet mode: {mode or 'empty'}",
            )
        ]

    for field in sorted(TASK_PACKET_LEGACY_FIELDS.intersection(packet)):
        findings.append(
            _finding(
                "TP_LEGACY_FIELD_FORBIDDEN",
                field,
                f"legacy task packet field is not part of the v2 projection: {field}",
            )
        )

    allowed_fields = (
        set(TASK_PACKET_REFINEMENT_FIELDS)
        if mode == ISSUE_REFINEMENT_MODE
        else set(TASK_PACKET_FALLBACK_FIELDS)
    )
    for field in sorted(set(packet).difference(allowed_fields).difference(TASK_PACKET_LEGACY_FIELDS)):
        findings.append(
            _finding(
                "TP_FIELD_TYPE_INVALID",
                field,
                f"field is not permitted in {mode}: {field}",
            )
        )

    required_fields = (
        TASK_PACKET_REFINEMENT_FIELDS
        if mode == ISSUE_REFINEMENT_MODE
        else TASK_PACKET_FALLBACK_FIELDS
    )
    for field in required_fields:
        if field in {"mode", "github_issue_status"}:
            continue
        if field not in packet:
            findings.append(
                _finding(
                    "TP_REQUIRED_FIELD_MISSING",
                    field,
                    f"{mode} is missing required field: {field}",
                )
            )
            continue
        value = packet[field]
        if field in TASK_PACKET_LIST_FIELDS:
            if not isinstance(value, list):
                findings.append(
                    _finding(
                        "TP_FIELD_TYPE_INVALID",
                        field,
                        f"{field} must be a list",
                    )
                )
            elif not value:
                findings.append(
                    _finding(
                        "TP_LIST_EMPTY",
                        field,
                        f"{field} must contain at least one material item",
                    )
                )
            else:
                for index, item in enumerate(value):
                    item_field = f"{field}[{index}]"
                    if not isinstance(item, str):
                        findings.append(
                            _finding(
                                "TP_LIST_ITEM_TYPE_INVALID",
                                item_field,
                                f"{field} items must be strings",
                            )
                        )
                    elif not normalized_item(item):
                        findings.append(
                            _finding(
                                "TP_LIST_ITEM_EMPTY",
                                item_field,
                                f"{field} items must contain material text",
                            )
                        )
        elif not isinstance(value, str):
            findings.append(
                _finding(
                    "TP_FIELD_TYPE_INVALID",
                    field,
                    f"{field} must be a non-empty scalar",
                )
            )
        elif not normalized_item(value):
            findings.append(
                _finding(
                    "TP_REQUIRED_FIELD_MISSING",
                    field,
                    f"{field} must contain a material value",
                )
            )

    if mode == GITHUB_UNAVAILABLE_FALLBACK_MODE:
        status = packet.get("github_issue_status")
        if not isinstance(status, str) or normalized_item(status) != "pending_unavailable":
            findings.append(
                _finding(
                    "TP_FALLBACK_STATUS_INVALID",
                    "github_issue_status",
                    "github_unavailable_fallback requires exact pending_unavailable status",
                )
            )
        level = packet.get("intelligence_level")
        if (
            isinstance(level, str)
            and normalized_item(level)
            and normalized_item(level) not in ALLOWED_INTELLIGENCE_LEVELS
        ):
            findings.append(
                _finding(
                    "TP_FIELD_TYPE_INVALID",
                    "intelligence_level",
                    "intelligence_level must be fast_basic, standard, advanced, or frontier",
                )
            )

    if has_see_chat(source_text):
        findings.append(
            _finding(
                "TP_CHAT_AUTHORITY_FORBIDDEN",
                "task_packet",
                "task packet contains the forbidden chat-only authority phrase",
            )
        )

    allowed_paths = packet.get("allowed_paths")
    if isinstance(allowed_paths, list):
        for index, item in enumerate(allowed_paths):
            if not isinstance(item, str) or not normalized_item(item):
                continue
            problem = repo_relative_path_problem(item, repo_root, allow_glob=True)
            if problem:
                findings.append(
                    _finding(
                        "TP_ALLOWED_PATH_INVALID",
                        f"allowed_paths[{index}]",
                        f"{problem}: {normalized_item(item)}",
                    )
                )
                continue
            if mode == GITHUB_UNAVAILABLE_FALLBACK_MODE:
                boundaries = escalation_boundaries_for_path_scope(item)
                if boundaries:
                    findings.append(
                        _finding(
                            "TP_FALLBACK_ESCALATION_REQUIRED",
                            f"allowed_paths[{index}]",
                            "fallback local-work authority cannot cover a "
                            "mechanically recognized escalation boundary: "
                            + ", ".join(boundaries),
                        )
                    )

    context_read_set = packet.get("context_read_set")
    if isinstance(context_read_set, list):
        for index, item in enumerate(context_read_set):
            if not isinstance(item, str) or not normalized_item(item):
                continue
            problem = context_read_set_item_problem(
                item,
                repo_root,
                allow_task_packet_ref=True,
            )
            if problem:
                kind, reason = problem
                code = {
                    "overbroad": "TP_READ_SET_OVERBROAD",
                    "outside_repo": "TP_READ_SET_OUTSIDE_REPO",
                    "invalid": "TP_READ_SET_INVALID",
                }[kind]
                findings.append(
                    _finding(code, f"context_read_set[{index}]", reason)
                )

    project_validation = packet.get("project_specific_validation")
    if isinstance(project_validation, list):
        for index, item in enumerate(project_validation):
            if not isinstance(item, str) or not normalized_item(item):
                continue
            problem = project_validation_item_problem(item)
            if problem:
                findings.append(
                    _finding(
                        "TP_PROJECT_VALIDATION_REASON_MISSING",
                        f"project_specific_validation[{index}]",
                        problem,
                    )
                )

    return ("fail" if findings else "pass"), findings


def issue_scope_for_task_packet(
    issue_payload: dict[str, object],
    *,
    repo_root: Path = ROOT,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    findings: list[dict[str, object]] = []
    if work_unit_payload_kind(issue_payload) == "pr":
        findings.append(
            _finding(
                "TP_ISSUE_SCOPE_INVALID",
                "issue.kind",
                "issue_refinement requires a GitHub issue payload, not a pull request",
            )
        )
    state = normalized_item(issue_payload.get("state")).lower()
    if state != "open":
        findings.append(
            _finding(
                "TP_ISSUE_SCOPE_INVALID",
                "issue.state",
                f"issue_refinement requires an open issue; got {state or 'missing'}",
            )
        )

    body = strip_html_comments(str(issue_payload.get("body") or ""))
    if has_see_chat(body):
        findings.append(
            _finding(
                "TP_ISSUE_CHAT_AUTHORITY_FORBIDDEN",
                "issue.body",
                "source issue contains the forbidden chat-only authority phrase",
            )
        )

    fields, ambiguity_reasons = parse_issue_fields(body)
    canonical: dict[str, list[str]] = {}
    gates: dict[str, list[str]] = {}
    raw_issue_allowed_paths: list[str] = []
    for reason in ambiguity_reasons:
        findings.append(
            _finding(
                "TP_ISSUE_TASK_FIELD_AMBIGUOUS",
                "issue.body",
                reason,
            )
        )

    if not ambiguity_reasons:
        if "intelligence_level_reason" in fields:
            findings.append(
                _finding(
                    "TP_ISSUE_REASON_ALIAS_FORBIDDEN",
                    "issue.intelligence_level_reason",
                    "source issue uses legacy intelligence_level_reason; "
                    "reason is the only canonical field name",
                )
            )
        for field in CANONICAL_TASK_FIELDS:
            items = list_items(fields.get(field))
            if field == "allowed_paths":
                raw_issue_allowed_paths = items
                items = [normalized_path_item(item) for item in items]
            canonical[field] = items
            if not items:
                findings.append(
                    _finding(
                        "TP_ISSUE_SCOPE_INVALID",
                        f"issue.{field}",
                        f"issue is missing material canonical field: {field}",
                    )
                )
        for field in WORK_UNIT_EXECUTION_GATES:
            items = list_items(fields.get(field))
            gates[field] = items
            if not items:
                findings.append(
                    _finding(
                        "TP_ISSUE_SCOPE_INVALID",
                        f"issue.{field}",
                        f"issue is missing material execution gate: {field}",
                    )
                )

        for index, path in enumerate(raw_issue_allowed_paths):
            problem = repo_relative_path_problem(path, repo_root, allow_glob=True)
            if problem:
                findings.append(
                    _finding(
                        "TP_ISSUE_ALLOWED_PATH_INVALID",
                        f"issue.allowed_paths[{index}]",
                        f"{problem}: {path}",
                    )
                )

        for index, item in enumerate(gates.get("context_read_set", [])):
            problem = context_read_set_item_problem(item, repo_root)
            if problem:
                kind, reason = problem
                code = {
                    "overbroad": "TP_ISSUE_READ_SET_OVERBROAD",
                    "outside_repo": "TP_ISSUE_READ_SET_OUTSIDE_REPO",
                    "invalid": "TP_ISSUE_READ_SET_INVALID",
                }[kind]
                findings.append(
                    _finding(code, f"issue.context_read_set[{index}]", reason)
                )

        for index, item in enumerate(gates.get("project_specific_validation", [])):
            problem = project_validation_item_problem(item)
            if problem:
                findings.append(
                    _finding(
                        "TP_ISSUE_PROJECT_VALIDATION_REASON_MISSING",
                        f"issue.project_specific_validation[{index}]",
                        problem,
                    )
                )

    return {
        "number": issue_payload.get("number"),
        "state": state,
        "canonical_fields": canonical,
        "execution_gates": gates,
        "allowed_paths": canonical.get("allowed_paths", []),
        "context_read_set": gates.get("context_read_set", []),
        "project_specific_validation": gates.get("project_specific_validation", []),
    }, findings


def _source_references_issue(
    source: object,
    issue_payload: dict[str, object],
) -> bool:
    issue_number = issue_payload.get("number")
    if issue_number is None:
        return False
    expected = str(issue_number)
    text = normalized_item(source)
    local_reference = re.fullmatch(
        r"(?:github\s+)?issue\s*#?\s*(\d+)|#(\d+)",
        text,
        flags=re.IGNORECASE,
    )
    if local_reference:
        return expected in {
            group for group in local_reference.groups() if group is not None
        }

    expected_url = normalized_item(
        issue_payload.get("html_url") or issue_payload.get("url")
    )
    expected_repo_match = re.fullmatch(
        r"https?://github\.com/([^/]+)/([^/]+)/(issues)/(\d+)/?",
        expected_url,
        flags=re.IGNORECASE,
    )
    if not expected_repo_match:
        return False
    source_url = re.fullmatch(
        r"https?://github\.com/([^/]+)/([^/]+)/(issues)/(\d+)/?",
        text,
        flags=re.IGNORECASE,
    )
    if not source_url:
        return False
    return (
        source_url.group(1).casefold() == expected_repo_match.group(1).casefold()
        and source_url.group(2).casefold()
        == expected_repo_match.group(2).casefold()
        and source_url.group(3).casefold()
        == expected_repo_match.group(3).casefold()
        and source_url.group(4) == expected
        and expected_repo_match.group(4) == expected
    )


def _path_is_within_issue(
    path: str,
    issue_allowed_paths: list[str],
    *,
    repo_root: Path,
) -> bool:
    if path in NONE_PATH_VALUES:
        return True
    if _has_glob(path):
        return any(
            normalized_path_item(path) == normalized_path_item(allowed)
            for allowed in issue_allowed_paths
        )
    return any(
        path_matches_allowed(path, allowed, repo_root=repo_root)
        for allowed in issue_allowed_paths
    )


def _find_expanded_items(packet_items: list[str], issue_items: list[str]) -> list[str]:
    issue_normalized = {
        normalized_exact_item(item)
        for item in issue_items
        if normalized_exact_item(item)
    }
    return [
        item
        for item in packet_items
        if normalized_exact_item(item) not in issue_normalized
    ]


def evaluate_task_packet(
    packet: dict[str, object],
    source_text: str,
    issue_payload: dict[str, object] | None = None,
    *,
    repo_root: Path = ROOT,
) -> tuple[str, dict[str, object]]:
    mechanically_checked: list[str] = []
    not_checked: list[str] = []
    mode = _packet_mode(packet)
    shape_result, findings = validate_task_packet_shape(
        packet,
        source_text,
        repo_root=repo_root,
    )
    mechanically_checked.append(
        "packet mode presence, scalar type, and supported token"
    )
    if mode in TASK_PACKET_MODES:
        mechanically_checked.append("mode-specific field presence and shape")
    else:
        not_checked.append("mode-specific field presence and shape")
    if shape_result == "pass":
        mechanically_checked.extend(
            [
                "legacy-field exclusion",
                "context_read_set item syntax and repository containment",
                "project-specific validation bare-not_applicable reason",
            ]
        )
        context_items = list_items(packet.get("context_read_set"))
        if any(
            not is_context_pseudo_ref(
                item,
                allow_task_packet_ref=True,
            )
            for item in context_items
        ):
            mechanically_checked.append(
                "repository-file context_read_set existence"
            )
        if mode == GITHUB_UNAVAILABLE_FALLBACK_MODE:
            mechanically_checked.append(
                "known path-based fallback escalation boundaries"
            )
    elif mode == ISSUE_REFINEMENT_MODE or mode not in TASK_PACKET_MODES:
        not_checked.extend(
            [
                "issue identity, open state, and source authority",
                "allowed_paths non-expansion",
                "context_read_set exact-item non-expansion",
                "project_specific_validation exact-item non-expansion",
            ]
        )
    issue_number = issue_payload.get("number") if isinstance(issue_payload, dict) else None

    if shape_result == "pass" and mode == GITHUB_UNAVAILABLE_FALLBACK_MODE:
        if issue_payload is not None:
            findings.append(
                _finding(
                    "TP_FALLBACK_ISSUE_CONFLICT",
                    "issue",
                    "github_unavailable_fallback must not be compared as an issue refinement",
                )
            )

    issue_scope: dict[str, object] | None = None
    if shape_result == "pass" and mode == ISSUE_REFINEMENT_MODE:
        if issue_payload is None:
            findings.append(
                _finding(
                    "TP_ISSUE_REQUIRED",
                    "issue",
                    "issue_refinement requires --issue, --issue-json-file, or a bundle issue",
                )
            )
        else:
            issue_scope, issue_findings = issue_scope_for_task_packet(
                issue_payload,
                repo_root=repo_root,
            )
            mechanically_checked.append(
                "supplied issue identity, open state, and visible authority shape"
            )
            findings.extend(issue_findings)
            if not issue_findings:
                mechanically_checked.extend(
                    [
                        "allowed_paths non-expansion",
                        "context_read_set case-sensitive exact-item non-expansion",
                        "project_specific_validation case-sensitive exact-item non-expansion",
                    ]
                )
                source = packet.get("durable_source_of_truth")
                if not _source_references_issue(source, issue_payload):
                    findings.append(
                        _finding(
                            "TP_AUTHORITY_MISMATCH",
                            "durable_source_of_truth",
                            "task packet does not reference the supplied issue number",
                        )
                    )

                packet_paths = list_items(packet.get("allowed_paths"), paths=True)
                issue_paths = list(issue_scope.get("allowed_paths") or [])
                for path in packet_paths:
                    if not _path_is_within_issue(
                        path,
                        issue_paths,
                        repo_root=repo_root,
                    ):
                        findings.append(
                            _finding(
                                "TP_ALLOWED_PATH_EXPANSION",
                                "allowed_paths",
                                f"task packet expands issue allowed_paths: {path}",
                            )
                        )

                packet_reads = list_items(packet.get("context_read_set"))
                issue_reads = list(issue_scope.get("context_read_set") or [])
                for item in _find_expanded_items(packet_reads, issue_reads):
                    findings.append(
                        _finding(
                            "TP_READ_SET_EXPANSION",
                            "context_read_set",
                            f"task packet expands issue context_read_set: {item}",
                        )
                    )

                packet_validation = list_items(packet.get("project_specific_validation"))
                issue_validation = list(
                    issue_scope.get("project_specific_validation") or []
                )
                for item in _find_expanded_items(packet_validation, issue_validation):
                    findings.append(
                        _finding(
                            "TP_VALIDATION_EXPANSION",
                            "project_specific_validation",
                            f"task packet expands issue project_specific_validation: {item}",
                        )
                    )
            else:
                not_checked.extend(
                    [
                        "allowed_paths non-expansion",
                        "context_read_set exact-item non-expansion",
                        "project_specific_validation exact-item non-expansion",
                    ]
                )

    if (
        shape_result == "pass"
        and mode == ISSUE_REFINEMENT_MODE
        and issue_payload is None
    ):
        not_checked.extend(
            [
                "supplied issue identity, open state, and source authority",
                "allowed_paths non-expansion",
                "context_read_set exact-item non-expansion",
                "project_specific_validation exact-item non-expansion",
            ]
        )

    result = "fail" if findings else "pass"
    packet_projection = {
        "mode": mode or None,
        "allowed_paths": list_items(packet.get("allowed_paths"), paths=True),
        "context_read_set": list_items(packet.get("context_read_set")),
        "project_specific_validation": list_items(
            packet.get("project_specific_validation")
        ),
        "projection_within_issue_scope": (
            result == "pass" and mode == ISSUE_REFINEMENT_MODE
        ),
        "may_narrow_effective_execution_scope": (
            mode == ISSUE_REFINEMENT_MODE
        ),
        "cannot_modify_issue_authority": mode == ISSUE_REFINEMENT_MODE,
        "github_issue_required_before_pr": (
            mode == GITHUB_UNAVAILABLE_FALLBACK_MODE
        ),
        "temporary_local_execution_authority": (
            "conditional_on_verified_github_unavailability_and_no_escalation_trigger"
            if result == "pass" and mode == GITHUB_UNAVAILABLE_FALLBACK_MODE
            else False
        ),
        "pr_or_merge_authority": False,
    }
    if mode == GITHUB_UNAVAILABLE_FALLBACK_MODE:
        proof_boundary = (
            "Exit 0 proves only that the supplied fallback has the supported "
            "complete shape, exact pending_unavailable token, and no mechanically "
            "recognized path-based escalation boundary. It does not "
            "verify a GitHub outage, activate the conditional local-work "
            "authority, detect every semantic escalation trigger, or grant PR, "
            "merge, external-action, or human-gate authority."
        )
    elif mode == ISSUE_REFINEMENT_MODE:
        proof_boundary = (
            "Exit 0 proves only that the supplied issue-refinement projection "
            "has a supported shape and does not mechanically expand the supplied "
            "issue's paths or case-sensitive exact read/validation items."
        )
    else:
        proof_boundary = (
            "No supported task-packet proof boundary was established."
        )
    return result, {
        "result": result,
        "low_risk_inferred": False,
        "mode": mode or None,
        "issue": issue_number,
        "issue_scope": issue_scope,
        "task_packet": packet_projection,
        "mechanically_checked": list(dict.fromkeys(mechanically_checked)),
        "not_checked": list(dict.fromkeys([
            *not_checked,
            "whether GitHub was actually unavailable",
            "availability, content, or repository identity of durable pseudo-references",
            "semantic necessity of context references",
            "semantic equivalence of read-set or validation items",
            "semantic sufficiency or executability of project-specific validation",
            "non-path escalation triggers such as dependencies, credentials, external services, or policy meaning",
            "implementation correctness",
            "PR readiness, human approval, merge authority, or issue completion",
        ])),
        "proof_boundary": proof_boundary,
        "findings": findings,
    }
