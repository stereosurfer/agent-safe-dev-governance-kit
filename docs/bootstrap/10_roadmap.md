# 10 Roadmap

Status: active roadmap template and milestone register.

Use this hierarchy:

```text
Vision
  -> Milestone
  -> Epic
  -> Issue
  -> PR
  -> Commit
```

Each milestone must define:

```yaml
milestone:
  goal:
  non_goals:
  deliverables:
  acceptance:
  risks:
  rollback_plan:
  human_gates:
  phase_exit_criteria:
```

## Active Milestone

```yaml
active_milestone:
  name: Real-world field test
  controller_issue: "pending"
  milestone_status: pending_issue
  goal: "Use ASGK to manage a real non-trivial work unit outside pure documentation-only governance additions."
  reason: "Vertical Governance Completion is complete at the thin-router layer; release preparation remains blocked until ASGK is field-tested on real work."
  deliverables:
    - GitHub issue with durable source of truth
    - allowed paths
    - PR with Merge Decision Record
    - `python3 scripts/asgk.py doctor` or equivalent validation
    - at least one handoff packet or handoff-template usage
    - result comment on issue
    - issue closeout
    - lessons learned recorded
    - docs/control/V1_READINESS_AUDIT.md updated after the field test
  non_goals:
    - release preparation
    - publication or tagging
    - runtime-specific adapters
    - target-install scaffold or installer behavior
    - new dependencies unless explicitly human-gated
  acceptance:
    - field test completes or is blocked for a useful reason
    - blockers are converted into GitHub issues
    - field-test lessons are recorded in durable repo or GitHub surfaces
    - V1_READINESS_AUDIT.md is updated after the field test
    - `python3 scripts/asgk.py doctor` passes
  risks:
    - field test may expose missing target-install or handoff ergonomics
    - release preparation may start too early if the field-test gate is skipped
  rollback_plan:
    - keep v1.1 stabilization active
    - convert blockers into bounded issues
    - do not start release preparation until the audit is updated
  human_gates:
    - release or publication decision
    - new dependency or external capability
    - schema-breaking or protected-path change
  phase_exit_criteria:
    - real_world_field_test_completed_or_usefully_blocked
    - field_test_lessons_recorded
    - readiness_audit_updated_after_field_test
```

## Completed Recent Milestones / Gates

```yaml
completed_recent:
  document_navigation_split:
    result: "DOCUMENT_MAP.md is compact router; DOCUMENT_REGISTRY.md owns full registry; CONTEXT_BUDGET_POLICY.md owns task read sets."
  target_install_checklist_and_plan:
    result: "INSTALL_SURFACE, TARGET_INSTALL_CHECKLIST, TARGET_INSTALL_VALIDATION_PLAN, target-install-check, and standalone target-install-plan are in place."
  vertical_governance_initial_layer:
    result: "PR #89 added the decision-point registry, decision packet template, registry links, and decision-point read set. This is the initial layer, not full milestone completion."
  vertical_governance_completion:
    result: "Issue #100 / PR #101 exercised a real low-risk autonomous merge decision; issue #102 closes the milestone by recording thin-layer coverage and deferring heavier decision-check tooling until a future field test proves the need."
    completed_control_lines:
      decision_control: "completed as a thin decision-point router and packet template"
      evidence_control: "covered as packet evidence fields and required-evidence table entries, not a standalone policy"
      authority_control: "covered by registry authority order and packet authority fields"
      lifecycle_control: "covered by lifecycle_position fields and decision-point table"
      capability_risk_control: "covered by minimum-level, human-gate, and stop-condition routing to existing canonical docs"
    policy_sprawl_result: "No new per-decision policy files, decision-check CLI, schema, workflow, script, dependency, runtime adapter, or installer scaffold was added."
```
