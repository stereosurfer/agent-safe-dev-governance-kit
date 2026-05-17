# Validation Strategy

Status: active control policy.

This document defines what ASGK validation is allowed to prove, what each
validation layer owns, when findings block work, and what evidence is required
when validator behavior changes.

It is not a command manual, a full negative-fixture matrix, a PR review
checklist, or a future implementation catalog.

## Purpose

```text
Policy becomes useful when it can be checked.
Validation turns governance from advice into repeatable gates.
```

This strategy exists so validators stay honest about their proof boundary. A
validator may report only the state it mechanically checked. Missing, unknown,
pending, ambiguous, or unverifiable merge gates stay blocked or human-gated.

Low-risk status is never agent-declared. A PR is low-risk eligible only when the
current issue, low-risk policy, auto-merge policy, changed-path checks, PR-body
checks, CI, and human-gate boundaries all permit it.

## Document Boundary

```yaml
this_document_owns:
  - ASGK validation proof boundary
  - validation layer responsibilities
  - blocking versus warning classification principles
  - negative-fixture ownership rules
  - fail-closed policy-gate requirements
  - validator change requirements

this_document_does_not_own:
  - complete CLI syntax
  - exhaustive command behavior
  - negative case matrix rows
  - PR review sequence
  - context read-set selection
  - project-specific test requirements
  - release or merge approval

canonical_neighbors:
  negative_case_matrix: docs/control/NEGATIVE_TEST_PLAN.md
  PR_review_sequence: docs/control/PR_REVIEW_CHECKLIST.md
  context_read_sets: docs/control/CONTEXT_BUDGET_POLICY.md
  merge_decision_record: docs/control/MERGE_DECISION_RECORD.md
  low_risk_merge_policy: docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md
  human_gates: docs/control/HUMAN_GATED_OPERATIONS.md
  current_command_interface: python3 scripts/asgk.py --help
```

## Validation Boundary

Validation evidence must not be stretched beyond the layer that produced it.

```yaml
asgk_governance_validation:
  can_prove:
    - required repository control surfaces are present
    - PR bodies and Merge Decision Records have required structure
    - changed paths stay within supplied issue or PR scope
    - protected paths and runtime artifact paths are detected when supplied
    - current-status and handoff surfaces avoid known stale states
    - known-bad governance fixtures fail as expected
    - compact reports preserve tool-derived blocking findings over prose claims
  cannot_prove:
    - generated code semantics
    - third-party API freshness
    - security correctness
    - privacy safety
    - dependency or license safety
    - production readiness
    - human approval when the approval source cannot be mechanically separated

project_specific_validation:
  owner: current GitHub issue or PR
  examples:
    - unit tests
    - integration tests
    - type checks
    - lint checks
    - app-specific smoke tests
  required_pr_evidence:
    - command
    - result
    - concrete evidence
    - coverage limits

external_specialist_validation:
  owner: project policy or human-gated issue
  examples:
    - security scanner
    - dependency audit
    - privacy or egress review
    - current upstream documentation lookup
    - legal or license review
  rule: ASGK does not provide these checks unless the adopting project adds them
```

## Validation Layers

The current CLI is the executable interface. Use `python3 scripts/asgk.py --help`
and the command-specific help output for exact syntax. This strategy groups
validators by responsibility instead of duplicating the full command catalog.

### Scaffold And Bootstrap

```yaml
owners:
  - scripts/check_project.py
  - scripts/validate_bootstrap.py
  - python3 scripts/asgk.py doctor
  - python3 scripts/asgk.py validate
proves:
  - required directory and file surfaces exist
  - bootstrap documents contain required terms and sections
  - schemas and positive examples are parseable where checked
  - PR and issue templates keep required governance fields
does_not_prove:
  - semantic correctness
  - live GitHub state
  - low-risk merge eligibility
  - external security, privacy, dependency, or license safety
blocking_rule: failures block baseline repository validation
```

### PR Body And Merge Evidence

```yaml
owners:
  - scripts/policy_gate_check.py
  - scripts/pr_governance_preflight.py
  - python3 scripts/asgk.py pr-body-check
  - python3 scripts/asgk.py policy-gate
  - python3 scripts/asgk.py compact-pr-body-check
proves:
  - required PR body sections are present
  - Merge Decision Record fields are present and mechanically coherent
  - Current Status Impact is classified
  - merge-ready claims do not conflict with checked PR-body gates
does_not_prove:
  - actual CI success unless supplied by a tool-derived report
  - human approval
  - low-risk status
  - semantic truth of prose evidence
blocking_rule: fail closed for missing, pending, unknown, or unverifiable merge gates
```

