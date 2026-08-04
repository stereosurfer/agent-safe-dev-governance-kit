# ASGK Project Brief

## Project Name

Agent Safe Governance Kit (ASGK)

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

## Primary Outputs

```yaml
primary_outputs:
  - durable_rules_and_canonical_owners
  - bounded_github_work_units
  - checked_projection_and_validation_evidence
  - human_readable_handoff_and_recovery_state
  - target_specific_mechanical_claim_evidence
  - source_only_release_closeout
```

## Non-goals

- automatic model, provider, agent, or price-tier selection or switching;
- runtime-specific adapters, routing, subagent orchestration, or goal workflows;
- a universal target-repository file bundle or fixed target layout;
- treating validator success as semantic correctness, approval, release
  authority, or merge authority;
- replacing a required human decision with a model judgment or green CI;
- package, installer, SaaS, cloud, API, MCP, or external-egress behavior;
- making chat history a source of task authority.

## Durable Source Of Truth

The selected live GitHub issue or qualifying PR is the executable work-unit
authority. Canonical repository documents define durable rules and ownership;
validators provide bounded mechanical evidence; model judgment interprets that
evidence; explicit human decisions remain required wherever the applicable
policy says so. Chat history is context, never authority.
