# Document Registry

Status: optional target-project registry reference.

Use this template only when a target-specific assessment finds that the
repository needs a document registry and lacks an adequate equivalent. It is
not an ASGK adoption requirement or a required filename.

Keep an existing target-owned ownership or navigation mechanism when it already
satisfies the need. The example paths below are placeholders to adapt, not a
bundle to install.

## Scope

```text
The selected document registry is repo-local and target-owned.
```

Replace every placeholder and delete every row that does not exist in the target
repository.

## Relationship To Other Navigation Surfaces

```yaml
relationship:
  <target-owned router path or none>: compact navigation router
  <target-owned registry path>: complete target repo document registry
  <target-owned context policy path or none>: task-type read sets and context expansion
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
  historical_evidence: Superseded or archival material for bounded historical lookup; never current authority.
```

## Entry And Startup Documents

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `<target product entry or onboarding document>` | summary | project positioning and onboarding | `<yes or no>` | `<condition>` | `<lane>` |
| `<target agent operating guide, if used>` | canonical | target operating rules and safety boundaries | `<yes or no>` | `<condition>` | `<lane>` |
| `<target current-state or handoff surface, if used>` | status | compact current repo snapshot and next safe work | `<yes or no>` | `<condition>` | `<lane>` |
| `<current durable work-unit surface>` | canonical | active objective, allowed paths, acceptance, validation, and decision state | yes | every work unit | active task lane |

## Project-Specific Documents

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `<path>` | `<role>` | `<topic>` | no | `<condition>` | `<lane>` |

## Schemas And Contracts

| Path | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `<target schema path or pattern>` | schema | machine-readable validation structures | no | schema validation, fixtures, tooling | `<lane>` |
| `<target contract path or pattern>` | contract | semantic contract rules and invariants | no | contract, schema, validation, artifact work | `<lane>` |

## Scripts And CI

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `<target validation entrypoint>` | script | target validation behavior | no | local validation and CI debugging | `<lane>` |
| `<target CI workflow path>` | script | target CI validation behavior | no | CI/workflow changes | `<lane>` |

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
