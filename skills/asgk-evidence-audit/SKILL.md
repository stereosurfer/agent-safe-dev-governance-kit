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
   A matching hash is not attestation that a test ran; a saved snapshot is not
   a live issue read or approval; a synthetic actor, PR, or merge is not
   independent real-world evidence. Bind head-sensitive claims to the exact
   head and mark prior-head evidence stale after a code change.
   For a worker claim of a current GitHub read, inspect the observable read
   receipt. Otherwise label the fact as controller-supplied card/snapshot data
   or unknown; a URL or tool search is not a receipt.
5. Flag vague claims such as `passed`, `done`, or `safe` when no source is named.
   For capability claims, keep observed Lesson, independently verified repeat,
   regression result, and reviewed versioned method distinct. A metadata hit
   or record volume does not prove content, applicability, or promotion.
6. Keep the output in the PR body, issue comment, or report being audited.

## Stop States

- `blocked`: a merge/release claim lacks evidence.
- `requires_human`: an exact existing human-gated operation or policy requires
  a human decision; semantic/product judgment alone does not add a new gate.
- `evidence_ready`: claims have source, evidence, and limits.

## Exit Artifact

Evidence table or YAML block suitable for a PR body, issue comment, or audit report.
