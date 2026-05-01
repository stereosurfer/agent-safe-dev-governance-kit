# 05 Context Budget

## Default limits

```yaml
context_budget:
  max_files_per_task: 5
  max_changed_files_per_pr: 10
  max_issue_scope: one_atomic_outcome
  max_context_sources:
    - current issue
    - affected files
    - relevant contracts
    - current status doc
```

## Task packet required context

Every task packet must include:

- objective
- allowed paths
- expected output
- acceptance criteria
- stop conditions
- durable source of truth

## Stop when

```yaml
stop_when:
  - context_is_insufficient
  - task_touches_forbidden_path
  - schema_change_required_but_not_authorized
  - tests_fail_for_unrelated_reasons
  - new_dependency_required
```
