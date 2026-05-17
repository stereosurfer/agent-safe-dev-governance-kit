# Uncontrolled Document Audit

Status: active audit record.

This audit classifies status-like, log-like, and reference documents that could
otherwise drift into uncontrolled history logs. It was opened from ASGK's
historical stabilization evidence and remains a compact active audit record.

## Scope

```yaml
audit_scope:
  source: docs/control/HISTORICAL_ASGK_STABILIZATION_EVIDENCE.md
  candidate_docs:
    - docs/handoff/AGENT_LOG.md
    - docs/handoff/DECISIONS.md
    - docs/bootstrap/12_productization_notes.md
    - docs/EVOLUTION_MODEL.md
  non_goals:
    - rewrite large documents
    - add validation tooling
    - change schemas
    - perform release preparation
    - perform real-world field testing
```

## Classification Vocabulary

```yaml
classifications:
  current_snapshot: overwrite-oriented current state surface
  durable_decision_log: append-allowed decision record with compact entries
  append_allowed: append is allowed, but entries should be compact links or records
  compact_policy_needed: document needs explicit size/staleness boundaries
  reference_only: stable explanatory/reference document, not a status log
```

## Audit Results

| Document | Classification | Growth risk | Required action |
|---|---|---:|---|
| `docs/handoff/AGENT_LOG.md` | `append_allowed` | medium | Add compact append boundary; prefer links to GitHub reports over copied reports. |
| `docs/handoff/DECISIONS.md` | `durable_decision_log` | medium | Add decision-entry boundary; append concise durable decisions only. |
| `docs/bootstrap/12_productization_notes.md` | `reference_only` | low | Add reference-only boundary; do not append roadmap/status history. |
| `docs/EVOLUTION_MODEL.md` | `compact_policy_needed` | medium | Add maturity-snapshot boundary; update through bounded audit PRs only. |

## Rationale

### `docs/handoff/AGENT_LOG.md`

This file is explicitly append-oriented. That is acceptable only if entries stay
small and point to durable GitHub issue or PR comments. Full agent reports should
not be copied into this file by default, because that would duplicate history and
inflate startup/handoff context.

### `docs/handoff/DECISIONS.md`

This file is a durable decision log, so append is expected. The risk is not
append itself; the risk is using it as a discussion transcript. Entries should be
short, decision-oriented, and link to the issue or PR that contains the full
rationale.

### `docs/bootstrap/12_productization_notes.md`

This is a reference document for product positioning and boundary framing. It
should not become a release diary, roadmap queue, or status log. Productization
history and release history belong in GitHub issues, PRs, comments, releases,
tags, and merge commits. Repo policy documents may define boundaries, but they
must not become history ledgers.

### `docs/EVOLUTION_MODEL.md`

This document includes explanatory model content plus maturity snapshots. The
model portions are reference material. The maturity snapshot can go stale, so it
requires a clear update boundary: update only through bounded readiness or audit
work, and do not append chronological progress logs.

## Progressive Disclosure Rule

These documents must preserve progressive disclosure:

```yaml
progressive_disclosure:
  first_layer:
    purpose: compact orientation
    examples:
      - docs/handoff/CURRENT_STATUS.md
  second_layer:
    purpose: work-unit detail
    examples:
      - GitHub issue bodies
      - PR bodies
      - handoff packets
  third_layer:
    purpose: durable history
    examples:
      - issue comments
      - PR comments
      - merge commits
      - compact decision-log entries
```

Do not move third-layer history into first-layer status documents.

## Follow-up Guidance

```yaml
follow_up_guidance:
  add_tooling_now: false
  add_schema_now: false
  update_current_status_policy_now: false
  if_growth_recurs:
    - add targeted `asgk` checks for the specific document class
    - prefer link-only entries for append logs
    - split reference content from status content
```

## Acceptance Mapping

```yaml
acceptance:
  every_candidate_classified: true
  policy_added_only_where_needed: true
  large_docs_not_rewritten: true
  progressive_disclosure_preserved: true
```
