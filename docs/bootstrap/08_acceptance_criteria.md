# 08 Acceptance Criteria

## Three acceptance levels

```yaml
level_1_code_correctness:
  - tests pass
  - type checks pass when applicable
  - formatting checks pass

level_2_data_correctness:
  - schemas validate
  - contracts are satisfied
  - promotion gates pass or block with explicit reason

level_3_workflow_correctness:
  - issue linked
  - PR body complete
  - validation recorded
  - handoff updated
  - merge decision recorded
```

## Definition of Done

```yaml
done_when:
  - acceptance_sheet checked
  - validation commands run or not-run reason recorded
  - no forbidden paths touched
  - no runtime artifacts committed
  - durable handoff updated
```
