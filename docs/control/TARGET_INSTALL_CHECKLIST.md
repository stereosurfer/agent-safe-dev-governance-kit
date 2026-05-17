# Target Install Checklist

Status: active target-install specification.

This checklist defines what must be true before a target repository treats ASGK
as active governance.

It is a human- and agent-readable checklist. It is not an installer and not a
validator implementation.

## Core Rule

```text
A target repository must own its governance state.
```

Do not install ASGK by copying ASGK repo-local state into the target repository.
Use target templates, then customize the result for the target repository.

For existing ASGK-adopted repositories upgrading to compact governance, use an
upgrade manifest and keep it audit-and-plan until the target repository has its
own issue or PR:

```bash
python3 scripts/asgk.py compact-target-upgrade-check --manifest compact-target-upgrade.json
```

The manifest must preserve target-owned `CURRENT_STATUS.md`, document maps,
registries, bootstrap docs, and license surfaces.

## Required Target Files

The target repository should contain these governance surfaces before ASGK is
considered active:

```yaml
required_target_files:
  - AGENTS.md
  - README.md
  - docs/DOCUMENT_MAP.md
  - docs/DOCUMENT_REGISTRY.md
  - docs/handoff/CURRENT_STATUS.md
  - docs/control/CONTEXT_BUDGET_POLICY.md
  - docs/control/AGENT_CAPABILITY_MATRIX.md
  - docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md
  - docs/control/HUMAN_GATED_OPERATIONS.md
  - docs/control/MERGE_DECISION_RECORD.md
  - docs/control/TASK_PACKET_FORMAT.md
  - docs/control/AGENT_REPORT_FORMAT.md
  - .github/PULL_REQUEST_TEMPLATE.md
  - .github/ISSUE_TEMPLATE/agent_task.yml
```

Optional when the target repo uses ASGK CLI checks:

```yaml
optional_tooling_files:
  - scripts/asgk.py
  - scripts/policy_gate_check.py
  - scripts/pr_governance_preflight.py
```

## License Handling

ASGK v1.x is released under Apache-2.0. A target repository that copies or
adapts ASGK-derived files must preserve the applicable license and notice
handling for that material.

This does not mean the target repository must adopt Apache-2.0 as its global
license. The target owner must decide and record the target repository's own
license policy.

```yaml
license_handling_checks:
  visible_surface:
    examples:
      - LICENSE
      - LICENSE.md
      - NOTICE
      - NOTICE.md
      - THIRD_PARTY_NOTICES.md
      - docs/LICENSE.md
      - docs/NOTICE.md
  warning_if_missing: true
  blocking_by_default: false
  must_preserve:
    - ASGK Apache-2.0 notice for copied or adapted ASGK-derived material
    - applicable copyright notices
    - modification notices where Apache-2.0 requires them
  must_not_imply:
    - copying ASGK LICENSE automatically relicenses the whole target repository
```

## Template-derived Target Files

These files must be created from target-project templates and then customized.

```yaml
template_derived_files:
  - target: docs/DOCUMENT_MAP.md
    source_template: templates/DOCUMENT_MAP.template.md
    required_properties:
      - compact router only
      - points to docs/DOCUMENT_REGISTRY.md
      - does not contain full registry tables
      - does not contain ASGK repo-local registry rows
  - target: docs/DOCUMENT_REGISTRY.md
    source_template: templates/DOCUMENT_REGISTRY.template.md
    required_properties:
      - full target repository registry
      - placeholder rows removed
      - only target repository documents listed
```

## Customize-required Files

These files may be copied from ASGK starter material only if reviewed and adapted
for the target repository.

```yaml
customize_required_files:
  - docs/bootstrap/00_project_brief.md
  - docs/bootstrap/01_physical_boundaries.md
  - docs/bootstrap/02_storage_roots.md
  - docs/bootstrap/03_tech_stack.md
  - docs/handoff/CURRENT_STATUS.md
  - templates/task_packet.template.yaml
```

Required checks:

```yaml
customization_checks:
  project_brief:
    - target mission is present
    - target non-goals are present
    - no ASGK repository mission is treated as target mission
  physical_boundaries:
    - target writable paths are listed
    - target protected paths are listed
    - forbidden operations are listed
  storage_roots:
    - target Code Repo is identified
    - target Artifact Root policy is identified if used
    - target Local State Root policy is identified if used
  tech_stack:
    - target language/runtime/toolchain is declared
    - dependency policy is declared
  current_status:
    - target current state is fresh
    - next safe action is target-specific
    - no ASGK handoff state is present
  task_packet_template:
    - lanes match target repo
    - allowed path examples match target repo
    - validation commands match target repo
```

## Forbidden Target Authority

These ASGK repo-local or internal files must not become target-project authority.

```yaml
forbidden_as_target_authority:
  - ASGK docs/DOCUMENT_MAP.md
  - ASGK docs/DOCUMENT_REGISTRY.md
  - ASGK docs/handoff/AGENT_LOG.md
  - ASGK docs/handoff/DECISIONS.md
  - ASGK docs/control/HISTORICAL_ASGK_STABILIZATION_EVIDENCE.md
  - ASGK docs/control/HISTORICAL_ASGK_READINESS_EVIDENCE.md
  - ASGK docs/control/UNCONTROLLED_DOCUMENT_AUDIT.md
  - ASGK docs/EVOLUTION_MODEL.md
  - ASGK examples/negative/*
  - ASGK profiles/*
  - ASGK docs/adapters/*
```

## Deferred-v2 Guard

Runtime-specific adapter/profile material is not part of the v1.x target install
surface.

```yaml
deferred_v2_not_installed_by_default:
  - profiles/codex-app/
  - profiles/chatgpt-web-github-connector/
  - profiles/claude-code/
  - profiles/cursor/
  - profiles/opengoat/
  - docs/adapters/
```

These surfaces require a scoped v2.0 adapter/profile issue.

## Final Acceptance Checklist

```yaml
target_install_acceptance:
  - required target files exist or explicitly documented as not applicable
  - license or notice handling for ASGK-derived material is visible or explicitly documented
  - docs/DOCUMENT_MAP.md is a compact router
  - docs/DOCUMENT_REGISTRY.md is target-specific
  - customize-required files are target-specific
  - forbidden ASGK repo-local files are not target authority
  - deferred-v2 surfaces are not installed by default
  - target validation command is known
  - first governance smoke-test issue can be created
```

## Next Step

After this checklist is accepted, a later tooling issue may implement a mechanical
install-surface validator against `docs/control/TARGET_INSTALL_VALIDATION_PLAN.md`.
