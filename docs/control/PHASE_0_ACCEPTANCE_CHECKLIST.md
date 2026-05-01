# Phase 0 Acceptance Checklist

Phase 0 is accepted when the repo has a clear, bounded scaffold and enough contracts for implementation lanes to proceed without changing policy midstream.

## Governance

- [ ] `AGENTS.md` exists.
- [ ] Bootstrap docs exist under `docs/bootstrap/`.
- [ ] Control docs exist under `docs/control/`.
- [ ] Lane packets define objectives, allowed paths, acceptance, and stop conditions.
- [ ] Handoff status names current state, blockers, and next safe work.

## Storage And Boundaries

- [ ] Code Repo, Artifact Root, and Local State Root are separate.
- [ ] Google Drive sync-folder mode is filesystem sync only.
- [ ] App-managed Drive API is deferred/human-gated.
- [ ] Workspace lock behavior exists.
- [ ] Runtime artifacts and private source docs are excluded from repo scope.

## Contracts And Schemas

- [ ] Task packet schema exists.
- [ ] Merge decision schema exists.
- [ ] Promotion gate schema exists.
- [ ] Execution lane schema exists.
- [ ] Validation result schema exists.

## Scaffold And Tooling

- [ ] `check_project.py` passes.
- [ ] `validate_bootstrap.py` passes.
- [ ] `governance_hygiene.py` exists.
- [ ] GitHub issue and PR templates exist.

## Explicit Non-goals

- [ ] No cloud verifier required.
- [ ] No MCP write capability required.
- [ ] No real private source documents committed.
- [ ] No runtime artifacts committed.

## Remaining Gates Before v0.1 Runtime

- [ ] Project-specific tests defined.
- [ ] Domain schemas defined.
- [ ] First end-to-end smoke milestone defined.
