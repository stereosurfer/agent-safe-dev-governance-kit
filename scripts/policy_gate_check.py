#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from asgk_lib.common import field_value, markdown_headings, markdown_section as section

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
    "result",
    "reason",
]

CURRENT_STATUS_ALLOWED_VALUES = {"updated", "not_applicable", "deferred"}
MERGE_RESULT_ALLOWED_VALUES = {"merge_allowed", "merge_blocked"}
TRUE_VALUES = {"true"}
UNKNOWN_VALUES = {"", "pending", "unknown", "false", "no", "null", "none", "tbd", "todo"}
BODY_COHERENCE_MODE = "body-coherence"
MERGE_ELIGIBILITY_MODE = "merge-eligibility"
POLICY_GATE_MODES = {BODY_COHERENCE_MODE, MERGE_ELIGIBILITY_MODE}
RESULT_SENSITIVE_GATE_FIELDS = {"checks_passed", "human_gates_checked"}
EXACT_TRUE_GATE_FIELDS = {"allowed_paths_checked", "expected_output_checked"}
BLOCKED_BODY_GATE_VALUES = {*TRUE_VALUES, "pending", "false"}


def normalized_bool_text(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip().strip('"').strip("'").lower()


def add_finding(
    findings: list[dict[str, Any]],
    severity: str,
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
            "category": category,
            "field": field,
            "reason": reason,
            "recommended_fix": recommended_fix,
            "blocks_merge_eligibility": blocks_merge_eligibility,
        }
    )


def check_merge_decision(
    text: str,
    findings: list[dict[str, Any]],
    *,
    mode: str,
) -> None:
    merge_section = section(text, "Merge Decision")
    if not merge_section:
        add_finding(
            findings,
            "FAIL",
            "merge_decision_record",
            "Merge Decision",
            "Merge Decision section is missing.",
            "Add a Merge Decision section using docs/control/MERGE_DECISION_RECORD.md.",
        )
        return

    result = normalized_bool_text(field_value(merge_section, "result"))
    blocked_body_coherence = mode == BODY_COHERENCE_MODE and result == "merge_blocked"

    for field in MERGE_DECISION_REQUIRED_FIELDS:
        value = field_value(merge_section, field)
        if value is None:
            add_finding(
                findings,
                "FAIL",
                "merge_decision_record",
                field,
                "Required Merge Decision field is missing.",
                f"Add `{field}` to the Merge Decision Record.",
            )
            continue

        normalized = normalized_bool_text(value)
        if field in RESULT_SENSITIVE_GATE_FIELDS:
            allowed_values = BLOCKED_BODY_GATE_VALUES if blocked_body_coherence else TRUE_VALUES
            if normalized not in allowed_values:
                allowed_description = (
                    "`true`, `pending`, or `false`"
                    if blocked_body_coherence
                    else "`true`"
                )
                add_finding(
                    findings,
                    "FAIL",
                    "policy_gate",
                    field,
                    f"`{field}` is not valid for `{result or 'missing result'}` in {mode} mode.",
                    f"Use {allowed_description}; blank or `unknown` is never valid.",
                )
        elif field in EXACT_TRUE_GATE_FIELDS:
            if normalized not in TRUE_VALUES:
                add_finding(
                    findings,
                    "FAIL",
                    "policy_gate",
                    field,
                    f"`{field}` is not mechanically confirmed true.",
                    f"Set `{field}: true` before PR submission.",
                )
        elif normalized in UNKNOWN_VALUES:
            add_finding(
                findings,
                "FAIL",
                "merge_decision_record",
                field,
                "Required Merge Decision field is empty, unknown, pending, or false-like.",
                f"Set `{field}` to a concrete policy-supported value or keep the PR human-gated.",
            )

    if result not in MERGE_RESULT_ALLOWED_VALUES:
        add_finding(
            findings,
            "FAIL",
            "merge_decision_record",
            "result",
            "Merge Decision result is not one of the allowed values.",
            "Use `merge_allowed` or `merge_blocked`.",
        )
    elif mode == MERGE_ELIGIBILITY_MODE and result != "merge_allowed":
        add_finding(
            findings,
            "FAIL",
            "policy_gate",
            "result",
            "Strict merge-eligibility mode requires `result: merge_allowed`.",
            "Keep the PR blocked until every required check and human gate is complete, then update the durable Merge Decision.",
        )


