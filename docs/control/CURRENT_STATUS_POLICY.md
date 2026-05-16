# Current Status Policy

Status: active control policy.

This policy prevents `docs/handoff/CURRENT_STATUS.md` from becoming an
ever-growing history log. `CURRENT_STATUS.md` is a compact recovery surface for
the next human or agent session, not a project diary.

## Core Rule

```text
CURRENT_STATUS.md is overwritten, not appended.
```

It should answer only:

```text
Where is the repo now?
What is active, if anything?
What is the next safe action?
What must not be done?
Where is the durable history?
```

## Progressive Disclosure Rule

`CURRENT_STATUS.md` is the first disclosure layer, not the full work-unit record.
It should expose the smallest sufficient repo-level state and point to durable
GitHub objects only when more detail is needed.

```yaml
progressive_disclosure_layers:
  layer_1_repo_recovery:
    surface: docs/handoff/CURRENT_STATUS.md
    purpose: next-session orientation and next safe action
    content_limit: compact repo state only
  layer_2_work_unit_detail:
    surface: GitHub issue or PR body
    purpose: objective, allowed paths, validation, and Merge Decision Record
    content_limit: current work unit only
  layer_3_history:
    surface: GitHub comments, merged PRs, and merge commits
    purpose: durable evidence and historical detail
    content_limit: append history outside CURRENT_STATUS.md
```

Do not promote lower-layer detail into `CURRENT_STATUS.md` unless it is required
for safe recovery. If more context is needed, the next actor should open the
referenced issue, PR, or canonical document instead of expanding this file.

## Ownership

```yaml
canonical_status_surface: docs/handoff/CURRENT_STATUS.md
status_policy: docs/control/CURRENT_STATUS_POLICY.md
durable_history:
  - GitHub issues
  - GitHub pull requests
  - PR comments
  - issue result comments
  - merge commits
```

## What Belongs In CURRENT_STATUS.md

Keep only compact current state:

```yaml
allowed_content:
  - last_updated timestamp
  - durable source of truth rule
  - current snapshot
  - active issue or none
  - active PR or none
  - active branch or none
  - current milestone or phase
  - validation entrypoint and current CI expectation
  - closed gates
  - next safe action
  - links or references to durable history
```

## What Must Not Go Into CURRENT_STATUS.md

Do not store history or verbose logs here.

```yaml
forbidden_content:
  - full PR body copies
  - full issue body copies
  - long chronological work logs
  - repeated completed work-unit summaries
  - old active issue blocks after merge
  - self-referential active PR blocks that become stale immediately after merge
  - raw CI logs
  - large design discussions
  - chat transcript summaries
  - runtime artifacts
```

Use GitHub issues, PRs, and comments for history.

## Work-unit Refresh Rule

Every completed work unit must make a status-refresh decision before closeout.
Do not blindly update `CURRENT_STATUS.md` for every PR, but do not leave it stale
when repo-level recovery state has changed.

`CURRENT_STATUS.md` is post-merge-safe by default. It describes the repository
state a new session should see after the current PR merges, not the temporary
in-flight state of the PR that edits it.

```yaml
current_status_modes:
  post_merge_safe:
    default: true
    meaning: "CURRENT_STATUS.md remains accurate after this PR merges."
    closeout_pr_required: false
  in_flight_tracking:
    location:
      - GitHub issue body or comment
      - PR body or Handoff Report
      - work-unit handoff packet
    meaning: "Unmerged work state for the current actor."
    current_status_role: "reference only when needed for repo-level recovery"
  separate_status_refresh:
    default: false
    allowed_only_when:
      - current main already contains stale CURRENT_STATUS.md
      - a human-gated sequence intentionally defers status until after approval
      - post-merge state cannot be known safely before merge
    closeout_pr_required: true
```

Do not use `CURRENT_STATUS.md` as the live tracker for the PR that changes it.
Open PRs, issue comments, and handoff packets are the durable in-flight record.

```yaml
status_refresh_decision:
  update_required_when:
    - active work, phase, milestone, or next safe action changes
    - release, readiness, or stabilization status changes
    - completed work exposes a new blocker, gate, or required sequence change
    - several small PRs together change the repo-level recovery state
    - a new session would make the wrong next move from current status alone
  update_not_required_when:
    - PR detail is fully represented by the issue or PR and repo-level next action is unchanged
    - the change is map-only, wording-only, or fixture-only with no recovery impact
    - updating current status would only duplicate durable GitHub history
  required_evidence:
    - PR Merge Decision Record states whether current status was updated or why not
    - issue result comment records closeout evidence
```

If status refresh is required for repo-level recovery safety but cannot be made
accurate inside the same PR, open a separate bounded status-refresh issue
immediately after closeout. Do not use this path for cosmetic cleanup,
historical observations, or PR details that are already recoverable from the
issue or PR; report those as observations unless a new session would otherwise
take the wrong action.

