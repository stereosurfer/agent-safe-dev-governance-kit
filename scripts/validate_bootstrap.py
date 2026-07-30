#!/usr/bin/env python3
"""Validate bootstrap governance scaffold.

Dependency-light by design: no PyYAML/jsonschema required. This catches common
AI-over-simplification failures: missing files, missing required sections,
missing durable source fields, thin templates, invalid JSON, and storage-boundary
regressions.
"""
from __future__ import annotations
import contextlib, io, json, re, subprocess, sys, tempfile
from pathlib import Path

from asgk_lib.common import (
    field_block_lines,
    markdown_heading_occurrences,
    markdown_section,
)
from asgk_lib.negative_runner import run_expected_failures
from policy_gate_check import (
    MERGE_DECISION_REQUIRED_FIELDS,
    PR_REQUIRED_HEADINGS,
    line_field_count,
)

REQUIRED_FILES = [
 'README.md','AGENTS.md',
 'docs/bootstrap/00_project_brief.md','docs/bootstrap/01_physical_boundaries.md','docs/bootstrap/02_storage_roots.md','docs/bootstrap/03_tech_stack.md','docs/bootstrap/04_file_structure.md','docs/bootstrap/05_context_budget.md','docs/bootstrap/06_naming_versioning.md','docs/bootstrap/07_contract_first.md','docs/bootstrap/08_acceptance_criteria.md','docs/bootstrap/09_safety_checks.md','docs/bootstrap/10_roadmap.md','docs/bootstrap/11_auto_merge_policy.md','docs/bootstrap/12_productization_notes.md','docs/bootstrap/13_artifact_promotion_policy.md','docs/bootstrap/14_execution_lanes.md','docs/bootstrap/15_source_or_input_class_matrix.md','docs/bootstrap/16_downstream_promotion_matrix.md','docs/bootstrap/17_readiness_audit_policy.md',
 'docs/architecture/BOUNDARY_SPLIT.md','docs/architecture/EXTERNALIZED_RESPONSIBILITY_BOUNDARY.md','docs/architecture/STORAGE_PROFILE.md','docs/architecture/WORKSPACE_LOCK_POLICY.md','docs/architecture/CACHE_AND_STATE_POLICY.md','docs/architecture/RUNTIME_ARTIFACT_POLICY.md',
 'docs/control/CONTROL_LAYER_V0.md','docs/control/WORK_UNIT_STATE_MODEL.md','docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md','docs/control/HUMAN_GATED_OPERATIONS.md','docs/control/ISSUE_HYGIENE_GATE.md','docs/control/TASK_PACKET_FORMAT.md','docs/control/AGENT_REPORT_FORMAT.md','docs/control/MERGE_DECISION_RECORD.md','docs/control/FAILURE_THRESHOLDS.md','docs/control/PHASE_0_ACCEPTANCE_CHECKLIST.md',
 'docs/handoff/CURRENT_STATUS.md','docs/handoff/DECISIONS.md','docs/handoff/AGENT_LOG.md',
 'templates/task_packet.template.yaml',
 'contracts/storage_profile.contract.yaml','contracts/artifact_contract.yaml','contracts/validation_result.contract.yaml','contracts/promotion_gate.contract.yaml','contracts/execution_lane.contract.yaml',
 'schemas/validation_result.schema.json','schemas/storage_profile.schema.json','schemas/task_packet.schema.json','schemas/merge_decision.schema.json','schemas/promotion_gate.schema.json','schemas/execution_lane.schema.json','schemas/agent_report.schema.json',
 'scripts/check_project.py','scripts/validate_bootstrap.py','scripts/governance_hygiene.py',
 '.github/ISSUE_TEMPLATE/agent_task.yml','.github/ISSUE_TEMPLATE/workbench_task.md','.github/PULL_REQUEST_TEMPLATE.md','.github/workflows/bootstrap-validation.yml',
 'examples/storage_profile.local.json','examples/task_packet.example.yaml','examples/merge_decision.example.json','examples/promotion_gate.example.json','examples/execution_lane.example.json','examples/agent_report.example.md',
 'examples/pr_body.merge-blocked-draft.valid.md','examples/pr_status.valid.json','examples/pr_status.ready-blocked.json','examples/pr_status.duplicate-check-latest-success.json',
 'examples/github_events/pr.draft-blocked.json','examples/github_events/pr.ready-blocked.json','examples/github_events/pr.ready-allowed.json',
 'examples/negative/github_events/pr.missing-result.json','examples/negative/github_events/pr.missing-pull-request.json',
 'examples/negative/policy_gate/pr_body.checks-pending.md','examples/negative/policy_gate/pr_body.human-gates-pending.md',
 'examples/negative/policy_gate/pr_body.checks-false.md','examples/negative/policy_gate/pr_body.human-gates-false.md',
 'examples/negative/policy_gate/pr_body.blank-state.md','examples/negative/policy_gate/pr_body.unknown-state.md',
 'examples/negative/policy_gate/pr_body.generic-reason.md','examples/negative/policy_gate/pr_body.duplicate-state.md','examples/negative/policy_gate/pr_body.invalid-validation-source-shape.md',
 'examples/negative/pr_status.merge-blocked-all-clean.json','examples/negative/pr_status.duplicate-check-latest-failure.json','examples/negative/pr_status.duplicate-check-ambiguous.json','examples/negative/pr_status.missing-check-identity.json','examples/negative/pr_status.duplicate-check-missing-provider.json'
]

