# Negative Test Plan

Status: active control plan.

This plan defines the known-bad cases that this governance kit should eventually
block, request changes for, or human-gate. It does not add executable fixtures or
change validator behavior by itself.

## Purpose

Positive validation proves the happy path works. Negative validation proves that
bad paths are stopped.

The governance kit should not only allow correct workflows. It should also catch
or escalate common AI-agent failure modes:

- chat-only task authority;
- missing review or merge evidence;
- runtime artifact leakage;
- protected path changes;
- schema or policy drift;
- unauthorized external calls;
- human-gated operations hidden in low-risk PRs.

## Canonical References

```yaml
validation_strategy: docs/control/VALIDATION_STRATEGY.md
pr_review_checklist: docs/control/PR_REVIEW_CHECKLIST.md
context_budget: docs/control/CONTEXT_BUDGET_POLICY.md
agent_capability_matrix: docs/control/AGENT_CAPABILITY_MATRIX.md
human_gates: docs/control/HUMAN_GATED_OPERATIONS.md
runtime_artifact_policy: docs/architecture/RUNTIME_ARTIFACT_POLICY.md
storage_profile: docs/architecture/STORAGE_PROFILE.md
merge_decision_record: docs/control/MERGE_DECISION_RECORD.md
```

If this plan conflicts with `docs/control/VALIDATION_STRATEGY.md`, prefer the
validation strategy and open a follow-up issue to align this plan.

## Outcome Types

```yaml
negative_test_outcomes:
  blocked:
    meaning: validator or review gate should stop the PR or task
  request_changes:
    meaning: PR is recoverable inside current scope
  human_gated:
    meaning: work may continue only after durable human approval
  split_required:
    meaning: low-risk and high-risk work must be separated
  warning:
    meaning: issue should be reported but does not block by itself
```

## Fixture Strategy

Negative fixtures must be opt-in expected-failure cases.

```yaml
fixture_strategy:
  allowed_locations:
    - examples/negative/
    - tests/fixtures/negative/
  must_be_opt_in: true
  must_record_expected_failure: true
  must_not_be_loaded_as_positive_examples: true
  must_not_break_baseline_validation: true
```

Do not place malformed JSON, bad task packets, or intentionally unsafe paths in
normal `examples/` or `schemas/` locations unless the validator is explicitly
changed to treat them as expected failures.

## Negative Case Matrix

