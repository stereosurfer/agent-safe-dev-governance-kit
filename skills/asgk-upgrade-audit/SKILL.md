---
name: asgk-upgrade-audit
description: Use when updating an existing ASGK-adopted repository to newer ASGK guidance; audits target repo surfaces, separates reusable ASGK updates from target-owned state, and produces a bounded upgrade issue or PR plan without overwriting repo-local status or document maps.
---

# ASGK Upgrade Audit

Use this skill when an existing repository has already adopted ASGK and needs to
update to newer ASGK guidance, templates, skills, or policies.

This skill is for audit and planning by default. It is not an auto-upgrader.

## Authority

This skill does not create upgrade authority, approve changes, or override target
repository rules. Durable scope must live in a GitHub issue or repository file.

If this skill conflicts with `AGENTS.md`, the target repository's GitHub issue or
PR, target repository control documents, or ASGK validators, stop and use the
repository authority.

## Core Rule

```text
Upgrade reusable ASGK governance surfaces; do not overwrite target-owned state.
```

Target repositories own their own current status, document map, document
registry, project brief, physical boundaries, storage roots, and project-specific
rules. These must not be replaced with ASGK source-repository state.

## Required Inputs

- Target repository name or local checkout.
- Current ASGK source version or source branch to compare against.
- Target repository governance files, when available:
  - `AGENTS.md`
  - `README.md`
  - `.github/PULL_REQUEST_TEMPLATE.md`
  - `.github/ISSUE_TEMPLATE/agent_task.yml`
  - `docs/handoff/CURRENT_STATUS.md`
  - `docs/DOCUMENT_MAP.md`
  - `docs/DOCUMENT_REGISTRY.md`
  - `docs/control/CURRENT_STATUS_POLICY.md`
  - `docs/INSTALL_SURFACE.md`
  - `scripts/asgk.py`
  - `skills/`
- Target validation command, usually `python3 scripts/asgk.py doctor`.

## Procedure

### 1. Detect

Identify which ASGK surfaces exist in the target repository.

```yaml
detect:
  required_checks:
    - AGENTS.md exists
    - PR template exists
    - issue template exists or target issue process is documented
    - CURRENT_STATUS.md exists and is target-owned
    - validation command is known
    - scripts/asgk.py exists or target has an explicit replacement
    - skills/ exists or target uses repository-reference mode only
```

Do not assume the target repository is current because one ASGK file exists.

### 2. Classify

Classify the target repository before proposing changes.

```yaml
target_classification:
  recent_asgk:
    meaning: "Target has current ASGK layout and validators; small guidance update may be enough."
  older_asgk_without_skills:
    meaning: "Target has core governance but no source-distributed skill pack."
  customized_asgk:
    meaning: "Target has ASGK-derived files with project-specific sections that must be manually merged."
  partial_asgk:
    meaning: "Target has only some governance surfaces; adoption audit may be needed before upgrade."
  non_asgk:
    meaning: "Target should use target-install audit, not upgrade audit."
```

### 3. Separate Surfaces

Separate safe update candidates from target-owned state.

```yaml
safe_update_candidates:
  - reusable skills when the target already uses ASGK skill layout
  - generic control-policy wording when target customization is minimal
  - PR template snippets when merged into the target template without removing local sections
  - validator scripts only in a separate tooling issue
manual_merge_required:
  - .github/PULL_REQUEST_TEMPLATE.md when target has local sections
  - docs/control/CURRENT_STATUS_POLICY.md when target has local recovery rules
  - AGENTS.md when target has project-specific stop conditions
  - docs/INSTALL_SURFACE.md when target adoption model differs
never_overwrite:
  - docs/handoff/CURRENT_STATUS.md
  - docs/DOCUMENT_MAP.md
  - docs/DOCUMENT_REGISTRY.md
  - docs/bootstrap/00_project_brief.md
  - docs/bootstrap/01_physical_boundaries.md
  - docs/bootstrap/02_storage_roots.md
  - docs/bootstrap/03_tech_stack.md
  - agent/agent_rules.yaml unless created from target template in a dedicated issue
  - target repository LICENSE without explicit license decision
```

### 4. Check Compatibility

Before proposing a patch, check whether the target validator and templates are
compatible.

```yaml
compatibility_questions:
  - Does target `scripts/asgk.py` support the fields used by the new template?
  - Does `python3 scripts/asgk.py doctor` pass before the upgrade?
  - Does target CI run the same checks as the source ASGK version?
  - Are policy-gate or current-status-impact fields understood by target tooling?
  - Would a template update make target PRs fail existing CI?
```

If validator, workflow, schema, or required field compatibility is unclear, split
the upgrade into a tooling issue before changing templates or skills.

### 5. Produce A Bounded Upgrade Issue

Draft a target-repository issue instead of editing files directly unless the user
has already supplied a durable issue.

The issue should include:

```yaml
upgrade_issue_fields:
  objective:
  durable_source_of_truth:
  source_asgk_version_or_commit:
  detected_target_state:
  allowed_paths:
  expected_output:
  non_goals:
  validation:
  stop_conditions:
  rollback_expectations:
```

## Output Format

Return an audit report and issue draft.

```yaml
asgk_upgrade_audit:
  target_repository:
  source_asgk_reference:
  classification:
  detected_surfaces:
  missing_or_stale_surfaces:
  safe_update_candidates:
  manual_merge_required:
  never_overwrite:
  validator_compatibility:
  recommended_issue:
    title:
    allowed_paths:
    validation:
    stop_conditions:
  result: blocked | issue_ready | requires_human | target_install_audit_recommended
```

## Stop States

- `blocked`: target state is unavailable, validator compatibility is unclear, or required authority is missing.
- `requires_human`: license, release, package publication, public visibility, dependency, workflow, schema, or protected-path changes are involved.
- `target_install_audit_recommended`: target is partial or non-ASGK and should be audited for adoption before upgrade.
- `issue_ready`: a bounded upgrade issue can be created.

## Split-Issue Triggers

Open a separate issue instead of mixing concerns when the upgrade requires:

- `scripts/asgk.py` validator behavior changes;
- GitHub Actions or CI workflow changes;
- schema or contract changes;
- dependency changes;
- release execution, tag, package publication, or public visibility changes;
- license changes or replacing the target repository `LICENSE`;
- installer scaffold behavior;
- runtime-specific adapters or profiles.

## Common Scenarios

### Recent ASGK Repository

If the target is current and only needs a guidance update, propose a narrow issue
covering the affected reusable surfaces.

```yaml
allowed_paths_example:
  - .github/PULL_REQUEST_TEMPLATE.md
  - skills/asgk-post-merge-closeout/SKILL.md
  - skills/asgk-current-status-handoff/SKILL.md
```

### Older ASGK Repository Without Skills

Do not add the full skill pack automatically. Offer two paths:

```yaml
options:
  repository_reference_mode:
    action: "Keep skills out of the target repo; update policy/template guidance only."
  minimal_skill_adoption:
    action: "Add only the skills needed by the upgrade, in a dedicated issue."
```

### Heavily Customized Target Repository

Do not overwrite files. Produce a manual merge plan naming the section to update
and the target-owned sections to preserve.

### Stale Target CURRENT_STATUS

Do not use upgrade work to hide stale state. Recommend a bounded current-status
refresh issue first if stale status would mislead the next session.

## Exit Artifact

A concise audit report plus a bounded GitHub issue draft, including `safe_update_candidates`, `manual_merge_required`, and `never_overwrite`. Do not perform file updates unless the target repository already has a durable issue authorizing the specific allowed paths.
