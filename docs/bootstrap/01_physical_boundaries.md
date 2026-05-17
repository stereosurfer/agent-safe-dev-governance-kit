# 01 Physical Boundaries

Physical boundaries define where agents may read, write, create, delete, and generate files.

## Project Root

```text
<absolute-or-relative-project-root>
```

## Writable Paths

```yaml
writable_paths:
  - src/
  - backend/
  - frontend/
  - tests/
  - docs/
  - contracts/
  - schemas/
  - scripts/
  - examples/
  - templates/
  - .github/
```

## Generated Fixture Paths

```yaml
generated_paths:
  - tests/fixtures/
  - examples/
```

Runtime generated artifacts must not be placed in the repo.

## Protected Paths

```yaml
protected_paths:
  - .env
  - .env.*
  - secrets/
  - credentials/
  - private_keys/
  - node_modules/
  - .git/
  - Artifact Root unless explicitly authorized
  - Local State Root unless explicitly authorized
```

## Forbidden Actions

```yaml
forbidden_actions:
  - write outside allowed paths
  - write runtime artifacts into the code repo
  - write SQLite live DB into Artifact Root
  - write page render cache into Artifact Root
  - create public cloud sharing links
  - enable cloud/API/MCP lanes by default
  - delete user data
  - rewrite git history
  - force push
  - touch secrets
  - promote unvalidated generated artifacts
```