| Case ID | Bad input or behavior | Expected outcome | Owner | Future fixture path | Notes |
|---|---|---|---|---|---|
| `NEG-001-see-chat-source` | `durable_source_of_truth: see chat` | blocked | task packet validator / PR review | `examples/negative/task_packet.see-chat.yaml` | Chat is not durable authority. |
| `NEG-002-missing-durable-source` | issue or PR lacks durable source of truth | blocked | PR review / future PR validator | `examples/negative/pr_body.missing-source.md` | Must not start work. |
| `NEG-003-stale-issue` | issue appears satisfied by current `main` but is reused for new work | blocked or request_changes | issue hygiene gate | `examples/negative/issue.stale.md` | Requires comment and stop. |
| `NEG-004-missing-merge-decision` | PR body lacks `## Merge Decision` | blocked | PR review / future PR validator | `examples/negative/pr_body.no-merge-decision.md` | Merge evidence missing. |
| `NEG-005-incomplete-merge-decision` | Merge Decision Record missing required fields | blocked | PR review / future PR validator | `examples/negative/merge_decision.incomplete.yaml` | Use canonical schema later. |
| `NEG-006-pending-checks-merge` | PR says `merge_allowed` while checks are pending or unknown | blocked | PR review | `examples/negative/pr_body.pending-checks.md` | Cannot merge with unknown checks. |
| `NEG-007-changed-file-outside-allowed-paths` | changed file outside issue allowed paths | blocked or split_required | PR review / governance hygiene | `examples/negative/changed_paths.outside-allowed.txt` | Requires new issue or scope update. |
| `NEG-008-runtime-artifact-path` | changed path under `runs/`, `corpus/`, or `artifacts/` | blocked | governance_hygiene.py | `examples/negative/changed_paths.runtime-artifact.txt` | Runtime output leakage. |
| `NEG-009-protected-path` | changed path `.env`, `secrets/`, `.git/`, private keys | blocked | governance_hygiene.py | `examples/negative/changed_paths.protected.txt` | Protected path violation. |
| `NEG-010-private-binary-source` | `.pdf`, `.docx`, `.png`, `.tif`, etc outside fixture/example allowlist | blocked | governance_hygiene.py | `examples/negative/changed_paths.private-binary.txt` | Prevent private/source material commits. |
| `NEG-011-invalid-json-schema` | malformed JSON under `schemas/` | blocked | validate_bootstrap.py | `tests/fixtures/negative/schema.invalid.json` | Must be opt-in expected failure. |
| `NEG-012-invalid-example-json` | malformed JSON under positive examples | blocked | validate_bootstrap.py | `tests/fixtures/negative/example.invalid.json` | Do not put malformed examples in normal examples. |
| `NEG-013-storage-roots-equal` | `artifact_root == local_state_root` | blocked | validate_bootstrap.py | `examples/negative/storage_profile.same-root.json` | Storage boundary broken. |
| `NEG-014-drive-api-enabled-default` | `app_managed_drive_api: true` in default profile | blocked | validate_bootstrap.py | `examples/negative/storage_profile.drive-api.json` | External API gate opened. |
| `NEG-015-cache-not-local-only` | page renders, model cache, SQLite live DB, or temporary jobs not `local_only` | blocked | validate_bootstrap.py | `examples/negative/storage_profile.cache-not-local.json` | Cache/state boundary broken. |
| `NEG-016-summary-as-canonical` | PR relies on summary doc against canonical conflict | request_changes | PR review / document map | `examples/negative/review.summary-conflict.md` | Requires canonical source. |
| `NEG-017-context-expansion-unrecorded` | agent reads extra policy docs but report omits context expansion | request_changes | PR review / context budget | `examples/negative/agent_report.unrecorded-context.md` | Context drift risk. |
| `NEG-018-low-level-agent-security-work` | `fast_basic` or `standard` performs security boundary work | blocked | agent capability matrix / PR review | `examples/negative/agent_report.bad-level.md` | Escalation required. |
| `NEG-019-subagent-final-authority` | sub-agent acts as final authority for human-gated work | blocked | agent capability matrix / PR review | `examples/negative/agent_report.subagent-final-authority.md` | Human/frontier gate required. |
| `NEG-020-schema-breaking-low-risk` | schema breaking change marked low-risk merge | blocked | PR review / schema policy | `examples/negative/pr_body.schema-breaking-low-risk.md` | Human-gated. |
| `NEG-021-dependency-without-approval` | new dependency without issue approval, rationale, security/license review | human_gated | human gate / PR review | `examples/negative/pr_body.dependency-no-approval.md` | Requires explicit approval. |
| `NEG-022-cloud-api-mcp-without-gate` | cloud/API/model/MCP capability opened without explicit approval | human_gated | human gate / readiness policy | `examples/negative/pr_body.external-call-no-gate.md` | High-risk. |
| `NEG-023-validation-loosened` | validator becomes less strict without approval | blocked or human_gated | validation strategy / PR review | `examples/negative/pr_body.validation-loosened.md` | Must be explicit. |
| `NEG-024-negative-fixture-loaded-as-positive` | expected-failure fixture placed where positive validation reads it | blocked | validation strategy | `examples/negative/fixture.loaded-as-positive.md` | Fixture strategy violation. |
| `NEG-025-missing-pr-heading` | PR template or PR body lacks required section | blocked | validate_bootstrap / PR review | `examples/negative/pr_body.missing-heading.md` | Review surface degraded. |
| `NEG-026-unrelated-bundled-work` | PR bundles unrelated docs/code/schema/CI cleanup | split_required | PR review | `examples/negative/pr_body.unrelated-bundle.md` | Split work units. |
| `NEG-027-release-decision-low-risk` | release/publication decision marked low-risk | human_gated | human gate / PR review | `examples/negative/pr_body.release-low-risk.md` | Never low-risk. |
| `NEG-028-missing-rollback` | high-risk issue lacks rollback expectations | blocked | issue template / PR review | `examples/negative/issue.no-rollback.md` | Required for risky tasks. |
| `NEG-029-missing-stop-conditions` | task packet lacks stop conditions | blocked | task packet validator | `examples/negative/task_packet.no-stop.yaml` | Agent may overrun scope. |
| `NEG-030-executable-task-packet-without-issue` | executable task packet uses only a repo document as authority while GitHub is available | blocked | task packet validator | `examples/negative/task_packet.executable-no-github-issue.yaml` | Task packets refine issue scope; they do not replace issue-first authorization. |
| `NEG-031-doc-map-not-updated` | new canonical doc added but `docs/DOCUMENT_MAP.md` not updated | request_changes | PR review / document map | `examples/negative/pr_body.doc-map-stale.md` | Prevent ownership drift. |
| `NEG-032-compact-pr-outside-issue-scope` | compact PR references an issue but changes paths outside issue `allowed_paths` | blocked | compact governance red-team checker | `examples/negative/compact_governance/changed-path-outside-allowed.json` | Reference-only PR prose is not enough. |
| `NEG-033-compact-scope-lock-stale` | issue scope changes after a compact scope lock is captured | blocked | compact governance red-team checker | `examples/negative/compact_governance/issue-scope-lock-changed.json` | Scope lock mismatch must block. |
| `NEG-034-compact-task-packet-expands-scope` | task packet adds paths outside the source issue scope | blocked | compact governance red-team checker | `examples/negative/compact_governance/task-packet-expands-scope.json` | Task packets may narrow, not expand. |
| `NEG-035-compact-self-attested-claim-conflict` | PR prose claims merge readiness while tool-derived state is blocked | blocked | compact governance red-team checker | `examples/negative/compact_governance/self-attested-claim-overrides-tool-state.json` | Agent claims cannot create eligibility. |
| `NEG-036-compact-ci-pending-claimed-eligible` | CI is pending while compact PR prose implies merge eligibility | blocked | compact governance red-team checker | `examples/negative/compact_governance/ci-pending-claimed-eligible.json` | CI state must be tool-derived. |
| `NEG-037-compact-current-status-impact-mismatch` | `CURRENT_STATUS.md` changed while impact says `not_applicable` | blocked | compact governance red-team checker | `examples/negative/compact_governance/current-status-impact-mismatch.json` | Compact handoff cannot hide state drift. |
| `NEG-038-compact-restricted-boundary-human-gate` | compact report touches protected governance boundary | human_gated | compact governance red-team checker | `examples/negative/compact_governance/restricted-boundary-human-gate.json` | Human-gated state is not merge eligibility. |
| `NEG-039-compact-metadata-unavailable` | issue/PR metadata is unavailable | blocked | compact governance red-team checker | `examples/negative/compact_governance/github-metadata-unavailable.json` | Compact governance must fail closed. |
| `NEG-040-compact-scope-lock-missing-allowed-paths` | issue scope-lock input lacks material `allowed_paths` | blocked | compact scope-lock command | `examples/negative/compact_governance/scope-lock.missing-allowed-paths.json` | Scope lock cannot be generated without path authority. |
| `NEG-041-compact-issue-scope-missing-allowed-paths` | canonical issue scope input lacks material `allowed_paths` | blocked | compact issue-scope command | `examples/negative/compact_governance/issue-scope.missing-allowed-paths.json` | Canonical scope cannot be generated without path authority. |
| `NEG-042-compact-scope-lock-stale-capture` | captured scope lock hash does not match current canonical issue scope | blocked | compact scope-lock command | `examples/negative/compact_governance/scope-lock.stale-capture.json` | Captured scope locks must not survive issue-scope changes. |
| `NEG-043-compact-pr-report-metadata-unavailable` | PR metadata is unavailable for compact report compilation | fail_closed | compact PR report command | `examples/negative/compact_governance/pr-report.metadata-unavailable.json` | Compact report must not be guessed from agent prose. |
| `NEG-044-compact-pr-report-claim-conflict` | PR body or agent claim says merge-ready while tool-derived report findings block merge | blocked | compact PR report command | `examples/negative/compact_governance/pr-report.claim-conflicts-with-tool-state.json` | Merge-readiness prose must not override live status, issue-scope, path, or PR-body findings. |

