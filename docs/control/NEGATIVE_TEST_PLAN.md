# Negative Test Plan

Status: active control plan.

This plan defines known-bad cases that this governance kit blocks, requests
changes for, or human-gates through review guidance and implemented negative
fixture runners. It does not change validator behavior by itself.

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
validation strategy for validator proof boundaries, fail-closed behavior, and
fixture rules. Prefer this plan for human-readable case IDs, risk intent, review
classification, and candidate fixture paths. Executable implementation status
and exact command expectations belong only to
`scripts/asgk_lib/scenario_registry.py`. Open a follow-up issue when the two
surfaces drift.

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

These are human review classifications. They are not the common JSON `result`
enum. In command output, an unavailable required check or a required human gate
uses top-level `result: blocked`; `fail_closed` and `human_gated` remain domain
meaning rather than alternate common result tokens.

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

Fixture metadata explains intent only. It cannot override the exact result,
exit, finding-code multiset, human-gate state, or proof boundary registered for
an executable scenario. A `planned_unimplemented` row is a design gap, not
validation evidence.

## Negative Case Matrix

| Case ID | Bad input or behavior | Expected outcome | Owner | Fixture path or target | Notes |
|---|---|---|---|---|---|
| `NEG-001-see-chat-source` | `durable_source_of_truth: see chat` | blocked | task packet validator / PR review | `examples/negative/task_packet.see-chat.yaml` | Chat is not durable authority. |
| `NEG-002-missing-durable-source` | issue or PR lacks durable source of truth | blocked | PR review / future PR validator | `planned_unimplemented: missing durable source PR/issue fixture` | Must not start work. |
| `NEG-003-stale-issue` | issue appears satisfied by current `main` but is reused for new work | blocked or request_changes | issue hygiene gate | `planned_unimplemented: stale issue fixture` | Requires comment and stop. |
| `NEG-004-missing-merge-decision` | PR body lacks `## Merge Decision` | blocked | PR review / future PR validator | `examples/negative/pr_body.no-merge-decision.md` | Merge evidence missing. |
| `NEG-005-incomplete-merge-decision` | Merge Decision Record missing required fields | blocked | PR review / future PR validator | `planned_unimplemented: incomplete Merge Decision fixture` | Use canonical schema later. |
| `NEG-006-pending-checks-merge` | PR says `merge_allowed` while checks are pending | blocked | policy gate / PR review | `examples/negative/policy_gate/pr_body.checks-pending.md` | Must fail in body-coherence and merge-decision. |
| `NEG-007-changed-file-outside-allowed-paths` | changed file outside issue allowed paths | blocked or split_required | PR review / governance hygiene | `examples/negative/pr_status.changed-path-outside-allowed.json` | Requires new issue or scope update. |
| `NEG-008-runtime-artifact-path` | changed path under `runs/`, `corpus/`, or `artifacts/` | blocked | governance_hygiene.py | `examples/negative/changed_paths.runtime-artifact.txt` | Runtime output leakage. |
| `NEG-009-protected-path` | changed path `.env`, `secrets/`, `.git/`, private keys | blocked | governance_hygiene.py | `examples/negative/changed_paths.protected.txt` | Protected path violation. |
| `NEG-010-private-binary-source` | `.pdf`, `.docx`, `.png`, `.tif`, etc outside fixture/example allowlist | blocked | governance_hygiene.py | `examples/negative/changed_paths.private-binary.txt` | Prevent private/source material commits. |
| `NEG-011-invalid-json-schema` | malformed JSON under a present `schemas/` path | blocked | source_validation.py | `planned_unimplemented: isolated invalid schema fixture` | Live source validation checks parseability without making every schema a retained prerequisite. |
| `NEG-012-invalid-example-json` | malformed JSON under present positive examples | blocked | source_validation.py | `planned_unimplemented: isolated invalid positive-example fixture` | Do not put malformed examples in normal examples. |
| `NEG-013-storage-roots-equal` | `artifact_root == local_state_root` in the legacy fixed storage profile | not_source_validation | W7B bounded decision | `examples/negative/storage_profile.same-root.json` | The optional fixed storage family is not an ASGK source prerequisite. |
| `NEG-014-drive-api-enabled-default` | `app_managed_drive_api: true` in the legacy fixed storage profile | not_source_validation | W7B bounded decision | `examples/negative/storage_profile.drive-api.json` | Source validation does not infer target storage or external-action policy from this fixture. |
| `NEG-015-cache-not-local-only` | legacy fixed-profile cache placement differs | not_source_validation | W7B bounded decision | `planned_unimplemented: no new fixture before W7B` | Do not recreate a fixed target storage oracle during source validation. |
| `NEG-016-summary-as-canonical` | PR relies on summary doc against canonical conflict | request_changes | PR review / document map | `planned_unimplemented: summary conflict fixture` | Requires canonical source. |
| `NEG-017-context-expansion-unrecorded` | agent reads extra policy docs but report omits context expansion | request_changes | PR review / context budget | `planned_unimplemented: unrecorded context expansion fixture` | Context drift risk. |
| `NEG-018-low-level-agent-security-work` | `fast_basic` or `standard` performs security boundary work | blocked | agent capability matrix / PR review | `planned_unimplemented: capability mismatch fixture` | Escalation required. |
| `NEG-020-schema-breaking-low-risk` | schema breaking change marked low-risk merge | blocked | PR review / schema policy | `planned_unimplemented: schema-breaking low-risk PR fixture` | Human-gated. |
| `NEG-021-dependency-without-approval` | new dependency without issue approval, rationale, security/license review | human_gated | human gate / PR review | `planned_unimplemented: dependency without approval PR fixture` | Requires explicit approval. |
| `NEG-022-cloud-api-mcp-without-gate` | cloud/API/model/MCP capability opened without explicit approval | human_gated | human gate / readiness policy | `examples/negative/pr_body.external-call-no-gate.md` | High-risk. |
| `NEG-023-validation-loosened` | validator becomes less strict without approval | blocked or human_gated | validation strategy / PR review | `planned_unimplemented: validator-loosened PR fixture` | Must be explicit. |
| `NEG-024-negative-fixture-loaded-as-positive` | expected-failure fixture placed where positive validation reads it | blocked | validation strategy | `planned_unimplemented: negative fixture loaded as positive fixture` | Fixture strategy violation. |
| `NEG-025-missing-pr-heading` | PR template or PR body lacks required section | blocked | source validation / PR review | `planned_unimplemented: missing PR heading fixture` | Review surface degraded. |
| `NEG-026-unrelated-bundled-work` | PR bundles unrelated docs/code/schema/CI cleanup | split_required | PR review | `planned_unimplemented: unrelated bundled work PR fixture` | Split work units. |
| `NEG-027-release-decision-low-risk` | release/publication decision marked low-risk | human_gated | human gate / PR review | `planned_unimplemented: release low-risk claim PR fixture` | Never low-risk. |
| `NEG-028-missing-rollback` | high-risk issue lacks rollback expectations | blocked | issue template / PR review | `planned_unimplemented: missing rollback issue fixture` | Required for risky tasks. |
| `NEG-029-missing-stop-conditions` | task packet lacks stop conditions | blocked | task packet validator | `examples/negative/task_packet.no-stop.yaml` | Agent may overrun scope. |
| `NEG-030-issue-refinement-without-source-issue` | issue-refinement packet is evaluated without the live or captured source issue | blocked | task packet validator | `examples/negative/task_packet.executable-no-github-issue.yaml` | An issue refinement cannot create or replace its own authority. |
| `NEG-031-doc-map-not-updated` | new canonical doc added but `docs/DOCUMENT_MAP.md` not updated | request_changes | PR review / document map | `planned_unimplemented: stale document map PR fixture` | Prevent ownership drift. |
| `NEG-032-compact-pr-outside-issue-scope` | compact PR references an issue but changes paths outside issue `allowed_paths` | blocked | compact PR report / check-pr | `examples/negative/compact_governance/changed-path-outside-allowed.json` | Reference-only PR prose is not enough. |
| `NEG-033-compact-scope-lock-stale` | issue scope changes after a compact scope lock is captured | blocked | compact-scope-lock | `examples/negative/compact_governance/issue-scope-lock-changed.json` | Scope lock mismatch must block. |
| `NEG-034-compact-task-packet-expands-scope` | issue-refinement packet adds paths outside the source issue scope | blocked | canonical task-packet evaluator | `examples/negative/compact_governance/task-packet-expands-scope.json` | The legacy red-team caller owns no packet-comparison semantics. |
| `NEG-035-compact-self-attested-claim-conflict` | PR prose claims merge readiness while tool-derived state is blocked | blocked | compact-pr-report | `examples/negative/compact_governance/self-attested-claim-overrides-tool-state.json` | Agent claims cannot create eligibility. |
| `NEG-036-compact-ci-pending-claimed-eligible` | CI is pending while compact PR prose implies merge eligibility | blocked | compact-pr-report / check-pr | `examples/negative/compact_governance/ci-pending-claimed-eligible.json` | CI state must be tool-derived. |
| `NEG-037-compact-current-status-impact-mismatch` | `CURRENT_STATUS.md` changed while impact says `not_applicable` | blocked | compact-handoff-check | `examples/negative/compact_governance/current-status-impact-mismatch.json` | Compact handoff cannot hide state drift. |
| `NEG-038-compact-restricted-boundary-human-gate` | compact report touches protected governance boundary | human_gated | compact-pr-report | `examples/negative/compact_governance/restricted-boundary-human-gate.json` | Common result is `blocked`; human-gate status is `required`; neither is merge eligibility. |
| `NEG-039-compact-metadata-unavailable` | issue/PR metadata is unavailable | blocked | compact-pr-report | `examples/negative/compact_governance/github-metadata-unavailable.json` | Domain state fails closed and common result is `blocked`; no metadata is guessed. |
| `NEG-040-compact-scope-lock-missing-allowed-paths` | issue scope-lock input lacks material `allowed_paths` | blocked | compact scope-lock command | `examples/negative/compact_governance/scope-lock.missing-allowed-paths.json` | Scope lock cannot be generated without path authority. |
| `NEG-041-compact-issue-scope-missing-allowed-paths` | canonical issue scope input lacks material `allowed_paths` | blocked | compact issue-scope command | `examples/negative/compact_governance/issue-scope.missing-allowed-paths.json` | Canonical scope cannot be generated without path authority. |
| `NEG-042-compact-scope-lock-stale-capture` | captured scope lock hash does not match current canonical issue scope | blocked | compact scope-lock command | `examples/negative/compact_governance/scope-lock.stale-capture.json` | Captured scope locks must not survive issue-scope changes. |
| `NEG-043-compact-pr-report-metadata-unavailable` | PR metadata is unavailable for compact report compilation | fail_closed | compact PR report command | `examples/negative/compact_governance/pr-report.metadata-unavailable.json` | Compact report must not be guessed from agent prose. |
| `NEG-044-compact-pr-report-claim-conflict` | PR body or agent claim says merge-ready while tool-derived report findings block merge | blocked | compact PR report command | `examples/negative/compact_governance/pr-report.claim-conflicts-with-tool-state.json` | Merge-readiness prose must not override live status, issue-scope, path, or PR-body findings. |
| `NEG-045-compact-task-packet-expands-issue-scope` | issue-refinement task packet adds `allowed_paths` outside source issue scope | blocked | canonical task-packet evaluator via compact compatibility command | `examples/negative/compact_governance/task-packet-delta-expands-scope.json` | Issue refinements may narrow issue scope, not expand it. |
| `NEG-046-compact-pr-body-failed-report` | compact PR body references a failed compiled report while PR prose claims merge-ready | blocked | compact PR body command | `examples/negative/compact_governance/pr_body.compact.failed-report.md` | Compact PR bodies must not turn report references into merge authority. |
| `NEG-047-compact-handoff-hides-stale-current-status` | compact handoff marks current status `not_applicable` while completed work remains in active work | blocked | compact handoff command | `examples/negative/compact_governance/handoff.compact.hides-stale-current-status.yaml` | Compact handoff cannot hide stale active issue, PR, or branch references. |
| `NEG-050-pending-human-gate-merge` | PR says `merge_allowed` while human gates are pending | blocked | policy gate / PR review | `examples/negative/policy_gate/pr_body.human-gates-pending.md` | Must fail in body-coherence and merge-decision. |
| `NEG-051-false-checks-merge` | PR says `merge_allowed` while checks are false | blocked | policy gate / PR review | `examples/negative/policy_gate/pr_body.checks-false.md` | False required gates cannot support merge_allowed. |
| `NEG-052-false-human-gate-merge` | PR says `merge_allowed` while human gates are false | blocked | policy gate / PR review | `examples/negative/policy_gate/pr_body.human-gates-false.md` | A boolean cannot bypass unresolved human review. |
| `NEG-053-blocked-result-live-eligibility` | otherwise-clean non-draft PR still declares `merge_blocked` | blocked | check-pr | `examples/negative/pr_status.merge-blocked-all-clean.json` | Must fail only on the durable Merge Decision result. |
| `NEG-054-event-missing-result` | pull_request event body has missing or invalid Merge Decision result | fail_closed | GitHub event policy routing | `examples/negative/github_events/pr.missing-result.json` | Draft status must not select a fallback mode. |
| `NEG-055-latest-duplicate-check-fails` | older success is followed by a newer failure or pending run with the same identity | blocked | check-pr | `examples/negative/pr_status.duplicate-check-latest-failure.json` | Latest reliably ordered run controls current eligibility; older run remains superseded evidence. |
| `NEG-056-duplicate-check-order-ambiguous` | duplicate check identity cannot be reliably ordered on one head | fail_closed | check-pr | `examples/negative/pr_status.duplicate-check-ambiguous.json` | Ambiguous current check state must not be guessed. |
| `NEG-057-blank-decision-state` | required decision state is blank | fail_closed | policy gate / PR review | `examples/negative/policy_gate/pr_body.blank-state.md` | Blank state must fail in body-coherence and merge-decision. |
| `NEG-058-unknown-decision-state` | required decision state is `unknown` | fail_closed | policy gate / PR review | `examples/negative/policy_gate/pr_body.unknown-state.md` | Unknown state must fail in body-coherence and merge-decision. |
| `NEG-059-generic-merge-reason` | Merge Decision reason repeats generic decision text | blocked | policy gate / PR review | `examples/negative/policy_gate/pr_body.generic-reason.md` | Structured fields cannot replace evidence, limits, and judgment. |
| `NEG-060-duplicate-decision-state` | Merge Decision contains duplicate conflicting result fields | fail_closed | policy gate / PR review | `examples/negative/policy_gate/pr_body.duplicate-state.md` | Validators must not use first-value or last-value wins. |
| `NEG-061-invalid-validation-source-shape` | validation claim source combines a scalar with nested keys | fail_closed | policy gate / schema | `examples/negative/policy_gate/pr_body.invalid-validation-source-shape.md` | Validation source must be exactly one nested object. |
| `NEG-062-event-missing-pr-object` | routed event lacks the pull_request object | fail_closed | GitHub event policy routing | `examples/negative/github_events/pr.missing-pull-request.json` | Missing PR metadata is not a successful skip. |
| `NEG-063-status-check-missing-identity` | passing check has no usable name or context | fail_closed | check-pr | `examples/negative/pr_status.missing-check-identity.json` | A synthetic unnamed identity must not establish current status. |
| `NEG-064-duplicate-check-missing-provider` | repeated same-name CheckRuns have no workflow/provider identity | fail_closed | check-pr | `examples/negative/pr_status.duplicate-check-missing-provider.json` | Timestamp order cannot prove two providers are one rerun series. |
| `NEG-065-hidden-markdown-governance` | required heading exists only inside a fence, or a required field exists only in an HTML comment outside the visible YAML record | fail_closed | policy gate / check-pr | `scripts/asgk_lib/source_validation.py` mutation projection | Fenced pseudo-headings and comment-hidden fields must not satisfy visible governance structure. |
| `NEG-066-noncanonical-exact-token` | exact-true gate or event result is quoted or uses noncanonical case | fail_closed | policy gate / event routing | `scripts/asgk_lib/source_validation.py` mutation projection | Only literal unquoted lowercase decision tokens are accepted. |
| `NEG-067-unknown-pr-state-shape` | isDraft or reviewDecision is missing, mistyped, or unknown | fail_closed | check-pr | `scripts/asgk_lib/source_validation.py` mutation projection | Non-blocking PR state must be positively established. |
| `NEG-068-invalid-files-shape` | files is not a list or an entry lacks a string path | fail_closed | check-pr | `scripts/asgk_lib/source_validation.py` mutation projection | Missing path evidence cannot skip allowlist or hygiene checks. |
| `NEG-069-invalid-check-identity-type` | name or provider identity is non-string, or repeated named runs omit type/provider evidence | fail_closed | check-pr | `scripts/asgk_lib/source_validation.py` mutation projection | String coercion cannot manufacture check identity. |
| `NEG-070-mixed-check-timestamps` | repeated runs can be ordered only by comparing different timestamp meanings | fail_closed | check-pr | `scripts/asgk_lib/source_validation.py` mutation projection | One common start/creation field is required for the identity group. |
| `NEG-071-empty-status-rollup` | check-pr receives an empty current-check list | blocked | check-pr | `scripts/asgk_lib/source_validation.py` mutation projection | Absence of checks cannot establish passing status. |
| `NEG-072-negative-runner-crash` | expected-failure command exits nonzero because the validator crashed | blocked | negative runner | `scripts/asgk_lib/source_validation.py` crash sentinel projection | Interpreter failure is not expected governance rejection evidence. |
| `NEG-073-work-unit-reason-alias` | work unit uses `intelligence_level_reason` instead of canonical `reason` | blocked | work-unit-check | `examples/negative/work_unit.reason-alias-only.json` | Must report `WU_REASON_ALIAS_FORBIDDEN` and missing canonical reason. |
| `NEG-074-work-unit-context-gate-missing` | work unit omits `context_read_set` | blocked | work-unit-check | `examples/negative/work_unit.missing-context-read-set.json` | Must report `WU_EXECUTION_GATE_MISSING` for the exact gate. |
| `NEG-075-work-unit-project-validation-gate-missing` | work unit omits `project_specific_validation` | blocked | work-unit-check | `examples/negative/work_unit.missing-project-specific-validation.json` | Must report `WU_EXECUTION_GATE_MISSING` for the exact gate. |
| `NEG-076-task-packet-legacy-reason-alias` | fallback packet uses `intelligence_level_reason` | blocked | task-packet-check | `examples/negative/task_packet.reason-alias.yaml` | Must report `TP_LEGACY_FIELD_FORBIDDEN`; v1 aliases are not v2 authority. |
| `NEG-077-task-packet-fallback-status` | fallback status is not exact `pending_unavailable` | blocked | task-packet-check | `examples/negative/task_packet.fallback-status.yaml` | Must report `TP_FALLBACK_STATUS_INVALID`. |
| `NEG-078-task-packet-authority-mismatch` | refinement names a different issue than the supplied issue | blocked | task-packet-check | `examples/negative/compact_governance/task-packet-authority-mismatch.json` | Must report `TP_AUTHORITY_MISMATCH`. |
| `NEG-079-task-packet-read-set-expansion` | refinement adds an issue-unlisted context item | blocked | task-packet-check | `examples/negative/compact_governance/task-packet-read-set-expands.json` | Must report `TP_READ_SET_EXPANSION`. |
| `NEG-080-task-packet-validation-expansion` | refinement adds an issue-unlisted project check | blocked | task-packet-check | `examples/negative/compact_governance/task-packet-validation-expands.json` | Must report `TP_VALIDATION_EXPANSION`. |
| `NEG-081-task-packet-overbroad-read-set` | packet requests a whole-repository context read | blocked | task-packet-check | `examples/negative/task_packet.overbroad-context-read-set.yaml` | Must report `TP_READ_SET_OVERBROAD`. |
| `NEG-082-task-packet-empty-required-list` | fallback packet has an empty required list | blocked | task-packet-check | `examples/negative/task_packet.empty-list.yaml` | Must report `TP_LIST_EMPTY` for the actual empty field. |
| `NEG-083-hidden-work-unit-authority` | all 13 fields and gates exist only inside an HTML comment | blocked | work-unit-check | `scripts/asgk_lib/source_validation.py` mutation projection | Hidden text must not satisfy visible authority; missing-field/gate codes remain exact. |
| `NEG-084-work-unit-gate-semantics` | issue uses whole-repo or outside-root context, or bare `not_applicable` validation | blocked | work-unit-check | `scripts/asgk_lib/source_validation.py` mutation projections | Must report `WU_READ_SET_OVERBROAD`, `WU_READ_SET_OUTSIDE_REPO`, or `WU_PROJECT_VALIDATION_REASON_MISSING`. |
| `NEG-085-task-packet-unsafe-allowed-path` | packet allowed path is absolute or contains a dot segment | blocked | task-packet-check | `scripts/asgk_lib/source_validation.py` mutation projections | Must report `TP_ALLOWED_PATH_INVALID` before containment comparison. |
| `NEG-086-task-packet-context-root-escape` | packet context is absolute, traversal-based, or a symlink outside the repo | blocked | task-packet-check | `scripts/asgk_lib/source_validation.py` mutation projections | Must report `TP_READ_SET_OUTSIDE_REPO`; context measurement must not read it. |
| `NEG-087-task-packet-list-item-type` | schema list contains a number, object, boolean, or blank item | blocked | task-packet-check | `scripts/asgk_lib/source_validation.py` mutation projection | Runtime behavior must match the schema's non-empty string items. |
| `NEG-088-task-packet-invalid-source-issue` | refinement depends on an issue containing chat-only authority, unsafe paths/gates, or an unrelated-repo URL | blocked | task-packet-check | `scripts/asgk_lib/source_validation.py` mutation projections | Must report source-authority-specific codes and skip non-expansion claims when issue validation fails. |
| `NEG-089-task-packet-case-sensitive-exactness` | refinement changes path or command case or internal text | blocked | task-packet-check | `scripts/asgk_lib/source_validation.py` mutation projections | Exact read/validation comparison must preserve case and content. |
| `NEG-090-task-packet-glob-containment` | one packet glob is tested against a different issue glob | blocked | task-packet-check | `scripts/asgk_lib/source_validation.py` mutation projection | Without a proven set-subset algorithm, packet glob must exactly equal an issue glob. |
| `NEG-091-hidden-task-packet` | the complete fallback is hidden inside an HTML comment | blocked | task-packet-check | `scripts/asgk_lib/source_validation.py` mutation projection | Must fail visible parsing with `TP_MODE_MISSING`. |
| `NEG-092-context-reference-smuggling` | issue/URL prefix appends a whole-repo request, or arbitrary prose/nonexistent path is presented as context | blocked | work-unit-check / task-packet-check | `scripts/asgk_lib/source_validation.py` mutation projections | Whole-item pseudo-reference grammar and existing-file checks must report the exact overbroad or invalid-reference code. |
| `NEG-093-fallback-protected-scope` | GitHub-unavailable fallback names a mechanically recognizable protected governance path | blocked | task-packet-check | `scripts/asgk_lib/source_validation.py` mutation projection | Must report `TP_FALLBACK_ESCALATION_REQUIRED` and must not emit conditional local-work authority. |
| `NEG-094-refinement-pr-as-issue` | issue_refinement receives a PR-shaped payload identified by its URL or PR markers, including an explicit issue request that conflicts with PR markers | blocked | work-unit-check / task-packet-check | `scripts/asgk_lib/source_validation.py` mutation projections | Must report `TP_ISSUE_SCOPE_INVALID` or `WU_KIND_INVALID`; a caller hint cannot make a PR payload authoritative as an issue. |
| `NEG-095-not-applicable-empty-reason` | project validation uses `not_applicable` plus punctuation or connector words but no material reason | blocked | work-unit-check / task-packet-check | `scripts/asgk_lib/source_validation.py` mutation projections | Existing reason-missing finding codes must remain exact; positive Unicode reasons must remain accepted. |
| `NEG-096-refinement-qualified-wrong-repo` | refinement source text prefixes a matching issue number with a conflicting repository name | blocked | task-packet-check | `scripts/asgk_lib/source_validation.py` mutation projection | Must report `TP_AUTHORITY_MISMATCH`; only anchored local issue grammar or an exact same-repo URL is accepted. |
| `NEG-097-work-unit-task-field-ambiguity` | work unit repeats an individual heading using ATX H1-H6 or Setext syntax, mixes heading and canonical YAML forms, quotes or repeats a YAML key, changes the exact canonical label/level or supplies multiple canonical fences, or hides broad context behind a lower-level heading | blocked | work-unit-check | `scripts/asgk_lib/source_validation.py` mutation projections | Must report only `WU_TASK_FIELD_AMBIGUOUS` for ambiguous field parsing; Setext underlines never become data, lower-level content remains inside its owning field, and no first/last occurrence may grant authority. |
| `NEG-098-source-issue-task-field-ambiguity` | issue_refinement source issue mixes representations, repeats or quotes a top-level canonical YAML key, or places a quoted task field outside the sole canonical fence | blocked | task-packet-check | `scripts/asgk_lib/source_validation.py` mutation projections | Must report `TP_ISSUE_TASK_FIELD_AMBIGUOUS` and list scope/read/validation non-expansion as not checked. |
| `NEG-099-raw-task-packet-duplicate-key` | raw YAML fallback repeats a top-level task-packet key | blocked | task-packet-check / context-budget-measure | `scripts/asgk_lib/source_validation.py` mutation projection | Must report `TP_TASK_FIELD_AMBIGUOUS`; duplicate-key YAML cannot silently use the last value. |
| `NEG-100-competing-task-packet-source` | file-backed YAML supplies raw-plus-wrapper, nested, competing, or wrapper-plus-unrelated sources; file-backed JSON supplies competing wrappers or wrapper-plus-unrelated fields; a fixture bundle places raw packet fields beside task_packet | blocked | task-packet-check / compact-task-packet-check / context-budget-measure | `scripts/asgk_lib/source_validation.py` mutation projections | Must report `TP_TASK_FIELD_AMBIGUOUS`, preserve compact parity, and emit no temporary authority; valid sole wrappers remain positive controls. |
| `NEG-101-task-packet-yaml-scalar-type` | raw YAML uses implicit null, boolean, decimal, hexadecimal, octal, or binary numeric values where the schema requires strings | blocked | task-packet-check | `scripts/asgk_lib/source_validation.py` mutation projections | Must report exact `TP_FIELD_TYPE_INVALID` or `TP_LIST_ITEM_TYPE_INVALID` findings rather than coercing values to strings. |
| `NEG-102-source-issue-reason-alias` | issue_refinement source issue includes `intelligence_level_reason`, with or without canonical `reason` | blocked | task-packet-check | `scripts/asgk_lib/source_validation.py` mutation projection | Must report `TP_ISSUE_REASON_ALIAS_FORBIDDEN` and skip dependent non-expansion claims. |
| `NEG-103-source-inventory-missing-path` | supplied source inventory omits one retained canonical path | blocked | source_validation.py | `examples/negative/source_validation/missing-required-path.json` | Must emit only `SV_REQUIRED_PATH_MISSING` with the exact missing path. |
| `NEG-104-source-validation-input-mode` | caller combines live `--repo-root` and supplied `--source-inventory-file` modes | blocked | source_validation.py | registered controlled scenario | Must emit only `SV_INPUT_MODE_INVALID`; no source or target validation ran. |
| `NEG-105-source-inventory-unreadable` | supplied source inventory cannot be read | blocked | source_validation.py | registered controlled scenario | Must emit only `SV_INVENTORY_FILE_UNREADABLE`. |
| `NEG-106-source-inventory-invalid-json` | supplied source inventory is malformed JSON | blocked | source_validation.py | registered temporary input | Must emit only `SV_INVENTORY_JSON_INVALID`. |
| `NEG-107-source-inventory-invalid-shape` | supplied inventory is not the exact normalized unique path-array object | blocked | source_validation.py | registered temporary input | Must emit only `SV_INVENTORY_SHAPE_INVALID`. |
| `NEG-108-source-inventory-duplicate-key` | supplied inventory repeats a JSON object key and a later value would otherwise replace the earlier value | blocked | source_validation.py | registered transformed temporary input | Must emit only `SV_INVENTORY_SHAPE_INVALID`; JSON last-key-wins behavior cannot create evidence. |
| `NEG-109-source-inventory-json-too-deep` | supplied inventory exceeds the explicit pre-parse JSON nesting bound | blocked | source_validation.py | registered generated temporary input | Must emit one envelope with only `SV_INVENTORY_JSON_INVALID`, never depend on interpreter recursion behavior or produce a traceback. |
| `NEG-110-target-evidence-no-claims` | target evidence command receives no caller claim | blocked | target_evidence.py | registered `target_evidence_no_claims_incomplete` scenario | Must emit `TE_CLAIMS_MISSING`, domain `incomplete`, common `blocked`, and exit `1`; no target layout is inferred. |
| `NEG-111-target-evidence-four-mismatches` | complete caller claims disagree on expected path, forbidden path, expected text, and forbidden text | blocked | target_evidence.py | `examples/negative/target_evidence/mismatched_claims/notes/project.marker` | Must emit the exact four mismatch-code multiset and domain `claims_mismatch`; mismatch is not a target-fit conclusion. |
| `NEG-112-target-evidence-unsafe-path` | claim path is absolute, drive-prefixed, non-normalized, globbed, traversal-based, control-bearing, non-Unicode-scalar, resolves outside the root, or has a checked parent concurrently replaced by an outside-root symlink | blocked | target_evidence.py | direct bounded command and race probes | Unsafe syntax or symlink resolution must emit `TE_CLAIM_PATH_INVALID`; a replacement race may instead be incomplete or observe an in-root state, but must never read outside-root content. |
| `NEG-113-target-evidence-root-unavailable` | target root is missing, unreadable, or not a directory | blocked | target_evidence.py | direct bounded command probe | Must emit `TE_TARGET_ROOT_UNAVAILABLE`, domain `incomplete`, and no traceback. |
| `NEG-114-target-evidence-empty-literal` | text claim supplies an empty literal | blocked | target_evidence.py | direct bounded command probe | Must emit `TE_LITERAL_EMPTY`; an empty substring cannot manufacture a match. |
| `NEG-115-target-evidence-non-text` | text claim names a non-file, unreadable file, or invalid UTF-8 evidence | blocked | target_evidence.py | direct bounded command probes | Must emit the corresponding stable incomplete code and never expose target contents or the caller literal. |
| `NEG-116-target-evidence-invalid-literal` | text claim contains a non-Unicode-scalar value | blocked | target_evidence.py | direct bounded evaluator probe | Must emit `TE_LITERAL_INVALID`, domain `incomplete`, and no traceback. |
| `NEG-117-release-state-stale-completed-tag` | one otherwise-valid release-state set still describes the completed tag as candidate or pending | blocked | release-state-check / scenario registry | `examples/negative/release_state/README.stale-v1-2-candidate.md` | Exit `1`; exact finding multiset is `RS_STALE_RELEASE_STATE`; all other inputs are positive. |
| `NEG-118-release-state-duplicate-ledger` | one otherwise-valid release-state set contains a duplicate per-release ledger | blocked | release-state-check / scenario registry | `examples/negative/release_state/SOURCE_ONLY_RELEASE_POLICY.ledger.md` | Exit `1`; exact finding multiset is `RS_DUPLICATE_RELEASE_LEDGER`; all other inputs are positive. |

