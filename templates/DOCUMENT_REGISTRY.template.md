# Document Registry

Status: target-project template.

This template is for a repository that installs or adopts ASGK governance.

`docs/DOCUMENT_MAP.md` should be the target repository's small navigation router.
This file should be the target repository's complete document registry.

## Scope

```text
DOCUMENT_REGISTRY.md is repo-local.
```

Replace every placeholder and delete every row that does not exist in the target
repository.

## Relationship To DOCUMENT_MAP.md

```yaml
relationship:
  docs/DOCUMENT_MAP.md: compact navigation router
  docs/DOCUMENT_REGISTRY.md: complete target repo document registry
  docs/control/CONTEXT_BUDGET_POLICY.md: task-type read sets and context expansion
```

Do not read this file by default. Read it only when canonical ownership,
document roles, or registry rows must be inspected or updated.

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

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `<path>` | `<role>` | `<topic>` | no | `<condition>` | `<lane>` |

## Schemas And Contracts

| Path | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `schemas/*.json` | schema | machine-readable validation structures | no | schema validation, fixtures, tooling | `<lane>` |
| `contracts/*.yaml` | contract | semantic contract rules and invariants | no | contract, schema, validation, artifact work | `<lane>` |

## Scripts And CI

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `scripts/asgk.py` | script | ASGK validation wrapper if installed | no | local validation and CI debugging | `<lane>` |
| `.github/workflows/<workflow>.yml` | script | CI validation behavior | no | CI/workflow changes | `<lane>` |

## Registry Rules

1. Do not leave placeholder rows in the final target repository registry.
2. Do not copy ASGK's internal registry rows into a target project unless the
   target project actually contains those files.
3. Summary documents should point to canonical documents rather than repeating
   full policy text.
4. If a document becomes canonical for a new topic, update this registry in the
   same PR.
5. If validation behavior changes, update the relevant script, schema, example,
   and this registry together.
