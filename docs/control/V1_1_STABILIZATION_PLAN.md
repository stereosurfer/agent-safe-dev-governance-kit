# V1.1 Stabilization Plan

Status: active stabilization plan.

This document defines stabilization work before ASGK enters v1.0 release
preparation. The purpose is to harden the generic governance core through small
tooling improvements, install-surface readiness, vertical decision governance,
and at least one real-world field test.

## Decision

Release preparation is not started by this plan. After the real-world field-test
closeout and readiness audit update, the next safe work is to create a separate
release-preparation planning issue.

```yaml
decision:
  release_preparation_status: not_started
  reason: v1_1_stabilization_sequence_is_satisfied_enough_to_plan_release_preparation_but_release_work_requires_a_separate_gated_issue
  next_phase: release_preparation_planning
  active_milestone: Release preparation planning
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
  policy_gate_negative_fixtures: true
  target_install_negative_command: true
  vertical_governance_initial_layer: true
  decision_packet_exercise: true
  vertical_governance_policy_sprawl_reviewed: true
  vertical_governance_completion: true
  real_world_field_test: true
  field_test_lessons_recorded: true
  post_field_test_readiness_audit_updated: true
```

## Active Stabilization Work

```yaml
active_work:
  milestone: Release preparation planning
  controller_issue: pending
  phase_state: pending_issue
  prerequisite_completed:
    - Vertical Governance Completion
    - Real-world field test
    - Post-field-test readiness audit update
  completed_by:
    vertical_governance_completion: "#102 / PR #103"
    real_world_field_test: "#112 / PR #113"
    field_test_readiness_audit: "#114"
  objective: "Open a separate release-preparation planning issue covering license, tag, package, final readiness review, and explicit deferrals."
  non_goals:
    - release tagging without a release-preparation issue
    - publication or packaging without approval
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

Status: completed for checklist, validation plan, read-only checker, read-only planner, opt-in target-install checker fixtures, and opt-in target-install negative command. Scaffold/installer remains intentionally deferred.

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
  - python3 scripts/asgk.py negative target-install
```

Deferred outputs:

```yaml
deferred:
  - python3 scripts/asgk.py target-install-plan wrapper
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
    result: "The next active stabilization gate became the real-world field test; release preparation remained deferred until field-test closeout."
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

### 7. Real-world field test

Status: completed.

Objective:

```text
Use ASGK to manage a real non-trivial work unit outside pure documentation-only governance additions.
```

Completed result:

```yaml
real_world_field_test_result:
  implementation:
    issue: "#112"
    pr: "#113"
    merge_commit: "1dcdbd08a20a41a903d474ff8080317eefd87185"
    issue_state: closed_completed
  work_type: real_tooling_validation_work
  command_added: python3 scripts/asgk.py negative target-install
  validation_evidence:
    - python3 scripts/asgk.py negative target-install
    - python3 scripts/asgk.py negative all
    - python3 scripts/asgk.py doctor
    - GitHub Actions validate passed for PR #113
  lessons_learned:
    - ASGK can manage a bounded non-docs-only tooling/validation change through durable issue authority, branch, PR, validation evidence, decision packet, Merge Decision Record, merge, and closeout.
    - Decision-packet-shaped evidence was useful for recording source, limits, forbidden actions, rollback, and human-gate status.
    - Opt-in negative command flow is safer before default CI wiring.
    - Field-test implementation and field-test readiness audit must be separate closeout steps.
  known_limits:
    - did not prove target installation in a real external repository
    - did not wire target-install negative fixtures into default CI
    - did not add installer scaffold or target repository writes
  follow_up_issues: none_required_for_v1_release_preparation_gate
```

Acceptance:

```yaml
acceptance:
  - field test completed
  - lessons recorded in V1_READINESS_AUDIT.md
  - no blockers requiring new issue before release-preparation planning
  - release preparation not started by the field-test implementation PR
```

Classification:

```yaml
release_classification: required_before_release_preparation
v1_0_blocker: satisfied_sequence_gate
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
9. Vertical Governance Completion closeout [completed by #102 / PR #103]
10. Real-world field test [completed by #112 / PR #113]
11. Update V1_READINESS_AUDIT.md after field test [completed by #114]
12. Start release-preparation planning issue [next]
```

## Release Preparation Gate

Release preparation may be planned only through a separate release-preparation issue. This stabilization plan does not itself tag, publish, package, choose a license, or start release work.

```yaml
release_preparation_gate:
  status: ready_to_open_release_preparation_planning_issue
  satisfied:
    - parser_hardening_completed_or_sufficient_for_v1_core
    - status_check_completed
    - positive_handoff_fixture_completed
    - uncontrolled_document_audit_completed
    - document_navigation_split_completed
    - target_install_read_only_check_and_plan_completed
    - vertical_governance_initial_layer_completed
    - decision_packet_exercise_completed
    - vertical_governance_policy_sprawl_reviewed
    - real_world_field_test_completed
    - field_test_lessons_recorded
    - V1_READINESS_AUDIT.md updated after field test
  next_required_issue:
    title: "[RELEASE] Plan v1.0 release preparation"
    must_cover:
      - final readiness review
      - license selection
      - tag/release process
      - package or distribution boundary
      - explicit v2.0 deferrals
      - remaining human gates
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
