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
  -> issue closeout review
  -> handoff / current status
```

Accepted, rejected, superseded, and reverted paths remain in that GitHub
lineage. The bounded issue closeout review is a fast decision-tree entrypoint,
not a second work ledger. A separate task-owned delivery package may hold its
current questions and evidence; the optional `scripts/asgk.py catalog` command
finds bounded metadata pointers to prior Lessons and methods from an explicitly
supplied index. Neither grants current work authority.

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

ASGK v3.0.0 is the latest source-only release. This repository's root
entrypoints are the released governance surface; remaining non-default
material under [`v3/`](v3/README.md) is candidate/history, not a second
authority. The GitHub work-projection workflow is owned by
`scripts/asgk_lib/github_workflow.py` and exposed through
`python3 scripts/asgk.py workflow --help`; `v3/asgk3.py` is a compatibility
entry, not a second implementation:

```text
repo core
  -> canonical docs, templates, GitHub issue / PR workflow
validators
  -> scripts/asgk.py, policy gate, PR status checks, negative fixtures
skills
  -> focused procedures that guide evidence gathering and model judgment
```

ASGK does not require Hermes, Kanban, a persistent Bot, or a separate police
agent. When ASGK is used alongside Kanban, cards/runs belong to that runtime
while GitHub retains ASGK work scope, PR/MDR, and closeout authority. Codex
and GitHub alone can use the repository-governance loop; a recurring schedule
starts a run, not that run's permission to edit or publish. A [target-owned
no-Hermes website pilot](https://github.com/stereosurfer/little-q-rock-museum/issues/1)
has completed one clearly fictional public content cycle; recurring automation
and later-run authority were not tested.

Research, video, and translation are examples of capability evolution, not
mandatory ASGK modules. A task's question/evidence graph belongs to its own
delivery contract. Reusable Lessons and methods can be discovered in bounded
slices and promoted to a versioned Skill only through the applicable issue,
PR, tests, review, and any existing human gate that applies. A large lesson
corpus calls for progressive disclosure, not full-context loading or inflated
Bot memory. The optional metadata-only catalog is available through the public
root CLI; it does not read Lesson bodies, determine applicability, or promote a
method. The eleven root source Skills have been synthesized for the 3.0
operating contract under [#405](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/405).
The target-owned, read-only [context-defogger #8](https://github.com/stereosurfer/context-defogger/issues/8)
assessment is complete; it recommended minimum change, not target adoption.
The [#407 cold handoff](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/407)
used an independent no-history AI substitute with OWNER approval and recovered a
bounded accepted/rejected decision path. It was not an unfamiliar-human or
cross-provider test and did not prove a complete workflow graph. The no-Hermes
site pilot likewise proves one reviewed and published cycle, not a schedule.
These bounded results are part of the [3.0 release decision](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/412),
not proof of the untested capabilities named above.

Skills are not a new authority layer or a substitute for model judgment. They
direct attention to relevant evidence, safety boundaries, uncertainty, and stop
conditions. Durable authority comes from the selected durable GitHub issue or
qualifying pull request, applicable canonical repository rules, contracts, and
decision records, and an explicit durable human decision when an existing gate
requires one.

Validators do not create scope, approve a decision, or satisfy a human gate.
They produce bounded mechanical evidence and enforce only their declared
contracts. When a validator is a required gate, a blocking finding or failed
required check prevents the corresponding workflow claim from advancing. A
validator pass means only that its named checks passed at their stated proof
boundary; it is not semantic correctness, target fit, release approval, or
merge authority.

Model judgment interprets evidence and makes semantic recommendations within
the durable work unit. It neither creates task authority nor satisfies an
existing human gate.

For target adoption and material upgrades, a human selects a
frontier-capability evaluator outside ASGK. The Skill guides that
evaluator; ASGK does not select, route, rank, switch, or price-tier models.
Deterministic validators check known invariants and concrete claims. They do not
decide whether ASGK fits a target, prescribe target architecture, or prove
semantic adoption readiness.

## Who It Is For

ASGK is useful for repositories that:

- allow AI agents or automation to create code or documentation changes;
- need one source of truth for humans and agents;
- want issue-first work units with clear non-goals and rollback expectations;
- need local validation and negative fixtures before merge;
- want high-risk operations to require explicit human approval;
- care about recovery after context loss, compacted sessions, or agent handoff.

It can be a poor fit when existing PR/CI/review history already supplies enough
handoff and auditability for the actual risk. A target-owned, read-only
assessment may recommend minimum change, no change, or no adoption; it should
not force the source repository's full issue form, file layout, or runtime
profile into a smaller project. The default layer remains generic.

## What The Current Root Source Includes

- `AGENTS.md` operating rules for agents entering the repository.
- GitHub issue and PR templates for scoped work units.
- Allowed-path and protected-path expectations.
- Merge Decision Record fields for evidence-backed merge decisions.
- Human-gated operation policy for risky work.
- Low-risk autonomous merge policy for narrow eligible changes.
- `docs/handoff/CURRENT_STATUS.md` as a compact recovery surface.
- Current-status policy that makes status updates post-merge-safe by default.
- Local validation through `python3 scripts/asgk.py doctor`.
- GitHub snapshot/work projection, draft-only handoff and closeout, and bounded
  closeout search/trace through `python3 scripts/asgk.py workflow --help`.
  Capture uses GitHub GET only; supplied snapshots and local observations do
  not grant current issue authority or approval. A same-issue, substantive
  closeout in the strict canonical YAML subset can yield a
  `yaml_subset_shape_checked` edge; unsupported or malformed YAML remains an
  unverified candidate. JSON needs one visible, top-level closeout block;
  raw HTML-marked comments, nested-example closeouts, multiple visible JSON
  closeouts, mixed JSON/YAML closeouts, or an explicit DRAFT primary decision
  cannot create a checked edge. Search matches only named parsed decision
  fields, not extra metadata, comment preambles or hidden examples. Shape checking does not prove the decision, evidence,
  authorship, approval, or complete history. Use one
  snapshot per issue and one observation per PR per lookup; a closed issue
  without a recognizable supplied closeout is reported as incomplete, not
  silently treated as a complete trace.
- Optional metadata-only Lesson/method discovery through
  `python3 scripts/asgk.py catalog --help`, using an explicit caller-supplied
  index. Text hits are bounded pointers, not applicability recommendations,
  work authority, or Skill promotion.
- Negative fixtures for governance hygiene, PR bodies, handoff packets,
  caller-supplied target evidence, and stale current-status patterns.
- Explicit validation-boundary wording so `doctor` evidence is not treated as a
  substitute for project-specific tests, security review, privacy review, or API
  freshness checks.
- PR-level status validation for draft state, mergeability, review decision,
  status checks, PR-body policy, changed-path hygiene, and GitHub closing issue
  references.
- Eleven source-distributed ASGK Skills under `skills/`, synthesized from
  current rules and preview.1 proposals and used by relevant responsibility
  and stage; they are not loaded or installed as a bundle by default. The
  eleven `v3/skills/` files remain historical candidate evidence, not a second
  active pack.
- Document map and context-budget guidance so agents read the smallest
  sufficient context instead of the whole repository.
- Read-only `target-evidence-check` diagnostics for explicit caller-supplied
  path and literal-text claims. These provide bounded mechanical observations,
  not a target-fit decision, minimum-change recommendation, or
  adoption-readiness proof.

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

For a first governed change in this ASGK source repository:

```text
1. Read AGENTS.md, README.md, and docs/handoff/CURRENT_STATUS.md.
2. Open or select one GitHub issue with objective, allowed paths, validation,
   expected output, non-goals, stop conditions, and rollback expectations.
