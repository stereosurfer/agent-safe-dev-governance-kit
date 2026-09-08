# ASGK 3.0 preview handoff

## Current work

- Durable scope: [#357](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/357).
- Branch: `codex/asgk-3-preview`.
- Baseline main: `999d5a37a34c2484212b104b6234f5b0fbe5b09a`.
- This additive experiment does not resume or close #323/#356. Existing W6B dirty
  work remains in its original worktree. No merge, release or migration is authorized.
- Only the seven files listed in #357 belong to this work unit. The excluded visual
  guide is not read or included.

## What exists

Design-first contract, Python standard-library CLI, synthetic example, adversarial
tests, offline walkthrough and manual persistent-Bot testing protocol. Central rules
are represented as input ceilings; persistent policy storage, runtime enforcement and
platform integration are not implemented. This is a first vertical slice, not full v3.

## Recovery / next step

Read `v3/README.md`, `v3/DESIGN.md`, this file and #357. Use `v3/TESTING.md` only when
testing. Run the demo in a new temporary directory. Generated files stay out of git.
The user's next decision is based on hands-on results, not an automatic migration.
Do not inherit old roadmap scope or treat this document as approval of a new work unit.

In-place editing and incomplete-work recovery remain explicit limitations. No real
Bot/provider/human cold-start test, independent reviewer, target pilot, CI run, merge
approval or production security assurance is claimed. Local validation evidence is
recorded in #357; a green local suite only checks its declared predicates.

## Rollback

The original branch and worktree are unchanged. Ignore this branch to keep using v2;
do not delete either worktree or rewrite history automatically. Source commits retain
the experiment even if its temporary working directory is later removed.
