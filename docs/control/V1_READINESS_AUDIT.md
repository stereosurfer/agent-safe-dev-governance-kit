# V1 Readiness Audit

Status: active readiness audit.

This document defines what must be true before ASGK can be considered v1.0-ready. It is an audit surface, not an implementation task. It separates release-preparation sequence gates from v1.1 follow-ups and v2.0 runtime-specific work.

## Readiness Definition

ASGK v1.0 is ready when a new repository can use the generic, runtime-agnostic governance core to run bounded AI-assisted changes through:

```text
issue -> branch -> PR -> validation -> Merge Decision Record -> handoff -> merge/closeout
```

v1.0 readiness does not require runtime-specific adapters, full YAML parsing, SaaS packaging, or automatic semantic judgment.

## Current Maturity Snapshot

| Area | Current status | Release impact |
|---|---:|---|
| Governance core | mostly ready | required |
| PR auto-validation | ready for generic core | required |
| Negative defense tests | ready for core cases | required |
| Cross-agent handoff | ready for generic v0 | required |
| Current-status control | policy exists | required |
| Vertical governance | thin layer completed | required before field test |
| CLI entrypoint | ready as minimal wrapper | required |
| Parser robustness | partial | stabilize before release preparation if practical |
| Runtime-specific adapters | deferred | v2.0 |
| Product packaging | early | release preparation |
| Real-world field test | not yet completed | required before release preparation |

## V1.0 Readiness Dimensions

### 1. Governance Core

Required v1.0 capabilities:

- GitHub issue as durable task authority.
- PR body with required sections.
- Merge Decision Record.
- Human-gated operation boundaries.
- Low-risk merge policy.
- Document ownership map.
- Context budget policy.
- Current-status policy.
- Thin vertical decision-point routing without policy sprawl.

Current assessment:

```yaml
governance_core:
  status: ready_for_v1_core
  blocker: false
  evidence:
    - docs/DOCUMENT_MAP.md
    - docs/control/CONTEXT_BUDGET_POLICY.md
    - docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md
    - docs/control/HUMAN_GATED_OPERATIONS.md
    - docs/control/MERGE_DECISION_RECORD.md
    - docs/control/CURRENT_STATUS_POLICY.md
    - docs/control/DECISION_POINT_REGISTRY.md
    - templates/decision_packet.template.yaml
```

### 1a. Vertical Governance

Required v1.1 capabilities before the real-world field test:

- Decision Control: identify major decision points and route them to canonical docs.
- Evidence Control: capture evidence type, source, reproducibility, and sufficiency in the decision packet.
- Authority Control: define authority order when issue, PR, policy, packet, status, examples, and chat disagree.
- Lifecycle Control: record where the decision sits in the work-unit lifecycle.
- Capability / Risk Control: route minimum capability level, human gates, stop conditions, and rollback to existing canonical docs.

Current assessment:

```yaml
vertical_governance:
  status: completed_as_thin_layer
  blocker: false
  evidence:
    initial_layer: "#88 / PR #89"
    decision_exercise: "#100 / PR #101"
    closeout: "#102"
    documents:
      - docs/control/DECISION_POINT_REGISTRY.md
      - templates/decision_packet.template.yaml
      - docs/control/V1_1_STABILIZATION_PLAN.md
      - docs/bootstrap/10_roadmap.md
  policy_sprawl_review:
    result: avoided
    avoided_outputs:
      - per-decision policy files
      - decision-check CLI
      - decision schema
      - workflow changes
      - script changes
      - new dependencies
      - runtime adapters
      - installer scaffold
  follow_up:
    - promote evidence, authority, lifecycle, or capability/risk into standalone policy or tooling only if a later field test proves the need
```

### 2. PR Auto-validation

Required v1.0 capabilities:

- One CI entrypoint.
- Positive scaffold/bootstrap checks.
- Whitespace checks.
- Negative expected-failure checks for core known-bad cases.

Current assessment:

```yaml
pr_auto_validation:
  status: ready_for_v1_core
  blocker: false
  entrypoint: python3 scripts/asgk.py doctor
  ci_workflow: .github/workflows/bootstrap-validation.yml
```

### 3. Negative Defense Tests

Required v1.0 core cases:

- Runtime artifact paths are blocked.
- Protected paths are blocked.
- Private/binary source-like paths are blocked.
- PR body missing Merge Decision is blocked.
- PR body `see chat` authority is blocked.
- Task packet `see chat` authority is blocked.
- Task packet missing `stop_conditions` is blocked.
- Handoff packet missing critical recovery fields is blocked.

Current assessment:

```yaml
negative_defense:
  status: ready_for_v1_core
  blocker: false
  covered_categories:
    - changed_paths
    - pr_body
    - task_packet
    - handoff_packet
  known_gap: full semantic policy contradiction detection is not automated
```

### 4. Handoff And Cross-agent Recovery

Required v1.0 capabilities:

- Generic handoff packet specification.
- Handoff recovery context profile.
- Handoff packet negative tests.
- AI-fillable handoff template.
- Handoff check command.

Current assessment:

```yaml
cross_agent_handoff:
  status: ready_for_v1_core
  blocker: false
  evidence:
    - docs/control/HANDOFF_PACKET.md
    - docs/control/CONTEXT_BUDGET_POLICY.md
    - scripts/asgk.py handoff-template
    - scripts/asgk.py handoff-check
```

### 5. Current-status Control

Required v1.0 capabilities:

