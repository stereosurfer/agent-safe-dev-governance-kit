"""GitHub-native candidate. Read-only transport; every generated comment is a draft."""
import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from asgk3 import Invalid, canonical, digest, load, path_name, record, require, save_bundle, strings, timestamp, words

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE / 'scripts'))
from asgk_lib.task_packet import (evaluate_task_packet, issue_scope_for_task_packet,
                                 is_context_pseudo_ref, path_matches_allowed)

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


def envelope(result='pass', **extra):
    return dict(result=result, evidence_source='snapshot_and_local_observation',
                mechanically_checked=[], not_checked=['current live authorization', 'test execution',
                'semantic correctness', 'human approval', 'runtime side effects'],
                human_gate={'status': 'not_checked'}, proof_boundary=PROOF, findings=[], **extra)


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


def structured_closeout(body, issue_url):
    """Recognize same-issue fenced closeouts, never a bare marker or quote."""
    number = issue_url.rsplit('/', 1)[1]
    for match in re.finditer(r'(?ms)^```(json|yaml)[ \t]*\n(.*?)^```[ \t]*$', body):
        language, block = match.groups()
        if language == 'json':
            try:
                value = json.loads(block)
            except (ValueError, TypeError):
                continue
            if type(value) is not dict or type(value.get('issue_closeout_review')) is not dict:
                continue
            review = value['issue_closeout_review']
            if (review.get('issue') in (issue_url, '#' + number)
                    and review.get('status') in ('completed', 'closed_not_done', 'duplicate', 'superseded', 'blocked')
                    and type(review.get('decision_analysis')) is dict):
                return True
        else:
            lines = block.splitlines()
            if not lines or lines[0] != 'issue_closeout_review:':
                continue
            issue = re.search(r'(?m)^  issue:[ \t]*["\']?([^"\'\s]+)["\']?[ \t]*$', block)
            status = re.search(r'(?m)^  status:[ \t]*(\w+)[ \t]*$', block)
            if (issue and issue.group(1) in (issue_url, '#' + number)
                    and status and status.group(1) in ('completed', 'closed_not_done', 'duplicate', 'superseded', 'blocked')
                    and re.search(r'(?m)^  decision_analysis:[ \t]*$', block)):
                return True
    return False


def final_closeout_comment(body, issue):
    """Index only closed-issue comments without the generator's draft banner."""
    return (issue['state'] == 'closed'
            and not re.search(r'(?im)^#{1,6}[ \t]+issue closeout review[^\n]*\bdraft\b', body)
            and structured_closeout(body, issue['html_url']))


def index_snapshots(snapshots):
    nodes = {}
    known = {}
    for snapshot in snapshots:
        validate_snapshot(snapshot)
        repository = snapshot['repository']
        issue = snapshot['issue']
        key = (repository, str(issue['number']))
        require(key not in known or known[key] == issue['html_url'], 'SNAPSHOT_CONFLICT', issue['html_url'],
                'An issue and PR cannot share one GitHub number in the same repository')
        known[key] = issue['html_url']
        for item in snapshot['prs']:
            pr = item['pr']
            key = (repository, str(pr['number']))
            require(key not in known or known[key] == pr['html_url'], 'SNAPSHOT_CONFLICT', pr['html_url'],
                    'An issue and PR cannot share one GitHub number in the same repository')
            known[key] = pr['html_url']
    for snapshot in snapshots:
        issue = snapshot['issue']
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
            refs.update(known[(snapshot['repository'], n)] for n in shorthand
                        if (snapshot['repository'], n) in known)
            unresolved_shorthand = sorted('#' + n for n in shorthand
                                          if (snapshot['repository'], n) not in known)
            if kind == 'issue':
                refs.update(c['html_url'] for c in snapshot['comments']
                            if final_closeout_comment(c['body'], issue))
            nodes[link] = dict(url=link, kind=kind, body=body, links=sorted(refs - {link}),
                               unresolved_shorthand_refs=unresolved_shorthand,
                               structured_closeout=(kind == 'comment' and
                                   final_closeout_comment(body, issue)
                                   and link.startswith(issue['html_url'] + '#issuecomment-')),
                               source=snapshot['source'], captured_at=snapshot['captured_at'])
    return nodes


def search(snapshots, query):
    words(query, 'query')
    nodes = index_snapshots(snapshots)
    return envelope(matches=[dict(url=n['url'], kind=n['kind'], excerpt=n['body'][:280], source=n['source'])
        for n in nodes.values() if n['kind'] == 'comment' and n['structured_closeout']
        and query.casefold() in n['body'].casefold()],
        search_scope='Only structured closeout comments in supplied closed-issue snapshots; no repository scan')


