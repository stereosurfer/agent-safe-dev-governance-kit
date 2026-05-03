#!/usr/bin/env python3
from __future__ import annotations
import argparse
import re
import subprocess
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
NEGATIVE_CHANGED_PATH_FIXTURES = [
    "examples/negative/changed_paths.runtime-artifact.txt",
    "examples/negative/changed_paths.protected.txt",
    "examples/negative/changed_paths.private-binary.txt",
]


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


def read_text(path: str | Path) -> str:
    return rel(path).read_text(encoding="utf-8")


def has_see_chat(text: str) -> bool:
    return bool(re.search(r"\bsee\s+chat\b", text, flags=re.IGNORECASE))


def markdown_headings(text: str) -> set[str]:
    found: set[str] = set()
    for line in text.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            found.add(match.group(1).strip())
    return found


def line_field_exists(text: str, field: str) -> bool:
    return bool(re.search(rf"^[ \t]*{re.escape(field)}[ \t]*:", text, flags=re.MULTILINE))


def field_value(text: str, field: str) -> str | None:
    """Return a same-line scalar value for a lightweight YAML-like field.

    This deliberately avoids ``\s`` around the colon because ``\s`` can consume
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


def print_failures(failures: list[str]) -> int:
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("Check passed.")
    return 0


def cmd_doctor(_args: argparse.Namespace) -> int:
    commands = [
        ["python3", "scripts/check_project.py"],
        ["python3", "scripts/validate_bootstrap.py"],
        ["git", "diff", "--check"],
    ]
    for fixture in NEGATIVE_CHANGED_PATH_FIXTURES:
        commands.append([
            "python3", "scripts/governance_hygiene.py", "--paths-file",
            fixture, "--expect-blocked",
        ])
    return run_many(commands)


def cmd_validate(_args: argparse.Namespace) -> int:
    return run_many([["python3", "scripts/validate_bootstrap.py"]])


def cmd_hygiene(args: argparse.Namespace) -> int:
    command = ["python3", "scripts/governance_hygiene.py", "--paths-file", args.paths_file]
    if args.expect_blocked:
        command.append("--expect-blocked")
    return run_many([command])


def cmd_negative(args: argparse.Namespace) -> int:
    if args.case not in ("changed-paths", "all"):
        print(f"FAIL: unsupported negative case group: {args.case}")
        return 1
    return run_many([
        ["python3", "scripts/governance_hygiene.py", "--paths-file", fixture, "--expect-blocked"]
        for fixture in NEGATIVE_CHANGED_PATH_FIXTURES
    ])


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
    next_safe_action = field_value(text, "next_safe_action")
    if next_safe_action is not None and not next_safe_action:
        failures.append("next_safe_action is empty")
    validation_status_value = field_value(text, "validation_status")
    if validation_status_value and validation_status_value.lower() == "unknown":
        failures.append("validation_status must not be unknown")
    if re.search(r"^[ \t]*status[ \t]*:[ \t]*['\"]?unknown['\"]?[ \t]*$", text, flags=re.MULTILINE):
        failures.append("validation_status.status must not be unknown")
    for field in ("active_issue", "allowed_paths", "must_read"):
        value = field_value(text, field)
        if value is not None and not value:
            failures.append(f"{field} is empty")
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASGK minimal validation CLI.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("doctor", help="Run baseline positive and changed-path negative checks.")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("validate", help="Run bootstrap governance validation.")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("hygiene", help="Run changed-path governance hygiene.")
    p.add_argument("--paths-file", required=True)
    p.add_argument("--expect-blocked", action="store_true")
    p.set_defaults(func=cmd_hygiene)

    p = sub.add_parser("negative", help="Run opt-in negative checks.")
    p.add_argument("case", nargs="?", default="changed-paths", choices=["changed-paths", "all"])
    p.set_defaults(func=cmd_negative)

    p = sub.add_parser("pr-body-check", help="Check PR body and Merge Decision Record.")
    p.add_argument("--file", required=True)
    p.set_defaults(func=cmd_pr_body_check)

    p = sub.add_parser("task-packet-check", help="Check required task packet fields.")
    p.add_argument("--file", required=True)
    p.set_defaults(func=cmd_task_packet_check)

    p = sub.add_parser("handoff-check", help="Check generic handoff packet completeness.")
    p.add_argument("--file", required=True)
    p.set_defaults(func=cmd_handoff_check)

    p = sub.add_parser("handoff-template", help="Print an AI-fillable handoff packet draft.")
    p.add_argument("--issue", default=None)
    p.add_argument("--pr", default=None)
    p.add_argument("--branch", default=None)
    p.add_argument("--objective", default=None)
    p.set_defaults(func=cmd_handoff_template)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
