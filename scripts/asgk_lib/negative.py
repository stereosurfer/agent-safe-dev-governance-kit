from __future__ import annotations

import contextlib
import io
import shlex
import subprocess

from asgk_lib.common import ROOT

NEGATIVE_CHANGED_PATH_FIXTURES = [
    "examples/negative/changed_paths.runtime-artifact.txt",
    "examples/negative/changed_paths.protected.txt",
    "examples/negative/changed_paths.private-binary.txt",
]
EXPECTED_FAILURE_CHECKS = [
    ["python3", "scripts/asgk.py", "pr-body-check", "--file", "examples/negative/pr_body.no-merge-decision.md"],
    ["python3", "scripts/asgk.py", "pr-body-check", "--file", "examples/negative/pr_body.no-current-status-impact.md"],
    ["python3", "scripts/asgk.py", "pr-body-check", "--file", "examples/negative/pr_body.see-chat.md"],
    ["python3", "scripts/asgk.py", "task-packet-check", "--file", "examples/negative/task_packet.see-chat.yaml"],
    ["python3", "scripts/asgk.py", "task-packet-check", "--file", "examples/negative/task_packet.no-stop.yaml"],
    ["python3", "scripts/asgk.py", "task-packet-check", "--file", "examples/negative/task_packet.empty-list.yaml"],
    ["python3", "scripts/asgk.py", "task-packet-check", "--file", "examples/negative/task_packet.overbroad-files-to-inspect.yaml"],
    ["python3", "scripts/asgk.py", "task-packet-check", "--file", "examples/negative/task_packet.executable-no-github-issue.yaml"],
    ["python3", "scripts/asgk.py", "handoff-check", "--file", "examples/negative/handoff.missing-active-issue.yaml"],
    ["python3", "scripts/asgk.py", "handoff-check", "--file", "examples/negative/handoff.empty-next-safe-action.yaml"],
    ["python3", "scripts/asgk.py", "handoff-check", "--file", "examples/negative/handoff.unknown-validation-status.yaml"],
    ["python3", "scripts/asgk.py", "handoff-check", "--file", "examples/negative/handoff.missing-allowed-paths.yaml"],
    ["python3", "scripts/asgk.py", "handoff-check", "--file", "examples/negative/handoff.missing-must-read.yaml"],
    ["python3", "scripts/asgk.py", "handoff-check", "--file", "examples/negative/handoff.empty-required-lists.yaml"],
    ["python3", "scripts/asgk.py", "handoff-check", "--file", "examples/negative/handoff.unresolved-todo.yaml", "--fail-on-todo"],
    [
        "python3", "scripts/asgk.py", "closeout-check",
        "--file", "examples/negative/current_status.stale-closeout.md",
        "--completed-issue", "#52",
        "--completed-pr", "#53",
        "--completed-branch", "codex/positive-handoff-template-fixture",
    ],
    [
        "python3", "scripts/asgk.py", "closeout-check",
        "--file", "examples/negative/current_status.clean-closeout.md",
        "--completed-issue", "#9999",
        "--issue-closeout-reviews", "examples/negative/issue_closeout_reviews.missing-entry.md",
    ],
    [
        "python3", "scripts/asgk.py", "current-status-impact-check",
        "--pr-body", "examples/negative/current_status_impact/pr_body.updated-self-stale.md",
        "--changed-paths-file", "examples/negative/current_status_impact/changed_paths.current-status.txt",
        "--file", "examples/negative/current_status_impact/current_status.self-stale.md",
        "--this-pr", "#134",
        "--closing-issue", "#132",
        "--this-branch", "codex/public-readiness-audit-132",
    ],
    [
        "python3", "scripts/asgk.py", "current-status-impact-check",
        "--pr-body", "examples/negative/current_status_impact/pr_body.not-applicable-status-changed.md",
        "--changed-paths-file", "examples/negative/current_status_impact/changed_paths.current-status.txt",
        "--file", "examples/negative/current_status_impact/current_status.self-stale.md",
    ],
    [
        "python3", "scripts/asgk.py", "current-status-impact-check",
        "--pr-body", "examples/negative/current_status_impact/pr_body.deferred-status-changed.md",
        "--changed-paths-file", "examples/negative/current_status_impact/changed_paths.current-status.txt",
        "--file", "examples/negative/current_status_impact/current_status.self-stale.md",
    ],
    [
        "python3", "scripts/asgk.py", "release-state-check",
        "--tag", "v1.2.0",
        "--release-title", "ASGK v1.2.0",
        "--readme", "examples/negative/release_state/README.stale-v1-2-candidate.md",
    ],
]
POLICY_GATE_NEGATIVE_FIXTURES = [
    "examples/negative/policy_gate/pr_body.missing-merge-decision.md",
    "examples/negative/policy_gate/pr_body.missing-current-status-impact.md",
    "examples/negative/policy_gate/pr_body.updated-missing-post-merge-safe.md",
    "examples/negative/policy_gate/pr_body.checks-pending.md",
    "examples/negative/policy_gate/pr_body.human-gates-pending.md",
    "examples/negative/policy_gate/pr_body.see-chat-authority.md",
]
PR_STATUS_NEGATIVE_FIXTURES = [
    "examples/negative/pr_status.draft-failing.json",
    "examples/negative/pr_status.missing-closing-reference.json",
    "examples/negative/pr_status.changed-path-outside-allowed.json",
]
TARGET_INSTALL_NEGATIVE_FIXTURES = [
    "examples/negative/target_install/missing_required_files",
    "examples/negative/target_install/repo_local_readiness_surface",
]
RELEASE_STATE_NEGATIVE_FIXTURES = [
    "examples/negative/release_state/README.stale-v1-2-candidate.md",
]
RELEASE_STATE_LEDGER_NEGATIVE_FIXTURES = [
    "examples/negative/release_state/SOURCE_ONLY_RELEASE_POLICY.ledger.md",
]
WORK_UNIT_NEGATIVE_FIXTURES = [
    (
        "examples/negative/work_unit.merged-pr.json",
        "examples/work_unit.changed-paths.valid.txt",
    ),
    (
        "examples/work_unit.valid-issue.json",
        "examples/negative/work_unit.changed-paths.outside-allowed.txt",
    ),
    (
        "examples/negative/work_unit.missing-task-fields.json",
        "examples/negative/work_unit.missing-task-fields.paths.txt",
    ),
]
WORKSPACE_STATE_NEGATIVE_FIXTURES = [
    "examples/negative/workspace_state.stale-branch-untracked.json",
]
COMPACT_GOVERNANCE_RED_TEAM_CHECK = "scripts/compact_governance_red_team_check.py"
COMPACT_ISSUE_SCOPE_NEGATIVE_FIXTURES = [
    "examples/negative/compact_governance/issue-scope.missing-allowed-paths.json",
]
COMPACT_SCOPE_LOCK_NEGATIVE_CASES = [
    [
        "--json-file",
        "examples/negative/compact_governance/scope-lock.missing-allowed-paths.json",
    ],
    [
        "--json-file",
        "examples/compact_governance/scope_lock.valid-issue.json",
        "--compare-file",
        "examples/negative/compact_governance/scope-lock.stale-capture.json",
    ],
]
COMPACT_PR_REPORT_NEGATIVE_FIXTURES = [
    "examples/negative/compact_governance/pr-report.claim-conflicts-with-tool-state.json",
    "examples/negative/compact_governance/pr-report.metadata-unavailable.json",
    "examples/negative/compact_governance/pr-report.restricted-boundary-claimed-human-gate.json",
]
COMPACT_TASK_PACKET_NEGATIVE_FIXTURES = [
    "examples/negative/compact_governance/task-packet-delta-expands-scope.json",
]
COMPACT_PR_BODY_NEGATIVE_CASES = [
    (
        "examples/negative/compact_governance/pr_body.compact.failed-report.md",
        "examples/negative/compact_governance/pr-report.metadata-unavailable.json",
    ),
    (
        "examples/negative/compact_governance/pr_body.compact.requires-human-report.md",
        "examples/negative/compact_governance/reports/pr-report.requires-human-restricted-boundary.json",
    ),
]
COMPACT_HANDOFF_NEGATIVE_CASES = [
    [
        "--file",
        "examples/negative/compact_governance/handoff.compact.hides-stale-current-status.yaml",
        "--current-status",
        "examples/negative/compact_governance/current_status.compact.stale-active.md",
        "--completed-issue",
        "#240",
        "--completed-pr",
        "#241",
        "--completed-branch",
        "codex/compact-pr-body-profile-240",
    ],
]
COMPACT_TARGET_UPGRADE_NEGATIVE_MANIFESTS = [
    "examples/negative/compact_governance/target_upgrade/manifest.overwrites-current-status.json",
    "examples/negative/compact_governance/target_upgrade/manifest.default-enabled.json",
]
NEGATIVE_CASE_CHOICES = [
    "changed-paths",
    "textual",
    "policy-gate",
    "pr-status",
    "target-install",
    "release-state",
    "work-unit",
    "workspace-state",
    "compact-governance",
    "compact-issue-scope",
    "compact-scope-lock",
    "compact-pr-report",
    "compact-task-packet",
    "compact-pr-body",
    "compact-handoff",
    "compact-target-upgrade",
    "all",
]


