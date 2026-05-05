# Validation Strategy

Status: active control policy.

This document defines validation layers, validator responsibilities, negative
validation targets, blocking behavior, and future CLI mapping for this repository.
It exists to keep validation behavior explicit before more scripts, fixtures, or
CLI commands are added.

## Core Principle

```text
Policy becomes useful when it can be checked.
Validation turns governance from advice into a repeatable gate.
```

This strategy does not modify validator behavior by itself. It defines what each
current and future validator is expected to own.

Low-risk status is never agent-declared. A PR is only low-risk eligible when
existing low-risk and auto-merge policy gates pass. Validators may confirm only
mechanically checkable gates. Missing, unknown, pending, ambiguous, or
unverifiable gates keep the PR human-gated.

## Validation Layers

```yaml
validation_layers:
  scaffold_validation:
    script: scripts/check_project.py
    current_status: implemented
    purpose: required repository directory scaffold exists

  bootstrap_validation:
    script: scripts/validate_bootstrap.py
    current_status: implemented
    purpose: required files, required terms, JSON validity, task packet fields, PR headings, issue template fields, storage profile invariants

  path_hygiene:
    script: scripts/governance_hygiene.py
    current_status: implemented_with_pull_request_git_diff_ci
    purpose: changed-path and protected-path checks from files or git diff ranges

  policy_gate_check:
    script: scripts/policy_gate_check.py
    current_status: implemented_in_default_pull_request_ci
    purpose: read-only fail-closed PR-body policy gate check without low-risk inference

  work_unit_check:
    command: python3 scripts/asgk.py work-unit-check --issue <number> --git-base origin/main --git-head WORKTREE
    current_status: implemented_live_and_fixture_modes
    purpose: fail closed when the selected issue/PR is stale, wrong-type, missing allowed_paths, or local changed paths exceed allowed_paths

  task_packet_schema_check:
    command: python3 scripts/asgk.py task-packet-check --file <task_packet>
    current_status: implemented_dependency_free_json_and_canonical_yaml_shape
    purpose: validate canonical task-packet required fields, scalar/list shape, material values, intelligence level, and chat-only authority

  github_actions:
    workflow: .github/workflows/bootstrap-validation.yml
    current_status: implemented
    purpose: run repository validation on push and pull request; run PR-body policy gate on pull_request events

  negative_validation:
    current_status: implemented_with_policy_gate_fixtures_in_default_ci
    purpose: prove that known-bad inputs are blocked

  cli_wrapper:
    current_status: implemented_policy_gate_pr_status_and_task_packet_schema_wrappers
    purpose: expose validation through stable local commands
```

## `scripts/check_project.py`

### Owns

```yaml
owns:
  - required directory presence
  - minimum scaffold shape
  - dependency-light local execution
```

### Does Not Own

```yaml
does_not_own:
  - policy terms
  - JSON validity
  - PR template contents
  - path hygiene
  - semantic consistency
  - GitHub API checks
```

### Blocking Behavior

Failure blocks bootstrap validation and PR merge.

### Expected Use

```bash
python3 scripts/check_project.py
```

## `scripts/validate_bootstrap.py`

### Owns

```yaml
owns:
  - required file presence
  - required policy terms
  - JSON parse validity for schemas and examples
  - YAML-like required fields in task packets
  - PR template required headings
  - issue template required fields
  - control document required sections
  - storage profile invariants in examples
```

### Does Not Own

```yaml
does_not_own:
  - full JSON Schema validation
  - full YAML parsing
  - GitHub PR status checks
  - live issue or PR API checks
  - runtime artifact discovery from git diff
  - security review
  - human approval decisions
```

### Blocking Behavior

Failure blocks bootstrap validation and PR merge.

### Expected Use

```bash
python3 scripts/validate_bootstrap.py
```

## `scripts/governance_hygiene.py`

### Owns

```yaml
owns:
  - changed-path inspection from a paths file
  - changed-path inspection from a local git diff base/head range
  - protected-path detection
  - runtime artifact path detection
  - private/binary source-like file detection outside fixture/example paths
```

### Does Not Own

```yaml
does_not_own:
  - GitHub PR diff retrieval
  - PR body validation
  - semantic policy review
  - human-gated operation detection beyond path patterns
```

### Current Limitation

The script can derive paths from local `git diff --name-only`, but it does not
call the GitHub API. CI must provide a checked-out repository with enough
history for the requested diff range.

### Blocking Behavior

