# PR Review Checklist

Status: active control checklist.

This checklist turns pull request review into a repeatable gate. It is used
before approval, request changes, low-risk merge, or human-gated escalation.

## Canonical References

Use this checklist with:

```yaml
source_of_truth_rule: AGENTS.md
context_budget: docs/control/CONTEXT_BUDGET_POLICY.md
capability_matrix: docs/control/AGENT_CAPABILITY_MATRIX.md
validation_strategy: docs/control/VALIDATION_STRATEGY.md
low_risk_merge_policy: docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md
human_gates: docs/control/HUMAN_GATED_OPERATIONS.md
merge_decision_record: docs/control/MERGE_DECISION_RECORD.md
document_ownership: docs/DOCUMENT_MAP.md
current_status_policy: docs/control/CURRENT_STATUS_POLICY.md
```

If this checklist conflicts with a canonical policy, prefer the canonical policy
and open a follow-up issue to update this checklist.

## Review Inputs

Before reviewing, collect only the necessary context.

```yaml
required_review_inputs:
  - current PR body
  - changed file list
  - linked issue or durable source of truth
  - GitHub Actions status
  - relevant target files when needed
  - canonical policy files only when the PR touches their topic
```

Do not read the whole repository by default. Follow the linked authority's exact
`context_read_set`. Repo entries must be existing regular files and durable
references must occupy whole items; use a named classification from
`docs/control/CONTEXT_BUDGET_POLICY.md` only as advisory selection help.

## Step 1 — Source Of Truth Check

Confirm:

- [ ] Executable work links to a current GitHub issue or already-open PR.
- [ ] Linked authority contains all 13 canonical fields from `AGENTS.md`.
- [ ] `reason` is the formal field name; `intelligence_level_reason` is not used
      as a substitute.
- [ ] Linked authority separately contains material `context_read_set` and
      `project_specific_validation` execution gates.
- [ ] Pre-write `work-unit-check --authority-only` evidence exists when the
      repository command is available.
- [ ] The PR does not rely on `see chat` for scope, acceptance, or handoff.
- [ ] The PR body names the durable source of truth.

Block when:

- [ ] No valid GitHub authority exists for executable work.
- [ ] A task packet or repo document is used as executable authority while
      GitHub is available.
- [ ] Scope or acceptance exists only in chat.
- [ ] Linked issue appears stale or already satisfied.

Use `docs/control/ISSUE_HYGIENE_GATE.md` for stale issue review.

## Step 2 — Scope And Allowed Path Check

Confirm:

- [ ] Changed files match the issue's allowed paths.
- [ ] PR does not include unrelated cleanup.
- [ ] PR does not mix docs, code, schema, CI, and policy work unless explicitly scoped.
- [ ] Generated/runtime artifacts are absent.
- [ ] Protected paths are absent.

Block when:

- [ ] Any file is outside allowed paths without explicit issue authorization.
- [ ] Runtime artifacts, private source files, cache files, live DBs, or secrets are present.
- [ ] A new top-level directory appears without explicit approval.

For path hygiene, use:

```bash
python3 scripts/governance_hygiene.py --paths-file changed-paths.txt
```

when a changed-path list is available.

## Step 3 — Capability And Risk Check

Confirm:

- [ ] Task type matches the agent level used.
- [ ] Task did not cross into a higher-risk category.
- [ ] Any escalation or downscoping is recorded.

Use `docs/control/AGENT_CAPABILITY_MATRIX.md`.

Block or request changes when:

- [ ] A `fast_basic` or `standard` task performed advanced/security/policy work.
- [ ] The PR loosens policy without explicit approval.

## Step 4 — Context Budget Check

Confirm:

- [ ] PR or Agent Report records the exact context read set when non-trivial.
- [ ] Any named context classification is identified as advisory only.
- [ ] Any context expansion is explained.
- [ ] The agent did not read unrelated documents without a reason.
- [ ] Summary documents were not treated as canonical when canonical docs exist.

Use `docs/control/CONTEXT_BUDGET_POLICY.md` and `docs/DOCUMENT_MAP.md`.

Request changes when:

- [ ] Context expansion is material but unrecorded.
- [ ] The PR decision relies on a summary document that conflicts with a canonical doc.

## Step 5 — Current Status Freshness Check

Confirm:

