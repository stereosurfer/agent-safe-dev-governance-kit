# Decisions

Status: durable decision log.

Record durable architecture and governance decisions here.

Boundary:

- Append concise decision entries only.
- Each entry should state the decision, date, and durable source issue or PR.
- Do not copy full discussions, PR bodies, or chronological work logs here.
- Issue-level pitfalls, avoidable repeated errors, future-agent hints, and
  promotion candidates belong in `docs/handoff/ISSUE_CLOSEOUT_REVIEWS.md`.
- Detailed rationale belongs in issues, PRs, comments, and merge commits.

## 2026-05-04 - Complete Vertical Governance Completion As Thin Layer

```yaml
decision:
  durable_source: "#102"
  result: "Complete Vertical Governance Completion at the thin-router layer."
  decision_packet_exercise:
    decision_type: low_risk_auto_merge_decision
    lifecycle_position: pre_merge
    durable_source:
      issue: "#100"
      pr: "#101"
    evidence:
      - "PR #101 stayed inside #100 allowed paths."
      - "PR #101 GitHub Actions validation passed."
      - "PR #101 Merge Decision Record allowed low-risk merge."
  vertical_control_lines:
    decision_control: "completed as DECISION_POINT_REGISTRY.md and decision_packet.template.yaml"
    evidence_control: "covered by decision-packet evidence fields and required-evidence registry rows"
    authority_control: "covered by registry authority order and packet authority fields"
    lifecycle_control: "covered by lifecycle_position and decision-point lifecycle rows"
    capability_risk_control: "covered by minimum-level, human-gate, and stop-condition routing"
  policy_sprawl_review: "No per-decision policy files, decision-check CLI, schema, workflow, script, dependency, runtime adapter, or installer scaffold was added."
  next_gate: "Real-world field test before release preparation."
```
