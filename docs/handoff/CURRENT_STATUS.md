# Current Status

This is the repository recovery snapshot. It is overwritten, not appended.
Completed-work history and decision detail belong in GitHub issues, PRs,
comments, releases, and merge commits.

Last updated: `2026-08-04T16:00:00Z`

## Durable source of truth

- The selected live GitHub issue or qualifying PR is executable work-unit
  authority.
- Canonical repository documents define durable rules and ownership.
- Validators and CI provide bounded mechanical evidence; they do not approve,
  merge, release, or establish semantic truth.
- Chat memory and superseded planning material are not current authority.
- New sessions read `AGENTS.md`, `README.md`, this file, and the active issue or
  PR before expanding context through `docs/DOCUMENT_MAP.md`.

## Current snapshot

ASGK v1.7.3 remains the latest completed source-only GitHub release under the
Apache-2.0 license. ASGK 2.0 is an active document-driven evolution coordinated
by issue #323.

The product boundary is safe, smooth, traceable handoff between people and AI.
The handoff remains independent of a specific model, provider, agent, or prior
chat. People may replace the worker; the durable work unit tells the successor
what to do, where to do it, what not to do, what is forbidden, what evidence
exists, and what comes next.

The source contract has one 13-field work-unit identity and two execution gates.
Task packets can narrow an issue but cannot replace it. Retained JSON validators
use one evidence envelope with explicit checked and unchecked claims, stable
finding codes, human-gate state, and a proof boundary. `doctor`, `validate`, and
the negative suite use the retained scenario registry and source-validation
engine.

`target-evidence-check` checks only caller-supplied path and literal-text claims
against an arbitrary target layout. A matching claim never proves target fit,
governance depth, recommendation, approval, or readiness.

The W5 truth-layer owners now describe the current product meaning, the
document-driven self-evolution loop, this recovery snapshot, and canonical
document ownership. Superseded planning material is not current product
authority. The separate five-path authority-wording follow-up remains a
decision point in #323 and is not silently included here.

## Active work

```yaml
issue: "#323 ASGK 2.0 program"
pr: none
branch: main
state: active_program
latest_completed_work_unit: "W5 truth-layer replacement"
next_work_unit_decision: "#323 must record whether the separately scoped five-path authority-wording follow-up proceeds before W6."
```

## Current validation entrypoint

```bash
python3 scripts/asgk.py doctor
```

Additional focused checks:

- Source only: `python3 scripts/asgk.py validate`
- Exact registered scenarios: `python3 scripts/asgk.py negative all`
- PR body: `python3 scripts/pr_governance_preflight.py check --body-file <body-file>`
- PR readiness: `python3 scripts/asgk.py check-pr --pr <number>`
- Work-unit authority: `python3 scripts/asgk.py work-unit-check --issue <number> --authority-only --json`
- Work-unit diff: `python3 scripts/asgk.py work-unit-check --issue <number> --git-base origin/main --git-head HEAD --json`

## Closed gates

- prior chat, superseded planning material, or historical evidence as current
  task authority;
- automatic model/provider/agent selection, routing, switching, or price-tier
  dispatch;
- fixed target file shape, module picker, or adoption declaration as fit proof;
- validator success as semantic truth, human approval, release authority, or
  merge authority;
- cloud egress, API/model calls, MCP writes, dependencies, schema changes,
  publication, or visibility changes without their existing gates.

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files,
model cache, or external preparation outputs are authorized by this status.

## Next safe action

Continue from current `main` using the approved #323 graph. First resolve the
explicit five-path authority-wording decision point if it is required for W5
closure; otherwise create the next exact child issue from the current program
scope. Then proceed to W6 only from a fresh current-main scan and exact allowed
paths. Do not revive superseded planning material, reintroduce a runtime
adapter/routing model, or read the excluded visual guide.

```yaml
reference_scope:
  repo_local_router: docs/DOCUMENT_MAP.md
  source_ownership_inventory: docs/DOCUMENT_REGISTRY.md
rule:
  - read only the smallest current set
  - expand context through canonical pointers
  - keep plans, evidence, and decisions in durable issue, PR, and close-out state
  - do not copy ASGK's repo-local filenames into a target as a universal bundle
```
