# ASGK 3.0 — GitHub-native design contract

Preview.1-derived design; [scoped review #359](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/359).
The GitHub work-projection implementation is canonical under
`scripts/asgk_lib/github_workflow.py` and public through
`scripts/asgk.py workflow` after #397. The capability catalog, templates and
eleven proposed Skills remain candidates; this document is not a second
authority for issue scope, approval or release.
This design descends from the #358 GitHub-native candidate without overwriting
it. The [formal 3.0 program #372](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/372)
coordinates promotion. [#381](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/381)
imported the candidate subtree to main as non-default source; #397 promotes
only its GitHub workflow implementation. Neither step supersedes root policies
or any live child issue's exact authority.

## Product invariants

ASGK 是一套讓人與 AI 能安全、順利交接工作的規則與工具。
看得懂、接得下去、查得清楚；避免工作依賴特定模型、供應商、Agent 或既有對話。

GitHub is the durable work ledger:

```text
issue authority → branch / bounded change → validation → PR / MDR / review
→ policy-permitted merge → issue closeout review → compact recovery
```

The graph includes failed attempts, rejected choices, replacement issues and authorized
reverts. Closeout reviews are its searchable index, linking issue, PR, CI, decisions,
commits and corrections. Local JSON cannot replace this graph.

## Ownership and control layer

| Responsibility | Canonical owner | 3.0 projection |
| --- | --- | --- |
| Objective, plan, acceptance, write scope, non-goals, stops, rollback | Live issue / qualifying PR, existing 13 fields | Parsed, never re-authored as local authority |
| Read scope and validation | Same issue's two execution gates | Bounded context; all issue-required checks stay visible |
| Rules and human gates | Existing canonical repository policies | Relevant constraints and pointers, never inferred approval |
| Role/capability maximum | Centrally maintained evidence-linked role description | Optional narrowing, not a new grant or scheduler |
| Persistent identity / execution | Actor ID / run ID recorded with work | Replace receiver without transferring old approval |
| Changes and merge evidence | Branch, PR, exact head, checks, MDR, reviews | Snapshot and local diff observations |
| Decisions and closeout | GitHub issue comments | Rebuildable search/trace cache, no permanent second ledger |
| Repo recovery | CURRENT_STATUS | Snapshot, not history |
| Adoption and upgrade | Target-owned Skill-guided assessment | Frontier judgment; minimum change or no change |

Controller invokes the relevant Skills and checks live authority. Workers receive the
objective, exact selected paths, bounded context pointers, non-goals, prohibited actions,
expected output, checks and handoff destination. They do not need the whole governance
corpus, all tool schemas, release rules or unrelated work history.

Effective write scope = issue scope ∩ selected paths ∩ optional role ceiling. Read context
is an exact-item narrowing of the issue read set. Repository and
environment restrictions can narrow it further. This compiler does not enforce runtime
access or authenticate supplied input. Forbidden paths can only narrow scope; prose
non-goals/stops remain visible because automatically extracting every prohibition would
overclaim. Memory never authorizes.

Hermes persistent Bots, humans and temporary agents use the same durable work lineage.
Runtime messaging, orchestration and model selection remain external. Message receipt
is not acceptance/completion. Receivers recheck current issue/head and packet digest.

Hermes Kanban can own run/card/lease/review state while GitHub owns ASGK work authority,
PR decisions and searchable closeout. The exact mapping and failure tests are in
[KANBAN_BRIDGE](KANBAN_BRIDGE.md); no runtime adapter or Bot configuration is installed.
The worker normally self-reports against deterministic checks. Independent semantic
review is applied to material capability promotion and existing risk gates, not as a
mandatory police Bot for every task. Review identity must be real, not a renamed author.

## Executable candidate contract

1. Capture GET-only GitHub issue/comments and explicitly selected PR observations.
   Preserve source, timestamp, URLs, head, files, reviews and check observations.
2. Require an issue-backed packet using the existing issue parser and scope-comparison
   engine. Bind issue/comment/PR content and assignment. A saved snapshot is not live
   authority; importing JSON does not authenticate it.
3. Preserve actor/run, local base/head, remaining work, gaps, validation source/limits,
   durable links and decisions in handoff. Missing evidence yields a blocked handoff,
   never invented success. A successor gets a newly compiled packet.
4. Generate a draft GitHub issue closeout comment using the existing quality floor:
   reasons, rejected alternatives, applicability, evidence, known limits; maximum five
   decisions and 400 words. Reject overflow instead of truncating reasoning.
5. Search explicit snapshots for closeout comments and trace durable links with bounded
   hops. Duplicate-free JSON may form a shape-checked edge; fenced YAML is only a
   provenance-labeled, unparsed candidate URL and makes the affected lookup incomplete.
   Missing records remain unresolved; do not read the entire repo or invent links.

Committed in-place changes use exact git base/head. Partial work can be handed off with
missing receipts/checks recorded as blockers. Local checks do not cover ignored files,
untrusted test execution, runtime side effects or credential exfiltration.

Capture is not an atomic transaction. Issue/head changes require refresh. No preview
command posts comments, opens PRs, merges, closes issues or publishes. Generated PR
evidence is a fragment; existing PR template/preflight/MDR/strict check-pr still applies.
Completed closeout claims require a merged PR at the reported head and complete checks;
closed, unmerged prior attempts remain in the lineage. Even that
does not authorize closing the issue. Non-merge outcomes preserve their own reasons.

## All eleven Skills — full-content review

All eleven source SKILL.md files were read. The root copies on this candidate
branch are a fork-time comparison baseline, not guaranteed current-main rules;
the eleven revised candidate entrypoints are under v3/skills. These responsibility
changes are not a bulk installation and do not amend root policy or merge authority.

| Skill | Finding | 3.0 disposition |
| --- | --- | --- |
| asgk-startup | Full lifecycle detail is useful to controller, excessive for every worker; any open PR should not hijack unrelated assigned work | Controller selects relevant issue/PR; receiver verifies its packet and current head. Preserve stale/abandoned attempt handling |
| asgk-issue-scoping | Canonical fields and target discovery are sound; local re-authoring creates duplicate authority | Controller writes issue once; reuse parser/refinement engine; workers request narrowing, never expand scope |
| asgk-pr-evidence-merge-decision | Correct layered lifecycle but extensive syntax burdens non-PR workers | PR owner invokes Skill; workers supply evidence/gaps. Keep exact tokens, file preflight and current-head checks in existing tooling |
| asgk-gatekeeper | Eligibility can be mistaken for an approver role | Controller/reviewer checks existing gates. Role aliases do not prove independent actors; green checks are not approval |
| asgk-post-merge-closeout | Strong quality floor; trigger only covers merges while canonical closeout also covers abandoned, blocked, duplicate and superseded work | Keep post-merge process; explicitly route non-merge outcomes to the same closeout quality contract, without fake merge evidence |
| asgk-current-status-handoff | Repo recovery and per-worker interruption share the handoff name | Keep CURRENT_STATUS repo-level; per-run handoff belongs in issue/PR comments and successor projection |
| asgk-evidence-audit | Its requires_human state for semantic/product judgment is broader than target assessment Skills, which forbid that extra gate | Classify unsupported claims; require human gate only for exact existing operation/policy. Semantic judgment alone is not a new approval gate |
| asgk-governance-health-check | Explicit trigger is good; legacy gaps can still be mistaken for current blocking repair work | Scoped controller audit only; observations do not create backfill or fixes |
| asgk-release-prep | Exact tag/title/commit authority is sound; irrelevant to ordinary workers | Source-maintainer-only trigger; no packet or program approval substitutes for publication approval |
| asgk-target-install-audit | Actual guidance is judgment-led; install name may imply copying | Retain target-owned assessment, evaluate existing equivalents and minimum adaptation; no fixed Bot/module/file bundle or extra gate |
| asgk-upgrade-audit | Correct target ownership; version delta could be mistaken for mandatory sync | Required assessment before migration; compare responsibility/evidence, accept no-change and preserve target decisions/history |

Reduction comes from responsibility-specific invocation, not deleting safety or asking
users to learn a module picker. Reading all eleven is justified for this review, never
the default for every worker. Installed/global Skills remain unchanged.

## Falsification

Test missing/ambiguous issue authority, scope expansion, stale issue/comment/head,
forged local-only grants, wrong actor/run, out-of-scope git diff, missing checks, partial
handoff, unmerged completion, missing rejected choices, broken/cyclic decision links and
oversized reviews. A hash is not proof a test ran; a role name is not independent review;
cached history is not current scope. Keep those limits explicit.

## Document-driven evolution

Retain #357 → #358 → #359 → candidate branch commits → [PR #369](https://github.com/stereosurfer/agent-safe-dev-governance-kit/pull/369),
[PR #371](https://github.com/stereosurfer/agent-safe-dev-governance-kit/pull/371) and
entry-recovery [PR #380](https://github.com/stereosurfer/agent-safe-dev-governance-kit/pull/380)
→ their #368/#370/#377 closeouts → #372's later bounded promotion work. Do not erase
failed attempts or turn #370's pre-merge MDR timing exception into an on-time
approval. Independent later use and target-owned evidence remain necessary for
self-evolution and portability claims.

Capability work across Research, Video and Translation follows
[CAPABILITY_EVOLUTION](CAPABILITY_EVOLUTION.md): many lessons/ledgers are permitted,
while discovery and full-context loading are progressive. The source
[research package contract](https://github.com/stereosurfer/research-runtime-macos/blob/d09eac50c3cd12c1427dadaf5c09d1c8f7dfd38e/docs/PACKAGE_FORMAT.md)
demonstrates task-owned question/observation/evidence traversal; the candidate
capability catalog indexes reusable experience *outside* that active delivery graph.
A reviewed PR promotes a method into a versioned Skill; Bot memory and retrieval
indexes do not. This is a generic handoff invariant, not a requirement that every
target use the research package's exact files, three mandatory modules or an
automatic agent router.

The preview.1 branch still contains root files from its earlier fork; main has
since changed through W6B [PR #373](https://github.com/stereosurfer/agent-safe-dev-governance-kit/pull/373)
and recovery-status [PR #376](https://github.com/stereosurfer/agent-safe-dev-governance-kit/pull/376) / [PR #379](https://github.com/stereosurfer/agent-safe-dev-governance-kit/pull/379).
Do not call the older root copies current authority or treat a head-to-head diff
as the candidate's source patch. #397 promotes the GitHub workflow CLI into
the root entry and doctor, not the whole `v3/` subtree. #372 still requires
separately reviewed capability, template, Skill, field-test and release work.
This document does not publish 3.0 or bypass current main rules.
