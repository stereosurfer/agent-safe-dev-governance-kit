# Historical ASGK Stabilization Evidence

Status: archived ASGK evidence. Not active policy, not target-project
readiness, and not a release gate.

This file preserves the compact evidence that ASGK's early stabilization work
was completed before the first source-only release line. It exists only for
repo-local audit and archaeology. Current release behavior is governed by
`docs/control/SOURCE_ONLY_RELEASE_POLICY.md`; target adoption behavior is
governed by `docs/INSTALL_SURFACE.md` and the target-install validators.

Target repositories must not copy this file as project authority.

## Full Pre-Archive Source

The full deleted source remains in GitHub history at a fixed commit:

```yaml
pre_archive_source:
  path: docs/control/V1_1_STABILIZATION_PLAN.md
  commit: c18a536cc795320a8ea8979ce155304551740dc1
  github_blob: https://github.com/stereosurfer/agent-safe-dev-governance-kit/blob/c18a536cc795320a8ea8979ce155304551740dc1/docs/control/V1_1_STABILIZATION_PLAN.md
  github_blob_sha: 5a6c89fb2d151b72eaf9fbc52399e36e55bb70f3
  line_count: 334
  sha256: 8cd89a95bf8743aa2e04c0902adddebd3a96ab0a9fdce1db3358171e8990fa59
```

## Evidence Boundary

```yaml
historical_evidence_scope:
  records: completed early ASGK stabilization sequence
  does_not_authorize:
    - release execution
    - package publication
    - target repository readiness
    - installer scaffold work
    - runtime-specific adapters
    - current milestone status
  current_policy_surfaces:
    release_policy: docs/control/SOURCE_ONLY_RELEASE_POLICY.md
    target_adoption: docs/INSTALL_SURFACE.md
    target_install_check: docs/control/TARGET_INSTALL_VALIDATION_PLAN.md
    current_status: docs/handoff/CURRENT_STATUS.md
```

## Historical Completion Summary

```yaml
early_stabilization_sequence:
  parser_hardening_without_dependencies:
    status: completed_or_sufficient_for_source_only_v1
  current_status_check:
    status: completed
  positive_handoff_template_fixture:
    status: completed
  uncontrolled_document_audit:
    status: completed
    evidence: docs/control/UNCONTROLLED_DOCUMENT_AUDIT.md
  document_navigation_split:
    status: completed
  target_install_read_only_surfaces:
    status: completed
    evidence:
      - docs/INSTALL_SURFACE.md
      - docs/control/TARGET_INSTALL_CHECKLIST.md
      - docs/control/TARGET_INSTALL_VALIDATION_PLAN.md
      - scripts/asgk.py target-install-check
      - scripts/target_install_plan.py
  vertical_governance_thin_layer:
    status: completed
    sources:
      initial_layer: "#88 / PR #89"
      decision_exercise: "#100 / PR #101"
      closeout: "#102 / PR #103"
  real_world_field_test:
    status: completed
    sources:
      implementation: "#112 / PR #113"
      readiness_closeout: "#114 / PR #115"
```

## Field-Test Lessons Preserved

```yaml
field_test_lessons:
  - ASGK managed a bounded tooling/validation change through durable issue authority, branch, PR, validation evidence, merge decision, merge, and closeout.
  - Decision-packet-shaped evidence was useful for recording source, limits, forbidden actions, rollback, and human-gate status.
  - Opt-in negative command flow was safer before default CI wiring.
  - Implementation evidence and readiness closeout should remain separate steps.
```

## Historical Limits

```yaml
historical_limits:
  - did not prove target installation in a real external repository
  - did not add installer scaffold or target repository writes
  - did not authorize package publication
  - did not authorize runtime-specific adapters
```

## Maintenance Rule

Do not append new milestone history here. New work belongs in GitHub issues,
PRs, comments, releases, tags, merge commits, or a current policy surface named
by the issue.
