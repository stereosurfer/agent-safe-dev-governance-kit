# Negative Fixtures

Status: opt-in expected-failure fixtures.

Files in this directory are intentionally bad inputs for governance validators.
They are not positive examples, adoption templates, policy authority, or target
repository starter content.

## Rules

```yaml
negative_fixture_rule:
  expected_failure: true
  opt_in_only: true
  must_not_break_positive_validation: true
  must_record_expected_outcome: true
```

## Current Usage

Run all registered negative groups with:

```bash
python3 scripts/asgk.py negative all
```

Run a focused group with:

```bash
python3 scripts/asgk.py negative <group>
```

Available groups are reported by:

```bash
python3 scripts/asgk.py negative --help
```

The executable runner surface lives in `scripts/asgk_lib/negative.py`,
`scripts/asgk_lib/negative_cases.py`, and `scripts/asgk_lib/negative_runner.py`.
This README explains the boundary; it is not a second case registry.

## Fixture Classes

```yaml
fixture_classes:
  changed_paths:
    purpose: protected path, runtime artifact, and private/binary path blocking
  pr_body:
    purpose: PR-body parser and merge-policy expected failures
  policy_gate:
    purpose: fail-closed policy-gate expected failures
  task_packet:
    purpose: task-packet authority, scope, and stop-condition expected failures
  handoff:
    purpose: handoff packet and current-status stale-state expected failures
  compact_governance:
    purpose: compact report, scope-lock, task-packet, handoff, and target-upgrade red-team inputs
  target_install:
    purpose: intentionally invalid target-repository structures
```

Do not add a negative fixture unless a validator, runner group, CI step, or
scoped issue names the expected failure it protects.
