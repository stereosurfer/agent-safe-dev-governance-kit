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

ASGK separates three proof layers:

```yaml
proof_layers:
  body_coherence: PR body is complete and internally coherent with its declared decision
  merge_decision: merge_allowed is mechanically supported by the body fields
  check_pr: live PR state, current checks, issue scope, paths, body decision, and hygiene are composed
```

Passing one layer does not imply the next. None of these layers independently
proves low-risk status, human approval, or permission to merge.

## Document Boundary

```yaml
this_document_owns:
  - ASGK validation proof boundary
  - validation layer responsibilities
  - blocking versus warning classification principles
  - negative-fixture ownership rules
  - fail-closed policy-gate requirements
  - validator change requirements
  - body-coherence, merge-decision, and check-pr proof boundaries

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

## Common JSON Validation Envelope

Every retained core command that accepts `--json` emits one common evidence
envelope. Command-specific fields remain beside the envelope; they do not gain
authority from it.

```yaml
result: pass | fail | blocked | warning
evidence_source: <material evidence source>
mechanically_checked:
  - <what this invocation actually checked>
not_checked:
  - <material limit or unchecked claim>
human_gate:
  status: not_checked | not_applicable | required
  reason: <material explanation>
proof_boundary: <exact claim limit>
findings:
  - code: <STABLE_UPPER_SNAKE_CASE>
    field: <exact field> # or path, exactly one
    reason: <cause>
    blocking: true | false
```

The contract, schema, and dependency-free helper are:

```yaml
contract: contracts/validation_result.contract.yaml
schema: schemas/validation_result.schema.json
helper: scripts/asgk_lib/validation_result.py
```

The result vocabulary is evidence state, not work or merge authority:

- `pass` has no findings.
- `warning` has one or more nonblocking findings and no blocking finding.
- `fail` has a blocking finding for a mechanically observed invalid state or
  malformed caller-supplied input.
- `blocked` has a blocking finding because a required check could not be
  completed or a human gate is required.

`human_gate.status` never reports approval as passed. `required` is valid only
with `result: blocked`. Domain outcomes such as `fail_closed` and
`requires_human` remain in command-specific fields such as `domain_result`,
`derived_state`, or `routing`; they do not replace the common result vocabulary.
Human-gate state is derived independently from ordinary mechanical findings. If
one result has both a mechanical failure and a restricted boundary, the common
result remains `blocked`, the gate remains `required`, both finding causes remain
visible, and the command-specific `domain_result` may remain `fail`.

`mechanically_checked`, `not_checked`, and `proof_boundary` describe the branch
that actually ran. An unreadable file, unavailable metadata marker, missing
`gh`/`git` executable, or failed lookup must not inherit the successful branch's
checked claims.

Exit status is registered per scenario. It must not be inferred from the result
token alone: for example, workspace warnings exit `0` by default and `1` under
`--strict`.

Each finding code is selected at the owning cause. Codes must not be generated
from prose, field names, or exit status. A finding names exactly one `field` or
`path`, and scenario checks compare the full code multiset so duplicate findings
cannot disappear.

The retained JSON surface is policy-gate, PR status, work unit, task packet,
handoff, compact handoff, compact issue scope, compact scope lock, compact PR
report, compact PR body, context budget, workspace state, and source validation.
Legacy
`target-install-*`, `compact-target-upgrade-check`, and the parallel compact
red-team runner are not W3C envelope authority; their replacement or removal is
separately scoped under ASGK 2.0.

## Validation Layers

The current CLI is the executable interface. Use `python3 scripts/asgk.py --help`
and the command-specific help output for exact syntax. This strategy groups
validators by responsibility instead of duplicating the full command catalog.

### Source Reference-Superset Validation

```yaml
owner: scripts/asgk_lib/source_validation.py
public_entrypoints:
  - python3 scripts/asgk.py validate
  - python3 scripts/asgk.py doctor
