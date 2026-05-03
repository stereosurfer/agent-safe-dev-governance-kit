# Negative Fixtures

These files are opt-in expected-failure examples for governance validation.

They are not positive examples. Normal bootstrap validation must not treat these
fixtures as valid repository state unless a validator is explicitly running a
negative test mode.

## Rules

```yaml
negative_fixture_rule:
  expected_failure: true
  opt_in_only: true
  must_not_break_positive_validation: true
  must_record_expected_outcome: true
```

## How To Use Later

Future tools may run selected cases with commands such as:

```bash
asgk negative --case NEG-001
asgk negative --all
```

Until such tools exist, these fixtures are documentation-backed test targets for
`docs/control/NEGATIVE_TEST_PLAN.md` and review guidance.

## Included Cases

| Case | File | Expected outcome |
|---|---|---|
| NEG-001 | `task_packet.see-chat.yaml` | blocked |
| NEG-004 | `pr_body.no-merge-decision.md` | blocked |
| NEG-008 | `changed_paths.runtime-artifact.txt` | blocked |
| NEG-009 | `changed_paths.protected.txt` | blocked |
| NEG-010 | `changed_paths.private-binary.txt` | blocked |
| NEG-013 | `storage_profile.same-root.json` | blocked |
| NEG-014 | `storage_profile.drive-api.json` | blocked |
| NEG-022 | `pr_body.external-call-no-gate.md` | human_gated |
| NEG-029 | `task_packet.no-stop.yaml` | blocked |
