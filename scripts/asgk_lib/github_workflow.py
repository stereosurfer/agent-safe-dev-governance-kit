"""GitHub-backed work projections. Read-only transport; comments are drafts."""
import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from asgk_lib.workflow_common import (
    Invalid, canonical, digest, load, path_name, record, require, save_bundle,
    strings, timestamp, words,
)
from asgk_lib.validation_result import human_gate, validation_result_errors

from asgk_lib.task_packet import (evaluate_task_packet, issue_scope_for_task_packet,
                                 is_context_pseudo_ref, path_matches_allowed)

SOURCE = Path(__file__).resolve().parents[2]

PROOF = ('GitHub snapshots are observed evidence, not live or authenticated authorization. '
         'Local remote configuration and textual PR links are not authenticated repository identity '
         'or semantic GitHub linkage. No merge approval, test-execution attestation, runtime sandbox '
         'or external-side-effect audit.')
REPO = re.compile(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z')
SHA = re.compile(r'[0-9a-f]{40}\Z')
LINK = re.compile(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/'
                  r'(?:issues/\d+(?:#issuecomment-\d+)?|pull/\d+(?:#(?:issuecomment-|discussion_r)\d+)?|commit/[0-9a-f]{40})(?![A-Za-z0-9/#-])')
GITHUB_REMOTE = re.compile(
    r'(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/|git://github\.com/)'
    r'([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?/?\Z', re.IGNORECASE)
DEFAULT_CHECKED = ['workflow result construction up to the returned boundary']


def envelope(result='pass', **extra):
    return dict(result=result, evidence_source='snapshot_and_local_observation',
                mechanically_checked=DEFAULT_CHECKED.copy(),
                not_checked=['current live authorization', 'test execution',
                'semantic correctness', 'human approval', 'runtime side effects'],
                human_gate=human_gate(), proof_boundary=PROOF, findings=[], **extra)


def url(value):
    require(type(value) is str and LINK.fullmatch(value), 'DURABLE_URL', 'reference',
            'Expected a GitHub issue, PR, comment or exact commit URL')
    return value


def git(root, *args):
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, timeout=30)
    require(result.returncode == 0, 'GIT', 'repository', 'Read-only git observation failed: ' + ' '.join(args[:2]))
    return result.stdout


def commit(value):
    require(type(value) is str and SHA.fullmatch(value), 'COMMIT', 'sha', 'Expected exact 40-character commit SHA')


def checkout_identity(root, snapshot):
    """Bind a supplied repository label to local Git config, not to GitHub auth."""
    names = git(root, 'remote').decode().splitlines()
    repositories = []
    for name in names:
        remote = git(root, 'remote', 'get-url', name).decode().strip()
        match = GITHUB_REMOTE.fullmatch(remote)
        if match:
            repositories.append(match.group(1).casefold())
    if snapshot['repository'].casefold() in repositories:
        return 'matching_configured_github_remote'
    require(snapshot['source'] == 'fixture' and not names, 'REPO_IDENTITY', 'repo_root',
            'No configured GitHub remote matches the snapshot repository; do not project it onto this checkout')
    return 'not_checked_fixture_without_remote'


def validate_snapshot(snapshot, fresh=False):
    record(snapshot, 'version source captured_at repository issue comments prs', 'snapshot')
    require(snapshot['version'] == 1 and type(snapshot['version']) is int, 'SNAPSHOT_VERSION', 'version', 'Expected 1')
    require(snapshot['source'] in ('gh_api', 'connector_export', 'fixture'), 'SOURCE', 'source', 'Unknown evidence source')
    require(type(snapshot['repository']) is str and REPO.fullmatch(snapshot['repository']), 'REPOSITORY', 'repository', 'Expected owner/repo')
    age = (datetime.now(timezone.utc) - timestamp(snapshot['captured_at'], 'captured_at')).total_seconds()
    require(age >= -30, 'FUTURE_SNAPSHOT', 'captured_at', 'Snapshot is in the future')
    if fresh:
        require(age <= 1800, 'STALE_SNAPSHOT', 'captured_at', 'Refresh snapshot before work (30-minute cache limit is not a lease)')
    issue = snapshot['issue']
    require(type(issue) is dict, 'ISSUE_REQUIRED', 'issue', 'Expected GitHub issue payload')
    for key in ('number', 'html_url', 'body', 'state', 'updated_at'):
        require(key in issue, 'ISSUE_REQUIRED', key, 'Missing issue field')
    require(type(issue['number']) is int and issue['number'] > 0, 'ISSUE_ID', 'issue.number', 'Invalid number')
    require(issue['html_url'] == f"https://github.com/{snapshot['repository']}/issues/{issue['number']}",
            'ISSUE_ID', 'issue.html_url', 'Issue does not belong to selected repository')
    require(type(issue['body']) is str, 'ISSUE_REQUIRED', 'issue.body', 'Expected body text')
    require(issue['state'] in ('open', 'closed') and 'pull_request' not in issue,
            'ISSUE_REQUIRED', 'issue', 'Expected issue, not PR')
    timestamp(issue['updated_at'], 'issue.updated_at')
    require(type(snapshot['comments']) is list and type(snapshot['prs']) is list, 'SHAPE', 'snapshot', 'Expected comment/PR lists')
    seen = set()
    for comment in snapshot['comments']:
        require(type(comment) is dict and type(comment.get('body')) is str, 'COMMENT', 'comments', 'Missing comment body')
        link = url(comment.get('html_url'))
        require(link.startswith(issue['html_url'] + '#issuecomment-') and link not in seen,
                'COMMENT', 'comments', 'Wrong issue or duplicate comment URL')
        seen.add(link)
    numbers = set()
    for item in snapshot['prs']:
        record(item, 'pr files reviews checks comments', 'prs.entry')
        pr = item['pr']
        require(type(pr) is dict and type(pr.get('number')) is int, 'PR', 'pr', 'Missing PR number')
        require(pr['number'] not in numbers, 'PR', 'pr.number', 'Duplicate PR')
        numbers.add(pr['number'])
        require(pr.get('html_url') == f"https://github.com/{snapshot['repository']}/pull/{pr['number']}", 'PR', 'pr.html_url', 'Wrong PR repository')
        require(type(pr.get('head')) is dict and type(pr.get('base')) is dict, 'PR', 'pr', 'Missing head/base')
        commit(pr['head'].get('sha')); commit(pr['base'].get('sha'))
        require(pr.get('state') in ('open', 'closed') and type(pr.get('merged')) is bool,
                'PR', 'pr.state', 'Missing observed lifecycle state')
        if pr['merged']:
            require(pr['state'] == 'closed', 'PR', 'pr.state', 'Merged PR must be closed')
            commit(pr.get('merge_commit_sha'))
        for key in ('files', 'reviews', 'checks', 'comments'):
            require(type(item[key]) is list, 'PR', key, 'Expected observations list')
    return snapshot


def gh_get(endpoint, paginate=False):
    command = ['gh', 'api', '--hostname', 'github.com', '--method', 'GET', endpoint]
    if paginate:
        command += ['--paginate', '--slurp']
    result = subprocess.run(command, capture_output=True, text=True, timeout=45)
    require(result.returncode == 0, 'GITHUB_UNAVAILABLE', 'capture',
            'GitHub GET unavailable; use a trusted connector export. No write fallback was attempted.')
    payload = json.loads(result.stdout)
    return [item for page in payload for item in page] if paginate else payload


def capture(repository, number, prs=()):
    require(bool(REPO.fullmatch(repository)) and number > 0 and all(n > 0 for n in prs),
            'REPOSITORY', 'capture', 'Invalid repository or number')
    prefix = 'repos/' + repository
    issue = gh_get(f'{prefix}/issues/{number}')
    comments = gh_get(f'{prefix}/issues/{number}/comments?per_page=100', True)
    observations = []
    for n in prs:
        pr = gh_get(f'{prefix}/pulls/{n}')
        files = gh_get(f'{prefix}/pulls/{n}/files?per_page=100', True)
        require(len(files) == pr.get('changed_files'), 'INCOMPLETE_FILES', 'pr.files', 'GitHub file listing is incomplete')
        reviews = gh_get(f'{prefix}/pulls/{n}/reviews?per_page=100', True)
        pc = gh_get(f'{prefix}/issues/{n}/comments?per_page=100', True)
        # Check runs are observational only; not a replacement for strict source check-pr.
        checks = gh_get(f"{prefix}/commits/{pr['head']['sha']}/check-runs?per_page=100")
        require(checks.get('total_count') == len(checks.get('check_runs', [])),
                'INCOMPLETE_CHECKS', 'pr.checks', 'Check list is truncated; do not infer readiness')
        again = gh_get(f'{prefix}/pulls/{n}')
        require((pr['head']['sha'], pr['updated_at']) == (again['head']['sha'], again['updated_at']),
                'CAPTURE_DRIFT', 'pr', 'PR changed during capture')
        observations.append(dict(pr=pr, files=files, reviews=reviews, checks=checks['check_runs'], comments=pc))
    again = gh_get(f'{prefix}/issues/{number}')
    require((issue['body'], issue['updated_at']) == (again['body'], again['updated_at']),
            'CAPTURE_DRIFT', 'issue', 'Issue changed during capture')
    result = dict(version=1, source='gh_api', captured_at=datetime.now(timezone.utc).isoformat(),
                  repository=repository, issue=issue, comments=comments, prs=observations)
    return validate_snapshot(result)


