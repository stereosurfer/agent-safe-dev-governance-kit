# Target Install Validation Plan

Status: active validation and planning contract.

This document defines the read-only target-install checker, the read-only
target-install planner, and the compact target-upgrade manifest boundary.

It is not an installer, scaffold command, migration engine, or target repository
approval record.

## Purpose

Target-install validation answers two questions:

```text
1. Does this target repository look structurally safe to operate under ASGK governance?
2. What explicit read-only installation or upgrade plan should a future reviewed command follow?
```

The tooling must not write files, rewrite repository state, call external
services, infer project-specific policy, or treat ASGK source-repo state as
target-repo state.

## Document Boundary

```yaml
this_document_owns:
  - target-install checker behavior categories
  - target-install planner output contract
  - compact target-upgrade manifest check boundary
  - implemented versus planned target-install check classification
  - read-only and no-installer requirements

this_document_does_not_own:
  - human target-install checklist acceptance
  - install-surface copy/template/customize policy
  - script implementation details
  - target repository license decisions
  - future scaffold execution
  - CI workflow wiring

canonical_neighbors:
  human_checklist: docs/control/TARGET_INSTALL_CHECKLIST.md
  install_surface: docs/INSTALL_SURFACE.md
  checker_implementation: scripts/asgk_lib/target_install.py
  planner_implementation: scripts/target_install_plan.py
  compact_upgrade_manifest: python3 scripts/asgk.py compact-target-upgrade-check --help
```

## Source Repo Versus Target Repo

The ASGK source repository is not expected to pass `target-install-check` when
checked as if it were a target repository. The source repo intentionally contains
ASGK repo-local evidence, negative fixtures, adapters, examples, and internal
history that target repositories must not copy as authority.

```yaml
source_repo_self_check:
  expected_result: may_fail
  reason: ASGK source repo contains do-not-copy and repo-local surfaces
  not_a_bug_when:
    - docs/control/HISTORICAL_ASGK_* evidence is present
    - examples/negative/ is present
    - docs/adapters/ is present
    - source repo-local maps and registries are present
```

Use target-install checks against target repositories or target-install fixtures,
not as a release-readiness proof for the ASGK source repo.

## Current Command Surface

```yaml
implemented:
  target_install_check:
    command: python3 scripts/asgk.py target-install-check --repo-root <target>
    json: python3 scripts/asgk.py target-install-check --repo-root <target> --json
    behavior: read_only
  target_install_plan:
    command: python3 scripts/target_install_plan.py --repo-root <target>
    json: python3 scripts/target_install_plan.py --repo-root <target> --json
    behavior: read_only
  compact_target_upgrade_check:
    command: python3 scripts/asgk.py compact-target-upgrade-check --manifest <manifest.json>
    behavior: read_only_manifest_check

not_implemented:
  - python3 scripts/asgk.py target-install-check --strict
  - python3 scripts/asgk.py target-install-plan
  - scaffold or installer file writes
  - target-install CI job by default
```

Use command help for exact syntax. This document owns behavior boundaries, not a
complete CLI manual.

## Checker Categories

The checker emits findings with category, file/path, reason, recommended fix,
severity, and blocking status. Blocking findings return a failing exit code;
warnings return success with actionable findings.

```yaml
implemented_checker_categories:
  required_files:
    default: blocking
    checks: required ASGK governance files exist in the target
  license_handling:
    default: warning
    checks: visible license or notice handling surface exists
  document_navigation_split:
    default: blocking_or_warning
    checks: DOCUMENT_MAP is a compact router and DOCUMENT_REGISTRY is a registry
  template_derived_files:
    default: warning
    checks: router and registry no longer contain obvious template markers
  forbidden_repo_local_surfaces:
    default: blocking_or_warning
    checks: ASGK source-only history, audits, examples, adapters, or profiles are not target authority
  deferred_v2_guard:
    default: blocking_when_default_startup_references_v2
    checks: profiles and adapters are not part of v1.x default startup
  validation_command_presence:
    default: warning
    checks: target has an obvious validation command or workflow surface
```

## Required And Forbidden Surfaces

Target repositories should include the required governance surfaces listed in
`docs/control/TARGET_INSTALL_CHECKLIST.md`. This plan does not duplicate that
full checklist; it defines how the checker classifies the mechanical findings.