3. Create a branch from current main.
4. Change only the allowed paths.
5. Run the issue's project checks and python3 scripts/asgk.py doctor.
6. Draft the PR body in a file using .github/PULL_REQUEST_TEMPLATE.md.
7. Fill the Current Status Impact and Merge Decision Record sections.
8. Run local PR body governance preflight before PR create/edit:
   python3 scripts/pr_governance_preflight.py check --body-file <body-file>
9. Open or update the PR with the checked body file.
10. Wait for GitHub Actions when they apply.
11. Merge only when policy, validation, CI, and human gates allow it.
```

A target uses its own assessed authority, files, PR shape and project tests;
the ASGK source `doctor` and this repository's exact form are not universal
target gates.

For a recurring content job, the scheduler only awakens the worker. Each
actual change still needs its target's current durable authority and
publication boundary. A low-risk website may need only its existing GitHub
issue/PR, content/source rules, CI and compact closeout—or no ASGK adoption
when those controls already suffice. This choice requires target evidence;
the [3.0 website pilot](https://github.com/stereosurfer/little-q-rock-museum/issues/1#issuecomment-5826230588)
tested one accepted fictional note against rejected real-collection, product,
price, message, and site-setting paths. It did not test recurring updates.

This repository's `docs/DOCUMENT_MAP.md` and `docs/DOCUMENT_REGISTRY.md` are
repo-local. Do not copy them unchanged into a target repository. A target may
keep equivalent existing navigation and ownership mechanisms; use the templates
only when the assessment finds a real gap.

## Safety Model

ASGK separates ordinary bounded work from operations that must stop for explicit
human review.

Human-gated examples include release execution, repository visibility changes,
credentials or secrets, dependency changes, schema or contract changes,
runtime artifact boundaries, private source material, external target writes,
cloud/API/model lanes, destructive history operations, and unclear scope.

Low-risk merge is intentionally narrow. A PR must have the right issue, allowed
paths, passing validation, complete evidence, clean runtime boundaries, and no
human-gated trigger before it can be treated as low risk.

An OWNER-approved program may separately authorize an exact-scope,
tracked-source-only protected source change with no external side effect beyond
routine issue/PR metadata and complete ordinary-revert recovery, when canonical
policy and the current child issue both permit it. That program path requires
current-head scope/no-gate review, independent review, CI, and strict
`check-pr`; it is not current-head human review and cannot cover an operation
that remains human-gated.

## Current Release State

ASGK v3.0.0 is the latest completed source-only GitHub release under the
Apache-2.0 license. The [published release](https://github.com/stereosurfer/agent-safe-dev-governance-kit/releases/tag/v3.0.0)
tag points to the exact approved source commit
`f78f38154b0010f96062c1db1d1eddc2ec345012`; [release issue #412](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/412)
holds the human approval, validation and publication readback. No package,
installer, SaaS, runtime adapter or automatic Skill installation was published.
The GitHub workflow projection, optional metadata-only catalog and eleven root
source Skills are included. The bounded [#407 cold handoff](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/407)
and target-owned [no-Hermes website pilot](https://github.com/stereosurfer/little-q-rock-museum/issues/1)
remain evidence at their stated limits, not proof of recurring automation,
human/cross-provider handoff or general Kanban integration. Milestone closure
is recorded separately in [#372](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/372),
not implied by the release. The former 2.0
program and old runtime-adapter roadmaps are history, not current authority.

## What The Generic Core Does Not Supply

ASGK does not itself:

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

Optional Bot, Kanban, API, MCP, or other runtime integration requires its own
bounded scope and existing risk gates. Their absence does not prevent a
Codex-and-GitHub-only repository from using—or declining—ASGK.

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
  = historical released generic repo-governance line

ASGK v2.0
  = prior docs-driven evolution and retained historical evidence

ASGK 3.0
  = current v3.0.0 source-only release; program closure remains separate
```

The lineage matters, but old roadmap labels are not current product authority.
