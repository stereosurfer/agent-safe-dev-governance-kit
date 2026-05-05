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
| Governance core | ready for v1 core | required |
| PR auto-validation | ready for generic core | required |
| Negative defense tests | ready for core cases | required |
| Cross-agent handoff | ready for generic v0 | required |
| Current-status control | ready for v1 core | required |
| Vertical governance | thin layer completed | required |
| CLI entrypoint | ready as minimal wrapper | required |
| Parser robustness | sufficient for v1 core | required |
| Runtime-specific adapters | deferred | v2.0 |
| Product packaging | source-only GitHub release completed | source-only v1.0 complete |
| Real-world field test | completed | required before release preparation |
| Final readiness review | completed before release execution | satisfied |
| License | Apache-2.0 selected | required before public release |

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
    closeout: "#102 / PR #103"
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
- Policy-gate fixtures are available as opt-in expected failures.
- Target-install fixtures are available as opt-in expected failures.

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
    - policy_gate_opt_in
    - target_install_opt_in
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
    - PR #105 current-status closeout after vertical governance completion
    - PR #119 current-status closeout after release-preparation planning
```

### 6. CLI Entrypoint

Required v1.0 commands:

```bash
python3 scripts/asgk.py doctor
python3 scripts/asgk.py validate
python3 scripts/asgk.py hygiene --paths-file changed-paths.txt
python3 scripts/asgk.py negative
python3 scripts/asgk.py negative policy-gate
python3 scripts/asgk.py negative target-install
python3 scripts/asgk.py pr-body-check --file pr.md
python3 scripts/asgk.py task-packet-check --file task.yaml
python3 scripts/asgk.py handoff-check --file handoff.yaml
python3 scripts/asgk.py handoff-template
python3 scripts/asgk.py target-install-check
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
    - target-install negative fixtures are opt-in, not default CI
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
    - docs/DOCUMENT_REGISTRY.md
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

### 9. Real-world Field Test

Required sequence gate before release preparation:

- Real non-docs-only work unit.
- GitHub issue as durable authority.
- Bounded allowed paths.
- PR with Merge Decision Record.
- Validation evidence with limits.
- Decision packet or decision-packet-shaped section.
- Closeout and readiness audit update.

Current assessment:

```yaml
real_world_field_test:
  status: completed
  blocker: false
  implementation:
    issue: "#112"
    pr: "#113"
    merge_commit: "1dcdbd08a20a41a903d474ff8080317eefd87185"
    issue_state: closed_completed
  work_type: real_tooling_validation_work
  command_added: python3 scripts/asgk.py negative target-install
  validation_evidence:
    local:
      - python3 scripts/asgk.py negative target-install
      - python3 scripts/asgk.py negative all
      - python3 scripts/asgk.py doctor
    ci:
      - GitHub Actions validate passed for PR #113
  evidence_limits:
    - did not prove target installation in a real external repository
    - did not wire target-install negative fixtures into default CI
    - did not add installer scaffold or target repository writes
  lessons_learned:
    - ASGK can manage a bounded non-docs-only tooling/validation change through issue, branch, PR, validation evidence, decision packet, merge decision, merge, and closeout.
    - Decision packet fields were useful for recording validation source, evidence limits, forbidden actions, rollback, and human-gate status without creating new policy families.
    - Opt-in negative command flow is a safe intermediate step before default CI wiring.
    - Readiness audit closeout is a separate required step after implementation merge; otherwise field-test implementation can be mistaken for full field-test completion.
  follow_up_issues:
    - none_required_for_v1_release_preparation_gate
  release_readiness_impact: field_test_sequence_gate_satisfied
```

### 10. Final V1.0 Readiness Review

Current assessment:

```yaml
final_v1_readiness_review:
  status: completed_before_release_execution
  blocker: false
  reviewed_by_issue: "#120"
  result: "No v1.0 core blocker was recorded before release execution. Issue #130 later executed the source-only GitHub release after explicit human approval."
  remaining_human_gates:
    - package publication
    - external distribution
  remaining_not_authorized_by_this_review_or_release:
    - publishing a package
    - external distribution beyond source-only GitHub release
```

### 11. License And Distribution Path

Current assessment:

```yaml
license_and_distribution_path:
  status: selected
  blocker: false
  issue: "#124"
  selected_license: Apache-2.0
  license_file: LICENSE
  license_file_status: full_apache_2_0_text
  selected_distribution_path: source_only_github_release
  remaining_human_gates:
    - package publication
    - external distribution beyond source-only GitHub release
  note: "Source-only GitHub release v1.0.0 was executed under issue #130."
```

## Release Preparation Sequence Gate

The generic governance core and the required v1.1 sequence gates were satisfied
enough to execute a source-only v1.0 release only through a later separate issue.
Issue #130 completed that source-only release execution after explicit human
approval.

```yaml
release_preparation_gate:
  status: source_only_release_executed_by_130
  required_before_release_execution:
    - review docs/control/V1_1_STABILIZATION_PLAN.md
    - complete Vertical Governance Completion at thin-router layer
    - complete at least one real-world field test
    - record field-test lessons
    - update this audit after the field test
    - complete final v1.0 readiness review
    - select license
    - select distribution path
  satisfied_by:
    vertical_governance_completion: "#102 / PR #103"
    field_test_implementation: "#112 / PR #113"
    field_test_readiness_audit: "#114 / PR #115"
    release_preparation_plan: "#116 / PR #117"
    current_status_closeout: "#118 / PR #119"
    final_readiness_review: "#120 / PR #121"
    license_and_distribution_path: "#124"
    release_execution: "#130"
```

## V1.0 Blockers

Current technical blockers in the generic governance core:

```yaml
v1_0_core_blockers: []
```

Sequence blockers before opening source-only release execution issue:

```yaml
release_preparation_sequence_blockers: []
completed_sequence_gates:
  - vertical_governance_completion
  - real_world_field_test
  - post_field_test_readiness_audit
  - release_preparation_planning
  - final_v1_readiness_review
  - license_and_distribution_path
```

This distinction matters: the audit did not itself release the core. The later
human-gated release-execution issue #130 created the source-only v1.0.0 GitHub
release.

## V1.1 Stabilization Work

See `docs/control/V1_1_STABILIZATION_PLAN.md` for the stabilization plan.

Summary:

```yaml
v1_1_stabilization:
  parser_hardening_without_dependencies:
    reason: improve reliability of lightweight textual checks
    status: completed_or_sufficient_for_v1_core

  asgk_status_check:
    reason: automatically detect stale or oversized CURRENT_STATUS.md
    status: completed

  positive_handoff_template_fixture:
    reason: prove generated handoff-template output can be filled and checked
    status: completed

  uncontrolled_document_audit:
    reason: inspect other status-like docs for growth risk
    status: completed

  vertical_governance_completion:
    reason: complete decision/evidence/authority/lifecycle/capability-risk routing without policy sprawl
    status: completed_as_thin_layer

  real_world_field_test:
    reason: prove ASGK outside pure docs/governance self-modification
    status: completed
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
  current_recommendation: source_only_release_completed
  reason: Apache-2.0 and source-only GitHub release path were selected; no v1.0 core blocker was recorded; issue #130 confirmed target commit, final checks, release notes, rollback/revoke plan, and explicit human approval.
  release:
    tag_name: v1.0.0
    target_commit: "7d2e364c4c53d1296c7ce1c2d241291837d54c61"
    url: https://github.com/stereosurfer/agent-safe-dev-governance-kit/releases/tag/v1.0.0
  required_next_step: none_for_v1_0_release_execution
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
