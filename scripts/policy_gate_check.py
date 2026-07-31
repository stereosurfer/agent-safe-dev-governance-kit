#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from asgk_lib.common import (
    field_block_lines,
    field_value,
    markdown_heading_occurrences,
    markdown_section as section,
    raw_field_value,
    strip_html_comments,
)
from asgk_lib.status_policy import CURRENT_STATUS_IMPACT_REQUIRED_FIELDS
from asgk_lib.validation_result import checked_validation_result, make_finding

PR_REQUIRED_HEADINGS = [
    "Summary",
    "Task Reference",
    "Changed Files",
    "Validation",
    "Evidence Of Completion",
    "Scope Boundaries",
    "Current Status Impact",
    "Runtime Output Status",
    "Merge Decision",
    "Known Gaps",
    "Handoff Report",
]

MERGE_DECISION_REQUIRED_FIELDS = [
    "issue",
    "lane",
    "intelligence_level",
    "durable_source_of_truth",
    "checks_passed",
    "allowed_paths_checked",
    "expected_output_checked",
    "contracts_checked",
    "schemas_checked",
    "storage_boundary",
    "runtime_artifact_boundary",
    "safety_review",
    "human_gates_checked",
    "validation_evidence_checked",
    "validation_claim_source",
    "result",
    "reason",
]

CURRENT_STATUS_ALLOWED_VALUES = {"updated", "not_applicable", "deferred"}
MERGE_RESULT_ALLOWED_VALUES = {"merge_allowed", "merge_blocked"}
VALIDATION_MODES = {"body-coherence", "merge-decision"}
TRUE_VALUES = {"true"}
BLOCKED_COHERENCE_GATE_VALUES = {"true", "pending", "false"}
UNKNOWN_STATE_VALUES = {"", "unknown", "null", "none", "tbd", "todo"}
NON_SPECIFIC_REQUIRED_VALUES = UNKNOWN_STATE_VALUES | {"pending", "false", "no"}
INVALID_REASON_VALUES = NON_SPECIFIC_REQUIRED_VALUES | {
    "passed",
    "pass",
    "n/a",
    "na",
    "all good",
    "merge_allowed",
    "merge_blocked",
}
VALIDATION_CLAIM_SOURCE_VALUES = {
    "local_doctor": {
        "freshly_rerun",
        "recorded_in_pr_body",
        "existing_durable_record",
        "not_run",
        "not_applicable",
    },
    "ci": {
        "github_actions",
        "external_ci",
        "not_run",
        "not_applicable",
    },
}
DECISION_STATE_FIELDS = {
    "checks_passed",
    "allowed_paths_checked",
    "expected_output_checked",
    "human_gates_checked",
    "validation_evidence_checked",
    "result",
}


