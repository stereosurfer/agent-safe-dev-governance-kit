# Examples And Fixtures

Status: repository-local reference and validation material.

This directory contains more than one kind of file. Do not treat everything
under `examples/` as an adoption template.

## Taxonomy

```yaml
human_examples:
  purpose: small positive examples that humans and agents may inspect for shape
  authority: not policy authority
  task_packet_boundary: examples show one mode; fallback local-work authority is conditional on verified GitHub unavailability and never grants PR or merge authority
  examples:
    - examples/task_packet.example.yaml
    - examples/merge_decision.example.json
    - examples/agent_report.example.md
machine_fixtures:
  purpose: validator inputs used by local checks, CI, or focused commands
  authority: test input only
  executable_expectation_owner: scripts/asgk_lib/scenario_registry.py
  work_unit_boundary: valid work-unit fixtures carry the 13 canonical fields plus both execution gates
  examples:
    - examples/pr_status.valid.json
    - examples/work_unit.valid-issue.json
source_inventory_fixtures:
  purpose: required-path inclusion inputs for the ASGK source reference-superset validator
  authority: source-validator input only; not a target manifest or adoption surface
  positive: examples/source_validation/reference-superset.valid.json
  negative: examples/negative/source_validation/missing-required-path.json
  proof_limit: listed paths are not opened, read, or semantically evaluated in supplied-inventory mode
negative_expected_failures:
  purpose: inputs expected to trigger current opt-in mechanical checks
  authority: regression fixture only
  expected_outcome_boundary: fixture metadata is descriptive; exact executable expectations live in the scenario registry or an explicitly bounded legacy group
  proof_limit: not every mechanical failure establishes a semantic repository defect
  location: examples/negative/
compact_red_team_fixtures:
  purpose: legacy compact-governance inputs retained pending separately scoped deletion
  authority: inactive legacy input only; not a doctor or negative-all prerequisite, second compact-governance oracle, or retained JSON expectation owner
  locations:
    - examples/compact_governance/
    - examples/negative/compact_governance/
```

## Boundary Rules

- Examples and fixtures are not policy authority.
- A fixture supplies input, not its own expected result. For retained JSON
  behavior, `scripts/asgk_lib/scenario_registry.py` alone records the exact
  owner command, polarity, exit, common result, finding-code multiset,
  human-gate state, and proof boundary. Branch-specific cases may also lock
  exact checked and unchecked claims so an early failure cannot reuse a
  successful branch's evidence language.
- Every retained JSON behavior has positive and negative scenarios. The runner
  checks exact outcomes rather than accepting any nonzero exit as a valid
  negative result.
- A passing source-inventory fixture proves only that the caller-supplied list
  contains the retained ASGK source paths. It does not prove those files exist,
  inspect their contents, prescribe a target layout, or decide adoption.
- Target repositories must not copy this directory as an adoption bundle.
- Negative fixtures must not be used as positive examples. Interpret each only
  at the registry's or bounded legacy check's proof boundary.
- Target-install and compact target-upgrade fixtures preserve legacy checker
  coverage pending their separately scoped cutover. They do not prove target
  fit, adoption, architecture, governance depth, or approval.
- Historical issue, PR, CI, and release evidence belongs in GitHub, not as
  copied narrative inside this directory.
- Agents should not read this directory during default startup; read only the
  specific fixture or example named by the current issue, PR, validator, or
  documentation reference.

If a file here conflicts with a canonical policy, schema, contract, validator,
or GitHub issue/PR, fix the file or the stale reference in a scoped issue.