- `CURRENT_STATUS.md` must be compact.
- It must be overwritten, not appended.
- History must stay in GitHub issues, PRs, comments, and merge commits.
- The status surface must not retain stale active work.

Current assessment:

```yaml
current_status_control:
  status: ready_for_v1_core
  blocker: false
  evidence:
    - docs/control/CURRENT_STATUS_POLICY.md
    - docs/handoff/CURRENT_STATUS.md
  follow_up:
    - asgk status-check should be evaluated during v1.1 stabilization
```

### 6. CLI Entrypoint

Required v1.0 commands:

```bash
python3 scripts/asgk.py doctor
python3 scripts/asgk.py validate
python3 scripts/asgk.py hygiene --paths-file changed-paths.txt
python3 scripts/asgk.py negative
python3 scripts/asgk.py pr-body-check --file pr.md
python3 scripts/asgk.py task-packet-check --file task.yaml
python3 scripts/asgk.py handoff-check --file handoff.yaml
python3 scripts/asgk.py handoff-template
```

Current assessment:

```yaml
cli_entrypoint:
  status: ready_for_v1_core
  blocker: false
  known_limitations:
    - lightweight textual checks only
    - no full YAML parser
    - no GitHub API integration
    - no automatic file write for handoff-template
```

### 7. Documentation Ownership And Context Budget

Required v1.0 capabilities:

- Document map names canonical vs summary/example/template/script surfaces.
- Context policy prevents full-repo reading by default.
- Handoff recovery has a minimum read set.
- Runtime-specific adapters are not part of v1.x default context.

Current assessment:

```yaml
docs_context:
  status: ready_for_v1_core
  blocker: false
  evidence:
    - docs/DOCUMENT_MAP.md
    - docs/control/CONTEXT_BUDGET_POLICY.md
```

### 8. Human Judgment Boundaries

Required v1.0 capabilities:

- Human-gated operations are explicit.
- CLI and templates do not fabricate final semantic judgment.
- Handoff template uses TODO markers for judgment-heavy fields.
- Runtime-specific adapters are deferred until vendor docs and observed tests exist.

Current assessment:

```yaml
human_judgment_boundaries:
  status: ready_for_v1_core
  blocker: false
  human_judgment_required_for:
    - semantic policy conflicts
    - release/publication decisions
    - schema breaking changes
    - new dependencies
    - external API/model/MCP capability
    - runtime-specific adapter accuracy
```

## Release Preparation Sequence Gate

Although the generic governance core is close to v1.0-ready, release preparation is deliberately deferred until v1.1 stabilization work and at least one real-world field test are completed or explicitly deferred with rationale.

```yaml
release_preparation_gate:
  status: deferred
  required_before_release_preparation:
    - review docs/control/V1_1_STABILIZATION_PLAN.md
    - complete or explicitly defer parser hardening without dependencies
    - complete or explicitly defer asgk status-check
    - complete or explicitly defer positive handoff-template fixture
    - complete or explicitly defer uncontrolled-document audit
    - complete Vertical Governance Completion at thin-router layer
    - complete at least one real-world field test
    - record field-test lessons
    - update this audit after the field test
```

## V1.0 Blockers

Current technical blockers in the generic governance core:

```yaml
v1_0_core_blockers: []
```

Sequence blockers before release preparation:

```yaml
release_preparation_sequence_blockers:
  - v1_1_stabilization_not_completed
  - real_world_field_test_not_completed
completed_sequence_gates:
  - vertical_governance_completion
```

This distinction matters: the core is not known-broken, but release preparation should wait until the stabilization sequence is complete.

## V1.1 Stabilization Work

See `docs/control/V1_1_STABILIZATION_PLAN.md` for the active plan.

Summary:

```yaml
v1_1_stabilization:
  parser_hardening_without_dependencies:
    reason: improve reliability of lightweight textual checks

  asgk_status_check:
    reason: automatically detect stale or oversized CURRENT_STATUS.md

  positive_handoff_template_fixture:
    reason: prove generated handoff-template output can be filled and checked

  uncontrolled_document_audit:
    reason: inspect other status-like docs for growth risk

  vertical_governance_completion:
    reason: complete decision/evidence/authority/lifecycle/capability-risk routing without policy sprawl
    status: completed_as_thin_layer

  real_world_field_test:
    reason: prove ASGK outside pure docs/governance self-modification
    status: active_next_gate
```

## V2.0 Deferred Work

Runtime-specific optimization remains v2.0:

```yaml
v2_0_deferred:
  runtime_profiles:
    - Codex
    - ChatGPT Web / GitHub connector
    - OpenGoat
    - Claude Code
    - Cursor
    - Copilot
  requirements:
    - vendor documentation
    - observed behavior tests
    - no bypass of ASGK core governance
```

## Readiness Decision

```yaml
readiness_decision:
  version_target: v1.0
  current_recommendation: proceed_to_v1_1_stabilization_before_release_preparation
  reason: Vertical Governance Completion is satisfied at the thin-router layer; release preparation still waits for a real-world field test, field-test lessons, and a post-test audit update before licensing, tagging, and packaging gates
  required_next_step: execute the Real-world field test milestone
```

## Audit Use

Before declaring v1.0, review this file and update:

- blocker list;
- stabilization status;
- field-test evidence;
- follow-up list;
- evidence list;
- readiness decision.

Do not use this file to hide known failures. If a core validation failure appears, convert it into a GitHub issue and mark it as a v1.0 blocker until fixed.