REQUIRED_TERMS = {
 'AGENTS.md':['see chat','Issue Hygiene Gate','Stop conditions','Low-risk merge boundary'],
 'docs/bootstrap/01_physical_boundaries.md':['writable_paths','protected_paths','forbidden_actions','Artifact Root','Local State Root'],
 'docs/bootstrap/02_storage_roots.md':['code_repo','artifact_root','local_state_root','app_managed_drive_api','local_only'],
 'docs/bootstrap/11_auto_merge_policy.md':['auto_merge_allowed_when','auto_merge_forbidden_when','Merge Decision Record','durable source of truth'],
 'docs/bootstrap/13_artifact_promotion_policy.md':['Traceability is required, but traceability alone is not enough','blocked_thin_context','blocked_class_use_mismatch'],
 'docs/bootstrap/14_execution_lanes.md':['deterministic','codex_operated','api_provider','requires_allow_live_call_flag'],
 'docs/control/CONTROL_LAYER_V0.md':['Durable Control Surfaces','Work Unit State Model','Task Packet Format','Agent Report Format','Anti-drift Rules','Human Gates','Definition of Done'],
 'docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md':['Necessary operations allowed','Prohibited without human approval','Low-risk merge gates','After merge'],
 'docs/architecture/EXTERNALIZED_RESPONSIBILITY_BOUNDARY.md':['External Preparation App','Closed gates','raw PDF ingestion','OCR','prepared input'],
}

CONTROL_REQUIRED_SECTIONS = ['Purpose','Durable Control Surfaces','Work Unit State Model','Task Packet Format','Agent Report Format','Operating Loop','Anti-drift Rules','Human Gates','Definition of Done']
TASK_PACKET_FIELDS = ['task_id','lane','intelligence_level','durable_source_of_truth','objective','allowed_paths','expected_output','plan','checklist','acceptance_sheet','stop_conditions','rollback_expectations']
ISSUE_FIELDS = ['objective','durable_source_of_truth','lane','intelligence_level','allowed_paths','expected_output','acceptance_sheet','stop_conditions']
MERGE_DECISION_ALWAYS_TRUE_FIELDS = [
    'allowed_paths_checked','expected_output_checked','validation_evidence_checked',
]
PR_LIFECYCLE_EVENTS = [
    'opened','synchronize','reopened','edited','ready_for_review','converted_to_draft',
]

def fail(msg):
    print(f'FAIL: {msg}')
    sys.exit(1)

def read(root, path):
    return (root/path).read_text(encoding='utf-8')

def check_terms(root):
    for path, terms in REQUIRED_TERMS.items():
        text = read(root, path)
        for term in terms:
            if term not in text:
                fail(f'{path} missing required term: {term}')

