#!/usr/bin/env python3
"""Optional metadata-only discovery for reusable capability records.

This is not a delivery question graph, task authority or automatic skill promotion.
"""
import argparse
import json
import re
import sys

from asgk_lib.workflow_common import Invalid, load, path_name, record, require, strings, words
from asgk_lib.github_workflow import LINK
from asgk_lib.validation_result import human_gate

KINDS = {'lesson', 'ledger', 'proposal', 'workflow', 'policy', 'test', 'canon'}
STATES = {'observed', 'verified', 'promoted', 'rejected', 'superseded'}
ACTIVE = {'observed', 'verified', 'promoted'}
ID = re.compile(r'[a-z0-9][a-z0-9-]{0,79}\Z')
MAX_RESULTS = 20
MAX_INDEX_DEPTH = 64
PROOF = ('Catalog text matches, including negative applicability phrases, are bounded discovery hints, '
         'not applicability recommendations or a delivery question graph, instructions, task authority, '
         'Skill promotion or approval.')
NOT_CHECKED = ['content_ref file existence', 'record content', 'GitHub link existence',
               'evidence quality', 'current task authority', 'delivery question graph',
               'per-work question completion', 'semantic relevance', 'independent review',
               'Skill promotion', 'human approval']


def envelope(result='pass', checked=None, **extra):
    return dict(result=result, projection='capability_catalog',
                evidence_source='supplied_metadata_index',
                mechanically_checked=checked or ['index shape and reference syntax'],
                not_checked=NOT_CHECKED.copy(), human_gate=human_gate(),
                findings=[], proof_boundary=PROOF, **extra)


def finish_projection(result, field):
    if result['domain_result'] == 'incomplete':
        code = 'CATALOG_NO_MATCH'
        reason = 'No active metadata pointer matched the supplied domain, branch or query.'
    elif result['omitted']:
        code = 'CATALOG_RESULTS_OMITTED'
        reason = 'The limit omitted matching metadata pointers or branches; narrow the query or branch.'
    else:
        return result
    result['result'] = 'warning'
    result['domain_result'] = 'incomplete'
    result['findings'] = [dict(code=code, field=field, reason=reason, blocking=False)]
    return result


def _link(value, field):
    require(type(value) is str and len(value) <= 512 and LINK.fullmatch(value), 'DURABLE_URL', field,
            'Expected a durable GitHub issue, PR, comment or commit URL')


