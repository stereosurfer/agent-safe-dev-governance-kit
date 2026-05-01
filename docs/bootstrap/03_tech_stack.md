# 03 Tech Stack

Declare the stack before implementation.

```yaml
runtime_language: "<language/version>"
package_manager: "<tool>"
test_runner: "<tool>"
formatter: "<tool>"
type_checker: "<tool>"
ci: GitHub Actions
repo_host: GitHub
```

## Dependency policy

```yaml
dependency_policy:
  new_dependencies_require:
    - issue authorization
    - rationale
    - license check
    - security review
    - rollback plan
```

## Forbidden defaults

```yaml
avoid:
  - unnecessary frameworks
  - hidden global state
  - undocumented prompts
  - unversioned schemas
  - cloud egress by default
```