- [ ] PR includes a `Current Status Impact` section.
- [ ] The section sets status to exactly one of: `updated`, `not_applicable`, or `deferred`.
- [ ] Milestone-impacting or resume-surface-impacting PRs either update `docs/handoff/CURRENT_STATUS.md` in the same PR or explain a valid deferral.
- [ ] `not_applicable` is reasonable for the changed files and does not hide a recovery-state change.
- [ ] `deferred` includes a reason and a follow-up issue or next safe action when repo-level recovery would otherwise be unsafe.
- [ ] If `CURRENT_STATUS.md` changed, it is accurate for the repository state after merge and does not point to the same PR as active.

Use `docs/control/CURRENT_STATUS_POLICY.md`.

Request changes when:

- [ ] `Current Status Impact` is missing.
- [ ] A roadmap, milestone, stabilization, install-surface, decision-governance, or handoff-relevant tooling PR marks current status as `not_applicable` without a clear reason.
- [ ] `deferred` lacks a follow-up path and the current compact status would mislead the next agent.
- [ ] `CURRENT_STATUS.md` is updated but would become self-stale immediately after merge.

## Step 6 — Validation Check

Confirm:

- [ ] Reviewer distinguishes `body-coherence`, strict `merge-decision`, and live
      `check-pr` evidence.
- [ ] GitHub PR event auto-routing used the declared
      `merge_decision.result`, not draft status alone. File-backed preflight
      explicitly used `body-coherence`; direct CLI and `check-pr` used strict
      `merge-decision`.
- [ ] For merge readiness, GitHub Actions completed successfully.
- [ ] PR records validation commands and results.
- [ ] Validation not run has a valid reason.
- [ ] Docs-only PRs still pass bootstrap validation.
- [ ] Script or validation behavior changes include explicit test evidence.

Current baseline validation:

```bash
python3 scripts/asgk.py doctor
python3 scripts/asgk.py validate
python3 scripts/validate_bootstrap.py
git diff --check
```

`asgk validate` and the bootstrap wrapper must reach
`scripts/asgk_lib/source_validation.py`. `doctor` composes that same source
engine with status, diff, and registered scenario checks. Do not treat
`scripts/check_project.py` as an active validation prerequisite; it remains only
until its separately scoped W6D deletion.

If validation used a non-default live `--repo-root`, confirm the report names
both the inspected source and validator reference roots. Such validation may
execute repository-local Python from the inspected root and therefore applies
only to a trusted ASGK source tree, never an arbitrary target.

Block merge readiness when:

- [ ] Required checks are failing, pending, missing, or unknown.
- [ ] `merge_allowed` passed without every exact-true gate set to true or
      without concrete attribution and boundary fields.
- [ ] Blank, missing, unknown, or unsupported required decision state was accepted.
- [ ] A quoted state token, HTML-commented field, or fenced pseudo-heading was
      accepted as real governance structure.
- [ ] Duplicate current-head check runs cannot be reliably ordered, or the latest
      run is failing or pending.
- [ ] Repeated same-name CheckRuns lack workflow/app/provider identity and could
      belong to different providers.
- [ ] `check-pr` accepted an unknown draft/review state, malformed files list,
      non-string check identity, or mixed timestamp semantics.
- [ ] Validation script behavior changed but no test/fixture evidence is provided.
- [ ] CI failure is unexplained.

Use `docs/control/VALIDATION_STRATEGY.md` for validator responsibilities.

A coherent `merge_blocked` body may truthfully contain pending or false
checks/human gates and pass `body-coherence`. That is valid review state, not
merge eligibility. Before merge readiness, require strict `merge-decision` and
live `check-pr`.

## Step 7 — Storage And Runtime Boundary Check

Confirm:

- [ ] No Artifact Root writes from repo task.
- [ ] No Local State Root writes from repo task.
- [ ] No runtime outputs committed.
- [ ] No SQLite live DB, preview cache, model cache, or scratch files committed.
- [ ] No private source materials committed.

Block when:

- [ ] Storage roots are mixed.
- [ ] Runtime artifact boundary is unclear.
- [ ] Externalized preparation outputs are moved into the repo without authorization.

Canonical references:

```text
docs/architecture/STORAGE_PROFILE.md
docs/architecture/RUNTIME_ARTIFACT_POLICY.md
docs/architecture/CACHE_AND_STATE_POLICY.md
docs/architecture/EXTERNALIZED_RESPONSIBILITY_BOUNDARY.md
```

## Step 8 — Human Gate Check

Confirm whether the PR touches any human-gated operation:

- [ ] destructive git operation
- [ ] security boundary change
- [ ] storage boundary change
- [ ] schema breaking change
- [ ] database migration
- [ ] new dependency
- [ ] new parser/model dependency
- [ ] new cloud egress
- [ ] Google Drive API integration
- [ ] MCP tool or MCP write capability
- [ ] release/publication decision
- [ ] milestone closure
- [ ] merge policy authority change

