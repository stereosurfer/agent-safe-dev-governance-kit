# 09 Safety Checks

## Required checks

```yaml
safety_checks:
  secrets:
    - no .env committed
    - no keys or credentials committed
  filesystem:
    - no writes outside allowed paths
    - no runtime outputs in repo
  data:
    - no private source files committed
    - no unvalidated artifact promoted
  git:
    - no force push
    - no history rewrite
  dependency:
    - no new dependency without issue approval
  external_calls:
    - no live API/model/cloud call without explicit lane approval
```

## Minimum commands

```bash
python3 scripts/check_project.py
python3 scripts/validate_bootstrap.py
git diff --check
```
