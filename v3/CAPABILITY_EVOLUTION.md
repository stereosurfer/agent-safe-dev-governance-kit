# Capability evolution — experience without memory inflation

Preview.1 contract for Research, Video, Translation and other long-running workflows.
These are examples, not an ASGK module menu. A persistent Bot is an operator; a Skill
is a versioned method; GitHub issue/PR/commit and closeout are the governed change
lineage. A Kanban card may carry a run. None of these roles should absorb the others.

## Four different kinds of state

| Surface | Keep here | Do not infer |
| --- | --- | --- |
| Bot memory | Identity, preferences, active work pointers, current stable Skill version | Complete method, write scope or approval |
| Versioned Skill | Repeatable method, routing to relevant references, real safety constraints | Every incident, raw evidence or permanent run history |
| Lessons and ledgers | Case observations, experiments, source/claim/event relationships, contradictions and unresolved questions | A new rule just because a record exists |
| Canonical knowledge | Reviewed durable principles, source policy, benchmark and failure patterns | Task authority or automatic promotion |

There may be hundreds or thousands of lessons/ledger entries. Do not impose a document
count limit to solve context pressure. Preserve full records at their appropriate home;
reduce *default loading* instead. Large/private raw research or media outputs stay in a
target-owned store, not in ASGK source or Bot memory. A GitHub record can link to them
without copying their bytes into the Skill repository.

## Delivery question graph and reusable capability catalog

