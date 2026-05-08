# Issue Closeout Reviews

Status: advisory issue-level closeout review ledger.

This file centralizes reusable decisions, pitfalls, and prevention notes that
would otherwise be scattered across many GitHub issue comments.

It is not part of the default startup set. Read it only when a current issue,
PR, health check, upgrade audit, closeout review, or similar prior-work pattern
requires reusable issue-level lessons.

## Authority Boundary

```yaml
authority_boundary: "This review ledger is advisory. It does not override AGENTS.md, the current GitHub issue or PR, validators, control policies, merge decisions, CURRENT_STATUS.md, or human gates."
```

Each entry should point back to durable evidence in GitHub issues, PRs,
comments, merge commits, repo files, or validation output. Do not use this file
as merge authority, task scope, acceptance criteria, or a substitute for PR
evidence.

## Placement

Use this ledger for issue-level learning that is broader than one PR body but
too reusable to leave only in scattered comments.

Keep related surfaces separate:

```yaml
surface_boundaries:
  pr_body: "What this PR changed, how it was validated, and whether it can merge."
  issue_closeout_comment: "Completion evidence and issue closure state."
  current_status: "Compact recovery state for the next session."
  decisions_log: "Durable architecture or governance decisions only."
  issue_closeout_reviews: "Reusable issue-level decisions, pitfalls, preventions, and promotion candidates."
```

## When To Add An Entry

Add one compact entry when the issue is closing and at least one condition is
true:

```yaml
required_when:
  - issue has more than one PR
  - issue is a release train or milestone closeout
  - issue changes validation behavior
  - issue changes docs/control/**
  - issue changes .github/**
  - issue changes scripts/**
  - issue includes human-gated authorization
  - issue had failed attempts or repeated correction loops
  - issue produced a reusable operational lesson
optional_when:
  - single small docs-only PR
  - typo or formatting issue
  - simple target-file update with no governance implication
not_needed_when:
  - issue is closed as duplicate
  - issue is abandoned without implementation
  - no reusable lesson exists
```

If the ledger is not in the current issue's allowed paths, do not edit it
silently. Record `no_ledger_update` in the issue closeout comment or open a
bounded follow-up issue when the review is genuinely useful.

## Entry Limits

```yaml
limits:
  max_decisions: 5
  max_avoidable_errors: 5
  max_future_agent_hints: 5
  max_total_words: 800
  release_train_exception: "May exceed limits only when the issue spans multiple PRs and the entry remains evidence-linked."
```

Do not write generic reflection such as "be more careful" or "this was
important." Every lesson must name a concrete decision, prevention, scope
condition, and evidence link.

## Entry Template

Use newest entries first.

````md
## YYYY-MM-DD - Issue #NNN - Short Title

```yaml
issue_closeout_review:
  issue: "#NNN"
  status: completed
  scope_summary: "One-sentence issue result."
  prs_in_scope:
    - pr: "#NNN"
      role: "What this PR contributed."

  decisions:
    - decision: "Concrete decision made."
      reason: "Why it was chosen."
      reusable_rule: "How to apply the decision next time."
      applies_when:
        - "Narrow condition where this lesson applies."
      does_not_apply_when:
        - "Boundary that prevents over-generalization."
      evidence:
        - "#NNN"
        - "#NNN"

  avoidable_repeated_errors:
    - error: "Observed mistake or near miss."
      prevention: "Specific check, file, or workflow that prevents it."
      evidence:
        - "#NNN"

  future_agent_hints:
    - "Short instruction that helps future agents avoid redoing the search."

  promotion_candidates:
    capability_constraints:
      - none
    control_policy_updates:
      - none
    validator_updates:
      - none

  known_limits:
    - "What this review does not prove or authorize."
```
````

## Reviews

No issue closeout reviews are recorded yet.
