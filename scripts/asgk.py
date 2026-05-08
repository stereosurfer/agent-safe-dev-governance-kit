#!/usr/bin/env python3
from __future__ import annotations
import argparse
import fnmatch
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PR_REQUIRED_HEADINGS = [
    "Summary", "Task Reference", "Changed Files", "Validation",
    "Evidence Of Completion", "Scope Boundaries", "Current Status Impact",
    "Runtime Output Status", "Merge Decision", "Known Gaps", "Handoff Report",
]
CURRENT_STATUS_IMPACT_REQUIRED_FIELDS = [
    "status", "reason", "current_status_updated_in_this_pr",
    "post_merge_safe", "follow_up_issue",
]
MERGE_DECISION_REQUIRED_FIELDS = [
    "issue", "lane", "intelligence_level", "durable_source_of_truth",
    "checks_passed", "allowed_paths_checked", "expected_output_checked",
    "contracts_checked", "schemas_checked", "storage_boundary",
    "runtime_artifact_boundary", "safety_review", "human_gates_checked",
    "result", "reason",
]
TASK_PACKET_REQUIRED_FIELDS = [
    "task_id",
    "lane",
    "intelligence_level",
    "intelligence_level_reason",
    "durable_source_of_truth",
    "objective",
    "product_context",
    "current_repository_context",
    "files_to_inspect_first",
    "allowed_paths",
    "expected_changes",
    "expected_output",
    "non_goals",
    "constraints",
    "plan",
    "checklist",
    "acceptance_sheet",
    "validation_commands",
    "stop_conditions",
    "rollback_expectations",
]
WORK_UNIT_REQUIRED_FIELDS = [
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
]
WORK_UNIT_FIELD_ALIASES = {
    "reason": ["reason", "intelligence_level_reason"],
}
TASK_PACKET_LIST_FIELDS = [
    "files_to_inspect_first",
    "allowed_paths",
    "expected_changes",
    "non_goals",
    "constraints",
    "plan",
    "checklist",
    "acceptance_sheet",
    "validation_commands",
    "stop_conditions",
]
TASK_PACKET_SCALAR_FIELDS = [
    field for field in TASK_PACKET_REQUIRED_FIELDS if field not in TASK_PACKET_LIST_FIELDS
]
TASK_PACKET_ALLOWED_INTELLIGENCE_LEVELS = {
    "fast_basic",
    "standard",
    "advanced",
    "frontier",
}
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
CONTEXT_TOKEN_ESTIMATE_CHARS_PER_TOKEN = 4
CONTEXT_MEASUREMENT_METHOD = (
    "estimated_repo_context_tokens = ceil(characters / 4); repo files only; "
    "excludes issue/PR text, system prompt, chat, tool output, model completion, "
    "and provider billing usage."
)
CONTEXT_PSEUDO_REFS = {
    "current github issue or pr",
    "current issue or pr",
    "current issue",
    "current pr",
    "open prs or current issue when relevant",
    "target file",
}
OVERBROAD_FILES_TO_INSPECT_REFS = {
    ".",
    "/",
    "*",
    "**",
    "repo",
    "repository",
    "whole repo",
    "whole repository",
    "entire repo",
    "entire repository",
    "full repo",
    "full repository",
    "everything",
    "all files",
    "all docs",
    "all documents",
    "docs",
    "docs/",
    "docs/*",
    "docs/**",
    "docs/control",
    "docs/control/",
    "docs/control/*",
    "docs/control/**",
    "docs/bootstrap",
    "docs/bootstrap/",
    "docs/bootstrap/*",
    "docs/bootstrap/**",
}
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


