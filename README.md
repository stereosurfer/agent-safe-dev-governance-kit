# Agent-Safe Development Governance Kit

A GitHub-native governance kit for safe, durable human-AI repository work.

ASGK is a set of rules and tools that lets people and AI hand work over safely
and smoothly. It keeps work understandable, resumable, and traceable without
depending on a particular model, provider, agent, or prior conversation. Work
is authorized, bounded, validated, reviewed, and handed off through GitHub
issues, pull requests, repository files, and local checks.

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

ASGK does not prove that generated code is semantically correct, secure, private,
or based on current third-party APIs. It blocks unsupported workflow and merge
claims: missing issue authority, vague validation evidence, out-of-scope file
changes, unresolved human gates, runtime-artifact leakage, and stale handoff
state. Project tests, type checks, security scanners, dependency audits, current
documentation lookup, privacy controls, code review, and human judgment remain
separate responsibilities.

## Product Shape

ASGK v1.x is distributed as a source-only governance kit:

```text
repo core
  -> canonical docs, templates, GitHub issue / PR workflow
validators
  -> scripts/asgk.py, policy gate, PR status checks, negative fixtures
skills
  -> focused procedures that guide evidence gathering and model judgment
```

Skills are not a new authority layer or a substitute for model judgment. They
direct attention to relevant evidence, safety boundaries, uncertainty, and stop
conditions while durable authority remains in GitHub issues, pull requests,
repository files, ASGK validators, and existing human gates.

For target adoption and material upgrades, a human selects a
frontier-capability evaluator outside ASGK. The Skill guides that
evaluator; ASGK does not select, route, rank, switch, or price-tier models.
Deterministic validators check known invariants and concrete claims. They do not
decide whether ASGK fits a target, prescribe target architecture, or prove
semantic adoption readiness.

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
- Negative fixtures for governance hygiene, PR bodies, handoff packets, the
  current legacy target-install shape checker, and stale current-status
  patterns.
- Explicit validation-boundary wording so `doctor` evidence is not treated as a
  substitute for project-specific tests, security review, privacy review, or API
  freshness checks.
- PR-level status validation for draft state, mergeability, review decision,
  status checks, PR-body policy, changed-path hygiene, and GitHub closing issue
  references.
- Source-distributed ASGK Skill Pack v0 under `skills/` for startup, issue
  scoping, PR evidence, gatekeeping, post-merge closeout, current-status
  handoff, evidence audit, target-install audit, and governance health checks.
- Document map and context-budget guidance so agents read the smallest
  sufficient context instead of the whole repository.
- Read-only target-install diagnostics for a legacy expected source shape.
  These provide mechanical observations, not a target-fit decision,
  minimum-change recommendation, or adoption-readiness proof.

## Quick Start

For this repository:

```bash
python3 scripts/asgk.py doctor
```

For adopting or materially upgrading ASGK in another repository, start with
`docs/INSTALL_SURFACE.md` and
`skills/asgk-target-install-audit/SKILL.md`. Have a human choose a
frontier-capability evaluator. The read-only assessment uses target
evidence to recommend the minimum sufficient adaptation, no change, or no
adoption. It adds no approval gate; existing gates apply only if a proposed
implementation triggers them.

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
7. Draft the PR body in a file using .github/PULL_REQUEST_TEMPLATE.md.
8. Fill the Current Status Impact and Merge Decision Record sections.
9. Run local PR body governance preflight before PR create/edit:
   python3 scripts/pr_governance_preflight.py check --body-file <body-file>
10. Open or update the PR with the checked body file.
11. Wait for GitHub Actions when they apply.
12. Merge only when policy, validation, CI, and human gates allow it.
```

This repository's `docs/DOCUMENT_MAP.md` and `docs/DOCUMENT_REGISTRY.md` are
repo-local. Do not copy them unchanged into a target repository. A target may
keep equivalent existing navigation and ownership mechanisms; use the templates
only when the assessment finds a real gap.

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

ASGK v1.7.3 is the latest completed source-only GitHub release under the
Apache-2.0 license.

v1.7.3 is a v1.x PR-readiness fallback patch release. It keeps the v1.7.2
source-local boundary baseline and tightens ASGK Skills so target repositories
without the source-repo `check-pr` command can record that command as
unavailable and use repository-local PR evidence instead. It remains a
source-only GitHub release: no package, installer, runtime adapter, dependency,
schema, workflow, repository visibility change, cloud/API/model lane, MCP
change, or v2.0 work is included.

The active ASGK 2.0 evolution keeps the generic governance core and focuses on
clear, resumable, traceable human-AI work plus frontier-guided target
assessment. The superseded runtime-adapter/profile roadmap does not define
ASGK 2.0.

## What v1.x Does Not Include

ASGK v1.x does not:

- replace Codex, Claude Code, Cursor, ChatGPT, OpenGoat, or other agent
  runtimes;
- provide runtime-specific profiles in the default operating profile;
- auto-approve high-risk work;
- publish packages or installers by default;
- manage project-specific architecture, product strategy, or domain schemas;
- detect every hallucinated API, stale dependency usage, SQL injection, XSS,
  privacy leak, license issue, or production-readiness defect;
- prevent an external agent runtime from sending private code or data to a model
  provider; ASGK can require gates and records, but runtime egress controls live
  outside the governance kit;
- remove the need for tests, code review, and human judgment.

## Where To Read Next

- `docs/QUICKSTART.md` for the first governed change.
- `AGENTS.md` for agent operating rules.
- `docs/DOCUMENT_MAP.md` for canonical document ownership in this repository.
- `docs/INSTALL_SURFACE.md` for frontier-guided target assessment,
  responsibility boundaries, and minimum sufficient adaptation.
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
  = latest released generic repo-governance line

ASGK v2.0
  = active docs-driven evolution of safe handoff, traceability, and assessment
```

The lineage matters, but old roadmap labels are not current product authority.
