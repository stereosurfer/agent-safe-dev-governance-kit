#!/usr/bin/env python3
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

from asgk_lib.common import (
    ROOT,
    field_block_lines,
    field_block_text,
    field_value,
    has_see_chat,
    markdown_heading_occurrences,
    markdown_headings,
    markdown_section,
    normalize_repo_path,
    normalized_field_value,
    raw_field_value,
    read_changed_paths,
    read_text,
    rel,
    same_repo_path,
    strip_html_comments,
)
from asgk_lib.compact_handoff import (
    branch_ref_matches,
    compact_handoff_check,
    numbered_ref_matches,
    valid_follow_up_issue,
)
from asgk_lib.compact_target_upgrade import compact_target_upgrade_check
from asgk_lib.handoff import evaluate_handoff_file, is_material_handoff_text
from asgk_lib.release_state import check_release_state_docs
from asgk_lib.status_policy import (
    CANONICAL_CURRENT_STATUS_PATH,
    CLOSEOUT_PRE_MERGE_NEXT_ACTION_PATTERNS,
    CURRENT_STATUS_IMPACT_ALLOWED_VALUES,
    CURRENT_STATUS_IMPACT_REQUIRED_FIELDS,
    TRUE_VALUES,
)
from asgk_lib.target_install import (
    print_target_install_findings,
    target_install_findings,
)
from asgk_lib.task_packet import (
    CANONICAL_TASK_FIELDS,
    TASK_PACKET_FALLBACK_FIELDS,
    TASK_PACKET_LEGACY_FIELDS,
    TASK_PACKET_REFINEMENT_FIELDS,
    WORK_UNIT_EXECUTION_GATES,
    context_read_set_item_problem,
    escalation_boundaries_for_path_scope,
    evaluate_task_packet,
    is_context_pseudo_ref,
    list_items,
    path_matches_allowed,
    project_validation_item_problem,
    repo_relative_path_problem,
    validate_task_packet_shape,
    work_unit_payload_kind,
)
from asgk_lib.text_fields import (
    TaskFieldAmbiguityError,
    _visible_markdown_headings,
    material_items,
    parse_simple_task_packet_yaml_checked,
    parse_visible_task_fields,
    task_packet_yaml_source_checked,
)
from asgk_lib.negative import (
    NEGATIVE_CASE_CHOICES,
    run_changed_path_hygiene_checks,
    run_negative_case,
    run_textual_negative_checks,
)
from asgk_lib.workspace_state import (
    live_workspace_state,
    print_workspace_state_result,
    workspace_state_findings,
)

BODY_COHERENCE_MODE = "body-coherence"
MERGE_DECISION_MODE = "merge-decision"
WORK_UNIT_REQUIRED_FIELDS = list(CANONICAL_TASK_FIELDS)
WORK_UNIT_EXECUTION_GATE_FIELDS = list(WORK_UNIT_EXECUTION_GATES)
WORK_UNIT_PARSE_FIELDS = [
    *WORK_UNIT_REQUIRED_FIELDS,
    *WORK_UNIT_EXECUTION_GATE_FIELDS,
    "intelligence_level_reason",
]
TASK_PACKET_SOURCE_FIELDS = {
    *TASK_PACKET_FALLBACK_FIELDS,
    *TASK_PACKET_REFINEMENT_FIELDS,
    *TASK_PACKET_LEGACY_FIELDS,
}
STATUS_REQUIRED_HEADINGS = [
    "Durable source of truth", "Current snapshot", "Active work",
    "Current validation entrypoint", "Closed gates",
    "Runtime artifact status", "Next safe action",
]
STATUS_FORBIDDEN_HISTORY_HEADINGS = [
    "History", "Work Log", "Chronological Log", "Completed Work Log",
    "Last completed",
]
STATUS_FORBIDDEN_PHRASES = [
    "full PR body", "raw CI log", "chat transcript", "see chat",
]
CONTEXT_TOKEN_ESTIMATE_CHARS_PER_TOKEN = 4
CONTEXT_MEASUREMENT_METHOD = (
    "estimated_repo_context_tokens = ceil(characters / 4); repo files only; "
    "excludes issue/PR text, system prompt, chat, tool output, model completion, "
    "and provider billing usage."
)


def strict_contract_scalar_value(text: str, field: str) -> tuple[str, bool]:
    """Parse one lightweight scalar without forgiving malformed quote layers."""

    raw = raw_field_value(text, field)
    if raw is None:
        return "", False
    source = raw.strip()
    if not source:
        return "", False
    if source[0] == '"':
        if len(source) < 2 or source[-1] != '"':
            return "", False
        try:
            value = json.loads(source)
        except json.JSONDecodeError:
            return "", False
        return (value, True) if isinstance(value, str) else ("", False)
    if source[0] == "'":
        if len(source) < 2 or source[-1] != "'":
            return "", False
        inner = source[1:-1]
        if "'" in inner.replace("''", ""):
            return "", False
        return inner.replace("''", "'"), True
    if '"' in source or "'" in source:
        return "", False
    return source, True


def run_command(args: list[str], *, cwd: Path = ROOT) -> int:
    print("+ " + " ".join(args))
    return subprocess.run(args, cwd=cwd).returncode


def run_many(commands: list[list[str]]) -> int:
    failures = 0
    for command in commands:
        if run_command(command) != 0:
            failures += 1
    if failures:
        print(f"FAIL: {failures} command(s) failed.")
        return 1
    return 0


def run_policy_gate(
    pr_body: str | Path,
    *,
    mode: str = MERGE_DECISION_MODE,
    as_json: bool = False,
) -> int:
    command = [
        "python3",
        "scripts/policy_gate_check.py",
        "--pr-body",
        str(pr_body),
        "--mode",
        mode,
    ]
    if as_json:
        command.append("--json")
    return subprocess.run(command, cwd=ROOT).returncode