compatibility_projection: scripts/validate_bootstrap.py
proves:
  - the retained ASGK source-reference paths exist in live mode
  - current encoded source policy and W2/W3 projection checks pass
  - present schema and example JSON is parseable where checked
  - the issue, PR, handoff, validation, and scenario projections remain aligned
  - doctor executes the same registered negative and exact scenarios used by CI
  - a caller-supplied source inventory has the supported shape and includes the retained required paths
does_not_prove:
  - that a supplied-inventory path exists or that its contents were inspected
  - unencoded semantic correctness
  - target fit, target layout, governance depth, or adoption readiness
  - live GitHub state
  - human approval, PR readiness, or merge authority
  - external security, privacy, dependency, or license safety
blocking_rule: failures block baseline repository validation
```

`scripts/validate_bootstrap.py` is a thin compatibility delegate and owns no
required list, policy rule, fixture expectation, or parallel implementation.
`doctor` reaches the same engine through `asgk validate`; it no longer invokes
the directory-existence-only `scripts/check_project.py`. That file remains
present only for its separately authorized W6D removal.

`asgk validate --source-inventory-file <path> --json` is a source-only
fixture/capture mode. It checks caller-supplied path membership without reading
the listed paths. It is not a target checker, install manifest, adoption plan,
or evidence that a target should resemble this repository.

Live `--repo-root` mode names both `inspected_source_root` and the
`validator_reference_root` that owns the required set. Encoded live checks may
execute Python commands from the inspected root, including its scenario
registry and runner. Use this mode only for a trusted ASGK source tree; it is not
an arbitrary-target or untrusted-code inspection interface.

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
  - a blocked body is internally consistent about unresolved gates
  - a merge_allowed claim does not conflict with checked PR-body gates
does_not_prove:
  - actual CI success unless supplied by a tool-derived report
  - human approval
  - low-risk status
  - semantic truth of prose evidence
blocking_rule: fail closed for missing, blank, unknown, unsupported, or decision-incoherent states
```

Governance structure is parsed from visible Markdown. HTML comments cannot
supply headings or fields. A heading inside a fenced block is not a section
heading, while visible YAML fields inside the intended fenced record remain
machine-checkable. Exact decision tokens are unquoted; quoted `"true"` is not
the boolean `true`.

Work-unit and source-issue task fields additionally require one unambiguous
representation: unique visible recognized ATX or Setext task-field headings,
including GitHub issue-form H3 headings, or one exact ATX H2
`## Required Task Fields` section with raw YAML or one sole unlabeled, `yaml`,
or `yml` fence. Exact includes label spelling, spacing, punctuation, and case.
A Setext underline is syntax, not field content. A lower-level heading inside
an individual field remains part of that field until the next heading at the
same or a higher level. Duplicate headings or keys, a noncanonical
`Required Task Fields` heading, multiple canonical sections or fences, and
mixed representations fail before field completeness or containment is
evaluated. Fenced examples outside the canonical section do not supply
authority.

For GitHub PR events, the durable `merge_decision.result` selects the
body-level validation mode. File-backed preflight explicitly selects
`body-coherence`; direct CLI and `check-pr` explicitly select strict
`merge-decision`. Event callers must not override result-based routing, and
routing must not depend on draft status alone.

```yaml
body_validation_modes:
  body-coherence:
    selected_when:
      - file-backed create/edit preflight explicitly invokes it
      - a GitHub event body declares merge_blocked
    merge_blocked_values:
      checks_passed: [true, pending, false]
      human_gates_checked: [true, pending, false]
    merge_allowed_requirement:
      checks_passed: true
      human_gates_checked: true
    always_exact_true:
      - allowed_paths_checked
      - expected_output_checked
      - validation_evidence_checked
    fails_on:
      - blank required state
      - missing required state
      - unknown required state
      - unsupported required state
    proof_limit: body submission is coherent; no merge eligibility, low-risk status, or human approval is inferred

  merge-decision:
    direct_cli_default: true
    selected_when:
      - a GitHub event body declares merge_allowed
      - check-pr validates the body
    requires:
      - result is merge_allowed
      - checks_passed, allowed_paths_checked, expected_output_checked, human_gates_checked, and validation_evidence_checked are exactly true
      - attribution and boundary fields are complete and concrete
    proof_limit: Merge Decision Record is mechanically clear; full live PR eligibility is not proved

  invalid_or_missing_result:
    outcome: fail_closed
```

