# Compact Target Upgrade Profile

Status: opt-in profile. This file does not make compact governance default in
ASGK or in any target repository.

The compact target-upgrade profile describes how an existing ASGK-adopted
repository may plan an upgrade to compact governance surfaces without
overwriting target-owned state.

## Core Rule

```text
Plan the upgrade; do not reinstall ASGK and do not copy ASGK repo-local state.
```

Target repositories own their own recovery state, document navigation, project
bootstrap docs, and license policy. Compact governance updates must be merged
into those surfaces through a bounded target-repository issue or PR.

## Manifest Shape

```json
{
  "version": "asgk.compact_target_upgrade.v1",
  "target_repository": "owner/repo",
  "source_asgk_reference": "commit-or-tag",
  "classification": "recent_asgk",
  "upgrade_mode": "audit_and_plan",
  "target_repository_writes_performed": false,
  "durable_upgrade_issue_required": true,
  "compact_governance": {
    "default_enabled": false
  },
  "license_notice_handling": {
    "asgk_apache_2_notice_preserved": true,
    "target_license_replaced": false,
    "notice_surface": "LICENSE or NOTICE"
  },
  "target_owned_state": {
    "preserved": [],
    "overwritten_paths": []
  },
  "surface_plan": {
    "copy_as_is": [],
    "manual_merge_required": [],
    "never_overwrite": []
  },
  "validation": {
    "commands": []
  },
  "human_gates": []
}
```

## Checker

Run:

```bash
python3 scripts/asgk.py compact-target-upgrade-check \
  --manifest examples/compact_governance/target_upgrade/manifest.valid.json
```

The checker blocks manifests that enable compact governance by default, replace
target license surfaces, omit license notice handling, perform target writes, or
copy target-owned files such as `docs/handoff/CURRENT_STATUS.md` as-is. It
always reports `low_risk_inferred: false`.

## Never Overwrite

The checker treats these as target-owned upgrade boundaries:

```yaml
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

These may be manually merged or freshly created in a target-repository issue,
but they must not be copied as ASGK source-repo truth.
