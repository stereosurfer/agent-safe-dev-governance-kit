---
name: asgk-pr-evidence-merge-decision
description: Prepare a GitHub PR body and current-head evidence using existing template and preflight; not needed by every task worker.
---

# PR evidence and merge decision

The PR owner uses the target's canonical template, issue authority and validation rules.
Workers provide concrete output, validation source/limits, decisions and unresolved work;
they do not each need the entire PR policy.

Keep the distinction between draft/ready lifecycle, body-coherence, strict merge-decision
and live check-pr. An ordinary review request is not merge approval. Begin incomplete
work with merge_blocked. A new head makes older evidence/review stale; do not copy
approval from an abandoned attempt.

Use evidence labels from the existing source Skill contract and name the exact command,
head, result, durable pointer and non-proof. A worker's pass is a reported claim until
verified at its stated boundary. Actor/role names do not prove reviewer independence.

Before any actual PR-body write, save the complete body locally and run the repository's
file-backed preflight. Candidate CLI evidence or handoff fragments are not complete PR
bodies and are not preflight-approved. Reuse existing validators, not copied boolean logic.

Resolve applicable human gates from durable exact-head evidence. Program execution
authorization is not owner review of the head. Keep known gaps and CURRENT_STATUS impact
explicit; update status only if repo recovery would otherwise mislead. Return the PR
evidence and next gate; do not merge merely because formatting passed.

For capability-promotion PRs, link the originating lessons/ledgers, before/after
behavioral tests, rejected alternatives, independent semantic review when material,
the exact Skill version and rollback. A Kanban review or completion receipt is one
evidence source, never a substitute for this PR's current-head policy decision.
