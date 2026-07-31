"""Compact handoff validation built on the canonical core evaluator."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from asgk_lib.common import ROOT, field_value, markdown_section, normalize_repo_path, rel
from asgk_lib.handoff import (
    COMPACT_HANDOFF_ROOT,
    evaluate_handoff_file,
    is_material_handoff_text,
)
from asgk_lib.status_policy import (
    CLOSEOUT_PRE_MERGE_NEXT_ACTION_PATTERNS,
    CURRENT_STATUS_IMPACT_ALLOWED_VALUES,
    CURRENT_STATUS_IMPACT_REQUIRED_FIELDS,
)

FOLLOW_UP_ISSUE_PATTERN = r"^(?:none|#[0-9]+)(?![\s\S])"


def _finding(code: str, field: str, reason: str) -> dict[str, object]:
    return {
        "code": code,
        "field": field,
        "reason": reason,
        "blocking": True,
    }


def valid_follow_up_issue(value: object) -> bool:
    return (
        isinstance(value, str)
        and re.fullmatch(FOLLOW_UP_ISSUE_PATTERN, value) is not None
    )


def numbered_ref_matches(active_value: str | None, completed_ref: str) -> bool:
    if not active_value or not completed_ref:
        return False

    def number(value: str) -> int | None:
        stripped = value.strip()
        github_ref = re.match(
            r"https://github[.]com/[^/\s]+/[^/\s]+/"
            r"(?:issues|pull)/([0-9]+)(?:\b|/)",
            stripped,
        )
        if github_ref:
            return int(github_ref.group(1))
        hash_ref = re.match(r"#([0-9]+)\b", stripped)
        if hash_ref:
            return int(hash_ref.group(1))
        bare_ref = re.fullmatch(r"([0-9]+)", stripped)
        return int(bare_ref.group(1)) if bare_ref else None

    active_number = number(active_value)
    completed_number = number(completed_ref)
    if active_number and completed_number:
        return active_number == completed_number
    return active_value.strip() == completed_ref.strip()


def branch_ref_matches(active_value: str | None, completed_ref: str) -> bool:
    return bool(
        active_value
        and completed_ref
        and active_value.strip() == completed_ref.strip()
    )


def _impact_findings(packet: dict[str, object]) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    impact = packet.get("current_status_impact")
    if not isinstance(impact, dict):
        return [
            _finding(
                "CH_CURRENT_STATUS_IMPACT_MISSING",
                "current_status_impact",
                "compact handoff requires a current_status_impact mapping",
            )
        ]

    for field in CURRENT_STATUS_IMPACT_REQUIRED_FIELDS:
        if field not in impact:
            findings.append(
                _finding(
                    "CH_CURRENT_STATUS_IMPACT_FIELD_MISSING",
                    f"current_status_impact.{field}",
                    "required current-status impact field is missing",
                )
            )

    unknown = sorted(set(impact) - set(CURRENT_STATUS_IMPACT_REQUIRED_FIELDS))
    for field in unknown:
        findings.append(
            _finding(
                "CH_CURRENT_STATUS_IMPACT_FIELD_INVALID",
                f"current_status_impact.{field}",
                "field is not part of the current-status impact contract",
            )
        )

    status = impact.get("status")
    status_valid = False
    if "status" in impact and (
        not isinstance(status, str)
        or status not in CURRENT_STATUS_IMPACT_ALLOWED_VALUES
    ):
        findings.append(
            _finding(
                "CH_CURRENT_STATUS_IMPACT_STATUS_INVALID",
                "current_status_impact.status",
                "status must be updated, not_applicable, or deferred",
            )
        )
    elif "status" in impact:
        status_valid = True

    reason = impact.get("reason")
    if "reason" in impact and not is_material_handoff_text(reason):
        findings.append(
            _finding(
                "CH_CURRENT_STATUS_IMPACT_REASON_INVALID",
                "current_status_impact.reason",
                "reason must be a material string",
            )
        )

    updated = impact.get("current_status_updated_in_this_pr")
    updated_valid = isinstance(updated, bool)
    if "current_status_updated_in_this_pr" in impact and not updated_valid:
        findings.append(
            _finding(
                "CH_CURRENT_STATUS_IMPACT_FIELD_INVALID",
                "current_status_impact.current_status_updated_in_this_pr",
                "field must be a boolean",
            )
        )

    post_merge_safe = impact.get("post_merge_safe")
    post_merge_safe_valid = (
        isinstance(post_merge_safe, bool)
        or post_merge_safe == "not_applicable"
    )
    if "post_merge_safe" in impact and not post_merge_safe_valid:
        findings.append(
            _finding(
                "CH_CURRENT_STATUS_IMPACT_FIELD_INVALID",
                "current_status_impact.post_merge_safe",
                "field must be a boolean or not_applicable",
            )
        )

    follow_up = impact.get("follow_up_issue")
    if "follow_up_issue" in impact and not valid_follow_up_issue(follow_up):
        findings.append(
            _finding(
                "CH_CURRENT_STATUS_IMPACT_FIELD_INVALID",
                "current_status_impact.follow_up_issue",
                "field must be exactly none or one #<number> issue reference",
            )
        )

    if status_valid and updated_valid and post_merge_safe_valid and status == "updated":
        if updated is not True or post_merge_safe is not True:
            findings.append(
                _finding(
                    "CH_CURRENT_STATUS_IMPACT_INCONSISTENT",
                    "current_status_impact",
                    "updated requires both update and post-merge-safe booleans to be true",
                )
            )
    elif status_valid and updated_valid and status in {"not_applicable", "deferred"} and updated is True:
        findings.append(
            _finding(
                "CH_CURRENT_STATUS_IMPACT_INCONSISTENT",
                "current_status_impact.current_status_updated_in_this_pr",
                f"{status} cannot claim the status file was updated in this PR",
            )
        )

    return findings


def compact_handoff_check(
    handoff_file: str | Path,
    current_status_file: str | Path,
    *,
    completed_issues: list[str],
    completed_prs: list[str],
    completed_branches: list[str],
) -> tuple[str, dict[str, object]]:
    core_result, core_report, packet = evaluate_handoff_file(
        handoff_file,
        root_name=COMPACT_HANDOFF_ROOT,
        allowed_extra_fields={"current_status_impact"},
    )

    base_output: dict[str, object] = {
        **core_report,
        "handoff_file": normalize_repo_path(str(handoff_file)),
        "current_status": normalize_repo_path(str(current_status_file)),
        "completed_refs_supplied": {
            "issues": completed_issues,
            "prs": completed_prs,
            "branches": completed_branches,
        },
        "low_risk_inferred": False,
    }
    if core_result != "pass" or packet is None:
        base_output["freshness_checked"] = False
        base_output["not_checked"] = [
            *list(core_report.get("not_checked", [])),
            "current-status impact shape and consistency",
            "CURRENT_STATUS file existence, status-check, or supplied completed refs",
        ]
        return "fail", base_output

    findings = _impact_findings(packet)
    if findings:
        return "fail", {
            **base_output,
            "result": "fail",
            "freshness_checked": False,
            "mechanically_checked": [
                *list(core_report.get("mechanically_checked", [])),
                "current_status_impact required fields, types, and status consistency",
            ],
            "not_checked": [
                *list(core_report.get("not_checked", [])),
                "CURRENT_STATUS file existence, status-check, or supplied completed refs",
                "live GitHub state, human approval, PR readiness, or merge authority",
            ],
            "proof_boundary": (
                f"{core_report['proof_boundary']} The compact impact block was "
                "evaluated and found structurally invalid or internally "
                "inconsistent; CURRENT_STATUS freshness was therefore not checked."
            ),
            "findings": findings,
        }

    status_path = rel(current_status_file)
    status_valid = False
    status_check_ran = False
    if not status_path.exists():
        findings.append(
            _finding(
                "CH_CURRENT_STATUS_FILE_MISSING",
                "current_status",
                f"current-status file does not exist: {current_status_file}",
            )
        )
        status_text = ""
    elif not status_path.is_file():
        findings.append(
            _finding(
                "CH_CURRENT_STATUS_CHECK_FAILED",
                "current_status",
                f"current-status path is not a readable file: {current_status_file}",
            )
        )
        status_text = ""
    else:
        try:
            status_text = status_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            findings.append(
                _finding(
                    "CH_CURRENT_STATUS_CHECK_FAILED",
                    "current_status",
                    f"could not read current-status file: {exc}",
                )
            )
            status_text = ""
        else:
            status_result = subprocess.run(
                [sys.executable, "scripts/asgk.py", "status-check", "--file", str(status_path)],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            status_check_ran = True
            if status_result.returncode != 0:
                findings.append(
                    _finding(
                        "CH_CURRENT_STATUS_CHECK_FAILED",
                        "current_status",
                        "current-status file failed status-check",
                    )
                )
            else:
                status_valid = True

    if not status_valid:
        checked_status_surfaces = [
            "CURRENT_STATUS path existence, file type, and readability",
        ]
        unchecked_status_surfaces: list[str] = []
        if status_check_ran:
            checked_status_surfaces.append("CURRENT_STATUS local status-check result")
        else:
            unchecked_status_surfaces.append("CURRENT_STATUS local status-check result")
        return "fail", {
            **base_output,
            "result": "fail",
            "freshness_checked": False,
            "mechanically_checked": [
                *list(core_report.get("mechanically_checked", [])),
                "current_status_impact required fields, types, and status consistency",
                *checked_status_surfaces,
            ],
            "not_checked": [
                *list(core_report.get("not_checked", [])),
                *unchecked_status_surfaces,
                "caller-supplied completed issue, PR, and branch references",
                "CURRENT_STATUS pre-merge next-action patterns",
                "live GitHub state, human approval, PR readiness, or merge authority",
            ],
            "proof_boundary": (
                f"{core_report['proof_boundary']} The compact impact block passed, "
                "but full freshness was not checked because CURRENT_STATUS was "
                "missing or failed its local structural check."
            ),
            "findings": findings,
        }

    if status_valid:
        active_work = markdown_section(status_text, "Active work")
        next_safe_action_section = markdown_section(status_text, "Next safe action")
        active_issue = field_value(active_work, "issue")
        active_pr = field_value(active_work, "pr")
        active_branch = field_value(active_work, "branch")
        for issue in completed_issues:
            if numbered_ref_matches(active_issue, issue):
                findings.append(
                    _finding(
                        "CH_STALE_COMPLETED_ISSUE",
                        "current_status.active_work",
                        f"completed issue still appears in active work: {issue}",
                    )
                )
        for pr in completed_prs:
            if numbered_ref_matches(active_pr, pr):
                findings.append(
                    _finding(
                        "CH_STALE_COMPLETED_PR",
                        "current_status.active_work",
                        f"completed PR still appears in active work: {pr}",
                    )
                )
        for branch in completed_branches:
            if branch_ref_matches(active_branch, branch):
                findings.append(
                    _finding(
                        "CH_STALE_COMPLETED_BRANCH",
                        "current_status.active_work",
                        f"completed branch still appears in active work: {branch}",
                    )
                )

        for pattern in CLOSEOUT_PRE_MERGE_NEXT_ACTION_PATTERNS:
            if re.search(pattern, next_safe_action_section, flags=re.IGNORECASE):
                findings.append(
                    _finding(
                        "CH_NEXT_SAFE_ACTION_STALE",
                        "current_status.next_safe_action",
                        "next safe action appears to describe pre-merge closeout work: "
                        f"{pattern}",
                    )
                )

    result = "fail" if findings else "pass"
    freshness_boundary = (
        (
            f"{core_report['proof_boundary']} Compact freshness checks additionally "
            "prove only local consistency with the supplied CURRENT_STATUS file and "
            "caller-supplied completed references."
        )
        if result == "pass"
        else (
            f"{core_report['proof_boundary']} Compact freshness checks evaluated "
            "the supplied CURRENT_STATUS file and caller-supplied completed "
            "references and found a local inconsistency. No live GitHub state, "
            "human approval, PR readiness, or merge authority was established."
        )
    )
    return result, {
        **base_output,
        "result": result,
        "freshness_checked": True,
        "mechanically_checked": [
            *list(core_report.get("mechanically_checked", [])),
            "current_status_impact required fields, types, and status consistency",
            "CURRENT_STATUS local status-check result",
            "caller-supplied completed issue, PR, and branch references",
        ],
        "not_checked": [
            *list(core_report.get("not_checked", [])),
            "live GitHub state of completed or active references",
            "semantic correctness of current-status impact classification",
            "human approval, PR readiness, or merge authority",
        ],
        "proof_boundary": freshness_boundary,
        "findings": findings,
    }