```yaml
must_not_be_target_authority:
  blocking:
    - docs/control/HISTORICAL_ASGK_STABILIZATION_EVIDENCE.md
    - docs/control/HISTORICAL_ASGK_READINESS_EVIDENCE.md
    - docs/control/UNCONTROLLED_DOCUMENT_AUDIT.md
    - docs/EVOLUTION_MODEL.md
    - legacy docs/control/V1_1_STABILIZATION_PLAN.md
    - legacy docs/control/V1_READINESS_AUDIT.md
  warning:
    - docs/handoff/AGENT_LOG.md
    - docs/handoff/DECISIONS.md
    - examples/negative/
    - profiles/
    - docs/adapters/
```

A target project may keep one of these only through a scoped adaptation issue and
documented reason. Keeping it must not make ASGK source-repo history target
authority.

## Compact Target-Upgrade Manifest Boundary

The compact target-upgrade checker validates planning manifests for repositories
that already adopted ASGK and want to upgrade to compact governance surfaces.
It does not write target repositories.

```yaml
compact_target_upgrade_contract:
  schema_version: asgk.compact_target_upgrade.v1
  mode: audit_and_plan
  required_defaults:
    target_repository_writes_performed: false
    compact_governance.default_enabled: false
    durable_upgrade_issue_required: true
  license_boundary:
    asgk_apache_2_notice_preserved: true
    target_license_replaced: false
  never_overwrite:
    - docs/handoff/CURRENT_STATUS.md
    - docs/DOCUMENT_MAP.md
    - docs/DOCUMENT_REGISTRY.md
    - docs/bootstrap/00_project_brief.md
    - docs/bootstrap/01_physical_boundaries.md
    - docs/bootstrap/02_storage_roots.md
    - docs/bootstrap/03_tech_stack.md
    - LICENSE
```

## Planner Output Contract

The planner emits a deterministic read-only plan. It may report what should be
copied, templated, customized, or avoided, but it must not perform those writes.

```yaml
target_install_plan:
  schema: asgk.target_install_plan.v0
  mode: read_only_plan
  writes_files: false
  sections:
    copy_as_is:
      fields: [source, target, source_status, target_status]
    template_then_customize:
      fields: [source, target, required_action, source_status, target_status]
    customize_required:
      fields: [path, required_review, target_status]
    do_not_copy:
      fields: [path, reason, target_status]
    license_handling:
      fields: [source_license, license, target_action, not_implied]
    post_install_checks:
      fields: [command_or_action]
```

## Planned But Not Current Behavior

These checks or commands may be implemented later only through a separate issue.
They must not be treated as current validator guarantees.

```yaml
planned_or_future_optional:
  customize_required_content_checks:
    status: planned
    examples:
      - target project brief has target mission
      - current status is target-specific and fresh
      - task packet template examples match target repo lanes
  current_status_freshness:
    status: planned
    boundary: target-specific freshness review, not ASGK source-repo release state
  target_install_plan_wrapper:
    status: not_implemented
    command: python3 scripts/asgk.py target-install-plan
  strict_mode:
    status: not_implemented
    command: python3 scripts/asgk.py target-install-check --strict
  optional_ci_job:
    status: future_optional
    boundary: opt-in target-install validation only
  scaffold_script:
    status: future_optional
    prerequisite: checker and planner are stable and a reviewed plan exists
```

## Output Requirements

```yaml
checker_output_requires:
  - result
  - category
  - file_or_path
  - reason
  - recommended_fix
  - blocking

planner_output_requires:
  - schema
  - mode
  - writes_files
  - copy_as_is
  - template_then_customize
  - customize_required
  - do_not_copy
  - license_handling
  - post_install_checks
```

## Non-goals

```yaml
current_tooling_non_goals:
  - no file writes
  - no installer behavior
  - no external service calls
  - no schema migration
  - no runtime-adapter validation
  - no automatic PR creation
  - no target repository approval
```

## Validation Expansion Rules

Target-install validation may expand only when a durable issue authorizes the
new check, names expected positive and negative cases, and explains whether the
new finding is blocking or warning.

Loosening required-file, do-not-copy, license-boundary, or target-owned-state
checks requires explicit human approval.
