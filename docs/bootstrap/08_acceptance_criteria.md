# 08 Acceptance Criteria

Status: source-repository summary.

The current issue's `acceptance_sheet` and `project_specific_validation` name
what this work must prove. Select checks that match the change; do not require
an unrelated artifact-promotion pipeline merely to complete a repository PR.

```yaml
acceptance_dimensions:
  implementation: project tests, type checks, or formatting when applicable
  data_or_interface: relevant target-owned schema, contract, fixture, provenance, or output-quality checks when applicable
  governance: issue authority, allowed paths, PR evidence, CI, Merge Decision Record, applicable human gates, and close-out
```

Record each check's evidence source and proof limit. A structural or
deterministic fallback check does not prove human-facing quality, semantic
correctness, production readiness, or permission to publish. If a workflow
uses a task-owned promotion process, its issue must name that process and
its tests; ASGK supplies no universal status chain.

Complete the issue's acceptance sheet and document any not-run check with a
material reason. Update `docs/handoff/CURRENT_STATUS.md` only when repo-level
recovery state would otherwise mislead the next session. Keep detailed
accepted/rejected decisions in GitHub close-out, not a parallel ledger.