def validate_index(index):
    """Validate metadata shape and reference syntax, not file existence or content."""
    pending = [(index, 0)]
    while pending:
        value, depth = pending.pop()
        require(depth <= MAX_INDEX_DEPTH, 'INDEX_DEPTH', 'index',
                'Index JSON nesting exceeds the supported depth.')
        if type(value) is dict:
            pending.extend((child, depth + 1) for child in value.values())
        elif type(value) is list:
            pending.extend((child, depth + 1) for child in value)
    record(index, 'version purpose records', 'index')
    require(type(index['version']) is int and index['version'] == 1,
            'INDEX_VERSION', 'version', 'Expected version 1')
    require(index['purpose'] == 'capability_catalog', 'INDEX_PURPOSE', 'purpose',
            'Expected a capability catalog, not a delivery question graph')
    require(type(index['records']) is list, 'INDEX_SHAPE', 'records', 'Expected list')
    ids = set()
    for number, item in enumerate(index['records']):
        field = f'records[{number}]'
        record(item, 'id kind domain tree_path state title summary tags applies_when does_not_apply_when '
               'source_ref evidence_refs content_ref decision_ref supersedes capability_version', field)
        require(type(item['id']) is str and ID.fullmatch(item['id']), 'RECORD_ID', field + '.id',
                'Expected stable lowercase hyphenated ID')
        require(item['id'] not in ids, 'DUPLICATE_ID', field + '.id', 'Duplicate record ID')
        ids.add(item['id'])
        require(type(item['kind']) is str and item['kind'] in KINDS,
                'RECORD_KIND', field + '.kind', 'Unknown kind')
        require(type(item['state']) is str and item['state'] in STATES,
                'RECORD_STATE', field + '.state', 'Unknown state')
        require(type(item['domain']) is str and ID.fullmatch(item['domain']),
                'RECORD_DOMAIN', field + '.domain', 'Expected domain slug')
        strings(item['tree_path'], field + '.tree_path', True)
        require(len(item['tree_path']) <= 6 and all(ID.fullmatch(part) for part in item['tree_path']),
                'TREE_PATH', field + '.tree_path', 'Expected one to six topic-branch slugs')
        for name in ('title', 'summary', 'applies_when', 'does_not_apply_when'):
            words(item[name], field + '.' + name)
        require(len(item['title']) <= 120 and len(item['summary']) <= 320,
                'METADATA_LENGTH', field, 'Title/summary must remain a small discovery surface')
        strings(item['tags'], field + '.tags', True)
        require(all(ID.fullmatch(tag) for tag in item['tags']),
                'RECORD_TAG', field + '.tags', 'Expected slug tags')
        _link(item['source_ref'], field + '.source_ref')
        strings(item['evidence_refs'], field + '.evidence_refs')
        for link in item['evidence_refs']:
            _link(link, field + '.evidence_refs')
        path_name(item['content_ref'], field + '.content_ref')
        require(len(item['content_ref']) <= 256, 'METADATA_LENGTH', field + '.content_ref',
                'Content pointer must be at most 256 characters')
        require(item['decision_ref'] is None or
                (type(item['decision_ref']) is str and len(item['decision_ref']) <= 512
                 and LINK.fullmatch(item['decision_ref'])),
                'DECISION_REF', field + '.decision_ref', 'Expected durable GitHub decision URL or null')
        strings(item['supersedes'], field + '.supersedes')
        require(item['capability_version'] is None or
                (type(item['capability_version']) is str and bool(item['capability_version'].strip())
                 and len(item['capability_version']) <= 64),
                'CAPABILITY_VERSION', field + '.capability_version', 'Expected version string or null')
        if item['state'] in {'observed', 'verified'}:
            require(item['capability_version'] is None, 'STATE_PROVENANCE', field + '.capability_version',
                    'Observed or verified metadata cannot claim a promoted capability version')
        if item['state'] == 'promoted':
            require(bool(item['decision_ref']) and bool(item['capability_version']),
                    'PROMOTION_PROVENANCE', field,
                    'Promoted record needs a reviewed decision link and capability version')
        if item['state'] in {'verified', 'promoted'}:
            require(bool(item['evidence_refs']), 'EVIDENCE_PROVENANCE', field + '.evidence_refs',
                    'Verified or promoted records need at least one evidence pointer')
    for number, item in enumerate(index['records']):
        require(item['id'] not in item['supersedes'] and
                all(ref in ids or LINK.fullmatch(ref) for ref in item['supersedes']),
                'SUPERSESSION_REF', f'records[{number}].supersedes',
                'Supersession must point to a local record ID or a durable cross-index GitHub link')
    by_id = {item['id']: item for item in index['records']}
    for number, item in enumerate(index['records']):
        if item['state'] in ACTIVE:
            for ref in item['supersedes']:
                require(ref not in by_id or by_id[ref]['state'] not in ACTIVE,
                        'ACTIVE_SUPERSESSION', f'records[{number}].supersedes',
                        'An active record cannot supersede another still-active local record')
    return index


def _pointer(item):
    return dict(id=item['id'], kind=item['kind'], state=item['state'],
                title=item['title'], summary=item['summary'], tree_path=item['tree_path'],
                content_ref=item['content_ref'], source_ref=item['source_ref'],
                decision_ref=item['decision_ref'], capability_version=item['capability_version'])


def _branch(branch):
    require(type(branch) in (list, tuple) and len(branch) <= 6
            and all(type(part) is str and ID.fullmatch(part) for part in branch),
            'QUERY_BRANCH', 'branch', 'Expected up to six topic-branch slugs')


def browse(index, domain, branch=(), limit=8):
    """Reveal one tree level, with bounded direct leaves; do not read leaf bodies."""
    validate_index(index)
    require(type(domain) is str and ID.fullmatch(domain), 'QUERY_DOMAIN', 'domain', 'Name one domain')
    _branch(branch)
    require(type(limit) is int and 1 <= limit <= MAX_RESULTS,
            'RESULT_LIMIT', 'limit', 'Select one to twenty metadata pointers')
    candidates = [item for item in index['records'] if item['domain'] == domain
                  and item['state'] in ACTIVE and item['tree_path'][:len(branch)] == list(branch)]
    children = {}
    direct = []
    for item in candidates:
        if len(item['tree_path']) > len(branch):
            part = item['tree_path'][len(branch)]
            children[part] = children.get(part, 0) + 1
        else:
            direct.append(item)
    ordered = sorted(children.items())
    shown_children = [dict(branch=list(branch) + [name], record_count=count)
                      for name, count in ordered[:limit]]
    slots = limit - len(shown_children)
    pointers = [_pointer(item) for item in sorted(direct, key=lambda x: x['id'])[:slots]]
    shown = len(shown_children) + len(pointers)
    return finish_projection(envelope(checked=['index shape', 'reference syntax', 'single-level tree projection'],
                             domain_result='matched' if candidates else 'incomplete',
                             domain=domain, branch=list(branch), children=shown_children, pointers=pointers,
                             omitted=max(0, len(ordered) + len(direct) - shown)), 'branch')


