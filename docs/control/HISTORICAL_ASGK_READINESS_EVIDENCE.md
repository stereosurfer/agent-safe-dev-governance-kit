# Historical ASGK Readiness Evidence

Status: archived ASGK evidence. Not active release policy, not current
readiness authority, and not target-project state.

This file preserves a compact record of the readiness evidence used before
ASGK's first source-only release. It is deliberately historical. Current
source-only release rules live in `docs/control/SOURCE_ONLY_RELEASE_POLICY.md`.
Readiness audits for output, API, import, publication, or external-call work
use `docs/bootstrap/17_readiness_audit_policy.md`.

Target repositories must not copy this file as project authority.

## Full Pre-Archive Source

The full deleted source remains in GitHub history at a fixed commit:

```yaml
pre_archive_source:
  path: docs/control/V1_READINESS_AUDIT.md
  commit: c18a536cc795320a8ea8979ce155304551740dc1
  github_blob: https://github.com/stereosurfer/agent-safe-dev-governance-kit/blob/c18a536cc795320a8ea8979ce155304551740dc1/docs/control/V1_READINESS_AUDIT.md
  github_blob_sha: e4b2e85043e2554d6d7901624809948ea14411b9
  line_count: 495
  sha256: 5d8ecbf5fedbf8741797357f96f6be2d81ae2bfb4e7e6c17dddc110ec496a73b
```

## Evidence Boundary

```yaml
historical_readiness_scope:
  records: completed ASGK source-only v1 readiness evidence
  does_not_authorize:
    - current release execution
    - package publication
    - external distribution beyond approved source-only releases
    - target repository readiness
    - runtime-specific adapters
    - provider or model calls
  current_policy_surfaces:
    source_only_release_policy: docs/control/SOURCE_ONLY_RELEASE_POLICY.md
    general_readiness_policy: docs/bootstrap/17_readiness_audit_policy.md
    target_adoption: docs/INSTALL_SURFACE.md
    current_status: docs/handoff/CURRENT_STATUS.md
```

## Historical Readiness Result

```yaml
historical_result:
  source_only_v1_0_release:
    status: completed
    execution_issue: "#130"
    tag_name: v1.0.0
    target_commit: "7d2e364c4c53d1296c7ce1c2d241291837d54c61"
    release_url: https://github.com/stereosurfer/agent-safe-dev-governance-kit/releases/tag/v1.0.0
  selected_license:
    issue: "#124"
    value: Apache-2.0
  selected_distribution_path:
    issue: "#124"
    value: source_only_github_release
```

## Historical Evidence Sources

```yaml
evidence_sources:
  vertical_governance_completion: "#102 / PR #103"
  real_world_field_test: "#112 / PR #113"
  field_test_readiness_closeout: "#114 / PR #115"
  source_only_release_policy_creation: "#116 / PR #117"
  current_status_closeout: "#118 / PR #119"
  final_readiness_review: "#120 / PR #121"
  license_and_distribution_path: "#124"
  first_source_only_release_execution: "#130"
```

## Historical Capability Snapshot

```yaml
historical_capability_snapshot:
  governance_core: ready_for_source_only_v1_at_time_of_release
  pr_validation: ready_for_generic_core_at_time_of_release
  negative_defense_tests: ready_for_core_cases_at_time_of_release
  handoff_recovery: ready_for_generic_handoff_at_time_of_release
  current_status_control: ready_for_source_only_v1_at_time_of_release
  cli_entrypoint: ready_as_minimal_wrapper_at_time_of_release
  parser_robustness: sufficient_for_source_only_v1_at_time_of_release
  target_install_surface: read_only_check_and_plan_available
  runtime_specific_adapters: deferred
  package_publication: not_authorized
```

## Preserved Limits

```yaml
preserved_limits:
  - historical evidence does not prove current release readiness
  - historical evidence does not make target repositories ready
  - historical evidence does not authorize package publication
  - historical evidence does not authorize runtime-specific adapters
  - historical evidence does not replace current issue, PR, CI, or release-policy checks
```

## Maintenance Rule

Do not use this file as a living readiness checklist. New readiness decisions
belong in the current issue or PR, with current policy and validation evidence.