def run_policy_gate_capture(
    pr_body: str | Path,
    *,
    mode: str = MERGE_DECISION_MODE,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "python3",
            "scripts/policy_gate_check.py",
            "--pr-body",
            str(pr_body),
            "--mode",
            mode,
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def run_hygiene_capture(paths: list[str]) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmpdir:
        paths_file = Path(tmpdir) / "changed_paths.txt"
        paths_file.write_text("\n".join(paths) + ("\n" if paths else ""), encoding="utf-8")
        return subprocess.run(
            ["python3", "scripts/governance_hygiene.py", "--paths-file", str(paths_file)],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )


def load_git_changed_paths(git_base: str, git_head: str) -> list[str]:
    if git_head.upper() in {"WORKTREE", "WT"}:
        diff_result = subprocess.run(
            ["git", "diff", "--name-only", git_base],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if diff_result.returncode != 0:
            raise RuntimeError(diff_result.stdout.strip() or "git diff failed")
        untracked_result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if untracked_result.returncode != 0:
            raise RuntimeError(untracked_result.stdout.strip() or "git ls-files failed")
        paths = {
            normalize_repo_path(line)
            for output in (diff_result.stdout, untracked_result.stdout)
            for line in output.splitlines()
            if normalize_repo_path(line)
        }
        return sorted(paths)

    result = subprocess.run(
        ["git", "diff", "--name-only", git_base, git_head],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout.strip() or "git diff failed")
    return [
        normalize_repo_path(line)
        for line in result.stdout.splitlines()
        if normalize_repo_path(line)
    ]


def read_changed_path_list(path: str | Path) -> list[str]:
    return [
        normalize_repo_path(line)
        for line in read_text(path).splitlines()
        if normalize_repo_path(line) and not normalize_repo_path(line).startswith("#")
    ]


def git_remote_repo_slug() -> str:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout.strip() or "git remote get-url origin failed")
    remote = result.stdout.strip()
    match = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$", remote)
    if not match:
        raise RuntimeError(f"cannot infer GitHub repo from origin remote: {remote}")
    return f"{match.group('owner')}/{match.group('repo')}"


def load_live_work_unit(kind: str, number: str) -> dict[str, object]:
    repo = git_remote_repo_slug()
    endpoint = (
        f"repos/{repo}/issues/{number}"
        if kind == "issue"
        else f"repos/{repo}/pulls/{number}"
    )
    result = subprocess.run(
        ["gh", "api", endpoint],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout.strip() or f"gh api {endpoint} failed")
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise RuntimeError("GitHub work-unit payload must be a JSON object")
    payload["_asgk_requested_kind"] = kind
    return payload


def load_work_unit_payload(args: argparse.Namespace) -> dict[str, object]:
    sources = [bool(args.issue), bool(args.pr), bool(args.json_file)]
    if sum(sources) != 1:
        raise ValueError("provide exactly one of --issue, --pr, or --json-file")
    if args.json_file:
        payload = json.loads(read_text(args.json_file))
        if not isinstance(payload, dict):
            raise ValueError("work-unit JSON fixture must be an object")
        return payload
    if args.issue:
        return load_live_work_unit("issue", str(args.issue).lstrip("#"))
    return load_live_work_unit("pr", str(args.pr).lstrip("#"))


def work_unit_kind(payload: dict[str, object]) -> str:
    return work_unit_payload_kind(payload)


def parse_work_unit_task_fields_checked(
    body: str,
) -> tuple[dict[str, object], list[str]]:
    visible_body = strip_html_comments(body)
    return parse_visible_task_fields(visible_body, WORK_UNIT_PARSE_FIELDS)


def parse_work_unit_task_fields(body: str) -> dict[str, object]:
    fields, ambiguity_reasons = parse_work_unit_task_fields_checked(body)
    return {} if ambiguity_reasons else fields


def work_unit_field_value(fields: dict[str, object], field: str) -> object | None:
    return fields.get(field)


def work_unit_execution_gate_failures(fields: dict[str, object]) -> list[str]:
    failures: list[str] = []
    for field in WORK_UNIT_EXECUTION_GATE_FIELDS:
        if not material_items(fields.get(field)):
            failures.append(field)
    return failures


def extract_allowed_paths(body: str) -> list[str]:
    fields = parse_work_unit_task_fields(body)
    return [
        normalize_repo_path(item)
        for item in material_items(fields.get("allowed_paths"))
    ]


def canonical_issue_scope_from_payload(payload: dict[str, object]) -> tuple[str, dict[str, object]]:
    kind = work_unit_kind(payload)
    number = payload.get("number")
    state = str(payload.get("state") or "").lower()
    title = str(payload.get("title") or "")
    fields, ambiguity_reasons = parse_work_unit_task_fields_checked(
        str(payload.get("body") or "")
    )
    findings: list[dict[str, str]] = []
    canonical_fields: dict[str, list[str]] = {}

    if kind != "issue":
        findings.append({
            "field": "kind",
            "reason": f"canonical issue scope requires an issue payload, got {kind}",
        })

    for reason in ambiguity_reasons:
        findings.append({
            "code": "WU_TASK_FIELD_AMBIGUOUS",
            "field": "body",
            "reason": reason,
        })

    for field in WORK_UNIT_REQUIRED_FIELDS:
        value = work_unit_field_value(fields, field)
        items = material_items(value)
        if field == "allowed_paths":
            items = [normalize_repo_path(item) for item in items]
        if not items and not ambiguity_reasons:
            findings.append({
                "field": field,
                "reason": "missing material issue scope field",
            })
        canonical_fields[field] = items

    canonical_issue_scope = {
        "version": "asgk.compact_issue_scope.v1",
        "source": {
            "kind": kind,
            "number": number,
            "state": state,
            "title": title,
        },
        "required_fields": WORK_UNIT_REQUIRED_FIELDS,
        "fields": canonical_fields,
        "allowed_paths": canonical_fields.get("allowed_paths", []),
        "scope_rules": {
            "task_packet_may_narrow": True,
            "task_packet_must_not_expand": True,
            "low_risk_inferred": False,
        },
    }

    result = "fail" if findings else "pass"
    return result, {
        "result": result,
        "issue": number,
        "canonical_issue_scope": canonical_issue_scope,
        "low_risk_inferred": False,
        "findings": findings,
    }


def compact_scope_lock_from_payload(payload: dict[str, object]) -> tuple[str, dict[str, object]]:
    scope_result, scope_output = canonical_issue_scope_from_payload(payload)
    number = scope_output.get("issue")
    findings: list[dict[str, str]] = list(scope_output.get("findings", []))
    canonical_issue_scope = scope_output.get("canonical_issue_scope")

    if scope_result != "pass" or not isinstance(canonical_issue_scope, dict):
        return "fail", {
            "result": "fail",
            "issue": number,
            "low_risk_inferred": False,
            "findings": findings,
        }

    encoded = json.dumps(canonical_issue_scope, sort_keys=True, separators=(",", ":")).encode("utf-8")
    scope_hash = hashlib.sha256(encoded).hexdigest()
    scope_lock = {
        "version": "asgk.compact_scope_lock.v1",
        "issue": number,
        "scope_hash": scope_hash,
        "canonical_issue_scope_version": canonical_issue_scope.get("version"),
        "allowed_paths": canonical_issue_scope.get("allowed_paths", []),
        "low_risk_inferred": False,
    }
    return "pass", {
        "result": "pass",
        "issue": number,
        "scope_hash": scope_hash,
        "allowed_paths": canonical_issue_scope.get("allowed_paths", []),
        "scope_lock": scope_lock,
        "canonical_issue_scope": canonical_issue_scope,
        "low_risk_inferred": False,
        "findings": [],
    }


def extract_scope_hash(payload: dict[str, object]) -> str:
    scope_lock = payload.get("scope_lock")
    if isinstance(scope_lock, dict):
        return str(scope_lock.get("scope_hash") or "")
    return str(payload.get("scope_hash") or "")


def compare_scope_lock(current: dict[str, object], captured: dict[str, object]) -> list[dict[str, str]]:
    current_hash = extract_scope_hash(current)
    captured_hash = extract_scope_hash(captured)
    findings: list[dict[str, str]] = []
    if not captured_hash:
        findings.append({
            "field": "compare_file",
            "reason": "captured scope lock is missing scope_hash",
        })
    if not current_hash:
        findings.append({
            "field": "scope_hash",
            "reason": "current scope lock is missing scope_hash",
        })
    if current_hash and captured_hash and current_hash != captured_hash:
        findings.append({
            "field": "scope_hash",
            "reason": "captured scope lock does not match current issue scope",
        })
    return findings


def compact_pr_report_restricted_boundaries(paths: list[str]) -> list[str]:
    boundaries: list[str] = []
    for path in paths:
        normalized = normalize_repo_path(path)
        boundaries.extend(escalation_boundaries_for_path_scope(normalized))
    return sorted(set(boundaries))


def nonblank_string(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def status_check_name(item: dict[str, object]) -> str | None:
    if "name" in item:
        return nonblank_string(item.get("name"))
    return nonblank_string(item.get("context"))


def status_check_provider(item: dict[str, object]) -> str | None:
    return nonblank_string(item.get("workflowName"))


def status_check_identity(item: dict[str, object]) -> str | None:
    name = status_check_name(item)
    if name is None:
        return None
    workflow = status_check_provider(item)
    return f"{workflow}::{name}" if workflow else name


def parse_status_check_timestamp(value: object) -> tuple[float, str] | None:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip()
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        timestamp = parsed.replace(tzinfo=timezone.utc).timestamp()
    else:
        timestamp = parsed.timestamp()
    return timestamp, normalized


def status_check_ordering(
    item: dict[str, object],
) -> tuple[float | None, str | None, str | None]:
    selected_field = nonblank_string(item.get("_asgk_ordering_field"))
    if selected_field:
        parsed = parse_status_check_timestamp(item.get(selected_field))
        if parsed is not None:
            timestamp, value = parsed
            return timestamp, selected_field, value
    for field in ("startedAt", "createdAt", "completedAt", "updatedAt"):
        parsed = parse_status_check_timestamp(item.get(field))
        if parsed is not None:
            timestamp, value = parsed
            return timestamp, field, value
    return None, None, None


def common_status_check_ordering(
    items: list[dict[str, object]],
) -> tuple[str, list[tuple[float, str, dict[str, object]]]] | None:
    for field in ("startedAt", "createdAt"):
        ordered: list[tuple[float, str, dict[str, object]]] = []
        for item in items:
            parsed = parse_status_check_timestamp(item.get(field))
            if parsed is None:
                ordered = []
                break
            timestamp, value = parsed
            ordered.append((timestamp, value, item))
        if ordered:
            return field, ordered
    return None


def select_latest_status_checks(
    status_rollup: object,
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, str]],
]:
    if not isinstance(status_rollup, list):
        return [], [], [{
            "field": "statusCheckRollup",
            "reason": "statusCheckRollup is not a list",
        }]

    records: list[tuple[dict[str, object], str, str, bool]] = []
    current: list[dict[str, object]] = []
    superseded: list[dict[str, object]] = []
    errors: list[dict[str, str]] = []
    for index, item in enumerate(status_rollup):
        if not isinstance(item, dict):
            errors.append({
                "field": "statusCheckRollup.shape",
                "reason": f"status check entry {index} is not an object",
            })
            continue
        if "name" in item and nonblank_string(item.get("name")) is None:
            errors.append({
                "field": "statusCheckRollup.identity",
                "reason": (
                    f"status check entry {index} has a non-string or blank "
                    "`name` identity"
                ),
            })
            current.append(item)
            continue
        if (
            "workflowName" in item
            and item.get("workflowName") is not None
            and not isinstance(item.get("workflowName"), str)
        ):
            errors.append({
                "field": "statusCheckRollup.identity",
                "reason": (
                    f"status check entry {index} has a non-string "
                    "`workflowName` provider identity"
                ),
            })
            current.append(item)
            continue
        identity = status_check_identity(item)
        if identity is None:
            errors.append({
                "field": "statusCheckRollup.identity",
                "reason": (
                    f"status check entry {index} has no usable name or context "
                    "identity"
                ),
            })
            current.append(item)
            continue
        name = status_check_name(item)
        assert name is not None
        checkrun_like = "name" in item or item.get("__typename") == "CheckRun"
        records.append((item, identity, name, checkrun_like))

    ambiguous_checkruns: set[int] = set()
    checkruns_by_name: dict[str, list[dict[str, object]]] = {}
    for item, _identity, name, checkrun_like in records:
        if checkrun_like:
            checkruns_by_name.setdefault(name, []).append(item)
    for name, items in sorted(checkruns_by_name.items()):
        if len(items) <= 1 or all(status_check_provider(item) for item in items):
            continue
        errors.append({
            "field": "statusCheckRollup.identity",
            "reason": (
                f"repeated CheckRun `{name}` has no workflow/provider identity "
                "and cannot be safely treated as one rerun series"
            ),
        })
        ambiguous_checkruns.update(id(item) for item in items)
        current.extend(items)

    groups: dict[str, list[dict[str, object]]] = {}
    for item, identity, _name, _checkrun_like in records:
        if id(item) not in ambiguous_checkruns:
            groups.setdefault(identity, []).append(item)

    for identity, items in sorted(groups.items()):
        if len(items) == 1:
            current.append(items[0])
            continue

        common_ordering = common_status_check_ordering(items)
        if common_ordering is None:
            errors.append({
                "field": "statusCheckRollup.ordering",
                "reason": (
                    f"repeated status check `{identity}` cannot be ordered "
                    "on one common valid `startedAt` or `createdAt` field"
                ),
            })
            current.extend(items)
            continue

        ordering_field, timestamped = common_ordering
        latest_timestamp = max(timestamp for timestamp, _value, _item in timestamped)
        latest = [
            item
            for timestamp, _value, item in timestamped
            if timestamp == latest_timestamp
        ]
        if len(latest) != 1:
            errors.append({
                "field": "statusCheckRollup.ordering",
                "reason": (
                    f"repeated status check `{identity}` has an ambiguous "
                    "latest timestamp"
                ),
            })
            current.extend(items)
            continue

        for timestamp, value, item in timestamped:
            annotated = dict(item)
            annotated["_asgk_ordering_field"] = ordering_field
            annotated["_asgk_ordering_timestamp"] = value
            if item is latest[0]:
                current.append(annotated)
            else:
                superseded.append(annotated)

    return current, superseded, errors


def compact_pr_report_status_checks(status_rollup: object) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    current, superseded, errors = select_latest_status_checks(status_rollup)
    for items, is_current in ((current, True), (superseded, False)):
        for item in items:
            _timestamp, ordering_field, ordering_value = status_check_ordering(item)
            checks.append({
                "identity": status_check_identity(item) or "missing_check_identity",
                "name": str(item.get("name") or item.get("context") or "unnamed_check"),
                "status": str(item.get("status") or ""),
                "conclusion": str(item.get("conclusion") or item.get("state") or ""),
                "details_url": str(item.get("detailsUrl") or item.get("targetUrl") or ""),
                "ordering_field": ordering_field or "",
                "ordering_timestamp": ordering_value or "",
                "current": is_current,
                "superseded": not is_current,
            })
    for error in errors:
        checks.append({
            "identity": error["field"],
            "name": "statusCheckRollup",
            "status": "AMBIGUOUS",
            "conclusion": "",
            "details_url": "",
            "current": True,
            "superseded": False,
            "error": error["reason"],
        })
    return checks


def compact_pr_report_agent_claims(payload: dict[str, object], body: str) -> dict[str, object]:
    merge_section = markdown_section(body, "Merge Decision")
    pr_body_claims = {
        "merge_decision_result": normalized_field_value(merge_section, "result"),
        "checks_passed": normalized_field_value(merge_section, "checks_passed"),
        "human_gates_checked": normalized_field_value(merge_section, "human_gates_checked"),
        "validation_evidence_checked": normalized_field_value(merge_section, "validation_evidence_checked"),
    }
    merge_ready_claimed = pr_body_claims["merge_decision_result"] == "merge_allowed"
    human_gate_claimed = pr_body_claims["human_gates_checked"] in TRUE_VALUES
    sources = ["pr_body.merge_decision.result"] if merge_ready_claimed else []
    if human_gate_claimed:
        sources.append("pr_body.human_gates_checked")

    fixture_claims: dict[str, object] = {}
    raw_fixture_claims = payload.get("agent_claims")
    if isinstance(raw_fixture_claims, dict):
        fixture_claims = dict(raw_fixture_claims)
        fixture_merge_result = str(fixture_claims.get("merge_result") or "").lower()
        if fixture_merge_result == "merge_allowed":
            merge_ready_claimed = True
            sources.append("agent_claims.merge_result")
        if fixture_claims.get("auto_merge_eligible") is True:
            merge_ready_claimed = True
            sources.append("agent_claims.auto_merge_eligible")
        if fixture_claims.get("human_gates_checked") is True:
            human_gate_claimed = True
            sources.append("agent_claims.human_gates_checked")

    return {
        "merge_ready_claimed": merge_ready_claimed,
        "human_gate_claimed": human_gate_claimed,
        "claim_sources": sorted(set(sources)),
        "pr_body": pr_body_claims,
        "fixture": fixture_claims,
    }


