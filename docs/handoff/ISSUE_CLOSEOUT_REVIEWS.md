# Issue Closeout Reviews

Status: mandatory issue-level decision-analysis ledger.

This file centralizes bounded decision analysis, reusable decisions, pitfalls,
and prevention notes that would otherwise be scattered across many GitHub issue
comments.

It is not part of the default startup set. Read it during issue closeout,
governance health checks, upgrade audits, closeout review, or similar prior-work
lookup.

## Authority Boundary

```yaml
authority_boundary: "This review ledger is mandatory closeout evidence, but it does not override AGENTS.md, the current GitHub issue or PR, validators, control policies, merge decisions, CURRENT_STATUS.md, or human gates."
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

## Required Entry Rule

Every issue closeout must add one bounded decision-analysis entry to this file.
Do not decide whether a closeout is important enough to record. Capture the
decision-analysis material first; future decision-tree or policy work can
downselect later.

Bounded means scope-limited and evidence-dense. It does not mean abbreviated,
lossy, simplified, or summary-only. Do not omit decision reasons, rejected paths,
applicability boundaries, evidence links, or known limits to make an entry
shorter.

```yaml
required_for:
  - completed issue
  - duplicate issue
  - superseded issue
  - abandoned or closed-not-done issue
  - blocked issue closeout
  - release, milestone, validation, docs/control, script, or human-gated issue
```

If the ledger is not in the current issue's allowed paths, do not edit it
silently. Open or use a bounded closeout-review issue or PR. The original issue
is not fully closed out until the ledger entry exists.

GitHub issue comments still own closeout facts: merge result, validation
evidence, issue state, and links. This file owns the bounded decision-analysis
record for later reuse.

## Entry Limits

```yaml
limits:
  max_decisions: 5
  max_avoidable_errors: 5
  max_future_agent_hints: 5
  max_total_words: 800
  release_train_exception: "May exceed limits only when the issue spans multiple PRs and the entry remains evidence-linked."
  quality_floor: "Preserve decision reasons, rejected paths, applicability boundaries, evidence links, and known limits even when the issue is routine."
```

Do not write generic reflection such as "be more careful" or "this was
important." Every lesson must name a concrete decision, prevention, scope
condition, and evidence link. Do not replace the decision analysis with a short
summary.

## Entry Template

Use newest entries first.

````md
## YYYY-MM-DD - Issue #NNN - Short Title

```yaml
issue_closeout_review:
  issue: "#NNN"
  status: completed | closed_not_done | duplicate | superseded | blocked
  scope_summary: "One-sentence issue result."
  prs_in_scope:
    - pr: "#NNN"
      role: "What this PR contributed."

  decision_analysis:
    decision_made: "The final closeout decision."
    why_this_path: "Why this path was chosen."
    rejected_paths:
      - path: "Alternative considered."
        reason: "Why it was not chosen."
    reusable_signal:
      applies_later: true
      reason: "Why this entry may help future decision-tree or policy extraction."

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

## 2026-05-17 - Issue #271 - Mandatory Closeout Review Entries

```yaml
issue_closeout_review:
  issue: "#271"
  status: completed
  scope_summary: "Closeout review entries are mandatory for every ASGK issue closeout."
  prs_in_scope:
    - pr: "#272"
      role: "Updates the existing closeout review ledger rules, post-merge closeout skill, quickstart guidance, and closeout-check validation."

  decision_analysis:
    decision_made: "Use the existing ISSUE_CLOSEOUT_REVIEWS.md ledger as the required bounded decision-analysis record for every issue closeout."
    why_this_path: "The repo already had the correct ledger and template; the gap was conditional guidance and missing enforcement."
    rejected_paths:
      - path: "Keep entries conditional."
        reason: "Conditional entry rules lose raw decision material needed for later decision-tree extraction."
      - path: "Create a new closeout-analysis format."
        reason: "A second format would duplicate the existing ledger and add another judgment point."
    reusable_signal:
      applies_later: true
      reason: "Future closeout and decision-tree work should capture first, then downselect later."

  decisions:
    - decision: "Remove optional/no-entry closeout review paths."
      reason: "The user wants no judgment step about whether an issue deserves decision analysis."
      reusable_rule: "Every issue closeout gets one bounded decision-analysis ledger entry."
      applies_when:
        - "Any ASGK issue is being closed or marked completed, superseded, duplicate, blocked, or closed-not-done."
      does_not_apply_when:
        - "No ASGK issue is being closed."
      evidence:
        - "#271"

  avoidable_repeated_errors:
    - error: "Treating a guidance file as enforceable without a validator."
      prevention: "Run closeout-check with an issue closeout review ledger path and completed issue."
      evidence:
        - "#271"

  future_agent_hints:
    - "Do not decide whether to write an Issue Closeout Review; write one bounded decision-analysis entry."
    - "Keep GitHub issue comments as factual closeout evidence and this file as bounded decision analysis."

  promotion_candidates:
    capability_constraints:
      - none
    control_policy_updates:
      - "Consider adding closeout-check to post-merge closeout scripts if future automation needs stronger enforcement."
    validator_updates:
      - "closeout-check now fails when a completed issue lacks a matching issue closeout review entry."

  known_limits:
    - "This does not backfill historical issue closeout reviews."
    - "This does not query GitHub state; closeout-check verifies caller-supplied issue markers against local files."
```
