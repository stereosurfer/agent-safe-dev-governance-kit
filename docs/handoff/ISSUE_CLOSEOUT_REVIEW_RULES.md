# Issue Closeout Review Rules

Status: mandatory issue-closeout decision-analysis writing rules.

This file defines how agents write bounded issue-closeout decision analysis in
GitHub issue closeout comments.

It is not part of the default startup set. Read it when writing or auditing an
issue closeout comment, governance health check, upgrade audit, or similar
prior-work lookup.

## Authority Boundary

```yaml
authority_boundary: "These writing rules shape issue closeout comments, but they do not override AGENTS.md, the current GitHub issue or PR, validators, control policies, merge decisions, CURRENT_STATUS.md, or human gates."
```

Each issue closeout review should point back to durable evidence in GitHub
issues, PRs, comments, merge commits, repo files, or validation output. Do not
use this file as merge authority, task scope, acceptance criteria, a history
ledger, or a substitute for PR evidence.

## Placement

Use these rules when an issue closeout needs decision analysis that is broader
than one PR body and reusable enough to help future agents avoid repeating the
same search or mistake.

Keep related surfaces separate:

```yaml
surface_boundaries:
  pr_body: "What this PR changed, how it was validated, and whether it can merge."
  issue_closeout_comment: "Completion evidence and issue closure state."
  current_status: "Compact recovery state for the next session."
  decisions_log: "Durable architecture or governance decisions only."
  issue_closeout_review_rules: "Rules for reusable issue-level decisions, pitfalls, preventions, and promotion candidates."
```

## Required Entry Rule

Every current issue closeout performed after PR #272 merged must include one
bounded decision-analysis block in the GitHub issue closeout comment. Do not
decide whether a current closeout is important enough to record. Capture the
decision-analysis material first; future decision-tree or policy work can
downselect later.

This rule is non-retroactive. Issues closed before PR #272 merged are not
missing work merely because they lack an Issue Closeout Review. A health
check may report a pre-rule gap as a legacy observation, but it must not turn
that observation into automatic repair work.

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

Do not edit this rules file for routine issue closeouts. Change it only when the
writing rule itself is wrong or incomplete and a durable issue authorizes the
rule change. Missing historical closeout reviews are observations, not repair
work.

GitHub issue comments still own closeout facts: merge result, validation
evidence, issue state, links, and the issue closeout review. This file owns only
the rules for writing that review.

## Review Limits

```yaml
limits:
  max_decisions: 5
  max_avoidable_errors: 5
  max_future_agent_hints: 5
  max_total_words: 400
  release_train_exception: "May exceed limits only when the issue spans multiple PRs and the entry remains evidence-linked."
  quality_floor: "Preserve decision reasons, rejected paths, applicability boundaries, evidence links, and known limits even when the issue is routine."
```

Do not write generic reflection such as "be more careful" or "this was
important." Every lesson must name a concrete decision, prevention, scope
condition, and evidence link. Do not replace the decision analysis with a short
summary.

## Review Template

Use this shape in the GitHub issue closeout comment when an issue is closed.

````md
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
