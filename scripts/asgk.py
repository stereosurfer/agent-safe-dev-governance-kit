#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PR_REQUIRED_HEADINGS = [
    "Summary", "Task Reference", "Changed Files", "Validation",
    "Evidence Of Completion", "Scope Boundaries", "Runtime Output Status",
    "Merge Decision", "Known Gaps", "Handoff Report",
]
MERGE_DECISION_REQUIRED_FIELDS = [
    "issue", "lane", "intelligence_level", "durable_source_of_truth",
    "checks_passed", "allowed_paths_checked", "expected_output_checked",
    "contracts_checked", "schemas_checked", "storage_boundary",
    "runtime_artifact_boundary", "safety_review", "human_gates_checked",
    "result", "reason",
]
TASK_PACKET_REQUIRED_FIELDS = ["durable_source_of_truth", "allowed_paths", "stop_conditions"]
HANDOFF_REQUIRED_FIELDS = [
    "active_issue", "active_pr", "branch", "objective", "current_state",
    "completed", "remaining", "allowed_paths", "modified_files",
    "validation_status", "blockers", "next_safe_action", "must_read",
    "must_not_do", "decisions", "open_questions",
]
HANDOFF_REQUIRED_LIST_FIELDS = [
    "completed", "remaining", "allowed_paths", "modified_files", "must_read",
    "must_not_do", "decisions", "open_questions",
]
HANDOFF_REQUIRED_SCALAR_FIELDS = ["active_issue"]
STATUS_REQUIRED_HEADINGS = [
    "Durable source of truth", "Current snapshot", "Active work",
    "Current validation entrypoint", "Closed gates", "Last completed",
    "Runtime artifact status", "Next safe action",
]
STATUS_FORBIDDEN_HISTORY_HEADINGS = [
    "History", "Work Log", "Chronological Log", "Completed Work Log",
]
STATUS_FORBIDDEN_PHRASES = [
    "full PR body", "raw CI log", "chat transcript", "see chat",
]
CLOSEOUT_PRE_MERGE_NEXT_ACTION_PATTERNS = [
    r"verify\s+github\s+actions",
    r"wait\s+for\s+github\s+actions",
    r"update\s+(?:the\s+)?merge\s+decision",
    r"merge\s+only\s+if",
    r"merge\s+pr\s+#?\d+",
    r"close\s+issue\s+#?\d+",
]
CURRENT_STATUS_IMPACT_ALLOWED_VALUES = {"updated", "not_applicable", "deferred"}
CANONICAL_CURRENT_STATUS_PATH = "docs/handoff/CURRENT_STATUS.md"
TRUE_VALUES = {"true", "yes"}
EMPTY_FOLLOWUP_VALUES = {"", "none", "null", "tbd", "todo"}
NEGATIVE_CHANGED_PATH_FIXTURES = [
    "examples/negative/changed_paths.runtime-artifact.txt",
    "examples/negative/changed_paths.protected.txt",
    "examples/negative/changed_paths.private-binary.txt",
]
EXPECTED_FAILURE_CHECKS = [
    ["python3", "scripts/asgk.py", "pr-body-check", "--file", "examples/negative/pr_body.no-merge-decision.md"],
    ["python3", "scripts/asgk.py", "pr-body-check", "--file", "examples/negative/pr_body.see-chat.md"],
    ["python3", "scripts/asgk.py", "task-packet-check", "--file", "examples/negative/task_packet.see-chat.yaml"],
    ["python3", "scripts/asgk.py", "task-packet-check", "--file", "examples/negative/task_packet.no-stop.yaml"],
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
]
POLICY_GATE_NEGATIVE_FIXTURES = [
    "examples/negative/policy_gate/pr_body.missing-merge-decision.md",
    "examples/negative/policy_gate/pr_body.missing-current-status-impact.md",
    "examples/negative/policy_gate/pr_body.updated-missing-post-merge-safe.md",
    "examples/negative/policy_gate/pr_body.checks-pending.md",
    "examples/negative/policy_gate/pr_body.human-gates-pending.md",
    "examples/negative/policy_gate/pr_body.see-chat-authority.md",
]
TARGET_INSTALL_NEGATIVE_FIXTURES = [
    "examples/negative/target_install/missing_required_files",
    "examples/negative/target_install/repo_local_readiness_surface",
]
TARGET_INSTALL_LICENSE_NOTICE_PATHS = [
    "LICENSE",
    "LICENSE.md",
    "NOTICE",
    "NOTICE.md",
    "THIRD_PARTY_NOTICES.md",
    "docs/LICENSE.md",
    "docs/NOTICE.md",
]
TARGET_INSTALL_REQUIRED_FILES = [
    "AGENTS.md",
    "README.md",
    "docs/DOCUMENT_MAP.md",
    "docs/DOCUMENT_REGISTRY.md",
    "docs/handoff/CURRENT_STATUS.md",
    "docs/control/CONTEXT_BUDGET_POLICY.md",
    "docs/control/AGENT_CAPABILITY_MATRIX.md",
    "docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md",
    "docs/control/HUMAN_GATED_OPERATIONS.md",
    "docs/control/MERGE_DECISION_RECORD.md",
    "docs/control/TASK_PACKET_FORMAT.md",
    "docs/control/AGENT_REPORT_FORMAT.md",
    "agent/agent_rules.yaml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/agent_task.yml",
]
TARGET_INSTALL_LEGACY_AGENT_KEYS = [
    "require_subagent_intelligence_level",
    "subagent_intelligence_levels",
    "subagent_assignment_required_fields",
]
TARGET_INSTALL_PREFERRED_AGENT_KEYS = [
    "require_assignment_intelligence_level",
    "assignment_intelligence_levels",
    "worker_assignment_required_fields",
]
TARGET_INSTALL_FORBIDDEN_BLOCKING_PATHS = [
    "docs/control/V1_1_STABILIZATION_PLAN.md",
    "docs/control/V1_READINESS_AUDIT.md",
    "docs/control/UNCONTROLLED_DOCUMENT_AUDIT.md",
    "docs/EVOLUTION_MODEL.md",
]
TARGET_INSTALL_FORBIDDEN_WARNING_PATHS = [
    "docs/handoff/AGENT_LOG.md",
    "docs/handoff/DECISIONS.md",
    "examples/negative",
    "profiles",
    "docs/adapters",
]
TARGET_INSTALL_DEFERRED_V2_SURFACES = ["profiles/", "docs/adapters/"]


