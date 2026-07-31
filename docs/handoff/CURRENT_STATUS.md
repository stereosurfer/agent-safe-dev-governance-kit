# Current Status

This is the repository recovery snapshot. It is overwritten, not appended.
Historical evidence and completed-work detail belong in GitHub issues, PRs,
comments, releases, and merge commits.

Last updated: `2026-07-31T15:48:20Z`

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

CURRENT_STATUS is only a recovery snapshot. It does not own completed-work or
decision history.

Adoption and material-upgrade assessment remains read-only, target-specific,
and guided by a human-selected frontier-capability model. Deterministic tools
may collect evidence or check caller-supplied claims; they do not choose an
Agent, prescribe target architecture, or decide governance depth.

Legacy target-install commands still retain fixed-shape assumptions. Their
planned clean cutover belongs to later bounded work under #323 and must not be
treated as target-fit or approval authority.

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

Create the separately scoped W4A child issue from current `main` after W3C
close-out. W4A owns the source reference-superset validator split; do not
preempt W4B target claim checking, W4C legacy-tool removal, or resume superseded
plans.

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
