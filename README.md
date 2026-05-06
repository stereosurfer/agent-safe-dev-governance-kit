# Agent-Safe Development Governance Kit

A GitHub-native governance kit for safe AI-assisted repository changes.

ASGK helps a repository accept changes from humans, Codex, Claude Code, Cursor,
ChatGPT, other AI agents, scripts, or automation without letting chat become the
control plane. Work is authorized, bounded, validated, reviewed, and handed off
through GitHub issues, pull requests, repository files, and local checks.

## What It Is

ASGK is a repo governance layer. It is not an agent runtime, package manager,
installer, orchestration platform, or project architecture framework.

It gives a repository a durable operating loop:

```text
issue
  -> allowed paths
  -> branch
  -> bounded change
  -> validation
  -> pull request
  -> Merge Decision Record
  -> human gate or low-risk merge
  -> handoff / current status
```

The core principle is:

```text
Chat is not the control plane.
GitHub issues, pull requests, repository files, and handoff documents are.
```

## Problem It Solves

AI coding agents can move quickly, but repo state often gets trapped in private
chat threads, stale handoff notes, implicit assumptions, or unreviewed tool
actions. That creates avoidable risks:

- work starts from the wrong issue or stale branch;
- changes drift outside the allowed scope;
- validation results are summarized without evidence;
- risky operations are treated like routine edits;
- the next human or agent cannot safely resume.

ASGK turns those risks into explicit repository contracts: required issue
fields, PR evidence, allowed-path boundaries, stop conditions, validation
commands, merge records, human-gated operations, and compact current-status
handoff.

## Product Shape

ASGK v1.x is distributed as a source-only governance kit:

```text
repo core
  -> canonical docs, templates, GitHub issue / PR workflow
validators
  -> scripts/asgk.py, policy gate, PR status checks, negative fixtures
skills
  -> reusable procedures that sequence existing repo/GitHub gates
```

Skills are not a new authority layer. They help agents use the repo governance
surface with less repeated rule reading, while final authority remains in GitHub
issues, pull requests, repository files, ASGK validators, and human gates.

## Who It Is For

ASGK v1.x is useful for repositories that:

- allow AI agents or automation to create code or documentation changes;
- need one source of truth for humans and agents;
- want issue-first work units with clear non-goals and rollback expectations;
- need local validation and negative fixtures before merge;
- want high-risk operations to require explicit human approval;
- care about recovery after context loss, compacted sessions, or agent handoff.

It is a poor fit when a project wants fully ad hoc agent work, does not use
GitHub issues and PRs, or wants a runtime-specific agent profile to define the
governance model. ASGK v1.x deliberately keeps the default layer generic.

## What ASGK v1.x Includes

- `AGENTS.md` operating rules for agents entering the repository.
- GitHub issue and PR templates for scoped work units.
- Allowed-path and protected-path expectations.
- Merge Decision Record fields for evidence-backed merge decisions.
- Human-gated operation policy for risky work.
- Low-risk autonomous merge policy for narrow eligible changes.
- `docs/handoff/CURRENT_STATUS.md` as a compact recovery surface.
- Current-status policy that makes status updates post-merge-safe by default.
- Local validation through `python3 scripts/asgk.py doctor`.
- Negative checks for governance hygiene, PR bodies, handoff packets, target
  install readiness, and stale current-status patterns.
- PR-level status validation for draft state, mergeability, review decision,
  status checks, PR-body policy, changed-path hygiene, and GitHub closing issue
  references.
- Source-distributed ASGK Skill Pack v0 under `skills/` for startup, issue
  scoping, PR evidence, gatekeeping, post-merge closeout, current-status
  handoff, evidence audit, target-install audit, and governance health checks.
- Document map and context-budget guidance so agents read the smallest
  sufficient context instead of the whole repository.
- Target-install read-only checks for evaluating whether another repository has
  the expected governance surface.

## Quick Start

For this repository:

```bash
python3 scripts/asgk.py doctor
```

For adopting ASGK in another repository, start with `docs/INSTALL_SURFACE.md`.
Treat that path as copying and adapting a governance scaffold, not installing a
runtime package.

If your agent client supports skills, copy the needed directories under
`skills/` into the client skill location. If it does not, keep them as
repository-reference procedures and read only the specific `SKILL.md` needed for
the current work unit. See `docs/SKILL_PACK.md`.

For a first governed change in a repository that already has ASGK adopted:

```text
1. Read AGENTS.md.
2. Read docs/handoff/CURRENT_STATUS.md.
3. Open or select one GitHub issue with objective, allowed paths, validation,
   expected output, non-goals, stop conditions, and rollback expectations.
4. Create a branch from current main.
5. Change only the allowed paths.
6. Run python3 scripts/asgk.py doctor.
7. Open a PR using .github/PULL_REQUEST_TEMPLATE.md.
8. Fill the Current Status Impact and Merge Decision Record sections.
9. Wait for GitHub Actions when they apply.
10. Merge only when policy, validation, CI, and human gates allow it.
```

Do not copy this repository's internal
`docs/DOCUMENT_MAP.md` unchanged into a target repository; create the target
repo's own map from `templates/DOCUMENT_MAP.template.md`.

## Safety Model

ASGK separates ordinary bounded work from operations that must stop for explicit
human review.

Human-gated examples include release execution, repository visibility changes,
credentials or secrets, protected paths, dependency changes, schema or contract
changes, runtime artifact boundaries, private source material, cloud/API/model
lanes, and unclear scope.

Low-risk merge is intentionally narrow. A PR must have the right issue, allowed
paths, passing validation, complete evidence, clean runtime boundaries, and no
human-gated trigger before it can be treated as low risk.

## Current Release State

ASGK v1.2.1 is the latest completed source-only GitHub release under the
Apache-2.0 license.

v1.2.1 includes the v1.2 risk-gate mechanization, PR closing reference
validation, ASGK Skill Pack v0, and the release-state closeout checkpoint. It
remains a source-only GitHub release: no package, installer, runtime adapter,
dependency, schema, workflow, or repository visibility change is included.

The v1.x line is the generic repo-governance product line. Later runtime-specific
profiles or adapters are planned as optional optimization layers, not as the
default governance model.

## What v1.x Does Not Include

ASGK v1.x does not:

- replace Codex, Claude Code, Cursor, ChatGPT, OpenGoat, or other agent
  runtimes;
- provide runtime-specific profiles in the default operating profile;
- auto-approve high-risk work;
- publish packages or installers by default;
- manage project-specific architecture, product strategy, or domain schemas;
- remove the need for tests, code review, and human judgment.

## Where To Read Next

- `docs/QUICKSTART.md` for the first governed change.
- `AGENTS.md` for agent operating rules.
- `docs/DOCUMENT_MAP.md` for canonical document ownership in this repository.
- `docs/INSTALL_SURFACE.md` for target-repository adoption boundaries.
- `docs/SKILL_PACK.md` for source-distributed skill usage and maintenance
  touchpoints.
- `docs/control/CURRENT_STATUS_POLICY.md` for current-status and handoff rules.
- `docs/control/HUMAN_GATED_OPERATIONS.md` for operations that require human
  approval.
- `docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md` for low-risk merge
  eligibility.

## Lineage

ASGK grew out of Bootstrap Kit v2.1, the source lineage and template embryo
extracted from earlier project experiences.

```text
Bootstrap Kit v2.1
  = source lineage and template embryo

ASGK v1.x
  = current generic repo-governance product line

ASGK v2.0
  = planned runtime-adapter/profile optimization line
```

The lineage matters, but it is not the product boundary. ASGK v1.x is the
generic repository governance core.
