# Compact PR Body Profile

Status: opt-in profile. This file does not change the default PR template.

Compact PR bodies may reduce repeated issue scope, changed-path, and validation
prose only when they reference a compiled compact PR report produced by ASGK
tooling.

The compact profile still requires the default PR review gates:

- `Current Status Impact`
- `Merge Decision`
- `Task Reference`
- `Scope Boundaries`
- `Handoff Report`

## Required Reference

Compact PR bodies must include:

````markdown
## Compiled Report Reference

```yaml
compact_pr_report:
  report_source: path, PR artifact, or PR comment containing the report
  report_result: pass
  pr_status_result: pass
  low_risk_inferred: false
```
````

The PR body reference is not authority by itself. The report JSON must also be
checked with:

```bash
python3 scripts/asgk.py compact-pr-body-check --body-file <body> --report-json <report>
```

The check fails if the PR body is missing required governance sections, the
policy gate fails, the compiled report is not passing, the report has findings,
or the report does not explicitly keep `low_risk_inferred: false`.

## Non-Goals

- Do not make compact PR bodies the default.
- Do not remove `Current Status Impact`.
- Do not remove `Merge Decision`.
- Do not treat a report reference as merge authority.
- Do not infer low-risk status from compact artifacts.
