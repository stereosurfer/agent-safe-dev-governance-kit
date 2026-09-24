# 01 Physical Boundaries

This is a short source-repo boundary summary. `AGENTS.md` and the current
issue/PR define allowed paths and escalation; `docs/control/HUMAN_GATED_OPERATIONS.md`
defines human-gated operations. No example directory list grants write access.

## Writing source

Write only the exact paths authorized by the selected GitHub work unit (or a
valid, narrower task-packet refinement). A file under `docs/`, `scripts/`,
`schemas/`, `.github/`, or any other directory is not writable merely because
that directory exists. Protected governance or instruction paths require the
explicit issue scope and applicable escalation/review; they are not all
categorically forbidden.

## Hard boundaries

- Do not edit `.git/`, credentials, secrets, private keys, or private source
  material as ordinary source work. Stop for the applicable human gate if the
  task actually requires them.
- Do not commit generated runtime output, raw captures, live databases, caches,
  scratch, or other private/transient state. Small, sanitized, intentional
  fixtures are reviewed source changes, not a runtime-output exception.
- Do not write outside the issue's allowed paths, create an external storage
  location, move external responsibility into the repo, or use cloud/API/MCP
  capability based on a template. Each requires its own durable scope and gate.
- Do not delete user data, rewrite Git history, or force push as a workaround.

ASGK does not require a target to use Code Repo, Artifact Root, and Local State
Root as three named directories. Target storage, locking, cache, sync, and
cleanup belong to a target-owned design only when that work actually needs
them. See `docs/architecture/RUNTIME_ARTIFACT_POLICY.md` for ASGK source
commit hygiene and `docs/architecture/LOG_AND_RECORD_RETENTION_POLICY.md`
for ASGK governance record placement.
