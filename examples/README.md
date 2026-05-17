# Examples And Fixtures

Status: repository-local reference and validation material.

This directory contains more than one kind of file. Do not treat everything
under `examples/` as an adoption template.

## Taxonomy

```yaml
human_examples:
  purpose: small positive examples that humans and agents may inspect for shape
  authority: not policy authority
  examples:
    - examples/task_packet.example.yaml
    - examples/merge_decision.example.json
    - examples/agent_report.example.md
machine_fixtures:
  purpose: validator inputs used by local checks, CI, or focused commands
  authority: test input only
  examples:
    - examples/pr_status.valid.json
    - examples/work_unit.valid-issue.json
negative_expected_failures:
  purpose: known-bad inputs that must fail under opt-in negative checks
  authority: regression fixture only
  location: examples/negative/
compact_red_team_fixtures:
  purpose: compact-governance tool-state and claim-conflict test inputs
  authority: regression fixture only
  locations:
    - examples/compact_governance/
    - examples/negative/compact_governance/
```

## Boundary Rules

- Examples and fixtures are not policy authority.
- Target repositories must not copy this directory as an adoption bundle.
- Negative fixtures are intentionally invalid and must not be used as positive
  examples.
- Historical issue, PR, CI, and release evidence belongs in GitHub, not as
  copied narrative inside this directory.
- Agents should not read this directory during default startup; read only the
  specific fixture or example named by the current issue, PR, validator, or
  documentation reference.

If a file here conflicts with a canonical policy, schema, contract, validator,
or GitHub issue/PR, fix the file or the stale reference in a scoped issue.
