# V1.1 Stabilization Plan

Status: active stabilization plan.

This document defines stabilization work before ASGK enters v1.0 release
preparation. The purpose is to harden the generic governance core through small
tooling improvements, install-surface readiness, vertical decision governance,
and at least one real-world field test.

## Decision

Do not proceed directly to release preparation.

```yaml
decision:
  release_preparation_status: deferred
  reason: known v1.1 hardening work, install-surface safety, vertical decision governance, and real-world field testing should happen first
  next_phase: v1.1 stabilization
  active_milestone: Vertical Governance Completion
  controller_issue: "#88"
```

## Stabilization Goals

```yaml
v1_1_stabilization_goals:
  - harden lightweight parser behavior without adding dependencies
  - add status-check coverage for CURRENT_STATUS.md staleness and size risks
  - prove handoff-template output can become a valid checked handoff packet
  - audit status-like documents for uncontrolled growth risk
  - split document navigation into router registry and context read sets
  - define target-project install surface, checklist, checker, and read-only plan
  - add vertical governance for major decision points without policy sprawl
  - run one real-world field test before release preparation
```

## Completed Stabilization Work

```yaml
completed:
  parser_hardening_without_dependencies: true
  asgk_status_check: true
  positive_handoff_template_fixture: true
  uncontrolled_document_audit: true
  document_navigation_split: true
  target_install_checklist_and_validation_plan: true
  read_only_target_install_check: true
  read_only_target_install_plan: true
  vertical_governance_initial_layer: true
```

## Active Stabilization Work

```yaml
active_work:
  milestone: Vertical Governance Completion
  controller_issue: "#88"
  phase_state: initial_layer_completed
  completed_by: "#88 / PR #89"
  objective: "Complete vertical governance by proving the decision-point registry and reusable decision packet can guide a real decision without policy sprawl."
  next_work_unit_candidate: "Exercise one decision packet on a real decision point."
  non_goals:
    - decision-check CLI before the decision-packet exercise proves the need
    - decision schema
    - one policy document per decision type
    - installer scaffold behavior
```

## Work Items

### 1. Parser hardening without dependencies

Status: completed.

Objective:

```text
Improve `scripts/asgk.py` lightweight textual checks without introducing PyYAML or other dependencies.
```

### 2. `asgk status-check`

Status: completed.

Objective:

```text
Add a lightweight check for `docs/handoff/CURRENT_STATUS.md` so stale active work and uncontrolled growth are easier to detect.
```

### 3. Positive handoff-template fixture

Status: completed.

Objective:

```text
Prove that `handoff-template` output can be filled into a valid packet that passes `handoff-check`.
```

### 4. Uncontrolled-document audit

Status: completed.

Objective:

```text
Inspect status-like or log-like documents for CURRENT_STATUS-style growth risk.
```

### 5. Install/template usage and target-install safety

Status: completed for checklist, validation plan, read-only checker, and read-only planner. Scaffold/installer remains intentionally deferred.

Objective:

```text
Ensure target repositories can adopt ASGK through an explicit install surface and read-only planning/checking before any file-writing scaffold exists.
```

Completed outputs:

```yaml
target_install_outputs:
  - docs/INSTALL_SURFACE.md
  - docs/control/TARGET_INSTALL_CHECKLIST.md
  - docs/control/TARGET_INSTALL_VALIDATION_PLAN.md
  - python3 scripts/asgk.py target-install-check
  - python3 scripts/target_install_plan.py
```

Deferred outputs:

```yaml
deferred:
  - python3 scripts/asgk.py target-install-plan wrapper
  - target-install negative fixtures
  - opt-in CI job
  - scaffold/installer script
```

### 6. Vertical Governance Completion

Status: active milestone; initial layer completed by #88 / PR #89.

Objective:

```text
Add a thin vertical governance layer so major decision points can be resumed, reviewed, and checked consistently across projects using ASGK.
```

Initial deliverables:

```yaml
vertical_governance_initial_deliverables:
  status: completed
  completed_by: "#88 / PR #89"
  outputs:
    - docs/control/DECISION_POINT_REGISTRY.md
    - templates/decision_packet.template.yaml
    - docs/DOCUMENT_REGISTRY.md registration
    - docs/control/CONTEXT_BUDGET_POLICY.md decision_point read set
    - docs/handoff/CURRENT_STATUS.md active milestone update
```

Remaining exit criteria:

```yaml
vertical_governance_remaining_exit_criteria:
  - exercise a decision packet in one real decision point
  - confirm the registry routes to existing canonical documents without creating policy sprawl
  - explicitly defer or scope any future decision-check CLI after the exercise
  - update V1_READINESS_AUDIT.md and the field-test path after the exercise
```

Acceptance:

```yaml
acceptance:
  - decision registry remains a router/index rather than a parallel policy system
  - decision packet template captures decision type, lifecycle, durable source, canonical docs, evidence, authority, allowed/forbidden actions, stop conditions, rollback, human gate, validation, and next safe action
  - #88 / PR #89 is treated as initial-layer completion, not full milestone completion
  - no decision-check CLI, schema, dependency, or file-writing automation is introduced before a real decision-packet exercise proves the need
  - `python3 scripts/asgk.py doctor` passes
```

Classification:

```yaml
release_classification: v1_1_stabilization
v1_0_blocker: required_before_release_preparation
```

### 7. Real-world field test

Status: pending after Vertical Governance Completion initial layer.

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
  - issue closeout
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
1. Parser hardening without dependencies [completed]
2. asgk status-check [completed]
3. Positive handoff-template fixture [completed]
4. Uncontrolled-document audit [completed]
5. Document navigation split [completed]
6. Target install checklist/check/plan [completed through read-only plan]
7. Vertical Governance Completion initial layer [completed by #88 / PR #89]
8. Decision-packet exercise for one real decision point
9. Real-world field test
10. Update V1_READINESS_AUDIT.md
11. Start release checklist / licensing gate
```

## Release Preparation Gate

Release preparation may resume only when:

```yaml
release_preparation_gate:
  - parser_hardening_completed_or_explicitly_deferred
  - status_check_completed_or_explicitly_deferred
  - positive_handoff_fixture_completed_or_explicitly_deferred
  - uncontrolled_document_audit_completed_or_explicitly_deferred
  - document_navigation_split_completed
  - target_install_read_only_check_and_plan_completed
  - vertical_governance_initial_layer_completed
  - decision_packet_exercise_completed
  - vertical_governance_policy_sprawl_reviewed
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
  - installer scaffold before checker/planner and decision governance are stable
```

Those belong to release preparation or v2.0, not this stabilization plan.