If yes, the PR is not low-risk merge eligible. A durable approval record may
authorize the human-gated path, but it does not convert the work into low-risk
autonomous merge.

Required approval record:

```yaml
human_gate:
  operation:
  reason:
  risks:
  rollback_plan:
  approval_source:
  reviewed_head:
  reviewed_diff:
  decision: approved | changes_requested | rejected
  decided_by:
  decided_at:
  reaffirmed_after_head_change: true | false | not_applicable
```

Use `docs/control/HUMAN_GATED_OPERATIONS.md`.

`human_gates_checked: true` is a claim, not evidence by itself. When a human
gate applies, confirm the current-head durable record says
`decision: approved`. `changes_requested` or `rejected` requires
`human_gates_checked: false` and `result: merge_blocked`. When no gate applies,
confirm the durable no-gate risk/path determination. New code commits
invalidate review of an older head unless the human reaffirms it. Do not reuse
review from a prior or closed-unmerged PR.

When a program-scoped reversible merge path is claimed, also confirm:

- [ ] The program issue contains durable OWNER execution authorization.
- [ ] An OWNER-approved exact scope source predates the child issue.
- [ ] The current child issue explicitly invokes it and is equal to or narrower
      than the exact work-unit path/action set.
- [ ] The PR carries the canonical `program_execution_authorization` record.
- [ ] The work changes tracked source only, has no external side effect beyond
      routine issue/PR metadata, is completely ordinary-revert-safe, and is
      independently reviewed.
- [ ] Current-head evidence confirms semantic scope match and that no
      Human-Gated Operations item applies.
- [ ] Scope/no-gate review, independent review, CI, and `check-pr` were
      refreshed after the latest commit.
- [ ] The record does not claim the OWNER reviewed the current head or diff.
- [ ] The PR is not changing the program path, human gates, merge authority, or
      enforcement/non-inference semantics, including by creating, removing,
      loosening, tightening, or reclassifying them.

Even with a durable approval record, the Agent reports `requires_human` for a
human-gated merge unless canonical policy and the current issue explicitly
authorize that escalated merge path.

## Step 9 — Merge Decision Record Check

Confirm PR includes:

```yaml
merge_decision:
  issue:
  lane:
  intelligence_level:
  durable_source_of_truth:
  checks_passed:
  allowed_paths_checked:
  expected_output_checked:
  contracts_checked:
  schemas_checked:
  storage_boundary:
  runtime_artifact_boundary:
  safety_review:
  human_gates_checked:
  validation_evidence_checked:
  validation_claim_source:
    local_doctor:
    ci:
  result: merge_allowed | merge_blocked
  reason:
```

For GitHub PR event auto-routing, route body validation from the durable result:

```text
merge_blocked -> body-coherence
merge_allowed -> merge-decision
missing/invalid result -> fail closed
```

File-backed create/edit preflight explicitly selects `body-coherence`; direct
CLI and `check-pr` explicitly select strict `merge-decision`.

For `body-coherence`, confirm:

- [ ] `allowed_paths_checked`, `expected_output_checked`, and
      `validation_evidence_checked` are exactly true.
- [ ] `merge_blocked` uses only true, pending, or false for
      `checks_passed` and `human_gates_checked`.
- [ ] Blank, missing, unknown, and unsupported required states fail.
- [ ] Passing output states that merge eligibility, low-risk status, and human
      approval were not inferred.

For strict `merge-decision`, confirm:

- [ ] `result` is `merge_allowed`.
- [ ] Every exact-true gate is true and attribution/boundary fields are
      complete and concrete.
- [ ] The result is described as body-level decision clarity, not full live PR
      eligibility.

Block merge readiness when:

- [ ] Merge Decision Record is missing.
- [ ] `result` is `merge_blocked`, even when the body is coherent and ready for review.
- [ ] Any strict required gate is pending, unknown, false, blank, or missing.
- [ ] `result` is `merge_allowed` but an applicable human gate lacks a durable
      current-head `decision: approved` record.
- [ ] Reason does not match the actual risk.

Use `docs/control/MERGE_DECISION_RECORD.md`.

After strict `merge-decision`, run live `check-pr`. It independently requires an
open, non-draft, mergeable PR, non-blocking review state, current passing
checks, closing issue authority, allowed paths, and hygiene. It must reject
every `merge_blocked` result and report `low_risk_inferred: false`.

## Step 10 — Review Outcome

Choose exactly one outcome. When more than one description appears relevant,
apply the first matching outcome in this precedence order:

