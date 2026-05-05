---
name: asgk-evidence-audit
description: Use when auditing validation claims, PR evidence, reports, or release notes in ASGK work; separates evidence source, concrete evidence, and limits without adding a new evidence authority layer.
---

# ASGK Evidence Audit

Use this skill when a PR, issue, report, or release note claims validation, readiness, completion, or safety.

## Authority

Evidence must point to durable artifacts or fresh command output. This skill classifies evidence; it does not make unverified claims true.

## Evidence Classes

- `freshly_rerun`: command was run in the current work unit.
- `github_actions`: observed GitHub Actions result.
- `fixture`: deterministic example or negative fixture.
- `repo_file`: claim is supported by a repository file.
- `inferred_from_merged_pr`: inferred from merged code or PR history.
- `not_run`: validation was not run.

## Procedure

1. Extract each validation or completion claim.
2. Attach one evidence class to each claim.
3. Record concrete evidence: command, check name, file path, issue, PR, commit, or URL.
4. Record limits or non-proofs.
5. Flag vague claims such as `passed`, `done`, or `safe` when no source is named.
6. Keep the output in the PR body, issue comment, or report being audited.

## Stop States

- `blocked`: a merge/release claim lacks evidence.
- `requires_human`: semantic safety or product judgment is being claimed.
- `evidence_ready`: claims have source, evidence, and limits.

## Exit Artifact

Evidence table or YAML block suitable for a PR body, issue comment, or audit report.