### Scope, Path, PR, And Workspace State

```yaml
owners:
  - python3 scripts/asgk.py work-unit-check --authority-only
  - scripts/governance_hygiene.py
  - python3 scripts/asgk.py hygiene
  - python3 scripts/asgk.py check-pr
  - python3 scripts/asgk.py work-unit-check
  - python3 scripts/asgk.py workspace-state-check
proves:
  - authority-only mode checks an open work unit, one visible unambiguous field representation, exact 13 fields, reason naming, allowed paths, and both execution gates before a diff exists
  - supplied changed paths are inside allowed paths
  - protected paths and runtime artifact paths are detected
  - live or fixture issue/PR metadata is internally usable
  - check-pr rejects drafts and every merge_blocked result
  - repeated check identities use the latest reliably ordered run for the current head
  - repeated CheckRun identity includes name plus workflow/app/provider; missing provider identity fails closed
  - duplicate runs use one common startedAt or createdAt field instead of comparing different timestamp meanings
  - isDraft, reviewDecision, file-list shape, and check identity/provider types are positively validated
  - fixture or captured metadata is labeled separately from live GitHub evidence
  - stale or merged local branches are surfaced as workspace observations
does_not_prove:
  - that authority-only mode checked any changed path or implementation
  - final merge approval
  - human-gated approval
  - security or privacy safety beyond checked path patterns
  - that warnings require automatic repair issues
blocking_rule: ambiguous task fields, path, authority, strict Merge Decision, live PR state, latest-check failure or pending, and ambiguous check ordering block; workspace observations warn unless strict mode or policy says otherwise
```

### Task, Context, And Legacy Target Diagnostics

```yaml
owners:
  - python3 scripts/asgk.py task-packet-check
  - python3 scripts/asgk.py context-budget-measure
proves:
  - task packets use exactly one supported projection mode with material values
  - raw YAML task packets reject duplicate or quoted top-level keys and retain implicit null, boolean, and numeric scalar types for schema-parity checks
  - file-backed YAML rejects raw-plus-wrapper, nested, competing, or wrapper-plus-unrelated task-packet sources; file-backed JSON rejects competing top-level wrappers or wrapper-plus-unrelated fields
  - fixture bundles reject bad_input or top-level raw packet fields competing with task_packet and emit no packet authority projection
  - source issues use one visible unambiguous task-field representation before refinement comparison
  - a source issue cannot use intelligence_level_reason as an additional or substitute canonical field
  - issue_refinement packets do not mechanically expand supplied issue paths or exact read/validation items
  - github_unavailable_fallback packets carry the 13 canonical fields, both execution gates, and exact pending_unavailable status
  - packet list items match the schema's non-empty string type
  - packet paths reject absolute paths, dot segments, and resolved root escape
  - context_read_set accepts only whole-item durable references or existing in-root regular files and rejects appended broad-read clauses
  - fallback allowed_paths reject mechanically recognizable protected governance boundaries
  - context-budget estimates are derived from concrete named files
does_not_prove:
  - that a context estimate equals provider-billed tokens
  - semantic equivalence of context or validation items
  - general glob-set containment beyond exact packet/issue glob equality
  - that GitHub was actually unavailable
  - every non-path escalation trigger or the semantic sufficiency of project-specific validation
  - PR readiness, human approval, merge authority, or issue completion
blocking_rule: task-field ambiguity, unsupported packet modes, legacy fields, scope/read/validation expansion, malformed authority, invalid context references, or recognized fallback escalation paths block
```

Material `not_applicable` reasons are Unicode-aware; punctuation and connector
words alone fail, while concrete non-English reasons remain valid.

The still-present target-install commands are legacy fixed-shape diagnostics.
They are not target fit, adoption, architecture, governance-depth, approval, or
W3C retained-JSON evidence. W4 owns their clean replacement and removal.