def rel(path: str | Path) -> Path:
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


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


def run_policy_gate(pr_body: str | Path, *, as_json: bool = False) -> int:
    command = ["python3", "scripts/policy_gate_check.py", "--pr-body", str(pr_body)]
    if as_json:
        command.append("--json")
    return subprocess.run(command, cwd=ROOT).returncode


def run_expected_failures(commands: list[list[str]]) -> int:
    unexpected_passes = 0
    for command in commands:
        print("+ expect failure: " + " ".join(command))
        result = subprocess.run(command, cwd=ROOT)
        if result.returncode == 0:
            print("FAIL: expected command to fail, but it passed.")
            unexpected_passes += 1
    if unexpected_passes:
        print(f"FAIL: {unexpected_passes} expected-failure check(s) unexpectedly passed.")
        return 1
    print(f"Expected-failure checks passed: {len(commands)} command(s) failed as expected.")
    return 0


def read_text(path: str | Path) -> str:
    return rel(path).read_text(encoding="utf-8")


def has_see_chat(text: str) -> bool:
    return bool(re.search(r"\bsee\s+chat\b", text, flags=re.IGNORECASE))


def has_unresolved_todo(text: str) -> bool:
    return bool(re.search(r"\b(?:AI_TODO|TODO)\b", text))


def markdown_headings(text: str) -> set[str]:
    found: set[str] = set()
    for line in text.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            found.add(match.group(1).strip())
    return found