### Scope, Path, PR, And Workspace State

```yaml
owners:
  - scripts/governance_hygiene.py
  - python3 scripts/asgk.py hygiene
  - python3 scripts/asgk.py check-pr
  - python3 scripts/asgk.py work-unit-check
  - python3 scripts/asgk.py workspace-state-check
proves:
  - supplied changed paths are inside allowed paths
  - protected paths and runtime artifact paths are detected
  - live or fixture issue/PR metadata is internally usable
  - stale or merged local branches are surfaced as workspace observations
does_not_prove:
  - final merge approval
  - human-gated approval
  - security or privacy safety beyond checked path patterns
  - that warnings require automatic repair issues
blocking_rule: path and authority failures block; workspace observations warn unless strict mode or policy says otherwise
```

### Task, Context, And Target Adoption

```yaml
owners:
  - python3 scripts/asgk.py task-packet-check
  - python3 scripts/asgk.py context-budget-measure
  - python3 scripts/asgk.py target-install-check
proves:
  - task packets contain required fields and material values
  - executable task packets use GitHub issue or PR authority when GitHub is available
  - files_to_inspect_first avoids overbroad whole-repo read requests
  - context-budget estimates are derived from concrete named files
  - target-install checks report copy, template, customize, and do-not-copy boundaries
does_not_prove:
  - that a target repository has adopted ASGK correctly after manual edits
  - that a context estimate equals provider-billed tokens
  - that a task packet expands issue authority
blocking_rule: malformed authority or overbroad context requests block; target-install findings remain read-only until a target-owned issue authorizes changes
```

### Current Status, Handoff, And Release State

```yaml
owners:
  - python3 scripts/asgk.py status-check
  - python3 scripts/asgk.py closeout-check
  - python3 scripts/asgk.py current-status-impact-check
  - python3 scripts/asgk.py handoff-check
  - python3 scripts/asgk.py compact-handoff-check
  - python3 scripts/asgk.py release-state-check
proves:
  - handoff and current-status surfaces avoid known stale active-work patterns
  - current-status impact values use the allowed vocabulary
  - release-state closeout does not leave known candidate or pending residue
does_not_prove:
  - historical issue completeness
  - that old pre-rule work needs repair
  - that a release should be executed
blocking_rule: current work closeout can block; legacy observations must not become automatic repair work
```

### Compact Governance Reports

```yaml
owners:
  - python3 scripts/asgk.py compact-issue-scope
  - python3 scripts/asgk.py compact-scope-lock
  - python3 scripts/asgk.py compact-pr-report
  - python3 scripts/asgk.py compact-task-packet-check
  - python3 scripts/asgk.py compact-target-upgrade-check
proves:
  - issue scope can be normalized into a canonical object
  - scope locks detect material scope drift
  - task packets narrow rather than expand issue scope
  - PR reports preserve tool-derived state and blocking findings
  - target-upgrade manifests do not overwrite target-owned state by default
does_not_prove:
  - low-risk eligibility by itself
  - adoption safety in a target repository without target-owned review
  - human approval for restricted boundaries
blocking_rule: unavailable metadata or prose/tool conflicts fail closed
```

### Negative Validation

```yaml
owner:
  - python3 scripts/asgk.py negative
  - scripts/asgk_lib/negative.py
matrix_owner: docs/control/NEGATIVE_TEST_PLAN.md
proves:
  - registered known-bad fixtures fail as expected
  - expected-failure fixtures are not treated as positive examples
  - bad workflow claims stay blocked or human-gated where modeled
does_not_prove:
  - exhaustive coverage of all future agent mistakes
  - correctness of unregistered fixtures
  - project-specific security or privacy behavior
blocking_rule: expected-failure mismatches block validation work
```

### GitHub Actions

```yaml
owner: .github/workflows/bootstrap-validation.yml
proves:
  - configured repository checks run repeatably on the event that triggered CI
  - bootstrap validation and configured negative checks pass in CI
  - PR-body policy gate runs on pull_request event payloads
does_not_prove:
  - final status of the currently running workflow before it completes
  - semantic review
  - human approval
  - low-risk merge eligibility by itself
blocking_rule: failing required checks block merge eligibility
```

## Blocking Versus Warning

Use blocking for defects that make current authorization, validation, review, or
merge state unsafe. Use warning or observation for drift that is real but does
not invalidate the current work unit.

