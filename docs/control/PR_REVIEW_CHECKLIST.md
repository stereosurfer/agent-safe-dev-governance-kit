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

Do not read the whole repository by default. Use the `merge_decision` or
appropriate task profile from `docs/control/CONTEXT_BUDGET_POLICY.md`.

## Step 1 — Source Of Truth Check

Confirm:

- [ ] PR links to a GitHub issue or durable repo document.
- [ ] Linked source includes objective, allowed paths, expected output, checklist,
      acceptance sheet, stop conditions, and rollback expectations.
- [ ] The PR does not rely on `see chat` for scope, acceptance, or handoff.
- [ ] The PR body names the durable source of truth.

Block when:

- [ ] No durable source of truth exists.
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
- [ ] Sub-agent use, if any, is allowed for this task type.
- [ ] Task did not cross into a higher-risk category.
- [ ] Any escalation or downscoping is recorded.

Use `docs/control/AGENT_CAPABILITY_MATRIX.md`.

Block or request changes when:

- [ ] A `fast_basic` or `standard` task performed advanced/security/policy work.
- [ ] A sub-agent acted as final authority for a human-gated task.
- [ ] The PR loosens policy without explicit approval.

## Step 4 — Context Budget Check

Confirm:

- [ ] PR or Agent Report records the selected context profile when non-trivial.
- [ ] Any context expansion is explained.
- [ ] The agent did not read unrelated documents without a reason.
- [ ] Summary documents were not treated as canonical when canonical docs exist.

Use `docs/control/CONTEXT_BUDGET_POLICY.md` and `docs/DOCUMENT_MAP.md`.

Request changes when:

- [ ] Context expansion is material but unrecorded.
- [ ] The PR decision relies on a summary document that conflicts with a canonical doc.

## Step 5 — Validation Check

Confirm:

- [ ] GitHub Actions completed successfully.
- [ ] PR records validation commands and results.
- [ ] Validation not run has a valid reason.
- [ ] Docs-only PRs still pass bootstrap validation.
- [ ] Script or validation behavior changes include explicit test evidence.

Current baseline validation:

```bash
python3 scripts/check_project.py
python3 scripts/validate_bootstrap.py
git diff --check
```

Block when:

- [ ] Required checks are failing, pending, missing, or unknown.
- [ ] Validation script behavior changed but no test/fixture evidence is provided.
- [ ] CI failure is unexplained.

Use `docs/control/VALIDATION_STRATEGY.md` for validator responsibilities.

## Step 6 — Storage And Runtime Boundary Check

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

## Step 7 — Human Gate Check

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

If yes, the PR is not low-risk merge eligible unless a durable human approval
record exists.

Required approval record:

```yaml
human_gate:
  operation:
  reason:
  risks:
  rollback_plan:
  approval_source:
  approved_by:
  approved_at:
```

Use `docs/control/HUMAN_GATED_OPERATIONS.md`.

## Step 8 — Merge Decision Record Check

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
  result: merge_allowed | merge_blocked
  reason:
```

Block when:

- [ ] Merge Decision Record is missing.
- [ ] `checks_passed` is pending, unknown, or false.
- [ ] `result` is `merge_allowed` but a human gate applies.
- [ ] Reason does not match the actual risk.

Use `docs/control/MERGE_DECISION_RECORD.md`.

## Step 9 — Review Outcome

Choose exactly one outcome.

### `approve_or_merge_eligible`

Use when:

- [ ] All required checks pass.
- [ ] Scope matches issue.
- [ ] No human gate applies.
- [ ] Merge Decision Record is complete.
- [ ] Runtime artifact and storage boundaries are clean.

If all low-risk merge policy gates pass, the PR may be merged under
`docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md`.

### `request_changes`

Use when:

- [ ] PR is directionally correct but missing required sections, evidence, or
      bounded fixes.
- [ ] Validation is fixable inside the same scope.
- [ ] Changed files include small unintended drift that can be removed.

### `block`

Use when:

- [ ] Human-gated operation lacks approval.
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

Outcome: approve_or_merge_eligible | request_changes | block | split_required

Evidence:
- Linked issue/source:
- Changed files:
- Validation:
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
- The PR says `see chat` for scope or acceptance.
- A summary doc conflicts with a canonical doc.
- The agent changed files outside allowed paths.
- The PR includes runtime artifacts.
- A human-gated operation is hidden inside a docs or tooling change.
- The PR body lacks a Merge Decision Record.
- The PR is large because unrelated cleanup was bundled in.

## Relationship To Future Negative Tests

The negative test plan should include cases that intentionally violate this
checklist, such as:

- missing Merge Decision Record;
- changed file outside allowed paths;
- runtime artifact path;
- `see chat` durable source;
- pending or missing checks;
- human gate without approval.

Those cases should be opt-in expected-failure fixtures and must not break normal
positive validation unless a validator is explicitly designed to read them as
negative fixtures.
