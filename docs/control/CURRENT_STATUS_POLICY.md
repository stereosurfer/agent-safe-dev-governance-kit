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
  - raw CI logs
  - large design discussions
  - chat transcript summaries
  - runtime artifacts
```

Use GitHub issues, PRs, and comments for history.

## Overwrite-not-append Rule

After a work unit completes:

1. Update result evidence in the issue or PR comment.
2. Close or merge the durable GitHub object when appropriate.
3. Replace the active work section in `CURRENT_STATUS.md`.
4. Do not append a completed-work history section unless it is a short link-only reference.

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
  - next_safe_action points to completed work
  - last_updated is older than the last merged governance PR that changed work state
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

## Future Automation

A future `asgk status-check` may verify:

```yaml
status_check_targets:
  - active issue is open or marked none
  - active PR is open or marked none
  - next_safe_action is present
  - file does not exceed soft size limit
  - no forbidden history sections are present
```

Do not implement that checker in this policy-only work unit.