Ambiguity maps to stable findings:

- `WU_TASK_FIELD_AMBIGUOUS`: work-unit body;
- `TP_ISSUE_TASK_FIELD_AMBIGUOUS`: source issue body;
- `TP_TASK_FIELD_AMBIGUOUS`: raw task-packet YAML or competing packet source.

After a task-field ambiguity finding, completeness, gate semantics, and downstream
containment or non-expansion checks that depend on the ambiguous fields are
reported as not checked.

A legacy reason alias in a source issue maps to
`TP_ISSUE_REASON_ALIAS_FORBIDDEN`; source parsing remains observable, but
dependent non-expansion comparisons are reported as not checked.

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
  - python3 scripts/asgk.py task-packet-check
proves:
  - the 13-field task identity can be normalized into a canonical object
  - scope locks detect drift in that 13-field identity
  - compact-task-packet-check delegates to the canonical task-packet evaluator rather than owning comparison semantics
  - PR reports preserve tool-derived state and blocking findings
does_not_prove:
  - freshness or validity of context_read_set and project_specific_validation; work-unit-check owns those execution gates
  - low-risk eligibility by itself
  - adoption safety in a target repository without target-owned review
  - human approval for restricted boundaries
blocking_rule: unavailable metadata or prose/tool conflicts fail closed
```

`compact-target-upgrade-check` and
`scripts/compact_governance_red_team_check.py` remain in the source tree only
until their separately scoped cutover or deletion work. The red-team script is
not part of `doctor`, `negative all`, or source-validation orchestration. Neither
surface is a second compact-governance oracle or owns retained JSON
expectations.

### Negative Validation

```yaml
owners:
  scenario_expectations: scripts/asgk_lib/scenario_registry.py
  exact_execution: scripts/asgk_lib/scenario_runner.py
projections:
  public_facade: scripts/asgk_lib/negative.py
  cli: python3 scripts/asgk.py negative
  doctor: python3 scripts/asgk.py doctor
  ci: .github/workflows/bootstrap-validation.yml
human_case_intent: docs/control/NEGATIVE_TEST_PLAN.md
proves:
  - registered commands match exact exit, result, finding-code multiset, human-gate state, and proof boundary
  - branch-specific scenarios may additionally lock exact mechanically_checked and not_checked lists
  - positive and negative retained scenarios remain paired
  - canonical and compact task-packet commands remain byte-for-byte equivalent
  - the canonical source command and bootstrap compatibility wrapper remain byte-for-byte equivalent for positive and negative inventory scenarios
  - controlled missing, malformed, unavailable, and missing-executable inputs emit exactly one JSON object
  - runner self-tests reject crashes, signals, mixed output, wrong codes, wrong proof boundaries, wrong human-gate/domain states, and wrong checked/unchecked claims
  - expected-failure fixtures are not treated as positive examples
  - bad workflow claims stay blocked or human-gated where modeled
does_not_prove:
  - exhaustive coverage of all future agent mistakes
  - correctness of unregistered fixtures
  - project-specific security or privacy behavior
blocking_rule: expected-failure mismatches block validation work
```

Compatibility modules `negative_cases.py` and `negative_runner.py` delegate to
the canonical registry and runner. They do not own expectations.

### GitHub Actions

```yaml
owner: .github/workflows/bootstrap-validation.yml
proves:
  - configured repository checks run repeatably on the event that triggered CI
  - doctor runs the canonical scenario registry in CI
  - PR-body validation mode is selected from the declared durable result
  - changed-path hygiene is evaluated against the triggering PR
does_not_prove:
  - final status of the currently running workflow before it completes
  - semantic review
  - human approval
  - low-risk merge eligibility by itself