## Current Execution Surface

Negative fixtures are active opt-in expected-failure inputs. The executable
owner and its projections are:

```yaml
negative_runner_surface:
  exact_scenario_owner: scripts/asgk_lib/scenario_registry.py
  exact_execution_verifier: scripts/asgk_lib/scenario_runner.py
  facade: scripts/asgk_lib/negative.py
  compatibility_wrappers:
    - scripts/asgk_lib/negative_cases.py
    - scripts/asgk_lib/negative_runner.py
  composed_by:
    - python3 scripts/asgk.py doctor
    - .github/workflows/bootstrap-validation.yml
```

```bash
python3 scripts/asgk.py negative all
python3 scripts/asgk.py negative <group>
python3 scripts/asgk.py negative --help
```

Positive validation must not load negative fixtures as valid repository state.
Default startup must not read `examples/` unless the current issue, PR,
validator, or documentation reference names a specific example or fixture.

For each retained JSON behavior, the registry owns at least one positive and one
negative scenario. It records the exact owner command, polarity, exit, common
result, finding-code multiset, human-gate state, and proof boundary. The runner
also checks task-packet alias parity, source-validator/wrapper parity, controlled
input failures, and rejects
false evidence such as signals, tracebacks, stderr, mixed output, malformed
JSON, wrong results, wrong code multiplicity, wrong proof boundaries, wrong
human-gate or domain states, and wrong checked/unchecked claims. Branch-specific
scenarios lock exact checked/unchecked lists when an early failure could
otherwise overclaim work. Controlled live scenarios cover both a nonzero tool
response and an executable that is absent from `PATH`.