def run_policy_gate_capture(pr_body: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", "scripts/policy_gate_check.py", "--pr-body", str(pr_body)],
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


def normalize_repo_path(path: str) -> str:
    cleaned = path.strip().replace("\\", "/")
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    return cleaned


def same_repo_path(left: str, right: str) -> bool:
    return normalize_repo_path(left) == normalize_repo_path(right)


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
    explicit = str(payload.get("kind") or payload.get("_asgk_requested_kind") or "").lower()
    if explicit in {"issue", "pr"}:
        return explicit
    if "pull_request" in payload or "merged" in payload or "mergeable" in payload:
        return "pr"
    return "issue"


def path_matches_allowed(path: str, allowed_path: str) -> bool:
    path = normalize_repo_path(path)
    allowed = normalize_repo_path(allowed_path).strip('"').strip("'")
    if not allowed or allowed in {"none", "none_for_source_only_release_execution"}:
        return False
    if allowed.endswith("/**"):
        return path.startswith(allowed[:-3].rstrip("/") + "/")
    if allowed.endswith("/"):
        return path.startswith(allowed)
    if any(char in allowed for char in "*?[]"):
        return fnmatch.fnmatchcase(path, allowed)
    return path == allowed


def normalized_task_field_label(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", label.strip().lower()).strip("_")


def parse_markdown_task_field_sections(text: str) -> dict[str, object]:
    fields: dict[str, object] = {}
    matches = list(re.finditer(r"^#{2,6}\s+(.+?)\s*$", text, flags=re.MULTILINE))
    for index, match in enumerate(matches):
        field = normalized_task_field_label(match.group(1))
        if not field:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        if not content or content in {"_No response_", "No response"}:
            continue
        fields[field] = content
    return fields


def parse_work_unit_task_fields(body: str) -> dict[str, object]:
    fields = parse_markdown_task_field_sections(body)
    fields.update(parse_simple_task_packet_yaml(body))
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


def work_unit_field_value(fields: dict[str, object], field: str) -> object | None:
    for candidate in WORK_UNIT_FIELD_ALIASES.get(field, [field]):
        if candidate in fields:
            return fields[candidate]
    return None


def work_unit_required_field_failures(fields: dict[str, object]) -> list[str]:
    failures: list[str] = []
    for field in WORK_UNIT_REQUIRED_FIELDS:
        value = work_unit_field_value(fields, field)
        if not material_items(value):
            failures.append(f"Work-unit body missing material required task field: {field}")
    return failures


def extract_allowed_paths(body: str) -> list[str]:
    fields = parse_work_unit_task_fields(body)
    return [
        normalize_repo_path(item)
        for item in material_items(fields.get("allowed_paths"))
    ]


def check_work_unit_payload(
    payload: dict[str, object],
    changed_paths: list[str],
) -> tuple[str, list[dict[str, object]], list[str]]:
    findings: list[dict[str, object]] = []
    kind = work_unit_kind(payload)
    number = payload.get("number")
    state = str(payload.get("state") or "").lower()
    body = str(payload.get("body") or "")

    def add(field: str, reason: str, fix: str) -> None:
        findings.append({
            "severity": "FAIL",
            "field": field,
            "reason": reason,
            "recommended_fix": fix,
        })

    if kind == "issue":
        if "pull_request" in payload:
            add(
                "kind",
                f"Work unit #{number or 'unknown'} is a pull request, not an issue.",
                "Use --pr for PR follow-up work or select an open issue with allowed_paths.",
            )
        if state != "open":
            add(
                "state",
                f"Issue state is not open: {state or 'missing'}.",
                "Select an open issue or create a new durable issue before changing files.",
            )
    elif kind == "pr":
        merged = payload.get("merged")
        if state not in {"open"} or merged is True:
            add(
                "state",
                f"PR state is not open or is already merged: state={state or 'missing'}, merged={merged}.",
                "Use only an open PR that still needs follow-up fixes, or create a new issue.",
            )
    else:
        add("kind", f"Unknown work-unit kind: {kind}", "Provide an issue or PR payload.")

    if has_see_chat(body):
        add(
            "body",
            "Work-unit body contains chat-only authority phrase: see chat.",
            "Move scope, acceptance, and handoff authority into the issue, PR, or repo docs.",
        )

    task_fields = parse_work_unit_task_fields(body)
    for failure in work_unit_required_field_failures(task_fields):
        add(
            "required_task_fields",
            failure,
            "Add the missing field to the GitHub issue, PR, or task packet before changing files.",
        )

    allowed_paths = extract_allowed_paths(body)
    if not allowed_paths:
        add(
            "allowed_paths",
            "Work-unit body does not include material allowed_paths.",
            "Add explicit allowed_paths to the GitHub issue, PR, or task packet.",
        )

    normalized_changed_paths = [normalize_repo_path(path) for path in changed_paths if normalize_repo_path(path)]
    if not normalized_changed_paths:
        add(
            "changed_paths",
            "No changed paths were provided or detected.",
            "Run this check with --paths-file or --git-base/--git-head after creating a bounded diff.",
        )

    unauthorized = [
        path for path in normalized_changed_paths
        if allowed_paths and not any(path_matches_allowed(path, allowed) for allowed in allowed_paths)
    ]
    for path in unauthorized:
        add(
            "changed_paths",
            f"Changed path is outside allowed_paths: {path}",
            "Remove the change, update the durable issue before writing, or create a separate issue.",
        )

    hygiene = run_hygiene_capture(normalized_changed_paths)
    if hygiene.returncode != 0:
        add(
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
    as_json: bool,
) -> int:
    output = {
        "result": result,
        "low_risk_inferred": False,
        "work_unit": {
            "kind": work_unit_kind(payload),
            "number": payload.get("number"),
            "state": payload.get("state"),
            "url": payload.get("html_url") or payload.get("url"),
        },
        "allowed_paths": allowed_paths,
        "changed_paths": changed_paths,
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
        print("Work-unit check passed. No low-risk status was inferred.")
    return 1 if findings else 0


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


def yaml_dedent(lines: list[str]) -> str:
    material = [line for line in lines if line.strip()]
    if not material:
        return ""
    min_indent = min(len(re.match(r"^[ \t]*", line).group(0).replace("\t", "    ")) for line in material)
    return "\n".join(line[min_indent:] if len(line) >= min_indent else line for line in lines)


def task_packet_yaml_source(text: str) -> str:
    bad_input = field_block_lines(text, "bad_input")
    if bad_input is not None:
        return yaml_dedent(bad_input)
    task_packet = field_block_lines(text, "task_packet")
    if task_packet is not None:
        return yaml_dedent(task_packet)
    return text


def parse_simple_task_packet_yaml(text: str) -> dict[str, object]:
    """Parse the repository's dependency-free task-packet YAML subset.

    This is not a general YAML parser. It covers the canonical task-packet shape:
    top-level scalar fields and top-level list fields. For full YAML features,
    keep the source in JSON or add a separately approved dependency.
    """

    packet: dict[str, object] = {}
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            index += 1
            continue
        match = re.match(r"^([A-Za-z0-9_\-]+)[ \t]*:[ \t]*(.*?)\s*$", line)
        if not match:
            index += 1
            continue
        field = match.group(1)
        value = match.group(2).strip()
        if value:
            packet[field] = value.strip('"').strip("'")
            index += 1
            continue

        children: list[str] = []
        index += 1
        while index < len(lines):
            child = lines[index]
            child_stripped = child.strip()
            if child_stripped and not child.startswith((" ", "\t")) and re.match(r"^[A-Za-z0-9_\-]+[ \t]*:", child_stripped):
                break
            if child_stripped:
                item = re.match(r"^[ \t]*-[ \t]*(.*?)\s*$", child)
                if item:
                    item_value = item.group(1).strip().strip('"').strip("'")
                    if item_value:
                        children.append(item_value)
            index += 1
        packet[field] = children
    return packet


def load_task_packet_payload(path: str | Path) -> tuple[dict[str, object], str]:
    text = read_text(path)
    if path_str := str(path):
        if path_str.endswith(".json"):
            payload = json.loads(text)
            if not isinstance(payload, dict):
                raise ValueError("task packet JSON must be an object")
            candidate = payload.get("bad_input") or payload.get("task_packet") or payload
            if not isinstance(candidate, dict):
                raise ValueError("bad_input or task_packet must be an object")
            return candidate, text
    source = task_packet_yaml_source(text)
    return parse_simple_task_packet_yaml(source), text


def context_ref_text(value: object) -> str:
    return normalize_repo_path(str(value).strip().strip('"').strip("'"))


def normalized_context_ref(value: object) -> str:
    return context_ref_text(value).lower()


def task_packet_files_to_inspect_first(packet: dict[str, object]) -> list[str]:
    value = packet.get("files_to_inspect_first")
    if not isinstance(value, list):
        return []
    return [context_ref_text(item) for item in value if str(item).strip().strip('"').strip("'")]


def is_context_pseudo_ref(value: object) -> bool:
    return normalized_context_ref(value) in CONTEXT_PSEUDO_REFS


def is_overbroad_files_to_inspect_ref(value: object) -> bool:
    ref = context_ref_text(value)
    lowered = ref.lower()
    if lowered in OVERBROAD_FILES_TO_INSPECT_REFS:
        return True
    if any(char in ref for char in "*?[]"):
        return True
    if is_context_pseudo_ref(ref):
        return False
    candidate = rel(ref)
    return candidate.exists() and candidate.is_dir()


def task_packet_context_ref_failures(packet: dict[str, object]) -> list[str]:
    failures: list[str] = []
    for item in task_packet_files_to_inspect_first(packet):
        if is_overbroad_files_to_inspect_ref(item):
            failures.append(f"files_to_inspect_first contains overbroad read request: {item}")
    return failures


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

    for ref in task_packet_files_to_inspect_first(packet):
        if is_overbroad_files_to_inspect_ref(ref):
            overbroad_refs.append(ref)
            continue
        if is_context_pseudo_ref(ref):
            pseudo_refs.append(ref)
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
            "Estimate covers UTF-8 text from repo files named in files_to_inspect_first only; "
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


def task_packet_schema_failures(packet: dict[str, object], source_text: str) -> list[str]:
    failures: list[str] = []
    for field in TASK_PACKET_REQUIRED_FIELDS:
        if field not in packet:
            failures.append(f"missing task packet field: {field}")

    for field in TASK_PACKET_SCALAR_FIELDS:
        if field in packet:
            value = packet[field]
            if not isinstance(value, str) or not value.strip():
                failures.append(f"{field} must be a non-empty scalar")

    for field in TASK_PACKET_LIST_FIELDS:
        if field in packet:
            value = packet[field]
            if not isinstance(value, list):
                failures.append(f"{field} must be a list")
            elif not any(isinstance(item, str) and item.strip() for item in value):
                failures.append(f"{field} must contain at least one material item")

    intelligence_level = str(packet.get("intelligence_level", "")).strip().strip('"').strip("'")
    if intelligence_level and intelligence_level not in TASK_PACKET_ALLOWED_INTELLIGENCE_LEVELS:
        failures.append(
            "intelligence_level must be one of: "
            + ", ".join(sorted(TASK_PACKET_ALLOWED_INTELLIGENCE_LEVELS))
        )

    if has_see_chat(source_text):
        failures.append("task packet contains forbidden chat-only authority phrase: see chat")

    failures.extend(task_packet_context_ref_failures(packet))

    return failures


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

    passing_conclusions = {"SUCCESS", "SKIPPED", "NEUTRAL"}
    for item in status_rollup:
        if not isinstance(item, dict):
            add_pr_status_finding(
                findings,
                "statusCheckRollup",
                "Status check entry is not an object.",
                "Fetch PR status with gh pr view --json statusCheckRollup.",
            )
            continue
        name = str(item.get("name") or item.get("context") or "unnamed_check")
        status = str(item.get("status") or "").upper()
        conclusion = str(item.get("conclusion") or "").upper()
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


def pr_file_paths(files: object) -> list[str]:
    if not isinstance(files, list):
        return []
    paths: list[str] = []
    for item in files:
        if isinstance(item, str):
            paths.append(item)
        elif isinstance(item, dict):
            path = item.get("path") or item.get("filename")
            if path:
                paths.append(str(path))
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


def check_pr_issue_allowed_paths(payload: dict[str, object], body: str, findings: list[dict[str, str]]) -> None:
    issue_number = merge_decision_issue_number(body)
    if issue_number is None:
        return
    if "files" not in payload:
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

    for path in pr_file_paths(payload.get("files")):
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

    if payload.get("isDraft") is True:
        add_pr_status_finding(
            findings,
            "isDraft",
            "PR is still draft.",
            "Mark the PR ready for review only after gates are complete.",
        )

    merge_state = str(payload.get("mergeStateStatus") or "").upper()
    if merge_state != "CLEAN":
        add_pr_status_finding(
            findings,
            "mergeStateStatus",
            f"PR merge state is not CLEAN: {merge_state or 'missing'}.",
            "Resolve merge conflicts, blocked state, or pending mergeability before merge.",
        )

    review_decision = str(payload.get("reviewDecision") or "").upper()
    if review_decision in {"CHANGES_REQUESTED", "REVIEW_REQUIRED"}:
        add_pr_status_finding(
            findings,
            "reviewDecision",
            f"Review decision blocks merge: {review_decision}.",
            "Resolve requested changes or required review before merge eligibility.",
        )

    check_status_rollup(payload.get("statusCheckRollup"), findings)

    body = payload.get("body")
    if body is None:
        body = ""
    body_text = str(body)
    with tempfile.TemporaryDirectory() as tmpdir:
        body_path = Path(tmpdir) / "pull_request_body.md"
        body_path.write_text(body_text, encoding="utf-8")
        policy_gate = run_policy_gate_capture(body_path)
        if policy_gate.returncode != 0:
            add_pr_status_finding(
                findings,
                "body",
                "PR body policy gate failed.",
                "Fix Current Status Impact, Merge Decision, source-of-truth, or PR structure fields.",
            )

    check_closing_issue_reference(payload, body_text, findings)
    check_pr_issue_allowed_paths(payload, body_text, findings)

    if "files" not in payload:
        add_pr_status_finding(
            findings,
            "files",
            "PR file list is missing.",
            "Fetch PR metadata with gh pr view --json files or provide a fixture with files.",
        )
    else:
        hygiene = run_hygiene_capture(pr_file_paths(payload.get("files")))
        if hygiene.returncode != 0:
            add_pr_status_finding(
                findings,
                "files",
                "Changed-path hygiene failed.",
                "Remove protected/runtime/private-source-like paths or keep the PR human-gated.",
            )

    return ("fail" if findings else "pass", findings)


def print_pr_status_result(payload: dict[str, object], result: str, findings: list[dict[str, str]], *, as_json: bool) -> int:
    output = {
        "result": result,
        "low_risk_inferred": False,
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
        print("PR status check result: fail. No low-risk status was inferred.")
    else:
        print("PR status check passed. No low-risk status was inferred.")
    return 1 if findings else 0


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


def release_version_tuple(tag: str) -> tuple[int, int, int] | None:
    match = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)", tag.strip())
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def find_latest_completed_readme_versions(text: str) -> list[str]:
    return re.findall(
        r"ASGK\s+(v\d+\.\d+\.\d+)\s+is\s+the\s+latest\s+completed\s+source-only\s+GitHub\s+release",
        text,
        flags=re.IGNORECASE,
    )


def release_state_stale_patterns(tag: str) -> list[tuple[str, str]]:
    escaped = re.escape(tag)
    return [
        (rf"{escaped}[^\n.]*candidate", f"{tag} is still described as candidate"),
        (rf"candidate[^\n.]*{escaped}", f"{tag} is still described as candidate"),
        (rf"{escaped}[^\n.]*pending", f"{tag} is still described as pending"),
        (rf"pending[^\n.]*{escaped}", f"{tag} is still described as pending"),
        (
            rf"{escaped}[^\n.]*requires[^\n.]*release execution",
            f"{tag} still appears to require release execution",
        ),
        (
            rf"{escaped}[^\n.]*tag or GitHub release requires",
            f"{tag} still appears to require tag or GitHub release creation",
        ),
        (
            rf"{escaped}[^\n.]*release execution[^\n.]*not_started",
            f"{tag} release execution is still marked not_started",
        ),
    ]


def check_release_state_docs(
    *,
    tag: str,
    release_title: str,
    readme_path: Path,
    roadmap_path: Path,
    current_status_path: Path,
) -> list[str]:
    failures: list[str] = []
    if release_version_tuple(tag) is None:
        failures.append(f"release tag must be semver-like vX.Y.Z: {tag}")

    docs = [
        ("README", readme_path),
        ("roadmap", roadmap_path),
        ("current status", current_status_path),
    ]
    texts: dict[str, str] = {}
    for label, path in docs:
        if not path.exists():
            failures.append(f"missing {label} release-state file: {path}")
            continue
        texts[label] = path.read_text(encoding="utf-8")

    readme = texts.get("README", "")
    if readme:
        latest_versions = find_latest_completed_readme_versions(readme)
        if not latest_versions:
            failures.append("README does not identify the latest completed source-only GitHub release")
        for version in latest_versions:
            if version != tag:
                failures.append(f"README latest completed release is {version}, expected {tag}")
        if tag not in readme:
            failures.append(f"README does not mention released tag {tag}")

    combined_text = "\n\n".join(texts.values())
    if release_title and release_title not in combined_text:
        failures.append(f"release title not found in release-state docs: {release_title}")

    for label, text in texts.items():
        for pattern, reason in release_state_stale_patterns(tag):
            if re.search(pattern, text, flags=re.IGNORECASE):
                failures.append(f"{label}: {reason}")

    return failures


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
    if args.case == "pr-status":
        return run_expected_failures([
            ["python3", "scripts/asgk.py", "check-pr", "--json-file", fixture]
            for fixture in PR_STATUS_NEGATIVE_FIXTURES
        ])
    if args.case == "target-install":
        return run_expected_failures([
            ["python3", "scripts/asgk.py", "target-install-check", "--repo-root", fixture]
            for fixture in TARGET_INSTALL_NEGATIVE_FIXTURES
        ])
    if args.case == "release-state":
        return run_expected_failures([
            [
                "python3", "scripts/asgk.py", "release-state-check",
                "--tag", "v1.2.0",
                "--release-title", "ASGK v1.2.0",
                "--readme", fixture,
            ]
            for fixture in RELEASE_STATE_NEGATIVE_FIXTURES
        ])
    if args.case == "work-unit":
        return run_expected_failures([
            [
                "python3", "scripts/asgk.py", "work-unit-check",
                "--json-file", fixture,
                "--paths-file", paths_file,
            ]
            for fixture, paths_file in WORK_UNIT_NEGATIVE_FIXTURES
        ])
    if args.case == "all":
        changed = cmd_negative(argparse.Namespace(case="changed-paths"))
        textual = cmd_negative(argparse.Namespace(case="textual"))
        policy_gate = cmd_negative(argparse.Namespace(case="policy-gate"))
        pr_status = cmd_negative(argparse.Namespace(case="pr-status"))
        target_install = cmd_negative(argparse.Namespace(case="target-install"))
        release_state = cmd_negative(argparse.Namespace(case="release-state"))
        work_unit = cmd_negative(argparse.Namespace(case="work-unit"))
        return 1 if changed or textual or policy_gate or pr_status or target_install or release_state or work_unit else 0
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
    return print_pr_status_result(payload, result, findings, as_json=args.json)


def cmd_work_unit_check(args: argparse.Namespace) -> int:
    using_paths_file = bool(args.paths_file)
    using_git_range = bool(args.git_base or args.git_head)
    if using_paths_file == using_git_range:
        return print_failures(["provide exactly one of --paths-file or --git-base/--git-head"])
    if using_git_range and not (args.git_base and args.git_head):
        return print_failures(["--git-base and --git-head must be provided together"])

    try:
        payload = load_work_unit_payload(args)
        changed_paths = (
            read_changed_path_list(args.paths_file)
            if args.paths_file
            else load_git_changed_paths(args.git_base, args.git_head)
        )
    except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
        return print_failures([str(exc)])

    result, findings, allowed_paths = check_work_unit_payload(payload, changed_paths)
    return print_work_unit_result(
        payload,
        result,
        findings,
        allowed_paths,
        changed_paths,
        as_json=args.json,
    )


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
    if "Current Status Impact" not in headings:
        failures.append("missing Current Status Impact section")
    else:
        current_status_section = markdown_section(text, "Current Status Impact")
        for field in CURRENT_STATUS_IMPACT_REQUIRED_FIELDS:
            if not line_field_exists(current_status_section, field):
                failures.append(f"missing Current Status Impact field: {field}")
    if "Merge Decision" not in headings:
        failures.append("missing Merge Decision section")
    else:
        for field in MERGE_DECISION_REQUIRED_FIELDS:
            if not line_field_exists(text, field):
                failures.append(f"missing Merge Decision field: {field}")
    result = field_value(text, "result")
    if result and "|" not in result and result not in {"merge_allowed", "merge_blocked"}:
        failures.append("Merge Decision field result must be merge_allowed or merge_blocked")
    checks_passed = field_value(text, "checks_passed")
    if checks_passed and checks_passed.lower() in {"pending", "unknown", "pending github actions"}:
        failures.append("checks_passed is pending or unknown")
    return print_failures(failures)


def cmd_task_packet_check(args: argparse.Namespace) -> int:
    try:
        packet, source_text = load_task_packet_payload(args.file)
    except (json.JSONDecodeError, ValueError) as exc:
        return print_failures([f"invalid task packet format: {exc}"])
    return print_failures(task_packet_schema_failures(packet, source_text))


def cmd_context_budget_measure(args: argparse.Namespace) -> int:
    try:
        packet, source_text = load_task_packet_payload(args.task_packet)
    except (json.JSONDecodeError, ValueError) as exc:
        return print_failures([f"invalid task packet format: {exc}"])
    failures = task_packet_schema_failures(packet, source_text)
    if failures:
        return print_failures(failures)
    measurement = context_budget_measurement(packet)
    return print_context_budget_measurement(measurement, as_json=args.json)


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


def cmd_release_state_check(args: argparse.Namespace) -> int:
    failures = check_release_state_docs(
        tag=args.tag,
        release_title=args.release_title,
        readme_path=rel(args.readme),
        roadmap_path=rel(args.roadmap),
        current_status_path=rel(args.current_status),
    )
    return print_failures(failures)


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
    p.add_argument("case", nargs="?", default="changed-paths", choices=["changed-paths", "textual", "policy-gate", "pr-status", "target-install", "release-state", "work-unit", "all"])
    p.set_defaults(func=cmd_negative)

    p = sub.add_parser("policy-gate", help="Run PR-body policy gate checks.")
    p.add_argument("--pr-body", help="Path to a PR body markdown file.")
    p.add_argument("--github-event", help="Path to a GitHub Actions event payload JSON file.")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_policy_gate)

    p = sub.add_parser("check-pr", help="Check GitHub PR status and checkable merge gates.")
    p.add_argument("--pr", help="GitHub pull request number for live gh lookup.")
    p.add_argument("--json-file", help="Fixture or captured gh pr view JSON payload.")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_check_pr)

    p = sub.add_parser("work-unit-check", help="Check live work-unit authority against changed paths.")
    p.add_argument("--issue", help="GitHub issue number for live gh REST lookup.")
    p.add_argument("--pr", help="GitHub pull request number for live gh REST lookup.")
    p.add_argument("--json-file", help="Fixture or captured issue/PR JSON payload.")
    p.add_argument("--paths-file", help="Newline-delimited changed-path list.")
    p.add_argument("--git-base", help="Base revision for git diff --name-only.")
    p.add_argument("--git-head", help="Head revision for git diff --name-only.")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_work_unit_check)

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

    p = sub.add_parser("context-budget-measure", help="Estimate repo-context tokens from task packet files_to_inspect_first.")
    p.add_argument("--task-packet", required=True)
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.set_defaults(func=cmd_context_budget_measure)

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

    p = sub.add_parser("release-state-check", help="Check post-release docs are not stale candidate/pending surfaces.")
    p.add_argument("--tag", required=True, help="Released tag, for example v1.2.0.")
    p.add_argument("--release-title", required=True, help="Released GitHub release title.")
    p.add_argument("--readme", default="README.md")
    p.add_argument("--roadmap", default="docs/bootstrap/10_roadmap.md")
    p.add_argument("--current-status", default="docs/handoff/CURRENT_STATUS.md")
    p.set_defaults(func=cmd_release_state_check)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
