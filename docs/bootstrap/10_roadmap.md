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
  name: Post-v1.x stewardship and public-readiness decision
  controller_issue: "#132"
  milestone_status: public_readiness_decision_pending
  goal: "Keep the v1.0.0 source-only release state durable, clarify v1.x adoption surfaces, and preserve human gates for public visibility, broader distribution, package/installer work, and runtime-specific adapters."
  reason: "ASGK v1.0.0 source-only GitHub release is complete. Follow-up docs have clarified post-merge-safe status policy, product entry, and source-only adoption; the remaining open gate is whether to make the existing repository public."
  deliverables:
    - "public-readiness decision remains tracked through issue #132"
    - "v1.x product-entry and source-adoption docs remain aligned with source-only release state"
    - "future release/version decisions start from new durable GitHub issues"
  non_goals:
    - repository visibility change without explicit human approval
    - package publication
    - runtime-specific adapters
    - installer scaffold or target repository writes
    - v1.1 or later release execution without a new release issue
    - new dependencies unless explicitly human-gated
  acceptance:
    - completed v1.0.0 release state remains recorded in GitHub release, tag, issue #130, and closeout docs
    - post-v1 product-entry follow-ups remain recorded in merged PRs
    - public visibility decision remains human-gated through #132 or a successor issue
    - future v1.x or v2.0 work starts only from a new durable GitHub issue
  risks:
    - follow-up work may accidentally expand v1.0 source-only scope
    - v2.0 runtime adapter expectations may be confused with v1.0 readiness
    - source-only adoption wording may be mistaken for package or installer availability
    - public visibility may expose full repository history, issues, PRs, releases, and action logs
  rollback_plan:
    - use #130 rollback or revoke plan for any release metadata or tag correction
    - convert any unclear release gate into a separate issue
    - keep source repository state as the fallback release surface
  human_gates:
    - repository visibility change
    - package publication
    - external distribution beyond source-only GitHub release
    - runtime-specific adapter or installer work
  phase_exit_criteria:
    - public_visibility_decision_recorded_or_deferred
    - no_active_post_v1_product_entry_follow_up_required
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
  post_merge_safe_current_status:
    result: "Issue #135 / PR #136 made CURRENT_STATUS.md post-merge-safe by default, added the post_merge_safe PR field, and added a local current-status-impact check for self-staling status updates."
  product_entry_docs:
    result: "Issue #137 / PR #138 rewrote README.md and docs/QUICKSTART.md as v1.x product/adoption entry documents, moving lineage later and removing stale early-roadmap next steps."
  source_only_adoption_surface:
    result: "Issue #139 / PR #140 clarified docs/INSTALL_SURFACE.md and docs/DOCUMENT_REGISTRY.md for v1.x source-only adoption, Apache-2.0 / LICENSE handling, and non-installer/non-runtime boundaries."
```

## Likely Next Directions

```yaml
likely_next_directions:
  public_visibility_decision:
    durable_source: "#132 or successor human-gated issue"
    status: human_gated
    note: "Changing the existing repository to public exposes the full git history, issues, PRs, releases, and GitHub Actions logs."
  v1_1_candidate:
    durable_source: "new release-planning issue only if a human requests it"
    status: not_started
    possible_scope:
      - post-merge-safe current-status policy and checker
      - README / Quickstart product-entry refresh
      - source-only adoption and license-handling clarification
    non_goal: "Do not move tags or rewrite v1.0.0."
  v2_runtime_adapters:
    durable_source: "future v2.0 adapter/profile issues"
    status: deferred
    note: "Runtime-specific profiles remain optional optimization layers, not v1.x default governance."
```
