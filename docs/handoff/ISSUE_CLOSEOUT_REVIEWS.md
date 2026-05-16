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

## 2026-05-17 - Issue #273 - Backfill Closeout Review Entry For Issue 269

```yaml
issue_closeout_review:
  issue: "#273"
  status: completed
  scope_summary: "Backfill the missing mandatory closeout review entry for issue #269 and include this issue's self-entry."
  prs_in_scope:
    - pr: "#274"
      role: "Adds bounded decision-analysis entries for issues #269 and #273 only."

  decision_analysis:
    decision_made: "Use one bounded follow-up issue to add the #269 entry and the #273 self-entry in the same ledger-only PR."
    why_this_path: "Issue #269 closed before the mandatory-entry rule reached main, and adding only #269 would create a recursive missing-entry gap for #273."
    rejected_paths:
      - path: "Only add the #269 entry."
        reason: "That would leave #273 without its own mandatory closeout review entry after merge."
      - path: "Reopen or rewrite issue #269."
        reason: "Issue #269 and PR #270 are already completed; the gap is closeout evidence, not implementation scope."
      - path: "Start a broad historical closeout backfill."
        reason: "Issue #271 explicitly did not authorize broad historical backfill."
    reusable_signal:
      applies_later: true
      reason: "Closeout-review repair issues should include their own entry when the ledger is already in scope."

  decisions:
    - decision: "Treat closeout-review backfill as a ledger-only follow-up."
      reason: "The implementation evidence already lives in issue #269 and PR #270; only the mandatory decision-analysis ledger was missing."
      reusable_rule: "If a missing closeout review entry is discovered after merge, open a bounded issue that allows only the ledger path."
      applies_when:
        - "A completed issue lacks its mandatory Issue Closeout Review entry."
        - "The missing entry can be repaired without changing the original implementation files."
      does_not_apply_when:
        - "The original implementation evidence is disputed or unavailable."
        - "Repair requires changing policy, validators, or historical evidence files."
      evidence:
        - "#269"
        - "#270"
        - "#271"
        - "#272"
        - "#273"

  avoidable_repeated_errors:
    - error: "Creating a closeout-review repair issue that omits its own closeout review entry."
      prevention: "When the ledger path is in scope, include the repair issue's self-entry before opening the PR."
      evidence:
        - "#273"

  future_agent_hints:
    - "For ledger repair issues, add both the repaired issue entry and the repair issue's self-entry when both are known."
    - "Do not use this pattern to start broad historical backfill without an explicit issue."

  promotion_candidates:
    capability_constraints:
      - none
    control_policy_updates:
      - none
    validator_updates:
      - none

  known_limits:
    - "This does not backfill older closed issues beyond #269."
    - "This does not change the #269/#270 implementation, merge result, or historical evidence files."
```

## 2026-05-17 - Issue #269 - Archive Early V1 Readiness And Stabilization Surfaces

```yaml
issue_closeout_review:
  issue: "#269"
  status: completed
  scope_summary: "Early v1 readiness and stabilization surfaces were archived as historical evidence instead of active policy."
  prs_in_scope:
    - pr: "#270"
      role: "Renamed active-looking V1 readiness/stabilization documents into historical ASGK evidence records and updated routing/target-install references."

  decision_analysis:
    decision_made: "Replace active-looking early V1 planning/audit documents with clearly historical ASGK evidence records."
    why_this_path: "The old filenames and active-state wording could mislead agents or target repos into treating pre-v1 readiness material as current policy after ASGK v1.6.0."
    rejected_paths:
      - path: "Keep the original V1 filenames and only edit wording."
        reason: "The filenames themselves still looked like active pre-release planning surfaces."
      - path: "Delete the historical evidence entirely."
        reason: "The detailed source remains useful as GitHub history and audit evidence."
      - path: "Invent a new archive system."
        reason: "The issue only needed current-surface cleanup, not a new repository authority layer."
    reusable_signal:
      applies_later: true
      reason: "Historical governance material should be retained as evidence without remaining in active routing or target-install authority."

  decisions:
    - decision: "Keep compact historical evidence files with fixed source links, blob SHAs, line counts, and checksums."
      reason: "This preserves auditability while removing long stale planning text from the active repo surface."
      reusable_rule: "When retiring stale governance history, preserve a recoverable evidence pointer instead of leaving old active-looking control files in place."
      applies_when:
        - "A repo-local governance document is historically useful but no longer current policy."
        - "The full source remains available in GitHub history."
      does_not_apply_when:
        - "The file is still the current policy authority."
        - "The historical source contains private or sensitive material that should not remain linked."
      evidence:
        - "#269"
        - "#270"

  avoidable_repeated_errors:
    - error: "Letting old V1 planning filenames survive as current-looking target-install or release-policy guidance."
      prevention: "Route historical ASGK evidence through explicit historical names and keep target-install checks blocking repo-local ASGK evidence in target authority."
      evidence:
        - "#269"
        - "#270"

  future_agent_hints:
    - "Use current release policy for active authority; use HISTORICAL_ASGK_*_EVIDENCE only for audit or do-not-copy reasoning."
    - "Do not copy ASGK repo-local historical evidence files into target repositories as current governance policy."

  promotion_candidates:
    capability_constraints:
      - none
    control_policy_updates:
      - none
    validator_updates:
      - "Target-install validation continues blocking both legacy V1 readiness surfaces and renamed historical ASGK evidence surfaces in target authority."

  known_limits:
    - "This does not rewrite GitHub history or the original merged release evidence."
    - "This does not prove all future historical documents are named safely."
    - "This does not change the latest completed release identity."
```

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
