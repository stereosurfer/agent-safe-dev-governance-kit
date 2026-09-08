---
name: asgk-current-status-handoff
description: Distinguish repo recovery from per-run interrupted handoff; preserve compact CURRENT_STATUS and GitHub-owned work history.
---

# Current status and handoff

CURRENT_STATUS is the repo recovery snapshot, never a work ledger. Its canonical policy
remains the source repository's docs/control/CURRENT_STATUS_POLICY.md or target equivalent.

Per-run interruption belongs in the current issue/PR comment: actor, role, run, branch,
base/head, input scope, actual changes, validation source/limits, decisions, incomplete
work and next action. A receiver recompiles against current authority; unknown results
remain unknown. Dirty or partially evidenced work may be handed off as blocked instead
of inventing completion.

For repo status, ask whether leaving the snapshot unchanged would mislead the next
session after merge. Choose updated, not_applicable or a justified deferred follow-up.
Keep it post-merge-safe. Do not repeat each worker event or closeout there.

Record the disposition in the existing PR/issue. Do not create unrelated status repairs
or expand into whole-repo health checking. No packet or handoff transfers human approval.