blocking_rule: failing required checks block merge eligibility
```

PR lifecycle coverage requires these `pull_request` activity types:

```text
opened, synchronize, reopened, edited, ready_for_review, converted_to_draft
```

Event routing is:

```text
declared result: merge_blocked -> body-coherence
declared result: merge_allowed -> merge-decision
missing or invalid result       -> fail closed
```

Marking ready for review does not select strict validation and does not imply
merge eligibility.

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
| Coherent merge_blocked PR body has pending or false checks/human gates | allowed for body-coherence; merge remains blocked | body explicitly preserves unresolved state |
| PR body has blank, missing, unknown, or unsupported required state | blocking | neither body coherence nor merge decision is mechanically supported |
| merge_allowed PR body has pending or false required gates | blocking | strict Merge Decision is not mechanically supported |
| check-pr receives result merge_blocked | blocking | full live eligibility requires a strict merge_allowed decision |
| Latest reliably ordered run for a required check is failed or pending | blocking | superseded older runs cannot establish current eligibility |
| Duplicate check identity cannot be ordered reliably | blocking | current check state is ambiguous and must fail closed |
| PR body relies on chat-only authority | blocking | chat is not durable source of truth |
| Changed path outside allowed paths | blocking or split_required | work exceeds durable scope |
| Protected path or runtime artifact path appears in changed paths | blocking or human_gated | safety boundary touched |
| Human-gated operation lacks a durable current-head `decision: approved` record | human_gated | approval cannot be inferred |
| human_gates_checked is true without either the applicable approved record or a durable no-gate risk/path determination | blocking or human_gated | a boolean cannot self-certify human judgment or a no-gate conclusion |
| Negative fixture unexpectedly passes | blocking | known-bad path is not stopped |
| Negative fixture crashes for an unrelated reason | blocking for validation work | expected-failure evidence is untrustworthy |
| Current issue closeout lacks required post-rule review evidence | blocking for current closeout | current closeout contract incomplete |
| Pre-rule issue lacks newer closeout evidence | legacy_observation | old work is not retroactively missing work |
| Workspace remains on a merged local branch | warning | local hygiene issue, not merge evidence |
| Summary document is stale against canonical policy | warning unless acceptance depends on it | requires targeted docs issue |
| Optional document missing | warning | not part of required scaffold |

## Evidence Staleness And Recovery

- A validation failure or stale evidence returns the durable result to
  `merge_blocked` before more work.
- A code commit after human review makes that review stale unless the human
  reaffirms it for the new head or diff.
- Older check runs remain evidence but are superseded by the latest reliably
  timestamped run of the same identity on the same head.
- If the approach is wrong, record the abandonment reason and return the durable
  result to `merge_blocked` before closing the PR unmerged. Preserve its branch,
  commits, CI, comments, and decision record, then restart authorized work from
  current `main` on a fresh branch.
- A closed-unmerged attempt does not require reverting `main`. Reverting merged
  work requires separate authorization and must preserve history.

## Negative Fixture Rules

Negative fixtures are safety tests, not examples for adoption.

```yaml
negative_fixture_rule:
  canonical_matrix: docs/control/NEGATIVE_TEST_PLAN.md
  executable_registry: scripts/asgk_lib/scenario_registry.py
  exact_runner: scripts/asgk_lib/scenario_runner.py
  facade: scripts/asgk_lib/negative.py
  allowed_locations:
    - examples/negative/
    - tests/fixtures/negative/
  must_be_opt_in: true
  retained_json_expectations:
    - polarity
    - exact owner command
    - exact exit
    - exact common result
    - exact finding-code multiset
    - exact human-gate status
    - exact proof boundary
    - optional exact mechanically_checked list for branch-specific evidence
    - optional exact not_checked list for branch-specific evidence
  must_not_be_loaded_by_positive_validation_as_valid_example: true
  must_name_owner_or_validator: true
```

Do not add malformed files into normal schema, template, or positive example
paths unless the relevant validator explicitly treats them as expected failures.

Do not duplicate the full negative case matrix here. This document owns the
fixture rules and common proof boundary. `docs/control/NEGATIVE_TEST_PLAN.md`
owns human-readable case intent and classification. The scenario registry alone
owns executable retained-JSON expectations.

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
  positive_scenarios:
  negative_scenarios:
  expected_result:
  expected_exit:
  expected_finding_codes:
  proof_boundary:
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
