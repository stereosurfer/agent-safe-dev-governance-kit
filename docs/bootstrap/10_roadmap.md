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
  goal: "Add thin vertical governance so important decision points can be resumed, reviewed, and checked consistently across projects using ASGK."
  reason: "Horizontal repo governance is now strong; the next gap is consistent recovery of major decision points across target projects."
  deliverables:
    - docs/control/DECISION_POINT_REGISTRY.md
    - templates/decision_packet.template.yaml
    - docs/DOCUMENT_REGISTRY.md registration
    - docs/control/CONTEXT_BUDGET_POLICY.md decision-point read set
    - docs/control/V1_1_STABILIZATION_PLAN.md milestone alignment
    - docs/handoff/CURRENT_STATUS.md status alignment
  non_goals:
    - decision-check CLI in the first work unit
    - decision schema
    - one policy document per decision type
    - target-install scaffold or installer behavior
    - runtime-specific adapters
  acceptance:
    - decision-point layer remains a thin router/index
    - decision packet template captures inputs, evidence, authority, stop conditions, rollback, human gate, validation, and next safe action
    - current status identifies Vertical Governance Completion as active work
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
    - at least one future work unit can use a decision packet or explicitly defer it with reason
```

## Completed Recent Milestones / Gates

```yaml
completed_recent:
  document_navigation_split:
    result: "DOCUMENT_MAP.md is compact router; DOCUMENT_REGISTRY.md owns full registry; CONTEXT_BUDGET_POLICY.md owns task read sets."
  target_install_checklist_and_plan:
    result: "INSTALL_SURFACE, TARGET_INSTALL_CHECKLIST, TARGET_INSTALL_VALIDATION_PLAN, target-install-check, and standalone target-install-plan are in place."
```
