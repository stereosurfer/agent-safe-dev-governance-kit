---
name: asgk-governance-health-check
description: Audit repository governance only when explicitly scoped or scheduled; distinguish current blockers from historical observations.
---

# Governance health check

Use for an explicitly requested/scheduled periodic, milestone or repo-wide audit.
A merged PR or ordinary closeout prompt is not authorization for a full health scan.

Begin with the scoped open PRs/issues and repo recovery. Run the actual repository's
validation entrypoint; source doctor is not a universal target gate. Sample only the
authorized time/issue set for MDR, head-specific evidence, closeout and release residue.
Use closeout search/trace before reading whole code histories.

Classify current blockers separately from legacy observations. Missing historical
reviews, optional upgrades or source-shape differences do not create repair work.
Recommend a bounded follow-up only with the evidence and reason; do not implement it
under audit authority.

Return healthy, watch or blocked with exact evidence and limits. Do not infer that a
sample proves the entire repo healthy or that a green validator proves semantic safety.
