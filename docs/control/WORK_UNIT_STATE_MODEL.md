# Work Unit State Model

```yaml
states:
  idea:
    meaning: raw concept, not executable
  task_packet_ready:
    meaning: objective, scope, paths, checks, and acceptance exist
  agent_working:
    meaning: assigned agent is executing the packet
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
- `task_packet_ready` requires durable source of truth.
- `accepted` requires validation evidence.
- `merged` requires Merge Decision Record or explicit human approval.