| Finding | Classification | Reason |
|---|---|---|
| Required scaffold file or directory missing | blocking | repository control surface is incomplete |
| Required term missing from canonical policy | blocking | policy may have been loosened or damaged |
| Invalid JSON in checked schema or positive example | blocking | machine-readable contract is broken |
| Required PR template or issue field missing | blocking | review or work-unit capture degraded |
| Missing Merge Decision Record | blocking | merge gate cannot be reviewed |
| Missing Current Status Impact | blocking | recovery-state impact is unclassified |
| Merge-ready PR body has pending, unknown, or false gates | blocking | merge eligibility is not mechanically supported |
| PR body relies on chat-only authority | blocking | chat is not durable source of truth |
| Changed path outside allowed paths | blocking or split_required | work exceeds durable scope |
| Protected path or runtime artifact path appears in changed paths | blocking or human_gated | safety boundary touched |
| Human-gated operation lacks durable approval | human_gated | approval cannot be inferred |
| Negative fixture unexpectedly passes | blocking | known-bad path is not stopped |
| Negative fixture crashes for an unrelated reason | blocking for validation work | expected-failure evidence is untrustworthy |
| Current issue closeout lacks required post-rule review evidence | blocking for current closeout | current closeout contract incomplete |
| Pre-rule issue lacks newer closeout evidence | legacy_observation | old work is not retroactively missing work |
| Workspace remains on a merged local branch | warning | local hygiene issue, not merge evidence |
| Summary document is stale against canonical policy | warning unless acceptance depends on it | requires targeted docs issue |
| Optional document missing | warning | not part of required scaffold |

## Negative Fixture Rules

Negative fixtures are safety tests, not examples for adoption.

```yaml
negative_fixture_rule:
  canonical_matrix: docs/control/NEGATIVE_TEST_PLAN.md
  executable_registry: scripts/asgk_lib/negative.py
  allowed_locations:
    - examples/negative/
    - tests/fixtures/negative/
  must_be_opt_in: true
  must_record_expected_failure: true
  must_not_be_loaded_by_positive_validation_as_valid_example: true
  must_name_owner_or_validator: true
```

Do not add malformed files into normal schema, template, or positive example
paths unless the relevant validator explicitly treats them as expected failures.

Do not duplicate the full negative case matrix here. This document owns the
fixture rules and proof boundary; `docs/control/NEGATIVE_TEST_PLAN.md` owns the
case IDs, expected outcomes, and implementation status.

## Command Documentation Rule

The executable command surface belongs to the CLI and scripts.

```yaml
command_documentation_rule:
  exact_syntax: python3 scripts/asgk.py --help
  command_specific_syntax: python3 scripts/asgk.py <command> --help
  strategy_document_may_describe:
    - responsibility groups
    - proof boundaries
    - blocking semantics
    - required evidence for behavior changes
  strategy_document_must_not_become:
    - full command reference
    - future CLI roadmap
    - duplicated implementation comments
```

If command help and this strategy disagree on exact syntax, command help is the
current executable interface and this strategy should be repaired in a scoped
documentation issue.

## Validation Expansion Rules

Validation may expand only when the current durable issue or PR authorizes it.

```yaml
validation_expansion_allowed_when:
  - current issue authorizes script or workflow changes
  - negative test plan identifies a gap
  - CI failure reveals missing required coverage
  - document map or registry identifies canonical ownership drift
  - human or reviewer asks for stricter validation

validation_expansion_must_not:
  - add new dependencies without explicit approval
  - make low-risk status agent-declared
  - turn observations into automatic repair work
  - make target repositories overwrite target-owned state
  - loosen an existing gate without explicit human approval
```

## Validator Change Requirements

Any PR changing validation behavior must include explicit evidence.

```yaml
validator_change_record:
  script_changed:
  behavior_added:
  behavior_removed:
  blocking_or_warning:
  positive_cases:
  negative_cases:
  rollback_plan:
```

For validation-script changes, the PR should include fixture, unit, or command
evidence that proves the new behavior. A docs-only clarification must say when
validator behavior is unchanged.

Loosening validation requires explicit human approval in the current durable
issue or PR. Silent loosening is blocking or human-gated.

## Relationship To Context Budget

Validation should reduce token use. Agents should prefer compact validator
output over rereading unrelated files.

```text
run validator -> read compact failure output -> inspect only files named by failure
```

Validators should not force `docs/control/**`, `examples/**`, or historical
documents into the default startup read set. A validator may point to a specific
file only when the failure or current work unit needs it.

## Current Known Gap

```yaml
known_gaps:
  - PR status validation is not wired into default CI because a running workflow cannot certify its own final status
```

Known gaps are not blockers for unrelated docs-only governance work. They should
become separate issues before tool implementation.
