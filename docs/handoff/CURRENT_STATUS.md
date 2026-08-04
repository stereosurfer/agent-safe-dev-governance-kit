# Current Status

This is the repository recovery snapshot. It is overwritten, not appended.
Historical evidence and completed-work detail belong in GitHub issues, PRs,
comments, releases, and merge commits.

Last updated: `2026-08-04T09:03:17Z`

## Durable source of truth

- GitHub issues, PRs, comments, releases, and repository files are authoritative.
- Chat memory and superseded roadmap documents are not current authority.
- New sessions read `AGENTS.md`, `README.md`, this file, and the active issue or
  PR before expanding context through `docs/DOCUMENT_MAP.md`.

## Current snapshot

ASGK v1.7.3 remains the latest completed source-only GitHub release under the
Apache-2.0 license. ASGK 2.0 is an active docs-driven evolution coordinated by
issue #323.

The source contract now has one 13-field work-unit identity, two separate
execution gates, and two bounded task-packet modes. Work-unit handoff uses one
typed core for both the normal packet and compact projection. Compact handoff
must pass the core evaluator before CURRENT_STATUS freshness is checked.

Retained core JSON validators use one common evidence envelope with explicit
checked and unchecked claims, stable finding codes, human-gate state, and a
proof boundary. `scripts/asgk_lib/scenario_registry.py` owns exact retained
scenario expectations; doctor and CI execute the same registry rather than
maintaining duplicate fixture lists. Early failures name only checks that ran,
missing live-tool executables emit controlled envelopes, and a mechanical
failure cannot hide a simultaneous required human gate.

ASGK source validation now has one engine:
`scripts/asgk_lib/source_validation.py`. `asgk validate`, `doctor`, and the thin
`validate_bootstrap.py` compatibility wrapper reach that engine. Its retained
source-reference set excludes superseded Roadmap, duplicate-owner,
fixed-storage/promotion, legacy-target, and directory-only checker
prerequisites. Supplied source inventories prove path membership only; they do
not inspect contents or describe a target installation shape.

`target-evidence-check` checks only explicit caller-supplied expect/forbid path
and literal-text claims against an arbitrary target layout. Its three domain
states map to the common evidence envelope. Exit `0` proves only that accepted
named claims matched, never target fit, governance depth, recommendation,
approval, or readiness.

CURRENT_STATUS is only a recovery snapshot. It does not own completed-work or
decision history.

Adoption and material-upgrade assessment remains read-only and target-specific,
guided by a human-selected frontier-capability model. Tools may check claims;
they do not choose an Agent, prescribe architecture, or decide governance depth.

The fixed-shape target tools and dedicated fixtures are removed.
`target-evidence-check` is the sole target mechanical interface and checks
explicit claims; frontier judgment owns fit, depth, minimum change, or no change.

## Active work

```yaml
issue: "#323 ASGK 2.0 program"
pr: none
branch: main
state: active_program
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

- prior chat, superseded roadmap, or historical plan as current task authority
- automatic model selection, routing, switching, or price-tier dispatch
- fixed target file shape, module picker, or adoption declaration as fit proof
- validator success as semantic truth, human approval, or merge authority
- cloud egress, API/model calls, MCP writes, dependencies, schema changes,
  publication, or visibility changes without their existing gates

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files,
model cache, or external preparation outputs are authorized by this status.

## Next safe action

From current `main`, create W5 after the W4C close-out. W5 rewrites the Project
Brief and Evolution Model and scans public/startup projections; do not revive a
Roadmap, runtime-adapter stage, maturity ledger, fixed target shape, or automatic
Agent routing.

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
