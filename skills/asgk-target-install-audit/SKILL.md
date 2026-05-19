---
name: asgk-target-install-audit
description: Use when evaluating or transferring ASGK into another repository; audits target-install readiness, copy/template/customize boundaries, license handling, and do-not-copy-as-is risks.
---

# ASGK Target Install Audit

Use this skill before adopting ASGK into a target repository or when checking whether an adoption is structurally ready.

## Authority

The target repository must own its own governance state. Do not copy ASGK repo-local status, readiness audits, document maps, or internal history as target authority.

Install safety is not install completeness. A plan that avoids copying protected
state is still incomplete if copied, templated, or customized references point to
missing target paths or source-only ASGK files.

## Minimum Reads

- `docs/INSTALL_SURFACE.md`
- `docs/control/TARGET_INSTALL_CHECKLIST.md`
- `docs/control/TARGET_INSTALL_VALIDATION_PLAN.md` when validator behavior matters
- Target repository file tree

## Procedure

1. Identify target repo root and existing governance files.
2. Run `python3 scripts/asgk.py target-install-check --repo-root <target>` when available.
3. Run `python3 scripts/asgk.py target-install-plan --repo-root <target>` when available to inspect the read-only copy/template/customize/do-not-copy plan. Treat planner output as adoption evidence, not approval authority.
4. Classify files as:
   - copy as-is
   - template then customize
   - customize required
   - do not copy as-is
   - deferred v2
5. Check that planned target paths exist, or are explicitly marked as files to
   create, customize, defer, or intentionally omit.
6. Scan planned copied/customized surfaces for stale source-only references,
   donor repo-local document names, and bootstrap paths that do not exist in the
   target repository.
7. Check Apache-2.0 notice handling for copied or adapted ASGK material.
8. Flag ASGK repo-local files copied into target authority.
9. Produce an adoption readiness report and, if asked, a bounded adoption issue plan.

## Stop States

- `blocked`: target repo lacks required governance surface or has copied ASGK internal state as authority.
- `blocked`: planned install references target paths that are missing without an explicit create/customize/defer/omit decision.
- `requires_human`: licensing, visibility, security, or protected-path decisions are needed.
- `ready_for_adoption_pr`: missing and risky items are bounded enough for an adoption PR.

## Exit Artifact

Target-install readiness report with missing files, risky files, path-existence
decisions, stale source-reference findings, license/notice handling, and next
adoption issue or PR plan.
