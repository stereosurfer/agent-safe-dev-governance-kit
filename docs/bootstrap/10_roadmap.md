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
  name: ASGK v1.7.0 source-only release preparation
  milestone_status: release_prep_ready_for_execution_issue
  release_prep_issue: "#307"
  release_execution_issue: pending_human_gated_issue
  planned_tag: v1.7.0
  planned_title: "ASGK v1.7.0"
  planned_target_commit: "94d2f1032f2ef4246bdd6327fc633f969af34253"
  release_execution_status: separate_human_gated_issue_required
  latest_completed_release: "ASGK v1.6.0"
  latest_release_issue: "#248"
  latest_release_url: https://github.com/stereosurfer/agent-safe-dev-governance-kit/releases/tag/v1.6.0
  note: "v1.7.0 preparation is recorded under #307, but the release is not completed until a separate human-gated release execution issue approves and creates the tag and GitHub release. Release history is canonical in GitHub releases, release issues, PRs, MDRs, comments, tags, and merge commits."
```

## Completed Recent Milestones / Gates

```yaml
completed_recent:
  document_navigation_split:
    result: "DOCUMENT_MAP.md is compact router; DOCUMENT_REGISTRY.md owns full registry; CONTEXT_BUDGET_POLICY.md owns task read sets."
  target_install_checklist_and_plan:
    result: "INSTALL_SURFACE, TARGET_INSTALL_CHECKLIST, TARGET_INSTALL_VALIDATION_PLAN, target-install-check, and the canonical `python3 scripts/asgk.py target-install-plan` wrapper are in place; standalone `scripts/target_install_plan.py` remains compatibility entrypoint."
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
  initial_source_only_release_policy:
    result: "Issue #116 / PR #117 added the initial source-only v1 release policy. Issue #118 / PR #119 refreshed current status after that policy closeout."
  final_v1_readiness_review:
    result: "Issue #120 records that no v1.0 core blocker is currently known and that release execution may be proposed only through a later separate human-gated issue."
  license_and_distribution_path:
    result: "Issue #124 records Apache-2.0 as the approved v1.0 license and source-only GitHub release as the selected distribution path."
  source_only_release_line:
    latest_completed_release: "ASGK v1.6.0"
    latest_release_issue: "#248"
    evidence_boundary: "Historical release execution details live in GitHub releases, release issues, PRs, MDRs, comments, tags, and merge commits."
    release_index: https://github.com/stereosurfer/agent-safe-dev-governance-kit/releases
  post_merge_safe_current_status:
    result: "Issue #135 / PR #136 made CURRENT_STATUS.md post-merge-safe by default, added the post_merge_safe PR field, and added a local current-status-impact check for self-staling status updates."
  product_entry_docs:
    result: "Issue #137 / PR #138 rewrote README.md and docs/QUICKSTART.md as v1.x product/adoption entry documents, moving lineage later and removing stale early-roadmap next steps."
  source_only_adoption_surface:
    result: "Issue #139 / PR #140 clarified docs/INSTALL_SURFACE.md and docs/DOCUMENT_REGISTRY.md for v1.x source-only adoption, Apache-2.0 / LICENSE handling, and non-installer/non-runtime boundaries."
  risk_gate_mechanization:
    result: "Issues #150, #152, #155, #157, and #161 added PR-body policy-gate CI wiring, changed-path hygiene CI wiring, PR status validation, task-packet schema-shaped validation, and GitHub closing issue reference validation."
  skill_pack_v0:
    result: "Issues #163 and #165 added source-distributed ASGK Skill Pack v0 plus maintenance touchpoint guidance without adding a new skill-compliance checker."
```

## Likely Next Directions

```yaml
likely_next_directions:
  public_visibility_decision:
    durable_source: "#132 or successor human-gated issue"
    status: human_gated
    note: "Changing the existing repository to public exposes the full git history, issues, PRs, releases, and GitHub Actions logs."
  future_v1_x_release:
    durable_source: "future human-gated release execution issue"
    status: human_gated
    note: "v1.7.0 release execution requires a separate issue with explicit approval naming the exact tag, title, target commit, source-only distribution, final validation, product-entry/handoff closeout plan, and rollback or revoke plan."
    non_goal: "Do not move existing tags or rewrite completed release history."
  v2_runtime_adapters:
    durable_source: "future v2.0 adapter/profile issues"
    status: deferred
    note: "Runtime-specific profiles remain optional optimization layers, not v1.x default governance."
```
