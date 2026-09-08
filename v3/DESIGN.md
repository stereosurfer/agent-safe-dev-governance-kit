# ASGK 3.0 preview — design contract

Status: experimental; authority: [issue #357](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/357).

ASGK 是一套讓人與 AI 能安全、順利交接工作的規則與工具。
目標是看得懂、接得下去、查得清楚，避免工作依賴特定模型、供應商、Agent 或既有對話。

## Design boundary

This preview explores centrally maintained rules compiled into a small work-specific
packet. It does not replace the repository's current governance or migrate v2.
The design precedes the implementation; changes to either remain reviewable on an
isolated branch. Passing tests is checked projection evidence, not independent later
use, target adoption evidence, or proof of successful self-evolution.

Role describes reusable capabilities; actor identifies the person or persistent Bot;
run identifies one execution. A new actor/run must receive a newly compiled packet.
Memory, chat, role membership, and a previous packet never grant new authority.

## Input contract

The single JSON input has a version, work/run/actor/role identifiers, objective,
authority reference and UTC expiry, requested reads/writes/tools, three ceilings
(`role`, `repo`, `environment`), explicit forbidden paths, non-goals, context entries,
validation requirements and a next step. All keys are required, unknown keys fail.

Paths are exact POSIX repo-relative file paths. There are no globs or implied directory
grants in this prototype. Each requested path/tool must be in all three ceilings;
forbidden paths win. A denied request fails the entire compilation, never silently
shrinks the task. Empty write/tool sets support read-only work.

Every context entry names one requested read path, a reason and an expected SHA-256.
Every requested read has exactly one entry. Context remains data, not instructions
that may expand authority. Compilation emits pointers, not the contents of the repo.
Validation requirements are named claims, not executable shell commands.

This first slice uses immutable input files and separate output files. Read/write
overlap is rejected explicitly: in-place editing needs a baseline/current evidence
model and is not implemented here. Interrupted work with missing required receipts
fails verification; a complete partial-work recovery protocol remains future work.
The JSON is a reference input format, not a mandatory form that every worker should
fill in. It represents centrally supplied ceilings plus a task-specific request;
persistent central storage and authoring interfaces are not implemented.

The authority reference is caller-supplied. Its authenticity is **not verified**.
Expiry and the explicit revoked flag are mechanical checks against the current input;
there is no revocation service, signature, atomic lease or security sandbox.

## Compilation and verification

The effective scope is requested scope ∩ role ceiling ∩ repo ceiling ∩ environment
ceiling, minus forbidden paths. Packets include per-claim inclusion reasons, rejected
context outside the selected read set fails, and non-goals/forbidden paths stay visible.

Canonical sorted JSON hashes bind the entire input and compiled projection. Packet
verification recompiles against the separately supplied current input; a self-consistent
packet hash alone is not trusted. Changing scope, actor, run, expiry or policy invalidates
the old packet. Identical input yields identical output, with no timestamp noise.

## Evidence and handoff

A report binds to the packet ID and actor/run/work IDs. Each declared write requires
exactly one file receipt (path + SHA-256). Every required validation has exactly one
status (`pass`, `fail`, `blocked`, `not_run`), detail and receipt paths. A pass needs at
least one receipt. Receipts may refer only to requested read/write paths. The checker
confirms local bytes and rejects symlinks; it does not prove a test command ran, who
authored bytes, or whether other files changed. Read receipts must match the original
context hashes. Only regular UTF-8 report JSON is processed, never executed.

Reports also contain current state, next step, known gaps and decisions. Each decision
has a unique ID, optional earlier parent ID, question, choice, reason, alternatives and
evidence paths. At least one explicit decision is required, including a no-change
decision when appropriate. Cycles, missing parents and unsupported evidence fail.

Handoff and closeout are generated only after packet and evidence checks. Failed or
unknown validations and known gaps produce `blocked`, never ready. `ready_for_review`
means evidence predicates match, not permission to merge or publication approval.
Closeout contains a bounded decision summary plus a packet/report digest for retrieval;
the full report retains the tree. A successor recompiles, rather than inheriting the old
actor's authority. Outputs are portable files owned by the caller, not a new permanent
repository ledger. The user decides where durable issue/PR records should live.

## Adversarial acceptance

Reject stale packets, expired/revoked input, scope expansion, missing/extra fields,
duplicate JSON keys, traversal/absolute paths, symbolic-link evidence, altered receipts,
fake validation status, missing receipts and broken decision chains. Documentation must
separately identify unaddressed runtime threats: prompt injection, stolen authority,
external side effects, forged-but-consistent evidence, filesystem races and concurrent
writers. Local checking is not runtime enforcement.

## Platform relationship

Hermes Bot Mode's persistent Bot identity, messaging, grouping and native task systems
are possible execution surfaces. This preview supplies a manual packet/report protocol,
not a Bot implementation or replacement scheduler. No platform-specific configuration
is installed. No model calls, automatic routing, new dependencies, target writes or
global Skill synchronization are performed.

Before production use, test a real independent receiver, interruption/recovery,
runtime access control, evidence provenance, and a target-owned adoption assessment.
These are unproven here. Do not interpret the experimental directory as a 3.0 release.
