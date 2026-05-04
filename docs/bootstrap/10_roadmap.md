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
  name: Vertical Governance Completion
  controller_issue: "#88"
  milestone_status: active
  phase_state: initial_layer_completed
  goal: "Add thin vertical governance so important decision points can be resumed, reviewed, and checked consistently across projects using ASGK."
  reason: "Horizontal repo governance is now strong; the next gap is consistent recovery of major decision points across target projects."
  completed_initial_layer:
    issue: "#88"
    pr: "#89"
    outputs:
      - docs/control/DECISION_POINT_REGISTRY.md
      - templates/decision_packet.template.yaml
      - docs/DOCUMENT_REGISTRY.md registration
      - docs/control/CONTEXT_BUDGET_POLICY.md decision-point read set
      - docs/control/V1_1_STABILIZATION_PLAN.md milestone alignment
      - docs/handoff/CURRENT_STATUS.md status alignment
  remaining_exit_criteria:
    - exercise a decision packet in one real decision point
    - confirm the decision-point layer routes to existing canonical docs without policy sprawl
    - explicitly defer or scope any future decision-check CLI after the exercise
    - update readiness and field-test path after the decision-packet exercise
  non_goals:
    - decision-check CLI in the first work unit
    - decision schema
    - one policy document per decision type
    - target-install scaffold or installer behavior
    - runtime-specific adapters
  acceptance:
    - decision-point layer remains a thin router/index
    - decision packet template captures inputs, evidence, authority, stop conditions, rollback, human gate, validation, and next safe action
    - current status and roadmap distinguish initial-layer completion from milestone completion
    - next work can be discovered from repository state without prior chat history
    - `python3 scripts/asgk.py doctor` passes
  risks:
    - policy sprawl if each decision type becomes its own policy document
    - token bloat if decision-point work reads all canonical documents by default
    - confusion with existing Merge Decision Record if the registry duplicates rather than routes
  rollback_plan:
    - revert the decision registry/template PR if it introduces policy conflict or bloated context behavior
    - keep existing horizontal governance unchanged
  human_gates:
    - any tooling, schema, or file-writing automation beyond the docs/template layer
  phase_exit_criteria:
    - decision registry merged
    - decision packet template merged
    - decision packet exercised in a real decision point
    - policy-sprawl risk reviewed after the exercise
    - readiness or field-test path updated after the exercise
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
```