def trace(snapshots, start, max_hops=5):
    url(start)
    require(type(max_hops) is int and 0 <= max_hops <= 5, 'HOP_LIMIT', 'max_hops', 'Use zero to five durable hops')
    nodes = index_snapshots(snapshots)
    todo = [(start, 0)]
    visited = set(); found = []; unresolved = []; frontier = []; unresolved_shorthand = set()
    while todo:
        link, depth = todo.pop(0)
        if link in visited:
            continue
        visited.add(link)
        if link not in nodes:
            unresolved.append(link)
            continue
        node = nodes[link]
        found.append(dict(url=link, kind=node['kind'], hops=depth, links=node['links'],
                          unresolved_shorthand_refs=node['unresolved_shorthand_refs'], source=node['source']))
        unresolved_shorthand.update(node['unresolved_shorthand_refs'])
        if depth < max_hops:
            todo.extend((ref, depth + 1) for ref in node['links'])
        else:
            frontier.extend(ref for ref in node['links'] if ref not in visited)
    return envelope('warning' if unresolved or frontier or unresolved_shorthand else 'pass', nodes=found,
                    unresolved=sorted(set(unresolved)), hop_limit_frontier=sorted(set(frontier)),
                    unresolved_shorthand_refs=sorted(unresolved_shorthand),
                    trace_scope='Linked snapshot evidence only; unresolved shorthand is not guessed to be an issue or PR')


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
    config = load(Path(__file__).parent / 'examples/demo.json')
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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
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
    args = parser.parse_args(argv)
    try:
        if args.command == 'capture':
            snapshot = capture(args.repo, args.issue, args.pr)
            save_bundle(args.out, {'snapshot.json': snapshot})
            result = envelope(snapshot_source='gh_api', issue=snapshot['issue']['html_url'])
        elif args.command == 'demo':
            result = workflow_demo(args.out)
        elif args.command in ('search', 'trace'):
            snapshots = [load(path) for path in args.snapshot]
            result = search(snapshots, args.query) if args.command == 'search' else trace(snapshots, args.start, args.max_hops)
        elif args.command == 'packet':
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
        elif args.command == 'card-draft':
            snapshot = load(args.snapshot); packet = load(args.packet)
            metadata, body = card_draft(snapshot, packet, args.repo_root)
            save_bundle(args.out, {'CARD.md': body, 'CARD.json': metadata})
            result = envelope(issue=packet['issue'], packet_id=packet['packet_id'],
                              card_sha256=metadata['body_sha256'], output=str(Path(args.out).resolve()))
        else:
            snapshot = load(args.snapshot); packet = load(args.packet)
            if args.command == 'check':
                check_packet(snapshot, packet, args.repo_root)
                result = envelope(issue=packet['issue'], packet_id=packet['packet_id'])
            else:
                report = load(args.report)
                result, text = (handoff_draft(snapshot, packet, report, args.repo_root) if args.command == 'handoff'
                               else closeout_draft(snapshot, packet, report, args.repo_root, args.status))
                name = 'HANDOFF_DRAFT.md' if args.command == 'handoff' else 'CLOSEOUT_DRAFT.md'
                save_bundle(args.out, {name: text, 'observations.json': result})
        if not result['mechanically_checked']:
            result['mechanically_checked'] = {
                'capture': ['GET response shapes', 'repository/issue/PR identities', 'capture drift checks'],
                'packet': ['canonical issue fields', 'existing refinement engine', 'baseline context hashes', 'scope narrowing'],
                'check': ['current supplied issue/refinement', 'packet digest', 'issue/comment/PR-head consistency'],
                'card-draft': ['supplied snapshot shape, freshness and declared non-fixture source label', 'checked issue-backed packet',
                               'controller-supplied provenance and bounded card fields'],
                'search': ['supplied snapshot shape', 'closed-issue structured closeout without draft banner',
                           'case-insensitive query match'],
                'trace': ['supplied snapshot shape', 'durable URL links',
                          'closed-issue structured closeout edge', 'known-snapshot shorthand links',
                          'bounded traversal and unresolved references'],
                'demo': ['synthetic lifecycle fixture', 'local in-place git change', 'partial handoff', 'closeout/search/trace'],
            }.get(args.command, [])
        if args.command == 'capture':
            result['evidence_source'] = 'gh_api'
        elif args.command in ('packet', 'check', 'card-draft'):
            result['evidence_source'] = snapshot['source']
        elif args.command in ('search', 'trace'):
            result['evidence_source'] = 'supplied_snapshots'
        elif args.command == 'demo':
            result['evidence_source'] = 'fixture_and_local_git'
        if args.command == 'card-draft':
            result['not_checked'].append('actual origin or authenticity of the supplied snapshot')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result['result'] == 'blocked' else 0
    except Invalid as exc:
        result = envelope('fail'); result['findings'] = [exc.finding]
    except (OSError, ValueError, TypeError, KeyError, RecursionError, subprocess.SubprocessError) as exc:
        result = envelope('fail')
        result['findings'] = [dict(code='INPUT_IO', field='input/output', reason=str(exc), blocking=True)]
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1
