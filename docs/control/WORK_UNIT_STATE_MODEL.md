# Work Unit State Model

```yaml
states:
  idea:
    meaning: raw concept, not executable
  scoped:
    meaning: objective, scope, paths, checks, and acceptance exist
  in_progress:
    meaning: the authorized issue or PR is being worked
  pr_open:
    meaning: repository change exists in pull request
  needs_review:
    meaning: diff/report/checks require evaluation
  needs_revision:
    meaning: PR is useful but not acceptable yet
  blocked:
    meaning: missing input, failing gate, or human decision required
  accepted:
    meaning: acceptance criteria satisfied
  merged:
    meaning: durable repo state updated
```

## Transition rules

- `idea` cannot go directly to `pr_open` or `merged`.
- `scoped` requires a GitHub issue or PR for executable work when
  GitHub is available. A task packet may refine the scope, but it cannot be the
  primary authorization for file edits.
- `accepted` requires validation evidence.
- `merged` requires Merge Decision Record or explicit human approval.
