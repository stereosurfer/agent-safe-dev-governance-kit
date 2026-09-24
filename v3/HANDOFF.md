# ASGK 3.0 candidate lineage handoff

The GitHub workflow and optional catalog CLI are now canonical under
`scripts/asgk_lib/`, exposed as `python3 scripts/asgk.py workflow` and
`python3 scripts/asgk.py catalog` through #397 and #399, respectively. This file records preview.1
history and remaining candidate limits; it is not the repository recovery
snapshot. Read root `AGENTS.md`, `README.md`,
`docs/handoff/CURRENT_STATUS.md`, and the live work issue first.

## Current authority and lineage

- [#372](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/372) coordinates the formal 3.0 release program. One live child issue or qualifying PR, not this handoff or #372 alone, authorizes a source change.
- Preview.1's earlier scoped design review is [#359](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/359).
- Parent candidate: [#358](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/358), commit af7b143fa5b0d3c33d3b9e0cbe8f64434ee124ea.
- Rejected direction retained: [#357](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/357), local commit 7e2cfc6.
- Branch: `codex/asgk-3-preview.1`; resolve its **live** head before a new action. Its last completed field-test baseline is [PR #371](https://github.com/stereosurfer/agent-safe-dev-governance-kit/pull/371)'s merge `1e0d82109141fe083f3fa469145200c6f7b3c3d0`, not a guarantee that the branch still points there. The original preview branch is separate.
- [#362](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/362)'s provenance correction was integrated by [PR #369](https://github.com/stereosurfer/agent-safe-dev-governance-kit/pull/369) into preview.1 as `62438b4c3c6439678226498b0ebc75d26a639fa3`; [#368](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/368) closed after that non-default-base merge.
- [#370](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/370)'s observed Lesson was integrated by PR #371. Its [closeout](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/370#issuecomment-5806869845) preserves the pre-merge MDR timing exception: the OWNER merged the reviewed head, but the PR body's earlier `merge_blocked`/pending record must not be rewritten as an on-time gate pass.
- [#377](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/377)'s entry/handoff recovery was integrated by [PR #380](https://github.com/stereosurfer/agent-safe-dev-governance-kit/pull/380) into preview.1 as `1d530176f05880ef90e36cfb2eccc87cb6c5bbb3`; it did not change main by itself.
- [#381](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/381) was the bounded candidate-subtree import decision. #397 integrates the GitHub workflow and #399 the optional metadata-only catalog into the root CLI. Neither activates templates, source Skills, target migration, release or global Skill synchronization. Earlier W6B and status PRs remain historical evidence, not next-work routing.

## Candidate recovery

For an actual repository mutation, start with the **current main** `AGENTS.md`,
`README.md`, `docs/handoff/CURRENT_STATUS.md`, and the selected live issue or PR.
The preview branch's root copies may lag main; if instructions conflict, stop.
For candidate recovery, read [README](README.md) and this handoff first. Expand
only for the question: [DESIGN](DESIGN.md) for ownership/architecture,
[TESTING](TESTING.md) for checks, [KANBAN_BRIDGE](KANBAN_BRIDGE.md) for a Hermes
run, or [CAPABILITY_EVOLUTION](CAPABILITY_EVOLUTION.md) for Lessons. Open the
relevant `v3/skills` entrypoint only when its procedure is needed. Follow links
to #357–#371 for a specific decision trace; do not load that history by default.
The live child issue or PR still supplies exact allowed paths and validation.

The prior standalone compiler/receipt demo has been replaced by the root
`scripts/asgk.py workflow` entrypoint. GitHub issue parsing and refinement
reuse existing source functions. Its commands capture
read-only snapshots, project an issue, preserve partial handoff, draft issue closeout,
and search/trace linked GitHub comments. In-place committed changes are supported.

The eleven `v3/skills` candidate Skills are reviewed proposals, not the eleven
current root `skills/` instructions or a second governance authority. Do not
install them alongside the root set; load only the one needed for
the current role. A completed closeout keeps closed unmerged PR attempts beside
the merged replacement and blocks unresolved open attempts.

## Evidence and next action

Parent-candidate checks, failures and live-read provenance remain in #358 comments.
Preview.1's bounded checks and research-reference correction belong to #359;
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

The separate [#367](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/367) Hermes issue-comment write test and #370 fixed-path Lesson commit are field evidence, not a v3 CLI posting feature or an installed runtime adapter. Check their own issue records for current credential and closeout state before relying on them.

The linked [research-runtime-macos delivery contract](https://github.com/stereosurfer/research-runtime-macos/blob/d09eac50c3cd12c1427dadaf5c09d1c8f7dfd38e/docs/PACKAGE_FORMAT.md)
and [synthetic example](https://github.com/stereosurfer/research-runtime-macos/tree/d09eac50c3cd12c1427dadaf5c09d1c8f7dfd38e/examples/research-package-demo)
have been compared with this candidate. They demonstrate a stable answer contract,
topic-local question ledger, an `AGENT_ENTRY` → question node → observation →
evidence unit reading route, human handoff, source map and separate raw audit layer.
Preview.1 now distinguishes this task-owned delivery graph from its optional
cross-work capability catalog. The catalog is not a replacement for the package
contract and does not validate research completion.
The #370 Lesson remains `observed`; PR #371's review/merge/closeout provide a
decision trail, not independent reproduction, Skill promotion or later-use proof.
Do not interpret “candidate works” as authority to migrate other repos or finish W1–W10.
Preserve the rejected attempt and correction links; no reset, force push or silent deletion.

## Known implementation limits

- The root workflow CLI does not automate GitHub posting, PR creation, merge, closure, Bot setup or publication. Separate #367/#370 field tests used other scoped tools; they are not CLI features.
- Capture is not atomic; a saved snapshot is not live authority or authenticated evidence.
- Local committed diff observation does not retain uncommitted patch contents or inspect ignored/external side effects.
- Checks report evidence coverage, not command execution, approval or semantic correctness.
- Search/trace indexes only supplied snapshots: duplicate-free JSON gets a bounded
  shape-checked edge, while YAML closeouts remain visible only as unverified
  candidate URLs and make the affected lookup incomplete. It reports missing
  links and never invents history, authorship, approval or YAML semantics.
  Supply only one selected snapshot per issue and one observation per PR; a
  visited closed issue with no recognizable supplied closeout warns, and even
  a JSON pass is not proof of historical completeness.
- No independent behavioral proof for the candidate Skills yet; format checks are narrower.
- Kanban bridge and card-draft are not an installed adapter or runtime-enforced
  tool policy. The one successful Luna negative-path run does not prove that
  another model/run will obey the card. #367 and #370's separately scoped writes
  do not prove general write confinement or production safety.
- The optional capability catalog is a metadata projection, not a delivery question
  graph or proof of actual Research, Video or Translation workflow quality. The linked
  research package is a concrete domain-owned delivery implementation; ASGK does not
  impose its exact filenames or toolchain on video and translation targets.

Presence of this subtree on `main` changes no root operating rule by itself.
#397 makes the GitHub workflow implementation/CLI canonical; #399 does the same
for optional metadata-only catalog discovery, not the full `v3/` subtree. Preview.1
and its source commits preserve candidate lineage; do not delete a branch or
worktree automatically.
