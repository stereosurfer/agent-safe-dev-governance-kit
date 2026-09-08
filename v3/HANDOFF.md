# ASGK 3.0 candidate handoff

## Current authority and lineage

- Correction: [#358](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/358).
- Rejected direction retained: [#357](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/357), local commit 7e2cfc6.
- Branch: codex/asgk-3-preview; original main baseline 999d5a37a34c2484212b104b6234f5b0fbe5b09a.
- No merge, release, migration, target write or global Skill synchronization.
- #323/#356 and the original dirty W6B worktree are separate and untouched.

## Candidate recovery

Read v3/README.md, v3/DESIGN.md, this file and #358. Follow v3/TESTING.md when testing.
Use only the relevant v3/skills entrypoint for the controller/receiver role.
Root v2 instructions and canonical policies still govern this repository's actual mutations.

The prior standalone compiler/receipt demo has been replaced as the public entrypoint.
GitHub issue parsing and refinement reuse existing source functions. New commands capture
read-only snapshots, project an issue, preserve partial handoff, draft issue closeout,
and search/trace linked GitHub comments. In-place committed changes are supported.

All eleven source Skills were read and evaluated. Eleven short branch-local candidates
implement the responsibility changes and correct identified gate/closeout ambiguity.
Existing source Skills remain the baseline for comparison; installed copies are unchanged.

## Evidence and next action

Exact checks, failures, commit and live-read provenance are recorded in #358 comments.
CLI GitHub capture failed in this host environment; connector reads are a distinct source
and cannot be reported as a successful CLI integration test. Unit/fixture results do not
prove a real Bot, independent reviewer, human cold-start, target pilot or release.

The user now tests the candidate. Use durable findings to scope the next correction.
Do not interpret “candidate works” as authority to migrate other repos or finish W1–W10.
Preserve the rejected attempt and correction links; no reset, force push or silent deletion.

## Known implementation limits

- No automated GitHub posting, PR creation, merge, closure, Bot setup or publication.
- Capture is not atomic; a saved snapshot is not live authority or authenticated evidence.
- Local committed diff observation does not retain uncommitted patch contents or inspect ignored/external side effects.
- Checks report evidence coverage, not command execution, approval or semantic correctness.
- Search/trace indexes only supplied snapshots, reports missing links, and never invents history.
- No independent behavioral proof for the candidate Skills yet; format checks are narrower.

Ignoring this branch preserves v2. Its source commits survive temporary worktree removal;
do not delete either worktree automatically.
