---
name: asgk-issue-scoping
description: Guide controller-side issue scoping from user intent and actual repository evidence; workers only refine an existing issue.
---

# Issue scoping

GitHub owns the work contract. Use the canonical 13 fields and two execution gates from
the target repository's AGENTS; do not maintain another field list here. Source tools can
parse and compare those fields. A task packet is a derived refinement.

Inspect relevant current evidence before proposing allowed paths or acceptance. Preserve
objective, non-goals, forbidden actions, stop conditions and rollback in the durable issue.
A role/capability ceiling can narrow the task but cannot grant scope absent from the issue.
Choose the smallest sufficient context through canonical pointers; avoid whole-repo reads.

For adoption or upgrade, first use the appropriate target-owned assessment, allowing
minimum change or no change. No module menu, fixed bundle or semantic-judgment-only
human gate. Name an exact existing gate only when the proposed operation triggers it.

Record the scope in GitHub before implementation. Worker feedback may propose a narrower
scope or identify a gap; the controller resolves it durably before expansion. Preserve
the existing verified-outage exception without inventing a snapshot-as-authority shortcut.

Return issue URL, scope, evidence boundary and next action. Do not infer merge,
publication, global Skill synchronization or external permissions.
