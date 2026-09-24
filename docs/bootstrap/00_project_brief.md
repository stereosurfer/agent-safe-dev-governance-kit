# ASGK Project Brief

## Project Name

Agent-Safe Development Governance Kit (ASGK)

## Mission

ASGK is a set of rules and tools that lets people and AI safely and smoothly
hand work to one another. It keeps the work state understandable, preserves a
small durable handoff, and leaves decisions and evidence quickly traceable
without depending on a particular model, provider, agent, or prior chat.

The minimum handoff must make clear:

- what to do;
- where to do it;
- what not to do;
- what must not be touched;
- what evidence exists and what was not checked; and
- what the next safe action is.

## Product Boundary

ASGK is repository governance, not an agent router or an automatic model
selector. People choose and replace the person or agent that continues a work
unit. ASGK supplies the durable scope, bounded context, validation evidence,
human gates, handoff state, and close-out trail needed for that replacement.
GitHub owns governed work and decision lineage. A task-owned delivery package
may own its current questions and evidence; a capability repository may index
prior Lessons and versioned methods. These do not replace GitHub authority.
Kanban, when used, owns runtime card/run state; it is optional, including for
Codex-and-GitHub-only work.

## Primary Outputs

```yaml
primary_outputs:
  - durable_rules_and_canonical_owners
  - bounded_github_work_units
  - checked_projection_and_validation_evidence
  - human_readable_handoff_and_recovery_state
  - searchable_github_decision_lineage
  - target_specific_mechanical_claim_evidence
  - source_only_release_closeout
```

## Non-goals

- automatic model, provider, agent, or price-tier selection or switching;
- requiring a Bot, Group, Kanban board, reviewer Bot, runtime adapter, or
  research/video/translation module in the generic operating profile;
- a universal target-repository file bundle or fixed target layout;
- treating validator success as semantic correctness, approval, release
  authority, or merge authority;
- replacing a required human decision with a model judgment or green CI;
- supplying a package, installer, SaaS, cloud/API/MCP or external-egress
  capability by default; a separately scoped optional integration still needs
  its applicable existing risk gates;
- making chat history a source of task authority.

A scheduler or prior successful run is a trigger or historical observation,
not current write or publication permission. A read-only target assessment
may recommend the minimum change or no adoption; it must not impose this
source repository's full file layout or issue form on every target.

## Durable Source Of Truth

The selected live GitHub issue or qualifying PR is the executable work-unit
authority. Canonical repository documents define durable rules and ownership;
validators provide bounded mechanical evidence; model judgment interprets that
evidence; explicit human decisions remain required wherever the applicable
policy says so. Chat history is context, never authority.