def check_json(root):
    json_paths = sorted((root/'schemas').rglob('*.json')) + sorted((root/'examples').rglob('*.json'))
    for p in json_paths:
        try:
            json.loads(p.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            fail(f'{p.relative_to(root)} invalid JSON: {e}')

def check_yaml_like_fields(root):
    packet = read(root,'templates/task_packet.template.yaml')
    for field in TASK_PACKET_FIELDS:
        if not re.search(rf'^{re.escape(field)}\s*:', packet, re.M):
            fail(f'templates/task_packet.template.yaml missing field: {field}')

def check_templates(root):
    pr = read(root,'.github/PULL_REQUEST_TEMPLATE.md')
    headings = markdown_heading_occurrences(pr)
    for h in PR_REQUIRED_HEADINGS:
        if headings.count(h) != 1:
            fail(f'PR template must contain exactly one visible heading: {h}')
    merge_section = markdown_section(pr, 'Merge Decision')
    if not merge_section:
        fail('PR template missing visible Merge Decision section')
    for field in MERGE_DECISION_REQUIRED_FIELDS:
        if line_field_count(merge_section, field) != 1:
            fail(f'PR template must contain exactly one Merge Decision field: {field}')
    validation_source_lines = field_block_lines(
        merge_section,
        'validation_claim_source',
    ) or []
    validation_source = '\n'.join(validation_source_lines)
    material_source_lines = [
        line
        for line in validation_source_lines
        if line.strip() and not line.lstrip().startswith('#')
    ]
    if len(material_source_lines) != 2:
        fail('PR template validation_claim_source must contain exactly two child fields')
    child_indents = {
        len(re.match(r'^[ \t]*', line).group(0).replace('\t', '    '))
        for line in material_source_lines
    }
    if len(child_indents) != 1:
        fail('PR template validation_claim_source child fields must share one indentation')
    for field in ['local_doctor', 'ci']:
        if line_field_count(validation_source, field) != 1:
            fail(f'PR template must contain exactly one validation_claim_source.{field}')
    for term in [
        'body-level decision state',
        'merge_blocked',
        'merge_allowed',
        'current-head',
        'decision: approved',
    ]:
        if term not in pr:
            fail(f'PR template missing lifecycle term: {term}')
    if not re.search(r'no\s+human gate applies', pr):
        fail('PR template missing no-human-gate determination path')
    issue = read(root,'.github/ISSUE_TEMPLATE/agent_task.yml')
    for field in ISSUE_FIELDS:
        if field not in issue:
            fail(f'agent_task.yml missing field/token: {field}')

def check_merge_decision_projection(root):
    schema = json.loads(read(root,'schemas/merge_decision.schema.json'))
    example = json.loads(read(root,'examples/merge_decision.example.json'))

    required = set(schema.get('required', []))
    missing_schema_fields = [field for field in MERGE_DECISION_REQUIRED_FIELDS if field not in required]
    if missing_schema_fields:
        fail(f'merge_decision.schema.json missing required fields: {", ".join(missing_schema_fields)}')

    missing_example_fields = [field for field in MERGE_DECISION_REQUIRED_FIELDS if field not in example]
    if missing_example_fields:
        fail(f'merge_decision.example.json missing fields: {", ".join(missing_example_fields)}')

    properties = schema.get('properties', {})
    result_values = properties.get('result', {}).get('enum', [])
    if result_values != ['merge_allowed', 'merge_blocked']:
        fail('merge_decision.schema.json result enum must be merge_allowed, merge_blocked')

    for field in MERGE_DECISION_ALWAYS_TRUE_FIELDS:
        if properties.get(field, {}).get('const') is not True:
            fail(f'merge_decision.schema.json must require {field} to be exactly true')
        if example.get(field) is not True:
            fail(f'merge_decision.example.json must set {field} to true')

    boundary_options = (
        schema.get('$defs', {})
        .get('concrete_boundary_value', {})
        .get('oneOf', [])
    )
    if not any(option.get('const') is True for option in boundary_options):
        fail('merge_decision.schema.json concrete boundary values must permit exact true')
    if any(option.get('type') == 'boolean' for option in boundary_options):
        fail('merge_decision.schema.json concrete boundary values must not permit false')

    concrete_string = schema.get('$defs', {}).get('concrete_string', {})
    material_pattern = concrete_string.get('pattern')
    placeholder_pattern = concrete_string.get('not', {}).get('pattern')
    if not material_pattern or not placeholder_pattern:
        fail('merge_decision.schema.json concrete strings must reject whitespace and placeholder states')

    def concrete_string_accepts(value):
        return bool(
            re.search(material_pattern, value)
            and not re.search(placeholder_pattern, value)
        )

    for invalid in [' ', 'pending', ' FALSE ', 'unknown', 'todo']:
        if concrete_string_accepts(invalid):
            fail(f'merge_decision.schema.json concrete string accepts placeholder: {invalid!r}')
    if not concrete_string_accepts('named durable evidence'):
        fail('merge_decision.schema.json concrete string rejects material evidence')

    reason_schema = schema.get('$defs', {}).get('reason_string', {})
    reason_parts = reason_schema.get('allOf', [])
    generic_reason_pattern = next(
        (
            part.get('not', {}).get('pattern')
            for part in reason_parts
            if part.get('not', {}).get('pattern')
        ),
        None,
    )
    if not generic_reason_pattern:
        fail('merge_decision.schema.json reason must reject generic decision text')
    for invalid in ['passed', 'n/a', 'all good', 'merge_allowed']:
        if not re.search(generic_reason_pattern, invalid):
            fail(f'merge_decision.schema.json reason pattern misses generic value: {invalid}')
    if properties.get('reason', {}).get('$ref') != '#/$defs/reason_string':
        fail('merge_decision.schema.json reason must use reason_string')

    declared_gate_state = (
        schema.get('$defs', {})
        .get('declared_gate_state', {})
        .get('enum', [])
    )
    if declared_gate_state != [True, False, 'pending']:
        fail('merge_decision.schema.json declared gate state must be true, false, pending')

    validation_source = properties.get('validation_claim_source', {})
    if set(validation_source.get('required', [])) != {'local_doctor', 'ci'}:
        fail('merge_decision.schema.json validation claim source must require local_doctor and ci')
    expected_source_values = {
        'local_doctor': {
            'freshly_rerun','recorded_in_pr_body','existing_durable_record',
            'not_run','not_applicable',
        },
        'ci': {'github_actions','external_ci','not_run','not_applicable'},
    }
    for field, expected_values in expected_source_values.items():
        actual_values = set(
            validation_source.get('properties', {})
            .get(field, {})
            .get('enum', [])
        )
        if actual_values != expected_values:
            fail(f'merge_decision.schema.json validation_claim_source.{field} enum drifted')

    allowed_condition = next(
        (
            item
            for item in schema.get('allOf', [])
            if item.get('if', {}).get('properties', {}).get('result', {}).get('const')
            == 'merge_allowed'
        ),
        None,
    )
    if allowed_condition is None:
        fail('merge_decision.schema.json missing merge_allowed conditional')
    allowed_properties = allowed_condition.get('then', {}).get('properties', {})
    for field in ['checks_passed','human_gates_checked','validation_evidence_checked']:
        if allowed_properties.get(field, {}).get('const') is not True:
            fail(f'merge_decision.schema.json merge_allowed must require {field}: true')

    if example.get('result') != 'merge_allowed':
        fail('merge_decision.example.json must demonstrate merge_allowed')
    for field in ['checks_passed','human_gates_checked']:
        if example.get(field) is not True:
            fail(f'merge_decision.example.json merge_allowed requires {field}: true')

def check_pr_workflow_projection(root):
    workflow = read(root,'.github/workflows/bootstrap-validation.yml')
    for event in PR_LIFECYCLE_EVENTS:
        if not re.search(rf'^\s+-\s+{re.escape(event)}\s*$', workflow, re.M):
            fail(f'bootstrap-validation.yml missing pull_request activity: {event}')
    if 'policy-gate --github-event "$GITHUB_EVENT_PATH"' not in workflow:
        fail('bootstrap-validation.yml must route PR policy gate from the declared event result')
    forbidden_auto_flag = '--mode' + ' auto'
    if forbidden_auto_flag in workflow:
        fail('bootstrap-validation.yml must not introduce a third automatic proof mode')

def run_json_command(root, args, *, expected_returncode):
    result = subprocess.run(
        [sys.executable, *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != expected_returncode:
        detail = result.stdout.strip() or result.stderr.strip() or 'no output'
        fail(f'command returned {result.returncode}, expected {expected_returncode}: {" ".join(args)}: {detail}')
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        fail(f'command did not emit JSON: {" ".join(args)}: {error}')

def run_json_payload_command(root, args, payload, *, expected_returncode):
    with tempfile.TemporaryDirectory() as tmpdir:
        payload_path = Path(tmpdir) / 'payload.json'
        payload_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding='utf-8',
        )
        resolved = [
            str(payload_path) if arg == '{payload}' else arg
            for arg in args
        ]
        return run_json_command(
            root,
            resolved,
            expected_returncode=expected_returncode,
        )

def check_policy_gate_routing_fixtures(root):
    positive_cases = {
        'examples/github_events/pr.draft-blocked.json': 'body-coherence',
        'examples/github_events/pr.ready-blocked.json': 'body-coherence',
        'examples/github_events/pr.ready-allowed.json': 'merge-decision',
    }
    for fixture, expected_mode in positive_cases.items():
        payload = run_json_command(
            root,
            ['scripts/asgk.py','policy-gate','--github-event',fixture,'--json'],
            expected_returncode=0,
        )
        if payload.get('mode') != expected_mode:
            fail(f'{fixture} routed to {payload.get("mode")}, expected {expected_mode}')

    for fixture in [
        'examples/negative/github_events/pr.missing-result.json',
        'examples/negative/github_events/pr.missing-pull-request.json',
    ]:
        payload = run_json_command(
            root,
            ['scripts/asgk.py','policy-gate','--github-event',fixture,'--json'],
            expected_returncode=1,
        )
        if payload.get('routing') != 'fail_closed' or 'mode' in payload:
            fail(f'{fixture} must fail routing before selecting a proof mode')

    override = run_json_command(
        root,
        [
            'scripts/asgk.py','policy-gate',
            '--github-event','examples/github_events/pr.ready-allowed.json',
            '--mode','body-coherence','--json',
        ],
        expected_returncode=1,
    )
    if override.get('routing') != 'fail_closed':
        fail('GitHub event mode override must fail closed')

    quoted_result_event = json.loads(
        read(root, 'examples/github_events/pr.ready-allowed.json')
    )
    quoted_result_event['pull_request']['body'] = (
        quoted_result_event['pull_request']['body']
        .replace('  result: merge_allowed', '  result: "merge_allowed"')
    )
    quoted_result = run_json_payload_command(
        root,
        [
            'scripts/asgk.py','policy-gate',
            '--github-event','{payload}','--json',
        ],
        quoted_result_event,
        expected_returncode=1,
    )
    if quoted_result.get('routing') != 'fail_closed' or 'mode' in quoted_result:
        fail('quoted Merge Decision result must fail before GitHub event mode selection')

    uppercase_result_event = json.loads(
        read(root, 'examples/github_events/pr.ready-allowed.json')
    )
    uppercase_result_event['pull_request']['body'] = (
        uppercase_result_event['pull_request']['body']
        .replace('  result: merge_allowed', '  result: MERGE_ALLOWED')
    )
    uppercase_result = run_json_payload_command(
        root,
        [
            'scripts/asgk.py','policy-gate',
            '--github-event','{payload}','--json',
        ],
        uppercase_result_event,
        expected_returncode=1,
    )
    if uppercase_result.get('routing') != 'fail_closed' or 'mode' in uppercase_result:
        fail('noncanonical Merge Decision result case must fail before mode selection')

def check_policy_gate_failure_projection(root):
    expected_fields = {
        'examples/negative/policy_gate/pr_body.checks-pending.md': {'checks_passed'},
        'examples/negative/policy_gate/pr_body.human-gates-pending.md': {'human_gates_checked'},
        'examples/negative/policy_gate/pr_body.checks-false.md': {'checks_passed'},
        'examples/negative/policy_gate/pr_body.human-gates-false.md': {'human_gates_checked'},
        'examples/negative/policy_gate/pr_body.blank-state.md': {'checks_passed'},
        'examples/negative/policy_gate/pr_body.unknown-state.md': {'human_gates_checked'},
        'examples/negative/policy_gate/pr_body.generic-reason.md': {'reason'},
        'examples/negative/policy_gate/pr_body.duplicate-state.md': {'result'},
        'examples/negative/policy_gate/pr_body.invalid-validation-source-shape.md': {'validation_claim_source'},
    }
    for fixture, expected in expected_fields.items():
        for mode in ['body-coherence', 'merge-decision']:
            payload = run_json_command(
                root,
                [
                    'scripts/asgk.py','policy-gate','--pr-body',fixture,
                    '--mode',mode,'--json',
                ],
                expected_returncode=1,
            )
            actual = {
                finding.get('field')
                for finding in payload.get('findings', [])
            }
            if actual != expected:
                fail(f'{fixture} {mode} findings {sorted(actual)} != {sorted(expected)}')

    blocked = run_json_command(
        root,
        [
            'scripts/asgk.py','policy-gate',
            '--pr-body','examples/pr_body.merge-blocked-draft.valid.md',
            '--json',
        ],
        expected_returncode=1,
    )
    blocked_fields = {
        finding.get('field')
        for finding in blocked.get('findings', [])
    }
    if blocked.get('mode') != 'merge-decision':
        fail('direct policy-gate default must remain strict merge-decision')
    if blocked_fields != {'result','checks_passed','human_gates_checked'}:
        fail(f'blocked draft strict findings drifted: {sorted(blocked_fields)}')

def check_pr_status_projection(root):
    compact = run_json_command(
        root,
        [
            'scripts/asgk.py','compact-pr-report',
            '--json-file','examples/pr_status.duplicate-check-latest-success.json',
            '--json',
        ],
        expected_returncode=0,
    )
    status_checks = compact.get('pr', {}).get('status_checks', [])
    current = [
        check for check in status_checks
        if check.get('current') is True and check.get('conclusion') == 'SUCCESS'
    ]
    superseded = [
        check for check in status_checks
        if check.get('superseded') is True and check.get('conclusion') == 'FAILURE'
    ]
    if len(current) != 1 or len(superseded) != 1:
        fail('latest-success compact report must retain one current success and one superseded failure')
    if current[0].get('identity') != superseded[0].get('identity'):
        fail('current and superseded status checks must share one identity')
    if (
        current[0].get('ordering_field') != 'startedAt'
        or superseded[0].get('ordering_field') != 'startedAt'
    ):
        fail('duplicate status checks must report one common startedAt ordering field')
    current_timestamp = current[0].get('ordering_timestamp')
    superseded_timestamp = superseded[0].get('ordering_timestamp')
    if (
        not isinstance(current_timestamp, str)
        or not isinstance(superseded_timestamp, str)
        or current_timestamp <= superseded_timestamp
    ):
        fail('current status check timestamp must be later than superseded evidence')

    expected_failure_fields = {
        'examples/pr_status.ready-blocked.json': {'merge_decision.result'},
        'examples/negative/pr_status.merge-blocked-all-clean.json': {'merge_decision.result'},
        'examples/negative/pr_status.duplicate-check-latest-failure.json': {
            'statusCheckRollup.validate',
            'statusCheckRollup.audit',
        },
        'examples/negative/pr_status.duplicate-check-ambiguous.json': {'statusCheckRollup.ordering'},
        'examples/negative/pr_status.missing-check-identity.json': {'statusCheckRollup.identity'},
        'examples/negative/pr_status.duplicate-check-missing-provider.json': {'statusCheckRollup.identity'},
    }
    for fixture, expected_fields in expected_failure_fields.items():
        payload = run_json_command(
            root,
            ['scripts/asgk.py','check-pr','--json-file',fixture,'--json'],
            expected_returncode=1,
        )
        actual_fields = {
            finding.get('field')
            for finding in payload.get('findings', [])
        }
        if actual_fields != expected_fields:
            fail(f'{fixture} findings {sorted(actual_fields)} != {sorted(expected_fields)}')

    def copy_payload(payload):
        return json.loads(json.dumps(payload))

    def assert_payload_findings(label, payload, expected_fields):
        result = run_json_payload_command(
            root,
            ['scripts/asgk.py','check-pr','--json-file','{payload}','--json'],
            payload,
            expected_returncode=1,
        )
        actual_fields = {
            finding.get('field')
            for finding in result.get('findings', [])
        }
        if actual_fields != expected_fields:
            fail(f'{label} findings {sorted(actual_fields)} != {sorted(expected_fields)}')

    valid_payload = json.loads(read(root, 'examples/pr_status.valid.json'))
    valid_result = run_json_payload_command(
        root,
        ['scripts/asgk.py','check-pr','--json-file','{payload}','--json'],
        valid_payload,
        expected_returncode=0,
    )
    if valid_result.get('evidence_source') != 'supplied_json_fixture_or_capture':
        fail('check-pr --json-file must identify supplied fixture/capture evidence')
    if 'supplied fixture or captured PR metadata' not in valid_result.get('proof_boundary', ''):
        fail('check-pr fixture proof boundary must not claim live GitHub evidence')

    hidden_heading = copy_payload(valid_payload)
    hidden_heading['body'] = hidden_heading['body'].replace(
        '## Validation',
        '```text\n## Validation\n```',
    )
    assert_payload_findings('fenced pseudo-heading', hidden_heading, {'body'})

    commented_heading = copy_payload(valid_payload)
    commented_heading['body'] = commented_heading['body'].replace(
        '## Validation',
        '<!--\n## Validation\n-->',
    )
    assert_payload_findings('commented pseudo-heading', commented_heading, {'body'})

    commented_gate = copy_payload(valid_payload)
    commented_gate['body'] = commented_gate['body'].replace(
        '  checks_passed: true',
        '```\n<!--\n  checks_passed: true\n-->\n```yaml',
    )
    assert_payload_findings('comment-hidden exact gate', commented_gate, {'body'})

    quoted_gate = copy_payload(valid_payload)
    quoted_gate['body'] = quoted_gate['body'].replace(
        '  checks_passed: true',
        '  checks_passed: "true"',
    )
    assert_payload_findings('quoted exact gate', quoted_gate, {'body'})

    uppercase_gate = copy_payload(valid_payload)
    uppercase_gate['body'] = uppercase_gate['body'].replace(
        '  checks_passed: true',
        '  checks_passed: TRUE',
    )
    assert_payload_findings('noncanonical exact gate case', uppercase_gate, {'body'})

    for label, invalid_draft in [
        ('missing isDraft', None),
        ('string isDraft', 'false'),
    ]:
        payload = copy_payload(valid_payload)
        if invalid_draft is None:
            del payload['isDraft']
        else:
            payload['isDraft'] = invalid_draft
        assert_payload_findings(label, payload, {'isDraft'})

    for label, review_value in [
        ('missing reviewDecision', '__MISSING__'),
        ('object reviewDecision', {'state': 'APPROVED'}),
        ('unknown reviewDecision', 'UNRECOGNIZED'),
        ('noncanonical reviewDecision', 'approved'),
    ]:
        payload = copy_payload(valid_payload)
        if review_value == '__MISSING__':
            del payload['reviewDecision']
        else:
            payload['reviewDecision'] = review_value
        assert_payload_findings(label, payload, {'reviewDecision'})

    for label, files_value in [
        ('object files', {}),
        ('null files', None),
        ('non-string file path', [{'path': {'value': 'README.md'}}]),
    ]:
        payload = copy_payload(valid_payload)
        payload['files'] = files_value
        assert_payload_findings(label, payload, {'files.shape'})

    empty_rollup = copy_payload(valid_payload)
    empty_rollup['statusCheckRollup'] = []
    assert_payload_findings(
        'empty statusCheckRollup',
        empty_rollup,
        {'statusCheckRollup'},
    )

    invalid_name = copy_payload(valid_payload)
    invalid_name['statusCheckRollup'][0]['name'] = {'value': 'validate'}
    assert_payload_findings(
        'non-string status check name',
        invalid_name,
        {'statusCheckRollup.identity'},
    )

    invalid_provider = copy_payload(valid_payload)
    invalid_provider['statusCheckRollup'][0]['workflowName'] = {
        'value': 'Bootstrap validation',
    }
    assert_payload_findings(
        'non-string status check provider',
        invalid_provider,
        {'statusCheckRollup.identity'},
    )

    missing_typename = json.loads(
        read(root, 'examples/negative/pr_status.duplicate-check-missing-provider.json')
    )
    for check in missing_typename['statusCheckRollup']:
        check.pop('__typename', None)
    assert_payload_findings(
        'repeated name without typename or provider',
        missing_typename,
        {'statusCheckRollup.identity'},
    )

    mixed_ordering = json.loads(
        read(root, 'examples/pr_status.duplicate-check-latest-success.json')
    )
    first_check, second_check = mixed_ordering['statusCheckRollup']
    first_check['conclusion'] = 'SUCCESS'
    first_check.pop('startedAt', None)
    first_check['completedAt'] = '2026-07-27T10:20:00Z'
    second_check['conclusion'] = 'SUCCESS'
    second_check['startedAt'] = '2026-07-27T10:15:00Z'
    second_check['completedAt'] = '2026-07-27T10:16:00Z'
    assert_payload_findings(
        'mixed timestamp semantics',
        mixed_ordering,
        {'statusCheckRollup.ordering'},
    )

def check_negative_runner_projection():
    cases = [
        (
            'traceback crash',
            'raise RuntimeError("asgk-negative-runner-crash-sentinel")',
            'command crashed',
        ),
        (
            'exit code 2',
            'raise SystemExit(2)',
            'command returned 2',
        ),
        (
            'signal termination',
            'import os, signal; os.kill(os.getpid(), signal.SIGTERM)',
            'another code or signal',
        ),
    ]
    for label, code, expected_output in cases:
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            result = run_expected_failures(
                ((sys.executable, '-c', code),)
            )
        if result != 1 or expected_output not in captured.getvalue():
            fail(
                f'negative runner must reject {label} as governance evidence'
            )

def check_control_sections(root):
    text = read(root,'docs/control/CONTROL_LAYER_V0.md')
    for section in CONTROL_REQUIRED_SECTIONS:
        if f'## {section}' not in text:
            fail(f'CONTROL_LAYER_V0.md missing section: {section}')

def check_storage_profile(root):
    profile = json.loads(read(root,'examples/storage_profile.local.json'))
    if profile['artifact_root'] == profile['local_state_root']:
        fail('artifact_root and local_state_root must differ')
    if profile['sync_policy'].get('app_managed_drive_api') is not False:
        fail('app_managed_drive_api must be false')
    for key in ['page_renders','model_cache','sqlite_live_db','temporary_jobs']:
        if profile['cache_policy'].get(key) != 'local_only':
            fail(f'{key} cache policy must be local_only')

def main():
    root = Path.cwd()
    missing = [p for p in REQUIRED_FILES if not (root/p).exists()]
    if missing:
        for p in missing: print(f'Missing required file: {p}')
        fail(f'{len(missing)} required files missing')
    check_terms(root)
    check_json(root)
    check_yaml_like_fields(root)
    check_templates(root)
    check_merge_decision_projection(root)
    check_pr_workflow_projection(root)
    check_policy_gate_routing_fixtures(root)
    check_policy_gate_failure_projection(root)
    check_pr_status_projection(root)
    check_negative_runner_projection()
    check_control_sections(root)
    check_storage_profile(root)
    print('Bootstrap validation passed.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
