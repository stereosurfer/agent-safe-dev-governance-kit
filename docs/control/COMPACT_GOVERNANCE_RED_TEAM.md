# Compact Governance Red-Team Surface

Status: opt-in red-team validation surface. Compact governance is not enabled
as a default operating profile by this document.

Decision source: GitHub issue #225.

## Purpose

Compact governance should reduce repeated prose only after ASGK can prove that
shorter artifacts do not create a merge or scope gap. This red-team surface
models that migration before any default PR template, issue template,
`AGENTS.md`, or low-risk merge rule changes.

The target direction is:

```text
one complete issue scope -> captured scope lock -> tool-derived PR report -> compact handoff state
```

The red-team rule is stricter:

```text
agent-authored claims must never override tool-derived state
```

## Non-Default Boundary

This work does not authorize:

- reference-first PR bodies as the default;
- delta-only task packets as the default;
- compact handoff as the default;
- removal of Merge Decision Record or Current Status Impact sections;
- low-risk merge inference from compact artifacts;
- human-gate approval by agent-authored prose.

Any later compact-governance implementation must be a separate issue-backed
work unit.

## Modeled Objects

```yaml
issue_scope:
  role: "The single full task scope."
  required_tool_state:
    - allowed_paths
    - scope_hash_or_lock_equivalent

scope_lock:
  role: "A captured view of the issue scope used by the PR."
  must_block_when:
    - issue scope changed after capture

pr_state:
  role: "Tool-derived PR and CI metadata."
  required_tool_state:
    - changed_paths
    - ci_status
    - current_status_changed
    - current_status_impact
    - restricted_boundaries
    - metadata_available

task_packet:
  role: "Optional execution capsule."
  invariant: "May narrow issue scope, never expand it."

agent_claims:
  role: "PR prose or chat-authored claims."
  invariant: "Cannot create merge eligibility."
```

## Red-Team Hazards

The opt-in checker covers these hazards:

1. PR changed paths exceed issue `allowed_paths`.
2. Issue scope changes after the PR captured a scope lock.
3. Task packet adds allowed paths not present in the source issue.
4. Agent-authored gate claims conflict with tool-derived blocking state.
5. CI is pending while prose implies merge eligibility.
6. `CURRENT_STATUS.md` changed while Current Status Impact says
   `not_applicable`.
7. Restricted governance or human-gated boundaries require human review.
8. GitHub or PR metadata is unavailable and the compact check fails closed.

## Checker

Run the red-team fixtures with:

```bash
python3 scripts/asgk.py negative compact-governance
```

The command runs `scripts/compact_governance_red_team_check.py`, which evaluates
positive and negative JSON fixtures. The checker exits successfully only when
each fixture produces its expected result.

Expected fixture results:

```yaml
pass: "Tool-derived state is internally consistent."
blocked: "A checkable gate, such as CI, is not complete."
fail: "Scope, lock, status-impact, or self-attested-claim conflict exists."
fail_closed: "Required GitHub/PR metadata is unavailable."
requires_human: "A restricted or human-gated boundary is detected."
```

## Migration Guardrails

Before compact governance can become default, ASGK needs a later issue that
turns these modeled states into live validators:

- canonical issue scope extraction;
- scope lock capture and comparison;
- changed-path comparison against issue `allowed_paths`;
- task-packet narrowing check against issue scope;
- PR compiled report generation from live PR/CI metadata;
- fail-closed behavior when GitHub metadata is unavailable;
- explicit `requires_human` state for restricted boundaries;
- compact PR/handoff templates that reference the compiled report instead of
  restating unchanged scope.

Until those validators exist, verbose PR bodies remain the safer default.

## Canonical Issue Scope Primitive

The first dependency is a canonical issue scope object:

```bash
python3 scripts/asgk.py compact-issue-scope --issue <number> --json
python3 scripts/asgk.py compact-issue-scope --json-file examples/compact_governance/issue_scope.valid-issue.json --json
```

The command compiles the issue fields already required by issue-first work into
a stable `canonical_issue_scope` object. It normalizes `allowed_paths`, reports
missing material fields as findings, and always emits `low_risk_inferred:
false`.

This object is not a task packet, PR report, merge decision, or handoff. Later
compact-governance work may reference it, hash it, or compare it to live issue
state, but it does not replace the GitHub issue as the source of task authority.

## Scope Lock Primitive

The scope-lock primitive is also opt-in:

```bash
python3 scripts/asgk.py compact-scope-lock --issue <number> --json
python3 scripts/asgk.py compact-scope-lock --json-file examples/compact_governance/scope_lock.valid-issue.json --json
```

The command extracts the required task fields already used by `work-unit-check`,
normalizes `allowed_paths`, and emits a deterministic `scope_hash`.

This scope lock is not a merge decision. It does not make a PR low risk and
does not let a task packet expand issue scope. Later compact-report work must
compare a PR's captured scope lock to the live issue scope and fail when the
hash changes.
