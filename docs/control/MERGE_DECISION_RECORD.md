# Merge Decision Record

Each governed PR body must include a Merge Decision Record. The record is
durable decision state, including while a PR is blocked or under review.

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
    local_doctor: freshly_rerun | recorded_in_pr_body | existing_durable_record | not_run | not_applicable
    ci: github_actions | external_ci | not_run | not_applicable
  result: merge_allowed | merge_blocked
  reason:
```

Use these state values:

```yaml
decision_state:
  checks_passed: true | pending | false
  allowed_paths_checked: true
  expected_output_checked: true
  human_gates_checked: true | pending | false
  validation_evidence_checked: true
  result: merge_allowed | merge_blocked
```

These are literal, unquoted lowercase body tokens. In particular,
`checks_passed: "true"` is a string and does not satisfy an exact-true gate.

A missing or `merge_blocked` Merge Decision Record blocks merge. A blocked
record may still be coherent enough to create a draft, run CI, request review,
or preserve a revision blocker.

A Merge Decision Record is also incomplete when structured fields replace
judgment. The `reason` field must be free text that names the relevant evidence,
limits, and any unverified items. It must not only repeat enum values such as
`passed`, `none`, `n/a`, `all good`, or `merge_allowed`.

## Validation Modes

For GitHub PR event routing, the declared durable `result` selects the
body-level mode. Draft status does not select a mode. File-backed create/edit
preflight explicitly selects `body-coherence`; direct CLI and `check-pr`
explicitly select strict `merge-decision`. Event callers must not override the
result-based mode.

```yaml
mode_routing:
  merge_blocked: body-coherence
  merge_allowed: merge-decision
  missing_or_invalid: fail_closed
```

### `body-coherence`

File-backed create/edit preflight explicitly uses `body-coherence`. It checks
that the body is complete and internally coherent with its declared result.

- `merge_blocked` may use `checks_passed` and `human_gates_checked` values
  `true`, `pending`, or `false`.
- `merge_allowed` requires those fields to be exactly `true`.
- Blank, missing, unknown, or unsupported required states fail.
- `allowed_paths_checked`, `expected_output_checked`, and
  `validation_evidence_checked` must always be exactly `true`.
- Passing this mode does not infer merge eligibility, low-risk status, human
  approval, or permission to merge.

### `merge-decision`

`merge-decision` is the direct CLI default and the strict PR-body decision
check. It requires `result: merge_allowed`; `checks_passed`,
`allowed_paths_checked`, `expected_output_checked`, `human_gates_checked`, and
`validation_evidence_checked` must be exactly `true`, while attribution and
boundary fields must be complete and concrete.

Passing this mode proves only that the Merge Decision Record is mechanically
clear. Live mergeability, review state, current check runs, issue authority,
changed paths, and hygiene belong to `check-pr`.

`check-pr` always uses strict `merge-decision` validation and independently
rejects every `result: merge_blocked`.

## Lifecycle Use

```text
draft + merge_blocked
  -> ready for review + merge_blocked
  -> applicable current-head decision: approved,
     or durable no-gate risk/path determination plus a complete program
     execution record when the protected reversible path is used
  -> exact-true gates true + concrete boundary fields complete + merge_allowed
  -> strict merge-decision
  -> live check-pr
  -> human or policy merge decision
```

If validation fails or evidence becomes stale, return the record to
`merge_blocked` before continuing. A new code commit invalidates human review
tied to an older head unless it is reaffirmed.

## Human Review Evidence

`human_gates_checked: true` is a claim, not evidence by itself. When a human
gate applies, the PR or linked issue must cite a current-head durable record
with `decision: approved`. `changes_requested` or `rejected` requires
`human_gates_checked: false` and `result: merge_blocked`. When no human gate
applies, cite the durable no-gate risk/path determination. Prior-PR review and
review of a superseded head are not transferable.

Program execution authorization is separate evidence. It may authorize an
already-bounded repo-local reversible work unit without repeated OWNER prompts,
but it does not prove `human_gates_checked: true`. That field remains supported
by an independent current-head determination that no Human-Gated Operations
item applies. When the program-scoped protected-path exception is used, cite the
OWNER-approved exact scope source, complete record defined in
`docs/control/HUMAN_GATED_OPERATIONS.md`, canonical merge policy, and a current
child issue no broader than the scope source. The program grant may persist across commits; the
scope/no-gate review, independent review, CI, and `check-pr` must be refreshed
for every head. Never describe the program grant as current-head human review.

A PR that changes the program path, human gates, merge authority, or
enforcement/non-inference semantics—including by creating, removing, loosening,
tightening, or reclassifying them—cannot use the path it changes. Apply the
stricter baseline or proposed policy and require current-head human approval.

The body checker validates structured field consistency; it does not establish
that a cited review is real, current, or sufficient. The reviewer or gatekeeper
must inspect the durable record and current head/diff. `merge_allowed` remains
neither Agent approval nor merge authority.

## Validation Evidence Source

Validation claims must say where the evidence came from. Do not collapse
different evidence sources into a generic `passed` statement.
Structured validation fields are attribution aids, not a substitute for
judgment. Reviewers should treat empty or generic evidence, limits, or reason
text as merge-blocking until clarified.

Validation claims must stay inside their evidence boundary. `doctor` and ASGK
policy checks prove governance-surface behavior, not application semantics,
security correctness, privacy safety, dependency health, or current third-party
API usage. Code-changing PRs should name the project-specific tests that cover
the changed behavior and explicitly state any coverage limits.

Use this vocabulary when practical:

```yaml
validation_evidence_source:
  freshly_rerun: "The command was run in the current work unit."
  recorded_in_pr_body: "The PR body records the result, but the current reviewer did not rerun it."
  github_actions: "The result was observed from GitHub Actions or another named CI check."
  existing_durable_record: "The result comes from a merged PR, issue comment, repo file, or other durable record."
  inferred_from_merged_pr: "The result is inferred from the fact that a merged PR recorded or required it."
  not_run: "The check was not run."
  not_applicable: "The check does not apply to this work unit."
```

If a final report says a command passed, it should distinguish:

```yaml
validation:
  local_doctor:
    status: passed | failed | not_run | not_applicable
    source: freshly_rerun | recorded_in_pr_body | existing_durable_record | not_run | not_applicable
    evidence: "Concrete command output summary, PR body reference, issue comment, or durable record."
    limits: "What this validation does not prove."
  github_actions:
    status: passed | failed | pending | not_applicable
    source: github_actions | external_ci | not_run | not_applicable
    evidence: "Named check, run URL, or reason not applicable."
    limits: "What CI does not prove."
  project_specific_tests:
    status: passed | failed | not_run | not_applicable
    source: freshly_rerun | github_actions | existing_durable_record | not_run | not_applicable
    evidence: "Named test, typecheck, smoke test, or reason not applicable."
    limits: "What changed behavior, API freshness, security, or privacy claims this does not prove."
```

Examples of invalid validation summaries:

```yaml
invalid_validation_summaries:
  - evidence: "passed"
  - limits: "none"
  - limits: "n/a"
  - reason: "all good"
  - reason: "merge_allowed"
```