def normalized_bool_text(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip().strip('"').strip("'").lower()


def add_finding(
    findings: list[dict[str, Any]],
    severity: str,
    code: str,
    category: str,
    field: str,
    reason: str,
    recommended_fix: str,
    *,
    blocks_merge_eligibility: bool = True,
) -> None:
    findings.append(
        {
            "severity": severity,
            "code": code,
            "category": category,
            "field": field,
            "reason": reason,
            "recommended_fix": recommended_fix,
            "blocks_merge_eligibility": blocks_merge_eligibility,
            "blocking": blocks_merge_eligibility,
        }
    )


def line_field_count(text: str, field: str) -> int:
    return len(
        re.findall(
            rf"^[ \t]*{re.escape(field)}[ \t]*:",
            text,
            flags=re.MULTILINE,
        )
    )


def required_field_shape(
    text: str,
    fields: list[str],
    findings: list[dict[str, Any]],
    *,
    category: str,
    record_name: str,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for field in fields:
        count = line_field_count(text, field)
        counts[field] = count
        if count == 0:
            add_finding(
                findings,
                "FAIL",
                "PG_REQUIRED_FIELD_MISSING",
                category,
                field,
                f"Required {record_name} field is missing.",
                f"Add `{field}` exactly once to the {record_name}.",
            )
        elif count > 1:
            add_finding(
                findings,
                "FAIL",
                "PG_REQUIRED_FIELD_DUPLICATE",
                category,
                field,
                f"Required {record_name} field appears more than once.",
                (
                    f"Keep exactly one `{field}` value; duplicate governance "
                    "state is ambiguous and fails closed."
                ),
            )
    return counts


def check_exact_true_gate(
    merge_section: str,
    findings: list[dict[str, Any]],
    field: str,
) -> None:
    value = raw_field_value(merge_section, field)
    if value is None:
        return
    if value.strip() not in TRUE_VALUES:
        add_finding(
            findings,
            "FAIL",
            "PG_GATE_NOT_TRUE",
            "policy_gate",
            field,
            f"`{field}` is not exactly true.",
            f"Set `{field}: true` only when that gate is verified.",
        )


def check_declared_gate_state(
    merge_section: str,
    findings: list[dict[str, Any]],
    field: str,
    allowed_values: set[str],
    *,
    reason: str,
    recommended_fix: str,
) -> None:
    value = raw_field_value(merge_section, field)
    if value is None:
        return
    if value.strip() not in allowed_values:
        add_finding(
            findings,
            "FAIL",
            "PG_BLOCKED_GATE_STATE_INVALID",
            "policy_gate",
            field,
            reason,
            recommended_fix,
        )


def check_merge_decision(
    text: str,
    findings: list[dict[str, Any]],
    *,
    mode: str,
) -> None:
    merge_section = section(text, "Merge Decision")
    if not merge_section:
        return

    field_counts = required_field_shape(
        merge_section,
        MERGE_DECISION_REQUIRED_FIELDS,
        findings,
        category="merge_decision_record",
        record_name="Merge Decision",
    )
    for field in MERGE_DECISION_REQUIRED_FIELDS:
        if field_counts[field] != 1 or field == "validation_claim_source":
            continue
        normalized = (
            (raw_field_value(merge_section, field) or "").strip()
            if field in DECISION_STATE_FIELDS
            else normalized_bool_text(field_value(merge_section, field))
        )
        if field == "reason" and normalized in INVALID_REASON_VALUES:
            add_finding(
                findings,
                "FAIL",
                "PG_REASON_NON_MATERIAL",
                "merge_decision_record",
                field,
                "Merge Decision reason is generic decision-state text, not judgment.",
                (
                    "Name the relevant evidence, limits, and unresolved risk; "
                    "do not use values such as `passed`, `all good`, or "
                    "`merge_allowed` as the reason."
                ),
            )
        elif (
            field not in DECISION_STATE_FIELDS
            and normalized in NON_SPECIFIC_REQUIRED_VALUES
        ):
            add_finding(
                findings,
                "FAIL",
                "PG_REQUIRED_FIELD_NON_MATERIAL",
                "merge_decision_record",
                field,
                "Required Merge Decision field is empty, unknown, pending, or false-like.",
                f"Set `{field}` to a concrete policy-supported value or keep the PR human-gated.",
            )

    if field_counts["validation_claim_source"] == 1:
        parent_value = field_value(merge_section, "validation_claim_source")
        if normalized_bool_text(parent_value):
            add_finding(
                findings,
                "FAIL",
                "PG_VALIDATION_SOURCE_NOT_OBJECT",
                "merge_decision_record",
                "validation_claim_source",
                "Validation claim source must be a nested object, not a scalar.",
                (
                    "Leave `validation_claim_source:` empty on its own line and "
                    "provide exactly the nested `local_doctor` and `ci` fields."
                ),
            )

        block_lines = field_block_lines(
            merge_section,
            "validation_claim_source",
        ) or []
        material_lines = [
            line
            for line in block_lines
            if line.strip() and not line.lstrip().startswith("#")
        ]
        child_indents = {
            len(re.match(r"^[ \t]*", line).group(0).replace("\t", "    "))
            for line in material_lines
        }
        if len(material_lines) != 2 or len(child_indents) != 1:
            add_finding(
                findings,
                "FAIL",
                "PG_VALIDATION_SOURCE_SHAPE_INVALID",
                "merge_decision_record",
                "validation_claim_source",
                "Validation claim source nested object has an invalid shape.",
                (
                    "Provide exactly two direct child fields at the same "
                    "indentation: `local_doctor` and `ci`."
                ),
            )
        validation_claim_source = "\n".join(block_lines)
        for field in ("local_doctor", "ci"):
            count = line_field_count(validation_claim_source, field)
            if count != 1:
                add_finding(
                    findings,
                    "FAIL",
                    "PG_VALIDATION_SOURCE_FIELD_CARDINALITY",
                    "merge_decision_record",
                    f"validation_claim_source.{field}",
                    (
                        "Validation claim source field is missing."
                        if count == 0
                        else "Validation claim source field appears more than once."
                    ),
                    (
                        f"Keep exactly one `validation_claim_source.{field}` "
                        "using a canonical value."
                    ),
                )
                continue
            value = field_value(validation_claim_source, field)
            normalized = normalized_bool_text(value)
            if normalized not in VALIDATION_CLAIM_SOURCE_VALUES[field]:
                add_finding(
                    findings,
                    "FAIL",
                    "PG_VALIDATION_SOURCE_VALUE_INVALID",
                    "merge_decision_record",
                    f"validation_claim_source.{field}",
                    "Validation claim source is missing or unsupported.",
                    (
                        f"Use one of the canonical `validation_claim_source.{field}` "
                        f"values: {', '.join(sorted(VALIDATION_CLAIM_SOURCE_VALUES[field]))}."
                    ),
                )

    result_value = (
        raw_field_value(merge_section, "result")
        if field_counts["result"] == 1
        else None
    )
    result = result_value.strip() if result_value is not None else ""
    if result not in MERGE_RESULT_ALLOWED_VALUES:
        if field_counts["result"] == 1:
            add_finding(
                findings,
                "FAIL",
                "PG_RESULT_INVALID",
                "merge_decision_record",
                "result",
                "Merge Decision result is not one of the allowed values.",
                "Use `merge_allowed` or `merge_blocked`.",
            )
        result = ""

    for field in [
        "allowed_paths_checked",
        "expected_output_checked",
        "validation_evidence_checked",
    ]:
        check_exact_true_gate(merge_section, findings, field)

    if mode == "merge-decision":
        if result and result != "merge_allowed":
            add_finding(
                findings,
                "FAIL",
                "PG_STRICT_RESULT_NOT_ALLOWED",
                "policy_gate",
                "result",
                "Strict Merge Decision validation requires `result: merge_allowed`.",
                "Keep the record `merge_blocked` until every required decision gate is complete.",
            )
        for field in ["checks_passed", "human_gates_checked"]:
            check_exact_true_gate(merge_section, findings, field)
        return

    if result == "merge_allowed":
        for field in ["checks_passed", "human_gates_checked"]:
            check_exact_true_gate(merge_section, findings, field)
        return

    if result == "merge_blocked":
        for field in ["checks_passed", "human_gates_checked"]:
            check_declared_gate_state(
                merge_section,
                findings,
                field,
                BLOCKED_COHERENCE_GATE_VALUES,
                reason=(
                    f"`{field}` is not a supported state for a coherent "
                    "`merge_blocked` record."
                ),
                recommended_fix=(
                    f"Use `{field}: true`, `{field}: pending`, or "
                    f"`{field}: false`; blank and unknown states are invalid."
                ),
            )


def check_current_status_impact(text: str, findings: list[dict[str, Any]]) -> None:
    current_status_section = section(text, "Current Status Impact")
    if not current_status_section:
        return

    field_counts = required_field_shape(
        current_status_section,
        CURRENT_STATUS_IMPACT_REQUIRED_FIELDS,
        findings,
        category="current_status_impact",
        record_name="Current Status Impact",
    )

    status = (
        normalized_bool_text(field_value(current_status_section, "status"))
        if field_counts["status"] == 1
        else ""
    )
    if field_counts["status"] == 1 and status not in CURRENT_STATUS_ALLOWED_VALUES:
        add_finding(
            findings,
            "FAIL",
            "PG_STATUS_IMPACT_STATUS_INVALID",
            "current_status_impact",
            "status",
            "Current Status Impact status is missing or invalid.",
            "Use exactly one of: updated, not_applicable, deferred.",
        )

    reason = (
        field_value(current_status_section, "reason")
        if field_counts["reason"] == 1
        else None
    )
    if (
        field_counts["reason"] == 1
        and normalized_bool_text(reason) in NON_SPECIFIC_REQUIRED_VALUES
    ):
        add_finding(
            findings,
            "FAIL",
            "PG_STATUS_IMPACT_REASON_INVALID",
            "current_status_impact",
            "reason",
            "Current Status Impact reason is missing or non-specific.",
            "Explain why CURRENT_STATUS.md was updated, not applicable, or deferred.",
        )

    updated = (
        normalized_bool_text(
            field_value(current_status_section, "current_status_updated_in_this_pr")
        )
        if field_counts["current_status_updated_in_this_pr"] == 1
        else ""
    )
    if (
        status == "updated"
        and field_counts["current_status_updated_in_this_pr"] == 1
        and updated not in TRUE_VALUES
    ):
        add_finding(
            findings,
            "FAIL",
            "PG_STATUS_IMPACT_UPDATE_FALSE",
            "current_status_impact",
            "current_status_updated_in_this_pr",
            "Current Status Impact says updated, but update confirmation is not true.",
            "Set current_status_updated_in_this_pr: true only if docs/handoff/CURRENT_STATUS.md changed in this PR.",
        )

    post_merge_safe = (
        normalized_bool_text(field_value(current_status_section, "post_merge_safe"))
        if field_counts["post_merge_safe"] == 1
        else ""
    )
    if (
        status == "updated"
        and field_counts["post_merge_safe"] == 1
        and post_merge_safe not in TRUE_VALUES
    ):
        add_finding(
            findings,
            "FAIL",
            "PG_STATUS_IMPACT_NOT_POST_MERGE_SAFE",
            "current_status_impact",
            "post_merge_safe",
            "Current Status Impact says updated, but does not confirm the status is post-merge-safe.",
            "Set `post_merge_safe: true` only when CURRENT_STATUS.md remains accurate after this PR merges.",
        )

    follow_up = (
        field_value(current_status_section, "follow_up_issue")
        if field_counts["follow_up_issue"] == 1
        else None
    )
    if (
        status == "deferred"
        and field_counts["follow_up_issue"] == 1
        and normalized_bool_text(follow_up) in {"", "none", "null", "tbd", "todo"}
    ):
        add_finding(
            findings,
            "FAIL",
            "PG_STATUS_IMPACT_FOLLOWUP_MISSING",
            "current_status_impact",
            "follow_up_issue",
            "Current Status Impact is deferred without a durable follow-up path.",
            "Provide a follow-up issue or a concrete next safe action in the Handoff Report.",
        )


def check_chat_authority(text: str, findings: list[dict[str, Any]]) -> None:
    if re.search(r"\bsee\s+chat\b", text, flags=re.IGNORECASE):
        add_finding(
            findings,
            "FAIL",
            "PG_CHAT_AUTHORITY_FORBIDDEN",
            "source_of_truth",
            "see chat",
            "PR body uses chat-only authority.",
            "Replace chat-only authority with a GitHub issue, PR, or repository document reference.",
        )


def check_pr_body(text: str, *, mode: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    visible_headings = markdown_heading_occurrences(text)
    for required in PR_REQUIRED_HEADINGS:
        count = visible_headings.count(required)
        if count == 0:
            add_finding(
                findings,
                "FAIL",
                "PG_SECTION_MISSING",
                "pr_structure",
                required,
                f"Required PR section `{required}` is missing.",
                f"Add `## {required}` to the PR body.",
            )
        elif count > 1:
            add_finding(
                findings,
                "FAIL",
                "PG_SECTION_DUPLICATE",
                "pr_structure",
                required,
                f"Required PR section `{required}` appears more than once.",
                (
                    f"Keep exactly one `## {required}` section; duplicate "
                    "governance sections are ambiguous and fail closed."
                ),
            )
    check_chat_authority(strip_html_comments(text), findings)
    check_current_status_impact(text, findings)
    check_merge_decision(text, findings, mode=mode)
    return findings


def proof_boundary(mode: str) -> str:
    if mode == "body-coherence":
        return (
            "A body-coherence pass proves only that the PR body is complete and "
            "mechanically coherent for its declared Merge Decision."
        )
    return (
        "A merge-decision pass proves only that the Merge Decision Record's "
        "merge_allowed claim is mechanically supported by the checked body "
        "fields."
    )


def output_findings(
    findings: list[dict[str, Any]],
    *,
    mode: str,
    declared_result: str,
    evidence_source: str,
    as_json: bool,
    mechanically_checked: list[str] | None = None,
    not_checked: list[str] | None = None,
    boundary: str | None = None,
) -> int:
    blocking = [finding for finding in findings if finding["blocks_merge_eligibility"]]
    result = "fail" if blocking else "pass"
    boundary = boundary or proof_boundary(mode)
    checked_surfaces = mechanically_checked or [
        "required PR body sections",
        "Current Status Impact field shape and consistency",
        f"{mode} Merge Decision field shape and gate tokens",
        "chat-only authority phrase rejection",
    ]
    unchecked_surfaces = not_checked or [
        "PR diff or changed-path scope",
        "CI, project tests, or evidence truth",
        "human approval, current-head approval, or merge authority",
    ]
    payload = checked_validation_result({
        "result": result,
        "mode": mode,
        "declared_merge_decision": declared_result,
        "merge_eligibility_inferred": False,
        "low_risk_inferred": False,
        "human_approval_inferred": False,
        "findings": findings,
    },
        evidence_source=evidence_source,
        mechanically_checked=checked_surfaces,
        not_checked=unchecked_surfaces,
        proof_boundary=boundary,
    )
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        if not findings:
            print(f"Policy gate {mode} passed. {boundary}")
            if mode == "body-coherence" and declared_result == "merge_blocked":
                print("The declared Merge Decision remains merge_blocked.")
        else:
            for finding in findings:
                location = (
                    finding.get("field")
                    or finding.get("path")
                    or "finding"
                )
                print(
                    f"{finding['severity']}: [{finding['category']}] {location} - "
                    f"{finding['reason']} Fix: {finding['recommended_fix']}"
                )
            print(f"Policy gate {mode} result: {result}. {boundary}")
        print(
            "Full PR merge eligibility, low-risk status, and human approval "
            "were not inferred."
        )
    return 0 if payload["result"] == "pass" else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only fail-closed ASGK PR-body checker with explicit body "
            "coherence and Merge Decision proof boundaries."
        )
    )
    parser.add_argument("--pr-body", required=True, help="Path to a PR body markdown file.")
    parser.add_argument(
        "--mode",
        choices=sorted(VALIDATION_MODES),
        default="merge-decision",
        help=(
            "Validation proof layer. Direct CLI calls default to strict "
            "merge-decision."
        ),
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument(
        "--evidence-source",
        choices=["supplied_pr_body_file", "supplied_github_event_file"],
        default="supplied_pr_body_file",
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args()

    try:
        text = Path(args.pr_body).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        finding = make_finding(
            "PG_BODY_READ_FAILED",
            f"could not read PR body file: {exc}",
            path=args.pr_body,
            blocking=True,
            severity="FAIL",
            category="input",
            recommended_fix="Provide one readable UTF-8 PR body file.",
            blocks_merge_eligibility=True,
        )
        return output_findings(
            [finding],
            mode=args.mode,
            declared_result="",
            evidence_source=args.evidence_source,
            as_json=args.json,
            mechanically_checked=["PR body file readability"],
            not_checked=[
                "required PR body sections",
                "Current Status Impact field shape and consistency",
                f"{args.mode} Merge Decision field shape and gate tokens",
                "chat-only authority phrase rejection",
                "PR diff, CI, project tests, or evidence truth",
                "human approval, current-head approval, or merge authority",
            ],
            boundary=(
                "Only PR body file readability was checked; no PR-body policy "
                "evaluation ran because the supplied file could not be read."
            ),
        )
    findings = check_pr_body(text, mode=args.mode)
    merge_section = section(text, "Merge Decision")
    declared_result = (raw_field_value(merge_section, "result") or "").strip()
    return output_findings(
        findings,
        mode=args.mode,
        declared_result=declared_result,
        evidence_source=args.evidence_source,
        as_json=args.json,
    )


if __name__ == "__main__":
    raise SystemExit(main())