def markdown_section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s+(.+?)(?:\n## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group(1).strip() if match else ""


def line_field_exists(text: str, field: str) -> bool:
    return bool(re.search(rf"^[ \t]*{re.escape(field)}[ \t]*:", text, flags=re.MULTILINE))


def field_value(text: str, field: str) -> str | None:
    """Return a same-line scalar value for a lightweight YAML-like field.

    This deliberately avoids ``\\s`` around the colon because ``\\s`` can consume
    newlines. A field like ``next_safe_action:`` followed by another field on the
    next line must be treated as an empty value, not as if the next field were the
    value.
    """

    match = re.search(
        rf"^[ \t]*{re.escape(field)}[ \t]*:[ \t]*(.*?)[ \t]*$",
        text,
        flags=re.MULTILINE,
    )
    if not match:
        return None
    return match.group(1).strip().strip('"').strip("'")


def normalized_field_value(text: str, field: str) -> str:
    value = field_value(text, field)
    if value is None:
        return ""
    return value.strip().strip('"').strip("'").lower()


def read_changed_paths(path: str | Path) -> set[str]:
    return {
        line.strip()
        for line in read_text(path).splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def same_repo_path(left: str, right: str) -> bool:
    return left.strip().lstrip("./") == right.strip().lstrip("./")


def field_block_lines(text: str, field: str) -> list[str] | None:
    """Return indented child lines for a lightweight YAML-like field block."""

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


def print_failures(failures: list[str]) -> int:
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("Check passed.")
    return 0


def add_target_install_finding(
    findings: list[dict[str, str | bool]],
    severity: str,
    category: str,
    path: str,
    reason: str,
    recommended_fix: str,
    *,
    blocking: bool,
) -> None:
    findings.append({
        "severity": severity,
        "category": category,
        "file": path,
        "reason": reason,
        "recommended_fix": recommended_fix,
        "blocking": blocking,
    })


def repo_path(root: Path, path: str) -> Path:
    return root / path


def read_repo_text(root: Path, path: str) -> str:
    return repo_path(root, path).read_text(encoding="utf-8")


def target_install_findings(root: Path) -> list[dict[str, str | bool]]:
    findings: list[dict[str, str | bool]] = []

    for required in TARGET_INSTALL_REQUIRED_FILES:
        if not repo_path(root, required).exists():
            add_target_install_finding(
                findings,
                "FAIL",
                "required_files",
                required,
                "required target-install file is missing",
                "Create the file from the ASGK install surface or explicitly document why it is not applicable.",
                blocking=True,
            )

    if not any(repo_path(root, path).exists() for path in TARGET_INSTALL_LICENSE_NOTICE_PATHS):
        add_target_install_finding(
            findings,
            "WARN",
            "license_handling",
            "LICENSE",
            "no visible license or notice handling surface found",
            "Add LICENSE/NOTICE handling or document how ASGK Apache-2.0 notices are preserved for copied or adapted ASGK-derived material.",
            blocking=False,
        )

    document_map_path = repo_path(root, "docs/DOCUMENT_MAP.md")
    if document_map_path.exists():
        text = document_map_path.read_text(encoding="utf-8")
        required_refs = ["docs/DOCUMENT_REGISTRY.md", "docs/control/CONTEXT_BUDGET_POLICY.md"]
        for ref in required_refs:
            if ref not in text:
                add_target_install_finding(
                    findings,
                    "FAIL",
                    "document_navigation_split",
                    "docs/DOCUMENT_MAP.md",
                    f"compact router does not reference {ref}",
                    f"Update docs/DOCUMENT_MAP.md to route readers to {ref}.",
                    blocking=True,
                )
        forbidden_markers = [
            "| Document | Role | Canonical for | Read by default | Read when | Owned by lane |",
            "## Task-type Reading Guide",
        ]
        for marker in forbidden_markers:
            if marker in text:
                add_target_install_finding(
                    findings,
                    "FAIL",
                    "document_navigation_split",
                    "docs/DOCUMENT_MAP.md",
                    f"document map still contains non-router marker: {marker}",
                    "Move full registry rows to docs/DOCUMENT_REGISTRY.md and task read sets to docs/control/CONTEXT_BUDGET_POLICY.md.",
                    blocking=True,
                )
        template_markers = ["target-project navigation router template", "<lane>", "<path>", "<topic>"]
        for marker in template_markers:
            if marker in text:
                add_target_install_finding(
                    findings,
                    "WARN",
                    "template_derived_files",
                    "docs/DOCUMENT_MAP.md",
                    f"document map still contains template marker: {marker}",
                    "Customize docs/DOCUMENT_MAP.md for the target repository.",
                    blocking=False,
                )

    document_registry_path = repo_path(root, "docs/DOCUMENT_REGISTRY.md")
    if document_registry_path.exists():
        text = document_registry_path.read_text(encoding="utf-8")
        for marker in ["# Document Registry", "DOCUMENT_REGISTRY.md is repo-local"]:
            if marker not in text:
                add_target_install_finding(
                    findings,
                    "FAIL",
                    "document_navigation_split",
                    "docs/DOCUMENT_REGISTRY.md",
                    f"document registry missing marker: {marker}",
                    "Create docs/DOCUMENT_REGISTRY.md from templates/DOCUMENT_REGISTRY.template.md and customize it.",
                    blocking=True,
                )
        if "| Document | Role | Canonical for | Read by default | Read when | Owned by lane |" not in text:
            add_target_install_finding(
                findings,
                "WARN",
                "document_navigation_split",
                "docs/DOCUMENT_REGISTRY.md",
                "document registry does not appear to contain registry rows",
                "Add target-repository document rows or document why the registry is intentionally minimal.",
                blocking=False,
            )
        for marker in ["target-project template", "<lane>", "<path>", "<topic>"]:
            if marker in text:
                add_target_install_finding(
                    findings,
                    "WARN",
                    "template_derived_files",
                    "docs/DOCUMENT_REGISTRY.md",
                    f"document registry still contains template marker: {marker}",
                    "Customize docs/DOCUMENT_REGISTRY.md for the target repository.",
                    blocking=False,
                )

    agent_rules_path = repo_path(root, "agent/agent_rules.yaml")
    if agent_rules_path.exists():
        text = agent_rules_path.read_text(encoding="utf-8")
        has_migration_note = "target_legacy_key_migration" in text or "legacy_key_migration" in text
        for key in TARGET_INSTALL_LEGACY_AGENT_KEYS:
            if key in text and not has_migration_note:
                add_target_install_finding(
                    findings,
                    "FAIL",
                    "legacy_key_guard",
                    "agent/agent_rules.yaml",
                    f"target agent rules contain ASGK internal compatibility key: {key}",
                    "Use templates/agent_rules.template.yaml or add a scoped target_legacy_key_migration note.",
                    blocking=True,
                )
        if not any(key in text for key in TARGET_INSTALL_PREFERRED_AGENT_KEYS):
            add_target_install_finding(
                findings,
                "WARN",
                "legacy_key_guard",
                "agent/agent_rules.yaml",
                "target agent rules do not contain the preferred assignment/worker keys",
                "Review templates/agent_rules.template.yaml and use assignment_intelligence_levels / worker_assignment_required_fields.",
                blocking=False,
            )
        if "status: target-project-template" in text:
            add_target_install_finding(
                findings,
                "FAIL",
                "template_derived_files",
                "agent/agent_rules.yaml",
                "agent rules still look like an uncustomized target-project template",
                "Customize roles, allowed paths, and stop conditions for the target repository.",
                blocking=True,
            )

    for forbidden in TARGET_INSTALL_FORBIDDEN_BLOCKING_PATHS:
        if repo_path(root, forbidden).exists():
            add_target_install_finding(
                findings,
                "FAIL",
                "forbidden_repo_local_surfaces",
                forbidden,
                "ASGK repo-local governance file is present in the target repository surface",
                "Remove this file from target authority or document an explicit adaptation issue.",
                blocking=True,
            )

    for forbidden in TARGET_INSTALL_FORBIDDEN_WARNING_PATHS:
        if repo_path(root, forbidden).exists():
            add_target_install_finding(
                findings,
                "WARN",
                "forbidden_repo_local_surfaces",
                forbidden,
                "ASGK repo-local or deferred surface is present",
                "Keep only if intentionally adapted; otherwise remove from the target install surface.",
                blocking=False,
            )

    for startup_path in ["AGENTS.md", "docs/DOCUMENT_MAP.md"]:
        path = repo_path(root, startup_path)
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for surface in TARGET_INSTALL_DEFERRED_V2_SURFACES:
            if "default_startup_set" in text and surface in text:
                add_target_install_finding(
                    findings,
                    "FAIL",
                    "deferred_v2_guard",
                    startup_path,
                    f"default startup surface appears to reference deferred v2 path: {surface}",
                    "Remove runtime-specific profiles/adapters from the v1.x default startup path.",
                    blocking=True,
                )

    if not any(repo_path(root, candidate).exists() for candidate in ["scripts/asgk.py", ".github/workflows"]):
        add_target_install_finding(
            findings,
            "WARN",
            "validation_command_presence",
            ".",
            "no obvious validation command or workflow surface found",
            "Document the target repository validation command before relying on ASGK governance.",
            blocking=False,
        )

    return findings


def print_target_install_findings(findings: list[dict[str, str | bool]], *, as_json: bool) -> int:
    blocking_count = sum(1 for finding in findings if bool(finding["blocking"]))
    warning_count = sum(1 for finding in findings if not bool(finding["blocking"]))
    result = "fail" if blocking_count else ("warning" if warning_count else "pass")
    if as_json:
        print(json.dumps({"result": result, "findings": findings}, indent=2, sort_keys=True))
    else:
        if not findings:
            print("Target install check passed.")
        else:
            for finding in findings:
                print(
                    f"{finding['severity']}: [{finding['category']}] {finding['file']} - "
                    f"{finding['reason']} Fix: {finding['recommended_fix']}"
                )
            print(f"Target install check result: {result} ({blocking_count} blocking, {warning_count} warning).")
    return 1 if blocking_count else 0


def cmd_doctor(_args: argparse.Namespace) -> int:
    commands = [
        ["python3", "scripts/check_project.py"],
        ["python3", "scripts/validate_bootstrap.py"],
        ["git", "diff", "--check"],
        ["python3", "scripts/asgk.py", "status-check"],
    ]
    for fixture in NEGATIVE_CHANGED_PATH_FIXTURES:
        commands.append([
            "python3", "scripts/governance_hygiene.py", "--paths-file",
            fixture, "--expect-blocked",
        ])
    baseline = run_many(commands)
    textual = run_expected_failures(EXPECTED_FAILURE_CHECKS)
    return 1 if baseline or textual else 0


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
    if args.case == "changed-paths":
        return run_many([
            ["python3", "scripts/governance_hygiene.py", "--paths-file", fixture, "--expect-blocked"]
            for fixture in NEGATIVE_CHANGED_PATH_FIXTURES
        ])
    if args.case == "textual":
        return run_expected_failures(EXPECTED_FAILURE_CHECKS)
    if args.case == "policy-gate":
        return run_expected_failures([
            ["python3", "scripts/policy_gate_check.py", "--pr-body", fixture]
            for fixture in POLICY_GATE_NEGATIVE_FIXTURES
        ])
    if args.case == "target-install":
        return run_expected_failures([
            ["python3", "scripts/asgk.py", "target-install-check", "--repo-root", fixture]
            for fixture in TARGET_INSTALL_NEGATIVE_FIXTURES
        ])
    if args.case == "all":
        changed = cmd_negative(argparse.Namespace(case="changed-paths"))
        textual = cmd_negative(argparse.Namespace(case="textual"))
        policy_gate = cmd_negative(argparse.Namespace(case="policy-gate"))
        target_install = cmd_negative(argparse.Namespace(case="target-install"))
        return 1 if changed or textual or policy_gate or target_install else 0
    print(f"FAIL: unsupported negative case group: {args.case}")
    return 1


def cmd_policy_gate(args: argparse.Namespace) -> int:
    if bool(args.pr_body) == bool(args.github_event):
        return print_failures(["provide exactly one of --pr-body or --github-event"])

    if args.pr_body:
        return run_policy_gate(rel(args.pr_body), as_json=args.json)

    event = json.loads(rel(args.github_event).read_text(encoding="utf-8"))
    pull_request = event.get("pull_request")
    if not isinstance(pull_request, dict):
        payload = {
            "result": "skipped",
            "reason": "GitHub event payload does not contain a pull_request object.",
            "low_risk_inferred": False,
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print("Policy gate skipped: GitHub event payload has no pull_request object.")
        return 0

    body = pull_request.get("body")
    if body is None:
        body = ""

    with tempfile.TemporaryDirectory() as tmpdir:
        body_path = Path(tmpdir) / "pull_request_body.md"
        body_path.write_text(str(body), encoding="utf-8")
        return run_policy_gate(body_path, as_json=args.json)


def cmd_status_check(args: argparse.Namespace) -> int:
    status_path = rel(args.file)
    failures: list[str] = []
    if not status_path.exists():
        return print_failures([f"missing current status file: {args.file}"])

    text = status_path.read_text(encoding="utf-8")
    headings = markdown_headings(text)

    for heading in STATUS_REQUIRED_HEADINGS:
        if heading not in headings:
            failures.append(f"missing current status heading: ## {heading}")

    line_count = len(text.splitlines())
    if line_count > args.max_lines:
        failures.append(f"current status is too long: {line_count} lines > {args.max_lines}")

    if "python3 scripts/asgk.py doctor" not in text:
        failures.append("current status does not name python3 scripts/asgk.py doctor")

    if re.search(r"issue:\s*['\"]?#23\b", text):
        failures.append("current status appears to retain stale issue #23 active state")

    for heading in STATUS_FORBIDDEN_HISTORY_HEADINGS:
        if heading in headings:
            failures.append(f"forbidden history-log heading in current status: ## {heading}")

    lower_text = text.lower()
    for phrase in STATUS_FORBIDDEN_PHRASES:
        if phrase.lower() in lower_text:
            failures.append(f"forbidden current-status phrase: {phrase}")

    next_action = markdown_section(text, "Next safe action")
    if not next_action:
        failures.append("current status next safe action is empty")

    return print_failures(failures)


def cmd_closeout_check(args: argparse.Namespace) -> int:
    status_path = rel(args.file)
    if not status_path.exists():
        return print_failures([f"missing closeout status file: {args.file}"])

    text = status_path.read_text(encoding="utf-8")
    active_work = markdown_section(text, "Active work")
    next_safe_action = markdown_section(text, "Next safe action")
    failures: list[str] = []

    for issue in args.completed_issue:
        if issue and issue in active_work:
            failures.append(f"completed issue still appears in active work: {issue}")

    for pr in args.completed_pr:
        if pr and pr in active_work:
            failures.append(f"completed PR still appears in active work: {pr}")

    for branch in args.completed_branch:
        if branch and branch in active_work:
            failures.append(f"completed branch still appears in active work: {branch}")

    if not next_safe_action:
        failures.append("next safe action is empty")
    else:
        for pattern in CLOSEOUT_PRE_MERGE_NEXT_ACTION_PATTERNS:
            if re.search(pattern, next_safe_action, flags=re.IGNORECASE):
                failures.append(f"next safe action appears to describe pre-merge closeout work: {pattern}")

    return print_failures(failures)


def cmd_current_status_impact_check(args: argparse.Namespace) -> int:
    pr_body = read_text(args.pr_body)
    changed_paths = read_changed_paths(args.changed_paths_file)
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

    status = normalized_field_value(current_status_section, "status")
    if status not in CURRENT_STATUS_IMPACT_ALLOWED_VALUES:
        failures.append("Current Status Impact status must be updated, not_applicable, or deferred")

    reason = normalized_field_value(current_status_section, "reason")
    if reason in {"", "pending", "unknown", "none", "tbd", "todo"}:
        failures.append("Current Status Impact reason is missing or non-specific")

    updated = normalized_field_value(current_status_section, "current_status_updated_in_this_pr")
    if status == "updated" and updated not in TRUE_VALUES:
        failures.append("status is updated but current_status_updated_in_this_pr is not true")

    if current_status_changed and status != "updated":
        failures.append(f"{CANONICAL_CURRENT_STATUS_PATH} changed but Current Status Impact status is not updated")

    if status == "updated" and not current_status_changed:
        failures.append(f"Current Status Impact status is updated but {CANONICAL_CURRENT_STATUS_PATH} did not change")

    post_merge_safe = normalized_field_value(current_status_section, "post_merge_safe")
    if status == "updated" and post_merge_safe not in TRUE_VALUES:
        failures.append("status is updated but post_merge_safe is not true")

    follow_up = normalized_field_value(current_status_section, "follow_up_issue")
    if status == "deferred":
        has_handoff_next_action = bool(re.search(r"next safe action", handoff_section, flags=re.IGNORECASE))
        if follow_up in EMPTY_FOLLOWUP_VALUES and not has_handoff_next_action:
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

        status_text = read_text(args.file)
        active_work = markdown_section(status_text, "Active work")
        next_safe_action = markdown_section(status_text, "Next safe action")

        if args.this_pr and args.this_pr in active_work:
            failures.append(f"current status active work points to this PR: {args.this_pr}")

        for issue in args.closing_issue:
            if issue and issue in active_work:
                failures.append(f"current status active work points to closing issue: {issue}")

        if args.this_branch and args.this_branch in active_work:
            failures.append(f"current status active work points to this branch: {args.this_branch}")

        if not next_safe_action:
            failures.append("current status next safe action is empty")
        else:
            for pattern in CLOSEOUT_PRE_MERGE_NEXT_ACTION_PATTERNS:
                if re.search(pattern, next_safe_action, flags=re.IGNORECASE):
                    failures.append(f"next safe action appears to describe pre-merge closeout work: {pattern}")

    return print_failures(failures)


def cmd_pr_body_check(args: argparse.Namespace) -> int:
    text = read_text(args.file)
    failures: list[str] = []
    headings = markdown_headings(text)
    for heading in PR_REQUIRED_HEADINGS:
        if heading not in headings:
            failures.append(f"missing PR heading: ## {heading}")
    if has_see_chat(text):
        failures.append("PR body contains forbidden chat-only authority phrase: see chat")
    if "Merge Decision" not in headings:
        failures.append("missing Merge Decision section")
    else:
        for field in MERGE_DECISION_REQUIRED_FIELDS:
            if not line_field_exists(text, field):
                failures.append(f"missing Merge Decision field: {field}")
    result = field_value(text, "result")
    if result and result not in {"merge_allowed", "merge_blocked"}:
        failures.append("Merge Decision field result must be merge_allowed or merge_blocked")
    checks_passed = field_value(text, "checks_passed")
    if checks_passed and checks_passed.lower() in {"pending", "unknown", "pending github actions"}:
        failures.append("checks_passed is pending or unknown")
    return print_failures(failures)


def cmd_task_packet_check(args: argparse.Namespace) -> int:
    text = read_text(args.file)
    failures: list[str] = []
    for field in TASK_PACKET_REQUIRED_FIELDS:
        if not line_field_exists(text, field):
            failures.append(f"missing task packet field: {field}")
    if has_see_chat(text):
        failures.append("task packet contains forbidden chat-only authority phrase: see chat")
    durable_source = field_value(text, "durable_source_of_truth")
    if durable_source is not None and not durable_source:
        failures.append("durable_source_of_truth is empty")
    return print_failures(failures)


def cmd_handoff_check(args: argparse.Namespace) -> int:
    text = read_text(args.file)
    failures: list[str] = []
    for field in HANDOFF_REQUIRED_FIELDS:
        if not line_field_exists(text, field):
            failures.append(f"missing handoff field: {field}")
    if has_see_chat(text):
        failures.append("handoff packet contains forbidden chat-only authority phrase: see chat")
    if args.fail_on_todo and has_unresolved_todo(text):
        failures.append("handoff packet contains unresolved TODO or AI_TODO marker")
    next_safe_action = field_value(text, "next_safe_action")
    if next_safe_action is not None and not next_safe_action:
        failures.append("next_safe_action is empty")
    validation_status_value = field_value(text, "validation_status")
    if validation_status_value and validation_status_value.lower() == "unknown":
        failures.append("validation_status must not be unknown")
    if re.search(r"^[ \t]*status[ \t]*:[ \t]*['\"]?unknown['\"]?[ \t]*$", text, flags=re.MULTILINE):
        failures.append("validation_status.status must not be unknown")
    for field in HANDOFF_REQUIRED_SCALAR_FIELDS:
        value = field_value(text, field)
        if value is not None and not value:
            failures.append(f"{field} is empty")
    for field in HANDOFF_REQUIRED_LIST_FIELDS:
        if line_field_exists(text, field) and not list_field_has_material_item(text, field):
            failures.append(f"{field} has no material list item")
    return print_failures(failures)


def cmd_handoff_template(args: argparse.Namespace) -> int:
    active_issue = args.issue or "AI_TODO: active issue, e.g. #40"
    active_pr = args.pr or "AI_TODO: active PR or none with reason"
    branch = args.branch or "AI_TODO: current branch"
    objective = args.objective or "AI_TODO: summarize objective from durable source"

    packet = f"""handoff_packet:
  active_issue: {yaml_quote(active_issue)}
  active_pr: {yaml_quote(active_pr)}
  branch: {yaml_quote(branch)}
  objective: {yaml_quote(objective)}
  current_state: "AI_TODO: summarize current state from issue, PR, and repo files."
  completed:
    - "AI_TODO: completed step or output."
  remaining:
    - "AI_TODO: remaining bounded work."
  allowed_paths:
    - "AI_TODO: copy allowed path from issue."
  modified_files:
    - "AI_TODO: list modified file or none."
  validation_status:
    status: "not_run"
    evidence: "TODO: pass/fail/blocked/not_run evidence. Do not write unknown."
  blockers: "AI_TODO: blocker list or none."
  next_safe_action: "AI_TODO: one concrete next safe action."
  must_read:
    - "AGENTS.md"
    - "docs/handoff/CURRENT_STATUS.md"
    - "docs/control/HANDOFF_PACKET.md"
    - "docs/DOCUMENT_MAP.md"
  must_not_do:
    - "AI_TODO: forbidden action for the next actor."
  decisions:
    - "AI_TODO: durable decision already made, or none."
  open_questions:
    - "AI_TODO: open question requiring human/reviewer judgment, or none."
"""
    print(packet, end="")
    return 0


def cmd_target_install_check(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve()
    findings = target_install_findings(root)
    return print_target_install_findings(findings, as_json=args.json)


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
    p.add_argument("case", nargs="?", default="changed-paths", choices=["changed-paths", "textual", "policy-gate", "target-install", "all"])
    p.set_defaults(func=cmd_negative)

    p = sub.add_parser("policy-gate", help="Run PR-body policy gate checks.")
    p.add_argument("--pr-body", help="Path to a PR body markdown file.")
    p.add_argument("--github-event", help="Path to a GitHub Actions event payload JSON file.")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_policy_gate)

    p = sub.add_parser("status-check", help="Check docs/handoff/CURRENT_STATUS.md for compactness and stale markers.")
    p.add_argument("--file", default="docs/handoff/CURRENT_STATUS.md")
    p.add_argument("--max-lines", type=int, default=120)
    p.set_defaults(func=cmd_status_check)

    p = sub.add_parser("closeout-check", help="Check local closeout status for stale active work markers.")
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

    p = sub.add_parser("task-packet-check", help="Check required task packet fields.")
    p.add_argument("--file", required=True)
    p.set_defaults(func=cmd_task_packet_check)

    p = sub.add_parser("handoff-check", help="Check generic handoff packet completeness.")
    p.add_argument("--file", required=True)
    p.add_argument("--fail-on-todo", action="store_true", help="Fail if TODO or AI_TODO markers remain.")
    p.set_defaults(func=cmd_handoff_check)

    p = sub.add_parser("handoff-template", help="Print an AI-fillable handoff packet draft.")
    p.add_argument("--issue", default=None)
    p.add_argument("--pr", default=None)
    p.add_argument("--branch", default=None)
    p.add_argument("--objective", default=None)
    p.set_defaults(func=cmd_handoff_template)

    p = sub.add_parser("target-install-check", help="Read-only target ASGK installation check.")
    p.add_argument("--repo-root", default=str(ROOT), help="Repository root to inspect. Defaults to this repository.")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_target_install_check)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
