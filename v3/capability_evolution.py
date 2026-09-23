#!/usr/bin/env python3
"""Candidate metadata-only discovery for evidence-linked capability records.

This is a projection, never task authority or automatic skill promotion.
"""
import argparse
import json
import re
import sys

from asgk3 import Invalid, load, path_name, record, require, strings, words
from github_workflow import LINK

KINDS = {'lesson', 'ledger', 'proposal', 'workflow', 'policy', 'test', 'canon'}
STATES = {'observed', 'verified', 'promoted', 'rejected', 'superseded'}
ACTIVE = {'observed', 'verified', 'promoted'}
ID = re.compile(r'[a-z0-9][a-z0-9-]{0,79}\Z')
MAX_RESULTS = 20


def _link(value, field):
    require(type(value) is str and LINK.fullmatch(value), 'DURABLE_URL', field,
            'Expected a durable GitHub issue, PR, comment or commit URL')


def validate_index(index):
    """Validate metadata shape and local references, not evidence or content."""
    record(index, 'version records', 'index')
    require(type(index['version']) is int and index['version'] == 1,
            'INDEX_VERSION', 'version', 'Expected version 1')
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
        strings(item['evidence_refs'], field + '.evidence_refs', True)
        for link in item['evidence_refs']:
            _link(link, field + '.evidence_refs')
        path_name(item['content_ref'], field + '.content_ref')
        require(item['decision_ref'] is None or
                (type(item['decision_ref']) is str and LINK.fullmatch(item['decision_ref'])),
                'DECISION_REF', field + '.decision_ref', 'Expected durable GitHub decision URL or null')
        strings(item['supersedes'], field + '.supersedes')
        require(item['capability_version'] is None or
                (type(item['capability_version']) is str and bool(item['capability_version'].strip())),
                'CAPABILITY_VERSION', field + '.capability_version', 'Expected version string or null')
        if item['state'] == 'promoted':
            require(bool(item['decision_ref']) and bool(item['capability_version']),
                    'PROMOTION_PROVENANCE', field,
                    'Promoted record needs a reviewed decision link and capability version')
    for item in index['records']:
        require(item['id'] not in item['supersedes'] and
                all(ref in ids or LINK.fullmatch(ref) for ref in item['supersedes']),
                'SUPERSESSION_REF', item['id'],
                'Supersession must point to a local record ID or a durable cross-index GitHub link')
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
    return dict(result='pass' if candidates else 'incomplete', evidence_source='supplied_metadata_index',
                mechanically_checked=['index shape', 'local references', 'single-level tree projection'],
                not_checked=['record content', 'GitHub link existence', 'evidence quality', 'current task authority',
                             'semantic relevance', 'human approval'], human_gate={'status': 'not_checked'}, findings=[],
                proof_boundary='Tree branches and leaves are discovery hints, never instructions or approval.',
                domain=domain, branch=list(branch), children=shown_children, pointers=pointers,
                omitted=max(0, len(ordered) + len(direct) - shown))


def select(index, domain, query, limit=8, branch=()):
    """Return bounded metadata pointers, never lesson bodies or inferred authority."""
    validate_index(index)
    require(type(domain) is str and ID.fullmatch(domain), 'QUERY_DOMAIN', 'domain', 'Name one domain')
    _branch(branch)
    words(query, 'query')
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
    return dict(result='pass' if pointers else 'incomplete', evidence_source='supplied_metadata_index',
                mechanically_checked=['index shape', 'local references', 'bounded domain/query selection'],
                not_checked=['record content', 'GitHub link existence', 'evidence quality', 'current task authority',
                             'semantic relevance', 'human approval'], human_gate={'status': 'not_checked'}, findings=[],
                proof_boundary='Metadata pointers are discovery hints; only live issue/PR and reviewed skill versions govern action.',
                domain=domain, branch=list(branch), query=query, total_matches=len(ranked), omitted=max(0, len(ranked) - len(pointers)),
                pointers=pointers)


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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    check = sub.add_parser('check', help='Validate index shape and local references only')
    check.add_argument('--index', required=True)
    choose = sub.add_parser('select', help='Retrieve bounded metadata for one domain')
    choose.add_argument('--index', required=True)
    choose.add_argument('--domain', required=True)
    choose.add_argument('--query', required=True)
    choose.add_argument('--limit', type=int, default=8)
    choose.add_argument('--branch', action='append', default=[])
    tree = sub.add_parser('browse', help='Reveal one branch level and bounded direct leaves')
    tree.add_argument('--index', required=True)
    tree.add_argument('--domain', required=True)
    tree.add_argument('--branch', action='append', default=[])
    tree.add_argument('--limit', type=int, default=8)
    args = parser.parse_args(argv)
    try:
        index = load(args.index)
        if args.command == 'check':
            validate_index(index)
            result = dict(result='pass', evidence_source='supplied_metadata_index',
                          human_gate={'status': 'not_checked'}, findings=[], count=len(index['records']),
                          mechanically_checked=['index shape', 'local references'],
                          not_checked=['record content', 'GitHub link existence', 'evidence quality',
                                       'task authority', 'promotion approval'],
                          proof_boundary='Structural validation only; this index is not an authority ledger.')
        elif args.command == 'select':
            result = select(index, args.domain, args.query, args.limit, args.branch)
        else:
            result = browse(index, args.domain, args.branch, args.limit)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['result'] == 'pass' else 2
    except (Invalid, OSError, ValueError, TypeError, KeyError) as error:
        finding = error.finding if isinstance(error, Invalid) else dict(
            code='INPUT_IO', field='index', reason=str(error), blocking=True)
        print(json.dumps(dict(result='fail', evidence_source='supplied_metadata_index',
                              mechanically_checked=['input shape up to the reported failure'],
                              not_checked=['record content', 'GitHub link existence', 'evidence quality',
                                           'task authority', 'promotion approval'],
                              human_gate={'status': 'not_checked'},
                              proof_boundary='Index validation failed; no records were authorized or promoted.',
                              findings=[finding]), ensure_ascii=False, indent=2))
        return 1


if __name__ == '__main__':
    sys.exit(main())
