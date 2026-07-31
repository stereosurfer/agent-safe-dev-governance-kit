from __future__ import annotations

from dataclasses import dataclass

COMMANDS_PASS = "commands_pass"
EXPECTED_FAILURE = "expected_failure"
EXPECTED_SUCCESS = "expected_success"

ASGK = ("python3", "scripts/asgk.py")


@dataclass(frozen=True)
class NegativeCaseGroup:
    mode: str
    commands: tuple[tuple[str, ...], ...]


def _commands(prefix: tuple[str, ...], fixtures: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
    return tuple((*prefix, fixture) for fixture in fixtures)


def _commands_with_suffix(
    prefix: tuple[str, ...],
    fixtures: tuple[str, ...],
    suffix: tuple[str, ...],
) -> tuple[tuple[str, ...], ...]:
    return tuple((*prefix, fixture, *suffix) for fixture in fixtures)


def _case_commands(prefix: tuple[str, ...], cases: tuple[tuple[str, ...], ...]) -> tuple[tuple[str, ...], ...]:
    return tuple((*prefix, *case) for case in cases)

def _policy_gate_mode_commands(
    fixtures: tuple[str, ...],
    modes: tuple[str, ...],
) -> tuple[tuple[str, ...], ...]:
    return tuple(
        (
            "python3",
            "scripts/policy_gate_check.py",
            "--pr-body",
            fixture,
            "--mode",
            mode,
        )
        for fixture in fixtures
        for mode in modes
    )


TEXTUAL_EXPECTED_FAILURES = (
    (*ASGK, "pr-body-check", "--file", "examples/negative/pr_body.no-merge-decision.md"),
    (*ASGK, "pr-body-check", "--file", "examples/negative/pr_body.no-current-status-impact.md"),
    (*ASGK, "pr-body-check", "--file", "examples/negative/pr_body.see-chat.md"),
    (*ASGK, "task-packet-check", "--file", "examples/negative/task_packet.see-chat.yaml"),
    (*ASGK, "task-packet-check", "--file", "examples/negative/task_packet.no-stop.yaml"),
    (*ASGK, "task-packet-check", "--file", "examples/negative/task_packet.empty-list.yaml"),
    (*ASGK, "task-packet-check", "--file", "examples/negative/task_packet.overbroad-context-read-set.yaml"),
    (*ASGK, "task-packet-check", "--file", "examples/negative/task_packet.executable-no-github-issue.yaml"),
    (*ASGK, "task-packet-check", "--file", "examples/negative/task_packet.reason-alias.yaml"),
    (*ASGK, "task-packet-check", "--file", "examples/negative/task_packet.fallback-status.yaml"),
    (*ASGK, "handoff-check", "--file", "examples/negative/handoff.missing-active-issue.yaml"),
    (*ASGK, "handoff-check", "--file", "examples/negative/handoff.empty-next-safe-action.yaml"),
    (*ASGK, "handoff-check", "--file", "examples/negative/handoff.unknown-validation-status.yaml"),
    (*ASGK, "handoff-check", "--file", "examples/negative/handoff.missing-allowed-paths.yaml"),
    (*ASGK, "handoff-check", "--file", "examples/negative/handoff.missing-must-read.yaml"),
    (*ASGK, "handoff-check", "--file", "examples/negative/handoff.empty-required-lists.yaml"),
    (*ASGK, "handoff-check", "--file", "examples/negative/handoff.unresolved-todo.yaml", "--fail-on-todo"),
    (
        *ASGK, "closeout-check",
        "--file", "examples/negative/current_status.stale-closeout.md",
        "--completed-issue", "#52",
        "--completed-pr", "#53",
        "--completed-branch", "codex/positive-handoff-template-fixture",
    ),
    (
        *ASGK, "current-status-impact-check",
        "--pr-body", "examples/negative/current_status_impact/pr_body.updated-self-stale.md",
        "--changed-paths-file", "examples/negative/current_status_impact/changed_paths.current-status.txt",
        "--file", "examples/negative/current_status_impact/current_status.self-stale.md",
        "--this-pr", "#134",
        "--closing-issue", "#132",
        "--this-branch", "codex/public-readiness-audit-132",
    ),
    (
        *ASGK, "current-status-impact-check",
        "--pr-body", "examples/negative/current_status_impact/pr_body.not-applicable-status-changed.md",
        "--changed-paths-file", "examples/negative/current_status_impact/changed_paths.current-status.txt",
        "--file", "examples/negative/current_status_impact/current_status.self-stale.md",
    ),
    (
        *ASGK, "current-status-impact-check",
        "--pr-body", "examples/negative/current_status_impact/pr_body.deferred-status-changed.md",
        "--changed-paths-file", "examples/negative/current_status_impact/changed_paths.current-status.txt",
        "--file", "examples/negative/current_status_impact/current_status.self-stale.md",
    ),
    (
        *ASGK, "release-state-check",
        "--tag", "v1.2.0",
        "--release-title", "ASGK v1.2.0",
        "--readme", "examples/negative/release_state/README.stale-v1-2-candidate.md",
    ),
)

RELEASE_STATE_COMMANDS = (
    (*ASGK, "release-state-check", "--tag", "v1.2.0", "--release-title", "ASGK v1.2.0", "--readme", "examples/negative/release_state/README.stale-v1-2-candidate.md"),
    (*ASGK, "release-state-check", "--tag", "v1.6.0", "--release-title", "ASGK v1.6.0", "--release-policy", "examples/negative/release_state/SOURCE_ONLY_RELEASE_POLICY.ledger.md"),
)

WORK_UNIT_COMMANDS = (
    (*ASGK, "work-unit-check", "--json-file", "examples/negative/work_unit.merged-pr.json", "--paths-file", "examples/work_unit.changed-paths.valid.txt"),
    (*ASGK, "work-unit-check", "--json-file", "examples/work_unit.valid-issue.json", "--paths-file", "examples/negative/work_unit.changed-paths.outside-allowed.txt"),
    (*ASGK, "work-unit-check", "--json-file", "examples/negative/work_unit.missing-task-fields.json", "--paths-file", "examples/negative/work_unit.missing-task-fields.paths.txt"),
    (*ASGK, "work-unit-check", "--json-file", "examples/negative/work_unit.reason-alias-only.json", "--authority-only"),
    (*ASGK, "work-unit-check", "--json-file", "examples/negative/work_unit.missing-context-read-set.json", "--authority-only"),
    (*ASGK, "work-unit-check", "--json-file", "examples/negative/work_unit.missing-project-specific-validation.json", "--authority-only"),
)

COMPACT_SCOPE_LOCK_CASES = (
    ("--json-file", "examples/negative/compact_governance/scope-lock.missing-allowed-paths.json"),
    ("--json-file", "examples/compact_governance/scope_lock.valid-issue.json", "--compare-file", "examples/negative/compact_governance/scope-lock.stale-capture.json"),
)

COMPACT_PR_BODY_CASES = (
    ("examples/negative/compact_governance/pr_body.compact.failed-report.md", "examples/negative/compact_governance/pr-report.metadata-unavailable.json"),
    ("examples/negative/compact_governance/pr_body.compact.requires-human-report.md", "examples/negative/compact_governance/reports/pr-report.requires-human-restricted-boundary.json"),
)

COMPACT_HANDOFF_CASES = (
    (
        "--file", "examples/negative/compact_governance/handoff.compact.hides-stale-current-status.yaml",
        "--current-status", "examples/negative/compact_governance/current_status.compact.stale-active.md",
        "--completed-issue", "#240",
        "--completed-pr", "#241",
        "--completed-branch", "codex/compact-pr-body-profile-240",
    ),
)

POLICY_GATE_BASE_FAILURES = (
    "examples/negative/policy_gate/pr_body.missing-merge-decision.md",
    "examples/negative/policy_gate/pr_body.missing-current-status-impact.md",
    "examples/negative/policy_gate/pr_body.updated-missing-post-merge-safe.md",
    "examples/negative/policy_gate/pr_body.see-chat-authority.md",
)

POLICY_GATE_DUAL_MODE_FAILURES = (
    "examples/negative/policy_gate/pr_body.checks-pending.md",
    "examples/negative/policy_gate/pr_body.human-gates-pending.md",
    "examples/negative/policy_gate/pr_body.checks-false.md",
    "examples/negative/policy_gate/pr_body.human-gates-false.md",
    "examples/negative/policy_gate/pr_body.blank-state.md",
    "examples/negative/policy_gate/pr_body.unknown-state.md",
    "examples/negative/policy_gate/pr_body.generic-reason.md",
    "examples/negative/policy_gate/pr_body.duplicate-state.md",
    "examples/negative/policy_gate/pr_body.invalid-validation-source-shape.md",
)

POLICY_GATE_FAILURE_COMMANDS = (
    *_policy_gate_mode_commands(POLICY_GATE_BASE_FAILURES, ("merge-decision",)),
    *_policy_gate_mode_commands(
        POLICY_GATE_DUAL_MODE_FAILURES,
        ("body-coherence", "merge-decision"),
    ),
    (
        "python3",
        "scripts/policy_gate_check.py",
        "--pr-body",
        "examples/pr_body.merge-blocked-draft.valid.md",
    ),
    (
        *ASGK,
        "policy-gate",
        "--github-event",
        "examples/negative/github_events/pr.missing-result.json",
    ),
    (
        *ASGK,
        "policy-gate",
        "--github-event",
        "examples/negative/github_events/pr.missing-pull-request.json",
    ),
)

NEGATIVE_CASE_GROUPS = {
    "changed-paths": NegativeCaseGroup(COMMANDS_PASS, _commands_with_suffix(
        ("python3", "scripts/governance_hygiene.py", "--paths-file"),
        (
            "examples/negative/changed_paths.runtime-artifact.txt",
            "examples/negative/changed_paths.protected.txt",
            "examples/negative/changed_paths.private-binary.txt",
        ),
        ("--expect-blocked",),
    )),
    "textual": NegativeCaseGroup(EXPECTED_FAILURE, TEXTUAL_EXPECTED_FAILURES),
    "policy-gate": NegativeCaseGroup(EXPECTED_FAILURE, POLICY_GATE_FAILURE_COMMANDS),
    "pr-status": NegativeCaseGroup(EXPECTED_FAILURE, _commands(
        (*ASGK, "check-pr", "--json-file"),
        (
            "examples/negative/pr_status.draft-failing.json",
            "examples/negative/pr_status.missing-closing-reference.json",
            "examples/negative/pr_status.changed-path-outside-allowed.json",
            "examples/pr_status.ready-blocked.json",
            "examples/negative/pr_status.merge-blocked-all-clean.json",
            "examples/negative/pr_status.duplicate-check-latest-failure.json",
            "examples/negative/pr_status.duplicate-check-ambiguous.json",
            "examples/negative/pr_status.missing-check-identity.json",
            "examples/negative/pr_status.duplicate-check-missing-provider.json",
        ),
    )),
    "target-install": NegativeCaseGroup(EXPECTED_FAILURE, _commands(
        (*ASGK, "target-install-check", "--repo-root"),
        (
            "examples/negative/target_install/missing_required_files",
            "examples/negative/target_install/repo_local_historical_evidence_surface",
        ),
    )),
    "release-state": NegativeCaseGroup(EXPECTED_FAILURE, RELEASE_STATE_COMMANDS),
    "work-unit": NegativeCaseGroup(EXPECTED_FAILURE, WORK_UNIT_COMMANDS),
    "workspace-state": NegativeCaseGroup(EXPECTED_SUCCESS, _commands_with_suffix(
        (*ASGK, "workspace-state-check", "--json-file"),
        ("examples/negative/workspace_state.stale-branch-untracked.json",),
        ("--expect-warnings",),
    )),
    "compact-issue-scope": NegativeCaseGroup(EXPECTED_FAILURE, _commands(
        (*ASGK, "compact-issue-scope", "--json-file"),
        ("examples/negative/compact_governance/issue-scope.missing-allowed-paths.json",),
    )),
    "compact-scope-lock": NegativeCaseGroup(EXPECTED_FAILURE, _case_commands((*ASGK, "compact-scope-lock"), COMPACT_SCOPE_LOCK_CASES)),
    "compact-pr-report": NegativeCaseGroup(EXPECTED_FAILURE, _commands(
        (*ASGK, "compact-pr-report", "--json-file"),
        (
            "examples/negative/compact_governance/pr-report.claim-conflicts-with-tool-state.json",
            "examples/negative/compact_governance/pr-report.metadata-unavailable.json",
            "examples/negative/compact_governance/pr-report.restricted-boundary-claimed-human-gate.json",
        ),
    )),
    "compact-task-packet": NegativeCaseGroup(EXPECTED_FAILURE, _commands(
        (*ASGK, "compact-task-packet-check", "--json-file"),
        (
            "examples/negative/compact_governance/task-packet-delta-expands-scope.json",
            "examples/negative/compact_governance/task-packet-authority-mismatch.json",
            "examples/negative/compact_governance/task-packet-read-set-expands.json",
            "examples/negative/compact_governance/task-packet-validation-expands.json",
        ),
    )),
    "compact-pr-body": NegativeCaseGroup(EXPECTED_FAILURE, tuple(
        (*ASGK, "compact-pr-body-check", "--body-file", body, "--report-json", report)
        for body, report in COMPACT_PR_BODY_CASES
    )),
    "compact-handoff": NegativeCaseGroup(EXPECTED_FAILURE, _case_commands((*ASGK, "compact-handoff-check"), COMPACT_HANDOFF_CASES)),
    "compact-target-upgrade": NegativeCaseGroup(EXPECTED_FAILURE, _commands(
        (*ASGK, "compact-target-upgrade-check", "--manifest"),
        (
            "examples/negative/compact_governance/target_upgrade/manifest.overwrites-current-status.json",
            "examples/negative/compact_governance/target_upgrade/manifest.default-enabled.json",
        ),
    )),
}


@dataclass(frozen=True)
class TempInput:
    """One deterministic temporary input prepared by the scenario runner."""

    source: str | None = None
    content: str | None = None
    replacements: tuple[tuple[str, str], ...] = ()
    json_transform: str | None = None
    suffix: str = ".json"


@dataclass(frozen=True)
class JsonScenario:
    """Exact machine-readable scenario owned by this registry."""

    name: str
    group: str
    command: tuple[str, ...]
    polarity: str
    expected_result: str
    expected_exit: int
    expected_codes: tuple[str, ...]
    proof_boundary: str
    expected_human_gate_status: str = "not_checked"
    expected_domain_result: str | None = None
    temp_input: TempInput | None = None
    environment: str | None = None
    expected_mechanically_checked: tuple[str, ...] | None = None
    expected_not_checked: tuple[str, ...] | None = None


@dataclass(frozen=True)
class ParityScenario:
    """Byte-for-byte command parity assertion."""

    name: str
    group: str
    left_command: tuple[str, ...]
    right_command: tuple[str, ...]
    polarity: str


POLICY_MERGE_BOUNDARY = (
    "A merge-decision pass proves only that the Merge Decision Record's "
    "merge_allowed claim is mechanically supported by the checked body fields."
)
POLICY_BODY_BOUNDARY = (
    "A body-coherence pass proves only that the PR body is complete and "
    "mechanically coherent for its declared Merge Decision."
)
POLICY_BODY_READ_FAILURE_BOUNDARY = (
    "Only PR body file readability was checked; no PR-body policy evaluation "
    "ran because the supplied file could not be read."
)
POLICY_ROUTING_BOUNDARY = (
    "No body validation mode was selected because GitHub PR event routing "
    "was incomplete or invalid."
)
CHECK_PR_BOUNDARY = (
    "check-pr composes the named mechanical fields from supplied fixture or "
    "captured PR metadata. It does not infer low-risk status, human approval, "
    "or merge authority."
)
CHECK_PR_PARTIAL_BOUNDARY = (
    "check-pr reports only completed mechanical fields from supplied fixture or "
    "captured PR metadata; unavailable file-list or issue-scope surfaces remain "
    "explicitly not checked. It does not infer low-risk status, human approval, "
    "or merge authority."
)
WORK_UNIT_AUTHORITY_BOUNDARY = (
    "Exit 0 in authority-only mode proves only that the supplied open work-unit "
    "authority has the visible 13 fields, mechanically valid execution-gate "
    "shape, and no checked chat-only authority. It checks no diff, implementation, "
    "protected-path approval, human gate, or merge state."
)
TASK_PACKET_BOUNDARY = (
    "Exit 0 proves only that the supplied issue-refinement projection has a "
    "supported shape and does not mechanically expand the supplied issue's paths "
    "or case-sensitive exact read/validation items."
)
TASK_PACKET_UNSUPPORTED_BOUNDARY = (
    "No supported task-packet proof boundary was established."
)
TASK_PACKET_FALLBACK_BOUNDARY = (
    "Exit 0 proves only that the supplied fallback has the supported complete "
    "shape, exact pending_unavailable token, and no mechanically recognized "
    "path-based escalation boundary. It does not verify a GitHub outage, activate "
    "the conditional local-work authority, detect every semantic escalation "
    "trigger, or grant PR, merge, external-action, or human-gate authority."
)
HANDOFF_BOUNDARY = (
    "A passing handoff check proves only that the supplied file has one expected "
    "root, the required typed fields contain material values, validation status "
    "uses the supported enum, and the checked chat/TODO markers are absent. It "
    "does not prove that statements are true, GitHub references are live, paths "
    "are authorized, validation commands ran, work is complete, or a human gate "
    "or merge decision is satisfied."
)
COMPACT_HANDOFF_BOUNDARY = (
    HANDOFF_BOUNDARY
    + " Compact freshness checks additionally prove only local consistency with "
    "the supplied CURRENT_STATUS file and caller-supplied completed references."
)
COMPACT_HANDOFF_IMPACT_INVALID_BOUNDARY = (
    HANDOFF_BOUNDARY
    + " The compact impact block was evaluated and found structurally invalid or "
    "internally inconsistent; CURRENT_STATUS freshness was therefore not checked."
)
COMPACT_HANDOFF_FRESHNESS_INCONSISTENT_BOUNDARY = (
    HANDOFF_BOUNDARY
    + " Compact freshness checks evaluated the supplied CURRENT_STATUS file and "
    "caller-supplied completed references and found a local inconsistency. No live "
    "GitHub state, human approval, PR readiness, or merge authority was established."
)
ISSUE_SCOPE_BOUNDARY = (
    "The compact issue-scope projection checks only the supplied issue's visible "
    "canonical task fields and allowed_paths. It does not grant authority or "
    "prove implementation, approval, or merge readiness."
)
SCOPE_LOCK_BOUNDARY = (
    "The compact scope lock proves only a deterministic projection of the "
    "supplied issue scope and, when requested, records the result of one "
    "captured-hash equality comparison. It grants no authority and proves no "
    "implementation or approval."
)
SCOPE_LOCK_PROJECTION_FAILURE_BOUNDARY = (
    "Issue-scope projection failed; no deterministic scope lock or comparison "
    "proof was produced. No authority, implementation, or approval was established."
)
SCOPE_LOCK_CAPTURE_HASH_MISSING_BOUNDARY = (
    "The current issue scope and its deterministic hash were projected, and the "
    "captured scope-hash presence was checked, but no equality comparison proof "
    "was produced because the capture had no material scope_hash. No authority, "
    "implementation, or approval was established."
)
COMPACT_PR_REPORT_BOUNDARY = (
    "Compiles only mechanically observable PR, issue-scope, scope-lock, check, "
    "explicit-claim-conflict, and restricted-boundary evidence from supplied or "
    "live metadata; it does not infer human approval, low-risk status, or merge authority."
)
COMPACT_PR_FILE_LIST_INCOMPLETE_BOUNDARY = (
    "Compiles only the mechanically observable PR, issue-scope, scope-lock, check, "
    "and explicit-claim-conflict evidence supported by supplied or live metadata. "
    "No restricted-boundary proof was produced because the PR file list was missing "
    "or invalid; it does not infer human approval, low-risk status, or merge authority."
)
COMPACT_PR_PARTIAL_FILE_LIST_WITH_GATE_BOUNDARY = (
    "Compiles mechanically observable PR, issue-scope, scope-lock, check, "
    "explicit-claim-conflict, and restricted-boundary evidence from valid PR file "
    "entries. Invalid entries prevent complete restricted-boundary coverage, but "
    "any observed restricted path still requires a human gate; no approval or "
    "merge authority is inferred."
)
COMPACT_PR_METADATA_UNAVAILABLE_BOUNDARY = (
    "Only the explicit PR metadata-unavailable marker was checked; no PR status, "
    "issue-scope, scope-lock, claim-conflict, or restricted-boundary proof was produced."
)
COMPACT_PR_BODY_BOUNDARY = (
    "Checks only local compact PR-body structure against the supplied compiled "
    "report; it does not prove that report is current or live, or establish "
    "human approval, low-risk status, or merge authority."
)
COMPACT_PR_BODY_INPUT_INCOMPLETE_BOUNDARY = (
    "Only local input availability and the checks supported by readable inputs "
    "were evaluated; unavailable or malformed inputs prevented a complete compact "
    "PR-body/report comparison. No freshness, semantic correctness, human approval, "
    "low-risk status, or merge authority was established."
)
CONTEXT_BUDGET_BOUNDARY = (
    "Estimate covers successfully read UTF-8 text from repo files named in "
    "context_read_set only; "
    "it does not include GitHub issue or PR body text, system/developer prompts, "
    "chat history, tool output, retrieved web/app content, or model completion "
    "tokens. It does not prove that selected context is semantically necessary "
    "or sufficient."
)
CONTEXT_PACKET_FAILURE_BOUNDARY = (
    "No context measurement ran because the task packet failed the canonical "
    "shape evaluator."
)
WORKSPACE_BOUNDARY = (
    "Checks only supplied or locally observed workspace branch, upstream, "
    "merged-state, and untracked-path evidence; it does not infer issue authority, "
    "path authorization, human approval, low-risk status, or merge readiness."
)
WORKSPACE_SUPPLIED_BOUNDARY = (
    "Checks only supplied workspace branch, upstream, merged-state, untracked-path, "
    "and changed-path fields; it does not prove that the fixture is current or live, "
    "and does not infer issue authority, path authorization, human approval, "
    "low-risk status, or merge readiness."
)
WORKSPACE_PAYLOAD_SHAPE_BOUNDARY = (
    "Only the workspace-state payload shape was checked; no branch, upstream, "
    "merged-state, or path evidence was evaluated because required fields were "
    "missing or invalid. It does not infer issue authority, path authorization, "
    "human approval, low-risk status, or merge readiness."
)
WORKSPACE_LOOKUP_INCOMPLETE_BOUNDARY = (
    "Reports only the workspace lookup attempts that completed; failed lookup "
    "surfaces remain explicitly not checked. It does not infer issue authority, "
    "path authorization, human approval, low-risk status, or merge readiness."
)
SOURCE_INVENTORY_PROOF_BOUNDARY = (
    "Exit 0 proves only that the caller-supplied source inventory has the "
    "supported JSON shape and includes the retained ASGK source-reference "
    "paths. It does not prove any listed file exists or is readable, inspect "
    "file contents or semantic correctness, assess a target repository's fit, "
    "layout, governance depth, or adoption readiness, establish human approval, "
    "or grant PR or merge authority."
)
SOURCE_INPUT_FAILURE_BOUNDARY = (
    "No source required-path comparison or live source-tree validation ran "
    "because the supplied input could not be accepted. No target, human "
    "approval, PR-readiness, or merge-authority claim was established."
)
SOURCE_INVENTORY_CHECKED = (
    "supplied source inventory JSON object shape",
    "supplied source inventory path normalization and uniqueness",
    "required ASGK source path membership",
)
SOURCE_INVENTORY_NOT_CHECKED = (
    "source file existence, readability, or contents",
    "semantic correctness of any listed source file",
    "target repository fit, layout, governance depth, or adoption readiness",
    "human approval",
    "PR readiness or merge authority",
)
SOURCE_INPUT_NOT_CHECKED = (
    "required ASGK source path membership",
    *SOURCE_INVENTORY_NOT_CHECKED,
)


RETAINED_JSON_SCENARIOS = (
    JsonScenario(
        "policy_event_allowed",
        "policy-gate",
        (*ASGK, "policy-gate", "--github-event", "examples/github_events/pr.ready-allowed.json", "--json"),
        "positive",
        "pass",
        0,
        (),
        POLICY_MERGE_BOUNDARY,
    ),
    JsonScenario(
        "policy_event_missing_result",
        "policy-gate",
        (*ASGK, "policy-gate", "--github-event", "examples/negative/github_events/pr.missing-result.json", "--json"),
        "negative",
        "fail",
        1,
        ("PG_EVENT_RESULT_INVALID",),
        POLICY_ROUTING_BOUNDARY,
        expected_mechanically_checked=(
            "GitHub event file readability and JSON syntax",
            "GitHub pull-request event routing inputs",
            "exact durable Merge Decision result token",
        ),
        expected_not_checked=(
            "PR body validation because routing failed",
            "PR diff, CI, project tests, or evidence truth",
            "human approval, low-risk status, or merge authority",
        ),
    ),
    JsonScenario(
        "check_pr_valid",
        "pr-status",
        (*ASGK, "check-pr", "--json-file", "examples/pr_status.valid.json", "--json"),
        "positive",
        "pass",
        0,
        (),
        CHECK_PR_BOUNDARY,
    ),
    JsonScenario(
        "check_pr_merge_blocked",
        "pr-status",
        (*ASGK, "check-pr", "--json-file", "examples/pr_status.ready-blocked.json", "--json"),
        "negative",
        "fail",
        1,
        ("PR_MERGE_DECISION_NOT_ALLOWED",),
        CHECK_PR_BOUNDARY,
    ),
    JsonScenario(
        "check_pr_invalid_files_skip_downstream_checks",
        "pr-status",
        (*ASGK, "check-pr", "--json-file", "{temp_input}", "--json"),
        "negative",
        "fail",
        1,
        ("PR_FILES_SHAPE_INVALID",),
        CHECK_PR_PARTIAL_BOUNDARY,
        temp_input=TempInput(
            source="examples/pr_status.valid.json",
            json_transform="check_pr_files_invalid",
        ),
        expected_mechanically_checked=(
            "PR open, draft, and merge-state metadata",
            "status-check presence and top-level shape",
            "strict Merge Decision body validation",
            "GitHub closing issue reference",
            "PR file-list presence and shape",
            "status-check entry shape and latest-run ordering",
        ),
        expected_not_checked=(
            "semantic correctness of PR changes or evidence prose",
            "human approval or current-head approval evidence",
            "low-risk eligibility or merge authority",
            "security, privacy, dependency, or release correctness",
            "closing-issue allowed_paths containment",
            "changed-path hygiene patterns",
        ),
    ),
    JsonScenario(
        "check_pr_missing_status_rollup_skips_ordering",
        "pr-status",
        (*ASGK, "check-pr", "--json-file", "{temp_input}", "--json"),
        "negative",
        "fail",
        1,
        ("PR_STATUS_CHECKS_MISSING",),
        CHECK_PR_PARTIAL_BOUNDARY,
        temp_input=TempInput(
            source="examples/pr_status.valid.json",
            json_transform="check_pr_status_rollup_missing",
        ),
        expected_mechanically_checked=(
            "PR open, draft, and merge-state metadata",
            "status-check presence and top-level shape",
            "strict Merge Decision body validation",
            "GitHub closing issue reference",
            "PR file-list presence and shape",
            "changed-path hygiene patterns",
            "closing-issue allowed_paths containment",
        ),
        expected_not_checked=(
            "semantic correctness of PR changes or evidence prose",
            "human approval or current-head approval evidence",
            "low-risk eligibility or merge authority",
            "security, privacy, dependency, or release correctness",
            "status-check entry shape and latest-run ordering",
        ),
    ),
    JsonScenario(
        "work_unit_authority_valid",
        "work-unit",
        (*ASGK, "work-unit-check", "--json-file", "examples/work_unit.valid-issue.json", "--authority-only", "--json"),
        "positive",
        "pass",
        0,
        (),
        WORK_UNIT_AUTHORITY_BOUNDARY,
        expected_mechanically_checked=(
            "work-unit kind and open state",
            "single visible task-field representation and field uniqueness",
            "chat-only authority exclusion",
            "visible canonical 13-field task identity",
            "context_read_set item syntax and repository containment",
            "repository-file context_read_set existence",
            "project_specific_validation bare-not_applicable reason",
        ),
        expected_not_checked=(
            "changed paths, diff contents, and path hygiene",
            "availability, content, or repository identity of durable pseudo-references",
            "semantic necessity of context references",
            "semantic sufficiency or executability of project_specific_validation",
            "implementation correctness",
            "human approval or protected-path authorization",
            "PR readiness, merge authority, or issue completion",
        ),
    ),
    JsonScenario(
        "work_unit_missing_execution_gate",
        "work-unit",
        (*ASGK, "work-unit-check", "--json-file", "examples/negative/work_unit.missing-context-read-set.json", "--authority-only", "--json"),
        "negative",
        "fail",
        1,
        ("WU_EXECUTION_GATE_MISSING",),
        WORK_UNIT_AUTHORITY_BOUNDARY,
        expected_mechanically_checked=(
            "work-unit kind and open state",
            "single visible task-field representation and field uniqueness",
            "chat-only authority exclusion",
            "visible canonical 13-field task identity",
            "project_specific_validation bare-not_applicable reason",
        ),
        expected_not_checked=(
            "changed paths, diff contents, and path hygiene",
            "availability, content, or repository identity of durable pseudo-references",
            "semantic necessity of context references",
            "semantic sufficiency or executability of project_specific_validation",
            "implementation correctness",
            "human approval or protected-path authorization",
            "PR readiness, merge authority, or issue completion",
            "context_read_set item syntax, existence, and repository containment",
        ),
    ),
    JsonScenario(
        "work_unit_missing_allowed_paths_and_execution_gates",
        "work-unit",
        (
            *ASGK,
            "work-unit-check",
            "--json-file",
            "examples/negative/compact_governance/scope-lock.missing-allowed-paths.json",
            "--paths-file",
            "examples/work_unit.changed-paths.valid.txt",
            "--json",
        ),
        "negative",
        "fail",
        1,
        (
            "WU_REQUIRED_FIELD_MISSING",
            "WU_EXECUTION_GATE_MISSING",
            "WU_EXECUTION_GATE_MISSING",
        ),
        (
            "Exit 0 in post-diff mode proves only that the supplied open "
            "work-unit authority and execution gates are structurally valid and "
            "the supplied changed paths pass mechanical containment and hygiene. "
            "It does not prove implementation correctness, human approval, or "
            "merge authority."
        ),
        expected_mechanically_checked=(
            "work-unit kind and open state",
            "single visible task-field representation and field uniqueness",
            "chat-only authority exclusion",
            "visible canonical 13-field task identity",
            "supplied changed-path presence",
            "changed-path hygiene patterns",
        ),
        expected_not_checked=(
            "availability, content, or repository identity of durable pseudo-references",
            "semantic necessity of context references",
            "semantic sufficiency or executability of project_specific_validation",
            "implementation correctness",
            "human approval or protected-path authorization",
            "PR readiness, merge authority, or issue completion",
            "context_read_set item syntax, existence, and repository containment",
            "project_specific_validation item syntax and bare-not_applicable reason",
            "allowed_paths containment",
        ),
    ),
    JsonScenario(
        "task_packet_valid",
        "compact-task-packet",
        (*ASGK, "task-packet-check", "--json-file", "examples/compact_governance/task_packet_delta.valid.json", "--json"),
        "positive",
        "pass",
        0,
        (),
        TASK_PACKET_BOUNDARY,
    ),
    JsonScenario(
        "task_packet_expands_scope",
        "compact-task-packet",
        (*ASGK, "task-packet-check", "--json-file", "examples/negative/compact_governance/task-packet-delta-expands-scope.json", "--json"),
        "negative",
        "fail",
        1,
        ("TP_ALLOWED_PATH_EXPANSION",),
        TASK_PACKET_BOUNDARY,
    ),
    JsonScenario(
        "task_packet_unsupported_mode_skips_field_shape",
        "compact-task-packet",
        (*ASGK, "task-packet-check", "--file", "{temp_input}", "--json"),
        "negative",
        "fail",
        1,
        ("TP_MODE_UNSUPPORTED",),
        TASK_PACKET_UNSUPPORTED_BOUNDARY,
        temp_input=TempInput(
            content='{"mode":"unsupported","surprise":{"nested":true}}'
        ),
        expected_mechanically_checked=(
            "packet mode presence, scalar type, and supported token",
        ),
        expected_not_checked=(
            "mode-specific field presence and shape",
            "issue identity, open state, and source authority",
            "allowed_paths non-expansion",
            "context_read_set exact-item non-expansion",
            "project_specific_validation exact-item non-expansion",
            "whether GitHub was actually unavailable",
            "availability, content, or repository identity of durable pseudo-references",
            "semantic necessity of context references",
            "semantic equivalence of read-set or validation items",
            "semantic sufficiency or executability of project-specific validation",
            "non-path escalation triggers such as dependencies, credentials, external services, or policy meaning",
            "implementation correctness",
            "PR readiness, human approval, merge authority, or issue completion",
        ),
    ),
    JsonScenario(
        "task_packet_pseudo_ref_does_not_claim_file_existence",
        "compact-task-packet",
        (*ASGK, "task-packet-check", "--file", "{temp_input}", "--json"),
        "positive",
        "pass",
        0,
        (),
        TASK_PACKET_FALLBACK_BOUNDARY,
        temp_input=TempInput(
            source="examples/task_packet.valid.json",
            replacements=(
                (
                    '"AGENTS.md",\n    "examples/task_packet.valid.json"',
                    '"#335"',
                ),
            ),
        ),
        expected_mechanically_checked=(
            "packet mode presence, scalar type, and supported token",
            "mode-specific field presence and shape",
            "legacy-field exclusion",
            "context_read_set item syntax and repository containment",
            "project-specific validation bare-not_applicable reason",
            "known path-based fallback escalation boundaries",
        ),
        expected_not_checked=(
            "whether GitHub was actually unavailable",
            "availability, content, or repository identity of durable pseudo-references",
            "semantic necessity of context references",
            "semantic equivalence of read-set or validation items",
            "semantic sufficiency or executability of project-specific validation",
            "non-path escalation triggers such as dependencies, credentials, external services, or policy meaning",
            "implementation correctness",
            "PR readiness, human approval, merge authority, or issue completion",
        ),
    ),
    JsonScenario(
        "handoff_valid",
        "handoff",
        (*ASGK, "handoff-check", "--file", "examples/handoff_packet.valid.yaml", "--fail-on-todo", "--json"),
        "positive",
        "pass",
        0,
        (),
        HANDOFF_BOUNDARY,
    ),
    JsonScenario(
        "handoff_invalid_status",
        "handoff",
        (*ASGK, "handoff-check", "--file", "examples/negative/handoff.unknown-validation-status.yaml", "--json"),
        "negative",
        "fail",
        1,
        ("HP_VALIDATION_STATUS_INVALID",),
        HANDOFF_BOUNDARY,
    ),
    JsonScenario(
        "compact_handoff_valid",
        "compact-handoff",
        (*ASGK, "compact-handoff-check", "--file", "examples/compact_governance/handoff.compact.valid.yaml", "--current-status", "examples/compact_governance/current_status.compact.clean.md", "--json"),
        "positive",
        "pass",
        0,
        (),
        COMPACT_HANDOFF_BOUNDARY,
    ),
    JsonScenario(
        "compact_handoff_invalid_core",
        "compact-handoff",
        (*ASGK, "compact-handoff-check", "--file", "examples/negative/compact_governance/handoff.compact.invalid-core.yaml", "--current-status", "examples/compact_governance/current_status.compact.clean.md", "--json"),
        "negative",
        "fail",
        1,
        ("HP_FIELD_TYPE_INVALID",),
        HANDOFF_BOUNDARY,
    ),
    JsonScenario(
        "compact_handoff_invalid_impact_does_not_claim_consistency",
        "compact-handoff",
        (
            *ASGK,
            "compact-handoff-check",
            "--file",
            "{temp_input}",
            "--current-status",
            "examples/compact_governance/current_status.compact.clean.md",
            "--json",
        ),
        "negative",
        "fail",
        1,
        ("CH_CURRENT_STATUS_IMPACT_FIELD_MISSING",),
        COMPACT_HANDOFF_IMPACT_INVALID_BOUNDARY,
        temp_input=TempInput(
            source="examples/compact_governance/handoff.compact.valid.yaml",
            replacements=(
                ('    follow_up_issue: "none"\n', ""),
            ),
            suffix=".yaml",
        ),
    ),
    JsonScenario(
        "compact_handoff_stale_refs_do_not_claim_consistency",
        "compact-handoff",
        (
            *ASGK,
            "compact-handoff-check",
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
            "--json",
        ),
        "negative",
        "fail",
        1,
        (
            "CH_STALE_COMPLETED_ISSUE",
            "CH_STALE_COMPLETED_PR",
            "CH_STALE_COMPLETED_BRANCH",
        ),
        COMPACT_HANDOFF_FRESHNESS_INCONSISTENT_BOUNDARY,
    ),
    JsonScenario(
        "compact_issue_scope_valid",
        "compact-issue-scope",
        (*ASGK, "compact-issue-scope", "--json-file", "examples/compact_governance/issue_scope.valid-issue.json", "--json"),
        "positive",
        "pass",
        0,
        (),
        ISSUE_SCOPE_BOUNDARY,
    ),
    JsonScenario(
        "compact_issue_scope_missing_field",
        "compact-issue-scope",
        (*ASGK, "compact-issue-scope", "--json-file", "examples/negative/compact_governance/issue-scope.missing-allowed-paths.json", "--json"),
        "negative",
        "fail",
        1,
        ("CIS_REQUIRED_FIELD_MISSING",),
        ISSUE_SCOPE_BOUNDARY,
    ),
    JsonScenario(
        "compact_scope_lock_valid",
        "compact-scope-lock",
        (*ASGK, "compact-scope-lock", "--json-file", "examples/compact_governance/scope_lock.valid-issue.json", "--json"),
        "positive",
        "pass",
        0,
        (),
        SCOPE_LOCK_BOUNDARY,
    ),
    JsonScenario(
        "compact_scope_lock_mismatch",
        "compact-scope-lock",
        (*ASGK, "compact-scope-lock", "--json-file", "examples/compact_governance/scope_lock.valid-issue.json", "--compare-file", "examples/negative/compact_governance/scope-lock.stale-capture.json", "--json"),
        "negative",
        "fail",
        1,
        ("CSL_HASH_MISMATCH",),
        SCOPE_LOCK_BOUNDARY,
    ),
    JsonScenario(
        "compact_scope_lock_projection_failure",
        "compact-scope-lock",
        (*ASGK, "compact-scope-lock", "--json-file", "examples/negative/compact_governance/scope-lock.missing-allowed-paths.json", "--json"),
        "negative",
        "fail",
        1,
        ("CIS_REQUIRED_FIELD_MISSING",),
        SCOPE_LOCK_PROJECTION_FAILURE_BOUNDARY,
        expected_mechanically_checked=(
            "canonical issue-scope projection",
        ),
        expected_not_checked=(
            "implementation correctness or diff contents",
            "whether the issue scope is semantically sufficient",
            "human approval, low-risk status, or merge authority",
            "deterministic SHA-256 scope hash",
        ),
    ),
    JsonScenario(
        "compact_scope_lock_capture_hash_missing_skips_equality",
        "compact-scope-lock",
        (
            *ASGK,
            "compact-scope-lock",
            "--json-file",
            "examples/compact_governance/scope_lock.valid-issue.json",
            "--compare-file",
            "examples/pr_status.valid.json",
            "--json",
        ),
        "negative",
        "fail",
        1,
        ("CSL_CAPTURE_HASH_MISSING",),
        SCOPE_LOCK_CAPTURE_HASH_MISSING_BOUNDARY,
        expected_mechanically_checked=(
            "canonical issue-scope projection",
            "deterministic SHA-256 scope hash",
            "captured scope-hash presence",
        ),
        expected_not_checked=(
            "implementation correctness or diff contents",
            "whether the issue scope is semantically sufficient",
            "human approval, low-risk status, or merge authority",
            "captured scope-hash equality",
        ),
    ),
    JsonScenario(
        "compact_pr_report_valid",
        "compact-pr-report",
        (*ASGK, "compact-pr-report", "--json-file", "examples/compact_governance/pr_report.valid-pr.json", "--json"),
        "positive",
        "pass",
        0,
        (),
        COMPACT_PR_REPORT_BOUNDARY,
    ),
    JsonScenario(
        "compact_pr_report_metadata_unavailable",
        "compact-pr-report",
        (*ASGK, "compact-pr-report", "--json-file", "examples/negative/compact_governance/pr-report.metadata-unavailable.json", "--json"),
        "negative",
        "blocked",
        1,
        ("CPR_METADATA_UNAVAILABLE",),
        COMPACT_PR_METADATA_UNAVAILABLE_BOUNDARY,
        expected_domain_result="fail_closed",
        expected_mechanically_checked=(
            "PR metadata availability marker",
        ),
        expected_not_checked=(
            "strict check-pr projection",
            "closing-issue reference, canonical scope, or deterministic scope lock",
            "agent-authored claim conflicts",
            "changed-path restricted-boundary patterns",
            "human approval, low-risk status, or merge authority",
        ),
    ),
    JsonScenario(
        "compact_pr_report_invalid_files_skip_restricted_boundary",
        "compact-pr-report",
        (*ASGK, "compact-pr-report", "--json-file", "{temp_input}", "--json"),
        "negative",
        "fail",
        1,
        ("PR_FILES_SHAPE_INVALID",),
        COMPACT_PR_FILE_LIST_INCOMPLETE_BOUNDARY,
        temp_input=TempInput(
            source="examples/compact_governance/pr_report.valid-pr.json",
            json_transform="check_pr_files_invalid",
        ),
        expected_mechanically_checked=(
            "PR metadata availability and strict check-pr projection",
            "closing-issue reference presence",
            "agent-authored claim conflicts",
            "closing-issue canonical scope and deterministic scope lock",
        ),
        expected_not_checked=(
            "truth or freshness of fixture/captured metadata",
            "semantic correctness of the PR diff or issue scope",
            "current-head human approval, low-risk status, or merge authority",
            "changed-path restricted-boundary patterns",
        ),
    ),
    JsonScenario(
        "compact_pr_report_invalid_and_restricted_files_preserve_gate",
        "compact-pr-report",
        (*ASGK, "compact-pr-report", "--json-file", "{temp_input}", "--json"),
        "negative",
        "blocked",
        1,
        (
            "PR_FILES_SHAPE_INVALID",
            "CPR_RESTRICTED_BOUNDARY_REQUIRES_HUMAN",
        ),
        COMPACT_PR_PARTIAL_FILE_LIST_WITH_GATE_BOUNDARY,
        expected_human_gate_status="required",
        expected_domain_result="fail",
        temp_input=TempInput(
            source="examples/compact_governance/pr_report.valid-pr.json",
            json_transform="compact_pr_restricted_boundary_with_invalid_file",
        ),
        expected_mechanically_checked=(
            "PR metadata availability and strict check-pr projection",
            "closing-issue reference presence",
            "agent-authored claim conflicts",
            "restricted-boundary patterns for valid PR file entries",
            "closing-issue canonical scope and deterministic scope lock",
        ),
        expected_not_checked=(
            "truth or freshness of fixture/captured metadata",
            "semantic correctness of the PR diff or issue scope",
            "current-head human approval, low-risk status, or merge authority",
            "complete changed-path restricted-boundary coverage",
        ),
    ),
    JsonScenario(
        "compact_pr_body_valid",
        "compact-pr-body",
        (*ASGK, "compact-pr-body-check", "--body-file", "examples/compact_governance/pr_body.compact.valid.md", "--report-json", "examples/compact_governance/pr_report_body_profile.valid-report.json", "--json"),
        "positive",
        "pass",
        0,
        (),
        COMPACT_PR_BODY_BOUNDARY,
    ),
    JsonScenario(
        "compact_pr_body_blocked_report",
        "compact-pr-body",
        (*ASGK, "compact-pr-body-check", "--body-file", "examples/negative/compact_governance/pr_body.compact.requires-human-report.md", "--report-json", "examples/negative/compact_governance/reports/pr-report.requires-human-restricted-boundary.json", "--json"),
        "negative",
        "fail",
        1,
        (
            "CPB_REPORT_DERIVED_STATE_NOT_CHECKABLE",
            "CPB_REPORT_RESULT_NOT_PASS",
        ),
        COMPACT_PR_BODY_BOUNDARY,
    ),
    JsonScenario(
        "compact_pr_body_malformed_findings_fail_closed",
        "compact-pr-body",
        (
            *ASGK,
            "compact-pr-body-check",
            "--body-file",
            "examples/compact_governance/pr_body.compact.valid.md",
            "--report-json",
            "{temp_input}",
            "--json",
        ),
        "negative",
        "fail",
        1,
        ("CPB_REPORT_FINDINGS_TYPE_INVALID",),
        COMPACT_PR_BODY_BOUNDARY,
        temp_input=TempInput(
            content=(
                '{"result":"pass","pr_status_result":"pass",'
                '"derived_state":"checkable_pass","low_risk_inferred":false,'
                '"findings":"blocking finding hidden in wrong type"}'
            ),
        ),
    ),
    JsonScenario(
        "context_budget_valid",
        "context-budget",
        (*ASGK, "context-budget-measure", "--task-packet", "examples/task_packet.valid.json", "--json"),
        "positive",
        "pass",
        0,
        (),
        CONTEXT_BUDGET_BOUNDARY,
    ),
    JsonScenario(
        "context_budget_rejects_overbroad",
        "context-budget",
        (*ASGK, "context-budget-measure", "--task-packet", "examples/negative/task_packet.overbroad-context-read-set.yaml", "--json"),
        "negative",
        "fail",
        1,
        ("TP_READ_SET_OVERBROAD",),
        CONTEXT_PACKET_FAILURE_BOUNDARY,
    ),
    JsonScenario(
        "context_budget_unsupported_mode_skips_field_and_context_checks",
        "context-budget",
        (
            *ASGK,
            "context-budget-measure",
            "--task-packet",
            "{temp_input}",
            "--json",
        ),
        "negative",
        "fail",
        1,
        ("TP_MODE_UNSUPPORTED",),
        CONTEXT_PACKET_FAILURE_BOUNDARY,
        temp_input=TempInput(
            content='{"mode":"unsupported","context_read_set":[123]}'
        ),
        expected_mechanically_checked=(
            "task-packet mode presence, scalar type, and supported token",
        ),
        expected_not_checked=(
            "mode-specific task-packet field presence and type shape",
            "context_read_set item syntax, repository-file existence, and containment",
            "repo-file byte, character, or token estimates",
            "semantic necessity or sufficiency of selected context",
            "human approval, low-risk status, or merge authority",
        ),
    ),
    JsonScenario(
        "workspace_clean",
        "workspace-state",
        (*ASGK, "workspace-state-check", "--json-file", "examples/workspace_state.clean.json", "--json"),
        "positive",
        "pass",
        0,
        (),
        WORKSPACE_SUPPLIED_BOUNDARY,
    ),
    JsonScenario(
        "workspace_warning",
        "workspace-state",
        (*ASGK, "workspace-state-check", "--json-file", "examples/negative/workspace_state.stale-branch-untracked.json", "--json"),
        "negative",
        "warning",
        0,
        ("WS_BRANCH_STALE", "WS_UNTRACKED_PATHS"),
        WORKSPACE_SUPPLIED_BOUNDARY,
    ),
    JsonScenario(
        "policy_event_draft_blocked",
        "policy-gate",
        (*ASGK, "policy-gate", "--github-event", "examples/github_events/pr.draft-blocked.json", "--json"),
        "positive",
        "pass",
        0,
        (),
        POLICY_BODY_BOUNDARY,
    ),
    JsonScenario(
        "policy_event_ready_blocked",
        "policy-gate",
        (*ASGK, "policy-gate", "--github-event", "examples/github_events/pr.ready-blocked.json", "--json"),
        "positive",
        "pass",
        0,
        (),
        POLICY_BODY_BOUNDARY,
    ),
    JsonScenario(
        "policy_direct_default_is_strict",
        "policy-gate",
        ("python3", "scripts/policy_gate_check.py", "--pr-body", "examples/pr_body.merge-blocked-draft.valid.md", "--json"),
        "negative",
        "fail",
        1,
        (
            "PG_GATE_NOT_TRUE",
            "PG_GATE_NOT_TRUE",
            "PG_STRICT_RESULT_NOT_ALLOWED",
        ),
        POLICY_MERGE_BOUNDARY,
    ),
    JsonScenario(
        "policy_quoted_result_fails_closed",
        "policy-gate",
        (*ASGK, "policy-gate", "--github-event", "{temp_input}", "--json"),
        "negative",
        "fail",
        1,
        ("PG_EVENT_RESULT_INVALID",),
        POLICY_ROUTING_BOUNDARY,
        temp_input=TempInput(
            source="examples/github_events/pr.ready-allowed.json",
            json_transform="policy_quoted_result",
        ),
    ),
    JsonScenario(
        "policy_uppercase_result_fails_closed",
        "policy-gate",
        (*ASGK, "policy-gate", "--github-event", "{temp_input}", "--json"),
        "negative",
        "fail",
        1,
        ("PG_EVENT_RESULT_INVALID",),
        POLICY_ROUTING_BOUNDARY,
        temp_input=TempInput(
            source="examples/github_events/pr.ready-allowed.json",
            json_transform="policy_uppercase_result",
        ),
    ),
    JsonScenario(
        "policy_quoted_boolean_rejected",
        "policy-gate",
        (*ASGK, "policy-gate", "--github-event", "{temp_input}", "--json"),
        "negative",
        "fail",
        1,
        ("PG_GATE_NOT_TRUE",),
        POLICY_MERGE_BOUNDARY,
        temp_input=TempInput(
            source="examples/github_events/pr.ready-allowed.json",
            json_transform="policy_quoted_boolean",
        ),
    ),
    JsonScenario(
        "check_pr_latest_success",
        "pr-status",
        (*ASGK, "check-pr", "--json-file", "examples/pr_status.duplicate-check-latest-success.json", "--json"),
        "positive",
        "pass",
        0,
        (),
        CHECK_PR_BOUNDARY,
    ),
    JsonScenario(
        "check_pr_latest_failure",
        "pr-status",
        (*ASGK, "check-pr", "--json-file", "examples/negative/pr_status.duplicate-check-latest-failure.json", "--json"),
        "negative",
        "fail",
        1,
        ("PR_STATUS_CHECK_NOT_PASSING", "PR_STATUS_CHECK_PENDING"),
        CHECK_PR_BOUNDARY,
    ),
    JsonScenario(
        "check_pr_ambiguous_latest",
        "pr-status",
        (*ASGK, "check-pr", "--json-file", "examples/negative/pr_status.duplicate-check-ambiguous.json", "--json"),
        "negative",
        "fail",
        1,
        ("PR_STATUS_CHECK_ORDERING_AMBIGUOUS",),
        CHECK_PR_BOUNDARY,
    ),
    JsonScenario(
        "workspace_warning_strict",
        "workspace-state",
        (*ASGK, "workspace-state-check", "--json-file", "examples/negative/workspace_state.stale-branch-untracked.json", "--strict", "--json"),
        "negative",
        "warning",
        1,
        ("WS_BRANCH_STALE", "WS_UNTRACKED_PATHS"),
        WORKSPACE_SUPPLIED_BOUNDARY,
    ),
    JsonScenario(
        "workspace_expected_warning_present",
        "workspace-state",
        (*ASGK, "workspace-state-check", "--json-file", "examples/negative/workspace_state.stale-branch-untracked.json", "--expect-warnings", "--json"),
        "negative",
        "warning",
        0,
        ("WS_BRANCH_STALE", "WS_UNTRACKED_PATHS"),
        WORKSPACE_SUPPLIED_BOUNDARY,
    ),
    JsonScenario(
        "workspace_expected_warning_missing",
        "workspace-state",
        (*ASGK, "workspace-state-check", "--json-file", "examples/workspace_state.clean.json", "--expect-warnings", "--json"),
        "negative",
        "fail",
        1,
        ("WS_EXPECTED_WARNING_MISSING",),
        WORKSPACE_SUPPLIED_BOUNDARY,
    ),
    JsonScenario(
        "compact_pr_report_requires_human",
        "compact-pr-report",
        (*ASGK, "compact-pr-report", "--json-file", "{temp_input}", "--json"),
        "negative",
        "blocked",
        1,
        ("CPR_RESTRICTED_BOUNDARY_REQUIRES_HUMAN",),
        COMPACT_PR_REPORT_BOUNDARY,
        expected_human_gate_status="required",
        expected_domain_result="requires_human",
        temp_input=TempInput(
            source="examples/compact_governance/pr_report.valid-pr.json",
            json_transform="compact_pr_restricted_boundary",
        ),
    ),
    JsonScenario(
        "compact_pr_report_mixed_failure_and_human_gate",
        "compact-pr-report",
        (*ASGK, "compact-pr-report", "--json-file", "{temp_input}", "--json"),
        "negative",
        "blocked",
        1,
        (
            "CPR_RESTRICTED_BOUNDARY_REQUIRES_HUMAN",
            "PR_MERGE_STATE_NOT_CLEAN",
        ),
        COMPACT_PR_REPORT_BOUNDARY,
        expected_human_gate_status="required",
        expected_domain_result="fail",
        temp_input=TempInput(
            source="examples/compact_governance/pr_report.valid-pr.json",
            json_transform="compact_pr_restricted_boundary_with_mechanical_failure",
        ),
    ),
    JsonScenario(
        "source_inventory_reference_superset",
        "source-validation",
        (
            *ASGK,
            "validate",
            "--source-inventory-file",
            "examples/source_validation/reference-superset.valid.json",
            "--json",
        ),
        "positive",
        "pass",
        0,
        (),
        SOURCE_INVENTORY_PROOF_BOUNDARY,
        expected_mechanically_checked=SOURCE_INVENTORY_CHECKED,
        expected_not_checked=SOURCE_INVENTORY_NOT_CHECKED,
    ),
    JsonScenario(
        "source_inventory_missing_required_path",
        "source-validation",
        (
            *ASGK,
            "validate",
            "--source-inventory-file",
            "examples/negative/source_validation/missing-required-path.json",
            "--json",
        ),
        "negative",
        "fail",
        1,
        ("SV_REQUIRED_PATH_MISSING",),
        SOURCE_INVENTORY_PROOF_BOUNDARY,
        expected_mechanically_checked=SOURCE_INVENTORY_CHECKED,
        expected_not_checked=SOURCE_INVENTORY_NOT_CHECKED,
    ),
)


WORK_UNIT_INPUT_BOUNDARY = (
    "No work-unit evaluation ran because its command input, durable source, "
    "or changed-path source was invalid."
)
TASK_PACKET_INPUT_BOUNDARY = (
    "No task-packet evaluation ran because its command input or supplied "
    "authority source was invalid."
)
POLICY_EVENT_JSON_BOUNDARY = (
    "No event routing or PR-body validation ran because the supplied GitHub "
    "event was not valid JSON."
)
POLICY_EVENT_FILE_BOUNDARY = (
    "No event routing or PR-body validation ran because the supplied GitHub "
    "event file could not be read."
)
CHECK_PR_MODE_BOUNDARY = (
    "No PR status evaluation ran because the input mode was invalid."
)
CHECK_PR_JSON_BOUNDARY = (
    "No PR status evaluation ran because the supplied payload was not valid JSON."
)
CHECK_PR_FILE_BOUNDARY = (
    "No PR status evaluation ran because the supplied payload file could not be read."
)
CHECK_PR_LIVE_BOUNDARY = (
    "No PR status evaluation ran because live GitHub metadata could not be retrieved."
)
CHECK_PR_LIVE_INVALID_BOUNDARY = (
    "No PR status evaluation ran because the live lookup response was not valid JSON."
)
CIS_JSON_BOUNDARY = (
    "No canonical issue-scope projection ran because the supplied payload was "
    "not valid JSON."
)
CIS_FILE_BOUNDARY = (
    "No canonical issue-scope projection ran because the supplied payload file "
    "could not be read."
)
CIS_LIVE_BOUNDARY = (
    "No canonical issue-scope projection ran because the issue payload was "
    "unavailable or invalid."
)
CIS_LIVE_INVALID_BOUNDARY = (
    "No canonical issue-scope projection ran because the live issue payload "
    "was invalid."
)
CSL_JSON_BOUNDARY = (
    "No scope lock ran because the supplied payload was not valid JSON."
)
CSL_FILE_BOUNDARY = (
    "No scope lock ran because the supplied payload file could not be read."
)
CSL_LIVE_BOUNDARY = (
    "No scope lock ran because the issue payload was unavailable or invalid."
)
CSL_LIVE_INVALID_BOUNDARY = (
    "No scope lock ran because the live issue payload was invalid."
)
CSL_COMPARE_JSON_BOUNDARY = (
    "The current scope projection may have run, but no comparison proof exists "
    "because the captured lock was not valid JSON."
)
CPR_JSON_BOUNDARY = (
    "No compact PR report was compiled because the supplied payload was not "
    "valid JSON."
)
CPR_FILE_BOUNDARY = (
    "No compact PR report was compiled because the supplied payload could not be read."
)
CPR_LIVE_BOUNDARY = (
    "No compact PR report was compiled because live GitHub metadata could not "
    "be retrieved."
)
CPR_LIVE_INVALID_BOUNDARY = (
    "No compact PR report was compiled because live GitHub metadata was invalid."
)
COMPACT_HANDOFF_STATUS_UNAVAILABLE_BOUNDARY = (
    HANDOFF_BOUNDARY
    + " The compact impact block passed, but full freshness was not checked "
    "because CURRENT_STATUS was missing or failed its local structural check."
)
CONTEXT_JSON_BOUNDARY = (
    "No context measurement ran because the task packet was not valid JSON."
)
CONTEXT_FILE_BOUNDARY = (
    "No context measurement ran because the task packet was unreadable."
)
WORKSPACE_JSON_BOUNDARY = (
    "No workspace-state evaluation ran because the supplied fixture was not "
    "valid JSON."
)
WORKSPACE_FILE_BOUNDARY = (
    "No workspace-state evaluation ran because the supplied fixture could not be read."
)


CONTROLLED_ERROR_SCENARIOS = (
    JsonScenario(
        "policy_body_file_missing",
        "controlled-errors",
        (*ASGK, "policy-gate", "--pr-body", "__asgk_missing__/pr-body.md", "--json"),
        "negative",
        "fail",
        1,
        ("PG_BODY_READ_FAILED",),
        POLICY_BODY_READ_FAILURE_BOUNDARY,
        expected_mechanically_checked=(
            "PR body file readability",
        ),
        expected_not_checked=(
            "required PR body sections",
            "Current Status Impact field shape and consistency",
            "merge-decision Merge Decision field shape and gate tokens",
            "chat-only authority phrase rejection",
            "PR diff, CI, project tests, or evidence truth",
            "human approval, current-head approval, or merge authority",
        ),
    ),
    JsonScenario(
        "policy_event_file_missing",
        "controlled-errors",
        (*ASGK, "policy-gate", "--github-event", "__asgk_missing__/event.json", "--json"),
        "negative",
        "fail",
        1,
        ("PG_EVENT_FILE_UNREADABLE",),
        POLICY_EVENT_FILE_BOUNDARY,
    ),
    JsonScenario(
        "policy_event_json_malformed",
        "controlled-errors",
        (*ASGK, "policy-gate", "--github-event", "{temp_input}", "--json"),
        "negative",
        "fail",
        1,
        ("PG_EVENT_JSON_INVALID",),
        POLICY_EVENT_JSON_BOUNDARY,
        temp_input=TempInput(content="{"),
    ),
    JsonScenario(
        "policy_event_mode_override_forbidden",
        "controlled-errors",
        (*ASGK, "policy-gate", "--github-event", "examples/github_events/pr.ready-allowed.json", "--mode", "merge-decision", "--json"),
        "negative",
        "fail",
        1,
        ("PG_EVENT_MODE_OVERRIDE_FORBIDDEN",),
        POLICY_ROUTING_BOUNDARY,
        expected_mechanically_checked=(
            "policy-gate command input mode",
            "GitHub event mode-override prohibition",
        ),
        expected_not_checked=(
            "GitHub event file readability, JSON syntax, or pull-request routing inputs",
            "exact durable Merge Decision result token",
            "PR body validation because routing failed",
            "PR diff, CI, project tests, or evidence truth",
            "human approval, low-risk status, or merge authority",
        ),
    ),
    JsonScenario(
        "policy_event_shape_invalid",
        "controlled-errors",
        (*ASGK, "policy-gate", "--github-event", "{temp_input}", "--json"),
        "negative",
        "fail",
        1,
        ("PG_EVENT_SHAPE_INVALID",),
        POLICY_ROUTING_BOUNDARY,
        temp_input=TempInput(content="[]"),
        expected_mechanically_checked=(
            "GitHub event file readability and JSON syntax",
            "GitHub event top-level shape",
        ),
        expected_not_checked=(
            "pull-request event routing inputs",
            "exact durable Merge Decision result token",
            "PR body validation because routing failed",
            "PR diff, CI, project tests, or evidence truth",
            "human approval, low-risk status, or merge authority",
        ),
    ),
    JsonScenario(
        "policy_event_pull_request_missing",
        "controlled-errors",
        (*ASGK, "policy-gate", "--github-event", "examples/negative/github_events/pr.missing-pull-request.json", "--json"),
        "negative",
        "fail",
        1,
        ("PG_EVENT_PULL_REQUEST_MISSING",),
        POLICY_ROUTING_BOUNDARY,
        expected_mechanically_checked=(
            "GitHub event file readability and JSON syntax",
            "GitHub event top-level shape",
            "pull_request object presence",
        ),
        expected_not_checked=(
            "exact durable Merge Decision result token",
            "PR body validation because routing failed",
            "PR diff, CI, project tests, or evidence truth",
            "human approval, low-risk status, or merge authority",
        ),
    ),
    JsonScenario(
        "check_pr_input_mode_invalid",
        "controlled-errors",
        (*ASGK, "check-pr", "--json"),
        "negative",
        "fail",
        1,
        ("PR_INPUT_MODE_INVALID",),
        CHECK_PR_MODE_BOUNDARY,
    ),
    JsonScenario(
        "check_pr_file_missing",
        "controlled-errors",
        (*ASGK, "check-pr", "--json-file", "__asgk_missing__/pr.json", "--json"),
        "negative",
        "fail",
        1,
        ("PR_PAYLOAD_FILE_UNREADABLE",),
        CHECK_PR_FILE_BOUNDARY,
    ),
    JsonScenario(
        "check_pr_json_malformed",
        "controlled-errors",
        (*ASGK, "check-pr", "--json-file", "{temp_input}", "--json"),
        "negative",
        "fail",
        1,
        ("PR_PAYLOAD_JSON_INVALID",),
        CHECK_PR_JSON_BOUNDARY,
        temp_input=TempInput(content="{"),
    ),
    JsonScenario(
        "check_pr_live_lookup_unavailable",
        "controlled-errors",
        (*ASGK, "check-pr", "--pr", "999", "--json"),
        "negative",
        "blocked",
        1,
        ("PR_LIVE_LOOKUP_FAILED",),
        CHECK_PR_LIVE_BOUNDARY,
        environment="gh_fail",
    ),
    JsonScenario(
        "work_unit_input_mode_invalid",
        "controlled-errors",
        (*ASGK, "work-unit-check", "--json-file", "examples/work_unit.valid-issue.json", "--json"),
        "negative",
        "fail",
        1,
        ("WU_INPUT_MODE_INVALID",),
        WORK_UNIT_INPUT_BOUNDARY,
    ),
    JsonScenario(
        "work_unit_file_missing",
        "controlled-errors",
        (*ASGK, "work-unit-check", "--json-file", "__asgk_missing__/work-unit.json", "--authority-only", "--json"),
        "negative",
        "fail",
        1,
        ("WU_INPUT_FILE_UNREADABLE",),
        WORK_UNIT_INPUT_BOUNDARY,
    ),
    JsonScenario(
        "work_unit_json_malformed",
        "controlled-errors",
        (*ASGK, "work-unit-check", "--json-file", "{temp_input}", "--authority-only", "--json"),
        "negative",
        "fail",
        1,
        ("WU_INPUT_JSON_INVALID",),
        WORK_UNIT_INPUT_BOUNDARY,
        temp_input=TempInput(content="{"),
    ),
    JsonScenario(
        "work_unit_live_lookup_unavailable",
        "controlled-errors",
        (*ASGK, "work-unit-check", "--issue", "999", "--authority-only", "--json"),
        "negative",
        "blocked",
        1,
        ("WU_LIVE_LOOKUP_FAILED",),
        WORK_UNIT_INPUT_BOUNDARY,
        environment="gh_fail",
    ),
    JsonScenario(
        "work_unit_git_diff_unavailable",
        "controlled-errors",
        (*ASGK, "work-unit-check", "--json-file", "examples/work_unit.valid-issue.json", "--git-base", "__asgk_missing_base__", "--git-head", "HEAD", "--json"),
        "negative",
        "blocked",
        1,
        ("WU_GIT_DIFF_FAILED",),
        WORK_UNIT_INPUT_BOUNDARY,
    ),
    JsonScenario(
        "task_packet_input_mode_invalid",
        "controlled-errors",
        (*ASGK, "task-packet-check", "--json"),
        "negative",
        "fail",
        1,
        ("TP_INPUT_MODE_INVALID",),
        TASK_PACKET_INPUT_BOUNDARY,
    ),
    JsonScenario(
        "task_packet_file_missing",
        "controlled-errors",
        (*ASGK, "task-packet-check", "--json-file", "__asgk_missing__/task-packet.json", "--json"),
        "negative",
        "fail",
        1,
        ("TP_INPUT_FILE_UNREADABLE",),
        TASK_PACKET_INPUT_BOUNDARY,
    ),
    JsonScenario(
        "task_packet_json_malformed",
        "controlled-errors",
        (*ASGK, "task-packet-check", "--json-file", "{temp_input}", "--json"),
        "negative",
        "fail",
        1,
        ("TP_INPUT_JSON_INVALID",),
        TASK_PACKET_INPUT_BOUNDARY,
        temp_input=TempInput(content="{"),
    ),
    JsonScenario(
        "task_packet_live_lookup_unavailable",
        "controlled-errors",
        (*ASGK, "task-packet-check", "--file", "examples/task_packet.valid.json", "--issue", "999", "--json"),
        "negative",
        "blocked",
        1,
        ("TP_LIVE_LOOKUP_FAILED",),
        TASK_PACKET_INPUT_BOUNDARY,
        environment="gh_fail",
    ),
    JsonScenario(
        "handoff_file_missing",
        "controlled-errors",
        (*ASGK, "handoff-check", "--file", "__asgk_missing__/handoff.yaml", "--json"),
        "negative",
        "fail",
        1,
        ("HP_FILE_MISSING",),
        HANDOFF_BOUNDARY,
    ),
    JsonScenario(
        "handoff_yaml_malformed",
        "controlled-errors",
        (*ASGK, "handoff-check", "--file", "{temp_input}", "--json"),
        "negative",
        "fail",
        1,
        ("HP_PACKET_AMBIGUOUS",),
        HANDOFF_BOUNDARY,
        temp_input=TempInput(content="{", suffix=".yaml"),
    ),
    JsonScenario(
        "compact_handoff_core_missing",
        "controlled-errors",
        (*ASGK, "compact-handoff-check", "--file", "__asgk_missing__/compact-handoff.yaml", "--current-status", "__asgk_missing__/status.md", "--json"),
        "negative",
        "fail",
        1,
        ("HP_FILE_MISSING",),
        HANDOFF_BOUNDARY,
    ),
    JsonScenario(
        "compact_handoff_status_missing",
        "controlled-errors",
        (*ASGK, "compact-handoff-check", "--file", "examples/compact_governance/handoff.compact.valid.yaml", "--current-status", "__asgk_missing__/status.md", "--json"),
        "negative",
        "fail",
        1,
        ("CH_CURRENT_STATUS_FILE_MISSING",),
        COMPACT_HANDOFF_STATUS_UNAVAILABLE_BOUNDARY,
        expected_mechanically_checked=(
            "supported YAML-subset parsing",
            "single expected handoff root",
            "required core field presence, type, and material content",
            "validation_status enum, evidence list, and material reason",
            "forbidden chat-only authority phrase",
            "unresolved TODO or AI_TODO markers",
            "current_status_impact required fields, types, and status consistency",
            "CURRENT_STATUS path existence, file type, and readability",
        ),
        expected_not_checked=(
            "truth or completeness of handoff statements",
            "live state of GitHub issue, PR, branch, or durable links",
            "path authorization or diff containment",
            "whether validation evidence was produced by executed commands",
            "work completion, human approval, merge readiness, or merge authority",
            "CURRENT_STATUS local status-check result",
            "caller-supplied completed issue, PR, and branch references",
            "CURRENT_STATUS pre-merge next-action patterns",
            "live GitHub state, human approval, PR readiness, or merge authority",
        ),
    ),
    JsonScenario(
        "compact_issue_scope_file_missing",
        "controlled-errors",
        (*ASGK, "compact-issue-scope", "--json-file", "__asgk_missing__/issue.json", "--json"),
        "negative",
        "fail",
        1,
        ("CIS_INPUT_FILE_UNREADABLE",),
        CIS_FILE_BOUNDARY,
    ),
    JsonScenario(
        "compact_issue_scope_json_malformed",
        "controlled-errors",
        (*ASGK, "compact-issue-scope", "--json-file", "{temp_input}", "--json"),
        "negative",
        "fail",
        1,
        ("CIS_INPUT_JSON_INVALID",),
        CIS_JSON_BOUNDARY,
        temp_input=TempInput(content="{"),
    ),
    JsonScenario(
        "compact_issue_scope_live_unavailable",
        "controlled-errors",
        (*ASGK, "compact-issue-scope", "--issue", "999", "--json"),
        "negative",
        "blocked",
        1,
        ("CIS_LIVE_LOOKUP_FAILED",),
        CIS_LIVE_BOUNDARY,
        environment="gh_fail",
    ),
    JsonScenario(
        "compact_scope_lock_file_missing",
        "controlled-errors",
        (*ASGK, "compact-scope-lock", "--json-file", "__asgk_missing__/issue.json", "--json"),
        "negative",
        "fail",
        1,
        ("CSL_INPUT_FILE_UNREADABLE",),
        CSL_FILE_BOUNDARY,
    ),
    JsonScenario(
        "compact_scope_lock_json_malformed",
        "controlled-errors",
        (*ASGK, "compact-scope-lock", "--json-file", "{temp_input}", "--json"),
        "negative",
        "fail",
        1,
        ("CSL_INPUT_JSON_INVALID",),
        CSL_JSON_BOUNDARY,
        temp_input=TempInput(content="{"),
    ),
    JsonScenario(
        "compact_scope_lock_live_unavailable",
        "controlled-errors",
        (*ASGK, "compact-scope-lock", "--issue", "999", "--json"),
        "negative",
        "blocked",
        1,
        ("CSL_LIVE_LOOKUP_FAILED",),
        CSL_LIVE_BOUNDARY,
        environment="gh_fail",
    ),
    JsonScenario(
        "compact_scope_lock_compare_json_malformed",
        "controlled-errors",
        (*ASGK, "compact-scope-lock", "--json-file", "examples/compact_governance/scope_lock.valid-issue.json", "--compare-file", "{temp_input}", "--json"),
        "negative",
        "fail",
        1,
        ("CSL_COMPARE_JSON_INVALID",),
        CSL_COMPARE_JSON_BOUNDARY,
        temp_input=TempInput(content="{"),
    ),
    JsonScenario(
        "compact_pr_report_file_missing",
        "controlled-errors",
        (*ASGK, "compact-pr-report", "--json-file", "__asgk_missing__/pr.json", "--json"),
        "negative",
        "fail",
        1,
        ("CPR_INPUT_FILE_UNREADABLE",),
        CPR_FILE_BOUNDARY,
    ),
    JsonScenario(
        "compact_pr_report_json_malformed",
        "controlled-errors",
        (*ASGK, "compact-pr-report", "--json-file", "{temp_input}", "--json"),
        "negative",
        "fail",
        1,
        ("CPR_INPUT_JSON_INVALID",),
        CPR_JSON_BOUNDARY,
        temp_input=TempInput(content="{"),
    ),
    JsonScenario(
        "compact_pr_report_live_unavailable",
        "controlled-errors",
        (*ASGK, "compact-pr-report", "--pr", "999", "--json"),
        "negative",
        "blocked",
        1,
        ("CPR_LIVE_LOOKUP_FAILED",),
        CPR_LIVE_BOUNDARY,
        environment="gh_fail",
    ),
    JsonScenario(
        "compact_pr_body_files_missing",
        "controlled-errors",
        (*ASGK, "compact-pr-body-check", "--body-file", "__asgk_missing__/body.md", "--report-json", "__asgk_missing__/report.json", "--json"),
        "negative",
        "fail",
        1,
        (
            "CPB_BODY_FILE_MISSING",
            "CPB_REPORT_FILE_MISSING",
        ),
        COMPACT_PR_BODY_INPUT_INCOMPLETE_BOUNDARY,
        expected_mechanically_checked=(
            "compact PR body file existence and readability",
            "compiled report file existence and readability",
        ),
        expected_not_checked=(
            "whether the compiled report is current or live",
            "semantic correctness of PR evidence or diff contents",
            "human approval, low-risk status, or merge authority",
            "Compiled Report Reference structure",
            "canonical PR body coherence and strict policy gate",
            "compiled report result, PR status, derived state, inference flags, and findings array",
        ),
    ),
    JsonScenario(
        "compact_pr_body_report_json_malformed",
        "controlled-errors",
        (*ASGK, "compact-pr-body-check", "--body-file", "examples/compact_governance/pr_body.compact.valid.md", "--report-json", "{temp_input}", "--json"),
        "negative",
        "fail",
        1,
        ("CPB_REPORT_JSON_INVALID",),
        COMPACT_PR_BODY_INPUT_INCOMPLETE_BOUNDARY,
        temp_input=TempInput(content="{"),
    ),
    JsonScenario(
        "context_budget_file_missing",
        "controlled-errors",
        (*ASGK, "context-budget-measure", "--task-packet", "__asgk_missing__/task-packet.json", "--json"),
        "negative",
        "fail",
        1,
        ("CBM_INPUT_FILE_UNREADABLE",),
        CONTEXT_FILE_BOUNDARY,
    ),
    JsonScenario(
        "context_budget_json_malformed",
        "controlled-errors",
        (*ASGK, "context-budget-measure", "--task-packet", "{temp_input}", "--json"),
        "negative",
        "fail",
        1,
        ("CBM_INPUT_JSON_INVALID",),
        CONTEXT_JSON_BOUNDARY,
        temp_input=TempInput(content="{"),
    ),
    JsonScenario(
        "workspace_state_file_missing",
        "controlled-errors",
        (*ASGK, "workspace-state-check", "--json-file", "__asgk_missing__/workspace.json", "--json"),
        "negative",
        "fail",
        1,
        ("WS_INPUT_FILE_UNREADABLE",),
        WORKSPACE_FILE_BOUNDARY,
    ),
    JsonScenario(
        "workspace_state_json_malformed",
        "controlled-errors",
        (*ASGK, "workspace-state-check", "--json-file", "{temp_input}", "--json"),
        "negative",
        "fail",
        1,
        ("WS_INPUT_JSON_INVALID",),
        WORKSPACE_JSON_BOUNDARY,
        temp_input=TempInput(content="{"),
    ),
    JsonScenario(
        "workspace_state_wrong_object_shape",
        "controlled-errors",
        (
            *ASGK,
            "workspace-state-check",
            "--json-file",
            "examples/pr_status.valid.json",
            "--json",
        ),
        "negative",
        "fail",
        1,
        ("WS_PAYLOAD_SHAPE_INVALID",),
        WORKSPACE_PAYLOAD_SHAPE_BOUNDARY,
        expected_mechanically_checked=(
            "workspace-state payload shape",
        ),
        expected_not_checked=(
            "issue or PR authority",
            "changed-path authorization or semantic diff contents",
            "human approval, low-risk status, or merge readiness",
            "workspace branch evidence",
            "workspace upstream evidence",
            "workspace untracked-path evidence",
            "workspace changed-path evidence",
            "merged-into-base evidence",
        ),
    ),
    JsonScenario(
        "check_pr_live_payload_invalid",
        "controlled-errors",
        (*ASGK, "check-pr", "--pr", "999", "--json"),
        "negative",
        "blocked",
        1,
        ("PR_LIVE_PAYLOAD_INVALID",),
        CHECK_PR_LIVE_INVALID_BOUNDARY,
        environment="gh_invalid_json",
    ),
    JsonScenario(
        "work_unit_live_payload_invalid",
        "controlled-errors",
        (*ASGK, "work-unit-check", "--issue", "999", "--authority-only", "--json"),
        "negative",
        "blocked",
        1,
        ("WU_LIVE_PAYLOAD_INVALID",),
        WORK_UNIT_INPUT_BOUNDARY,
        environment="gh_invalid_json",
    ),
    JsonScenario(
        "task_packet_live_payload_invalid",
        "controlled-errors",
        (*ASGK, "task-packet-check", "--file", "examples/task_packet.valid.json", "--issue", "999", "--json"),
        "negative",
        "blocked",
        1,
        ("TP_LIVE_PAYLOAD_INVALID",),
        TASK_PACKET_INPUT_BOUNDARY,
        environment="gh_invalid_json",
    ),
    JsonScenario(
        "compact_issue_scope_live_payload_invalid",
        "controlled-errors",
        (*ASGK, "compact-issue-scope", "--issue", "999", "--json"),
        "negative",
        "blocked",
        1,
        ("CIS_LIVE_PAYLOAD_INVALID",),
        CIS_LIVE_INVALID_BOUNDARY,
        environment="gh_invalid_json",
        expected_mechanically_checked=(
            "live issue lookup response JSON syntax",
        ),
        expected_not_checked=(
            "live issue lookup response top-level shape",
            "issue authority fields or allowed_paths",
            "implementation, human approval, or merge authority",
        ),
    ),
    JsonScenario(
        "compact_scope_lock_live_payload_invalid",
        "controlled-errors",
        (*ASGK, "compact-scope-lock", "--issue", "999", "--json"),
        "negative",
        "blocked",
        1,
        ("CSL_LIVE_PAYLOAD_INVALID",),
        CSL_LIVE_INVALID_BOUNDARY,
        environment="gh_invalid_json",
        expected_mechanically_checked=(
            "live issue lookup response JSON syntax",
        ),
        expected_not_checked=(
            "live issue lookup response top-level shape",
            "issue scope or deterministic hash",
            "implementation, human approval, or merge authority",
        ),
    ),
    JsonScenario(
        "compact_pr_report_live_payload_invalid",
        "controlled-errors",
        (*ASGK, "compact-pr-report", "--pr", "999", "--json"),
        "negative",
        "blocked",
        1,
        ("CPR_LIVE_PAYLOAD_INVALID",),
        CPR_LIVE_INVALID_BOUNDARY,
        environment="gh_invalid_json",
        expected_mechanically_checked=(
            "live GitHub PR lookup response JSON syntax",
        ),
        expected_not_checked=(
            "live GitHub PR lookup response top-level shape",
            "PR metadata, issue scope, status checks, or restricted boundaries",
            "human approval, low-risk status, or merge authority",
        ),
    ),
    JsonScenario(
        "check_pr_live_executable_missing",
        "controlled-errors",
        (*ASGK, "check-pr", "--pr", "999", "--json"),
        "negative",
        "blocked",
        1,
        ("PR_LIVE_LOOKUP_FAILED",),
        CHECK_PR_LIVE_BOUNDARY,
        environment="gh_missing",
    ),
    JsonScenario(
        "work_unit_live_executable_missing",
        "controlled-errors",
        (*ASGK, "work-unit-check", "--issue", "999", "--authority-only", "--json"),
        "negative",
        "blocked",
        1,
        ("WU_LIVE_LOOKUP_FAILED",),
        WORK_UNIT_INPUT_BOUNDARY,
        environment="gh_missing",
    ),
    JsonScenario(
        "task_packet_live_executable_missing",
        "controlled-errors",
        (*ASGK, "task-packet-check", "--file", "examples/task_packet.valid.json", "--issue", "999", "--json"),
        "negative",
        "blocked",
        1,
        ("TP_LIVE_LOOKUP_FAILED",),
        TASK_PACKET_INPUT_BOUNDARY,
        environment="gh_missing",
    ),
    JsonScenario(
        "compact_issue_scope_live_executable_missing",
        "controlled-errors",
        (*ASGK, "compact-issue-scope", "--issue", "999", "--json"),
        "negative",
        "blocked",
        1,
        ("CIS_LIVE_LOOKUP_FAILED",),
        CIS_LIVE_BOUNDARY,
        environment="gh_missing",
    ),
    JsonScenario(
        "compact_scope_lock_live_executable_missing",
        "controlled-errors",
        (*ASGK, "compact-scope-lock", "--issue", "999", "--json"),
        "negative",
        "blocked",
        1,
        ("CSL_LIVE_LOOKUP_FAILED",),
        CSL_LIVE_BOUNDARY,
        environment="gh_missing",
    ),
    JsonScenario(
        "compact_pr_report_live_executable_missing",
        "controlled-errors",
        (*ASGK, "compact-pr-report", "--pr", "999", "--json"),
        "negative",
        "blocked",
        1,
        ("CPR_LIVE_LOOKUP_FAILED",),
        CPR_LIVE_BOUNDARY,
        environment="gh_missing",
    ),
    JsonScenario(
        "workspace_git_executable_missing",
        "controlled-errors",
        (*ASGK, "workspace-state-check", "--json"),
        "negative",
        "warning",
        0,
        (
            "WS_BRANCH_LOOKUP_FAILED",
            "WS_BRANCH_UNAVAILABLE",
            "WS_CACHED_DIFF_LOOKUP_FAILED",
            "WS_DIFF_LOOKUP_FAILED",
            "WS_UNTRACKED_LOOKUP_FAILED",
            "WS_UPSTREAM_LOOKUP_FAILED",
            "WS_UPSTREAM_MISSING",
        ),
        WORKSPACE_LOOKUP_INCOMPLETE_BOUNDARY,
        environment="git_missing",
        expected_mechanically_checked=(
            "workspace-state payload and lookup-error projection",
        ),
        expected_not_checked=(
            "issue or PR authority",
            "changed-path authorization or semantic diff contents",
            "human approval, low-risk status, or merge readiness",
            "workspace branch evidence",
            "workspace upstream evidence",
            "workspace untracked-path evidence",
            "workspace unstaged changed-path evidence",
            "workspace staged changed-path evidence",
            "merged-into-base evidence",
        ),
    ),
    JsonScenario(
        "source_validation_input_mode_invalid",
        "controlled-errors",
        (
            *ASGK,
            "validate",
            "--repo-root",
            ".",
            "--source-inventory-file",
            "examples/source_validation/reference-superset.valid.json",
            "--json",
        ),
        "negative",
        "fail",
        1,
        ("SV_INPUT_MODE_INVALID",),
        SOURCE_INPUT_FAILURE_BOUNDARY,
        expected_mechanically_checked=(
            "source validation input mode selection",
        ),
        expected_not_checked=SOURCE_INPUT_NOT_CHECKED,
    ),
    JsonScenario(
        "source_inventory_file_unreadable",
        "controlled-errors",
        (
            *ASGK,
            "validate",
            "--source-inventory-file",
            "__asgk_missing__/source-inventory.json",
            "--json",
        ),
        "negative",
        "fail",
        1,
        ("SV_INVENTORY_FILE_UNREADABLE",),
        SOURCE_INPUT_FAILURE_BOUNDARY,
        expected_mechanically_checked=(
            "supplied source inventory file readability",
        ),
        expected_not_checked=SOURCE_INPUT_NOT_CHECKED,
    ),
    JsonScenario(
        "source_inventory_json_invalid",
        "controlled-errors",
        (
            *ASGK,
            "validate",
            "--source-inventory-file",
            "{temp_input}",
            "--json",
        ),
        "negative",
        "fail",
        1,
        ("SV_INVENTORY_JSON_INVALID",),
        SOURCE_INPUT_FAILURE_BOUNDARY,
        temp_input=TempInput(content="{", suffix=".json"),
        expected_mechanically_checked=(
            "supplied source inventory file readability",
            "supplied source inventory JSON parsing",
        ),
        expected_not_checked=SOURCE_INPUT_NOT_CHECKED,
    ),
    JsonScenario(
        "source_inventory_shape_invalid",
        "controlled-errors",
        (
            *ASGK,
            "validate",
            "--source-inventory-file",
            "{temp_input}",
            "--json",
        ),
        "negative",
        "fail",
        1,
        ("SV_INVENTORY_SHAPE_INVALID",),
        SOURCE_INPUT_FAILURE_BOUNDARY,
        temp_input=TempInput(
            content='{"paths": "README.md"}',
            suffix=".json",
        ),
        expected_mechanically_checked=(
            "supplied source inventory file readability",
            "supplied source inventory JSON parsing",
            "supplied source inventory JSON object shape",
        ),
        expected_not_checked=SOURCE_INPUT_NOT_CHECKED,
    ),
    JsonScenario(
        "source_inventory_duplicate_key",
        "controlled-errors",
        (
            *ASGK,
            "validate",
            "--source-inventory-file",
            "{temp_input}",
            "--json",
        ),
        "negative",
        "fail",
        1,
        ("SV_INVENTORY_SHAPE_INVALID",),
        SOURCE_INPUT_FAILURE_BOUNDARY,
        temp_input=TempInput(
            source="examples/source_validation/reference-superset.valid.json",
            replacements=(
                (
                    '"paths": [',
                    '"paths": ["LICENSE"],\n  "paths": [',
                ),
            ),
        ),
        expected_mechanically_checked=(
            "supplied source inventory file readability",
            "supplied source inventory JSON parsing",
            "supplied source inventory JSON object shape",
        ),
        expected_not_checked=SOURCE_INPUT_NOT_CHECKED,
    ),
    JsonScenario(
        "source_inventory_json_too_deep",
        "controlled-errors",
        (
            *ASGK,
            "validate",
            "--source-inventory-file",
            "{temp_input}",
            "--json",
        ),
        "negative",
        "fail",
        1,
        ("SV_INVENTORY_JSON_INVALID",),
        SOURCE_INPUT_FAILURE_BOUNDARY,
        temp_input=TempInput(
            content="[" * 2000 + "]" * 2000,
            suffix=".json",
        ),
        expected_mechanically_checked=(
            "supplied source inventory file readability",
            "supplied source inventory JSON nesting bound",
        ),
        expected_not_checked=SOURCE_INPUT_NOT_CHECKED,
    ),
)


JSON_SCENARIOS = (*RETAINED_JSON_SCENARIOS, *CONTROLLED_ERROR_SCENARIOS)


PARITY_SCENARIOS = (
    ParityScenario(
        "task_packet_alias_positive_parity",
        "compact-task-packet",
        (*ASGK, "task-packet-check", "--json-file", "examples/compact_governance/task_packet_delta.valid.json", "--json"),
        (*ASGK, "compact-task-packet-check", "--json-file", "examples/compact_governance/task_packet_delta.valid.json", "--json"),
        "positive",
    ),
    ParityScenario(
        "task_packet_alias_negative_parity",
        "compact-task-packet",
        (*ASGK, "task-packet-check", "--json-file", "examples/negative/compact_governance/task-packet-delta-expands-scope.json", "--json"),
        (*ASGK, "compact-task-packet-check", "--json-file", "examples/negative/compact_governance/task-packet-delta-expands-scope.json", "--json"),
        "negative",
    ),
    ParityScenario(
        "source_validation_wrapper_positive_parity",
        "source-validation",
        (
            *ASGK,
            "validate",
            "--source-inventory-file",
            "examples/source_validation/reference-superset.valid.json",
            "--json",
        ),
        (
            "python3",
            "scripts/validate_bootstrap.py",
            "--source-inventory-file",
            "examples/source_validation/reference-superset.valid.json",
            "--json",
        ),
        "positive",
    ),
    ParityScenario(
        "source_validation_wrapper_negative_parity",
        "source-validation",
        (
            *ASGK,
            "validate",
            "--source-inventory-file",
            "examples/negative/source_validation/missing-required-path.json",
            "--json",
        ),
        (
            "python3",
            "scripts/validate_bootstrap.py",
            "--source-inventory-file",
            "examples/negative/source_validation/missing-required-path.json",
            "--json",
        ),
        "negative",
    ),
)


EXACT_SCENARIO_GROUPS = sorted({scenario.group for scenario in JSON_SCENARIOS})
NEGATIVE_CASE_CHOICES = sorted(
    {
        *NEGATIVE_CASE_GROUPS,
        *EXACT_SCENARIO_GROUPS,
        "retained-json",
        "controlled-errors",
        "scenario-runner",
    }
) + ["all"]