def check_current_status_impact(text: str, findings: list[dict[str, Any]]) -> None:
    current_status_section = section(text, "Current Status Impact")
    if not current_status_section:
        add_finding(
            findings,
            "FAIL",
            "current_status_impact",
            "Current Status Impact",
            "Current Status Impact section is missing.",
            "Add Current Status Impact and classify it as updated, not_applicable, or deferred.",
        )
        return

    status = normalized_bool_text(field_value(current_status_section, "status"))
    if status not in CURRENT_STATUS_ALLOWED_VALUES:
        add_finding(
            findings,
            "FAIL",
            "current_status_impact",
            "status",
            "Current Status Impact status is missing or invalid.",
            "Use exactly one of: updated, not_applicable, deferred.",
        )

    reason = field_value(current_status_section, "reason")
    if reason is None or normalized_bool_text(reason) in UNKNOWN_VALUES:
        add_finding(
            findings,
            "FAIL",
            "current_status_impact",
            "reason",
            "Current Status Impact reason is missing or non-specific.",
            "Explain why CURRENT_STATUS.md was updated, not applicable, or deferred.",
        )

    updated = normalized_bool_text(field_value(current_status_section, "current_status_updated_in_this_pr"))
    if status == "updated" and updated not in TRUE_VALUES:
        add_finding(
            findings,
            "FAIL",
            "current_status_impact",
            "current_status_updated_in_this_pr",
            "Current Status Impact says updated, but update confirmation is not true.",
            "Set current_status_updated_in_this_pr: true only if docs/handoff/CURRENT_STATUS.md changed in this PR.",
        )

    post_merge_safe = normalized_bool_text(field_value(current_status_section, "post_merge_safe"))
    if status == "updated" and post_merge_safe not in TRUE_VALUES:
        add_finding(
            findings,
            "FAIL",
            "current_status_impact",
            "post_merge_safe",
            "Current Status Impact says updated, but does not confirm the status is post-merge-safe.",
            "Set `post_merge_safe: true` only when CURRENT_STATUS.md remains accurate after this PR merges.",
        )

    follow_up = field_value(current_status_section, "follow_up_issue")
    if status == "deferred" and (follow_up is None or normalized_bool_text(follow_up) in {"", "none", "null", "tbd", "todo"}):
        add_finding(
            findings,
            "FAIL",
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
            "source_of_truth",
            "see chat",
            "PR body uses chat-only authority.",
            "Replace chat-only authority with a GitHub issue, PR, or repository document reference.",
        )


def check_pr_body(text: str, *, mode: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    headings = markdown_headings(text)
    for required in ["Task Reference", "Scope Boundaries", "Current Status Impact", "Merge Decision", "Handoff Report"]:
        if required not in headings:
            add_finding(
                findings,
                "FAIL",
                "pr_structure",
                required,
                f"Required PR section `{required}` is missing.",
                f"Add `## {required}` to the PR body.",
            )
    check_chat_authority(text, findings)
    check_current_status_impact(text, findings)
    check_merge_decision(text, findings, mode=mode)
    return findings


def output_findings(
    findings: list[dict[str, Any]],
    *,
    as_json: bool,
    mode: str,
    declared_result: str,
) -> int:
    blocking = [finding for finding in findings if finding["blocks_merge_eligibility"]]
    result = "fail" if blocking else "pass"
    payload = {
        "result": result,
        "mode": mode,
        "declared_merge_decision": declared_result,
        "merge_eligibility_inferred": False,
        "low_risk_inferred": False,
        "findings": findings,
    }
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        if not findings:
            if mode == BODY_COHERENCE_MODE and declared_result == "merge_blocked":
                print(
                    "PR body coherence check passed for submission. "
                    "The declared Merge Decision remains merge_blocked; "
                    "no merge eligibility or low-risk status was inferred."
                )
            else:
                print(
                    f"Policy gate check passed in {mode} mode. "
                    "Full PR merge eligibility and low-risk status were not inferred."
                )
        else:
            for finding in findings:
                print(
                    f"{finding['severity']}: [{finding['category']}] {finding['field']} - "
                    f"{finding['reason']} Fix: {finding['recommended_fix']}"
                )
            print(
                f"Policy gate check result: {result} in {mode} mode. "
                "No merge eligibility or low-risk status was inferred."
            )
    return 1 if blocking else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only ASGK PR body checker with strict merge eligibility by default "
            "and an explicit body-coherence mode for truthful blocked drafts."
        )
    )
    parser.add_argument("--pr-body", required=True, help="Path to a PR body markdown file.")
    parser.add_argument(
        "--mode",
        choices=sorted(POLICY_GATE_MODES),
        default=MERGE_ELIGIBILITY_MODE,
        help=(
            "Use body-coherence only for truthful PR submission checks. "
            "The default merge-eligibility mode stays strict."
        ),
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    text = Path(args.pr_body).read_text(encoding="utf-8")
    findings = check_pr_body(text, mode=args.mode)
    merge_section = section(text, "Merge Decision")
    declared_result = normalized_bool_text(field_value(merge_section, "result"))
    return output_findings(
        findings,
        as_json=args.json,
        mode=args.mode,
        declared_result=declared_result,
    )


if __name__ == "__main__":
    raise SystemExit(main())