def project(snapshot, assignment, root, review=False):
    validate_snapshot(snapshot, fresh=not review)
    identity = checkout_identity(root, snapshot)
    issue = copy.deepcopy(snapshot['issue'])
    require(review or issue['state'] == 'open', 'ISSUE_CLOSED', 'issue', 'Closed issue cannot authorize new work')
    # Review of historical results is read-only, not resumed execution authority.
    if review:
        issue['state'] = 'open'
    scope, findings = issue_scope_for_task_packet(issue, repo_root=Path(root))
    if findings:
        raise Invalid(findings[0]['code'], findings[0]['field'], findings[0]['reason'])
    record(assignment, 'actor_id role_id run_id branch base_sha selected_paths selected_context '
           'forbidden_paths role_ceiling role_ref prior_handoff', 'assignment')
    for key in ('actor_id', 'role_id', 'run_id', 'branch'):
        words(assignment[key], key)
    commit(assignment['base_sha'])
    require(git(root, 'rev-parse', '--verify', assignment['base_sha'] + '^{commit}').decode().strip() == assignment['base_sha'],
            'BASE', 'base_sha', 'Unknown local baseline')
    for key in ('selected_paths', 'selected_context', 'forbidden_paths', 'role_ceiling'):
        strings(assignment[key], key, key in ('selected_paths', 'selected_context'))
    for name in assignment['selected_paths'] + assignment['forbidden_paths'] + assignment['role_ceiling']:
        if name != 'none':
            path_name(name, 'assignment.path')
    if assignment['role_ceiling']:
        url(assignment['role_ref'])
    else:
        require(assignment['role_ref'] is None, 'ROLE_REF', 'role_ref', 'No role ceiling means no role authority claim')
    if assignment['prior_handoff'] is not None:
        url(assignment['prior_handoff'])
    refinement = dict(mode='issue_refinement', durable_source_of_truth=issue['html_url'],
                      allowed_paths=assignment['selected_paths'], context_read_set=assignment['selected_context'],
                      project_specific_validation=scope['project_specific_validation'])
    result, details = evaluate_task_packet(refinement, canonical(refinement), issue, repo_root=Path(root))
    require(result == 'pass', 'REFINEMENT', 'assignment', canonical(details.get('findings', details)))
    for name in assignment['selected_paths']:
        require(name not in assignment['forbidden_paths'], 'FORBIDDEN', name, 'Explicit prohibition wins')
        require(not assignment['role_ceiling'] or name in assignment['role_ceiling'] or name == 'none',
                'ROLE_CEILING', name, 'Selected path outside role ceiling')
    context = []
    for name in assignment['selected_context']:
        if is_context_pseudo_ref(name):
            context.append(dict(ref=name, kind='durable_pointer'))
        else:
            path_name(name, 'context')
            mode = git(root, 'ls-tree', assignment['base_sha'], '--', name).decode()
            require(not mode.startswith(('120000', '160000')), 'UNSUPPORTED_FILE_MODE', name,
                    'Context symlink/submodule is not a regular baseline file')
            blob = git(root, 'show', assignment['base_sha'] + ':' + name)
            context.append(dict(ref=name, kind='baseline_file', sha256=hashlib.sha256(blob).hexdigest()))
    packet = dict(version=3, mode='issue_refinement', issue=issue['html_url'],
                  authority_sha256=digest(issue['body']), comments_sha256=digest(snapshot['comments']),
                  repository=snapshot['repository'], checkout_identity=identity,
                  assignment=copy.deepcopy(assignment),
                  canonical_fields=scope['canonical_fields'], refinement=refinement, context=context,
                  pr_heads={str(x['pr']['number']): x['pr']['head']['sha'] for x in snapshot['prs']},
                  source=snapshot['source'], proof_boundary=PROOF)
    packet['packet_id'] = digest(packet)
    return packet


def check_packet(snapshot, packet, root, review=False):
    require(type(packet) is dict and 'assignment' in packet, 'PACKET', 'packet', 'Missing issue-backed packet')
    expected = project(snapshot, packet['assignment'], root, review=review)
    # Closing an issue is lifecycle evolution, not a new task. New issue
    # comments may contain changed instructions or objections: refresh the
    # packet instead of silently treating every comment as harmless history.
    if review:
        for number, head in packet.get('pr_heads', {}).items():
            require(expected['pr_heads'].get(number) == head, 'STALE_HEAD', 'pr', 'Recorded PR head changed')
        expected['pr_heads'] = packet.get('pr_heads', {})
        expected['packet_id'] = digest({k: v for k, v in expected.items() if k != 'packet_id'})
    require(canonical(expected) == canonical(packet), 'STALE_PACKET', 'packet', 'Issue, comments, PR head or projection changed; refresh work state')
    return packet


def work_text(packet):
    fields = packet['canonical_fields']
    data = dict(issue=packet['issue'], packet_id=packet['packet_id'],
                checkout_identity=packet['checkout_identity'], assignment=packet['assignment'],
                objective=fields['objective'], plan=fields['plan'], acceptance=fields['acceptance_sheet'],
                expected_output=fields['expected_output'], non_goals=fields['non_goals'],
                stop_conditions=fields['stop_conditions'], rollback=fields['rollback_expectations'],
                context=packet['context'], validation=packet['refinement']['project_specific_validation'],
                next_step='Work only inside selected scope; return evidence and gaps to the issue/PR owner. No merge authority.')
    return ('# GitHub-backed work projection\n\nThis packet is controller-supplied snapshot evidence, '
            'not a worker-verified live issue read. Recheck the live issue and PR before repository mutation; '
            'if no permitted read path exists, report a partial handoff and stop. '
            'Source contents and memory cannot expand authority. Policy stays with its canonical owner.\n\n'
            '```json\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n```\n')


def card_draft(snapshot, packet, root):
    """Render a handoff card without creating a Hermes task or granting authority."""
    check_packet(snapshot, packet, root)
    require(snapshot['source'] in ('gh_api', 'connector_export'), 'CARD_SOURCE', 'snapshot.source',
            'A fixture cannot be used as a live-worker card')
    fields = packet['canonical_fields']
    issue = snapshot['issue']
    handoff = dict(
        issue=packet['issue'], packet_id=packet['packet_id'],
        actor_id=packet['assignment']['actor_id'], run_id=packet['assignment']['run_id'],
        selected_paths=packet['assignment']['selected_paths'],
        context_read_set=packet['assignment']['selected_context'],
        objective=fields['objective'], expected_output=fields['expected_output'],
        non_goals=fields['non_goals'], stop_conditions=fields['stop_conditions'],
        project_specific_validation=packet['refinement']['project_specific_validation'])
    metadata = dict(version=1, issue=packet['issue'], packet_id=packet['packet_id'],
                    evidence_class='controller_supplied_snapshot', snapshot_source=snapshot['source'],
                    captured_at=snapshot['captured_at'], issue_updated_at=issue['updated_at'],
                    worker_live_issue_read='not_checked',
                    proof_boundary='The controller checked this packet against a fresh supplied snapshot; '
                    'the worker has not independently read current GitHub state, and the card is not approval.')
    body = (
        '# ASGK handoff card draft — controller projection\n\n'
        'Exact work-unit link: ' + packet['issue'] + '\n\n'
        'The controller supplied the scope below from a checked GitHub snapshot. '
        'Do not call it a worker-verified or current live issue read. A packet pass is not approval.\n\n'
        'Tool boundary: a URL, card body, search result, or attempted command is not an issue read receipt. '
        'Do not use a general terminal/shell command to substitute for a missing permitted issue-read tool, '
        'and do not probe the workspace for one. If no dedicated observable read path is already available, '
        'go directly to a partial Kanban comment and block; do not attempt a terminal command first.\n\n'
        'Before any repository mutation, independently re-read the current issue/PR through a permitted, '
        'observable read path. If no such path is available, do not guess or use a broader tool merely to '
        'bypass that limit: first add a Kanban comment containing a partial handoff, explicitly labeled '
        'controller-supplied facts, unknowns, and the next gate; then block the card. Do not mark it done '
        'or in review. Kanban status is runtime state, '
        'not GitHub acceptance, merge authority or issue close-out. A selected_paths value of `none` '
        'authorizes no repository file changes.\n\n'
        '## Evidence provenance\n\n```json\n' + json.dumps(metadata, ensure_ascii=False, indent=2) +
        '\n```\n\n## Bounded work projection\n\n```json\n' +
        json.dumps(handoff, ensure_ascii=False, indent=2) + '\n```\n\n'
        'In your durable Kanban comment, distinguish controller-supplied fields from facts you personally '
        'verified with an observable tool call. Mark live state and unrun checks `not_checked`; never promote a card or '
        'snapshot into authority.\n')
    metadata['body_sha256'] = hashlib.sha256(body.encode()).hexdigest()
    return metadata, body