def format_command(args: list[str]) -> str:
    return shlex.join(args)


def run_captured(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def print_captured_output(output: str) -> None:
    if output.strip():
        print(output.rstrip())


def run_negative_case_capture(case: str) -> tuple[int, str]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        result = run_negative_case(case)
    return result, buffer.getvalue()


def run_many(commands: list[list[str]]) -> int:
    failures: list[tuple[list[str], str]] = []
    for command in commands:
        result = run_captured(command)
        if result.returncode != 0:
            failures.append((command, result.stdout))
    if failures:
        for command, output in failures:
            print(f"FAIL: command failed: {format_command(command)}")
            print_captured_output(output)
        print(f"FAIL: {len(failures)} command(s) failed.")
        return 1
    print(f"Checks passed: {len(commands)} command(s).")
    return 0


def run_expected_failures(commands: list[list[str]]) -> int:
    unexpected_passes: list[tuple[list[str], str]] = []
    for command in commands:
        result = run_captured(command)
        if result.returncode == 0:
            unexpected_passes.append((command, result.stdout))
    if unexpected_passes:
        for command, output in unexpected_passes:
            print(f"FAIL: expected command to fail, but it passed: {format_command(command)}")
            print_captured_output(output)
        print(f"FAIL: {len(unexpected_passes)} expected-failure check(s) unexpectedly passed.")
        return 1
    print(f"Expected-failure checks passed: {len(commands)} command(s) failed as expected.")
    return 0


def run_expected_successes(commands: list[list[str]]) -> int:
    failures: list[tuple[list[str], str]] = []
    for command in commands:
        result = run_captured(command)
        if result.returncode != 0:
            failures.append((command, result.stdout))
    if failures:
        for command, output in failures:
            print(f"FAIL: expected command to pass, but it failed: {format_command(command)}")
            print_captured_output(output)
        print(f"FAIL: {len(failures)} expected-success check(s) failed.")
        return 1
    print(f"Expected-success checks passed: {len(commands)} command(s) passed as expected.")
    return 0


def changed_path_hygiene_commands() -> list[list[str]]:
    return [
        ["python3", "scripts/governance_hygiene.py", "--paths-file", fixture, "--expect-blocked"]
        for fixture in NEGATIVE_CHANGED_PATH_FIXTURES
    ]


def run_changed_path_hygiene_checks() -> int:
    return run_many(changed_path_hygiene_commands())


def run_textual_negative_checks() -> int:
    return run_expected_failures(EXPECTED_FAILURE_CHECKS)


def run_negative_case(case: str) -> int:
    if case == "changed-paths":
        return run_changed_path_hygiene_checks()
    if case == "textual":
        return run_textual_negative_checks()
    if case == "policy-gate":
        return run_expected_failures([
            ["python3", "scripts/policy_gate_check.py", "--pr-body", fixture]
            for fixture in POLICY_GATE_NEGATIVE_FIXTURES
        ])
    if case == "pr-status":
        return run_expected_failures([
            ["python3", "scripts/asgk.py", "check-pr", "--json-file", fixture]
            for fixture in PR_STATUS_NEGATIVE_FIXTURES
        ])
    if case == "target-install":
        return run_expected_failures([
            ["python3", "scripts/asgk.py", "target-install-check", "--repo-root", fixture]
            for fixture in TARGET_INSTALL_NEGATIVE_FIXTURES
        ])
    if case == "release-state":
        return run_expected_failures([
            [
                "python3", "scripts/asgk.py", "release-state-check",
                "--tag", "v1.2.0",
                "--release-title", "ASGK v1.2.0",
                "--readme", fixture,
            ]
            for fixture in RELEASE_STATE_NEGATIVE_FIXTURES
        ] + [
            [
                "python3", "scripts/asgk.py", "release-state-check",
                "--tag", "v1.6.0",
                "--release-title", "ASGK v1.6.0",
                "--release-policy", fixture,
            ]
            for fixture in RELEASE_STATE_LEDGER_NEGATIVE_FIXTURES
        ])
    if case == "work-unit":
        return run_expected_failures([
            [
                "python3", "scripts/asgk.py", "work-unit-check",
                "--json-file", fixture,
                "--paths-file", paths_file,
            ]
            for fixture, paths_file in WORK_UNIT_NEGATIVE_FIXTURES
        ])
    if case == "workspace-state":
        return run_expected_successes([
            [
                "python3", "scripts/asgk.py", "workspace-state-check",
                "--json-file", fixture,
                "--expect-warnings",
            ]
            for fixture in WORKSPACE_STATE_NEGATIVE_FIXTURES
        ])
    if case == "compact-governance":
        return run_many([
            ["python3", COMPACT_GOVERNANCE_RED_TEAM_CHECK],
        ])
    if case == "compact-issue-scope":
        return run_expected_failures([
            [
                "python3", "scripts/asgk.py", "compact-issue-scope",
                "--json-file", fixture,
            ]
            for fixture in COMPACT_ISSUE_SCOPE_NEGATIVE_FIXTURES
        ])
    if case == "compact-scope-lock":
        return run_expected_failures([
            [
                "python3", "scripts/asgk.py", "compact-scope-lock",
                *negative_case,
            ]
            for negative_case in COMPACT_SCOPE_LOCK_NEGATIVE_CASES
        ])
    if case == "compact-pr-report":
        return run_expected_failures([
            [
                "python3", "scripts/asgk.py", "compact-pr-report",
                "--json-file", fixture,
            ]
            for fixture in COMPACT_PR_REPORT_NEGATIVE_FIXTURES
        ])
    if case == "compact-task-packet":
        return run_expected_failures([
            [
                "python3", "scripts/asgk.py", "compact-task-packet-check",
                "--json-file", fixture,
            ]
            for fixture in COMPACT_TASK_PACKET_NEGATIVE_FIXTURES
        ])
    if case == "compact-pr-body":
        return run_expected_failures([
            [
                "python3", "scripts/asgk.py", "compact-pr-body-check",
                "--body-file", body,
                "--report-json", report,
            ]
            for body, report in COMPACT_PR_BODY_NEGATIVE_CASES
        ])
    if case == "compact-handoff":
        return run_expected_failures([
            [
                "python3", "scripts/asgk.py", "compact-handoff-check",
                *negative_case,
            ]
            for negative_case in COMPACT_HANDOFF_NEGATIVE_CASES
        ])
    if case == "compact-target-upgrade":
        return run_expected_failures([
            [
                "python3", "scripts/asgk.py", "compact-target-upgrade-check",
                "--manifest", manifest,
            ]
            for manifest in COMPACT_TARGET_UPGRADE_NEGATIVE_MANIFESTS
        ])
    if case == "all":
        children = [child for child in NEGATIVE_CASE_CHOICES if child != "all"]
        failures: list[tuple[str, str]] = []
        for child in children:
            result, output = run_negative_case_capture(child)
            if result != 0:
                failures.append((child, output))
        if failures:
            for child, output in failures:
                print(f"FAIL: negative case group failed: {child}")
                print_captured_output(output)
            print(f"FAIL: {len(failures)} negative case group(s) failed.")
            return 1
        print(f"Negative checks passed: {len(children)} group(s).")
        return 0
    print(f"FAIL: unsupported negative case group: {case}")
    return 1
