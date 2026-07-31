from __future__ import annotations

import json
import subprocess

from asgk_lib.common import ROOT, normalize_repo_path
from asgk_lib.validation_result import checked_validation_result, make_finding


def git_output(args: list[str]) -> tuple[int, str]:
    try:
        result = subprocess.run(
            args,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except OSError as exc:
        return 127, f"could not execute {args[0]}: {exc}"
    return result.returncode, result.stdout.strip()


def _normalized_lines(output: str) -> list[str]:
    return [normalize_repo_path(line) for line in output.splitlines() if normalize_repo_path(line)]


def live_workspace_state(base_ref: str) -> dict[str, object]:
    branch_code, branch_output = git_output(["git", "branch", "--show-current"])
    branch = branch_output if branch_code == 0 else ""

    upstream_code, upstream_output = git_output(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    upstream = upstream_output if upstream_code == 0 else ""

    untracked_code, untracked_output = git_output(["git", "ls-files", "--others", "--exclude-standard"])
    untracked_paths = _normalized_lines(untracked_output) if untracked_code == 0 else []

    diff_code, diff_output = git_output(["git", "diff", "--name-only"])
    cached_code, cached_output = git_output(["git", "diff", "--cached", "--name-only"])
    changed_paths = sorted({
        path
        for output in (
            diff_output if diff_code == 0 else "",
            cached_output if cached_code == 0 else "",
            untracked_output if untracked_code == 0 else "",
        )
        for path in _normalized_lines(output)
    })

    merged_into_base = False
    merged_check_error = ""
    if branch:
        merged_code, merged_output = git_output(["git", "branch", "--merged", base_ref, "--format", "%(refname:short)"])
        if merged_code == 0:
            merged_into_base = branch in {
                line.strip()
                for line in merged_output.splitlines()
                if line.strip()
            }
        else:
            merged_check_error = merged_output or f"git branch --merged {base_ref} failed"

    return {
        "branch": branch,
        "upstream": upstream,
        "base_ref": base_ref,
        "merged_into_base": merged_into_base,
        "merged_check_error": merged_check_error,
        "untracked_paths": untracked_paths,
        "changed_paths": changed_paths,
        "lookup_errors": {
            "branch": branch_output if branch_code != 0 else "",
            "upstream": upstream_output if upstream_code != 0 else "",
            "untracked": untracked_output if untracked_code != 0 else "",
            "diff": diff_output if diff_code != 0 else "",
            "cached_diff": cached_output if cached_code != 0 else "",
        },
    }


def workspace_state_shape_finding(
    payload: dict[str, object],
) -> dict[str, object] | None:
    required_types: dict[str, type] = {
        "branch": str,
        "upstream": str,
        "base_ref": str,
        "merged_into_base": bool,
        "merged_check_error": str,
        "untracked_paths": list,
        "changed_paths": list,
    }
    problems: list[str] = []
    for field, expected_type in required_types.items():
        if field not in payload:
            problems.append(f"missing {field}")
            continue
        value = payload[field]
        if expected_type is bool:
            valid_type = type(value) is bool
        else:
            valid_type = isinstance(value, expected_type)
        if not valid_type:
            problems.append(
                f"{field} must be {expected_type.__name__}"
            )
    for field in ("untracked_paths", "changed_paths"):
        value = payload.get(field)
        if isinstance(value, list) and any(
            not isinstance(item, str) or not item.strip()
            for item in value
        ):
            problems.append(f"{field} must contain only nonblank strings")
    if "branch_is_stale" in payload and type(payload["branch_is_stale"]) is not bool:
        problems.append("branch_is_stale must be bool when present")
    if "lookup_errors" in payload:
        lookup_errors = payload["lookup_errors"]
        if not isinstance(lookup_errors, dict):
            problems.append("lookup_errors must be an object when present")
        else:
            for field in ("branch", "upstream", "untracked", "diff", "cached_diff"):
                if field not in lookup_errors:
                    problems.append(f"missing lookup_errors.{field}")
                elif not isinstance(lookup_errors[field], str):
                    problems.append(f"lookup_errors.{field} must be str")
    if not problems:
        return None
    return make_finding(
        "WS_PAYLOAD_SHAPE_INVALID",
        "workspace-state payload shape is invalid: " + "; ".join(problems),
        field="payload",
        blocking=True,
        severity="FAIL",
        recommended_fix=(
            "Provide the canonical workspace-state fields with their supported "
            "types, or rerun without --json-file for a live observation."
        ),
    )


def workspace_state_findings(payload: dict[str, object], *, main_branch: str) -> list[dict[str, object]]:
    shape_finding = workspace_state_shape_finding(payload)
    if shape_finding is not None:
        return [shape_finding]
    findings: list[dict[str, object]] = []

    def warn(
        code: str,
        field: str,
        reason: str,
        fix: str,
        **extra: object,
    ) -> None:
        findings.append(make_finding(
            code,
            reason,
            field=field,
            blocking=False,
            severity="WARN",
            recommended_fix=fix,
            **extra,
        ))

    branch = str(payload.get("branch") or "")
    base_ref = str(payload.get("base_ref") or "origin/main")
    upstream = str(payload.get("upstream") or "")
    merged_into_base = bool(payload.get("merged_into_base"))
    merged_check_error = str(payload.get("merged_check_error") or "")
    untracked = payload.get("untracked_paths")
    untracked_paths = [str(path) for path in untracked] if isinstance(untracked, list) else []
    changed = payload.get("changed_paths")
    changed_paths = [str(path) for path in changed] if isinstance(changed, list) else []
    branch_is_stale = bool(payload.get("branch_is_stale"))
    if "branch_is_stale" not in payload:
        branch_is_stale = bool(branch and branch != main_branch and merged_into_base and not changed_paths)

    if not branch:
        warn(
            "WS_BRANCH_UNAVAILABLE",
            "branch",
            "Current checkout appears to be detached or branch name is unavailable.",
            "Confirm the intended work branch before editing files.",
        )
    elif branch_is_stale:
        warn(
            "WS_BRANCH_STALE",
            "branch",
            f"Current branch `{branch}` is already merged into `{base_ref}`.",
            "Switch to main or create a fresh issue branch before starting a new work unit.",
        )

    if branch != main_branch and not upstream:
        warn(
            "WS_UPSTREAM_MISSING",
            "upstream",
            f"Current branch `{branch or '<detached>'}` has no upstream branch recorded.",
            "Confirm branch tracking before relying on remote status.",
        )

    if merged_check_error:
        warn(
            "WS_MERGED_LOOKUP_FAILED",
            "merged_into_base",
            f"Could not check whether the branch is merged into `{base_ref}`: {merged_check_error}",
            "Fetch the base ref or run the check again with a valid --base-ref.",
        )

    lookup_errors = payload.get("lookup_errors")
    if isinstance(lookup_errors, dict):
        lookup_codes = {
            "branch": "WS_BRANCH_LOOKUP_FAILED",
            "upstream": "WS_UPSTREAM_LOOKUP_FAILED",
            "untracked": "WS_UNTRACKED_LOOKUP_FAILED",
            "diff": "WS_DIFF_LOOKUP_FAILED",
            "cached_diff": "WS_CACHED_DIFF_LOOKUP_FAILED",
        }
        for key, code in lookup_codes.items():
            error = str(lookup_errors.get(key) or "").strip()
            if error:
                warn(
                    code,
                    f"lookup_errors.{key}",
                    f"Workspace `{key}` lookup failed: {error}",
                    "Rerun from a valid Git worktree before relying on workspace state.",
                )

    if untracked_paths:
        warn(
            "WS_UNTRACKED_PATHS",
            "untracked_paths",
            f"Workspace has {len(untracked_paths)} untracked path(s).",
            "Leave unrelated local artifacts alone, or intentionally move/remove them outside this work unit before validating changed-path scope.",
            paths=untracked_paths,
        )

    return findings


def print_workspace_state_result(
    payload: dict[str, object],
    findings: list[dict[str, object]],
    *,
    as_json: bool,
    strict: bool,
    expect_warnings: bool,
    evidence_source: str,
) -> int:
    shape_invalid = any(
        finding.get("code") == "WS_PAYLOAD_SHAPE_INVALID"
        for finding in findings
    )
    blocking_findings = any(
        finding.get("blocking") is True
        for finding in findings
    )
    if expect_warnings and not findings:
        findings = [
            make_finding(
                "WS_EXPECTED_WARNING_MISSING",
                "expected workspace-state warnings, but none were reported",
                field="expect_warnings",
                blocking=True,
                severity="FAIL",
                recommended_fix=(
                    "Use a warning fixture or remove --expect-warnings for a clean state."
                ),
            )
        ]
        result = "fail"
    else:
        result = "fail" if blocking_findings else ("warning" if findings else "pass")
    lookup_errors_value = payload.get("lookup_errors")
    lookup_errors = (
        lookup_errors_value
        if isinstance(lookup_errors_value, dict)
        else {}
    )
    mechanically_checked = ["workspace-state payload shape"]
    not_checked = [
        "issue or PR authority",
        "changed-path authorization or semantic diff contents",
        "human approval, low-risk status, or merge readiness",
    ]
    if shape_invalid:
        not_checked.extend([
            "workspace branch evidence",
            "workspace upstream evidence",
            "workspace untracked-path evidence",
            "workspace changed-path evidence",
            "merged-into-base evidence",
        ])
        boundary = (
            "Only the workspace-state payload shape was checked; no branch, "
            "upstream, merged-state, or path evidence was evaluated because "
            "required fields were missing or invalid. It does not infer issue "
            "authority, path authorization, human approval, low-risk status, or "
            "merge readiness."
        )
        output = checked_validation_result({
            "result": result,
            "strict": strict,
            "expect_warnings": expect_warnings,
            "low_risk_inferred": False,
            "state": payload,
            "findings": findings,
        },
            evidence_source=evidence_source,
            mechanically_checked=mechanically_checked,
            not_checked=not_checked,
            proof_boundary=boundary,
        )
        if as_json:
            print(json.dumps(output, indent=2, sort_keys=True))
        else:
            finding = findings[0]
            print(
                f"FAIL: {finding['field']} - {finding['reason']} Fix: "
                f"{finding.get('recommended_fix', 'Correct the payload shape.')}"
            )
            print("Workspace state check result: fail. No merge status was inferred.")
        return 1

    if evidence_source == "supplied_workspace_state_fixture":
        mechanically_checked.append(
            "supplied branch, upstream, merged-state, untracked-path, and changed-path fields"
        )
        boundary = (
            "Checks only supplied workspace branch, upstream, merged-state, "
            "untracked-path, and changed-path fields; it does not prove that the "
            "fixture is current or live, and does not infer issue authority, path "
            "authorization, human approval, low-risk status, or merge readiness."
        )
        output = checked_validation_result({
            "result": result,
            "strict": strict,
            "expect_warnings": expect_warnings,
            "low_risk_inferred": False,
            "state": payload,
            "findings": findings,
        },
            evidence_source=evidence_source,
            mechanically_checked=mechanically_checked,
            not_checked=[
                *not_checked,
                "truth or freshness of supplied workspace-state fields",
            ],
            proof_boundary=boundary,
        )
        if as_json:
            print(json.dumps(output, indent=2, sort_keys=True))
        elif findings:
            for finding in findings:
                paths = finding.get("paths")
                suffix = f" Paths: {', '.join(paths)}" if isinstance(paths, list) and paths else ""
                print(
                    f"{finding.get('severity', 'WARN')}: {finding['field']} - "
                    f"{finding['reason']} Fix: "
                    f"{finding.get('recommended_fix', 'Review the workspace state.')}{suffix}"
                )
            print(f"Workspace state check result: {output['result']}. No merge status was inferred.")
        else:
            print("Workspace state check passed. No merge status was inferred.")
        if output["result"] == "fail":
            return 1
        if strict and findings:
            return 1
        return 0

    mechanically_checked[0] = "workspace-state payload and lookup-error projection"
    lookup_surfaces = {
        "branch": "workspace branch evidence",
        "upstream": "workspace upstream evidence",
        "untracked": "workspace untracked-path evidence",
        "diff": "workspace unstaged changed-path evidence",
        "cached_diff": "workspace staged changed-path evidence",
    }
    for key, surface in lookup_surfaces.items():
        if str(lookup_errors.get(key) or "").strip():
            not_checked.append(surface)
        else:
            mechanically_checked.append(surface)
    merged_check_error = str(payload.get("merged_check_error") or "").strip()
    if merged_check_error or not str(payload.get("branch") or "").strip():
        not_checked.append("merged-into-base evidence")
    else:
        mechanically_checked.append("merged-into-base evidence")
    lookup_incomplete = any(
        str(value or "").strip()
        for value in lookup_errors.values()
    ) or bool(merged_check_error)
    boundary = (
        (
            "Reports only the workspace lookup attempts that completed; failed "
            "lookup surfaces remain explicitly not checked. It does not infer "
            "issue authority, path authorization, human approval, low-risk "
            "status, or merge readiness."
        )
        if lookup_incomplete
        else (
            "Checks only supplied or locally observed workspace branch, upstream, "
            "merged-state, and untracked-path evidence; it does not infer issue "
            "authority, path authorization, human approval, low-risk status, or "
            "merge readiness."
        )
    )
    output = checked_validation_result({
        "result": result,
        "strict": strict,
        "expect_warnings": expect_warnings,
        "low_risk_inferred": False,
        "state": payload,
        "findings": findings,
    },
        evidence_source=evidence_source,
        mechanically_checked=mechanically_checked,
        not_checked=not_checked,
        proof_boundary=boundary,
    )
    if as_json:
        print(json.dumps(output, indent=2, sort_keys=True))
    elif findings:
        for finding in findings:
            paths = finding.get("paths")
            suffix = f" Paths: {', '.join(paths)}" if isinstance(paths, list) and paths else ""
            print(
                f"{finding.get('severity', 'WARN')}: {finding['field']} - "
                f"{finding['reason']} Fix: "
                f"{finding.get('recommended_fix', 'Review the workspace state.')}{suffix}"
            )
        print(f"Workspace state check result: {output['result']}. No merge status was inferred.")
    else:
        print("Workspace state check passed. No merge status was inferred.")

    if output["result"] == "fail":
        return 1
    if strict and findings:
        return 1
    return 0
