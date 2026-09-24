# ASGK 3.0 preview.1 candidate handoff

## Current authority and lineage

- Preview.1 scope: [#359](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/359).
- Parent candidate: [#358](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/358), commit af7b143fa5b0d3c33d3b9e0cbe8f64434ee124ea.
- Rejected direction retained: [#357](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/357), local commit 7e2cfc6.
- Branch: codex/asgk-3-preview.1; original preview branch remains unchanged.
- Scoped correction: [#362](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/362)
  originated on `codex/asgk-3-preview.1-provenance-fix`; [#368](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/368)
  governs its review and proposed integration into preview.1. Until that PR merges,
  the correction remains on the separate branch. Verify the live PR state before
  treating it as part of preview.1.
- No merge to `main`, release, migration, target write or global Skill synchronization.
- #323/#356 and the original dirty W6B worktree are separate and untouched.

## Candidate recovery

Read v3/README.md, v3/DESIGN.md, this file and #358. Follow v3/TESTING.md when testing.
Read #359 for this revision's exact scope. Open KANBAN_BRIDGE only for a Kanban run;
open CAPABILITY_EVOLUTION only for a capability/lesson task.
Use only the relevant v3/skills entrypoint for the controller/receiver role.
Root v2 instructions and canonical policies still govern this repository's actual mutations.

The prior standalone compiler/receipt demo has been replaced as the public entrypoint.
GitHub issue parsing and refinement reuse existing source functions. New commands capture
read-only snapshots, project an issue, preserve partial handoff, draft issue closeout,
and search/trace linked GitHub comments. In-place committed changes are supported.

All eleven source Skills were read and evaluated. Eleven short branch-local candidates
implement the responsibility changes and correct identified gate/closeout ambiguity.
Existing source Skills remain the baseline for comparison; installed copies are unchanged.
Preview.1 edits only six relevant candidate Skills; the other five remain as reviewed in
the parent candidate. A completed closeout now keeps closed unmerged PR attempts beside
the merged replacement and blocks unresolved open attempts.

## Evidence and next action

Parent-candidate checks, failures and live-read provenance remain in #358 comments.
Preview.1's bounded checks and remaining research-reference gap belong to #359;
they must not be silently reported as parent-candidate proof. #362 adds a
`card-draft` command: it accepts a fresh, checked, non-fixture issue packet and
emits a controller-supplied Kanban card draft without posting to Hermes or GitHub.
The card names the issue, source and proof boundary, and requires a worker lacking
a permitted live issue-read tool to comment with a partial handoff before blocking.

The earlier #361 live GPT-6 Luna run showed a false worker-side “issue-verified”
claim without an observable GitHub read. #362 retained two imperfect retests:
`t_0fb59a91` blocked without a durable comment; `t_33c81c51` commented and
blocked, but attempted a general terminal command. The corrected, independently
generated card `t_46c2a073` used GPT-6 Luna on the isolated
`asgk-preview1-fix-362` board. Its redacted tool sequence was only
`kanban_show → kanban_comment → kanban_block`; the comment distinguished
controller-supplied facts from worker observation, named unknowns and the next
gate, and the card remained blocked without a repo write. The worker also noticed
that this no-write rehearsal selected `none` despite its parent issue's broader
implementation objective. These runs are evidence about this bounded negative
path, not proof of an executable live issue-read path, independent reviewer,
human cold-start, target pilot or release.

The linked [research-runtime-macos delivery contract](https://github.com/stereosurfer/research-runtime-macos/blob/d09eac50c3cd12c1427dadaf5c09d1c8f7dfd38e/docs/PACKAGE_FORMAT.md)
and [synthetic example](https://github.com/stereosurfer/research-runtime-macos/tree/d09eac50c3cd12c1427dadaf5c09d1c8f7dfd38e/examples/research-package-demo)
have been compared with this candidate. They demonstrate a stable answer contract,
topic-local question ledger, an `AGENT_ENTRY` → question node → observation →
evidence unit reading route, human handoff, source map and separate raw audit layer.
Preview.1 now distinguishes this task-owned delivery graph from its optional
cross-work capability catalog. The catalog is not a replacement for the package
contract and does not validate research completion.
Do not interpret “candidate works” as authority to migrate other repos or finish W1–W10.
Preserve the rejected attempt and correction links; no reset, force push or silent deletion.

## Known implementation limits

- No automated GitHub posting, PR creation, merge, closure, Bot setup or publication.
- Capture is not atomic; a saved snapshot is not live authority or authenticated evidence.
- Local committed diff observation does not retain uncommitted patch contents or inspect ignored/external side effects.
- Checks report evidence coverage, not command execution, approval or semantic correctness.
- Search/trace indexes only supplied snapshots, reports missing links, and never invents history.
- No independent behavioral proof for the candidate Skills yet; format checks are narrower.
- Kanban bridge and card-draft are not an installed adapter or runtime-enforced
  tool policy. The one successful Luna negative-path run does not prove that
  another model/run will obey the card or that a worker can execute a write task.
- The capability catalog is a synthetic metadata projection, not a delivery question
  graph or proof of actual Research, Video or Translation workflow quality. The linked
  research package is a concrete domain-owned delivery implementation; ASGK does not
  impose its exact filenames or toolchain on video and translation targets.

Ignoring this branch preserves v2. Its source commits survive temporary worktree removal;
do not delete either worktree automatically.
