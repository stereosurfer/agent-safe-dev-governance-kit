# Current Status

This is a compact negative fixture for stale active work.

Last updated: `2026-05-15T00:00:00Z`

## Durable source of truth

- GitHub issues, PRs, comments, releases, and repository files are authoritative.

## Current snapshot

Negative fixture that still points active work at completed package 6.

## Active work

```yaml
issue: "#240 Add compact PR body profile"
pr: "#241 Add compact PR body profile check"
branch: codex/compact-pr-body-profile-240
state: merged
```

## Current validation entrypoint

```bash
python3 scripts/asgk.py doctor
```

## Closed gates

- compact artifacts do not infer low-risk status

## Last completed

```yaml
issue: "#238"
pr: "#239"
state: "merged"
```

## Runtime artifact status

No runtime artifacts are authorized.

## Next safe action

Continue only after repairing this stale active-work block.
