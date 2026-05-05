# Target Install Validation Plan

Status: active validation policy with read-only check and plan layers.

This document defines mechanical checks and planning surfaces for validating ASGK
installation inside a target repository.

Implemented tooling is read-only. It is not an installer.

## Scope

The tooling answers two questions:

```text
1. Does this target repository look structurally safe to operate under ASGK governance?
2. What explicit installation plan should a future scaffold command follow?
```

It must not install files, rewrite files, modify repository state, call external
services, or infer project-specific policy beyond the installed governance files.

## Implemented Command Shapes

Read-only checker:

```bash
python3 scripts/asgk.py target-install-check
python3 scripts/asgk.py target-install-check --repo-root .
python3 scripts/asgk.py target-install-check --json
```

Read-only planner:

```bash
python3 scripts/target_install_plan.py
python3 scripts/target_install_plan.py --repo-root .
python3 scripts/target_install_plan.py --json
```

Preferred future wrapper:

```bash
python3 scripts/asgk.py target-install-plan
```

Not yet implemented:

```bash
python3 scripts/asgk.py target-install-check --strict
python3 scripts/asgk.py target-install-plan
```

## Validation Categories

```yaml
validation_categories:
  required_files: blocking
  license_handling: warning
  template_derived_files: blocking_or_warning
  customize_required_files: planned
  forbidden_repo_local_surfaces: blocking_or_warning
  legacy_key_guard: blocking_or_warning
  deferred_v2_guard: warning_or_blocking
  document_navigation_split: blocking
  current_status_freshness: planned
  validation_command_presence: warning
```

## License Handling Checks

The validator warns when no visible license or notice handling surface exists.
This is warning-only by default because target repositories may have their own
repository-level license policy.

```yaml
license_handling_checks:
  warn_if_missing_all:
    - LICENSE
    - LICENSE.md
    - NOTICE
    - NOTICE.md
    - THIRD_PARTY_NOTICES.md
    - docs/LICENSE.md
    - docs/NOTICE.md
  blocking_by_default: false
  warning_reason: "No visible surface explains how ASGK Apache-2.0 notices are preserved for copied or adapted ASGK-derived material."
  recommended_fix: "Add LICENSE/NOTICE handling or document ASGK Apache-2.0 attribution in the target repository's existing license or notice surface."
  non_goal: "Do not require the target repository to adopt Apache-2.0 globally."
```

## Required-file Checks

The validator checks that required target files exist.

```yaml
required_file_checks:
  blocking_if_missing:
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

The validator checks the router + registry split.

```yaml
document_navigation_split_checks:
  docs_DOCUMENT_MAP_md:
    must_exist: true
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

The validator detects whether target files still look like unedited templates.

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

Planned but not implemented in the first checker.

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

The validator blocks target installations that include known ASGK repo-local
surfaces as target authority and warns on optional/deferred surfaces that may
require explicit adaptation.

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

The validator detects ASGK internal compatibility keys in target agent rules.

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

Accepted migration-note markers for intentional compatibility:

```yaml
accepted_migration_note_markers:
  - target_legacy_key_migration
  - legacy_key_migration
```

## Deferred-v2 Checks

The validator warns when runtime-specific surfaces are present and blocks when
default startup surfaces reference deferred v2 paths.

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

The validator warns if the target repository has no obvious validation command or
workflow surface.

```yaml
validation_command_checks:
  warn_if_missing_all:
    - scripts/asgk.py
    - .github/workflows/
    - documented_validation_command
```

## Target Install Plan Output

The read-only planner emits a deterministic plan with these sections:

```yaml
target_install_plan:
  schema: asgk.target_install_plan.v0
  mode: read_only_plan
  writes_files: false
  copy_as_is:
    - source
    - target
    - source_status
    - target_status
  template_then_customize:
    - source
    - target
    - required_action
    - source_status
    - target_status
  customize_required:
    - path
    - required_review
    - target_status
  do_not_copy:
    - path
    - reason
    - target_status
  license_handling:
    - source_license
    - license
    - target_action
    - not_implied
  post_install_checks:
    - command_or_action
```

## Output Format

The checker emits actionable text by default and JSON when `--json` is used.
The planner emits a readable plan by default and JSON when `--json` is used.

```yaml
output_requirements:
  - result or schema
  - category_or_section
  - file_or_path
  - reason_or_required_action
  - recommended_fix_when_applicable
  - blocking_when_applicable
```

## Non-goals For Current Tooling

```yaml
current_tooling_non_goals:
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
    status: implemented_initial_subset
    command: scripts/asgk.py target-install-check
    behavior: read-only
  2_add_read_only_planner:
    status: implemented_standalone_script
    command: scripts/target_install_plan.py
    behavior: read-only
    future_wrapper: scripts/asgk.py target-install-plan
  3_add_negative_fixtures:
    examples:
      - target_map_is_full_registry
      - target_agent_rules_uses_legacy_subagent_keys
      - target_contains_ASGK_readiness_docs
  4_add_ci_optional_job:
    behavior: opt-in target-install validation
  5_add_scaffold_script:
    prerequisite: checker and planner stable
```
