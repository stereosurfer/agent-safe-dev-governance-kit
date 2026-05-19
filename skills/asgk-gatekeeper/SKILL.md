---
name: asgk-gatekeeper
description: Use when checking ASGK PR readiness with existing repo validators and GitHub metadata; reports blocked, eligible, or requires_human without approving merge or adding a new gate.
---

# ASGK Gatekeeper

Use this skill for PR readiness checks, CI follow-up, or pre-merge review.

## Authority

This skill selects and sequences existing checks. It must not create new approval authority. Use `blocked`, `eligible`, or `requires_human`; do not say `approved`.

## Minimum Inputs

- PR number.
- Issue number.
- Local branch state when relevant.
- Changed paths.

## Procedure

1. Confirm the PR is open and associated with the intended issue.
2. Confirm the PR is not draft when merge readiness is being assessed.
3. Run or inspect:
   - `python3 scripts/asgk.py doctor`
   - `python3 scripts/asgk.py check-pr --pr <number>`
   - PR CI status
   - `current-status-impact-check` when `docs/handoff/CURRENT_STATUS.md` changed
   - changed-path hygiene when local changed paths are available
4. Identify human-gated triggers from changed paths and issue scope.
5. Compare the PR's completion claim with the issue acceptance sheet. Named
   checks passing means only those checks passed; it does not prove semantic
   correctness, upgrade completeness, install completeness, or stale-reference
   cleanup unless the issue required and the PR records that evidence.
6. Report only the narrow readiness state.

## Stop States

- `blocked`: validator or CI failure exists, or issue-required completion evidence is missing.
- `requires_human`: human-gated trigger exists or semantic review is required.
- `eligible`: checkable gates pass and no human-gated trigger is detected; a human or policy still makes the merge decision.

## Exit Artifact

PR comment or final report listing checks, evidence source, blockers, and the next safe action.