When run for a PR or local changed-path list, failures should block low-risk
autonomous merge.

### Expected Use

```bash
python3 scripts/governance_hygiene.py --paths-file changed-paths.txt
python3 scripts/governance_hygiene.py --git-base origin/main --git-head HEAD
python3 scripts/asgk.py hygiene --git-base origin/main --git-head HEAD
```

## `scripts/policy_gate_check.py`

### Owns

```yaml
owns:
  - PR-body Merge Decision Record presence
  - required Merge Decision Record fields are present and non-empty
  - checks_passed is exactly true when merge eligibility is claimed
  - allowed_paths_checked is exactly true when merge eligibility is claimed
  - expected_output_checked is exactly true when merge eligibility is claimed
  - human_gates_checked is exactly true when merge eligibility is claimed
  - result is merge_allowed or merge_blocked
  - Current Status Impact section exists and uses updated not_applicable or deferred
  - chat-only authority phrase detection
```

### Does Not Own

```yaml
does_not_own:
  - inferring low-risk status
  - deciding whether a PR may be auto-merged
  - GitHub API or live CI status retrieval
  - changed-path retrieval
  - human approval decisions
  - semantic review of whether prose risk claims are correct
```

### Blocking Behavior

The checker is fail-closed for merge eligibility. Missing, unknown, pending,
ambiguous, or unverifiable PR-body gates block merge eligibility and require
human review.

It does not certify low risk. It only reports whether declared PR-body policy
gates are mechanically coherent.

### Expected Use

```bash
python3 scripts/policy_gate_check.py --pr-body pr_body.md
python3 scripts/policy_gate_check.py --pr-body pr_body.md --json
python3 scripts/asgk.py policy-gate --pr-body pr_body.md
python3 scripts/asgk.py policy-gate --github-event "$GITHUB_EVENT_PATH"
```

## GitHub Actions

### Owns

```yaml
owns:
  - repeatable CI execution of scaffold validation
  - repeatable CI execution of bootstrap validation
  - whitespace/diff check
  - pull_request changed-path hygiene from git diff
  - pull_request PR-body policy gate execution from the GitHub event payload
  - policy-gate negative fixture execution
```

### Does Not Own

```yaml
does_not_own:
  - PR semantic review
  - issue hygiene
  - human approval
  - low-risk merge decision by itself
  - external system checks
  - final self-certification of the currently running workflow job
```

### Blocking Behavior

A failing required workflow blocks low-risk autonomous merge.

Current workflow:

```text
.github/workflows/bootstrap-validation.yml
```

## Blocking vs Warning

Use this classification until scripts become more granular.

| Finding | Classification | Reason |
|---|---|---|
| Required file missing | blocking | scaffold incomplete |
| Required directory missing | blocking | scaffold incomplete |
| Required term missing from canonical policy | blocking | policy may have been simplified |
| Invalid JSON in schema/example | blocking | machine-readable contract broken |
| Missing PR template required heading | blocking | merge/review surface degraded |
| Missing issue template required field | blocking | task packet capture degraded |
| Missing Merge Decision Record in PR body | blocking | merge gate cannot be reviewed |
| Missing Current Status Impact in PR body | blocking | resume-state impact is unclassified |
| `checks_passed` not true in Merge Decision Record | blocking | validation gate not mechanically confirmed |
| `human_gates_checked` not true in Merge Decision Record | blocking | human-gate state is unresolved |
| Artifact Root equals Local State Root | blocking | storage boundary broken |
| Cache policy not `local_only` where required | blocking | storage/cache boundary broken |
| `app_managed_drive_api` enabled in v0 profile | blocking | external API gate opened |
| Protected path in changed-path list | blocking | safety boundary touched |
| Runtime artifact path in changed-path list | blocking | runtime output leakage |
| Summary doc stale against canonical doc | warning unless acceptance depends on it | requires targeted docs issue |
| Example stale against schema | blocking when example is part of validation; otherwise warning | depends on validator coverage |
| Missing optional doc | warning | not part of required scaffold |

## Negative Validation Targets

Negative tests should prove that known-bad inputs are blocked. Current policy-gate
PR-body fixtures are opt-in expected failures under `examples/negative/policy_gate/`.
They can be run without default CI wiring through:

```bash
python3 scripts/asgk.py negative policy-gate
```

Target-install fixtures are also opt-in expected failures under
`examples/negative/target_install/`. They can be run without default CI wiring
through:

```bash
python3 scripts/asgk.py negative target-install
```

