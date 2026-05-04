# Install Surface

Status: active installation boundary policy.

This document defines which ASGK files may be copied, templated, customized, or
excluded when ASGK is installed into a target repository.

Its purpose is to prevent ASGK repo-local state, internal compatibility keys,
oversized internal registries, v2.0 placeholders, and self-governance history
from leaking into target projects.

## Core Rule

```text
Install the generic governance core, not the ASGK repository's internal state.
```

Target repositories must own their own repo-local governance state after
installation. They must not treat ASGK's internal `docs/DOCUMENT_MAP.md`,
`docs/handoff/*`, stabilization plans, readiness audits, or compatibility-only
agent rule keys as target-project truth.

## Install Surface Classes

```yaml
install_surface_classes:
  copy_as_is: "Stable generic governance files that may be copied directly."
  template_then_customize: "Starter files that must be copied from templates and edited for the target repo."
  customize_required: "Files that may be copied but must be reviewed and edited before use."
  do_not_copy_as_is: "ASGK repo-local or internal files that must not become target-project authority."
  deferred_v2: "Runtime-specific optimization surfaces not part of v1.x installation."
```

## Copy As Is

These files may be copied directly when installing the current generic v1.x core,
subject to later target-project customization if needed.

```yaml
copy_as_is:
  - AGENTS.md
  - docs/control/CONTEXT_BUDGET_POLICY.md
  - docs/control/AGENT_CAPABILITY_MATRIX.md
  - docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md
  - docs/control/HUMAN_GATED_OPERATIONS.md
  - docs/control/MERGE_DECISION_RECORD.md
  - docs/control/TASK_PACKET_FORMAT.md
  - docs/control/AGENT_REPORT_FORMAT.md
  - .github/PULL_REQUEST_TEMPLATE.md
  - .github/ISSUE_TEMPLATE/agent_task.yml
  - scripts/asgk.py
```

Notes:

- `AGENTS.md` may be copied as the generic operating guide, but the target repo
  should still review project-specific stop conditions and protected paths.
- `scripts/asgk.py` may be copied only if its checked file expectations match
  the target scaffold or are explicitly adapted later.

## Template Then Customize

These templates are designed for target repositories. Copy them to the target
path and edit them before treating them as authoritative.

```yaml
template_then_customize:
  - source: templates/DOCUMENT_MAP.template.md
    target: docs/DOCUMENT_MAP.md
    required_action: "Replace placeholders with target-repository documents."
  - source: templates/agent_rules.template.yaml
    target: agent/agent_rules.yaml
    required_action: "Review assignment levels, roles, allowed paths, and stop conditions for the target repo."
```

## Customize Required

These files may be useful in a target repo, but they require project-specific
edits before use.

```yaml
customize_required:
  - docs/bootstrap/00_project_brief.md
  - docs/bootstrap/01_physical_boundaries.md
  - docs/bootstrap/02_storage_roots.md
  - docs/bootstrap/03_tech_stack.md
  - docs/handoff/CURRENT_STATUS.md
  - agent/task_packet.template.yaml
```

Required customization:

```yaml
customization_requirements:
  project_brief: "Replace ASGK/placeholder mission with target project mission and non-goals."
  physical_boundaries: "Set actual writable paths, protected paths, and forbidden actions."
  storage_roots: "Set target project Code Repo, Artifact Root, and Local State Root model."
  tech_stack: "Declare target project runtime, language, dependencies, and dependency policy."
  current_status: "Create a fresh target-project current snapshot; do not copy ASGK current status."
  task_packet_template: "Ensure lanes, allowed paths, and validation commands match the target repo."
```

## Do Not Copy As Is

These files are ASGK repo-local, historical, internal, or field-test state. They
must not become target-project authority without a dedicated adaptation issue.

```yaml
do_not_copy_as_is:
  - docs/DOCUMENT_MAP.md
  - docs/handoff/AGENT_LOG.md
  - docs/handoff/DECISIONS.md
  - docs/control/V1_1_STABILIZATION_PLAN.md
  - docs/control/V1_READINESS_AUDIT.md
  - docs/control/UNCONTROLLED_DOCUMENT_AUDIT.md
  - docs/EVOLUTION_MODEL.md
  - examples/negative/*
  - profiles/*
  - docs/adapters/*
```

Reasons:

```yaml
reasons:
  docs_DOCUMENT_MAP_md: "ASGK repo-local map; use templates/DOCUMENT_MAP.template.md instead."
  handoff_logs_and_decisions: "ASGK repository history, not target project state."
  stabilization_and_readiness_docs: "ASGK internal maturity state, not target project readiness."
  uncontrolled_document_audit: "ASGK internal audit result."
  negative_examples: "Validator expected-failure fixtures; copy only for validation work."
  profiles_and_adapters: "v2.0 deferred runtime-specific optimization surfaces."
```

## Internal Compatibility Files

ASGK's internal `agent/agent_rules.yaml` contains compatibility keys such as
`subagent_intelligence_levels`. These keys are retained in the ASGK repository to
avoid breaking existing validation and examples.

Do not use those legacy key names as the target-project default. Use
`templates/agent_rules.template.yaml` instead.

```yaml
legacy_internal_keys:
  - require_subagent_intelligence_level
  - subagent_intelligence_levels
  - subagent_assignment_required_fields
preferred_target_template_keys:
  - require_assignment_intelligence_level
  - assignment_intelligence_levels
  - worker_assignment_required_fields
```

## Deferred V2 Surfaces

Runtime-specific adapters and profiles are not part of the v1.x target-project
install surface.

```yaml
deferred_v2:
  - profiles/codex-app/
  - profiles/chatgpt-web-github-connector/
  - profiles/claude-code/
  - profiles/cursor/
  - profiles/opengoat/
  - docs/adapters/
```

They may be added later only through a scoped v2.0 adapter/profile issue with
vendor documentation, observed tests, and explicit acceptance criteria.

## Target Installation Checklist

Before the target repository treats ASGK as active governance, confirm:

```yaml
target_installation_checklist:
  - AGENTS.md exists and points to target repo state, not chat memory.
  - docs/DOCUMENT_MAP.md was generated from templates/DOCUMENT_MAP.template.md and customized.
  - agent/agent_rules.yaml was generated from templates/agent_rules.template.yaml or reviewed for clean assignment terminology.
  - docs/handoff/CURRENT_STATUS.md is a fresh target snapshot.
  - allowed paths and protected paths match the target repo.
  - PR and issue templates exist.
  - validation command is known and documented.
  - ASGK repo-local history was not copied as target-project authority.
```

## Maintenance Rule

If installation behavior changes, update this document, `docs/QUICKSTART.md`,
`docs/DOCUMENT_MAP.md`, and the affected target templates in the same PR.