```text
block
  -> split_required
  -> request_changes
  -> requires_human
  -> reviewable_merge_blocked
  -> check_pr_clear
```

Higher-precedence findings may be listed as evidence, but do not report a
second outcome.

### `reviewable_merge_blocked`

Use when:

- [ ] `body-coherence` passes for `merge_blocked`.
- [ ] The PR is ready to receive review or preserve a revision blocker.
- [ ] No `block`, `split_required`, `request_changes`, or explicit
      human-gate-only condition applies.
- [ ] No claim of merge eligibility or approval is made.

### `check_pr_clear`

Use when:

- [ ] All required checks pass.
- [ ] Scope matches issue.
- [ ] The human-gate boundary is clear: either no gate applies, or a durable
      current-head `decision: approved` record exists and canonical policy plus
      the current issue explicitly authorize the escalated merge path.
- [ ] Any program-scoped reversible path has a complete canonical record,
      OWNER-approved exact scope source, current-issue scope no broader than it,
      tracked-source/no-external-side-effect boundary, current-head scope/no-gate
      evidence, independent review, and no human-gated operation.
- [ ] Strict `merge-decision` and live `check-pr` pass.
- [ ] Runtime artifact and storage boundaries are clean.

If all low-risk merge policy gates pass, the PR may be merged under
`docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md`.

This outcome is not approval; a human or canonical policy still makes the merge
decision.

### `requires_human`

Use when:

- [ ] No `block`, `split_required`, or `request_changes` condition applies.
- [ ] A specific human-gated decision or issue/policy-required semantic
      acceptance remains unresolved, or explicit canonical-policy/current-issue
      authority for an escalated merge path is absent.
- [ ] A program grant is being used as a substitute for current-head human
      review of an operation that remains human-gated.
- [ ] Currently applicable non-human checks may be clear, but the named human
      decision or merge authority remains.
- [ ] Required current-head human evidence is missing, stale, or awaiting
      reaffirmation.

Do not use this outcome merely because an ordinary ready-for-review PR is
waiting for routine review; use `reviewable_merge_blocked` for that state.

### `request_changes`

Use when:

- [ ] PR is directionally correct but missing required sections, evidence, or
      bounded fixes.
- [ ] Validation is fixable inside the same scope.
- [ ] Changed files include small unintended drift that can be removed.

### `block`

Use when:

- [ ] Human-gated operation is outside durable scope or was rejected.
- [ ] Scope is wrong.
- [ ] Protected path or runtime artifact is present.
- [ ] Validation fails for unclear reasons.
- [ ] Required change would exceed allowed paths.
- [ ] The issue is stale or not a valid source of truth.

### `split_required`

Use when:

- [ ] PR mixes unrelated work units.
- [ ] Docs, code, schema, CI, or policy changes need separate risk handling.
- [ ] A low-risk part can merge separately from a high-risk part.

## Reviewer Comment Template

```md
## PR Review Result

Outcome: reviewable_merge_blocked | check_pr_clear | requires_human | request_changes | block | split_required

Evidence:
- Linked issue/source:
- Changed files:
- Validation:
- Current Status Impact:
- Runtime artifact status:
- Human gates:
- Merge Decision Record:

Required changes:
- <none or list>

Notes:
- <optional>
```

## Anti-Patterns

Do not approve or merge when:

- Checks are pending or unknown.
- The durable result is `merge_blocked`; a coherent blocked body is reviewable,
  not merge-eligible.
- Human review applies only to an older head or a closed-unmerged PR.
- A boolean or green workflow is presented as human approval.
- The PR says `see chat` for scope or acceptance.
- A summary doc conflicts with a canonical doc.
- The agent changed files outside allowed paths.
- The PR includes runtime artifacts.
- A human-gated operation is hidden inside a docs or tooling change.
- The PR body lacks a Merge Decision Record.
- The PR is large because unrelated cleanup was bundled in.
- The PR lacks Current Status Impact classification.
- The PR changes milestone, roadmap, install surface, decision governance, or handoff-relevant tooling without updating or explicitly deferring `CURRENT_STATUS.md`.

## Relationship To Future Negative Tests

The negative test plan should include cases that intentionally violate this
checklist, such as:

- missing Merge Decision Record;
- changed file outside allowed paths;
- runtime artifact path;
- `see chat` durable source;
- pending or missing checks;
- human gate without approval;
- missing Current Status Impact section.

Those cases should be opt-in expected-failure fixtures and must not break normal
positive validation unless a validator is explicitly designed to read them as
negative fixtures.
