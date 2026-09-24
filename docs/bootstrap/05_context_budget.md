# 05 Context Budget

This is a short entry to the canonical
[Context Budget Policy](../control/CONTEXT_BUDGET_POLICY.md), not a second set
of limits.

Start with `AGENTS.md`, `README.md`, `docs/handoff/CURRENT_STATUS.md`, and the
selected live GitHub issue or PR. For executable work, that authority records
an exact `context_read_set` and `project_specific_validation`. Read that exact
set; do not silently skip an item because it seems irrelevant. Narrow it only
through an authorized `issue_refinement`, and record any justified expansion.
No fixed per-task file count or per-PR changed-file count overrides the issue's
scope and validation.

A task packet is optional. `issue_refinement` may only narrow a live issue;
`github_unavailable_fallback` is a bounded local-work exception during a
verified outage and cannot authorize a PR or external action. Neither is a
second task authority.

Stop when required context or allowed paths are missing, the selected authority
conflicts with another source, a protected or human-gated action lacks
authorization, or validation cannot establish the required result. Do not solve
context pressure by silently skipping a gate. A named class is not authority,
but when its stated `use_when` matches the work, its required `read` entries
must be present in the exact issue/PR set; correct the authority if they are
missing.