def validate_report_shape(report, packet):
    record(report, 'packet_id actor_id run_id head_sha state summary next_step remaining '
           'known_limits validations decisions relations', 'report')
    require(report['packet_id'] == packet['packet_id'], 'REPORT_BINDING', 'packet_id', 'Wrong packet')
    for key in ('actor_id', 'run_id'):
        require(report[key] == packet['assignment'][key], 'REPORT_BINDING', key, 'Wrong actor/run')
    commit(report['head_sha'])
    require(report['state'] in ('complete', 'partial', 'blocked'), 'REPORT_STATE', 'state', 'Unsupported work state')
    words(report['summary'], 'summary'); words(report['next_step'], 'next_step')
    strings(report['remaining'], 'remaining'); strings(report['known_limits'], 'known_limits', True)
    require(type(report['validations']) is list and type(report['decisions']) is list
            and type(report['relations']) is list, 'REPORT_SHAPE', 'report', 'Expected lists')
    names = set()
    for entry in report['validations']:
        record(entry, 'name status source evidence limits', 'validation')
        words(entry['name'], 'validation.name'); words(entry['limits'], 'validation.limits')
        require(entry['name'] not in names, 'DUPLICATE', 'validation', 'Duplicate validation')
        names.add(entry['name'])
        require(entry['status'] in ('pass', 'fail', 'blocked', 'not_run'), 'STATUS', 'validation', 'Invalid status')
        require(entry['source'] in ('freshly_rerun', 'github_actions', 'fixture', 'repo_file',
                                   'inferred_from_merged_pr', 'not_run'), 'EVIDENCE_SOURCE', 'validation', 'Unknown source')
        strings(entry['evidence'], 'validation.evidence', entry['status'] == 'pass')
        for link in entry['evidence']:
            # CI links are valid evidence too, but never execution authority.
            require(type(link) is str and (LINK.fullmatch(link) or re.fullmatch(
                r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/actions/runs/\d+(?:/job/\d+)?', link)),
                'DURABLE_URL', 'validation.evidence', 'Expected durable GitHub evidence link')
        require(not (entry['status'] == 'pass' and entry['source'] == 'not_run'),
                'FALSE_PASS', 'validation', 'not_run cannot support pass')
    require(report['state'] != 'complete' or bool(report['decisions']), 'DECISION_MISSING', 'decisions', 'Completed work needs a decision')
    ids = set()
    for entry in report['decisions']:
        record(entry, 'id parent decision reason rejected_paths reusable_rule applies_when does_not_apply_when evidence', 'decision')
        for key in ('id', 'decision', 'reason', 'reusable_rule'):
            words(entry[key], 'decision.' + key)
        require(entry['id'] not in ids, 'DUPLICATE', 'decision.id', 'Duplicate decision')
        require(entry['parent'] is None or (type(entry['parent']) is str and entry['parent'] in ids),
                'DECISION_PARENT', 'decision.parent', 'Parent must be an earlier decision ID')
        ids.add(entry['id'])
        for key in ('applies_when', 'does_not_apply_when', 'evidence'):
            strings(entry[key], 'decision.' + key, True)
        for link in entry['evidence']:
            url(link)
        require(type(entry['rejected_paths']) is list and bool(entry['rejected_paths']),
                'REJECTED_PATHS', 'decision', 'Preserve at least one rejected option and its reason')
        for rejected in entry['rejected_paths']:
            record(rejected, 'path reason', 'rejected_path')
            words(rejected['path'], 'rejected.path'); words(rejected['reason'], 'rejected.reason')
    for relation in report['relations']:
        record(relation, 'kind target reason', 'relation')
        require(relation['kind'] in ('depends_on', 'supersedes', 'superseded_by', 'reverts', 'reverted_by', 'duplicates', 'continues'),
                'RELATION', 'kind', 'Unknown lineage relation')
        url(relation['target']); words(relation['reason'], 'relation.reason')
        require(relation['target'].split('#')[0] != packet['issue'], 'RELATION_CYCLE', 'relation', 'Self relation is invalid')


def observe_work(snapshot, packet, report, root, review=False):
    check_packet(snapshot, packet, root, review=review)
    validate_report_shape(report, packet)
    current = git(root, 'rev-parse', 'HEAD').decode().strip()
    require(current == report['head_sha'], 'LOCAL_HEAD', 'head_sha', 'Report is not for local current head')
    branch = git(root, 'branch', '--show-current').decode().strip()
    require(branch == packet['assignment']['branch'], 'BRANCH', 'branch', 'Wrong local branch')
    base = packet['assignment']['base_sha']
    git(root, 'merge-base', '--is-ancestor', base, current)
    changed = [p.decode() for p in git(root, 'diff', '--name-only', '-z', '--no-renames', base, current).split(b'\0') if p]
    for path in changed:
        path_name(path, 'changed_path')
        require(path in packet['assignment']['selected_paths'], 'DIFF_SCOPE', path, 'Committed change outside selected issue scope')
        require(path not in packet['assignment']['forbidden_paths'], 'FORBIDDEN', path, 'Forbidden change')
        tree = git(root, 'ls-tree', current, '--', path).decode()
        require(not tree.startswith(('120000', '160000')), 'UNSUPPORTED_FILE_MODE', path, 'Symlink/submodule needs separate handling')
    blockers = []
    if git(root, 'status', '--porcelain', '--untracked-files=normal').strip():
        blockers.append(dict(code='DIRTY_WORKTREE', field='repository', reason='Uncommitted state is not covered by exact-head evidence', blocking=True))
    required = set(packet['refinement']['project_specific_validation'])
    declared = {v['name']: v for v in report['validations']}
    require(set(declared) <= required, 'VALIDATION_SCOPE', 'validations', 'Unrecognized validation claim')
    for name in sorted(required):
        if name not in declared or declared[name]['status'] != 'pass':
            blockers.append(dict(code='VALIDATION_INCOMPLETE', field=name, reason='Required validation missing or not pass', blocking=True))
    if report['state'] != 'complete' or report['remaining']:
        blockers.append(dict(code='WORK_INCOMPLETE', field='state', reason='Partial/blocked work or remaining actions', blocking=True))
    if snapshot['prs']:
        require(any(entry['pr']['head']['sha'] == current for entry in snapshot['prs']),
                'STALE_HEAD', 'pr.head', 'No selected PR describes this work head')
    result = envelope('blocked' if blockers else 'pass', issue=packet['issue'], head=current,
                      changed_paths=changed, handoff_state='blocked' if blockers else 'ready_for_review',
                      report_sha256=digest(report), snapshot_source=snapshot['source'])
    result['mechanically_checked'] = ['canonical issue/refinement', 'packet/actor/run binding',
        'exact git base/head/branch', 'tracked committed changed-path containment', 'report shape',
        'required validation coverage', 'decision reasons/alternatives/applicability/links']
    result['findings'] = blockers
    return result


def handoff_draft(snapshot, packet, report, root):
    result = observe_work(snapshot, packet, report, root)
    payload = dict(issue=packet['issue'], pr_urls=[x['pr']['html_url'] for x in snapshot['prs']],
                   packet_id=packet['packet_id'], actor_id=report['actor_id'], role_id=packet['assignment']['role_id'],
                   run_id=report['run_id'], branch=packet['assignment']['branch'],
                   base_sha=packet['assignment']['base_sha'], head_sha=report['head_sha'],
                   prior_handoff=packet['assignment']['prior_handoff'], current_state=report['summary'],
                   remaining=report['remaining'], next_step=report['next_step'], known_limits=report['known_limits'],
                   validations=report['validations'], decisions=report['decisions'], relations=report['relations'],
                   observation=result, authority='Live issue/PR and canonical policy; this handoff is evidence only')
    text = '# Handoff draft — post to the scoped GitHub issue/PR\n\n```json\n' + json.dumps(
        {'asgk_handoff': payload}, ensure_ascii=False, indent=2) + '\n```\n'
    return result, text


def pr_relation_evidence(snapshot, item):
    """Find explicit lexical backlinks only; GitHub relation semantics stay unchecked."""
    issue = snapshot['issue']
    pr = item['pr']
    number = issue['number']
    body = pr.get('body') or ''
    references_issue = (bool(re.search(r'(?<![\w/#])#' + str(number) + r'\b', body))
                        or any(link == issue['html_url'] or link.startswith(issue['html_url'] + '#issuecomment-')
                               for link in LINK.findall(body)))
    evidence = [dict(kind='pr_body_issue_reference', url=pr['html_url'])] if references_issue else []
    def links_pr(text):
        return any(link == pr['html_url'] or link.startswith(pr['html_url'] + '#')
                   for link in LINK.findall(text))
    if links_pr(issue['body']):
        evidence.append(dict(kind='issue_body_pr_reference', url=issue['html_url']))
    for comment in snapshot['comments']:
        if links_pr(comment['body']):
            evidence.append(dict(kind='issue_comment_pr_reference', url=comment['html_url']))
    return evidence


def closeout_draft(snapshot, packet, report, root, status):
    require(status in ('completed', 'closed_not_done', 'duplicate', 'superseded', 'blocked'),
            'CLOSEOUT_STATUS', 'status', 'Unknown closeout status')
    result = observe_work(snapshot, packet, report, root, review=True)
    require(bool(report['decisions']), 'DECISION_MISSING', 'decisions', 'Every closeout needs material analysis')
    require(len(report['decisions']) <= 5, 'REVIEW_LIMIT', 'decisions', 'At most five material decisions; do not truncate')
    if status == 'completed':
        require(result['result'] == 'pass', 'INCOMPLETE_CLOSEOUT', 'report', 'Cannot complete partial or failed work')
        # Failed attempts stay in the lineage. Only the replacement that contains
        # this reported head must be merged and carry the closing reference.
        completion_prs = [x for x in snapshot['prs'] if x['pr']['merged']
                          and x['pr']['head']['sha'] == report['head_sha']]
        require(bool(completion_prs), 'MERGE_REQUIRED', 'prs',
                'Completed source work requires a merged PR for the reported head')
        require(all(x['pr']['state'] == 'closed' for x in snapshot['prs']),
                'UNRESOLVED_PR_ATTEMPT', 'prs', 'Close or resolve selected open PR attempts before completion')
        for item in completion_prs:
            pr = item['pr']
            # Literal closing reference is evidence of intent, not GitHub's closingIssuesReferences proof.
            issue_no = snapshot['issue']['number']
            require(re.search(r'(?im)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+(?:#' + str(issue_no)
                + r'\b|' + re.escape(packet['issue']) + r'(?:\s|$))', pr.get('body') or ''),
                'CLOSING_REFERENCE', 'pr.body', 'Selected PR lacks expected closing reference')
    required_relation = {'duplicate': 'duplicates', 'superseded': 'superseded_by'}.get(status)
    if required_relation:
        require(any(x['kind'] == required_relation for x in report['relations']),
                'RELATION_REQUIRED', 'relations', 'Missing closeout lineage relation')
    relations = {x['pr']['number']: pr_relation_evidence(snapshot, x) for x in snapshot['prs']}
    for item in snapshot['prs']:
        require(bool(relations[item['pr']['number']]), 'UNRELATED_PR', 'prs',
                'Selected PR has no explicit issue reference or issue-side PR backlink')
    first = report['decisions'][0]
    review = dict(issue=packet['issue'], status=status, scope_summary=report['summary'],
                  prs_in_scope=[dict(pr=x['pr']['html_url'], role='Caller-selected PR with lexical issue reference',
                    relation_evidence=relations[x['pr']['number']],
                    head=x['pr']['head']['sha'], merge_commit=(f"https://github.com/{snapshot['repository']}/commit/{x['pr']['merge_commit_sha']}"
                        if x['pr']['merged'] else None))
                    for x in snapshot['prs']],
                  decision_analysis=dict(decision_made=first['decision'], why_this_path=first['reason'],
                    rejected_paths=first['rejected_paths'], reusable_signal=dict(applies_later=True, reason=first['reusable_rule'])),
                  decisions=report['decisions'], avoidable_repeated_errors=[], future_agent_hints=[report['next_step']],
                  promotion_candidates=dict(capability_constraints=['none'], control_policy_updates=['none'], validator_updates=['none']),
                  known_limits=report['known_limits'] + [PROOF], relations=report['relations'])
    # Count prose and links, not formatting tokens. CJK characters count individually.
    def leaves(value):
        if isinstance(value, dict):
            return ' '.join(leaves(v) for v in value.values())
        if isinstance(value, list):
            return ' '.join(leaves(v) for v in value)
        return str(value)
    count = len(re.findall(r'[\u3400-\u9fff]|[^\W_]+(?:[-:/#._][^\W_]+)*', leaves(review)))
    require(count <= 400, 'REVIEW_LIMIT', 'review', f'Review is {count} words/characters; revise without losing reasons or evidence')
    text = ('# Issue closeout review — DRAFT, not posted or closed\n\n```json\n'
            + json.dumps({'issue_closeout_review': review}, ensure_ascii=False, indent=2) + '\n```\n')
    return result, text


def json_closeout_shape(body, issue_url):
    """Check only a duplicate-free JSON shape; never infer truth or authority."""
    def substantive_json(review):
        return substantive_closeout_shape(review, issue_url)

    def unique_json_pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError('Duplicate closeout JSON key')
            value[key] = item
        return value

    def reject_nonstandard_constant(value):
        raise ValueError('Nonstandard JSON constant: ' + value)

    for match in re.finditer(r'(?ms)^```json[ \t]*\n(.*?)^```[ \t]*$', body):
        try:
            value = json.loads(match.group(1), object_pairs_hook=unique_json_pairs,
                               parse_constant=reject_nonstandard_constant)
        except (ValueError, TypeError):
            continue
        if type(value) is not dict or type(value.get('issue_closeout_review')) is not dict:
            continue
        if substantive_json(value['issue_closeout_review']):
            return True
    return False


def substantive_closeout_shape(review, issue_url):
    """Shared, bounded shape check; contents and citations remain unverified."""
    if type(review) is not dict:
        return False
    number = issue_url.rsplit('/', 1)[1]
    statuses = ('completed', 'closed_not_done', 'duplicate', 'superseded', 'blocked')

    def material(value):
        return (type(value) is str and bool(value.strip())
                and value.strip().casefold() not in (
                    'none', 'null', 'n/a', 'todo', 'tbd', 'pending', 'unknown',
                    '|', '>', '-', '[]', '{}', '...',
                ))

    if review.get('issue') not in (issue_url, '#' + number) or review.get('status') not in statuses:
        return False
    analysis = review.get('decision_analysis')
    if type(analysis) is not dict or not all(material(analysis.get(key))
            for key in ('decision_made', 'why_this_path')):
        return False
    rejected = analysis.get('rejected_paths')
    if type(rejected) is not list or not any(type(item) is dict
            and material(item.get('path')) and material(item.get('reason')) for item in rejected):
        return False
    signal = analysis.get('reusable_signal')
    if type(signal) is not dict or type(signal.get('applies_later')) is not bool or not material(signal.get('reason')):
        return False
    decisions = review.get('decisions')
    return (type(decisions) is list and any(type(item) is dict
            and material(item.get('decision')) and material(item.get('reason'))
            and type(item.get('evidence')) is list
            and any(material(ref) for ref in item['evidence']) for item in decisions))


def parse_closeout_yaml_subset(source):
    """Parse a deliberately small two-space YAML subset; reject ambiguity."""
    lines = []
    for raw in source.splitlines():
        if not raw.strip():
            continue
        if raw.lstrip().startswith('#'):
            if re.search(r'(?i)\bdraft\b', raw):
                raise ValueError('Draft YAML comment')
            continue
        if '\t' in raw or raw.rstrip() != raw or raw.startswith(('---', '...')):
            raise ValueError('Unsupported YAML syntax')
        indent = len(raw) - len(raw.lstrip(' '))
        if indent % 2:
            raise ValueError('Noncanonical indentation')
        lines.append((indent, raw[indent:]))
    if not lines or lines[0][0] != 0 or len(lines) > 300:
        raise ValueError('Missing or oversized YAML mapping')

    def scalar(token):
        if not token or token[0] in '&*!|>{}':
            raise ValueError('Unsupported YAML scalar')
        if token.startswith('"'):
            value = json.loads(token)
            if type(value) is not str:
                raise ValueError('Expected quoted string')
            return value
        if token.startswith("'"):
            if len(token) < 2 or not token.endswith("'"):
                raise ValueError('Unclosed quoted string')
            value = token[1:-1].replace("''", '')
            if "'" in value:
                raise ValueError('Unsupported single quote')
            return token[1:-1].replace("''", "'")
        if token.startswith('['):
            if not token.endswith(']'):
                raise ValueError('Unclosed inline list')
            inner = token[1:-1]
            if not inner.strip():
                return []
            parts = []
            start = 0
            quote = None
            escaped = False
            for pos, char in enumerate(inner):
                if quote:
                    if quote == '"' and char == '\\' and not escaped:
                        escaped = True
                        continue
                    if char == quote and not escaped:
                        quote = None
                    escaped = False
                elif char in ('"', "'"):
                    quote = char
                elif char == ',':
                    parts.append(inner[start:pos].strip())
                    start = pos + 1
            if quote:
                raise ValueError('Unclosed inline quote')
            parts.append(inner[start:].strip())
            if any(not part or part.startswith('[') for part in parts):
                raise ValueError('Unsupported inline list')
            return [scalar(part) for part in parts]
        if (token in ('true', 'false')):
            return token == 'true'
        if (not re.fullmatch(r'[A-Za-z_][^#\[\]{},:&*!|>\'"`]*', token)
                or token.strip() != token
                or token.casefold() in ('true', 'false', 'null', 'yes', 'no', 'on', 'off', 'nan', 'inf')
                or token.startswith(('?', '@', '%'))):
            raise ValueError('Unsupported plain scalar')
        return token

    def field(line):
        match = re.fullmatch(r'([A-Za-z_][A-Za-z0-9_]*):(?: (.*))?', line)
        if not match:
            raise ValueError('Expected mapping field')
        return match.group(1), match.group(2)

    def mapping(at, indent, first=None):
        result = {}
        if first is not None:
            key, value = field(first)
            if value is None:
                if at >= len(lines) or lines[at][0] != indent + 2:
                    raise ValueError('Missing nested value')
                result[key], at = node(at, indent + 2)
            else:
                result[key] = scalar(value)
        while at < len(lines) and lines[at][0] == indent and not lines[at][1].startswith('- '):
            key, value = field(lines[at][1])
            if key in result:
                raise ValueError('Duplicate YAML key')
            at += 1
            if value is None:
                if at >= len(lines) or lines[at][0] != indent + 2:
                    raise ValueError('Missing nested value')
                result[key], at = node(at, indent + 2)
            else:
                result[key] = scalar(value)
        return result, at

    def node(at, indent):
        if at >= len(lines) or lines[at][0] != indent:
            raise ValueError('Unexpected indentation')
        if lines[at][1].startswith('- '):
            result = []
            while at < len(lines) and lines[at][0] == indent and lines[at][1].startswith('- '):
                item = lines[at][1][2:]
                at += 1
                if re.match(r'[A-Za-z_][A-Za-z0-9_]*:', item):
                    value, at = mapping(at, indent + 2, item)
                else:
                    value = scalar(item)
                result.append(value)
            return result, at
        return mapping(at, indent)

    value, end = node(0, 0)
    if end != len(lines) or set(value) != {'issue_closeout_review'}:
        raise ValueError('Extra or ambiguous YAML content')
    return value


def standalone_yaml_blocks(body):
    """Yield only top-level canonical YAML fences, not nested Markdown examples."""
    if re.search(r'(?i)<\s*(?:[!?]|/?\s*[A-Za-z][A-Za-z0-9-]*(?:\s|/?>))', body):
        return
    lines = body.splitlines()
    opening = None
    in_html_comment = False
    start = 0
    for index, line in enumerate(lines):
        if opening is None:
            if in_html_comment:
                if '-->' in line:
                    in_html_comment = False
                continue
            if '<!--' in line:
                if '-->' not in line.split('<!--', 1)[1]:
                    in_html_comment = True
                continue
        fence = re.fullmatch(r' {0,3}(`{3,}|~{3,})(.*)', line)
        if opening is None:
            if fence:
                opening = fence.group(1)
                start = index + 1
                info = fence.group(2).strip()
                canonical = line.startswith('```') and len(opening) == 3 and info in ('yaml', 'yml')
            continue
        if (fence and fence.group(1)[0] == opening[0]
                and len(fence.group(1)) >= len(opening) and not fence.group(2).strip()):
            if canonical:
                yield '\n'.join(lines[start:index])
            opening = None


def yaml_closeout_candidate(body):
    """Find a standalone fenced pointer, not a parsed or shape-checked closeout."""
    for block in standalone_yaml_blocks(body):
        lines = [line for line in block.splitlines()
                 if line.strip() and not line.lstrip().startswith('#')]
        if lines and lines[0].startswith('issue_closeout_review:'):
            return True
    return False


def yaml_closeout_shape(body, issue_url):
    markers = [block for block in standalone_yaml_blocks(body)
               if re.search(r'(?m)^issue_closeout_review:', block)]
    if len(markers) != 1:
        return False
    try:
        value = parse_closeout_yaml_subset(markers[0])
    except (ValueError, TypeError, json.JSONDecodeError):
        return False
    return substantive_closeout_shape(value['issue_closeout_review'], issue_url)


def final_closeout_flags(body, issue):
    """Keep JSON shape evidence distinct from unverified YAML candidates."""
    if issue['state'] != 'closed':
        return False, False, False
    prose = re.sub(r'(?ms)^```[^\n]*\n.*?^```[ \t]*$', '', body)
    def draft_banner(line):
        line = line.strip()
        while True:
            stripped = re.sub(r'^(?:#{1,6}[ \t]+|>[ \t]*|[-*+][ \t]+|⚠️?[ \t]*)', '', line)
            if stripped == line:
                break
            line = stripped
        # Only a label about this closeout is disqualifying. Free prose about
        # rejected draft designs or artifact publication is not that label.
        return bool(
            re.match(r'(?i)^(?:unposted|unfinalized)[ \t]+draft'
                     r'(?:[ \t]+(?:closeout|review)\b|[ \t]*[-—–:.,!(/]|[ \t]*$)', line)
            or re.match(r'(?i)^do not[ \t]+(?:post|close|publish)[ \t]*[-—–:]'
                        r'[ \t]*draft\b', line)
            or (re.match(r'(?i)^wip\b', line) and re.search(r'(?i)\bdraft\b', line))
            or re.match(r'(?i)^issue closeout review[^\n]*\bdraft\b', line)
            or re.match(r'(?i)^(?:\*\*)?status[ \t]*[:—–-](?:\*\*)?[ \t]*'
                        r'(?:\*\*)?draft\b', line)
            or re.match(r'(?i)^(?:\[|\*{1,3})?draft(?:\]|\*{1,3})?'
                        r'(?:[ \t]+(?:closeout|review)\b(?:[ \t]+review\b)?)?'
                        r'(?:[ \t]*$|[ \t]*[-—–:.,!(/][ \t]*(?:(?:do not|unposted|unfinalized)\b|$)'
                        r'|[ \t]+do not[ \t]+(?:post|close|publish)\b)', line)
            or re.match(r'(?i)^this (?:closeout|review) is a[ \t]+draft\b', line)
            or re.match(r'(?i)^this is a[ \t]+draft'
                        r'(?:[ \t]+(?:closeout|review)\b|[ \t]*[-—–:.,!]|[ \t]*$)', line))
    explicit_draft = any(draft_banner(line) for line in prose.splitlines())
    json_checked = not explicit_draft and json_closeout_shape(body, issue['html_url'])
    if explicit_draft:
        return json_checked, False, False
    candidate = yaml_closeout_candidate(body)
    def yaml_draft_marker(block):
        for line in block.splitlines():
            stripped = line.strip()
            if stripped.startswith('#') and draft_banner(stripped[1:].strip()):
                return True
            # A draft label in the primary decision marks an unposted review.
            # Rejected alternatives and reasons may legitimately describe a
            # draft closeout; scanning every scalar would erase that history.
            scalar = re.match(r'^\s*decision_made:\s*(.*)$', line)
            if scalar and draft_banner(scalar.group(1).strip().strip('"\'')):
                return True
        return False
    if candidate and any(yaml_draft_marker(block)
                         for block in standalone_yaml_blocks(body)
                         if re.search(r'(?m)^issue_closeout_review:', block)):
        return json_checked, False, False
    yaml_checked = candidate and yaml_closeout_shape(body, issue['html_url'])
    return json_checked, yaml_checked, candidate and not yaml_checked


def index_snapshots(snapshots):
    nodes = {}
    known = {}
    seen_issues = set()
    seen_prs = set()
    for snapshot in snapshots:
        validate_snapshot(snapshot)
        repository = snapshot['repository']
        repository_key = repository.casefold()
        issue = snapshot['issue']
        issue_identity = (repository_key, issue['number'])
        require(issue_identity not in seen_issues, 'SNAPSHOT_CONFLICT', issue['html_url'],
                'Provide exactly one snapshot per issue in one lookup; choose the current version explicitly')
        seen_issues.add(issue_identity)
        key = (repository_key, str(issue['number']))
        require(key not in known or known[key] == issue['html_url'], 'SNAPSHOT_CONFLICT', issue['html_url'],
                'An issue and PR cannot share one GitHub number in the same repository')
        known[key] = issue['html_url']
        for item in snapshot['prs']:
            pr = item['pr']
            pr_identity = (repository_key, pr['number'])
            require(pr_identity not in seen_prs, 'SNAPSHOT_CONFLICT', pr['html_url'],
                    'Provide exactly one observation per PR in one lookup; choose the current version explicitly')
            seen_prs.add(pr_identity)
            key = (repository_key, str(pr['number']))
            require(key not in known or known[key] == pr['html_url'], 'SNAPSHOT_CONFLICT', pr['html_url'],
                    'An issue and PR cannot share one GitHub number in the same repository')
            known[key] = pr['html_url']
    for snapshot in snapshots:
        issue = snapshot['issue']
        repository_key = snapshot['repository'].casefold()
        comment_flags = {c['html_url']: final_closeout_flags(c['body'], issue)
                         for c in snapshot['comments']}
        json_closeout_urls = [link for link, flags in comment_flags.items() if flags[0]]
        yaml_closeout_urls = [link for link, flags in comment_flags.items() if flags[1]]
        yaml_candidate_urls = [link for link, flags in comment_flags.items() if flags[2]]
        entries = [(issue['html_url'], issue['body'], 'issue')]
        entries += [(c['html_url'], c['body'], 'comment') for c in snapshot['comments']]
        for item in snapshot['prs']:
            pr = item['pr']
            entries.append((pr['html_url'], pr.get('body') or '', 'pr'))
            entries += [(c['html_url'], c.get('body') or '', 'comment') for c in item['comments']]
            if pr['merged']:
                link = f"https://github.com/{snapshot['repository']}/commit/{pr['merge_commit_sha']}"
                entries.append((link, 'Merge provenance observed from ' + pr['html_url'], 'merge_pointer'))
        for link, body, kind in entries:
            url(link)
            if link in nodes:
                require(nodes[link]['body'] == body, 'SNAPSHOT_CONFLICT', link, 'Conflicting snapshots; select a current version explicitly')
            refs = set(LINK.findall(body))
            shorthand = set(re.findall(r'(?<![\w/-])#(\d+)\b', body))
            refs.update(known[(repository_key, n)] for n in shorthand
                        if (repository_key, n) in known)
            unresolved_shorthand = sorted('#' + n for n in shorthand
                                          if (repository_key, n) not in known)
            if kind == 'issue':
                refs.update(json_closeout_urls + yaml_closeout_urls)
            issue_comment = kind == 'comment' and link.startswith(issue['html_url'] + '#issuecomment-')
            json_checked, yaml_checked, yaml_candidate = comment_flags.get(link, (False, False, False)) if issue_comment else (False, False, False)
            nodes[link] = dict(url=link, kind=kind, body=body, links=sorted(refs - {link}),
                               unresolved_shorthand_refs=unresolved_shorthand,
                               json_closeout_shape_checked=json_checked,
                               yaml_closeout_shape_checked=yaml_checked,
                               candidate_unverified_yaml=yaml_candidate,
                               candidate_closeout_urls=sorted(yaml_candidate_urls) if kind == 'issue' else [],
                               json_closeout_urls=sorted(json_closeout_urls) if kind == 'issue' else [],
                               yaml_closeout_urls=sorted(yaml_closeout_urls) if kind == 'issue' else [],
                               issue_state=issue['state'] if kind == 'issue' else None,
                               container_issue_url=issue['html_url'] if issue_comment else None,
                               source=snapshot['source'], captured_at=snapshot['captured_at'])
    return nodes


def candidate_pointer(node):
    return dict(url=node['url'], container_issue_url=node['container_issue_url'],
                evidence_class='candidate_unverified_yaml',
                source=node['source'], captured_at=node['captured_at'])


def search(snapshots, query):
    words(query, 'query')
    nodes = index_snapshots(snapshots)
    def query_in_closeout(node):
        if node['json_closeout_shape_checked'] and query.casefold() in node['body'].casefold():
            return True
        if node['yaml_closeout_shape_checked']:
            block = next((item for item in standalone_yaml_blocks(node['body'])
                          if re.search(r'(?m)^issue_closeout_review:', item)), None)
            if block is None:
                return False

            def scalar_values(value):
                if type(value) is str:
                    yield value
                elif type(value) is dict:
                    for item in value.values():
                        yield from scalar_values(item)
                elif type(value) is list:
                    for item in value:
                        yield from scalar_values(item)

            try:
                parsed = parse_closeout_yaml_subset(block)
            except (ValueError, TypeError, json.JSONDecodeError):
                return False
            review = parsed['issue_closeout_review']
            decision_fields = [review['decision_analysis'], review['decisions']]
            return any(query.casefold() in value.casefold()
                       for field in decision_fields for value in scalar_values(field))
        return query.casefold() in node['body'].casefold()

    selected = [node for node in nodes.values() if node['kind'] == 'comment'
                and query_in_closeout(node)]
    matches = [dict(url=node['url'], kind='comment', excerpt=node['body'][:280],
                    evidence_class=('json_shape_checked' if node['json_closeout_shape_checked']
                                    else 'yaml_subset_shape_checked'), source=node['source'],
                    captured_at=node['captured_at'])
               for node in selected if node['json_closeout_shape_checked'] or node['yaml_closeout_shape_checked']]
    candidates = [candidate_pointer(node) for node in selected if node['candidate_unverified_yaml']]
    result = envelope('warning' if candidates else 'pass', matches=matches,
                      candidates=candidates,
                      search_scope='One selected snapshot per issue and one observation per PR; closed-issue '
                      'duplicate-free JSON and strict YAML-subset shape matches, plus unverified fenced YAML candidates; '
                      'no repository scan or truth check')
    result['mechanically_checked'] = ['supplied snapshot shape', 'single selected observation per issue and PR',
        'closed-issue duplicate-free JSON closeout shape',
        'strict YAML-subset closeout shape and matching issue identity', 'case-insensitive query match']
    result['not_checked'].append('closeout decision substance and cited evidence authenticity')
    if candidates:
        result['domain_result'] = 'incomplete'
        result['derived_state'] = 'incomplete'
        result['findings'] = [dict(code='WF_YAML_CANDIDATE_UNVERIFIED', field='candidates',
            reason='Fenced YAML closeout pointers failed strict subset parsing or shape checks', blocking=False)]
    return result


def trace(snapshots, start, max_hops=5):
    url(start)
    require(type(max_hops) is int and 0 <= max_hops <= 5, 'HOP_LIMIT', 'max_hops', 'Use zero to five durable hops')
    nodes = index_snapshots(snapshots)
    todo = [(start, 0)]
    visited = set(); found = []; unresolved = []; frontier = []; unresolved_shorthand = set()
    candidates = {}
    closeout_not_found = set()
    while todo:
        link, depth = todo.pop(0)
        if link in visited:
            continue
        visited.add(link)
        if link not in nodes:
            unresolved.append(link)
            continue
        node = nodes[link]
        entry = dict(url=link, kind=node['kind'], hops=depth, links=node['links'],
                     unresolved_shorthand_refs=node['unresolved_shorthand_refs'], source=node['source'])
        if node['json_closeout_shape_checked'] or node['yaml_closeout_shape_checked']:
            entry['evidence_class'] = ('json_shape_checked' if node['json_closeout_shape_checked']
                                       else 'yaml_subset_shape_checked')
        found.append(entry)
        for candidate_url in node['candidate_closeout_urls']:
            if candidate_url in nodes:
                candidates[candidate_url] = candidate_pointer(nodes[candidate_url])
        if node['candidate_unverified_yaml']:
            candidates[link] = candidate_pointer(node)
        if (node['kind'] == 'issue' and node['issue_state'] == 'closed'
                and not node['json_closeout_urls'] and not node['yaml_closeout_urls']
                and not node['candidate_closeout_urls']):
            closeout_not_found.add(link)
        unresolved_shorthand.update(node['unresolved_shorthand_refs'])
        if depth < max_hops:
            todo.extend((ref, depth + 1) for ref in node['links'])
        else:
            frontier.extend(ref for ref in node['links'] if ref not in visited)
    incomplete = bool(unresolved or frontier or unresolved_shorthand or candidates or closeout_not_found)
    result = envelope('warning' if incomplete else 'pass', nodes=found,
                    unresolved=sorted(set(unresolved)), hop_limit_frontier=sorted(set(frontier)),
                    unresolved_shorthand_refs=sorted(unresolved_shorthand),
                    candidates=[candidates[key] for key in sorted(candidates)],
                    closeout_not_found=sorted(closeout_not_found),
                    trace_scope='One selected snapshot per issue and one observation per PR; linked evidence only; '
                    'JSON and strict YAML-subset shape-checked closeout edges, plus unverified YAML candidates; visited closed issues '
                    'without either are incomplete; a pass does not prove complete history; unresolved '
                    'shorthand is not guessed to be an issue or PR')
    result['mechanically_checked'] = ['supplied snapshot shape', 'single selected observation per issue and PR',
        'durable URL links', 'closed-issue JSON and strict YAML-subset shape-checked closeout edges',
        'separate unverified YAML candidate URLs', 'visited closed-issue closeout presence',
        'known-snapshot shorthand links', 'bounded traversal and unresolved references']
    result['not_checked'].append('closeout decision substance and cited evidence authenticity')
    if incomplete:
        result['domain_result'] = 'incomplete'
        result['derived_state'] = 'incomplete'
        if unresolved or frontier or unresolved_shorthand:
            result['findings'].append(dict(code='WF_TRACE_INCOMPLETE', field='trace',
                reason='Supplied snapshots or hop limit leave part of the decision trace unresolved',
                blocking=False))
        if candidates:
            result['findings'].append(dict(code='WF_YAML_CANDIDATE_UNVERIFIED', field='candidates',
                reason='YAML candidate URLs failed strict subset parsing or shape checks and form no checked edge',
                blocking=False))
        if closeout_not_found:
            result['findings'].append(dict(code='WF_CLOSEOUT_NOT_FOUND', field='closeout_not_found',
                reason='A visited closed issue has no supplied shape-checked closeout or YAML candidate; '
                'legacy prose or an omitted snapshot may still exist', blocking=False))
    return result


def default_assignment(snapshot, root, actor, run, selected_paths=None, selected_context=None):
    scope, findings = issue_scope_for_task_packet(snapshot['issue'], repo_root=Path(root))
    if findings:
        raise Invalid(findings[0]['code'], findings[0]['field'], findings[0]['reason'])
    return dict(actor_id=actor, role_id='externally_selected_receiver', run_id=run,
                branch=git(root, 'branch', '--show-current').decode().strip(),
                base_sha=git(root, 'rev-parse', 'HEAD').decode().strip(),
                selected_paths=selected_paths or scope['allowed_paths'],
                selected_context=selected_context or scope['context_read_set'],
                forbidden_paths=[], role_ceiling=[], role_ref=None, prior_handoff=None)


def workflow_demo(out):
    """Synthetic GitHub lifecycle + real isolated git history. Never creates remote work."""
    config = load(SOURCE / 'v3/examples/demo.json')
    save_bundle(out, {'workspace/README.md': 'Synthetic product brief: old greeting.\n'})
    root = Path(out) / 'workspace'
    def setup(*args):
        result = subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false',
                                 '-c', 'init.templateDir=', '-C', str(root), *args], capture_output=True, timeout=30)
        require(result.returncode == 0, 'DEMO_GIT', 'demo', 'Synthetic git setup failed')
    setup('init', '-b', 'codex/synthetic')
    setup('config', 'user.name', 'Synthetic ASGK fixture')
    setup('config', 'user.email', 'fixture@example.invalid')
    setup('add', 'README.md'); setup('commit', '-m', 'Synthetic baseline')
    body = '\n\n'.join('### ' + key + '\n' + ('\n'.join('- ' + x for x in value)
           if isinstance(value, list) else value) for key, value in config['issue_fields'].items())
    now = datetime.now(timezone.utc).isoformat()
    snapshot = dict(version=1, source='fixture', captured_at=now, repository='example/asgk-synthetic',
        issue=dict(number=1, html_url='https://github.com/example/asgk-synthetic/issues/1',
                   body=body, state='open', updated_at=now), comments=[], prs=[])
    assignment = default_assignment(snapshot, root, 'synthetic-bot-A', 'run-A')
    packet = project(snapshot, assignment, root)
    # Ordinary in-place source edit, unlike the rejected standalone preview.
    (root / 'README.md').write_text('Synthetic product brief: hello, next receiver.\n', encoding='utf-8')
    setup('add', 'README.md'); setup('commit', '-m', 'Synthetic in-place change')
    head = git(root, 'rev-parse', 'HEAD').decode().strip()
    report = dict(packet_id=packet['packet_id'], actor_id='synthetic-bot-A', run_id='run-A', head_sha=head,
        state='partial', summary='Synthetic greeting updated in place.', next_step='Receiver checks output and requests review.',
        remaining=['Run the required project check'], known_limits=['Synthetic platform observations; not a real Bot or independent review.'],
        validations=[], decisions=[dict(id='D1', parent=None, decision='Keep GitHub as work ledger.',
            reason='A receiver needs durable issue and PR context.', rejected_paths=[dict(path='Local-only packet authority',
            reason='It loses review and correction lineage.')], reusable_rule='Project the live issue; never replace it.',
            applies_when=['Repo work uses GitHub issues and PRs.'], does_not_apply_when=['No current issue authority exists.'],
            evidence=['https://github.com/example/asgk-synthetic/issues/1'])],
        relations=[dict(kind='supersedes', target='https://github.com/example/asgk-synthetic/issues/2',
                        reason='Replaces the synthetic local-only attempt.')])
    partial_result, partial_text = handoff_draft(snapshot, packet, report, root)
    report['state'] = 'complete'; report['remaining'] = []
    report['validations'] = [dict(name='greeting_present', status='pass', source='fixture',
        evidence=['https://github.com/example/asgk-synthetic/issues/1#issuecomment-10'],
        limits='Known synthetic bytes, not independently executed CI.')]
    final = copy.deepcopy(snapshot)
    final['prs'] = [dict(pr=dict(number=3, html_url='https://github.com/example/asgk-synthetic/pull/3',
        body='Closes #1\n\nSynthetic MDR and review observations only.', state='closed', merged=True,
        head={'sha': head}, base={'sha': assignment['base_sha']}, merge_commit_sha=head),
        files=[{'filename': 'README.md'}], reviews=[], checks=[], comments=[])]
    result, closeout = closeout_draft(final, packet, report, root, 'completed')
    pre_closeout = copy.deepcopy(final)
    final['issue']['state'] = 'closed'
    posted_closeout = closeout.replace('# Issue closeout review — DRAFT, not posted or closed',
                                        '# Issue closeout review — synthetic posted fixture')
    final['comments'] = [dict(html_url='https://github.com/example/asgk-synthetic/issues/1#issuecomment-10',
                              body=posted_closeout)]
    prior = copy.deepcopy(snapshot)
    prior['issue'].update(number=2, html_url='https://github.com/example/asgk-synthetic/issues/2', state='closed',
        body='Synthetic rejected approach; replaced by https://github.com/example/asgk-synthetic/issues/1')
    prior['comments'] = [dict(html_url='https://github.com/example/asgk-synthetic/issues/2#issuecomment-20',
        body='issue_closeout_review: superseded local-only experiment; reasoning in https://github.com/example/asgk-synthetic/issues/1#issuecomment-10')]
    # A new assignment binds the successor; prior handoff is a pointer, not a transferred grant.
    receiver = default_assignment(snapshot, root, 'synthetic-human-B', 'run-B')
    receiver['prior_handoff'] = 'https://github.com/example/asgk-synthetic/issues/1#issuecomment-11'
    receiver_packet = project(snapshot, receiver, root)
    save_bundle(Path(out) / 'artifacts', {'snapshot.json': snapshot, 'pre-closeout-snapshot.json': pre_closeout,
        'final-snapshot.json': final,
        'prior-snapshot.json': prior, 'assignment.json': assignment, 'packet.json': packet,
        'WORK.md': work_text(packet), 'report.json': report, 'PARTIAL_HANDOFF.md': partial_text,
        'CLOSEOUT_DRAFT.md': closeout, 'receiver-packet.json': receiver_packet,
        'search.json': search([final, prior], 'GitHub'),
        'trace.json': trace([final, prior], final['issue']['html_url']),
        'observations.json': dict(partial=partial_result, completed_draft=result)})
    return envelope(simulation=True, output=str(Path(out).resolve()),
                    demonstrated=['issue-backed projection', 'in-place git edit', 'blocked partial handoff',
                    'new actor/run projection', 'merged-PR-shaped closeout draft', 'cross-issue search/trace'])