The `source-validation` scenario group pairs one complete retained source
inventory with one inventory missing only `README.md`. Supplied-inventory
success checks list membership only: it does not read named files or establish
target fit, target layout, adoption readiness, human approval, or merge
authority.

The `target-evidence` group pairs an arbitrary-layout success containing no
ASGK-named target file with a four-claim mismatch and a no-claim incomplete
case. It locks exact domain/common results, exits, finding-code multisets,
checked and unchecked claims, human-gate state, and proof boundary. These
scenarios also lock the exact bounded claim records and literal metadata,
`writes_performed: false`, the allowed top-level payload keys, forbidden raw
literal or fixture-content output (including JSON-escaped forms), and unchanged
target-fixture tree fingerprints. They validate only caller-supplied
mechanical claims; they do not select claims or judge target fit, layout,
governance depth, adaptation, readiness, recommendation, or approval.

The `release-state` group pairs one three-document positive set with isolated
stale-state and duplicate-ledger negatives. It locks exact exit, common result,
finding-code multiset, checked and unchecked claims, `human_gate.status:
not_checked`, proof boundary, top-level keys, and unchanged input
fingerprints. The group proves local document coherence only; release
existence, tag existence, GitHub metadata, semantic readiness, human approval,
publication authority, and merge authority remain unchecked.

