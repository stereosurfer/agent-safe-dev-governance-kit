# Current Status

This is the repository recovery snapshot. It is overwritten, not appended.
Completed-work history and decision detail belong in GitHub issues, PRs,
comments, releases, and merge commits.

Last updated: `2026-09-24T14:38:01Z`

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
Apache-2.0 license. Issue #372 coordinates the active ASGK 3.0 release program.
The root README states the 3.0 product meaning; bounded root navigation,
control-source, GitHub workflow CLI, and optional metadata-only catalog CLI
cutovers are represented in current source. Both public namespaces use root
library owners and `doctor` runs their regression checks. The root target
templates are optional; Stage 3 examples are reviewed, not live-work proof.
Eleven `v3/` Skills remain candidates. Resolve live refs before claiming more;
#323 is prior 2.0 evidence, not the next-work router.

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

Superseded planning material is not current product authority. Completed source
work and its accepted or rejected decisions are indexed from #372 and child
issue close-outs, not repeated in this recovery snapshot.

## Active work

```yaml
issue: "#372 ASGK 3.0 source-only release program"
pr: none
branch: main
state: active_program
next_work_unit_decision: "Reconcile live #372 child and PR state; choose one unfinished, exact-scope 3.0 work unit. Eleven source Skills still need cutover before field tests, target pilot and release."
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

Continue under #372 from current `main`; inspect live PRs and child issues
before selecting one bounded unit. All eleven source Skills still need
evidence-backed 3.0 cutover, then cold handoff, GitHub/Kanban, target-fit and
release proof. The selected issue or PR supplies allowed paths and checks;
status, unpromoted `v3/` material, old plans and chat do not. Do not read the
excluded visual guide.

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
