# Document Map

Status: optional target-project navigation-router reference.

Use this template only when a target-specific assessment finds that the
repository needs a small navigation router and lacks an adequate equivalent.
It is not an ASGK adoption requirement, a required filename, or the ASGK
repository's own document map.

Keep an existing target-owned navigation mechanism when it already satisfies
the need. If the target chooses the example paths used below, the finished
`docs/DOCUMENT_MAP.md` should remain a small repo-local router and full registry
tables should live in `docs/DOCUMENT_REGISTRY.md`. Otherwise replace the example
paths with the target's own names and structure.

## Scope Rule

```text
The selected navigation router is repo-local and target-owned.
```

ASGK's internal `docs/DOCUMENT_MAP.md` governs only the ASGK repository. A target
must not copy it unchanged or treat it as target state.

This reference does not require a target to create either a document map or a
registry. Create or adapt only the surfaces justified by the assessment.

## Core Rule

```text
Do not read the whole repository for every task.
Read the smallest set of canonical documents required by the work unit.
```

If the target uses a registry and two documents appear to disagree, prefer the
document marked `canonical` for that topic. If a summary document disagrees with
a canonical document, the summary is stale and should be fixed through the
target's durable work-unit process.

## Default Startup Set

If the assessment recommends an explicit default startup set, tailor it to the
target's existing authority and handoff surfaces. The following is a pattern,
not a required bundle:

```yaml
default_startup_set:
  - <target agent operating guide, if used>
  - <target product entry or onboarding document>
  - <target compact current-state or handoff surface, if used>
  - <current durable work unit>
```

Additional documents should be pulled by task type, not by habit.

## Navigation Surfaces

```yaml
navigation_surfaces:
  router:
    path: <target-owned router path>
    read_by_default: false
    read_when:
      - document ownership is unclear
      - current issue asks for map/router work
  registry:
    path: <target-owned registry path or none>
    read_by_default: false
    read_when:
      - canonical ownership must be inspected or changed
      - registry row must be added or repaired
  read_sets:
    path: <target-owned context policy path or none>
    read_by_default: false
    read_when:
      - task-specific context selection is needed
      - context expansion is required
```

## Companion Registry When Needed

If the assessment finds that the target needs a separate registry, this optional
pairing may be adapted:

```text
templates/DOCUMENT_REGISTRY.template.md
  -> <target-owned registry path>
```

The selected router should point to that registry rather than duplicate its
full tables. Do not create a registry only because this reference mentions one.

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

## Compact Entry Summary

Keep this section short. If the target uses a separate registry, full rows
belong there.

```yaml
entry_summary:
  default_startup:
    - <target-owned startup surface>
    - <current durable work unit>
  full_registry: <target-owned registry path or none>
  context_read_sets: <target-owned context policy path or none>
```

## Maintenance Rules

1. Keep this file small enough to act as a router.
2. If the target uses a separate registry, add full document rows there, not in
   this router.
3. If the target uses a separate context policy, add task-type read sets there,
   not in this router.
4. Summary documents should point to canonical documents rather than repeating
   full policy text.
5. If a document becomes canonical for a new topic, update the target's
   ownership surface in the same work unit.
