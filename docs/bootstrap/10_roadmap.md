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
  name: Release preparation planning
  controller_issue: "pending"
  milestone_status: pending_issue
  goal: "Plan v1.0 release preparation after the real-world field test and readiness-audit closeout."
  reason: "Vertical Governance Completion and the first real-world field test are complete; release work still requires a separate gated issue before tagging, publishing, packaging, licensing, or release decisions."
  deliverables:
    - final readiness review
    - license-selection decision path
    - tag/release process plan
    - package or distribution boundary
    - explicit v2.0 deferrals
    - remaining human gates
  non_goals:
    - immediate release tagging
    - package publishing
    - runtime-specific adapters
    - installer scaffold or target repository writes
    - new dependencies unless explicitly human-gated
  acceptance:
    - release-preparation issue exists
    - release gates are explicit
    - v2.0 deferrals are preserved
    - `python3 scripts/asgk.py doctor` passes
  risks:
    - release preparation may accidentally become release execution
    - license/package decisions may require human approval
    - v2.0 runtime adapter expectations may be confused with v1.0 readiness
  rollback_plan:
    - keep v1.1 stabilization records intact
    - do not tag or publish until explicit release issue approval
    - convert any unclear release gate into a separate issue
  human_gates:
    - license selection
    - release tagging
    - package publication
    - external distribution
  phase_exit_criteria:
    - release_preparation_plan_approved
    - release_blockers_explicit
    - release_execution_issue_created_or_deferred
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
    result: "Issue #100 / PR #101 exercised a real low-risk autonomous merge decision; issue #102 / PR #103 closed the milestone by recording thin-layer coverage and deferring heavier decision-check tooling until a future field test proves the need."
    completed_control_lines:
      decision_control: "completed as a thin decision-point router and packet template"
      evidence_control: "covered as packet evidence fields and required-evidence table entries, not a standalone policy"
      authority_control: "covered by registry authority order and packet authority fields"
      lifecycle_control: "covered by lifecycle_position fields and decision-point table"
      capability_risk_control: "covered by minimum-level, human-gate, and stop-condition routing to existing canonical docs"
    policy_sprawl_result: "No new per-decision policy files, decision-check CLI, schema, workflow, script, dependency, runtime adapter, or installer scaffold was added."
  real_world_field_test:
    result: "Issue #112 / PR #113 completed a bounded non-docs-only tooling/validation field test by adding `python3 scripts/asgk.py negative target-install` with opt-in expected-failure fixtures. Issue #114 records the readiness-audit closeout."
    lessons:
      - "ASGK can manage a bounded tooling/validation change through durable issue authority, PR, validation evidence, decision packet, Merge Decision Record, merge, and closeout."
      - "Opt-in negative command flow is safer before default CI wiring."
      - "Field-test implementation and readiness-audit closeout should remain separate steps."
```
