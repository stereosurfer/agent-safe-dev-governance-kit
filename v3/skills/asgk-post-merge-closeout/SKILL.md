---
name: asgk-post-merge-closeout
description: Close out a scoped GitHub work unit, including merged, abandoned, duplicate, superseded or blocked outcomes, with decision lineage.
---

# Issue closeout and decision lineage

GitHub issue comments own closeout; the canonical writing guide is
docs/handoff/ISSUE_CLOSEOUT_REVIEW_RULES.md in this source repository. Use target-owned
equivalents where present. Do not create a local permanent decision ledger.

For completed source work, verify merged PRs, merge commits, expected closing references,
issue acceptance, validation, review/MDR and actual issue state. For abandoned, duplicate,
superseded or blocked closure, preserve the corresponding reasons and durable relationship;
do not require or invent a successful merge.

Every current closeout retains material decisions, reasons, rejected paths, applicability
and non-applicability, evidence and known limits. Apply the canonical five-decision /
400-word bound without silently truncating reasoning. Link corrections and authorized
reverts in the right direction: supersedes differs from superseded_by. Keep failed
attempts, their branches and CI as evidence.

Search prior closeout comments before broad repo reading when investigating decisions.
Search results are historical evidence, not present authority. Missing legacy reviews
are observations, not automatic repair work.

Candidate closeout output is a draft. Actual posting/closure follows live issue authority
and existing gates; milestone closure remains separately gated. If required review or
evidence is missing, record the blocker instead of closing. Consider CURRENT_STATUS only
for misleading repo recovery. Remind about installed Skill drift when source Skills
changed; never synchronize globally without explicit request. Stop after this unit.
