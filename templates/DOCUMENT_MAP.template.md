# Document Map

Status: target-project template.

This template is for a repository that installs or adopts ASGK governance. It is
not the ASGK repository's own document map.

Replace every placeholder and delete every row that does not exist in the target
repository. The finished file must describe the target repository's actual
canonical documents, summaries, examples, templates, schemas, contracts, status
surfaces, scripts, and task-specific read sets.

## Scope Rule

```text
DOCUMENT_MAP.md is repo-local.
```

ASGK's internal `docs/DOCUMENT_MAP.md` governs only the ASGK repository. A target
project must own its own `docs/DOCUMENT_MAP.md` after installation.

Do not copy ASGK's internal document map unchanged into a target repository.

## Core Rule

```text
Do not read the whole repository for every task.
Read the smallest set of canonical documents required by the work unit.
```

If two documents appear to disagree, prefer the document marked `canonical` for
that topic. If a summary document disagrees with a canonical document, the
summary document is stale and should be fixed in a separate issue.

## Default Startup Set

Every new agent session should start with only this minimal set unless the
current issue, PR, or handoff packet points elsewhere:

```yaml
default_startup_set:
  - AGENTS.md
  - README.md
  - docs/handoff/CURRENT_STATUS.md
  - current GitHub issue or PR
```

Additional documents should be pulled by task type, not by habit.

## Document Roles

```yaml
roles:
  canonical: Primary source of truth for a topic.
  summary: Short orientation document that points to canonical sources.
  example: Non-authoritative sample for humans and agents.
  schema: Machine-readable structure contract.
  contract: Semantic rules and invariants.
  template: Reusable starting point for work units or GitHub surfaces.
  status: Current handoff or state surface.
  script: Executable validation or hygiene behavior.
  future_optional: Planned future capability, not part of the current core.
```

## Entry And Startup Documents

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `README.md` | summary | project positioning and onboarding | yes | all new sessions | `<lane>` |
| `AGENTS.md` | canonical | generic operating profile, source-of-truth rule, escalation triggers, stop conditions | yes | all agent sessions | `<lane>` |
| `docs/handoff/CURRENT_STATUS.md` | status | compact current repo snapshot and next safe work | yes | all new sessions, handoff recovery | `<lane>` |
| current GitHub issue or PR | canonical | active task objective, allowed paths, acceptance, validation, merge state | yes | every work unit | active task lane |

## Project-Specific Documents

Add target repository documents here.

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `<path>` | `<role>` | `<topic>` | no | `<condition>` | `<lane>` |

## Schemas And Contracts

Add only the schemas and contracts that exist in the target repository.

| Path | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `schemas/*.json` | schema | machine-readable validation structures | no | schema validation, fixtures, tooling | `<lane>` |
| `contracts/*.yaml` | contract | semantic contract rules and invariants | no | contract, schema, validation, artifact work | `<lane>` |

## Scripts And CI

Add only the scripts and workflows that exist in the target repository.

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `scripts/asgk.py` | script | ASGK validation wrapper if installed | no | local validation and CI debugging | `<lane>` |
| `.github/workflows/<workflow>.yml` | script | CI validation behavior | no | CI/workflow changes | `<lane>` |

## Task-type Reading Guide

Start small. Add task-specific read sets only when the target repository needs
them.

```yaml
docs_only_task:
  read:
    - AGENTS.md
    - docs/handoff/CURRENT_STATUS.md
    - current issue or PR
    - target file
    - .github/PULL_REQUEST_TEMPLATE.md

merge_decision_task:
  read:
    - current PR body
    - changed file list
    - current GitHub issue
    - docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md
    - docs/control/HUMAN_GATED_OPERATIONS.md
    - docs/control/MERGE_DECISION_RECORD.md
```

## Maintenance Rules

1. Do not leave placeholder rows in the final target repository map.
2. Do not copy ASGK's internal document registry into a target project unless the
   target project actually contains those files.
3. Summary documents should point to canonical documents rather than repeating
   full policy text.
4. If a document becomes canonical for a new topic, update this map in the same
   PR.
5. If validation behavior changes, update the relevant script, schema, example,
   and this map together.