## Implementation Phases

### Phase 1 — Documentation-only plan

Current phase.

```yaml
phase_1:
  deliverable: docs/control/NEGATIVE_TEST_PLAN.md
  executable_fixtures: false
  validator_changes: false
```

### Phase 2 — Passive negative fixtures

Add expected-failure fixtures that are not loaded by positive validation.

```yaml
phase_2:
  paths:
    - examples/negative/
    - tests/fixtures/negative/
  validator_changes: optional
  requirement: fixtures must include expected outcome metadata
```

### Phase 3 — Validator support

Teach validators to run selected negative cases as expected failures.

```yaml
phase_3:
  scripts:
    - scripts/validate_bootstrap.py
    - scripts/governance_hygiene.py
  expected_behavior: bad inputs fail when tested as negative cases
  ci_behavior: positive validation still passes
```

### Phase 4 — PR-body and task-packet validation

Add future validation for PR bodies, task packets, and Merge Decision Records.

```yaml
phase_4:
  future_checks:
    - PR required heading detection
    - Merge Decision Record field validation
    - durable source of truth detection
    - see chat detection
```

### Phase 5 — CLI wrapper

Expose negative and positive validation through CLI.

```yaml
phase_5:
  future_commands:
    - asgk validate
    - asgk hygiene --paths changed-paths.txt
    - asgk negative --case NEG-001
    - asgk check-pr <number>
```

## Rules For Future Negative Fixtures

Each negative fixture should include a companion metadata file or front matter:

```yaml
negative_case:
  id:
  title:
  bad_input:
  expected_outcome:
  owner:
  validator:
  should_block_positive_validation: false
```

Do not add a negative fixture without an expected outcome.

## Blocking vs Human-Gated Distinction

`blocked` means the work is invalid under current policy.

`human_gated` means the work may be valid only with explicit durable human
approval. Human-gated work should not be hidden inside low-risk PRs.

Examples:

```yaml
blocked:
  - see chat as durable source
  - missing Merge Decision Record
  - runtime artifact committed
  - protected path changed

human_gated:
  - new dependency
  - schema breaking change
  - cloud/API/MCP enablement
  - release/publication decision
```

## Review Use

During PR review, use this plan to ask:

1. Does this PR resemble a known negative case?
2. Is the outcome block, request changes, human-gate, or split required?
3. Is the expected validator already implemented?
4. If not implemented, should this become a future fixture/tooling issue?

## Known Gaps

```yaml
known_gaps:
  - negative fixtures are not yet added
  - negative fixtures are not yet wired into CI
  - PR-body validation is not yet implemented
  - task-packet validation is not yet implemented as a full parser
  - governance_hygiene.py still needs stronger changed-path workflows
  - no CLI wrapper exists yet
```

These are planned follow-up issues, not blockers for this documentation-only
plan.
