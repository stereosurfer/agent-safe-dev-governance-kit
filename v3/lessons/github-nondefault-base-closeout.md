---
state: observed
---
# Non-default-base PR closeout: one observed case

## Observation
Issue [#368](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/368) was manually closed after [PR #369](https://github.com/stereosurfer/agent-safe-dev-governance-kit/pull/369) merged into `codex/asgk-3-preview.1`, a non-default base. The worker read the [#368 closeout comment](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/368#issuecomment-5805341585), as recorded in the [redacted #370 call trace](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/370#issuecomment-5806593354). That comment states PR #369 merged as `62438b4c3c6439678226498b0ebc75d26a639fa3` and instructs manual issue closure because the non-default-base merge cannot auto-close #368. The PR and merge commit are cited within that closeout; they were not separately read by the worker for this Lesson.

## Applicability
Inspect this Lesson when closing out a linked issue after a PR to a non-default branch has merged, and verify the issue's actual state and development linkage rather than assuming closure from merge status.

## Not established
This is one case, not a universal GitHub rule. It does not establish that every PR merge requires manual issue closure. A not-yet-tested counterexample is a PR targeting the repository's default branch with a recognized closing keyword; whether and when that closes a linked issue is not tested here.

## Evidence limits and next gate
The closeout comment is the observed source for PR #369's target, merge SHA, and manual closure. The PR and commit were not independently inspected in this observation. No mechanism beyond the closeout's account, broader platform behavior, or other repository configuration was verified. Next, independently test a default-branch closing-keyword case and a non-default-base case, reading live issue and PR states before drawing any broader conclusion. Keep this Lesson observed; do not promote it to a Skill rule.