def select(index, domain, query, limit=8, branch=()):
    """Return bounded metadata pointers, never lesson bodies or inferred authority."""
    validate_index(index)
    require(type(domain) is str and ID.fullmatch(domain), 'QUERY_DOMAIN', 'domain', 'Name one domain')
    _branch(branch)
    words(query, 'query')
    require(len(query) <= 320, 'QUERY_LENGTH', 'query', 'Query must be at most 320 characters')
    require(type(limit) is int and 1 <= limit <= MAX_RESULTS,
            'RESULT_LIMIT', 'limit', 'Select one to twenty metadata pointers')
    terms = [word.casefold() for word in re.findall(r'[\w-]+', query, re.UNICODE)]
    require(bool(terms), 'QUERY', 'query', 'Expected searchable words')
    ranked = []
    for item in index['records']:
        if (item['domain'] != domain or item['state'] not in ACTIVE
                or item['tree_path'][:len(branch)] != list(branch)):
            continue
        haystack = ' '.join(str(item[key]) for key in
                            ('title', 'summary', 'tags', 'applies_when', 'does_not_apply_when')).casefold()
        score = sum(haystack.count(term) for term in terms)
        if score:
            ranked.append((score, item))
    ranked.sort(key=lambda pair: (-pair[0], pair[1]['id']))
    pointers = [_pointer(item) for _, item in ranked[:limit]]
    return finish_projection(envelope(checked=['index shape', 'reference syntax', 'bounded domain/query selection'],
                             domain_result='matched' if pointers else 'incomplete',
                             domain=domain, branch=list(branch), query=query, total_matches=len(ranked),
                             omitted=max(0, len(ranked) - len(pointers)), pointers=pointers), 'query')


def review_separation(author_id, reviewer_id):
    """Reject obvious self-review without claiming identities were authenticated."""
    words(author_id, 'author_id')
    words(reviewer_id, 'reviewer_id')
    same = author_id == reviewer_id
    return dict(result='blocked' if same else 'warning',
                mechanically_checked=['supplied actor ID equality'],
                not_checked=['actor identity', 'review content', 'head binding', 'human approval'],
                finding='same_actor_self_review' if same else 'different_labels_not_independence_proof',
                proof_boundary='Different supplied IDs are not proof of independent review; verify the live GitHub actors and current head.')


def add_parser(sub):
    catalog = sub.add_parser('catalog', help='Inspect an explicit capability metadata index.')
    catalog_sub = catalog.add_subparsers(dest='catalog_command', required=True)
    check = catalog_sub.add_parser('check', help='Validate index shape and reference syntax only')
    check.add_argument('--index', required=True)
    choose = catalog_sub.add_parser('select', help='Retrieve bounded metadata for one domain')
    choose.add_argument('--index', required=True)
    choose.add_argument('--domain', required=True)
    choose.add_argument('--query', required=True)
    choose.add_argument('--limit', type=int, default=8)
    choose.add_argument('--branch', action='append', default=[])
    tree = catalog_sub.add_parser('browse', help='Reveal one branch level and bounded direct leaves')
    tree.add_argument('--index', required=True)
    tree.add_argument('--domain', required=True)
    tree.add_argument('--branch', action='append', default=[])
    tree.add_argument('--limit', type=int, default=8)
    for command in (check, choose, tree):
        command.add_argument('--json', action='store_true', help='Emit the common JSON evidence envelope.')
        command.set_defaults(func=run)
    return catalog


def run(args):
    try:
        index = load(args.index)
        if args.catalog_command == 'check':
            validate_index(index)
            result = envelope(checked=['index shape', 'reference syntax'], count=len(index['records']))
        elif args.catalog_command == 'select':
            result = select(index, args.domain, args.query, args.limit, args.branch)
        else:
            result = browse(index, args.domain, args.branch, args.limit)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['result'] == 'pass' else 1
    except RecursionError:
        result = envelope(result='fail', checked=['index JSON parser depth limit'])
        result['findings'] = [dict(
            code='INDEX_DEPTH', field='index',
            reason='Index JSON nesting exceeds the supported parser depth.', blocking=True)]
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1
    except (Invalid, OSError, ValueError, TypeError, KeyError) as error:
        finding = error.finding if isinstance(error, Invalid) else dict(
            code='INPUT_IO', field='index', reason=str(error), blocking=True)
        result = envelope(result='fail', checked=['input shape up to the reported failure'])
        result['findings'] = [finding]
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    add_parser(sub)
    args = parser.parse_args(['catalog', *(argv if argv is not None else sys.argv[1:])])
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
