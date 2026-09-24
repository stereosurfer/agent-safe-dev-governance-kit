# 07 Contract First

Status: conditional source summary.

The current GitHub issue or qualifying PR owns the work-unit contract:
objective, allowed paths, expected output, validation, non-goals, stop
conditions, and rollback. A task packet can narrow it but not replace it.

When a work unit creates or changes a machine-readable interface, identify
the relevant target-owned contract or schema before implementation. Specify
its inputs/outputs, required fields, invariants, failure cases, compatibility
and project-specific positive/negative checks as needed by that interface.
Do not manufacture an artifact contract, source class, promotion status, or
provider lane for ordinary repository work.

A task-owned delivery contract may define question/evidence graphs, output
eligibility or a promotion process for its own workflow. It does not grant
GitHub edit scope, external-action permission, merge authority, or human-gate
approval. Use the current issue and `docs/control/HUMAN_GATED_OPERATIONS.md`
for those boundaries.