## Release Execution Closeout Rule

Release execution changes the repo-level recovery surface whenever a tag,
GitHub release, release title, release URL, release target commit, or release
rollback/revoke state changes.

```yaml
release_execution_status_closeout:
  required_when:
    - git tag is created, deleted, moved, or revoked
    - GitHub release is created, edited, deleted, or revoked
    - release target commit changes
    - release notes or rollback/revoke plan materially change
  same_pr_allowed_when:
    - release execution work includes authorized file changes
    - CURRENT_STATUS.md can be made post-merge-safe before merge
  metadata_only_release_path:
    rule: "Do not edit files in the release execution work unit."
    required_follow_up:
      - create an immediate bounded status-refresh issue
      - open a status-only PR for docs/handoff/CURRENT_STATUS.md
      - record the follow-up issue or PR in the release execution closeout comment
  release_not_fully_closed_until:
    - CURRENT_STATUS.md is accurate for the post-release repo state
    - or a bounded status-refresh issue exists and is linked from the release issue closeout
```

A metadata-only release issue may close after tag/release creation only if its
closeout comment records the immediate status-refresh follow-up. Otherwise, the
release has been executed but the repo handoff surface is not fully closed out.

## PR Status Freshness Gate

Every PR must explicitly classify its `CURRENT_STATUS.md` impact in the PR body.
This is a review gate, not a requirement that every PR edits the status file.

```yaml
current_status_update_gate:
  required_for_all_prs: true
  allowed_values:
    - updated
    - not_applicable
    - deferred
  update_required_when:
    - active milestone changes
    - active issue or active PR changes
    - next safe action changes
    - last completed work changes
    - release readiness or stabilization status changes
    - roadmap or milestone register changes
    - install surface, target-install tooling, or decision governance changes
    - a new handoff-relevant command is added
    - a new session would make the wrong next move from CURRENT_STATUS.md alone
  not_applicable_when:
    - typo-only or formatting-only change
    - fixture-only change with no recovery-state impact
    - map/registry wording-only change with no active work or next-action impact
  deferred_allowed_when:
    - current PR cannot accurately write post-merge status without becoming self-stale
    - status update requires a separate bounded closeout/status-refresh issue
    - human gate or follow-up sequence must be resolved first
  deferred_required_evidence:
    - reason in PR Current Status Impact section
    - follow-up issue or next safe action in Handoff Report when repo-level recovery would otherwise be unsafe
  post_merge_safe_required_when:
    - status is updated
    - docs/handoff/CURRENT_STATUS.md changes in the PR
```

Reviewers should request changes when a milestone-impacting or resume-surface-impacting
PR marks `not_applicable` without a clear reason, or when `deferred` lacks a
follow-up path.

## In-flight PR Boundary

In-flight PR detail belongs in the PR body, PR comments, or a work-unit handoff
packet, not necessarily in `CURRENT_STATUS.md`.

A PR that changes `CURRENT_STATUS.md` must not merge a self-referential active
work block that points to the same PR as active, because the status becomes stale
as soon as the PR merges.

```yaml
self_staling_status_update:
  forbidden_when:
    - current_status.active_pr == this_pr
    - this_pr_is_expected_to_merge
    - no post_merge_status_repair is included
  preferred_pattern:
    - keep in-flight details in the PR body and Merge Decision Record
    - make CURRENT_STATUS.md accurate for the repository state after merge
    - use GitHub comments for closeout evidence
```

PR bodies should record this explicitly:

```yaml
current_status_impact:
  status: updated | not_applicable | deferred
  reason: "<why this status decision is correct>"
  current_status_updated_in_this_pr: true | false
  post_merge_safe: true | false | not_applicable
  follow_up_issue: none | "#<number>"
```

## Compact Handoff Freshness Check

Compact handoff may reduce repeated recovery prose only when it remains
checkable against this policy.

```bash
python3 scripts/asgk.py compact-handoff-check \
  --file handoff.yaml \
  --current-status docs/handoff/CURRENT_STATUS.md \
  --completed-issue "#123" \
  --completed-pr "#124" \
  --completed-branch codex/example
```

The check blocks compact handoffs that hide stale active work. A
`not_applicable` status-impact decision is valid only when the current-status
active-work block does not still name completed work and the next safe action
does not describe pre-merge closeout work.

`post_merge_safe: true` means `CURRENT_STATUS.md` will still be accurate after
the PR merges. If that cannot be stated truthfully, leave the file unchanged and
record in-flight details in the PR body, issue comment, or handoff packet.

## Overwrite-not-append Rule

After a work unit completes:

1. Update result evidence in the issue or PR comment.
2. Close or merge the durable GitHub object when appropriate.
3. Decide whether `CURRENT_STATUS.md` requires a repo-level refresh under the work-unit refresh rule.
4. If refresh is required, replace the active work, snapshot, last-completed reference, and next safe action sections.
5. Do not append a completed-work history section unless it is a short link-only reference.

