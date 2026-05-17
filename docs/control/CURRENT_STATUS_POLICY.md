# Current Status Policy

Status: active control policy.

This policy defines how `docs/handoff/CURRENT_STATUS.md` stays a compact
repo-level recovery surface instead of becoming a diary, PR tracker, release log,
or issue closeout ledger.

## Purpose

```text
CURRENT_STATUS.md is overwritten, not appended.
```

It should answer only:

```text
Where is the repo now?
What is active, if anything?
What is the next safe action?
What must not be done?
Where is durable history kept?
```

## Document Boundary

```yaml
this_policy_owns:
  - when CURRENT_STATUS.md should be updated
  - when CURRENT_STATUS.md should stay unchanged
  - post-merge-safe status requirements
  - PR Current Status Impact classification
  - stale current-status classification
  - current-status size and compaction rules
  - local automation boundaries for status-related checks

this_policy_does_not_own:
  - work-unit handoff packet fields
  - issue closeout review writing rules
  - PR body template headings
  - release approval or execution policy
  - historical work logs
  - validator implementation details

canonical_neighbors:
  repo_status_surface: docs/handoff/CURRENT_STATUS.md
  work_unit_handoff: docs/control/HANDOFF_PACKET.md
  issue_closeout_review_rules: docs/handoff/ISSUE_CLOSEOUT_REVIEW_RULES.md
  pr_body_shape: .github/PULL_REQUEST_TEMPLATE.md
  release_policy: docs/control/SOURCE_ONLY_RELEASE_POLICY.md
  command_interface: python3 scripts/asgk.py --help
```

## Ownership

```yaml
canonical_status_surface: docs/handoff/CURRENT_STATUS.md
status_policy: docs/control/CURRENT_STATUS_POLICY.md
durable_history:
  - GitHub issues
  - GitHub pull requests
  - GitHub issue and PR comments
  - GitHub releases
  - merge commits
```

`CURRENT_STATUS.md` is read by default during startup. Therefore it must stay
small, current, and recoverable without requiring a full repository scan.

## Progressive Disclosure

Keep the layers separate:

| Layer | Surface | Owns |
|---|---|---|
| repo recovery | `docs/handoff/CURRENT_STATUS.md` | current repo state and next safe action |
| work-unit detail | GitHub issue, PR body, or handoff packet | objective, allowed paths, validation, and Merge Decision Record |
| history | GitHub comments, merged PRs, releases, and merge commits | durable evidence and completed-work detail |

Do not promote lower-layer detail into `CURRENT_STATUS.md` unless a new session
would make the wrong next move without it.

## Allowed And Forbidden Content

```yaml
allowed_content:
  - last_updated timestamp
  - durable source of truth rule
  - compact current snapshot
  - active issue, PR, and branch, or none
  - current validation entrypoint
  - closed gates
  - last completed work as a short durable reference
  - next safe action

forbidden_content:
  - full issue or PR body copies
  - long chronological work logs
  - repeated completed work-unit summaries
  - stale active issue or PR blocks after merge
  - self-referential active PR blocks that become stale immediately after merge
  - raw CI logs
  - large design discussions
  - chat transcript summaries
  - routine issue closeout reviews
  - runtime artifacts or private source material
```

History belongs in GitHub. Reusable rules belong in canonical control documents.

## Status Refresh Decision

Every completed work unit must decide whether repo-level status changed. The
decision belongs in the PR `Current Status Impact` section and closeout evidence.

```yaml
update_required_when:
  - active work, phase, milestone, or next safe action changes
  - release, readiness, stabilization, public visibility, license, or distribution state changes
  - completed work exposes a new blocker, closed gate, or required sequence change
  - several small PRs together change repo-level recovery state
  - a new session would make the wrong next move from CURRENT_STATUS.md alone

update_not_required_when:
  - PR detail is fully represented by the issue or PR
  - repo-level next safe action is unchanged
  - the change is typo-only, wording-only, fixture-only, or map-only
  - updating status would only duplicate durable GitHub history

defer_only_when:
  - post-merge state cannot be known safely before merge
  - a human-gated sequence must resolve first
  - a separate bounded status-refresh issue is needed for recovery safety
```

Do not create status-refresh work merely because a historical observation exists.
Apply `docs/control/ISSUE_HYGIENE_GATE.md` before turning observations into
follow-up issues.

## PR Current Status Impact Gate

Every PR must classify current-status impact in the PR body. This is a review
gate, not a requirement that every PR edits `CURRENT_STATUS.md`.

```yaml
current_status_impact:
  status: updated | not_applicable | deferred
  reason: "<why this status decision is correct>"
  current_status_updated_in_this_pr: true | false
  post_merge_safe: true | false | not_applicable
  follow_up_issue: none | "#<number>"
```

Reviewers should request changes when:

```yaml
request_changes_when:
  - Current Status Impact is missing
  - status value is not updated, not_applicable, or deferred
  - reason is missing or generic
  - CURRENT_STATUS.md changes but status is not updated
  - status is updated but CURRENT_STATUS.md did not change
  - deferred lacks a follow-up path when repo recovery would otherwise be unsafe
```

## Post-merge-safe Rule

`CURRENT_STATUS.md` describes the repository state after the PR merges, not the
temporary in-flight state of the PR that edits it.

```yaml
post_merge_safe_required_when:
  - current_status_impact.status == updated
  - docs/handoff/CURRENT_STATUS.md changes in the PR

self_staling_status_update_forbidden_when:
  - active_pr names the PR that is about to merge
  - active_issue names an issue that will close on merge
  - next_safe_action points to pre-merge checks for the same PR
  - branch names the branch that will be deleted or completed on merge
```

In-flight work detail belongs in the issue, PR body, PR comments, or a
work-unit handoff packet.

## Release Execution Closeout

Release execution changes repo-level recovery state whenever tag, GitHub release,
release title, release URL, target commit, rollback, or revoke state changes.

```yaml
release_status_refresh_required_when:
  - git tag is created, deleted, moved, or revoked
  - GitHub release is created, edited, deleted, or revoked
  - release target commit changes
  - release notes or rollback/revoke plan materially change

release_not_fully_closed_until:
  - CURRENT_STATUS.md is accurate for the post-release repo state
  - or a bounded status-refresh issue exists and is linked from release closeout
```

Metadata-only release execution should not edit repo files in the release issue.
If release metadata changes require repo-level status refresh, create a bounded
status-refresh issue and link it from release closeout.

## Post-merge Closeout

After a PR merges:

```yaml
closeout_requires:
  - PR merge state confirmed
  - closing issue state confirmed
  - compact issue comment with completion evidence
  - required issue_closeout_review block in the GitHub issue comment
  - current-status refresh decision
```

Routine issue closeout reviews belong in GitHub issue comments under
`docs/handoff/ISSUE_CLOSEOUT_REVIEW_RULES.md`. They must not be copied into
`CURRENT_STATUS.md` or into a repo-local ledger.

Open a status-refresh issue only when leaving `CURRENT_STATUS.md` unchanged would
mislead the next session.

## Size And Compaction

`CURRENT_STATUS.md` should stay small enough to read every session.

```yaml
soft_limits:
  max_lines: 120
  max_active_work_units: 1
  max_last_completed_items: 3
  max_next_safe_actions: 1
```

When it grows too large:

```yaml
compact_by:
  - remove completed-work narrative
  - replace detail with issue, PR, release, or merge references
  - keep only current active state and next safe action
  - move reusable rules into canonical control docs
  - keep historical evidence in GitHub
```

## Staleness Rules

`CURRENT_STATUS.md` is stale when:

```yaml
stale_when:
  - active issue is closed but still listed as active
  - active PR is merged or closed but still listed as active
  - active PR points to the PR that just merged the status file
  - active branch points to completed or deleted work
  - next safe action points to completed work
  - next safe action points to pre-merge validation for an already merged PR
  - repo-level release, milestone, or recovery state changed but status did not
  - runtime-specific profile work appears as active in v1.x without a v2.0 issue
```

When stale status is found, repair it in the active handoff/closeout PR when in
scope. Otherwise open a bounded issue only when stale status would mislead the
next session.

## Current Status Shape

`CURRENT_STATUS.md` should keep this compact shape:

```text
# Current Status
Last updated: `<UTC timestamp>`

## Durable source of truth
## Current snapshot
## Active work
## Current validation entrypoint
## Closed gates
## Last completed
## Runtime artifact status
## Next safe action
```

The active work block should name one issue, one PR, one branch, and one state,
or `none` when no work is active.

## Relationship To Handoff Packet

`CURRENT_STATUS.md` is repo-level status. A handoff packet is work-unit-level
status.

Use `docs/control/HANDOFF_PACKET.md` when switching actors, tools, or sessions
inside an active work unit. Do not expand `CURRENT_STATUS.md` to replace the
handoff packet.

## Local Automation Boundary

Status-related commands check local files and supplied metadata. They do not
replace live GitHub closeout review or human judgment.

```yaml
status_check:
  command: python3 scripts/asgk.py status-check
  owns: compactness and stale-marker checks for CURRENT_STATUS.md

closeout_check:
  command: python3 scripts/asgk.py closeout-check
  owns: caller-supplied completed issue, PR, or branch is not still active in CURRENT_STATUS.md
  does_not_own:
    - live GitHub issue or PR state
    - required issue closeout review comment

current_status_impact_check:
  command: python3 scripts/asgk.py current-status-impact-check
  owns: PR body, changed paths, and CURRENT_STATUS.md agree locally
  does_not_own:
    - live GitHub state
    - final merge approval
```

Use command-specific help for exact syntax:

```bash
python3 scripts/asgk.py <command> --help
```
