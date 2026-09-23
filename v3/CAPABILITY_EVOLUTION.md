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

## A question tree for navigation, not a second authority

Organize the capability corpus around the questions an operator will actually ask.
A branch has a short name, scope and child pointers. A leaf points to one or more
lessons, ledger slices, tests, proposals or promoted method versions. Preserve competing
answers and rejected branches with reasons; do not flatten them into one success story.
The tree is navigation metadata. The full records and their cited evidence remain the
material to inspect, and the live issue/PR remains authority for any change.

Progressive disclosure is:

1. **Entry:** load the small Skill purpose and current work link.
2. **Branch:** choose a relevant question/domain from metadata and see counts, not bodies.
3. **Leaf:** retrieve a bounded set of summaries, status and provenance pointers.
4. **Evidence:** open selected full lesson/ledger/test and, only when needed, source
   material or a prior decision chain.

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
research proof. The module does not fetch lesson bodies, verify GitHub links, judge
evidence, synchronize Skills or change a Bot. It is one testable projection pattern,
not a required format for every target. Larger installations can shard indexes by
domain/question; the active Skill should point to the relevant shard, not concatenate
all records. A stale index is repaired through a bounded change, never silently treated
as current authority.
