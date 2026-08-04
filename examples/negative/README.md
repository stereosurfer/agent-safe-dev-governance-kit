# Negative Fixtures

Status: opt-in expected-failure fixtures.

Files in this directory are constructed to trigger current governance
validators. Some represent real invariant violations; legacy fixtures may only
preserve current mechanical behavior. They are not positive examples, adoption
templates, policy authority, semantic defect proof, or target starter content.

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
    purpose: task-packet mode, legacy-field, authority, path/read/validation expansion, and exact finding-code failures
  handoff:
    purpose: handoff packet and current-status stale-state expected failures
  source_validation:
    purpose: supplied source-inventory shape and required retained-path inclusion failures
    proof_limit: never target fit, target layout, adoption readiness, human approval, or merge authority
  target_evidence:
    purpose: exact caller-claim mismatches and incomplete claim-input behavior
    proof_limit: mismatch means only that named mechanical claims disagreed; it is not a target defect, fit, depth, readiness, or approval judgment
  compact_governance:
    purpose: retained compact report, scope-lock, task-packet, and handoff cases plus inactive red-team inputs
```

Do not add a negative fixture unless a validator, runner group, CI step, or
scoped issue names the expected failure it protects.