Recommended replacement pattern:

```yaml
active_work:
  issue: none
  pr: none
  branch: main
next_safe_action: "Open the next bounded issue from the roadmap."
last_completed:
  issue: "#40"
  pr: "#41"
  merge_commit: "1ec327e"
  note: "Details are in GitHub; do not duplicate here."
```

## Post-merge Closeout Rule

Before a low-risk PR is marked merge-allowed, check whether the PR changes
`docs/handoff/CURRENT_STATUS.md`.

```yaml
post_merge_closeout_check:
  if_current_status_changed:
    - current_status_must_be_valid_after_this_pr_merges
    - active_issue_must_not_be_the_issue_closed_by_this_pr_unless_followup_keeps_it_open
    - active_pr_must_not_be_this_pr
    - next_safe_action_must_not_point_to_this_prs_pre_merge_steps
  evidence_location:
    - PR Merge Decision Record
    - issue result comment
```

If an accurate post-merge status cannot be written inside the same PR, leave
`CURRENT_STATUS.md` unchanged and record work-unit state in the PR body or a
handoff packet instead. Open a separate bounded status-refresh issue only when
repo-level recovery would otherwise be unsafe.

For local-only mechanical closeout checks, use:

```bash
python3 scripts/asgk.py closeout-check \
  --completed-pr '#<pr>' \
  --completed-branch '<branch>'
```

The check is deliberately local-only: it checks supplied closeout markers
against `CURRENT_STATUS.md`. It does not query GitHub issue or PR state, and it
does not prove that the GitHub issue closeout comment contains the required
decision-analysis block. Use `docs/handoff/ISSUE_CLOSEOUT_REVIEW_RULES.md` only as
the writing guide for that comment, not as a repo-local history ledger.

## Size And Compaction Rules

`CURRENT_STATUS.md` should stay small enough to read every session.

```yaml
soft_limits:
  max_lines: 120
  max_active_work_units: 1
  max_last_completed_items: 3
  max_next_safe_actions: 1
```

If the file exceeds the soft limit:

1. Remove completed-work narrative.
2. Replace details with issue/PR numbers.
3. Keep only current active state and next safe action.
4. Move reusable rules into canonical control docs.
5. Move history into GitHub comments.

## Staleness Rules

A status file is stale when:

```yaml
stale_when:
  - active_issue is closed but still listed as active
  - active_pr is merged or closed but still listed as active
  - active_pr points to the PR that just merged this status file
  - next_safe_action points to completed work
  - next_safe_action points to pre-merge validation for an already merged PR
  - last_updated is older than the last merged governance PR that changed repo-level recovery state
  - runtime-specific profile work appears as active in v1.x without a v2.0 issue
```

When stale status is found, open a bounded docs issue or update it in the active
handoff/closeout PR.

## Current Status Template

```md
# Current Status

Last updated: `<UTC timestamp>`

## Durable source of truth

- GitHub issues, PRs, comments, and repository files are authoritative.
- Chat memory is not authoritative.

## Current snapshot

<one compact paragraph>

## Active work

```yaml
issue: none | "#<number> <title>"
pr: none | "#<number> <title>"
branch: main | "<branch>"
state: idle | active | blocked
```

## Current validation entrypoint

```bash
python3 scripts/asgk.py doctor
```

## Closed gates

- <gate>

## Last completed

```yaml
issue:
pr:
merge_commit:
note: "Details are in GitHub."
```

## Next safe action

<one bounded action>
```

## Relationship To Handoff Packet

`CURRENT_STATUS.md` is repo-level status. A handoff packet is work-unit-level
status.

Use `docs/control/HANDOFF_PACKET.md` when switching actors, tools, or sessions
inside an active work unit.

## Local Automation

`asgk closeout-check` verifies the local, caller-supplied closeout state only.
It may be used before merge or after merge when a completed issue, PR, or branch
must not remain active in `CURRENT_STATUS.md`.

```yaml
closeout_check_targets:
  - supplied completed issue is not in active work
  - supplied completed PR is not in active work
  - supplied completed branch is not in active work
  - next_safe_action is present
  - next_safe_action does not point to completed pre-merge work
```

`asgk status-check` remains the broader compactness and stale-marker check for
routine session startup and baseline validation.

For PR-specific current-status decisions, use:

```bash
python3 scripts/asgk.py current-status-impact-check \
  --pr-body pr.md \
  --changed-paths-file changed-paths.txt \
  --this-pr '#<pr>' \
  --closing-issue '#<issue>' \
  --this-branch '<branch>'
```

The command is local-only and does not query GitHub. It checks that the PR body,
changed paths, and `CURRENT_STATUS.md` agree, and that updated status is
post-merge-safe instead of pointing at the PR or branch that is about to merge.
