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

## Two trees with different owners

The [research-runtime 0.1 cycle](https://github.com/stereosurfer/research-runtime-macos/blob/7287e3550e9e4254955c4e226f7b1ddc97d9fd33/skill/research-runtime/references/research-cycle-v0.1.md)
is a concrete reference, not an ASGK mandate for every domain. It separates a stable
answer contract from a changing question ledger, then puts the concise handoff and
reviewed answer before a source map and raw evidence. Its Skill entrypoint opens deeper
references only for the relevant kind of work. The repository does **not** yet define
a reusable Lesson/"thought-tree" format; do not attribute one to it.

Keep these two structures distinct:

| Structure | Canonical owner | Navigation and completion |
| --- | --- | --- |
| **Work tree** | The task/target-owned package or existing GitHub issue/PR, according to the workflow | Decision/outcome contract stays stable until the objective changes; a question/requirement ledger updates as evidence arrives. Each material branch points to support, conflict, gap and stop decision. Completion is judged against the contract, never by tool/run status or number of records. |
| **Capability tree** | The versioned Skill/capability repository, with GitHub decisions governing promotion | A small entrypoint points to conditional references and a bounded index of relevant Lessons, tests, proposals and method versions. It helps find reusable experience; it does not replace a live work ledger or grant action authority. |

The work tree may be large. Keep its raw material at the task-owned location, and give
the next reader a short handoff → reviewed result → question/requirement status →
claim-to-evidence map → selected originals. Research uses the source repo's brief,
answer contract and question ledger as one example. A video job might instead track
deliverable decisions, asset lineage and render checks; a translation job might track
terminology decisions, unresolved passages and review evidence. ASGK does not require
those exact filenames, question types or folder layouts. The GitHub issue authorizes
changes; the work package records domain evidence and progress.

The capability tree is a discovery projection over its own corpus. A branch has a short
name, scope and child pointers. A leaf points to one or more Lessons, *bounded slices*
of case ledgers, tests, proposals or promoted method versions. The slice points back
to the canonical case package; it is not a copied live ledger. Preserve competing
answers and rejected branches with reasons instead of flattening them into one success
story. Full records and cited evidence remain available at their owners, and the live
issue/PR remains authority for any change.

Progressive disclosure is:

1. **Entry:** load the small Skill purpose, current work link and task handoff.
2. **Work branch:** inspect the relevant question/requirement and its current gap or
   stop state; do not load unrelated task evidence.
3. **Capability branch:** only when prior method experience is needed, choose a
   relevant domain/question from metadata and see counts, not bodies.
4. **Leaf:** retrieve a bounded set of Lesson/method summaries and provenance pointers.
5. **Evidence:** open selected full case slice, test and source material or prior
   decision chain when the current decision needs it.

For example, a research handoff might follow `research → source-context → long-discussion`
and inspect the root/reply hierarchy case. Video may follow `video → asset-lineage →
render-handoff`; translation may follow `translation → terminology → handoff`. These
paths illustrate *questions*, not mandated folder names or fixed business phases.

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

`v3/capability_evolution.py` reads an explicitly supplied JSON index. It validates
metadata shape and offers `browse` for one tree level or `select` for bounded pointers:

```bash
python3 v3/capability_evolution.py check --index v3/examples/capability_index.json
python3 v3/capability_evolution.py browse --index v3/examples/capability_index.json --domain research
python3 v3/capability_evolution.py browse --index v3/examples/capability_index.json --domain research --branch source-context
python3 v3/capability_evolution.py select --index v3/examples/capability_index.json --domain research --branch source-context --query handoff
```

The fixture is illustrative and its records are **observed**, not a real promotion or
research proof. The module is a *capability-tree discovery example*, not a work-tree
validator or a canonical question ledger. It does not fetch bodies, verify GitHub links,
judge evidence, decide whether task questions are complete, synchronize Skills or
change a Bot. It is one testable projection pattern, not a required format for every
target. Larger installations can shard indexes by domain/question; the active Skill
should point to the relevant shard, not concatenate all records. A stale index is
repaired through a bounded change, never silently treated as current authority.
