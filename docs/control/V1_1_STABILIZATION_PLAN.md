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
  active_milestone: Real-world field test
  controller_issue: pending
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
  decision_packet_exercise: true
  vertical_governance_policy_sprawl_reviewed: true
  vertical_governance_completion: true
```

## Active Stabilization Work

```yaml
active_work:
  milestone: Real-world field test
  controller_issue: pending
  phase_state: pending_issue
  prerequisite_completed: Vertical Governance Completion
  completed_by: "#102"
  objective: "Use ASGK to manage a real non-trivial work unit outside pure documentation-only governance additions."
  next_work_unit_candidate: "Create a field-test issue with durable source, allowed paths, PR/MDR, validation, handoff usage, closeout, and lessons learned."
  non_goals:
    - release preparation
    - publication or tagging
    - runtime-specific adapter work
    - installer scaffold behavior unless explicitly scoped
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

Status: completed.

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

Completed exit criteria:

```yaml
vertical_governance_completed_exit_criteria:
  decision_packet_exercise:
    status: completed
    durable_source:
      issue: "#100"
      pr: "#101"
    decision_type: low_risk_auto_merge_decision
    result: "A real docs-only milestone-phase PR used issue authority, allowed paths, GitHub Actions, PR Merge Decision Record, and low-risk merge gates."
  policy_sprawl_review:
    status: completed
    result: "The layer remains a router/index. No per-decision policy files, decision-check CLI, schema, workflow, script, dependency, runtime adapter, or installer scaffold was added."
  future_tooling_scope:
    status: deferred
    result: "Decision-check tooling should be opened only by a later issue after field-test evidence proves it is needed."
  readiness_and_field_test_path:
    status: completed
    result: "The next active stabilization gate is the real-world field test; release preparation remains deferred."
```

Control-line coverage:

```yaml
vertical_control_lines:
  decision_control: "completed as a thin decision-point registry and reusable packet template"
  evidence_control: "covered by packet evidence fields and decision-point required-evidence rows; not promoted to a standalone evidence policy"
  authority_control: "covered by registry authority order and packet authority fields"
  lifecycle_control: "covered by lifecycle_position fields and decision-point lifecycle table"
  capability_risk_control: "covered by minimum-level, human-gate, and stop-condition routing to existing canonical docs"
  future_escalation_rule: "Promote any line to standalone policy or checker only after a later issue proves the need from field-test evidence."
```

Acceptance:

```yaml
acceptance:
  - decision registry remains a router/index rather than a parallel policy system
  - decision packet template captures decision type, lifecycle, durable source, canonical docs, evidence, authority, allowed/forbidden actions, stop conditions, rollback, human gate, validation, and next safe action
  - #88 / PR #89 is treated as initial-layer completion
  - #100 / PR #101 is treated as the real decision-packet exercise
  - no decision-check CLI, schema, dependency, or file-writing automation is introduced before field-test evidence proves the need
  - `python3 scripts/asgk.py doctor` passes
```

Classification:

```yaml
release_classification: v1_1_stabilization
v1_0_blocker: required_before_release_preparation
```

### 7. Real-world field test

Status: active next gate after Vertical Governance Completion.

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
8. Decision-packet exercise for one real decision point [completed by #100 / PR #101]
9. Vertical Governance Completion closeout [completed by #102]
10. Real-world field test [active next gate]
11. Update V1_READINESS_AUDIT.md after field test
12. Start release checklist / licensing gate
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