```yaml
negative_validation_targets:
  see_chat_source_of_truth:
    bad_input: "durable_source_of_truth: see chat"
    expected: blocked
    owner: task_packet_schema_check
    fixture: examples/negative/task_packet.see-chat.yaml

  missing_task_packet_stop_conditions:
    bad_input: "task packet missing stop_conditions"
    expected: blocked
    owner: task_packet_schema_check
    fixture: examples/negative/task_packet.no-stop.yaml

  empty_task_packet_required_list:
    bad_input: "task packet allowed_paths exists but has no material item"
    expected: blocked
    owner: task_packet_schema_check
    fixture: examples/negative/task_packet.empty-list.yaml

  missing_merge_decision:
    bad_input: "PR body without Merge Decision section"
    expected: blocked
    owner: validate_bootstrap_or_pr_validator
    fixture: examples/negative/policy_gate/pr_body.missing-merge-decision.md

  missing_current_status_impact:
    bad_input: "PR body without Current Status Impact section"
    expected: blocked
    owner: policy_gate_check
    fixture: examples/negative/policy_gate/pr_body.missing-current-status-impact.md

  pending_or_unknown_merge_gate:
    bad_input: "checks_passed: pending or unknown"
    expected: blocked
    owner: policy_gate_check
    fixture: examples/negative/policy_gate/pr_body.checks-pending.md

  human_gate_unresolved:
    bad_input: "human_gates_checked: pending or false"
    expected: blocked
    owner: policy_gate_check
    fixture: examples/negative/policy_gate/pr_body.human-gates-pending.md

  chat_authority_in_pr_body:
    bad_input: "PR body says see chat"
    expected: blocked
    owner: policy_gate_check
    fixture: examples/negative/policy_gate/pr_body.see-chat-authority.md

  missing_target_install_required_files:
    bad_input: "target repository missing required ASGK governance files"
    expected: blocked
    owner: target_install_check
    fixture: examples/negative/target_install/missing_required_files/

  target_install_repo_local_readiness_surface:
    bad_input: "target repository includes ASGK repo-local V1 readiness audit"
    expected: blocked
    owner: target_install_check
    fixture: examples/negative/target_install/repo_local_readiness_surface/

  missing_pr_required_heading:
    bad_input: "PR template missing required heading"
    expected: blocked
    owner: validate_bootstrap

  runtime_artifact_path:
    bad_input: "runs/test-output.json"
    expected: blocked
    owner: governance_hygiene

  protected_path:
    bad_input: ".env"
    expected: blocked
    owner: governance_hygiene

  private_binary_source_file:
    bad_input: "source.pdf outside tests/fixtures or examples"
    expected: blocked
    owner: governance_hygiene

  invalid_json_schema:
    bad_input: "malformed JSON under schemas/"
    expected: blocked
    owner: validate_bootstrap

  storage_roots_equal:
    bad_input: "artifact_root == local_state_root"
    expected: blocked
    owner: validate_bootstrap

  drive_api_enabled_by_default:
    bad_input: "sync_policy.app_managed_drive_api: true"
    expected: blocked
    owner: validate_bootstrap

  external_call_gate_without_approval:
    bad_input: "policy or fixture enabling live API/cloud/MCP without human gate"
    expected: blocked_or_human_gated
    owner: future_validator_or_human_gate_review
```

## Negative Fixture Rules

Negative fixtures must not break normal CI unless the validator is designed to
read them as expected failures.

Required pattern:

```yaml
negative_fixture_rule:
  location: examples/negative/ or tests/fixtures/negative/
  must_be_opt_in: true
  must_record_expected_failure: true
  must_not_be_loaded_by_positive_validation_as_valid_example: true
```

Do not add malformed files into normal schema/example paths unless
`validate_bootstrap.py` is updated to treat them as expected-failure fixtures.

## Future Validation Commands

The future CLI should wrap existing scripts without changing their meaning.