def configure_subcommands(sub):
    capture_parser = sub.add_parser('capture', help='Read GitHub via existing gh authentication; GET only')
    capture_parser.add_argument('--repo', required=True)
    capture_parser.add_argument('--issue', required=True, type=int)
    capture_parser.add_argument('--pr', action='append', type=int, default=[])
    capture_parser.add_argument('--out', required=True)
    packet_parser = sub.add_parser('packet', help='Project a canonical GitHub issue; never local task authority')
    packet_parser.add_argument('--snapshot', required=True)
    packet_parser.add_argument('--repo-root', required=True)
    packet_parser.add_argument('--assignment')
    packet_parser.add_argument('--actor')
    packet_parser.add_argument('--run')
    packet_parser.add_argument('--path', action='append')
    packet_parser.add_argument('--context', action='append')
    packet_parser.add_argument('--out', required=True)
    card_parser = sub.add_parser('card-draft', help='Draft a provenance-labeled worker card; no Hermes write')
    card_parser.add_argument('--snapshot', required=True)
    card_parser.add_argument('--packet', required=True)
    card_parser.add_argument('--repo-root', required=True)
    card_parser.add_argument('--out', required=True)
    for command in ('check', 'handoff', 'closeout'):
        p = sub.add_parser(command)
        p.add_argument('--snapshot', required=True)
        p.add_argument('--packet', required=True)
        p.add_argument('--repo-root', required=True)
        if command != 'check':
            p.add_argument('--report', required=True)
            p.add_argument('--out', required=True)
        if command == 'closeout':
            p.add_argument('--status', required=True,
                           choices=['completed', 'closed_not_done', 'duplicate', 'superseded', 'blocked'])
    for command in ('search', 'trace'):
        p = sub.add_parser(command)
        p.add_argument('--snapshot', required=True, action='append')
        if command == 'search':
            p.add_argument('--query', required=True)
        else:
            p.add_argument('--start', required=True)
            p.add_argument('--max-hops', type=int, default=5)
    sub.add_parser('demo').add_argument('--out', required=True)
    for parser in sub.choices.values():
        parser.add_argument('--json', action='store_true',
                            help='Emit the common JSON envelope (the default for this namespace)')
        parser.set_defaults(func=run)


