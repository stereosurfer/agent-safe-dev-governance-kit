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
  name: Post-v1.0 release follow-up
  controller_issue: "none"
  milestone_status: no_active_release_milestone
  goal: "Keep source-only v1.0 release state durable while deferring broader distribution and runtime-specific work to future human-gated issues."
  reason: "ASGK v1.0.0 source-only GitHub release is complete; no package, installer, adapter, or external distribution lane is active."
  deliverables: []
  non_goals:
    - package publication
    - runtime-specific adapters
    - installer scaffold or target repository writes
    - new dependencies unless explicitly human-gated
  acceptance:
    - completed v1.0.0 release state remains recorded in GitHub release, tag, issue #130, and closeout docs
    - future v1.x or v2.0 work starts only from a new durable GitHub issue
  risks:
    - follow-up work may accidentally expand v1.0 source-only scope
    - v2.0 runtime adapter expectations may be confused with v1.0 readiness
  rollback_plan:
    - use #130 rollback or revoke plan for any release metadata or tag correction
    - convert any unclear release gate into a separate issue
    - keep source repository state as the fallback release surface
  human_gates:
    - package publication
    - external distribution beyond source-only GitHub release
    - runtime-specific adapter or installer work
  phase_exit_criteria:
    - no_active_post_release_follow_up_required
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
  release_preparation_planning:
    result: "Issue #116 / PR #117 added a planning-only v1 release-preparation plan. Issue #118 / PR #119 refreshed current status after the planning closeout."
  final_v1_readiness_review:
    result: "Issue #120 records that no v1.0 core blocker is currently known and that release execution may be proposed only through a later separate human-gated issue."
  license_and_distribution_path:
    result: "Issue #124 records Apache-2.0 as the approved v1.0 license and source-only GitHub release as the selected distribution path."
  source_only_v1_0_release_execution:
    result: "Issue #130 created tag v1.0.0 and GitHub release ASGK v1.0.0 at target commit 7d2e364c4c53d1296c7ce1c2d241291837d54c61 after final doctor validation and explicit human approval."
    release_url: https://github.com/stereosurfer/agent-safe-dev-governance-kit/releases/tag/v1.0.0
```
