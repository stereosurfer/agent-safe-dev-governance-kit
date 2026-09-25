# Current Status

This is the repository recovery snapshot. It is overwritten, not appended.
Completed-work history and decision detail belong in GitHub issues, PRs,
comments, releases, and merge commits.

Last updated: `2026-09-25T03:35:41Z`

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
Root navigation, control, workflow and optional catalog cutovers are current;
`doctor` runs root-owned regressions. Target templates are optional, and Stage 3
examples are not live-work proof.
Eleven root Skills are synthesized under #405; `v3/skills/` is candidate
history. Resolve live refs; #323 is prior 2.0 evidence, not current routing.

Target-owned [context-defogger #8](https://github.com/stereosurfer/context-defogger/issues/8) completed read-only minimum-change assessment, not adoption or write authority.
[#407](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/407) closed an OWNER-authorized no-history AI cold-read; unfamiliar-human, cross-provider, and complete-graph proof remain absent.
Target-owned [little-q #1](https://github.com/stereosurfer/little-q-rock-museum/issues/1) completed one reviewed, fictional public content cycle; recurring automation and future-run authority remain unproved.

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
next_work_unit_decision: "Under #372, audit current source/target claims and release gates, freeze only a verified candidate SHA, then seek a separate exact-SHA human-approved release issue. Do not redo #407 or the one-cycle website pilot."
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

Under #372, reconcile live PRs, audit #407 and little-q evidence at their
actual limits, then freeze a verified SHA and seek separate human release
approval. This status authorizes no target edit, tag, or release; only a
selected issue/PR grants scope. Do not read the excluded visual guide.

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