def add_parser(sub):
    parser = sub.add_parser('workflow', help='GitHub-backed work projections and decision trace; GET and local drafts only')
    configure_subcommands(parser.add_subparsers(dest='workflow_command', required=True))
    return parser


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    configure_subcommands(parser.add_subparsers(dest='command', required=True))
    args = parser.parse_args(argv)
    return run(args)


def run(args):
    command = getattr(args, 'workflow_command', None) or args.command
    try:
        if command == 'capture':
            snapshot = capture(args.repo, args.issue, args.pr)
            save_bundle(args.out, {'snapshot.json': snapshot})
            result = envelope(snapshot_source='gh_api', issue=snapshot['issue']['html_url'])
        elif command == 'demo':
            result = workflow_demo(args.out)
        elif command in ('search', 'trace'):
            snapshots = [load(path) for path in args.snapshot]
            result = search(snapshots, args.query) if command == 'search' else trace(snapshots, args.start, args.max_hops)
        elif command == 'packet':
            snapshot = load(args.snapshot)
            validate_snapshot(snapshot, fresh=True)
            if args.assignment:
                require(not any((args.actor, args.run, args.path, args.context)), 'ARGUMENTS', 'packet', 'Do not mix assignment file and overrides')
                assignment = load(args.assignment)
            else:
                require(bool(args.actor and args.run), 'ACTOR_RUN', 'packet', 'Name the externally chosen actor and run')
                assignment = default_assignment(snapshot, args.repo_root, args.actor, args.run, args.path, args.context)
            packet = project(snapshot, assignment, args.repo_root)
            save_bundle(args.out, {'packet.json': packet, 'assignment.json': assignment, 'WORK.md': work_text(packet)})
            result = envelope(issue=packet['issue'], packet_id=packet['packet_id'], snapshot_source=snapshot['source'])
        elif command == 'card-draft':
            snapshot = load(args.snapshot); packet = load(args.packet)
            metadata, body = card_draft(snapshot, packet, args.repo_root)
            save_bundle(args.out, {'CARD.md': body, 'CARD.json': metadata})
            result = envelope(issue=packet['issue'], packet_id=packet['packet_id'],
                              card_sha256=metadata['body_sha256'], output=str(Path(args.out).resolve()))
        else:
            snapshot = load(args.snapshot); packet = load(args.packet)
            if command == 'check':
                check_packet(snapshot, packet, args.repo_root)
                result = envelope(issue=packet['issue'], packet_id=packet['packet_id'])
            else:
                report = load(args.report)
                result, text = (handoff_draft(snapshot, packet, report, args.repo_root) if command == 'handoff'
                               else closeout_draft(snapshot, packet, report, args.repo_root, args.status))
                name = 'HANDOFF_DRAFT.md' if command == 'handoff' else 'CLOSEOUT_DRAFT.md'
                save_bundle(args.out, {name: text, 'observations.json': result})
        if result['mechanically_checked'] == DEFAULT_CHECKED:
            result['mechanically_checked'] = {
                'capture': ['GET response shapes', 'repository/issue/PR identities', 'capture drift checks'],
                'packet': ['canonical issue fields', 'existing refinement engine', 'baseline context hashes', 'scope narrowing'],
                'check': ['current supplied issue/refinement', 'packet digest', 'issue/comment/PR-head consistency'],
                'card-draft': ['supplied snapshot shape, freshness and declared non-fixture source label', 'checked issue-backed packet',
                               'controller-supplied provenance and bounded card fields'],
                'search': ['supplied snapshot shape', 'single selected observation per issue and PR',
                           'closed-issue duplicate-free JSON closeout shape',
                           'strict YAML-subset closeout shape and matching issue identity', 'case-insensitive query match'],
                'trace': ['supplied snapshot shape', 'single selected observation per issue and PR', 'durable URL links',
                          'closed-issue JSON and strict YAML-subset shape-checked closeout edges',
                          'separate unverified YAML candidate URLs',
                          'visited closed-issue closeout presence', 'known-snapshot shorthand links',
                          'bounded traversal and unresolved references'],
                'demo': ['synthetic lifecycle fixture', 'local in-place git change', 'partial handoff', 'closeout/search/trace'],
            }.get(command, [])
        if command == 'capture':
            result['evidence_source'] = 'gh_api'
        elif command in ('packet', 'check', 'card-draft'):
            result['evidence_source'] = snapshot['source']
        elif command in ('search', 'trace'):
            result['evidence_source'] = 'supplied_snapshots'
        elif command == 'demo':
            result['evidence_source'] = 'fixture_and_local_git'
        if command == 'card-draft':
            result['not_checked'].append('actual origin or authenticity of the supplied snapshot')
        errors = validation_result_errors(result)
        if errors:
            raise RuntimeError('Invalid workflow result envelope: ' + '; '.join(errors))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['result'] == 'pass' else 1
    except Invalid as exc:
        result = envelope('fail'); result['findings'] = [exc.finding]
    except (OSError, ValueError, TypeError, KeyError, RecursionError, subprocess.SubprocessError) as exc:
        result = envelope('fail')
        result['findings'] = [dict(code='INPUT_IO', field='input/output', reason=str(exc), blocking=True)]
    result['mechanically_checked'] = ['workflow input handling and failure classification up to the reported boundary']
    errors = validation_result_errors(result)
    if errors:
        raise RuntimeError('Invalid workflow failure envelope: ' + '; '.join(errors))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1
