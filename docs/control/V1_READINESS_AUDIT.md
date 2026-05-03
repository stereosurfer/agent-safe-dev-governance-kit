# V1 Readiness Audit

Status: active readiness audit.

This document defines what must be true before ASGK can be considered v1.0-ready. It is an audit surface, not an implementation task. It separates v1.0 blockers from v1.1 follow-ups and v2.0 runtime-specific work.

## Readiness Definition

ASGK v1.0 is ready when a new repository can use the generic, runtime-agnostic governance core to run bounded AI-assisted changes through:

```text
issue -> branch -> PR -> validation -> Merge Decision Record -> handoff -> merge/closeout
```

v1.0 readiness does not require runtime-specific adapters, full YAML parsing, SaaS packaging, or automatic semantic judgment.

## Current Maturity Snapshot

| Area | Current status | V1.0 impact |
|---|---:|---|
| Governance core | mostly ready | required |
| PR auto-validation | ready for v1.0 core | required |
| Negative defense tests | ready for core cases | required |
| Cross-agent handoff | ready for generic v0 | required |
| Current-status control | policy exists | required |
| CLI entrypoint | ready as minimal wrapper | required |
| Parser robustness | partial | v1.1 follow-up unless blocking bug appears |
| Runtime-specific adapters | deferred | v2.0 |
| Product packaging | early | v1.1 or later |

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
    - asgk status-check may become v1.1 tooling
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

## V1.0 Blockers

Current v1.0 blockers:

```yaml
v1_0_blockers: []
```

No current blocker is identified for a generic, runtime-agnostic v1.0 core.

This does not mean the project is finished. It means remaining known work can be classified as v1.1 or v2.0 unless a later audit discovers a defect in the core validation loop.

## V1.1 Follow-ups

Recommended v1.1 work:

```yaml
v1_1_follow_ups:
  parser_hardening_without_dependencies:
    reason: improve reliability of lightweight textual checks
    blocker_for_v1_0: false

  asgk_status_check:
    reason: automatically detect stale CURRENT_STATUS.md
    blocker_for_v1_0: false

  positive_handoff_template_fixture:
    reason: prove generated handoff-template output can be filled and checked
    blocker_for_v1_0: false

  install_or_template_usage_guide:
    reason: improve external adoption
    blocker_for_v1_0: false

  release_notes_and_tagging_policy:
    reason: package v1.0 more clearly
    blocker_for_v1_0: false

  uncontrolled_document_audit:
    reason: inspect other status-like docs for growth risk
    blocker_for_v1_0: false
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
  current_recommendation: proceed_to_v1_0_release_preparation
  reason: generic governance core, CI entrypoint, negative defense, handoff recovery, and current-status control are in place
  required_next_step: prepare v1.0 release checklist or tag policy
```

## Audit Use

Before declaring v1.0, review this file and update:

- blocker list;
- follow-up list;
- evidence list;
- readiness decision.

Do not use this file to hide known failures. If a core validation failure appears, convert it into a GitHub issue and mark it as a v1.0 blocker until fixed.