```yaml
future_cli_mapping:
  asgk doctor:
    runs:
      - python3 scripts/check_project.py
      - python3 scripts/validate_bootstrap.py

  asgk validate:
    runs:
      - python3 scripts/validate_bootstrap.py

  asgk hygiene --paths changed-paths.txt:
    runs:
      - python3 scripts/governance_hygiene.py --paths-file changed-paths.txt

  asgk hygiene --git-base <base> --git-head <head>:
    current_behavior:
      - run scripts/governance_hygiene.py with local git diff path collection
      - block protected paths, runtime artifacts, and private/binary source-like files
      - never call the GitHub API

  asgk policy-gate --pr-body pr_body.md:
    current_behavior:
      - run scripts/policy_gate_check.py --pr-body pr_body.md
      - report whether declared PR-body gates are mechanically coherent
      - never infer low-risk status from prose

  asgk policy-gate --github-event "$GITHUB_EVENT_PATH":
    current_behavior:
      - read pull_request.body from the GitHub Actions event payload
      - run scripts/policy_gate_check.py on that PR body
      - skip non-pull_request event payloads without failing push builds
      - never call the GitHub API
      - never infer low-risk status from prose

  asgk negative policy-gate:
    runs:
      - python3 scripts/policy_gate_check.py --pr-body examples/negative/policy_gate/pr_body.missing-merge-decision.md
      - python3 scripts/policy_gate_check.py --pr-body examples/negative/policy_gate/pr_body.missing-current-status-impact.md
      - python3 scripts/policy_gate_check.py --pr-body examples/negative/policy_gate/pr_body.checks-pending.md
      - python3 scripts/policy_gate_check.py --pr-body examples/negative/policy_gate/pr_body.human-gates-pending.md
      - python3 scripts/policy_gate_check.py --pr-body examples/negative/policy_gate/pr_body.see-chat-authority.md
    expected: all commands fail
    default_ci: true

  asgk check-pr <number>:
    current_behavior:
      - fetch PR metadata through gh pr view
      - check draft state, merge state, review decision, and status check rollup
      - run PR-body policy gate on the fetched body
      - require the Merge Decision issue to appear in GitHub closing issue references
      - run governance hygiene on fetched changed file paths
      - report checkable gates and unresolved human-review gates
      - never infer low-risk status

  asgk check-pr --json-file pr_status.json:
    current_behavior:
      - run the same PR-status validator from a captured or fixture JSON payload
      - support deterministic positive and negative tests without network access
      - fail closed when fixture metadata contains only non-closing issue references

  asgk work-unit-check --issue <number> --git-base <base> --git-head <head>:
    current_behavior:
      - fetch the issue through GitHub REST using gh api
      - fail if the issue is closed or is actually a pull request
      - parse allowed_paths from the issue body task fields
      - compare local git diff changed paths against allowed_paths
      - support WORKTREE as a git head alias for uncommitted and untracked local files
      - run changed-path hygiene on the same changed paths
      - never infer low-risk status

  asgk work-unit-check --pr <number> --paths-file changed-paths.txt:
    current_behavior:
      - fetch the pull request through GitHub REST using gh api
      - fail if the PR is closed or already merged
      - parse allowed_paths from the PR body when PR follow-up work is the active work unit
      - compare the supplied changed-path list against allowed_paths
      - never treat a merged PR as authority for new writes

  asgk work-unit-check --json-file work_unit.json --paths-file changed-paths.txt:
    current_behavior:
      - run the same work-unit validator from fixture or captured JSON
      - support deterministic positive and negative tests without network access
      - fail closed for merged PR fixtures and outside-allowed-path fixtures

  asgk task-packet-check --file task_packet.yaml:
    current_behavior:
      - validate JSON task packets, canonical YAML-like task packets, and negative fixtures with bad_input
      - require every field from docs/control/TASK_PACKET_FORMAT.md
      - require scalar/list shape and material list items
      - block see chat authority
      - validate known intelligence level values
      - avoid external YAML dependencies
```

CLI work must not add new dependencies in its first version unless a separate
issue explicitly authorizes them.

## Validation Expansion Rules

Validation may be expanded only when:

```yaml
validation_expansion_allowed_when:
  - current issue authorizes script or workflow changes
  - negative test plan identifies a gap
  - CI failure reveals missing required coverage
  - document map identifies a canonical ownership mismatch
  - human or reviewer asks for stricter validation
```

Validation must not be loosened without explicit human approval.

## Validator Change Requirements

Any PR changing validation behavior must include:

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

For validation-script changes, the PR should include examples or test evidence
that prove the new behavior.

## Relationship To Context Budget

Validation output should reduce token usage. Agents should prefer validator
reports over manually rereading unrelated files.

Expected pattern:

```text
run validator -> read compact failure output -> inspect only files named by failure
```

## Current Known Gaps

```yaml
known_gaps:
  - PR status validator is not wired into default CI because a running workflow cannot certify its own final status
```

These gaps are not blockers for docs-only governance work. They should become
separate issues before tool implementation.
