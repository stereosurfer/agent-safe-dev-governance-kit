# Policy Gate Negative Fixtures

Status: opt-in expected-failure fixtures.

These files are intentionally invalid PR bodies for `scripts/policy_gate_check.py`.
They must not be treated as valid examples and must not be loaded by positive
validation as successful PR bodies.

Expected use:

```bash
python3 scripts/policy_gate_check.py --pr-body examples/negative/policy_gate/<fixture>.md
```

Each command is expected to fail. These fixtures prove that mechanically
checkable policy gates block merge eligibility when required PR-body gates are
missing, pending, unknown, ambiguous, or chat-authoritative.

Fixtures:

```yaml
fixtures:
  pr_body.missing-merge-decision.md: missing Merge Decision Record
  pr_body.missing-current-status-impact.md: missing Current Status Impact
  pr_body.checks-pending.md: checks_passed is pending
  pr_body.human-gates-pending.md: human_gates_checked is pending
  pr_body.see-chat-authority.md: chat-only authority appears in PR body
```

Non-goals:

```yaml
non_goals:
  - no auto-merge behavior
  - no low-risk inference
  - no GitHub API use
  - no default CI wiring in this fixture-only work unit
```