def compact_pr_report_claim_conflict_findings(
    agent_claims: dict[str, object],
    tool_findings: list[dict[str, str]],
    human_gate_findings: list[dict[str, str]],
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if (tool_findings or human_gate_findings) and agent_claims.get("merge_ready_claimed") is True:
        findings.append({
            "field": "agent_claims",
            "reason": "agent-authored merge-ready claim conflicts with tool-derived blocking state",
        })
    if human_gate_findings and agent_claims.get("human_gate_claimed") is True:
        findings.append({
            "field": "agent_claims",
            "reason": "agent-authored human-gate claim conflicts with tool-derived restricted-boundary state",
        })
    return findings


def compact_pr_report_from_payload(payload: dict[str, object]) -> tuple[str, dict[str, object]]:
    if payload.get("metadata_available") is False:
        return "fail_closed", {
            "result": "fail_closed",
            "low_risk_inferred": False,
            "findings": [{
                "field": "metadata_available",
                "reason": "GitHub PR metadata is unavailable",
            }],
        }

    pr_number = payload.get("number")
    body = str(payload.get("body") or "")
    declared_kind = str(
        payload.get("kind") or payload.get("_asgk_requested_kind") or ""
    ).strip().lower()
    agent_claims = compact_pr_report_agent_claims(payload, body)
    changed_paths = pr_file_paths(payload.get("files"))
    issue_number = merge_decision_issue_number(body)
    issue_payload = pr_status_issue_payload(payload, issue_number) if issue_number is not None else None

    issue_scope_output: dict[str, object] | None = None
    scope_lock_output: dict[str, object] | None = None
    findings: list[dict[str, str]] = []

    if issue_number is None:
        findings.append({
            "field": "issue",
            "reason": "Merge Decision issue is missing",
        })
    elif issue_payload is None:
        findings.append({
            "field": "issue",
            "reason": f"closing issue #{issue_number} metadata is unavailable",
        })
    else:
        scope_result, issue_scope_output = canonical_issue_scope_from_payload(issue_payload)
        if scope_result != "pass":
            for finding in issue_scope_output.get("findings", []):
                if isinstance(finding, dict):
                    findings.append({
                        "field": str(finding.get("field") or "issue_scope"),
                        "reason": str(finding.get("reason") or "canonical issue scope failed"),
                    })
        lock_result, scope_lock_output = compact_scope_lock_from_payload(issue_payload)
        if lock_result != "pass":
            for finding in scope_lock_output.get("findings", []):
                if isinstance(finding, dict):
                    findings.append({
                        "field": str(finding.get("field") or "scope_lock"),
                        "reason": str(finding.get("reason") or "scope lock failed"),
                    })

    pr_status_result, pr_status_findings = check_pr_status_payload(payload)
    for finding in pr_status_findings:
        findings.append({
            "field": str(finding.get("field") or "pr_status"),
            "reason": str(finding.get("reason") or "PR status check failed"),
        })

    restricted_boundaries = compact_pr_report_restricted_boundaries(changed_paths)
    human_gate_findings = [
        {
            "field": "restricted_boundaries",
            "reason": "restricted boundary requires human review: " + ", ".join(restricted_boundaries),
        }
    ] if restricted_boundaries else []
    findings.extend(compact_pr_report_claim_conflict_findings(
        agent_claims,
        findings,
        human_gate_findings,
    ))

    derived_state = "fail" if findings else ("requires_human" if restricted_boundaries else "checkable_pass")
    result = "fail" if findings else ("requires_human" if restricted_boundaries else "pass")
    return result, {
        "result": result,
        "derived_state": derived_state,
        "low_risk_inferred": False,
        "agent_claims": agent_claims,
        "pr": {
            "number": pr_number,
            "url": payload.get("url"),
            "state": payload.get("state"),
            "is_draft": payload.get("isDraft"),
            "merge_state": payload.get("mergeStateStatus"),
            "review_decision": payload.get("reviewDecision"),
            "changed_paths": changed_paths,
            "status_checks": compact_pr_report_status_checks(payload.get("statusCheckRollup")),
            "closing_issue": issue_number,
        },
        "issue_scope": issue_scope_output.get("canonical_issue_scope") if issue_scope_output else None,
        "scope_lock": scope_lock_output.get("scope_lock") if scope_lock_output else None,
        "restricted_boundaries": restricted_boundaries,
        "human_gate_findings": human_gate_findings,
        "pr_status_result": pr_status_result,
        "findings": findings,
    }


def check_work_unit_payload(
    payload: dict[str, object],
    changed_paths: list[str],
    *,
    authority_only: bool = False,
) -> tuple[str, list[dict[str, object]], list[str]]:
    findings: list[dict[str, object]] = []
    kind = work_unit_kind(payload)
    declared_kind = str(
        payload.get("_asgk_requested_kind") or payload.get("kind") or ""
    ).strip().lower()
    number = payload.get("number")
    state = str(payload.get("state") or "").lower()
    body = str(payload.get("body") or "")

    def add(code: str, field: str, reason: str, fix: str) -> None:
        findings.append({
            "code": code,
            "severity": "FAIL",
            "field": field,
            "reason": reason,
            "recommended_fix": fix,
            "blocking": True,
        })

    if kind == "issue":
        if "pull_request" in payload:
            add(
                "WU_KIND_INVALID",
                "kind",
                f"Work unit #{number or 'unknown'} is a pull request, not an issue.",
                "Use --pr for PR follow-up work or select an open issue with allowed_paths.",
            )
        if state != "open":
            add(
                "WU_STATE_NOT_OPEN",
                "state",
                f"Issue state is not open: {state or 'missing'}.",
                "Select an open issue or create a new durable issue before changing files.",
            )
    elif kind == "pr":
        if declared_kind == "issue":
            add(
                "WU_KIND_INVALID",
                "kind",
                "Work unit was requested or declared as an issue but has "
                "pull-request markers.",
                "Use --pr for PR follow-up work or select an actual open issue.",
            )
        merged = payload.get("merged")
        if state not in {"open"} or merged is True:
            add(
                "WU_STATE_NOT_OPEN",
                "state",
                f"PR state is not open or is already merged: state={state or 'missing'}, merged={merged}.",
                "Use only an open PR that still needs follow-up fixes, or create a new issue.",
            )
    else:
        add(
            "WU_KIND_INVALID",
            "kind",
            f"Unknown work-unit kind: {kind}",
            "Provide an issue or PR payload.",
        )

    visible_body = strip_html_comments(body)
    if has_see_chat(visible_body):
        add(
            "WU_CHAT_AUTHORITY_FORBIDDEN",
            "body",
            "Work-unit body contains chat-only authority phrase: see chat.",
            "Move scope, acceptance, and handoff authority into the issue, PR, or repo docs.",
        )

    task_fields, task_field_ambiguity = parse_work_unit_task_fields_checked(
        visible_body
    )
    for reason in task_field_ambiguity:
        add(
            "WU_TASK_FIELD_AMBIGUOUS",
            "body",
            reason,
            "Use exactly one visible task-field representation with unique fields.",
        )

    if not task_field_ambiguity:
        if "intelligence_level_reason" in task_fields:
            add(
                "WU_REASON_ALIAS_FORBIDDEN",
                "intelligence_level_reason",
                "Legacy intelligence_level_reason cannot substitute for canonical reason.",
                "Rename the field to reason in the durable issue or PR.",
            )

        for field in WORK_UNIT_REQUIRED_FIELDS:
            if material_items(work_unit_field_value(task_fields, field)):
                continue
            add(
                "WU_REQUIRED_FIELD_MISSING",
                field,
                f"Work-unit body is missing material canonical task field: {field}.",
                "Add the missing field to the durable GitHub issue or PR before continuing.",
            )

        for field in work_unit_execution_gate_failures(task_fields):
            add(
                "WU_EXECUTION_GATE_MISSING",
                field,
                f"Work-unit body is missing material execution gate: {field}.",
                "Add the bounded read set or project-specific validation gate before continuing.",
            )

        for index, item in enumerate(material_items(task_fields.get("allowed_paths"))):
            problem = repo_relative_path_problem(item, ROOT, allow_glob=True)
            if problem:
                add(
                    "WU_ALLOWED_PATH_INVALID",
                    f"allowed_paths[{index}]",
                    f"{problem}: {item}",
                    "Use a safe repository-relative path or an explicitly bounded glob.",
                )

        for index, item in enumerate(material_items(task_fields.get("context_read_set"))):
            problem = context_read_set_item_problem(item, ROOT)
            if not problem:
                continue
            kind, reason = problem
            add(
                {
                    "overbroad": "WU_READ_SET_OVERBROAD",
                    "outside_repo": "WU_READ_SET_OUTSIDE_REPO",
                    "invalid": "WU_READ_SET_INVALID",
                }[kind],
                f"context_read_set[{index}]",
                reason,
                "Name the smallest safe repository-relative paths or durable references.",
            )

        for index, item in enumerate(
            material_items(task_fields.get("project_specific_validation"))
        ):
            problem = project_validation_item_problem(item)
            if problem:
                add(
                    "WU_PROJECT_VALIDATION_REASON_MISSING",
                    f"project_specific_validation[{index}]",
                    problem,
                    "Add a concrete reason after not_applicable or name the required check.",
                )

    allowed_paths = (
        [
            normalize_repo_path(item)
            for item in material_items(task_fields.get("allowed_paths"))
        ]
        if not task_field_ambiguity
        else []
    )
    normalized_changed_paths = [normalize_repo_path(path) for path in changed_paths if normalize_repo_path(path)]
    if not authority_only and not normalized_changed_paths:
        add(
            "WU_CHANGED_PATHS_MISSING",
            "changed_paths",
            "No changed paths were provided or detected.",
            "Run this check with --paths-file or --git-base/--git-head after creating a bounded diff.",
        )

    if not authority_only:
        unauthorized = [
            path for path in normalized_changed_paths
            if allowed_paths and not any(path_matches_allowed(path, allowed) for allowed in allowed_paths)
        ]
        for path in unauthorized:
            add(
                "WU_PATH_OUTSIDE_SCOPE",
                "changed_paths",
                f"Changed path is outside allowed_paths: {path}",
                "Remove the change, update the durable issue before writing, or create a separate issue.",
            )

        hygiene = run_hygiene_capture(normalized_changed_paths)
        if hygiene.returncode != 0:
            add(
                "WU_PATH_HYGIENE_FAILED",
                "changed_paths",
                "Changed-path hygiene failed for the supplied paths.",
                "Remove protected/runtime/private-source-like paths or keep the work human-gated.",
            )

    return ("fail" if findings else "pass"), findings, allowed_paths


def print_work_unit_result(
    payload: dict[str, object],
    result: str,
    findings: list[dict[str, object]],
    allowed_paths: list[str],
    changed_paths: list[str],
    *,
    authority_only: bool,
    as_json: bool,
) -> int:
    task_fields_ambiguous = any(
        finding.get("code") == "WU_TASK_FIELD_AMBIGUOUS"
        for finding in findings
    )
    mechanically_checked = [
        "work-unit kind and open state",
        "single visible task-field representation and field uniqueness",
        "chat-only authority exclusion",
    ]
    if not task_fields_ambiguous:
        mechanically_checked.extend([
            "visible canonical 13-field task identity",
            "context_read_set exact-reference syntax, existence, and repository containment",
            "project_specific_validation bare-not_applicable reason",
        ])
    not_checked = [
        "availability, content, or repository identity of durable pseudo-references",
        "semantic necessity of context references",
        "semantic sufficiency or executability of project_specific_validation",
        "implementation correctness",
        "human approval or protected-path authorization",
        "PR readiness, merge authority, or issue completion",
    ]
    if task_fields_ambiguous:
        not_checked.extend([
            "canonical task-field completeness and execution-gate semantics",
            "allowed_paths containment",
        ])
    if authority_only:
        not_checked.insert(0, "changed paths, diff contents, and path hygiene")
        proof_boundary = (
            "Exit 0 in authority-only mode proves only that the supplied open "
            "work-unit authority has the visible 13 fields, mechanically valid "
            "execution-gate shape, and no checked chat-only authority. It checks no diff, "
            "implementation, protected-path approval, human gate, or merge state."
        )
    else:
        mechanically_checked.append("supplied changed-path presence")
        if not task_fields_ambiguous:
            mechanically_checked.append("allowed_paths containment")
        mechanically_checked.append("changed-path hygiene patterns")
        proof_boundary = (
            "Exit 0 in post-diff mode proves only that the supplied open "
            "work-unit authority and execution gates are structurally valid and "
            "the supplied changed paths pass mechanical containment and hygiene. "
            "It does not prove implementation correctness, human approval, or "
            "merge authority."
        )
    output = {
        "result": result,
        "low_risk_inferred": False,
        "work_unit": {
            "kind": work_unit_kind(payload),
            "number": payload.get("number"),
            "state": payload.get("state"),
            "url": payload.get("html_url") or payload.get("url"),
        },
        "authority_only": authority_only,
        "changed_paths_checked": not authority_only,
        "canonical_task_fields": WORK_UNIT_REQUIRED_FIELDS,
        "execution_gates": WORK_UNIT_EXECUTION_GATE_FIELDS,
        "allowed_paths": allowed_paths,
        "changed_paths": changed_paths,
        "mechanically_checked": mechanically_checked,
        "not_checked": not_checked,
        "proof_boundary": proof_boundary,
        "findings": findings,
    }
    if as_json:
        print(json.dumps(output, indent=2, sort_keys=True))
    elif findings:
        for finding in findings:
            print(
                f"{finding['severity']}: {finding['field']} - "
                f"{finding['reason']} Fix: {finding['recommended_fix']}"
            )
        print("Work-unit check result: fail. No low-risk status was inferred.")
    else:
        mode = "authority-only" if authority_only else "post-diff"
        print(f"Work-unit {mode} check passed. No low-risk status was inferred.")
        print(proof_boundary)
    return 1 if findings else 0


def load_task_packet_payload(path: str | Path) -> tuple[dict[str, object], str]:
    text = read_text(path)
    if path_str := str(path):
        if path_str.endswith(".json"):
            payload = json.loads(text)
            if not isinstance(payload, dict):
                raise ValueError("task packet JSON must be an object")
            wrappers = [
                field
                for field in ("bad_input", "task_packet")
                if field in payload
            ]
            if len(wrappers) > 1:
                raise TaskFieldAmbiguityError([
                    "multiple JSON task-packet wrapper fields: "
                    + ", ".join(wrappers)
                ])
            if wrappers:
                wrapper = wrappers[0]
                unexpected = set(payload).difference(
                    {wrapper, "negative_case"}
                )
                if unexpected:
                    raise TaskFieldAmbiguityError([
                        "JSON task-packet wrapper cannot accompany other "
                        "top-level fields: "
                        + ", ".join(sorted(unexpected))
                    ])
                candidate = payload.get(wrapper)
            else:
                candidate = payload
            if not isinstance(candidate, dict):
                raise ValueError("bad_input or task_packet must be an object")
            return candidate, text
    visible_text = strip_html_comments(text)
    source, source_selection_reasons = task_packet_yaml_source_checked(
        visible_text,
        TASK_PACKET_SOURCE_FIELDS,
    )
    packet, source_reasons = parse_simple_task_packet_yaml_checked(source)
    ambiguity_reasons = list(dict.fromkeys([
        *source_selection_reasons,
        *source_reasons,
    ]))
    if ambiguity_reasons:
        raise TaskFieldAmbiguityError(ambiguity_reasons)
    return packet, visible_text


def task_packet_context_read_set(packet: dict[str, object]) -> list[str]:
    return list_items(packet.get("context_read_set"))


def estimate_tokens_from_characters(characters: int) -> int:
    if characters <= 0:
        return 0
    return (characters + CONTEXT_TOKEN_ESTIMATE_CHARS_PER_TOKEN - 1) // CONTEXT_TOKEN_ESTIMATE_CHARS_PER_TOKEN


def context_budget_measurement(packet: dict[str, object]) -> dict[str, object]:
    files: list[dict[str, object]] = []
    missing_refs: list[str] = []
    pseudo_refs: list[str] = []
    overbroad_refs: list[str] = []
    read_errors: list[dict[str, str]] = []
    total_bytes = 0
    total_characters = 0

    for ref in task_packet_context_read_set(packet):
        if is_context_pseudo_ref(ref, allow_task_packet_ref=True):
            pseudo_refs.append(ref)
            continue
        problem = context_read_set_item_problem(
            ref,
            ROOT,
            allow_task_packet_ref=True,
        )
        if problem:
            kind, reason = problem
            if kind == "overbroad":
                overbroad_refs.append(ref)
            else:
                read_errors.append({"path": ref, "error": reason})
            continue
        path = rel(ref)
        if not path.exists():
            missing_refs.append(ref)
            continue
        if path.is_dir():
            overbroad_refs.append(ref)
            continue
        try:
            raw = path.read_bytes()
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            read_errors.append({"path": ref, "error": f"utf-8 decode failed: {exc}"})
            continue
        total_bytes += len(raw)
        total_characters += len(text)
        files.append({
            "path": ref,
            "bytes": len(raw),
            "characters": len(text),
            "estimated_tokens": estimate_tokens_from_characters(len(text)),
        })

    return {
        "files": files,
        "files_count": len(files),
        "bytes": total_bytes,
        "characters": total_characters,
        "estimated_repo_context_tokens": estimate_tokens_from_characters(total_characters),
        "measurement_method": CONTEXT_MEASUREMENT_METHOD,
        "actual_model_tokens": "unavailable",
        "actual_model_token_source": "not_provided",
        "pseudo_refs": pseudo_refs,
        "missing_refs": missing_refs,
        "overbroad_refs": overbroad_refs,
        "read_errors": read_errors,
        "limits": (
            "Estimate covers UTF-8 text from repo files named in context_read_set only; "
            "it does not include GitHub issue or PR body text, system/developer prompts, chat history, "
            "tool output, retrieved web/app content, or model completion tokens."
        ),
    }


def print_context_budget_measurement(measurement: dict[str, object], *, as_json: bool) -> int:
    blocking = bool(measurement["missing_refs"] or measurement["overbroad_refs"] or measurement["read_errors"])
    if as_json:
        payload = {"result": "fail" if blocking else "pass", **measurement}
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("Context budget measurement:")
        print(f"files_count: {measurement['files_count']}")
        print(f"bytes: {measurement['bytes']}")
        print(f"characters: {measurement['characters']}")
        print(f"estimated_repo_context_tokens: {measurement['estimated_repo_context_tokens']}")
        print(f"measurement_method: {measurement['measurement_method']}")
        print(f"actual_model_tokens: {measurement['actual_model_tokens']}")
        print(f"actual_model_token_source: {measurement['actual_model_token_source']}")
        for field in ["pseudo_refs", "missing_refs", "overbroad_refs", "read_errors"]:
            values = measurement[field]
            if values:
                print(f"{field}:")
                for value in values:
                    print(f"- {value}")
            else:
                print(f"{field}: none")
        print(f"limits: {measurement['limits']}")
    return 1 if blocking else 0


def compact_pr_body_check(body_file: str | Path, report_file: str | Path) -> tuple[str, dict[str, object]]:
    body_path = rel(body_file)
    report_path = rel(report_file)
    findings: list[dict[str, str]] = []

    if not body_path.exists():
        findings.append({"field": "body_file", "reason": f"PR body file does not exist: {body_file}"})
        body_text = ""
    else:
        body_text = body_path.read_text(encoding="utf-8")

    headings = markdown_headings(body_text)
    if "Compiled Report Reference" not in headings:
        findings.append({
            "field": "Compiled Report Reference",
            "reason": "compact PR body must include a Compiled Report Reference section",
        })
    else:
        report_section = markdown_section(body_text, "Compiled Report Reference")
        if not normalized_field_value(report_section, "report_source"):
            findings.append({
                "field": "report_source",
                "reason": "Compiled Report Reference must name report_source",
            })

    if body_path.exists():
        pr_body_result = subprocess.run(
            ["python3", "scripts/asgk.py", "pr-body-check", "--file", str(body_path)],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if pr_body_result.returncode != 0:
            findings.append({
                "field": "pr_body_check",
                "reason": "compact PR body failed required PR body structure checks",
            })

        policy_gate = run_policy_gate_capture(body_path)
        if policy_gate.returncode != 0:
            findings.append({
                "field": "policy_gate",
                "reason": "compact PR body failed policy gate checks",
            })

    report: dict[str, object] = {}
    if not report_path.exists():
        findings.append({"field": "report_json", "reason": f"compact PR report file does not exist: {report_file}"})
    else:
        try:
            loaded_report = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            findings.append({"field": "report_json", "reason": f"invalid compact PR report JSON: {exc}"})
            loaded_report = {}
        if not isinstance(loaded_report, dict):
            findings.append({"field": "report_json", "reason": "compact PR report JSON must be an object"})
        else:
            report = loaded_report

    report_result = str(report.get("result") or "").lower()
    if report and report_result != "pass":
        findings.append({
            "field": "report.result",
            "reason": f"compiled report result is not pass: {report_result or 'missing'}",
        })

    pr_status_result = report.get("pr_status_result")
    if report and pr_status_result is not None and str(pr_status_result).lower() != "pass":
        findings.append({
            "field": "report.pr_status_result",
            "reason": f"compiled report PR status result is not pass: {pr_status_result}",
        })

    derived_state = str(report.get("derived_state") or "").lower()
    if report and derived_state != "checkable_pass":
        findings.append({
            "field": "report.derived_state",
            "reason": f"compiled report derived_state is not checkable_pass: {derived_state or 'missing'}",
        })

    if report and report.get("low_risk_inferred") is not False:
        findings.append({
            "field": "report.low_risk_inferred",
            "reason": "compiled report must explicitly keep low_risk_inferred false",
        })

    report_findings = report.get("findings")
    if isinstance(report_findings, list) and report_findings:
        findings.append({
            "field": "report.findings",
            "reason": "compiled report has blocking findings",
        })

    result = "fail" if findings else "pass"
    return result, {
        "result": result,
        "low_risk_inferred": False,
        "body_file": normalize_repo_path(str(body_file)),
        "report_file": normalize_repo_path(str(report_file)),
        "compiled_report": {
            "result": report.get("result"),
            "derived_state": report.get("derived_state"),
            "pr_status_result": report.get("pr_status_result"),
            "low_risk_inferred": report.get("low_risk_inferred"),
            "restricted_boundaries": report.get("restricted_boundaries"),
        },
        "findings": findings,
    }


def print_failures(failures: list[str]) -> int:
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("Check passed.")
    return 0


def add_pr_status_finding(
    findings: list[dict[str, str]],
    field: str,
    reason: str,
    recommended_fix: str,
) -> None:
    findings.append(
        {
            "severity": "FAIL",
            "field": field,
            "reason": reason,
            "recommended_fix": recommended_fix,
        }
    )


def check_status_rollup(status_rollup: object, findings: list[dict[str, str]]) -> None:
    if not isinstance(status_rollup, list) or not status_rollup:
        add_pr_status_finding(
            findings,
            "statusCheckRollup",
            "No status checks were reported for this PR.",
            "Wait for GitHub Actions or investigate missing required checks.",
        )
        return

    current_checks, _superseded_checks, ordering_errors = select_latest_status_checks(
        status_rollup
    )
    for error in ordering_errors:
        if error["field"] == "statusCheckRollup.identity":
            recommended_fix = (
                "Provide a usable check name plus workflow/app/provider identity "
                "for repeated CheckRuns; do not deduplicate by timestamp alone."
            )
        elif error["field"] == "statusCheckRollup.shape":
            recommended_fix = (
                "Fetch PR status with gh pr view --json statusCheckRollup and "
                "preserve each check as a structured object."
            )
        else:
            recommended_fix = (
                "Keep the PR merge-blocked until repeated checks have a unique, "
                "reliably timestamped latest run."
            )
        add_pr_status_finding(
            findings,
            error["field"],
            error["reason"],
            recommended_fix,
        )

    passing_conclusions = {"SUCCESS", "SKIPPED", "NEUTRAL"}
    for item in current_checks:
        name = str(item.get("name") or item.get("context") or "unnamed_check")
        status = str(item.get("status") or "").upper()
        conclusion = str(item.get("conclusion") or item.get("state") or "").upper()
        if status and status != "COMPLETED":
            add_pr_status_finding(
                findings,
                f"statusCheckRollup.{name}",
                f"Status check is not complete: {status}.",
                "Wait for the check to complete before merge eligibility.",
            )
        elif conclusion not in passing_conclusions:
            add_pr_status_finding(
                findings,
                f"statusCheckRollup.{name}",
                f"Status check conclusion is not passing: {conclusion or 'missing'}.",
                "Fix the failing check or keep the PR merge-blocked.",
            )


def validated_pr_file_paths(files: object) -> tuple[list[str], list[str]]:
    if not isinstance(files, list):
        return [], ["PR file list is not a list."]
    paths: list[str] = []
    errors: list[str] = []
    for index, item in enumerate(files):
        if isinstance(item, str):
            path = item.strip()
            if path:
                paths.append(path)
            else:
                errors.append(f"PR file entry {index} is a blank path string.")
        elif isinstance(item, dict):
            path_value = (
                item.get("path")
                if "path" in item
                else item.get("filename")
            )
            path = nonblank_string(path_value)
            if path is None:
                errors.append(
                    f"PR file entry {index} has no nonblank string path or filename."
                )
            else:
                paths.append(path)
        else:
            errors.append(
                f"PR file entry {index} is neither a path string nor an object."
            )
    return paths, errors


def pr_file_paths(files: object) -> list[str]:
    paths, _errors = validated_pr_file_paths(files)
    return paths


def issue_number_from_value(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"#\s*(\d+)\b", value)
    if not match:
        return None
    return int(match.group(1))


def merge_decision_issue_number(body: str) -> int | None:
    merge_decision = markdown_section(body, "Merge Decision")
    return issue_number_from_value(field_value(merge_decision, "issue"))


def closing_issue_numbers(references: object) -> set[int]:
    if not isinstance(references, list):
        return set()
    numbers: set[int] = set()
    for item in references:
        if not isinstance(item, dict):
            continue
        number = item.get("number")
        if isinstance(number, int):
            numbers.add(number)
        elif isinstance(number, str) and number.isdigit():
            numbers.add(int(number))
    return numbers


def check_closing_issue_reference(payload: dict[str, object], body: str, findings: list[dict[str, str]]) -> None:
    issue_number = merge_decision_issue_number(body)
    if issue_number is None:
        return

    if "closingIssuesReferences" not in payload:
        add_pr_status_finding(
            findings,
            "closingIssuesReferences",
            "PR closing issue references are missing from the metadata payload.",
            "Fetch PR metadata with gh pr view --json closingIssuesReferences or provide fixture metadata.",
        )
        return

    if issue_number not in closing_issue_numbers(payload.get("closingIssuesReferences")):
        add_pr_status_finding(
            findings,
            "closingIssuesReferences",
            f"Merge Decision issue #{issue_number} is not a GitHub closing issue reference.",
            f"Use a GitHub closing keyword such as `Closes #{issue_number}` instead of a non-closing reference.",
        )


def pr_status_issue_payload(payload: dict[str, object], issue_number: int) -> dict[str, object] | None:
    for key in ["issue", "closingIssue", "workUnit"]:
        candidate = payload.get(key)
        if isinstance(candidate, dict):
            number = candidate.get("number")
            if number == issue_number or str(number) == str(issue_number):
                return candidate

    references = payload.get("closingIssuesReferences")
    if isinstance(references, list):
        for item in references:
            if not isinstance(item, dict):
                continue
            number = item.get("number")
            if number == issue_number or str(number) == str(issue_number):
                if item.get("body") is not None:
                    return item

    if payload.get("_asgk_live_lookup") is True:
        try:
            return load_live_work_unit("issue", str(issue_number))
        except RuntimeError:
            return None
    return None


def check_pr_issue_allowed_paths(
    payload: dict[str, object],
    body: str,
    file_paths: list[str],
    findings: list[dict[str, str]],
) -> None:
    issue_number = merge_decision_issue_number(body)
    if issue_number is None:
        return
    issue_payload = pr_status_issue_payload(payload, issue_number)
    if issue_payload is None:
        add_pr_status_finding(
            findings,
            "issue.allowed_paths",
            f"Closing issue #{issue_number} body is unavailable for allowed_paths verification.",
            "Fetch live PR status with --pr or provide fixture issue metadata with body and allowed_paths.",
        )
        return

    issue_body = str(issue_payload.get("body") or "")
    allowed_paths = extract_allowed_paths(issue_body)
    if not allowed_paths:
        add_pr_status_finding(
            findings,
            "issue.allowed_paths",
            f"Closing issue #{issue_number} does not include material allowed_paths.",
            "Add explicit allowed_paths to the closing issue before merge eligibility.",
        )
        return

    for path in file_paths:
        normalized = normalize_repo_path(path)
        if not any(path_matches_allowed(normalized, allowed) for allowed in allowed_paths):
            add_pr_status_finding(
                findings,
                "files.allowed_paths",
                f"PR file is outside closing issue allowed_paths: {normalized}",
                "Remove the file from this PR or update the durable issue before merge eligibility.",
            )


def check_pr_status_payload(payload: dict[str, object]) -> tuple[str, list[dict[str, str]]]:
    findings: list[dict[str, str]] = []

    if payload.get("state") != "OPEN":
        add_pr_status_finding(
            findings,
            "state",
            f"PR state is not OPEN: {payload.get('state') or 'missing'}.",
            "Validate only open PRs before merge eligibility.",
        )

    if payload.get("isDraft") is not False:
        draft_value = payload.get("isDraft")
        add_pr_status_finding(
            findings,
            "isDraft",
            (
                "PR draft state is not positively established as boolean false; "
                f"found {draft_value!r}."
            ),
            (
                "Mark the PR ready when it should enter human review, while "
                "keeping the durable decision merge_blocked until every "
                "required gate is complete."
            ),
        )

    merge_state = str(payload.get("mergeStateStatus") or "").upper()
    if merge_state != "CLEAN":
        add_pr_status_finding(
            findings,
            "mergeStateStatus",
            f"PR merge state is not CLEAN: {merge_state or 'missing'}.",
            "Resolve merge conflicts, blocked state, or pending mergeability before merge.",
        )

    if "reviewDecision" not in payload:
        add_pr_status_finding(
            findings,
            "reviewDecision",
            "Review decision metadata is missing.",
            "Fetch PR metadata with gh pr view --json reviewDecision.",
        )
    else:
        raw_review_decision = payload.get("reviewDecision")
        if raw_review_decision is None:
            review_decision = ""
        elif isinstance(raw_review_decision, str):
            review_decision = raw_review_decision
        else:
            review_decision = "__INVALID_SHAPE__"

        if review_decision in {"CHANGES_REQUESTED", "REVIEW_REQUIRED"}:
            add_pr_status_finding(
                findings,
                "reviewDecision",
                f"Review decision blocks merge: {review_decision}.",
                "Resolve requested changes or required review before merge eligibility.",
            )
        elif review_decision not in {"", "APPROVED"}:
            add_pr_status_finding(
                findings,
                "reviewDecision",
                (
                    "Review decision metadata has an unsupported shape or "
                    f"value: {raw_review_decision!r}."
                ),
                (
                    "Use GitHub reviewDecision metadata with APPROVED or an "
                    "explicit empty/null no-decision state; unknown values fail closed."
                ),
            )

    check_status_rollup(payload.get("statusCheckRollup"), findings)

    body = payload.get("body")
    if body is None:
        body = ""
    body_text = str(body)
    merge_section = markdown_section(body_text, "Merge Decision")
    declared_merge_result = (raw_field_value(merge_section, "result") or "").strip()
    if declared_merge_result != "merge_allowed":
        add_pr_status_finding(
            findings,
            "merge_decision.result",
            f"Strict PR readiness requires result: merge_allowed; found {declared_merge_result or 'missing'}.",
            "Keep the PR merge-blocked until every required decision gate is complete, then update the durable Merge Decision.",
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        body_path = Path(tmpdir) / "pull_request_body.md"
        body_path.write_text(body_text, encoding="utf-8")
        merge_decision_gate = run_policy_gate_capture(
            body_path,
            mode=MERGE_DECISION_MODE,
        )
        if merge_decision_gate.returncode != 0:
            body_coherence = run_policy_gate_capture(
                body_path,
                mode=BODY_COHERENCE_MODE,
            )
        else:
            body_coherence = merge_decision_gate
        if body_coherence.returncode != 0:
            add_pr_status_finding(
                findings,
                "body",
                "PR body coherence check failed.",
                "Fix Current Status Impact, Merge Decision, source-of-truth, or required PR structure fields.",
            )

    check_closing_issue_reference(payload, body_text, findings)

    if "files" not in payload:
        add_pr_status_finding(
            findings,
            "files",
            "PR file list is missing.",
            "Fetch PR metadata with gh pr view --json files or provide a fixture with files.",
        )
    else:
        file_paths, file_shape_errors = validated_pr_file_paths(payload.get("files"))
        for error in file_shape_errors:
            add_pr_status_finding(
                findings,
                "files.shape",
                error,
                (
                    "Preserve the gh pr view files list as path strings or "
                    "objects with one nonblank string path."
                ),
            )
        if not file_shape_errors:
            check_pr_issue_allowed_paths(payload, body_text, file_paths, findings)
            hygiene = run_hygiene_capture(file_paths)
            if hygiene.returncode != 0:
                add_pr_status_finding(
                    findings,
                    "files",
                    "Changed-path hygiene failed.",
                    "Remove protected/runtime/private-source-like paths or keep the PR human-gated.",
                )

    return ("fail" if findings else "pass", findings)


def print_pr_status_result(
    payload: dict[str, object],
    result: str,
    findings: list[dict[str, str]],
    *,
    evidence_source: str,
    as_json: bool,
) -> int:
    evidence_description = (
        "live GitHub PR metadata"
        if evidence_source == "live_github"
        else "supplied fixture or captured PR metadata"
    )
    boundary = (
        f"check-pr composes the named mechanical fields from {evidence_description}. "
        "It does not infer low-risk status, human approval, or merge authority."
    )
    output = {
        "result": result,
        "evidence_source": evidence_source,
        "proof_boundary": boundary,
        "low_risk_inferred": False,
        "human_approval_inferred": False,
        "merge_authority_inferred": False,
        "pr": payload.get("number"),
        "url": payload.get("url"),
        "findings": findings,
    }
    if as_json:
        print(json.dumps(output, indent=2, sort_keys=True))
    elif findings:
        for finding in findings:
            print(
                f"{finding['severity']}: {finding['field']} - "
                f"{finding['reason']} Fix: {finding['recommended_fix']}"
            )
        print(f"PR status check result: fail. {boundary}")
    else:
        print(f"PR status check passed. {boundary}")
    return 1 if findings else 0


def cmd_doctor(_args: argparse.Namespace) -> int:
    commands = [
        ["python3", "scripts/check_project.py"],
        ["python3", "scripts/validate_bootstrap.py"],
        ["git", "diff", "--check"],
        ["python3", "scripts/asgk.py", "status-check"],
    ]
    baseline = run_many(commands)
    changed_paths = run_changed_path_hygiene_checks()
    textual = run_textual_negative_checks()
    return 1 if baseline or changed_paths or textual else 0


def cmd_validate(_args: argparse.Namespace) -> int:
    return run_many([["python3", "scripts/validate_bootstrap.py"]])


def cmd_hygiene(args: argparse.Namespace) -> int:
    command = ["python3", "scripts/governance_hygiene.py"]
    if args.paths_file:
        command.extend(["--paths-file", args.paths_file])
    if args.git_base or args.git_head:
        if args.git_base:
            command.extend(["--git-base", args.git_base])
        if args.git_head:
            command.extend(["--git-head", args.git_head])
    if args.expect_blocked:
        command.append("--expect-blocked")
    return run_many([command])


def cmd_negative(args: argparse.Namespace) -> int:
    return run_negative_case(args.case)


def print_policy_gate_routing_failure(
    *,
    field: str,
    reason: str,
    recommended_fix: str,
    declared_result: str = "",
    as_json: bool,
) -> int:
    finding = {
        "severity": "FAIL",
        "category": "policy_gate_routing",
        "field": field,
        "reason": reason,
        "recommended_fix": recommended_fix,
        "blocks_merge_eligibility": True,
    }
    boundary = (
        "No body validation mode was selected because GitHub PR event routing "
        "was incomplete or invalid."
    )
    if as_json:
        print(json.dumps({
            "result": "fail",
            "routing": "fail_closed",
            "declared_merge_decision": declared_result,
            "proof_boundary": boundary,
            "merge_eligibility_inferred": False,
            "low_risk_inferred": False,
            "human_approval_inferred": False,
            "findings": [finding],
        }, indent=2, sort_keys=True))
    else:
        print(
            f"FAIL: [policy_gate_routing] {field} - {reason} "
            f"Fix: {recommended_fix}"
        )
        print(boundary)
        print(
            "Full PR merge eligibility, low-risk status, and human approval "
            "were not inferred."
        )
    return 1


def cmd_policy_gate(args: argparse.Namespace) -> int:
    if bool(args.pr_body) == bool(args.github_event):
        return print_failures(["provide exactly one of --pr-body or --github-event"])

    if args.pr_body:
        return run_policy_gate(
            rel(args.pr_body),
            mode=args.mode or MERGE_DECISION_MODE,
            as_json=args.json,
        )

    if args.mode is not None:
        return print_policy_gate_routing_failure(
            field="mode",
            reason=(
                "GitHub PR event validation must route from the durable "
                "Merge Decision result; an explicit mode override is not allowed."
            ),
            recommended_fix=(
                "Remove `--mode` when using `--github-event`; use explicit "
                "modes only with `--pr-body`."
            ),
            as_json=args.json,
        )

    event = json.loads(rel(args.github_event).read_text(encoding="utf-8"))
    pull_request = event.get("pull_request")
    if not isinstance(pull_request, dict):
        return print_policy_gate_routing_failure(
            field="pull_request",
            reason="GitHub event payload does not contain a pull_request object.",
            recommended_fix=(
                "Provide the complete pull_request event payload; do not treat "
                "missing PR metadata as a successful skip."
            ),
            as_json=args.json,
        )

    body = pull_request.get("body")
    if body is None:
        body = ""

    with tempfile.TemporaryDirectory() as tmpdir:
        body_path = Path(tmpdir) / "pull_request_body.md"
        body_path.write_text(str(body), encoding="utf-8")
        selected_mode = args.mode
        if selected_mode is None:
            merge_section = markdown_section(str(body), "Merge Decision")
            declared_result = (raw_field_value(merge_section, "result") or "").strip()
            if declared_result == "merge_allowed":
                selected_mode = MERGE_DECISION_MODE
            elif declared_result == "merge_blocked":
                selected_mode = BODY_COHERENCE_MODE
            else:
                return print_policy_gate_routing_failure(
                    field="result",
                    reason=(
                        "GitHub event routing requires a declared "
                        "`merge_allowed` or `merge_blocked` result."
                    ),
                    recommended_fix=(
                        "Add a valid durable Merge Decision result before "
                        "rerunning the event check."
                    ),
                    declared_result=declared_result,
                    as_json=args.json,
                )
        return run_policy_gate(
            body_path,
            mode=selected_mode,
            as_json=args.json,
        )


def cmd_check_pr(args: argparse.Namespace) -> int:
    if bool(args.pr) == bool(args.json_file):
        return print_failures(["provide exactly one of --pr or --json-file"])

    if args.json_file:
        payload = json.loads(rel(args.json_file).read_text(encoding="utf-8"))
    else:
        command = [
            "gh", "pr", "view", str(args.pr),
            "--json",
            "number,title,state,isDraft,mergeStateStatus,reviewDecision,statusCheckRollup,body,files,url,closingIssuesReferences",
        ]
        result = subprocess.run(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if result.returncode != 0:
            print(result.stdout.strip() or "FAIL: gh pr view failed.")
            return result.returncode
        payload = json.loads(result.stdout)
        if isinstance(payload, dict):
            payload["_asgk_live_lookup"] = True

    if not isinstance(payload, dict):
        return print_failures(["PR status payload must be a JSON object"])

    result, findings = check_pr_status_payload(payload)
    evidence_source = (
        "supplied_json_fixture_or_capture"
        if args.json_file
        else "live_github"
    )
    return print_pr_status_result(
        payload,
        result,
        findings,
        evidence_source=evidence_source,
        as_json=args.json,
    )


def load_pr_payload(args: argparse.Namespace) -> dict[str, object]:
    if bool(args.pr) == bool(args.json_file):
        raise ValueError("provide exactly one of --pr or --json-file")
    if args.json_file:
        payload = json.loads(read_text(args.json_file))
    else:
        command = [
            "gh", "pr", "view", str(args.pr),
            "--json",
            "number,title,state,isDraft,mergeStateStatus,reviewDecision,statusCheckRollup,body,files,url,closingIssuesReferences",
        ]
        result = subprocess.run(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stdout.strip() or "gh pr view failed")
        payload = json.loads(result.stdout)
        if isinstance(payload, dict):
            payload["_asgk_live_lookup"] = True
    if not isinstance(payload, dict):
        raise ValueError("PR payload must be a JSON object")
    return payload


def cmd_compact_pr_report(args: argparse.Namespace) -> int:
    try:
        payload = load_pr_payload(args)
    except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
        return print_failures([str(exc)])

    result, output = compact_pr_report_from_payload(payload)
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    elif result == "pass":
        print(f"Compact PR report passed for PR #{output.get('pr', {}).get('number')}.")
    elif result == "requires_human":
        boundaries = ", ".join(output.get("restricted_boundaries", []))
        print(f"Compact PR report requires human review for restricted boundary: {boundaries}")
    else:
        for finding in output.get("findings", []):
            print(f"FAIL: {finding['field']} - {finding['reason']}")
        print("Compact PR report failed. No low-risk status was inferred.")
    return 0 if result == "pass" else 1


def print_work_unit_input_failure(
    reason: str,
    *,
    authority_only: bool,
    as_json: bool,
) -> int:
    finding = {
        "code": "WU_INPUT_MODE_INVALID",
        "severity": "FAIL",
        "field": "input",
        "reason": reason,
        "recommended_fix": (
            "Use --authority-only without changed-path options, or provide exactly "
            "one post-diff source: --paths-file or --git-base with --git-head."
        ),
        "blocking": True,
    }
    if as_json:
        print(json.dumps({
            "result": "fail",
            "low_risk_inferred": False,
            "authority_only": authority_only,
            "findings": [finding],
        }, indent=2, sort_keys=True))
    else:
        print(
            f"FAIL: [{finding['code']}] {finding['field']} - "
            f"{finding['reason']} Fix: {finding['recommended_fix']}"
        )
    return 1


def cmd_work_unit_check(args: argparse.Namespace) -> int:
    using_paths_file = bool(args.paths_file)
    using_git_range = bool(args.git_base or args.git_head)
    if args.authority_only and (using_paths_file or using_git_range):
        return print_work_unit_input_failure(
            "--authority-only cannot be combined with changed-path inputs",
            authority_only=args.authority_only,
            as_json=args.json,
        )
    if not args.authority_only and using_paths_file == using_git_range:
        return print_work_unit_input_failure(
            "post-diff mode requires exactly one of --paths-file or --git-base/--git-head",
            authority_only=args.authority_only,
            as_json=args.json,
        )
    if using_git_range and not (args.git_base and args.git_head):
        return print_work_unit_input_failure(
            "--git-base and --git-head must be provided together",
            authority_only=args.authority_only,
            as_json=args.json,
        )

    try:
        payload = load_work_unit_payload(args)
        if args.authority_only:
            changed_paths = []
        else:
            changed_paths = (
                read_changed_path_list(args.paths_file)
                if args.paths_file
                else load_git_changed_paths(args.git_base, args.git_head)
            )
    except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
        return print_work_unit_input_failure(
            str(exc),
            authority_only=args.authority_only,
            as_json=args.json,
        )

    result, findings, allowed_paths = check_work_unit_payload(
        payload,
        changed_paths,
        authority_only=args.authority_only,
    )
    return print_work_unit_result(
        payload,
        result,
        findings,
        allowed_paths,
        changed_paths,
        authority_only=args.authority_only,
        as_json=args.json,
    )


def cmd_compact_issue_scope(args: argparse.Namespace) -> int:
    sources = [bool(args.issue), bool(args.json_file)]
    if sum(sources) != 1:
        return print_failures(["provide exactly one of --issue or --json-file"])
    try:
        payload = (
            load_live_work_unit("issue", str(args.issue).lstrip("#"))
            if args.issue
            else json.loads(read_text(args.json_file))
        )
    except (RuntimeError, json.JSONDecodeError) as exc:
        return print_failures([str(exc)])
    if not isinstance(payload, dict):
        return print_failures(["compact issue-scope payload must be a JSON object"])

    result, output = canonical_issue_scope_from_payload(payload)
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    elif result == "pass":
        print(f"Canonical issue scope passed for issue #{output.get('issue')}.")
    else:
        for finding in output.get("findings", []):
            print(f"FAIL: {finding['field']} - {finding['reason']}")
        print("Canonical issue scope failed. No low-risk status was inferred.")
    return 0 if result == "pass" else 1


def cmd_compact_scope_lock(args: argparse.Namespace) -> int:
    sources = [bool(args.issue), bool(args.json_file)]
    if sum(sources) != 1:
        return print_failures(["provide exactly one of --issue or --json-file"])
    try:
        payload = (
            load_live_work_unit("issue", str(args.issue).lstrip("#"))
            if args.issue
            else json.loads(read_text(args.json_file))
        )
    except (RuntimeError, json.JSONDecodeError) as exc:
        return print_failures([str(exc)])
    if not isinstance(payload, dict):
        return print_failures(["compact scope-lock payload must be a JSON object"])

    result, output = compact_scope_lock_from_payload(payload)
    if result == "pass" and args.compare_file:
        try:
            captured = json.loads(read_text(args.compare_file))
        except json.JSONDecodeError as exc:
            return print_failures([str(exc)])
        if not isinstance(captured, dict):
            return print_failures(["captured scope-lock payload must be a JSON object"])
        compare_findings = compare_scope_lock(output, captured)
        if compare_findings:
            output["result"] = "fail"
            output["findings"] = compare_findings
            result = "fail"

    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    elif result == "pass":
        print(f"Compact scope lock passed for issue #{output.get('issue')}: {output.get('scope_hash')}")
    else:
        for finding in output.get("findings", []):
            print(f"FAIL: {finding['field']} - {finding['reason']}")
        print("Compact scope lock failed. No low-risk status was inferred.")
    return 0 if result == "pass" else 1


def cmd_status_check(args: argparse.Namespace) -> int:
    status_path = rel(args.file)
    failures: list[str] = []
    if not status_path.exists():
        return print_failures([f"missing current status file: {args.file}"])
    if not status_path.is_file():
        return print_failures([f"current status path is not a readable file: {args.file}"])

    try:
        text = status_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return print_failures([f"could not read current status file: {exc}"])
    visible_text = strip_html_comments(text)
    heading_occurrences = markdown_heading_occurrences(visible_text)
    all_heading_occurrences = [
        heading
        for _line, _level, heading, _style
        in _visible_markdown_headings(visible_text.splitlines())
    ]
    normalized_headings = {
        heading.casefold()
        for heading in all_heading_occurrences
    }

    for heading in STATUS_REQUIRED_HEADINGS:
        exact_count = heading_occurrences.count(heading)
        folded_count = sum(
            found.casefold() == heading.casefold()
            for found in all_heading_occurrences
        )
        if exact_count == 0:
            failures.append(f"missing current status heading: ## {heading}")
        elif exact_count > 1:
            failures.append(f"duplicate current status heading: ## {heading}")
        if folded_count > exact_count:
            failures.append(
                f"case-variant duplicate current status heading: ## {heading}"
            )

    line_count = len(text.splitlines())
    if line_count > args.max_lines:
        failures.append(f"current status is too long: {line_count} lines > {args.max_lines}")

    if "python3 scripts/asgk.py doctor" not in visible_text:
        failures.append("current status does not name python3 scripts/asgk.py doctor")

    for heading in STATUS_FORBIDDEN_HISTORY_HEADINGS:
        if heading.casefold() in normalized_headings:
            failures.append(f"forbidden history-log heading in current status: ## {heading}")

    lower_text = visible_text.lower()
    for phrase in STATUS_FORBIDDEN_PHRASES:
        if phrase.lower() in lower_text:
            failures.append(f"forbidden current-status phrase: {phrase}")

    next_action = markdown_section(visible_text, "Next safe action")
    if not next_action:
        failures.append("current status next safe action is empty")

    active_work = markdown_section(visible_text, "Active work")
    for field in ("issue", "pr", "branch", "state"):
        exact_occurrences = re.findall(
            rf"^[ \t]*{re.escape(field)}[ \t]*:",
            active_work,
            flags=re.MULTILINE,
        )
        folded_occurrences = re.findall(
            rf"^[ \t]*{re.escape(field)}[ \t]*:",
            active_work,
            flags=re.MULTILINE | re.IGNORECASE,
        )
        if len(exact_occurrences) != 1 or len(folded_occurrences) != 1:
            failures.append(
                f"current status active work must contain exactly one {field} field"
            )
        else:
            value = field_value(active_work, field)
            if value is None or not value.strip():
                failures.append(f"current status active work {field} is empty")

    return print_failures(failures)


def cmd_closeout_check(args: argparse.Namespace) -> int:
    status_path = rel(args.file)
    if not status_path.exists():
        return print_failures([f"missing closeout status file: {args.file}"])
    if not status_path.is_file():
        return print_failures([f"closeout status path is not a readable file: {args.file}"])

    try:
        text = strip_html_comments(status_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        return print_failures([f"could not read closeout status file: {exc}"])
    active_work = markdown_section(text, "Active work")
    next_safe_action = markdown_section(text, "Next safe action")
    active_issue = field_value(active_work, "issue")
    active_pr = field_value(active_work, "pr")
    active_branch = field_value(active_work, "branch")
    failures: list[str] = []

    for issue in args.completed_issue:
        if numbered_ref_matches(active_issue, issue):
            failures.append(f"completed issue still appears in active work: {issue}")

    for pr in args.completed_pr:
        if numbered_ref_matches(active_pr, pr):
            failures.append(f"completed PR still appears in active work: {pr}")

    for branch in args.completed_branch:
        if branch_ref_matches(active_branch, branch):
            failures.append(f"completed branch still appears in active work: {branch}")

    if not next_safe_action:
        failures.append("next safe action is empty")
    else:
        for pattern in CLOSEOUT_PRE_MERGE_NEXT_ACTION_PATTERNS:
            if re.search(pattern, next_safe_action, flags=re.IGNORECASE):
                failures.append(f"next safe action appears to describe pre-merge closeout work: {pattern}")

    return print_failures(failures)


def cmd_current_status_impact_check(args: argparse.Namespace) -> int:
    try:
        pr_body = read_text(args.pr_body)
    except (OSError, UnicodeError) as exc:
        return print_failures([f"could not read PR body file: {exc}"])
    try:
        changed_paths = read_changed_paths(args.changed_paths_file)
    except (OSError, UnicodeError) as exc:
        return print_failures([f"could not read changed-paths file: {exc}"])
    current_status_path = args.file.lstrip("./")
    current_status_changed = any(
        same_repo_path(path, current_status_path)
        or same_repo_path(path, CANONICAL_CURRENT_STATUS_PATH)
        for path in changed_paths
    )
    current_status_section = markdown_section(pr_body, "Current Status Impact")
    handoff_section = markdown_section(pr_body, "Handoff Report")
    failures: list[str] = []

    if not current_status_section:
        return print_failures(["missing PR Current Status Impact section"])

    for field in CURRENT_STATUS_IMPACT_REQUIRED_FIELDS:
        exact_occurrences = re.findall(
            rf"^[ \t]*{re.escape(field)}[ \t]*:",
            current_status_section,
            flags=re.MULTILINE,
        )
        folded_occurrences = re.findall(
            rf"^[ \t]*{re.escape(field)}[ \t]*:",
            current_status_section,
            flags=re.MULTILINE | re.IGNORECASE,
        )
        if len(exact_occurrences) != 1 or len(folded_occurrences) != 1:
            failures.append(
                f"Current Status Impact must contain exactly one {field} field"
            )

    status, status_shape_valid = strict_contract_scalar_value(
        current_status_section,
        "status",
    )
    if not status_shape_valid or status not in CURRENT_STATUS_IMPACT_ALLOWED_VALUES:
        failures.append("Current Status Impact status must be updated, not_applicable, or deferred")

    reason = field_value(current_status_section, "reason")
    if not is_material_handoff_text(reason):
        failures.append("Current Status Impact reason is missing or non-specific")

    updated_raw = raw_field_value(
        current_status_section,
        "current_status_updated_in_this_pr",
    ) or ""
    updated = updated_raw.strip()
    if updated not in {"true", "false"}:
        failures.append("current_status_updated_in_this_pr must be true or false")
    if status == "updated" and updated not in TRUE_VALUES:
        failures.append("status is updated but current_status_updated_in_this_pr is not true")
    if status in {"not_applicable", "deferred"} and updated != "false":
        failures.append(f"status is {status} but current_status_updated_in_this_pr is not false")

    if current_status_changed and status != "updated":
        failures.append(f"{CANONICAL_CURRENT_STATUS_PATH} changed but Current Status Impact status is not updated")

    if status == "updated" and not current_status_changed:
        failures.append(f"Current Status Impact status is updated but {CANONICAL_CURRENT_STATUS_PATH} did not change")

    post_merge_safe_raw = raw_field_value(
        current_status_section,
        "post_merge_safe",
    ) or ""
    post_merge_safe = post_merge_safe_raw.strip()
    if (
        post_merge_safe.startswith(('"', "'"))
        and post_merge_safe.endswith(post_merge_safe[0])
    ):
        post_merge_safe = post_merge_safe[1:-1]
    if post_merge_safe not in {"true", "false", "not_applicable"}:
        failures.append("post_merge_safe must be true, false, or not_applicable")
    elif (
        post_merge_safe in {"true", "false"}
        and post_merge_safe_raw.strip() != post_merge_safe
    ):
        failures.append("post_merge_safe booleans must be unquoted")
    if status == "updated" and post_merge_safe not in TRUE_VALUES:
        failures.append("status is updated but post_merge_safe is not true")

    follow_up, follow_up_shape_valid = strict_contract_scalar_value(
        current_status_section,
        "follow_up_issue",
    )
    if not follow_up_shape_valid or not valid_follow_up_issue(follow_up):
        failures.append("follow_up_issue must be exactly none or one #<number> issue reference")
    if status == "deferred":
        has_handoff_next_action = bool(re.search(r"next safe action", handoff_section, flags=re.IGNORECASE))
        if follow_up == "none" and not has_handoff_next_action:
            failures.append("status is deferred without follow_up_issue or Handoff Report next safe action")
        if current_status_changed:
            failures.append(f"status is deferred but {CANONICAL_CURRENT_STATUS_PATH} changed")

    if current_status_changed:
        status_result = subprocess.run(
            ["python3", "scripts/asgk.py", "status-check", "--file", args.file],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if status_result.returncode != 0:
            failures.append("status-check failed for current status file")
        else:
            try:
                status_text = strip_html_comments(read_text(args.file))
            except (OSError, UnicodeError) as exc:
                failures.append(f"could not read current status file: {exc}")
            else:
                active_work = markdown_section(status_text, "Active work")
                next_safe_action = markdown_section(status_text, "Next safe action")
                active_issue = field_value(active_work, "issue")
                active_pr = field_value(active_work, "pr")
                active_branch = field_value(active_work, "branch")

                if numbered_ref_matches(active_pr, args.this_pr):
                    failures.append(
                        f"current status active work points to this PR: {args.this_pr}"
                    )

                for issue in args.closing_issue:
                    if numbered_ref_matches(active_issue, issue):
                        failures.append(
                            "current status active work points to closing issue: "
                            f"{issue}"
                        )

                if branch_ref_matches(active_branch, args.this_branch):
                    failures.append(
                        "current status active work points to this branch: "
                        f"{args.this_branch}"
                    )

                if not next_safe_action:
                    failures.append("current status next safe action is empty")
                else:
                    for pattern in CLOSEOUT_PRE_MERGE_NEXT_ACTION_PATTERNS:
                        if re.search(
                            pattern,
                            next_safe_action,
                            flags=re.IGNORECASE,
                        ):
                            failures.append(
                                "next safe action appears to describe pre-merge "
                                f"closeout work: {pattern}"
                            )

    return print_failures(failures)


def cmd_pr_body_check(args: argparse.Namespace) -> int:
    policy_gate = run_policy_gate_capture(
        args.file,
        mode=BODY_COHERENCE_MODE,
    )
    if policy_gate.stdout.strip():
        print(policy_gate.stdout.rstrip())
    return policy_gate.returncode


def load_task_packet_check_inputs(
    args: argparse.Namespace,
) -> tuple[dict[str, object], str, dict[str, object] | None]:
    if args.json_file:
        if args.file or args.issue or args.issue_json_file:
            raise ValueError("use either --json-file or --file with --issue/--issue-json-file")
        payload = json.loads(read_text(args.json_file))
        if not isinstance(payload, dict):
            raise ValueError("task-packet fixture bundle must be a JSON object")
        competing_packet_fields = [
            field
            for field in payload
            if field == "bad_input" or field in TASK_PACKET_SOURCE_FIELDS
        ]
        if "task_packet" in payload and competing_packet_fields:
            raise TaskFieldAmbiguityError([
                "task-packet fixture bundle cannot combine task_packet with "
                "another packet source: "
                + ", ".join(sorted(competing_packet_fields))
            ])
        issue_payload = payload.get("issue")
        packet = payload.get("task_packet")
        if not isinstance(packet, dict):
            raise ValueError("task-packet fixture bundle must include task_packet object")
        if issue_payload is not None and not isinstance(issue_payload, dict):
            raise ValueError("task-packet fixture issue must be an object")
        return packet, json.dumps(packet, sort_keys=True), issue_payload

    if not args.file:
        raise ValueError("provide --file or --json-file")
    if args.issue and args.issue_json_file:
        raise ValueError("provide at most one of --issue or --issue-json-file")

    packet, source_text = load_task_packet_payload(args.file)
    if args.issue:
        issue_payload = load_live_work_unit("issue", str(args.issue).lstrip("#"))
    elif args.issue_json_file:
        issue_payload = json.loads(read_text(args.issue_json_file))
    else:
        issue_payload = None
    if issue_payload is not None and not isinstance(issue_payload, dict):
        raise ValueError("task-packet issue payload must be a JSON object")
    return packet, source_text, issue_payload


def print_task_packet_input_failure(reason: str, *, as_json: bool) -> int:
    finding = {
        "code": "TP_INPUT_MODE_INVALID",
        "field": "input",
        "reason": reason,
        "blocking": True,
    }
    output = {
        "result": "fail",
        "low_risk_inferred": False,
        "proof_boundary": "No task-packet evaluation ran because the input mode was invalid.",
        "findings": [finding],
    }
    if as_json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(f"FAIL: [{finding['code']}] {finding['field']} - {finding['reason']}")
    return 1


def print_task_packet_ambiguity_failure(
    reasons: tuple[str, ...],
    *,
    as_json: bool,
) -> int:
    findings = [
        {
            "code": "TP_TASK_FIELD_AMBIGUOUS",
            "field": "task_packet",
            "reason": reason,
            "blocking": True,
        }
        for reason in reasons
    ]
    output = {
        "result": "fail",
        "low_risk_inferred": False,
        "mode": None,
        "issue": None,
        "issue_scope": None,
        "task_packet": None,
        "mechanically_checked": [
            "visible top-level task-packet field uniqueness",
        ],
        "not_checked": [
            "packet mode and field shape",
            "source issue authority",
            "allowed_paths non-expansion",
            "context_read_set exact-item non-expansion",
            "project_specific_validation exact-item non-expansion",
            "implementation correctness",
            "PR readiness, human approval, merge authority, or issue completion",
        ],
        "proof_boundary": (
            "No task-packet authority or comparison proof was established "
            "because the visible task-field source was ambiguous."
        ),
        "findings": findings,
    }
    if as_json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        for finding in findings:
            print(
                f"FAIL: [{finding['code']}] {finding['field']} - "
                f"{finding['reason']}"
            )
    return 1


def cmd_task_packet_check(args: argparse.Namespace) -> int:
    try:
        packet, source_text, issue_payload = load_task_packet_check_inputs(args)
    except TaskFieldAmbiguityError as exc:
        return print_task_packet_ambiguity_failure(
            exc.reasons,
            as_json=args.json,
        )
    except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
        return print_task_packet_input_failure(str(exc), as_json=args.json)

    result, output = evaluate_task_packet(packet, source_text, issue_payload)
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    elif result == "pass":
        mode = output.get("mode")
        issue = output.get("issue")
        suffix = f" against issue #{issue}" if issue is not None else ""
        print(f"Task packet check passed for {mode}{suffix}.")
        print(output["proof_boundary"])
    else:
        for finding in output.get("findings", []):
            print(
                f"FAIL: [{finding.get('code', 'TP_UNKNOWN')}] "
                f"{finding['field']} - {finding['reason']}"
            )
        print("Task packet check failed. No low-risk status was inferred.")
    return 0 if result == "pass" else 1


def cmd_compact_pr_body_check(args: argparse.Namespace) -> int:
    result, output = compact_pr_body_check(args.body_file, args.report_json)
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    elif result == "pass":
        print("Compact PR body check passed. No low-risk status was inferred.")
    else:
        for finding in output.get("findings", []):
            print(f"FAIL: {finding['field']} - {finding['reason']}")
        print("Compact PR body check failed. No low-risk status was inferred.")
    return 0 if result == "pass" else 1


def cmd_compact_handoff_check(args: argparse.Namespace) -> int:
    result, output = compact_handoff_check(
        args.file,
        args.current_status,
        completed_issues=args.completed_issue,
        completed_prs=args.completed_pr,
        completed_branches=args.completed_branch,
    )
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    elif result == "pass":
        print("Compact handoff check passed. No low-risk status was inferred.")
    else:
        for finding in output.get("findings", []):
            print(f"FAIL: {finding['field']} - {finding['reason']}")
        print("Compact handoff check failed. No low-risk status was inferred.")
    return 0 if result == "pass" else 1


def cmd_compact_target_upgrade_check(args: argparse.Namespace) -> int:
    result, output = compact_target_upgrade_check(args.manifest)
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    elif result == "pass":
        print("Compact target upgrade check passed. No low-risk status was inferred.")
    else:
        for finding in output.get("findings", []):
            print(f"FAIL: {finding['field']} - {finding['reason']}")
        print("Compact target upgrade check failed. No low-risk status was inferred.")
    return 0 if result == "pass" else 1


def cmd_context_budget_measure(args: argparse.Namespace) -> int:
    try:
        packet, source_text = load_task_packet_payload(args.task_packet)
    except TaskFieldAmbiguityError as exc:
        return print_task_packet_ambiguity_failure(
            exc.reasons,
            as_json=args.json,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        return print_failures([f"invalid task packet format: {exc}"])
    result, findings = validate_task_packet_shape(packet, source_text)
    if result != "pass":
        for finding in findings:
            print(
                f"FAIL: [{finding.get('code', 'TP_UNKNOWN')}] "
                f"{finding['field']} - {finding['reason']}"
            )
        return 1
    measurement = context_budget_measurement(packet)
    return print_context_budget_measurement(measurement, as_json=args.json)


def cmd_handoff_check(args: argparse.Namespace) -> int:
    result, output, _packet = evaluate_handoff_file(
        args.file,
    )
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    elif result == "pass":
        print("Handoff check passed.")
        print(output["proof_boundary"])
    else:
        for finding in output.get("findings", []):
            print(
                f"FAIL: [{finding.get('code', 'HP_UNKNOWN')}] "
                f"{finding['field']} - {finding['reason']}"
            )
        print("Handoff check failed. No approval or completion was inferred.")
    return 0 if result == "pass" else 1


def cmd_handoff_template(args: argparse.Namespace) -> int:
    active_issue = args.issue or "AI_TODO: active issue, e.g. #40"
    active_pr = args.pr or "AI_TODO: active PR or none with reason"
    branch = args.branch or "AI_TODO: current branch"
    objective = args.objective or "AI_TODO: summarize objective from durable source"

    def quote(value: str) -> str:
        return json.dumps(value, ensure_ascii=False)

    packet = f"""handoff_packet:
  active_issue: {quote(active_issue)}
  active_pr: {quote(active_pr)}
  durable_source_of_truth:
    - {quote(active_issue)}
  branch: {quote(branch)}
  objective: {quote(objective)}
  current_state: "AI_TODO: summarize current state from issue, PR, and repo files."
  remaining:
    - "AI_TODO: remaining bounded work."
  allowed_paths:
    - "AI_TODO: copy allowed path from issue."
  modified_files:
    - "AI_TODO: list modified file, or none with a reason."
  non_goals:
    - "AI_TODO: copy a material non-goal from the issue."
  must_not_do:
    - "AI_TODO: forbidden action or path for the next actor."
  must_read:
    - "AGENTS.md"
    - "docs/handoff/CURRENT_STATUS.md"
    - "docs/control/HANDOFF_PACKET.md"
    - "AI_TODO: active issue or PR."
  validation_status:
    status: "not_run"
    evidence:
      - "AI_TODO: command result or reason validation has not run."
    reason: "AI_TODO: explain why this status is accurate."
  blockers:
    - "AI_TODO: blocker, or none with a material reason."
  next_safe_action: "AI_TODO: one concrete next safe action."
"""
    print(packet, end="")
    return 0


def cmd_target_install_check(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve()
    findings = target_install_findings(root)
    return print_target_install_findings(findings, as_json=args.json, strict=args.strict)


def cmd_target_install_plan(args: argparse.Namespace) -> int:
    from target_install_plan import build_plan as build_target_install_plan
    from target_install_plan import print_plan_text as print_target_install_plan_text

    root = Path(args.repo_root).resolve()
    plan = build_target_install_plan(root)
    if args.json:
        print(json.dumps(plan, indent=2, sort_keys=True))
    else:
        print_target_install_plan_text(plan)
    return 0


def cmd_release_state_check(args: argparse.Namespace) -> int:
    failures = check_release_state_docs(
        tag=args.tag,
        release_title=args.release_title,
        readme_path=rel(args.readme),
        roadmap_path=rel(args.roadmap),
        current_status_path=rel(args.current_status),
        release_policy_path=rel(args.release_policy),
    )
    return print_failures(failures)


def cmd_workspace_state_check(args: argparse.Namespace) -> int:
    if args.json_file:
        payload = json.loads(read_text(args.json_file))
        if not isinstance(payload, dict):
            return print_failures(["workspace-state JSON fixture must be an object"])
    else:
        payload = live_workspace_state(args.base_ref)
    findings = workspace_state_findings(payload, main_branch=args.main_branch)
    return print_workspace_state_result(
        payload,
        findings,
        as_json=args.json,
        strict=args.strict,
        expect_warnings=args.expect_warnings,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASGK minimal validation CLI.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("doctor", help="Run baseline positive and negative checks.")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("validate", help="Run bootstrap governance validation.")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("hygiene", help="Run changed-path governance hygiene.")
    p.add_argument("--paths-file")
    p.add_argument("--git-base")
    p.add_argument("--git-head")
    p.add_argument("--expect-blocked", action="store_true")
    p.set_defaults(func=cmd_hygiene)

    p = sub.add_parser("negative", help="Run opt-in negative checks.")
    p.add_argument("case", nargs="?", default="changed-paths", choices=NEGATIVE_CASE_CHOICES)
    p.set_defaults(func=cmd_negative)

    p = sub.add_parser("compact-issue-scope", help="Emit a canonical compact-governance issue scope object.")
    p.add_argument("--issue", help="GitHub issue number for live gh REST lookup.")
    p.add_argument("--json-file", help="Fixture or captured issue JSON payload.")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_compact_issue_scope)

    p = sub.add_parser("compact-scope-lock", help="Emit a deterministic compact-governance scope lock from an issue.")
    p.add_argument("--issue", help="GitHub issue number for live gh REST lookup.")
    p.add_argument("--json-file", help="Fixture or captured issue JSON payload.")
    p.add_argument("--compare-file", help="Captured scope-lock JSON to compare against the current issue scope.")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_compact_scope_lock)

    p = sub.add_parser("compact-pr-report", help="Compile a tool-derived compact PR report from GitHub PR metadata.")
    p.add_argument("--pr", help="GitHub pull request number for live gh lookup.")
    p.add_argument("--json-file", help="Fixture or captured gh pr view JSON payload.")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_compact_pr_report)

    p = sub.add_parser(
        "compact-task-packet-check",
        help="Compatibility command that delegates to task-packet-check.",
    )
    p.add_argument("--file", help="Task packet YAML/JSON file.")
    p.add_argument("--issue", help="GitHub issue number for live gh REST lookup.")
    p.add_argument("--issue-json-file", help="Fixture or captured issue JSON payload.")
    p.add_argument(
        "--json-file",
        help="Fixture bundle with task_packet and optional issue objects.",
    )
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_task_packet_check)

    p = sub.add_parser("compact-pr-body-check", help="Check a compact PR body against a compiled report.")
    p.add_argument("--body-file", required=True, help="Compact PR body markdown file.")
    p.add_argument("--report-json", required=True, help="Compiled compact PR report JSON file.")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_compact_pr_body_check)

    p = sub.add_parser("compact-handoff-check", help="Check the canonical handoff core, then compact current-status freshness.")
    p.add_argument("--handoff", "--file", dest="file", required=True, help="Compact handoff YAML file.")
    p.add_argument("--current-status", default="docs/handoff/CURRENT_STATUS.md", help="Current-status file to check.")
    p.add_argument("--completed-issue", action="append", default=[], help="Completed issue ref that must not remain active.")
    p.add_argument("--completed-pr", action="append", default=[], help="Completed PR ref that must not remain active.")
    p.add_argument("--completed-branch", action="append", default=[], help="Completed branch that must not remain active.")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_compact_handoff_check)

    p = sub.add_parser("compact-target-upgrade-check", help="Check a compact-governance target-upgrade manifest.")
    p.add_argument("--manifest", required=True, help="Compact target-upgrade manifest JSON file.")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_compact_target_upgrade_check)

    p = sub.add_parser("policy-gate", help="Run PR-body policy gate checks.")
    p.add_argument("--pr-body", help="Path to a PR body markdown file.")
    p.add_argument("--github-event", help="Path to a GitHub Actions event payload JSON file.")
    p.add_argument(
        "--mode",
        choices=[BODY_COHERENCE_MODE, MERGE_DECISION_MODE],
        help=(
            "Explicit validation layer for --pr-body only. File-backed bodies "
            "default to strict merge-decision; --github-event rejects mode "
            "overrides and always routes by the declared result."
        ),
    )
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_policy_gate)

    p = sub.add_parser("check-pr", help="Check GitHub PR status and checkable merge gates.")
    p.add_argument("--pr", help="GitHub pull request number for live gh lookup.")
    p.add_argument("--json-file", help="Fixture or captured gh pr view JSON payload.")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_check_pr)

    p = sub.add_parser(
        "work-unit-check",
        help="Check work-unit authority before writing or against a completed diff.",
    )
    p.add_argument("--issue", help="GitHub issue number for live gh REST lookup.")
    p.add_argument("--pr", help="GitHub pull request number for live gh REST lookup.")
    p.add_argument("--json-file", help="Fixture or captured issue/PR JSON payload.")
    p.add_argument("--paths-file", help="Newline-delimited changed-path list.")
    p.add_argument("--git-base", help="Base revision for git diff --name-only.")
    p.add_argument("--git-head", help="Head revision for git diff --name-only.")
    p.add_argument(
        "--authority-only",
        action="store_true",
        help="Validate durable authority without requiring or checking changed paths.",
    )
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_work_unit_check)

    p = sub.add_parser("workspace-state-check", help="Report local workspace hygiene without inferring merge readiness.")
    p.add_argument("--json-file", help="Fixture or captured workspace-state JSON payload.")
    p.add_argument("--main-branch", default="main", help="Main branch name used to identify non-work branches.")
    p.add_argument("--base-ref", default="origin/main", help="Base ref used for merged-branch checks.")
    p.add_argument("--strict", action="store_true", help="Return nonzero when warnings are present.")
    p.add_argument("--expect-warnings", action="store_true", help="Return nonzero unless at least one warning is present.")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_workspace_state_check)

    p = sub.add_parser("status-check", help="Check docs/handoff/CURRENT_STATUS.md for compactness and stale markers.")
    p.add_argument("--file", default="docs/handoff/CURRENT_STATUS.md")
    p.add_argument("--max-lines", type=int, default=120)
    p.set_defaults(func=cmd_status_check)

    p = sub.add_parser("closeout-check", help="Check local closeout status against CURRENT_STATUS.md.")
    p.add_argument("--file", default="docs/handoff/CURRENT_STATUS.md")
    p.add_argument("--completed-issue", action="append", default=[])
    p.add_argument("--completed-pr", action="append", default=[])
    p.add_argument("--completed-branch", action="append", default=[])
    p.set_defaults(func=cmd_closeout_check)

    p = sub.add_parser("current-status-impact-check", help="Check PR current-status impact is post-merge-safe.")
    p.add_argument("--pr-body", required=True)
    p.add_argument("--changed-paths-file", required=True)
    p.add_argument("--file", default="docs/handoff/CURRENT_STATUS.md")
    p.add_argument("--this-pr", default="")
    p.add_argument("--closing-issue", action="append", default=[])
    p.add_argument("--this-branch", default="")
    p.set_defaults(func=cmd_current_status_impact_check)

    p = sub.add_parser("pr-body-check", help="Check PR body and Merge Decision Record.")
    p.add_argument("--file", required=True)
    p.set_defaults(func=cmd_pr_body_check)

    p = sub.add_parser(
        "task-packet-check",
        help="Validate a task-packet mode and its non-expansion against issue authority.",
    )
    p.add_argument("--file", help="Task packet YAML/JSON file.")
    p.add_argument("--issue", help="GitHub issue number for live gh REST lookup.")
    p.add_argument("--issue-json-file", help="Fixture or captured issue JSON payload.")
    p.add_argument("--json-file", help="Fixture bundle with task_packet and optional issue objects.")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_task_packet_check)

    p = sub.add_parser(
        "context-budget-measure",
        help="Estimate repo-context tokens from a task packet context_read_set.",
    )
    p.add_argument("--task-packet", required=True)
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_context_budget_measure)

    p = sub.add_parser("handoff-check", help="Check canonical handoff packet shape and material content.")
    p.add_argument("--file", required=True)
    p.add_argument(
        "--fail-on-todo",
        action="store_true",
        help="Compatibility flag; TODO and AI_TODO markers always fail.",
    )
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_handoff_check)

    p = sub.add_parser("handoff-template", help="Print an AI-fillable handoff packet draft.")
    p.add_argument("--issue", default=None)
    p.add_argument("--pr", default=None)
    p.add_argument("--branch", default=None)
    p.add_argument("--objective", default=None)
    p.set_defaults(func=cmd_handoff_template)

    p = sub.add_parser("target-install-check", help="Read-only target ASGK installation check.")
    p.add_argument("--repo-root", default=str(ROOT), help="Repository root to inspect. Defaults to this repository.")
    p.add_argument("--strict", action="store_true", help="Return nonzero when warnings are present.")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_target_install_check)

    p = sub.add_parser("target-install-plan", help="Emit a read-only ASGK target-install plan.")
    p.add_argument("--repo-root", default=str(ROOT), help="Target repository root to inspect. Defaults to this repository.")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_target_install_plan)

    p = sub.add_parser("release-state-check", help="Check post-release docs are not stale candidate/pending surfaces.")
    p.add_argument("--tag", required=True, help="Released tag, for example v1.2.0.")
    p.add_argument("--release-title", required=True, help="Released GitHub release title.")
    p.add_argument("--readme", default="README.md")
    p.add_argument("--roadmap", default="docs/bootstrap/10_roadmap.md")
    p.add_argument("--current-status", default="docs/handoff/CURRENT_STATUS.md")
    p.add_argument(
        "--release-policy",
        default="docs/control/SOURCE_ONLY_RELEASE_POLICY.md",
        help="Optional source-only release policy to scan for duplicated release ledgers when present.",
    )
    p.set_defaults(func=cmd_release_state_check)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
