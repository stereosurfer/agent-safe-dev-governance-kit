# Target Install Validation Plan

Status: planned validation policy.

This document defines future mechanical checks for validating ASGK installation
inside a target repository.

It is not a validator implementation. It is the specification a future validator
should follow.

## Scope

The future validator should answer one question:

```text
Does this target repository look structurally safe to operate under ASGK governance?
```

It should not install files, rewrite files, modify repository state, call external
services, or infer project-specific policy beyond the installed governance files.

## Planned Command Shape

Future command shape may be:

```bash
python3 scripts/asgk.py target-install-check
```

Optional future arguments:

```bash
python3 scripts/asgk.py target-install-check --repo-root .
python3 scripts/asgk.py target-install-check --strict
python3 scripts/asgk.py target-install-check --json
```

## Validation Categories

```yaml
validation_categories:
  required_files: blocking
  template_derived_files: blocking_or_warning
  customize_required_files: blocking_or_warning
  forbidden_repo_local_surfaces: blocking
  legacy_key_guard: blocking_or_warning
  deferred_v2_guard: warning_or_blocking
  document_navigation_split: blocking
  current_status_freshness: warning
  validation_command_presence: warning
```

## Required-file Checks

The validator should check that required target files exist or are explicitly
marked not applicable in a target install record.

```yaml
required_file_checks:
  blocking_if_missing_without_exception:
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
    - agent/agent_rules.yaml
    - .github/PULL_REQUEST_TEMPLATE.md
    - .github/ISSUE_TEMPLATE/agent_task.yml
```

## Document Navigation Split Checks

The validator should check the router + registry split.

```yaml
document_navigation_split_checks:
  docs_DOCUMENT_MAP_md:
    must_exist: true
    must_be_compact_router: true
    must_reference:
      - docs/DOCUMENT_REGISTRY.md
      - docs/control/CONTEXT_BUDGET_POLICY.md
    must_not_contain:
      - "| Document | Role | Canonical for | Read by default | Read when | Owned by lane |"
      - "## Task-type Reading Guide"
  docs_DOCUMENT_REGISTRY_md:
    must_exist: true
    must_contain:
      - "# Document Registry"
      - "DOCUMENT_REGISTRY.md is repo-local"
    should_not_be_empty_registry: true
```

## Template-derived Checks

The validator should detect whether target files still look like unedited
templates.

```yaml
template_derived_checks:
  docs_DOCUMENT_MAP_md:
    warn_if_contains:
      - "target-project navigation router template"
      - "<lane>"
      - "<path>"
      - "<topic>"
  docs_DOCUMENT_REGISTRY_md:
    warn_if_contains:
      - "target-project template"
      - "<lane>"
      - "<path>"
      - "<topic>"
  agent_agent_rules_yaml:
    block_if_contains:
      - "status: target-project-template"
    warn_if_contains:
      - "Customize roles, allowed paths, and stop conditions"
```

## Customize-required Checks

The validator should warn or block when known customize-required files still look
like ASGK or placeholder content.

```yaml
customize_required_checks:
  docs_bootstrap_00_project_brief_md:
    warn_if_contains:
      - "ASGK"
      - "Bootstrap Kit"
      - "placeholder"
  docs_handoff_CURRENT_STATUS_md:
    block_if_contains:
      - "see chat"
    warn_if_contains:
      - "ASGK repository"
      - "stabilization"
      - "readiness audit"
  agent_task_packet_template_yaml:
    warn_if_contains:
      - "<lane>"
      - "<allowed_paths>"
```

## Forbidden Surface Checks

The validator should block target installations that include ASGK repo-local
surfaces as target authority.

```yaml
forbidden_surface_checks:
  block_if_present:
    - docs/control/V1_1_STABILIZATION_PLAN.md
    - docs/control/V1_READINESS_AUDIT.md
    - docs/control/UNCONTROLLED_DOCUMENT_AUDIT.md
    - docs/EVOLUTION_MODEL.md
  warn_if_present:
    - docs/handoff/AGENT_LOG.md
    - docs/handoff/DECISIONS.md
    - examples/negative/
    - profiles/
    - docs/adapters/
```

A target project may intentionally keep one of these only through a scoped
adaptation issue and a documented reason.

## Legacy-key Guard Checks

The validator should detect ASGK internal compatibility keys in target agent
rules.

```yaml
legacy_key_checks:
  agent_agent_rules_yaml:
    block_if_contains_without_migration_note:
      - require_subagent_intelligence_level
      - subagent_intelligence_levels
      - subagent_assignment_required_fields
    accept_if_contains:
      - require_assignment_intelligence_level
      - assignment_intelligence_levels
      - worker_assignment_required_fields
```

## Deferred-v2 Checks

The validator should warn when runtime-specific surfaces are present and block
when they are treated as v1.x defaults.

```yaml
deferred_v2_checks:
  warn_if_present:
    - profiles/codex-app/
    - profiles/chatgpt-web-github-connector/
    - profiles/claude-code/
    - profiles/cursor/
    - profiles/opengoat/
    - docs/adapters/
  block_if_default_startup_references:
    - profiles/
    - docs/adapters/
```

## Validation Command Checks

The validator should confirm the target repository has a known validation command
or explicitly records that validation is not yet installed.

```yaml
validation_command_checks:
  warn_if_missing_all:
    - scripts/asgk.py
    - .github/workflows/
    - documented_validation_command
```

## Output Format

Future validator output should be actionable.

```yaml
output_requirements:
  - result: pass | warning | fail
  - category
  - file
  - reason
  - recommended_fix
  - blocking: true | false
```

## Non-goals For First Validator

```yaml
first_validator_non_goals:
  - no file writes
  - no installer behavior
  - no external service calls
  - no schema migration
  - no runtime-adapter validation
  - no automatic PR creation
```

## Implementation Sequence

Recommended future sequence:

```yaml
implementation_sequence:
  1_add_static_checker:
    command: scripts/asgk.py target-install-check
    behavior: read-only
  2_add_negative_fixtures:
    examples:
      - target_map_is_full_registry
      - target_agent_rules_uses_legacy_subagent_keys
      - target_contains_ASGK_readiness_docs
  3_add_ci_optional_job:
    behavior: opt-in target-install validation
  4_add_installer_script:
    prerequisite: validator stable
```
