# 11 Auto-merge Policy

Auto-merge is not a trust decision. It is a consequence of passing explicit, versioned, testable rules.

## auto_merge_allowed_when

```yaml
auto_merge_allowed_when:
  - PR is linked to an approved issue
  - lane is declared and matches the issue
  - intelligence level is declared and justified
  - durable source of truth is a GitHub issue or PR for executable work
  - objective, plan, checklist, and acceptance sheet are outside chat
  - changed files are inside allowed paths
  - expected output is declared and matches the issue
  - protected paths are untouched
  - storage-boundary evidence is present
  - tests pass
  - scaffold validation passes
  - bootstrap validation passes
  - schema validation passes when schemas changed
  - acceptance criteria are checked
  - Agent Report is complete
  - Merge Decision Record is complete and allows merge
  - handoff status is updated
  - no new dependency is added
  - no schema breaking change is included
  - no new cloud egress is added
  - no API/model call lane is opened
  - no MCP write tool is added
```

## auto_merge_forbidden_when

```yaml
auto_merge_forbidden_when:
  - protected path changed
  - security boundary changed
  - storage boundary changed
  - schema breaking change
  - database migration
  - new dependency added
  - new cloud API
  - new telemetry
  - new parser/model dependency
  - new MCP tool
  - generated artifact promoted without validation
  - private source data touched
  - CI is skipped
  - reviewer and implementer are the same agent for policy changes
  - lane or task packet is missing from the PR
  - objective, plan, checklist, or acceptance sheet exists only in chat
  - durable source of truth is missing or says see chat
  - executable work relies on a task packet or repo document instead of a GitHub issue or PR while GitHub is available
  - intelligence level or reason is missing
  - allowed paths are missing or contradicted
  - expected output is missing or contradicted
  - storage-boundary evidence is missing
  - Merge Decision Record is missing or blocks merge
```

## Merge Decision Record

Each PR must include the YAML block defined in `docs/control/MERGE_DECISION_RECORD.md`.