Positive lifecycle coverage must separately prove:

```yaml
positive_pr_lifecycle:
  - draft merge_blocked passes file-backed body-coherence preflight
  - ready-for-review merge_blocked event passes body-coherence but remains blocked in check-pr
  - non-draft merge_allowed event passes strict merge-decision
  - clean live or fixture check-pr passes without inferring low-risk or approval
  - older failed duplicate check followed by newer success records the older run as superseded
```

## Rules For Negative Fixtures

Each negative fixture should either be referenced by an executable registry
scenario, retained by one explicitly bounded legacy regression group, or named
by a scoped future validation issue. When practical, include metadata or front
matter:

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

Do not add a negative fixture without an expected outcome. Metadata remains
descriptive and never overrides the registry.

## Blocking vs Human-Gated Distinction

In this human matrix, `blocked` means the work is invalid or cannot proceed
under current policy. It is not automatically identical to a validator's
top-level result token.

`human_gated` means the work may be valid only with explicit durable human
approval. Human-gated work should not be hidden inside low-risk PRs.

When a retained JSON command mechanically detects that boundary, it reports
`result: blocked` with `human_gate.status: required`; it never reports that
approval passed.

A simultaneous mechanical failure does not erase the gate. The common result
stays `blocked`, the restricted-boundary and mechanical finding codes both
remain present, and a command-specific `domain_result: fail` may describe the
mechanical branch.

`human_gates_checked: true` is not approval evidence by itself. When a human
gate applies, the durable record must identify the reviewed current head or
diff. Review from an older head or closed-unmerged PR is stale unless explicitly
reaffirmed.

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

For a wrong approach, close the PR unmerged and preserve its branch, commits,
CI, comments, and decision record before restarting from current `main`. Do not
delete failed-attempt evidence or treat a closed-unmerged PR as a change to
`main`.

## Remaining Gaps

```yaml
known_gaps:
  - not every planned negative case has an implemented fixture
  - legacy text-oriented regression groups remain for non-retained surfaces until their separately scoped cutovers
  - not every fixture file is independently registered; the registry owns behavior scenarios, not a permanent fixture inventory
  - PR-body fixtures intentionally preserve markdown parser coverage and should not be converted wholesale to JSON
```

These are follow-up opportunities, not a reason to delete active regression
fixtures without coverage evidence.
