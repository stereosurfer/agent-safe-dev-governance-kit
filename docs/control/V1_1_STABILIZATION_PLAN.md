# V1.1 Stabilization Plan

Status: active stabilization plan.

This document defines the stabilization work that should happen before ASGK enters v1.0 release preparation. The purpose is to harden the generic governance core through small tooling improvements and at least one real-world field test.

## Decision

Do not proceed directly to release preparation.

```yaml
decision:
  release_preparation_status: deferred
  reason: known v1.1 hardening work and real-world field testing should happen first
  next_phase: v1.1 stabilization
```

## Stabilization Goals

```yaml
v1_1_stabilization_goals:
  - harden lightweight parser behavior without adding dependencies
  - add status-check coverage for CURRENT_STATUS.md staleness and size risks
  - prove handoff-template output can become a valid checked handoff packet
  - audit status-like documents for uncontrolled growth risk
  - run one real-world field test before release preparation
```

## Work Items

### 1. Parser hardening without dependencies

Objective:

```text
Improve `scripts/asgk.py` lightweight textual checks without introducing PyYAML or other dependencies.
```

Candidate checks:

```yaml
parser_hardening:
  - list fields are not only present but materially non-empty when required
  - validation_status.status is scoped to the validation_status block when possible
  - TODO / AI_TODO detection can be configured for final packet checks
  - field parsing avoids cross-line capture
  - command errors are clear enough for humans and AI agents
```

Acceptance:

```yaml
acceptance:
  - no new dependency
  - no full parser redesign
  - existing negative checks still pass
  - at least one new positive and one new negative parser fixture if needed
```

Classification:

```yaml
release_classification: v1_1_stabilization
v1_0_blocker: false
```

### 2. `asgk status-check`

Objective:

```text
Add a lightweight check for `docs/handoff/CURRENT_STATUS.md` so stale active work and uncontrolled growth are easier to detect.
```

Candidate checks:

```yaml
status_check_targets:
  - file exists
  - next safe action exists
  - active work block exists
  - no obvious stale issue marker from known completed work when detectable locally
  - line count below soft limit from CURRENT_STATUS_POLICY.md
  - forbidden sections such as long chronological logs are absent
```

Acceptance:

```yaml
acceptance:
  - no GitHub API dependency in first version
  - no network calls
  - no new dependency
  - command reports warning/block clearly
```

Classification:

```yaml
release_classification: v1_1_stabilization
v1_0_blocker: false
```

### 3. Positive handoff-template fixture

Objective:

```text
Prove that `handoff-template` output can be filled into a valid packet that passes `handoff-check`.
```

Candidate artifact:

```text
examples/handoff_packet.valid.yaml
```

Acceptance:

```yaml
acceptance:
  - positive handoff fixture exists
  - `python3 scripts/asgk.py handoff-check --file examples/handoff_packet.valid.yaml` passes
  - CI may run the positive check if stable
```

Classification:

```yaml
release_classification: v1_1_stabilization
v1_0_blocker: false
```

### 4. Uncontrolled-document audit

Objective:

```text
Inspect status-like or log-like documents for CURRENT_STATUS-style growth risk.
```

Initial candidates:

```yaml
candidate_docs:
  - docs/handoff/AGENT_LOG.md
  - docs/handoff/DECISIONS.md
  - docs/control/LANE_STATUS.md
  - docs/bootstrap/12_productization_notes.md
  - docs/EVOLUTION_MODEL.md
```

Acceptance:

```yaml
acceptance:
  - classify each candidate as current_snapshot, durable_decision_log, append_allowed, compact_policy_needed, or reference_only
  - add policy only where needed
  - do not rewrite large docs unless a specific issue authorizes it
```

Classification:

```yaml
release_classification: v1_1_stabilization
v1_0_blocker: false
```

### 5. Install/template usage guide, if needed before field test

Objective:

```text
Ensure the field test has enough instructions to apply ASGK to a real or semi-real repository without relying on chat memory.
```

Acceptance:

```yaml
acceptance:
  - either existing QUICKSTART is sufficient for field test
  - or add a small install/template usage guide before testing
```

Classification:

```yaml
release_classification: conditional_v1_1_stabilization
v1_0_blocker: false
```

### 6. Real-world field test

Objective:

```text
Use ASGK to manage a real non-trivial work unit outside pure documentation-only governance additions.
```

Candidate field-test types:

```yaml
field_test_candidates:
  - small script/tooling change
  - schema or contract update
  - install/use ASGK in a small separate repo
  - manage a bounded change in another active project using ASGK handoff and validation flow
```

Minimum requirements:

```yaml
field_test_minimum:
  - GitHub issue with durable source of truth
  - allowed paths
  - PR with Merge Decision Record
  - `asgk doctor` or equivalent validation
  - at least one handoff packet or handoff-template usage
  - result comment on issue
  - lessons learned recorded
```

Acceptance:

```yaml
acceptance:
  - field test completes or is blocked for a useful reason
  - blockers are converted into issues
  - V1_READINESS_AUDIT.md is updated after the test
```

Classification:

```yaml
release_classification: required_before_release_preparation
v1_0_blocker: not_a_bug_but_required_sequence_gate
```

## Suggested Order

```text
1. Parser hardening without dependencies
2. asgk status-check
3. Positive handoff-template fixture
4. Uncontrolled-document audit
5. Install/template usage guide only if field test needs it
6. Real-world field test
7. Update V1_READINESS_AUDIT.md
8. Start release checklist / licensing gate
```

## Release Preparation Gate

Release preparation may resume only when:

```yaml
release_preparation_gate:
  - parser_hardening_completed_or_explicitly_deferred
  - status_check_completed_or_explicitly_deferred
  - positive_handoff_fixture_completed_or_explicitly_deferred
  - uncontrolled_document_audit_completed_or_explicitly_deferred
  - real_world_field_test_completed
  - field_test_lessons_recorded
  - V1_READINESS_AUDIT.md updated after field test
```

## Non-goals

The stabilization phase does not include:

```yaml
non_goals:
  - runtime-specific adapters
  - vendor-specific profile testing
  - release tagging
  - license selection
  - package publishing
  - SaaS or GitHub App work
```

Those belong to release preparation or v2.0, not this stabilization plan.