The owner's [research-runtime delivery contract](https://github.com/stereosurfer/research-runtime-macos/blob/d09eac50c3cd12c1427dadaf5c09d1c8f7dfd38e/docs/PACKAGE_FORMAT.md)
and [complete synthetic package](https://github.com/stereosurfer/research-runtime-macos/tree/d09eac50c3cd12c1427dadaf5c09d1c8f7dfd38e/examples/research-package-demo)
provide an actual thought-tree example. Do not reduce that delivery design to a flat
Lesson index.

Keep authorization, delivery and reusable capability separate:

| Structure | Owner | What it decides |
| --- | --- | --- |
| **Governed work lineage** | Live GitHub issue/PR, MDR and close-out | Objective, allowed paths, gates, acceptance and why a change was made. The task package cannot grant these. |
| **Delivery question graph** | The particular task's target-owned package or evidence home | What must be answered to deliver this task, current question status, observations, evidence, limits and next action. It cannot approve its own Skill promotion. |
| **Reusable capability catalog** | The versioned Skill/capability repository | Which prior Lessons, tests, method versions and bounded case references may help. It is a discovery index, not the active task's question graph or an authority ledger. |

For a substantial *research* task, the source contract gives humans `HANDOFF.md` or
`INDEX.html` first, and agents one small `kb/AGENT_ENTRY.md`. The agent routes its
actual question to a `QUESTION_TREE.json` node, reads that node's status and linked
observation IDs, resolves only relevant `OBSERVATIONS.jsonl` and `EVIDENCE_INDEX.json`
entries, then opens one **complete** source section or discussion unit when needed.
The `ANSWER_CONTRACT.md` remains stable unless the decision changes; the
`QUESTION_LEDGER.md` changes as gaps close. `RESEARCH.md` and `SOURCE_MAP.md` are
reviewed delivery views; `raw/` and diagnostic material are deeper audit layers.
An append-only observation is a case finding, not an instruction or universal rule.
Manifest/hash and graph checks prove package consistency, not the research conclusion.

This is a reference implementation for the *shape of the handoff*, not a mandatory
ASGK folder layout or a new generic core validator. A video workflow may route from
a deliverable question to asset versions, render observations and source media; a
translation workflow may route from a passage/terminology question to review findings
and source segments. Their Skill/target owns the precise file format and tests.
Some small tasks need only issue/PR evidence and a compact handoff, not a full package.
The reusable invariant is an actionable entry, bounded question/requirement routing,
stable IDs, observation-to-evidence provenance, explicit gaps and proof limits.

The capability catalog is a *different* progressive-disclosure projection over prior
experience. A branch names a domain/question; a leaf gives bounded pointers to Lessons,
ledger slices, tests, proposals or promoted method versions. A slice points back to
the canonical task package and its relevant question/observation, through a durable
provenance record; it is not a copy of the live ledger or its private raw data.
Preserve competing answers, rejected branches and applicability conditions. The live
issue/PR remains authority for any capability change.

The normal reading route is therefore:

1. **Current work:** GitHub authority and the task's compact human handoff or Agent
   entry, depending on the reader.
2. **Current question:** route to one relevant work-graph node and its gap/stop state.
3. **Current evidence:** resolve only linked observations, source metadata and selected
   complete evidence units.
4. **Prior method experience, if needed:** browse one capability-catalog branch and
   open a small set of applicable Lesson/method records with original provenance.

For example, a research handoff can route a current question about a long discussion
to its observation and complete root/reply evidence, while the catalog may separately
find past long-discussion lessons. Video may ask about asset lineage and a render
handoff; translation may ask about terminology and review. These are questions, not
mandated folder names or fixed business phases.

An observed lesson remains an observation. A verified lesson has independently
reproduced evidence but is not yet a rule. A promoted method has a reviewed decision,
tests and a Skill version. Rejected/superseded entries remain traceable but should not
be offered as current instructions. A search hit's rank or record volume does not
prove applicability.

## Promotion loop

```text
run/incident → lesson or ledger entry → competing explanations and test
→ bounded GitHub improvement issue → branch/PR → regression + independent review
→ existing ASGK gate → versioned Skill/knowledge change → later-use evidence
```

The originating Bot may propose and implement. It can run deterministic tests, but
cannot use its own favorable judgment as independent proof. Material changes to Skill
entrypoints, policies, security boundaries or generalized methods need a separate
reviewer and any exact existing human gate. Low-risk record corrections can follow the
repository's actual merge policy; no new universal human checkpoint is introduced.
Each PR states problem, observed cases, proposed method, expected benefit, regression
risk, positive/negative tests, evidence limits and rollback. The closeout links the
accepted and rejected branches in a short decision analysis. Merging a Skill change
does not silently rewrite an already-running Bot's context; the next run checks the
version it actually loaded.

## Candidate metadata demonstration

`v3/capability_evolution.py` reads an explicitly supplied *capability catalog*. It
validates metadata shape and offers `browse` for one catalog level or `select` for
bounded pointers:

```bash
python3 v3/capability_evolution.py check --index v3/examples/capability_index.json
python3 v3/capability_evolution.py browse --index v3/examples/capability_index.json --domain research
python3 v3/capability_evolution.py browse --index v3/examples/capability_index.json --domain research --branch source-context
python3 v3/capability_evolution.py select --index v3/examples/capability_index.json --domain research --branch source-context --query handoff
```

The fixture is illustrative and its records are **observed**, not a real promotion or
research proof. This catalog does **not** implement or validate the source repository's
delivery question graph. It does not fetch bodies, verify GitHub links, judge evidence,
decide whether task questions are complete, synchronize Skills or change a Bot. It is
one optional projection pattern, not a required format for every target. A future
domain-owned delivery package should be tested against its own contract, including
negative graph/link/path cases; it must not be certified by this catalog's green result.
Larger capability corpora can shard indexes by domain/question; the active Skill points
to the relevant shard instead of concatenating all records. A stale index is repaired
through a bounded change, never silently treated as current authority.

## First live observed Lesson candidate

Issue [#370](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/370)
tests the loop with one case from the [#368 closeout](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/368#issuecomment-5805341585).
`v3/capabilities/index.json` is a one-record discovery pointer to
`v3/lessons/github-nondefault-base-closeout.md`. The Lesson stays `observed`:
the closeout reports a manual issue closure after PR #369 merged to a
non-default base, but this record does not independently reproduce GitHub's
behavior or promote a Skill rule. The index is not task authority, a delivery
question graph, or a substitute for reading the cited issue and its limits.

The small regression checks the real pointer's shape, bounded branch browsing,
selection without loading the Lesson body, and rejection of an unsupported
`promoted` label. Passing it proves metadata behavior only. [PR #371](https://github.com/stereosurfer/agent-safe-dev-governance-kit/pull/371)
merged this observed Lesson into preview.1 as `1e0d82109141fe083f3fa469145200c6f7b3c3d0`;
[#370's closeout](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/370#issuecomment-5806869845)
links the change decision and preserves the pre-merge MDR timing exception.
That GitHub lineage is now durable, but it does not independently reproduce the
Lesson, prove later use, promote a Skill rule, or establish release readiness.
