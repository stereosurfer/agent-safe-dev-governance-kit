#!/usr/bin/env python3
"""Validate the retained ASGK source reference superset.

Dependency-light by design: no PyYAML/jsonschema required. The validator owns
only ASGK source-repository invariants. It is not a target-install manifest,
target-fit evaluator, or adoption decision.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

from asgk_lib.common import (
    field_block_lines,
    markdown_heading_occurrences,
    markdown_section,
)
from asgk_lib.scenario_registry import (
    CONTROLLED_ERROR_SCENARIOS,
    NEGATIVE_CASE_CHOICES,
    PARITY_SCENARIOS,
    RETAINED_JSON_SCENARIOS,
)
from asgk_lib.validation_result import (
    HUMAN_GATE_STATUS_VALUES,
    RESULT_VALUES,
    checked_validation_result,
    make_finding,
    validation_result_errors,
)
from asgk_lib.compact_handoff import FOLLOW_UP_ISSUE_PATTERN
from asgk_lib.handoff import (
    CORE_HANDOFF_ROOT,
    COMPACT_HANDOFF_ROOT,
    CORE_REQUIRED_FIELDS,
    FORBIDDEN_HANDOFF_CHARACTER_PATTERN_SOURCE,
    VALIDATION_STATUS_FIELDS,
    VALIDATION_STATUS_VALUES,
    is_material_handoff_text,
)
from asgk_lib.task_packet import (
    CANONICAL_TASK_FIELDS,
    TASK_PACKET_FALLBACK_FIELDS,
    TASK_PACKET_REFINEMENT_FIELDS,
    WORK_UNIT_EXECUTION_GATES,
    evaluate_task_packet,
)
from policy_gate_check import (
    MERGE_DECISION_REQUIRED_FIELDS,
    PR_REQUIRED_HEADINGS,
    line_field_count,
)

VALIDATOR_REFERENCE_ROOT = Path(__file__).resolve().parents[2]

STATIC_REQUIRED_SOURCE_PATHS_BY_ROLE = {
    "canonical_owner_spine": (
        "LICENSE",
        "README.md",
        "AGENTS.md",
        "docs/DOCUMENT_MAP.md",
        "docs/DOCUMENT_REGISTRY.md",
        "docs/INSTALL_SURFACE.md",
        "docs/bootstrap/01_physical_boundaries.md",
        "docs/control/AGENT_CAPABILITY_MATRIX.md",
        "docs/control/CONTEXT_BUDGET_POLICY.md",
        "docs/control/CURRENT_STATUS_POLICY.md",
        "docs/control/HANDOFF_PACKET.md",
        "docs/control/HUMAN_GATED_OPERATIONS.md",
        "docs/control/ISSUE_HYGIENE_GATE.md",
        "docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md",
        "docs/control/MERGE_DECISION_RECORD.md",
        "docs/control/NEGATIVE_TEST_PLAN.md",
        "docs/control/PR_REVIEW_CHECKLIST.md",
        "docs/control/SOURCE_ONLY_RELEASE_POLICY.md",
        "docs/control/TASK_PACKET_FORMAT.md",
        "docs/control/VALIDATION_STRATEGY.md",
        "docs/handoff/CURRENT_STATUS.md",
        "docs/handoff/ISSUE_CLOSEOUT_REVIEW_RULES.md",
    ),
    "retained_public_projections": (
        ".gitignore",
        "docs/QUICKSTART.md",
        "docs/SKILL_PACK.md",
        "docs/architecture/RUNTIME_ARTIFACT_POLICY.md",
        "docs/bootstrap/00_project_brief.md",
        "docs/bootstrap/05_context_budget.md",
        "docs/control/TARGET_INSTALL_CHECKLIST.md",
        "examples/README.md",
        "examples/negative/README.md",
    ),
    "retained_w3_projections": (
        ".github/ISSUE_TEMPLATE/agent_task.yml",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/workflows/bootstrap-validation.yml",
        "contracts/validation_result.contract.yaml",
        "docs/control/COMPACT_HANDOFF_PROFILE.md",
        "schemas/handoff_packet.schema.json",
        "schemas/merge_decision.schema.json",
        "schemas/task_packet.schema.json",
        "schemas/validation_result.schema.json",
        "templates/DOCUMENT_MAP.template.md",
        "templates/DOCUMENT_REGISTRY.template.md",
        "templates/task_packet.template.yaml",
        "examples/merge_decision.example.json",
        "examples/negative/pr_status.duplicate-check-missing-provider.json",
        "examples/task_packet.example.yaml",
        "examples/task_packet.valid.json",
        "examples/work_unit.valid-issue.json",
    ),
    "source_execution_surfaces": (
        "scripts/asgk.py",
        "scripts/asgk_lib/__init__.py",
        "scripts/asgk_lib/common.py",
        "scripts/asgk_lib/compact_handoff.py",
        "scripts/asgk_lib/handoff.py",
        "scripts/asgk_lib/negative.py",
        "scripts/asgk_lib/negative_cases.py",
        "scripts/asgk_lib/negative_runner.py",
        "scripts/asgk_lib/scenario_registry.py",
        "scripts/asgk_lib/scenario_runner.py",
        "scripts/asgk_lib/source_validation.py",
        "scripts/asgk_lib/status_policy.py",
        "scripts/asgk_lib/task_packet.py",
        "scripts/asgk_lib/text_fields.py",
        "scripts/asgk_lib/validation_result.py",
        "scripts/asgk_lib/workspace_state.py",
        "scripts/governance_hygiene.py",
        "scripts/policy_gate_check.py",
        "scripts/pr_governance_preflight.py",
    ),
    "source_distributed_skills": (
        "skills/asgk-current-status-handoff/SKILL.md",
        "skills/asgk-evidence-audit/SKILL.md",
        "skills/asgk-gatekeeper/SKILL.md",
        "skills/asgk-governance-health-check/SKILL.md",
        "skills/asgk-issue-scoping/SKILL.md",
        "skills/asgk-post-merge-closeout/SKILL.md",
        "skills/asgk-pr-evidence-merge-decision/SKILL.md",
        "skills/asgk-release-prep/SKILL.md",
        "skills/asgk-startup/SKILL.md",
        "skills/asgk-target-install-audit/SKILL.md",
        "skills/asgk-upgrade-audit/SKILL.md",
    ),
    "compatibility_wrapper": (
        "scripts/validate_bootstrap.py",
    ),
}

REGISTERED_FILE_OPTIONS = frozenset(
    {
        "--body-file",
        "--compare-file",
        "--current-status",
        "--file",
        "--github-event",
        "--json-file",
        "--paths-file",
        "--pr-body",
        "--readme",
        "--release-policy",
        "--report-json",
        "--source-inventory-file",
        "--task-packet",
    }
)

REQUIRED_TERMS = {
    "AGENTS.md": (
        "Source of truth rule",
        "Issue Hygiene Gate",
        "Stop conditions",
        "Low-risk merge boundary",
    ),
    "docs/control/CONTEXT_BUDGET_POLICY.md": (
        "context_read_set",
    ),
    "docs/control/HUMAN_GATED_OPERATIONS.md": (
        "current-head",
        "human_gate",
    ),
    "docs/control/VALIDATION_STRATEGY.md": (
        "mechanically_checked",
        "not_checked",
        "human_gate",
        "proof_boundary",
    ),
    "docs/control/MERGE_DECISION_RECORD.md": (
        "merge_blocked",
        "merge_allowed",
        "current-head",
    ),
    "docs/control/HANDOFF_PACKET.md": (
        "must_read",
        "must_not_do",
        "validation_status",
        "next_safe_action",
    ),
    "docs/control/CURRENT_STATUS_POLICY.md": (
        "current_status_impact",
        "post_merge_safe",
    ),
    "docs/INSTALL_SURFACE.md": (
        "frontier",
        "target-owned",
    ),
}

SOURCE_INVENTORY_CHECKED = (
    "supplied source inventory JSON object shape",
    "supplied source inventory path normalization and uniqueness",
    "required ASGK source path membership",
)
SOURCE_INVENTORY_NOT_CHECKED = (
    "source file existence, readability, or contents",
    "semantic correctness of any listed source file",
    "target repository fit, layout, governance depth, or adoption readiness",
    "human approval",
    "PR readiness or merge authority",
)
SOURCE_INVENTORY_PROOF_BOUNDARY = (
    "Exit 0 proves only that the caller-supplied source inventory has the "
    "supported JSON shape and includes the retained ASGK source-reference "
    "paths. It does not prove any listed file exists or is readable, inspect "
    "file contents or semantic correctness, assess a target repository's fit, "
    "layout, governance depth, or adoption readiness, establish human approval, "
    "or grant PR or merge authority."
)
SOURCE_INPUT_FAILURE_BOUNDARY = (
    "No source required-path comparison or live source-tree validation ran "
    "because the supplied input could not be accepted. No target, human "
    "approval, PR-readiness, or merge-authority claim was established."
)
LIVE_SOURCE_PROOF_BOUNDARY = (
    "Exit 0 proves only that the named retained ASGK source files exist and "
    "the current encoded source checks pass at the supplied repository root. "
    "The required set comes from this validator reference, while repo-local "
    "scenario structure and runner checks are evaluated from the inspected "
    "trusted ASGK source root. "
    "It does not prove target fit, target layout or governance depth, adoption "
    "readiness, unencoded semantic correctness, human approval, PR readiness, "
    "or merge authority."
)
LIVE_SOURCE_FAILURE_BOUNDARY = (
    "A failing live source result reports only required-path membership and "
    "the named check steps reached before the first failure. Remaining encoded "
    "checks, source-root trustworthiness, target fit, target layout or "
    "governance depth, adoption readiness, unencoded semantic correctness, "
    "human approval, PR readiness, and merge authority were not established."
)
LIVE_SOURCE_DOMAIN_NOT_CHECKED = (
    "unencoded semantic correctness of source documentation and behavior",
    "safety or trustworthiness of code at the inspected source root",
    "target repository fit, layout, governance depth, or adoption readiness",
    "human approval",
    "PR readiness or merge authority",
)

TASK_PACKET_FIELDS = list(TASK_PACKET_REFINEMENT_FIELDS)
ISSUE_FIELDS = [*CANONICAL_TASK_FIELDS, *WORK_UNIT_EXECUTION_GATES]
MERGE_DECISION_ALWAYS_TRUE_FIELDS = [
    'allowed_paths_checked','expected_output_checked','validation_evidence_checked',
]
PR_LIFECYCLE_EVENTS = [
    'opened','synchronize','reopened','edited','ready_for_review','converted_to_draft',
]


class SourceValidationFailure(RuntimeError):
    """One bounded failure from an encoded ASGK source check."""


class DuplicateInventoryKey(ValueError):
    """A caller-supplied inventory repeated one JSON object key."""


def fail(msg):
    raise SourceValidationFailure(msg)

def read(root, path):
    return (root/path).read_text(encoding='utf-8')


def _registered_command_paths(command):
    paths = set()
    previous = None
    for item in command:
        if (
            isinstance(item, str)
            and item.startswith("scripts/")
            and "{" not in item
        ):
            paths.add(item)
        if (
            previous in REGISTERED_FILE_OPTIONS
            and isinstance(item, str)
            and item
            and "{" not in item
            and not item.startswith("__asgk_missing__/")
        ):
            paths.add(item)
        previous = item
    return paths


def registered_evidence_paths():
    paths = set()
    for scenario in (*RETAINED_JSON_SCENARIOS, *CONTROLLED_ERROR_SCENARIOS):
        paths.update(_registered_command_paths(scenario.command))
        if scenario.temp_input is not None and scenario.temp_input.source:
            paths.add(scenario.temp_input.source)
    for scenario in PARITY_SCENARIOS:
        paths.update(_registered_command_paths(scenario.left_command))
        paths.update(_registered_command_paths(scenario.right_command))
    return tuple(sorted(paths))


def required_source_paths():
    paths = {
        path
        for role_paths in STATIC_REQUIRED_SOURCE_PATHS_BY_ROLE.values()
        for path in role_paths
    }
    paths.update(registered_evidence_paths())
    return tuple(sorted(paths))


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

def run_json_command(root, args, *, expected_returncode, label=None):
    result = subprocess.run(
        [sys.executable, *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != expected_returncode:
        detail = result.stdout.strip() or result.stderr.strip() or 'no output'
        prefix = f'{label}: ' if label else ''
        fail(f'{prefix}command returned {result.returncode}, expected {expected_returncode}: {" ".join(args)}: {detail}')
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        fail(f'command did not emit JSON: {" ".join(args)}: {error}')

def run_json_payload_command(
    root,
    args,
    payload,
    *,
    expected_returncode,
    label=None,
):
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
            label=label,
        )


def run_text_payload_command(root, args, payload, *, expected_returncode):
    with tempfile.TemporaryDirectory() as tmpdir:
        payload_path = Path(tmpdir) / 'payload.yaml'
        payload_path.write_text(payload, encoding='utf-8')
        resolved = [
            str(payload_path) if arg == '{payload}' else arg
            for arg in args
        ]
        return run_json_command(
            root,
            resolved,
            expected_returncode=expected_returncode,
        )


def run_json_payload_and_paths_command(
    root,
    args,
    payload,
    changed_paths,
    *,
    expected_returncode,
):
    with tempfile.TemporaryDirectory() as tmpdir:
        payload_path = Path(tmpdir) / 'payload.json'
        paths_path = Path(tmpdir) / 'changed-paths.txt'
        payload_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding='utf-8',
        )
        paths_path.write_text(
            ''.join(f'{path}\n' for path in changed_paths),
            encoding='utf-8',
        )
        resolved = [
            (
                str(payload_path)
                if arg == '{payload}'
                else str(paths_path)
                if arg == '{paths}'
                else arg
            )
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
        if payload.get('evidence_source') != 'supplied_github_event_file':
            fail(f'{fixture} must preserve GitHub event provenance')

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
        if payload.get('evidence_source') != 'supplied_github_event_file':
            fail(f'{fixture} routing failure must preserve GitHub event provenance')

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


def finding_codes(payload):
    return [
        finding.get('code')
        for finding in payload.get('findings', [])
        if isinstance(finding, dict)
    ]


def check_w3a_work_unit_and_task_packet_projection(root):
    schema = json.loads(read(root, 'schemas/task_packet.schema.json'))
    schema_refs = {
        entry.get('$ref')
        for entry in schema.get('oneOf', [])
        if isinstance(entry, dict)
    }
    expected_refs = {
        '#/$defs/issue_refinement',
        '#/$defs/github_unavailable_fallback',
    }
    if schema_refs != expected_refs:
        fail(f'task packet schema mode refs drifted: {sorted(schema_refs)}')

    definitions = schema.get('$defs', {})
    refinement = definitions.get('issue_refinement', {})
    fallback = definitions.get('github_unavailable_fallback', {})
    if set(refinement.get('required', [])) != set(TASK_PACKET_REFINEMENT_FIELDS):
        fail('task packet schema issue_refinement required fields drifted')
    if set(fallback.get('required', [])) != set(TASK_PACKET_FALLBACK_FIELDS):
        fail('task packet schema github_unavailable_fallback required fields drifted')
    if refinement.get('additionalProperties') is not False:
        fail('task packet issue_refinement must reject additional properties')
    if fallback.get('additionalProperties') is not False:
        fail('task packet github_unavailable_fallback must reject additional properties')

    schema_text = read(root, 'schemas/task_packet.schema.json')
    template_text = read(root, 'templates/task_packet.template.yaml')
    issue_form = read(root, '.github/ISSUE_TEMPLATE/agent_task.yml')
    if 'intelligence_level_reason' in schema_text or 'intelligence_level_reason' in template_text:
        fail('v2 task packet projections must not retain intelligence_level_reason')
    if 'type: textarea\n    id: context_read_set' not in issue_form:
        fail('agent task form must capture exact context_read_set content in a textarea')

    authority = run_json_command(
        root,
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', 'examples/work_unit.valid-issue.json',
            '--authority-only', '--json',
        ],
        expected_returncode=0,
    )
    if (
        authority.get('authority_only') is not True
        or authority.get('changed_paths_checked') is not False
        or authority.get('canonical_task_fields') != list(CANONICAL_TASK_FIELDS)
        or authority.get('execution_gates') != list(WORK_UNIT_EXECUTION_GATES)
    ):
        fail('authority-only work-unit proof boundary drifted')

    unlabeled_fence_work_unit = json.loads(
        read(root, 'examples/work_unit.valid-issue.json')
    )
    unlabeled_fence_work_unit['body'] = unlabeled_fence_work_unit[
        'body'
    ].replace('```yaml', '```', 1)
    run_json_payload_command(
        root,
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        unlabeled_fence_work_unit,
        expected_returncode=0,
    )

    post_diff = run_json_command(
        root,
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', 'examples/work_unit.valid-issue.json',
            '--paths-file', 'examples/work_unit.changed-paths.valid.txt',
            '--json',
        ],
        expected_returncode=0,
    )
    if post_diff.get('changed_paths_checked') is not True:
        fail('post-diff work-unit check must report changed_paths_checked true')

    fallback_result = run_json_command(
        root,
        [
            'scripts/asgk.py', 'task-packet-check',
            '--file', 'examples/task_packet.valid.json',
            '--json',
        ],
        expected_returncode=0,
    )
    if (
        fallback_result.get('mode') != 'github_unavailable_fallback'
        or fallback_result.get('task_packet', {}).get('github_issue_required_before_pr') is not True
        or fallback_result.get('task_packet', {}).get('temporary_local_execution_authority')
        != (
            'conditional_on_verified_github_unavailability_'
            'and_no_escalation_trigger'
        )
        or fallback_result.get('task_packet', {}).get('pr_or_merge_authority') is not False
    ):
        fail('fallback packet proof boundary drifted')

    canonical = run_json_command(
        root,
        [
            'scripts/asgk.py', 'task-packet-check',
            '--json-file', 'examples/compact_governance/task_packet_delta.valid.json',
            '--json',
        ],
        expected_returncode=0,
    )
    compact = run_json_command(
        root,
        [
            'scripts/asgk.py', 'compact-task-packet-check',
            '--json-file', 'examples/compact_governance/task_packet_delta.valid.json',
            '--json',
        ],
        expected_returncode=0,
    )
    if canonical != compact:
        fail('compact-task-packet-check must be output-identical to task-packet-check')
    canonical_projection = canonical.get('task_packet', {})
    if (
        canonical_projection.get('projection_within_issue_scope') is not True
        or canonical_projection.get('may_narrow_effective_execution_scope')
        is not True
        or canonical_projection.get('cannot_modify_issue_authority') is not True
        or 'may_narrow_issue_authority' in canonical_projection
        or 'must_not_expand_issue_authority' in canonical_projection
    ):
        fail('issue-refinement output must describe scope projection, not authority')

    same_repo_url_bundle = json.loads(
        read(root, 'examples/compact_governance/task_packet_delta.valid.json')
    )
    same_repo_url = (
        'https://github.com/stereosurfer/'
        'agent-safe-dev-governance-kit/issues/1001'
    )
    same_repo_url_bundle['issue']['html_url'] = same_repo_url
    same_repo_url_bundle['task_packet']['durable_source_of_truth'] = same_repo_url
    run_json_payload_command(
        root,
        [
            'scripts/asgk.py', 'task-packet-check',
            '--json-file', '{payload}', '--json',
        ],
        same_repo_url_bundle,
        expected_returncode=0,
    )

    negative_cases = [
        (
            'work-unit reason alias',
            [
                'scripts/asgk.py', 'work-unit-check',
                '--json-file', 'examples/negative/work_unit.reason-alias-only.json',
                '--authority-only', '--json',
            ],
            {'WU_REASON_ALIAS_FORBIDDEN', 'WU_REQUIRED_FIELD_MISSING'},
        ),
        (
            'work-unit missing context gate',
            [
                'scripts/asgk.py', 'work-unit-check',
                '--json-file', 'examples/negative/work_unit.missing-context-read-set.json',
                '--authority-only', '--json',
            ],
            {'WU_EXECUTION_GATE_MISSING'},
        ),
        (
            'work-unit missing project validation gate',
            [
                'scripts/asgk.py', 'work-unit-check',
                '--json-file', 'examples/negative/work_unit.missing-project-specific-validation.json',
                '--authority-only', '--json',
            ],
            {'WU_EXECUTION_GATE_MISSING'},
        ),
        (
            'work-unit outside allowed path',
            [
                'scripts/asgk.py', 'work-unit-check',
                '--json-file', 'examples/work_unit.valid-issue.json',
                '--paths-file', 'examples/negative/work_unit.changed-paths.outside-allowed.txt',
                '--json',
            ],
            {'WU_PATH_OUTSIDE_SCOPE'},
        ),
        (
            'work-unit post-diff input missing',
            [
                'scripts/asgk.py', 'work-unit-check',
                '--json-file', 'examples/work_unit.valid-issue.json',
                '--json',
            ],
            {'WU_INPUT_MODE_INVALID'},
        ),
        (
            'task packet chat authority',
            [
                'scripts/asgk.py', 'task-packet-check',
                '--file', 'examples/negative/task_packet.see-chat.yaml', '--json',
            ],
            {'TP_CHAT_AUTHORITY_FORBIDDEN'},
        ),
        (
            'task packet missing stop',
            [
                'scripts/asgk.py', 'task-packet-check',
                '--file', 'examples/negative/task_packet.no-stop.yaml', '--json',
            ],
            {'TP_REQUIRED_FIELD_MISSING'},
        ),
        (
            'task packet empty list',
            [
                'scripts/asgk.py', 'task-packet-check',
                '--file', 'examples/negative/task_packet.empty-list.yaml', '--json',
            ],
            {'TP_LIST_EMPTY'},
        ),
        (
            'task packet issue required',
            [
                'scripts/asgk.py', 'task-packet-check',
                '--file', 'examples/negative/task_packet.executable-no-github-issue.yaml',
                '--json',
            ],
            {'TP_ISSUE_REQUIRED'},
        ),
        (
            'task packet overbroad read set',
            [
                'scripts/asgk.py', 'task-packet-check',
                '--file', 'examples/negative/task_packet.overbroad-context-read-set.yaml',
                '--json',
            ],
            {'TP_READ_SET_OVERBROAD'},
        ),
        (
            'task packet reason alias',
            [
                'scripts/asgk.py', 'task-packet-check',
                '--file', 'examples/negative/task_packet.reason-alias.yaml', '--json',
            ],
            {'TP_LEGACY_FIELD_FORBIDDEN', 'TP_REQUIRED_FIELD_MISSING'},
        ),
        (
            'task packet fallback status',
            [
                'scripts/asgk.py', 'task-packet-check',
                '--file', 'examples/negative/task_packet.fallback-status.yaml', '--json',
            ],
            {'TP_FALLBACK_STATUS_INVALID'},
        ),
        (
            'task packet path expansion',
            [
                'scripts/asgk.py', 'task-packet-check',
                '--json-file', 'examples/negative/compact_governance/task-packet-delta-expands-scope.json',
                '--json',
            ],
            {'TP_ALLOWED_PATH_EXPANSION'},
        ),
        (
            'task packet authority mismatch',
            [
                'scripts/asgk.py', 'task-packet-check',
                '--json-file', 'examples/negative/compact_governance/task-packet-authority-mismatch.json',
                '--json',
            ],
            {'TP_AUTHORITY_MISMATCH'},
        ),
        (
            'task packet read-set expansion',
            [
                'scripts/asgk.py', 'task-packet-check',
                '--json-file', 'examples/negative/compact_governance/task-packet-read-set-expands.json',
                '--json',
            ],
            {'TP_READ_SET_EXPANSION'},
        ),
        (
            'task packet validation expansion',
            [
                'scripts/asgk.py', 'task-packet-check',
                '--json-file', 'examples/negative/compact_governance/task-packet-validation-expands.json',
                '--json',
            ],
            {'TP_VALIDATION_EXPANSION'},
        ),
    ]
    for label, command, expected_codes in negative_cases:
        payload = run_json_command(
            root,
            command,
            expected_returncode=1,
        )
        actual_codes = set(finding_codes(payload))
        if actual_codes != expected_codes:
            fail(
                f'{label} finding codes {sorted(actual_codes)} != '
                f'{sorted(expected_codes)}'
            )

    def replace_list_field(body, field, values):
        replacement = field + ':\n' + ''.join(
            f'  - {value}\n' for value in values
        )
        updated, count = re.subn(
            rf'(?m)^{re.escape(field)}:\n(?:  - .*\n)+',
            replacement,
            body,
            count=1,
        )
        if count != 1:
            fail(f'could not mutate fixture list field: {field}')
        return updated

    def assert_mutation(label, command, payload, expected_codes):
        result = run_json_payload_command(
            root,
            command,
            payload,
            expected_returncode=1,
            label=label,
        )
        actual_codes = set(finding_codes(result))
        if actual_codes != expected_codes:
            fail(
                f'{label} finding codes {sorted(actual_codes)} != '
                f'{sorted(expected_codes)}'
            )
        return result

    valid_work_unit = json.loads(read(root, 'examples/work_unit.valid-issue.json'))
    valid_field_values = json.loads(read(root, 'examples/task_packet.valid.json'))

    def individual_task_field_body(
        values,
        *,
        heading_level=2,
        heading_style='atx',
    ):
        sections = []
        for field in [*CANONICAL_TASK_FIELDS, *WORK_UNIT_EXECUTION_GATES]:
            value = values[field]
            if isinstance(value, list):
                content = '\n'.join(f'- {item}' for item in value)
            else:
                content = str(value)
            if heading_style == 'setext':
                marker = '=' if heading_level == 1 else '-'
                heading = f'{field}\n{marker * max(3, len(field))}'
            else:
                heading = f'{"#" * heading_level} {field}'
            sections.append(f'{heading}\n\n{content}')
        return '\n\n'.join(sections) + '\n'

    individual_work_unit = json.loads(json.dumps(valid_work_unit))
    individual_work_unit['body'] = individual_task_field_body(valid_field_values)
    run_json_payload_command(
        root,
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        individual_work_unit,
        expected_returncode=0,
    )

    setext_work_unit = json.loads(json.dumps(valid_work_unit))
    setext_work_unit['body'] = individual_task_field_body(
        valid_field_values,
        heading_style='setext',
    )
    run_json_payload_command(
        root,
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        setext_work_unit,
        expected_returncode=0,
    )
    setext_phantom_path = '-' * len('allowed_paths')
    setext_phantom_result = run_json_payload_and_paths_command(
        root,
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--paths-file', '{paths}', '--json',
        ],
        setext_work_unit,
        [setext_phantom_path],
        expected_returncode=1,
    )
    if set(finding_codes(setext_phantom_result)) != {
        'WU_PATH_OUTSIDE_SCOPE'
    }:
        fail('Setext underline must not become executable allowed-path data')

    nested_setext_work_unit = json.loads(json.dumps(valid_work_unit))
    nested_setext_work_unit['body'] = individual_task_field_body(
        valid_field_values,
        heading_level=1,
    )
    nested_setext_label = 'docs/QUICKSTART.md'
    nested_setext_underline = '-' * len(nested_setext_label)
    nested_setext_work_unit['body'] = nested_setext_work_unit['body'].replace(
        '\n\n# expected_output',
        (
            f'\n{nested_setext_label}\n'
            f'{nested_setext_underline}\n\n'
            '# expected_output'
        ),
        1,
    )
    nested_setext_authority = run_json_payload_command(
        root,
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        nested_setext_work_unit,
        expected_returncode=0,
    )
    if nested_setext_underline in set(
        nested_setext_authority.get('allowed_paths', [])
    ):
        fail('nested Setext underline must not enter allowed_paths projection')
    nested_setext_phantom_result = run_json_payload_and_paths_command(
        root,
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--paths-file', '{paths}', '--json',
        ],
        nested_setext_work_unit,
        [nested_setext_underline],
        expected_returncode=1,
    )
    if set(finding_codes(nested_setext_phantom_result)) != {
        'WU_PATH_OUTSIDE_SCOPE'
    }:
        fail('nested Setext underline must not authorize a changed path')

    unicode_validation_work_unit = json.loads(json.dumps(valid_work_unit))
    unicode_validation_work_unit['body'] = replace_list_field(
        unicode_validation_work_unit['body'],
        'project_specific_validation',
        ['not_applicable：純文件變更'],
    )
    run_json_payload_command(
        root,
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        unicode_validation_work_unit,
        expected_returncode=0,
    )

    issue_form_h3_work_unit = json.loads(json.dumps(valid_work_unit))
    issue_form_h3_work_unit['body'] = individual_task_field_body(
        valid_field_values,
        heading_level=3,
    )
    run_json_payload_command(
        root,
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        issue_form_h3_work_unit,
        expected_returncode=0,
    )

    fenced_example_work_unit = json.loads(json.dumps(individual_work_unit))
    fenced_example_work_unit['body'] += (
        '\n## Non-authoritative example\n\n'
        '```markdown\n'
        '## objective\n\n'
        'fenced examples do not grant authority\n\n'
        '## allowed_paths\n\n'
        '- ../outside\n'
        '```\n'
    )
    run_json_payload_command(
        root,
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        fenced_example_work_unit,
        expected_returncode=0,
    )

    canonical_fenced_example = json.loads(json.dumps(valid_work_unit))
    canonical_fenced_example['body'] += (
        '\n# Non-authoritative example\n\n'
        '```yaml\n'
        'objective: fenced examples do not grant authority\n'
        'allowed_paths:\n'
        '  - ../outside\n'
        '```\n'
    )
    run_json_payload_command(
        root,
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        canonical_fenced_example,
        expected_returncode=0,
    )

    canonical_same_level_example = json.loads(json.dumps(valid_work_unit))
    canonical_same_level_example['body'] += (
        '\n## Non-authoritative example\n\n'
        '```markdown\n'
        '## objective\n\n'
        'fenced example after the canonical section\n'
        '```\n'
    )
    run_json_payload_command(
        root,
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        canonical_same_level_example,
        expected_returncode=0,
    )

    noncanonical_h3_section = json.loads(json.dumps(valid_work_unit))
    noncanonical_h3_section['body'] = noncanonical_h3_section['body'].replace(
        '## Required Task Fields',
        '### Required Task Fields',
        1,
    )
    assert_mutation(
        'work-unit noncanonical H3 task-field section',
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        noncanonical_h3_section,
        {'WU_TASK_FIELD_AMBIGUOUS'},
    )

    for label, heading in [
        ('hyphenated', '## Required-Task-Fields'),
        ('uppercase underscore', '## REQUIRED_TASK_FIELDS'),
        ('punctuated', '## Required Task Fields!'),
    ]:
        nonexact_canonical = json.loads(json.dumps(valid_work_unit))
        nonexact_canonical['body'] = nonexact_canonical['body'].replace(
            '## Required Task Fields',
            heading,
            1,
        )
        assert_mutation(
            f'work-unit {label} canonical task-field section',
            [
                'scripts/asgk.py', 'work-unit-check',
                '--json-file', '{payload}', '--authority-only', '--json',
            ],
            nonexact_canonical,
            {'WU_TASK_FIELD_AMBIGUOUS'},
        )

    duplicate_heading_work_unit = json.loads(json.dumps(individual_work_unit))
    duplicate_heading_work_unit['body'] += (
        '\n## objective\n\n'
        'A second visible objective is ambiguous.\n'
    )
    assert_mutation(
        'work-unit duplicate task-field heading',
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        duplicate_heading_work_unit,
        {'WU_TASK_FIELD_AMBIGUOUS'},
    )

    duplicate_h1_heading = json.loads(json.dumps(individual_work_unit))
    duplicate_h1_heading['body'] += (
        '\n# objective\n\n'
        'A competing H1 objective is ambiguous.\n'
    )
    assert_mutation(
        'work-unit competing H1 task-field heading',
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        duplicate_h1_heading,
        {'WU_TASK_FIELD_AMBIGUOUS'},
    )

    duplicate_setext_heading = json.loads(json.dumps(individual_work_unit))
    duplicate_setext_heading['body'] += (
        '\nobjective\n'
        '=========\n\n'
        'A competing Setext objective is ambiguous.\n'
    )
    assert_mutation(
        'work-unit competing Setext task-field heading',
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        duplicate_setext_heading,
        {'WU_TASK_FIELD_AMBIGUOUS'},
    )

    mixed_work_unit = json.loads(json.dumps(valid_work_unit))
    mixed_work_unit['body'] += (
        '\n## objective\n\n'
        'An individual field cannot accompany Required Task Fields.\n'
    )
    assert_mutation(
        'work-unit mixed task-field representations',
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        mixed_work_unit,
        {'WU_TASK_FIELD_AMBIGUOUS'},
    )

    quoted_yaml_key_work_unit = json.loads(json.dumps(valid_work_unit))
    quoted_yaml_key_work_unit['body'] = (
        quoted_yaml_key_work_unit['body'].replace(
            '\n```\n',
            '\n"objective": quoted duplicate\n'
            '```\n',
            1,
        )
    )
    assert_mutation(
        'work-unit quoted canonical YAML key',
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        quoted_yaml_key_work_unit,
        {'WU_TASK_FIELD_AMBIGUOUS'},
    )

    quoted_field_outside_fence = json.loads(json.dumps(valid_work_unit))
    quoted_field_outside_fence['body'] = (
        quoted_field_outside_fence['body'].replace(
            '```yaml\n',
            '"allowed_paths":\n'
            '  - AGENTS.md\n\n'
            '```yaml\n',
            1,
        )
    )
    assert_mutation(
        'work-unit quoted task field outside canonical fence',
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        quoted_field_outside_fence,
        {'WU_TASK_FIELD_AMBIGUOUS'},
    )

    duplicate_yaml_key_work_unit = json.loads(json.dumps(valid_work_unit))
    duplicate_yaml_key_work_unit['body'] = (
        duplicate_yaml_key_work_unit['body'].replace(
            '\n```\n',
            '\nallowed_paths:\n'
            '  - scripts/asgk.py\n'
            '```\n',
            1,
        )
    )
    assert_mutation(
        'work-unit duplicate canonical YAML key',
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        duplicate_yaml_key_work_unit,
        {'WU_TASK_FIELD_AMBIGUOUS'},
    )

    nested_context_heading = json.loads(json.dumps(individual_work_unit))
    nested_context_heading['body'] = nested_context_heading['body'].replace(
        '\n\n## project_specific_validation',
        '\n\n### Additional reads\n\n- entire repo'
        '\n\n## project_specific_validation',
        1,
    )
    assert_mutation(
        'work-unit nested context heading cannot hide broad read',
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        nested_context_heading,
        {'WU_READ_SET_INVALID', 'WU_READ_SET_OVERBROAD'},
    )

    multiple_yaml_blocks_work_unit = json.loads(json.dumps(valid_work_unit))
    multiple_yaml_blocks_work_unit['body'] = (
        multiple_yaml_blocks_work_unit['body'].replace(
            '\n```\n',
            '\n```\n\n```yaml\nobjective: second candidate\n```\n',
            1,
        )
    )
    assert_mutation(
        'work-unit multiple canonical YAML blocks',
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        multiple_yaml_blocks_work_unit,
        {'WU_TASK_FIELD_AMBIGUOUS'},
    )

    multiple_canonical_sections = json.loads(json.dumps(valid_work_unit))
    multiple_canonical_sections['body'] += (
        '\n## Required Task Fields\n\n'
        '```yaml\n'
        'objective: second canonical section\n'
        '```\n'
    )
    assert_mutation(
        'work-unit multiple canonical task-field sections',
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        multiple_canonical_sections,
        {'WU_TASK_FIELD_AMBIGUOUS'},
    )

    hidden_work_unit = json.loads(json.dumps(valid_work_unit))
    hidden_work_unit['body'] = '<!--\n' + hidden_work_unit['body'] + '\n-->'
    assert_mutation(
        'hidden work-unit authority',
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        hidden_work_unit,
        {'WU_REQUIRED_FIELD_MISSING', 'WU_EXECUTION_GATE_MISSING'},
    )

    work_unit_mutations = [
        (
            'work-unit overbroad read set',
            'context_read_set',
            ['entire repo'],
            {'WU_READ_SET_OVERBROAD'},
        ),
        (
            'work-unit absolute read set',
            'context_read_set',
            ['/etc/hosts'],
            {'WU_READ_SET_OUTSIDE_REPO'},
        ),
        (
            'work-unit pseudo-reference broad suffix',
            'context_read_set',
            ['GitHub issue #176 and entire repo'],
            {'WU_READ_SET_OVERBROAD'},
        ),
        (
            'work-unit arbitrary prose read set',
            'context_read_set',
            ['read whatever is useful'],
            {'WU_READ_SET_INVALID'},
        ),
        (
            'work-unit task-packet self reference',
            'context_read_set',
            ['this task packet'],
            {'WU_READ_SET_INVALID'},
        ),
        (
            'work-unit bare not_applicable validation',
            'project_specific_validation',
            ['not_applicable'],
            {'WU_PROJECT_VALIDATION_REASON_MISSING'},
        ),
        (
            'work-unit punctuation-only not_applicable validation',
            'project_specific_validation',
            ['not applicable -'],
            {'WU_PROJECT_VALIDATION_REASON_MISSING'},
        ),
        (
            'work-unit traversal allowed path',
            'allowed_paths',
            ['docs/../README.md'],
            {'WU_ALLOWED_PATH_INVALID'},
        ),
    ]
    for label, field, values, expected_codes in work_unit_mutations:
        mutation = json.loads(json.dumps(valid_work_unit))
        mutation['body'] = replace_list_field(mutation['body'], field, values)
        assert_mutation(
            label,
            [
                'scripts/asgk.py', 'work-unit-check',
                '--json-file', '{payload}', '--authority-only', '--json',
            ],
            mutation,
            expected_codes,
        )

    pr_shape = json.loads(json.dumps(valid_work_unit))
    pr_shape.pop('kind', None)
    pr_shape['html_url'] = (
        'https://github.com/stereosurfer/agent-safe-dev-governance-kit/pull/176'
    )
    pr_result = run_json_payload_command(
        root,
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        pr_shape,
        expected_returncode=0,
    )
    if pr_result.get('work_unit', {}).get('kind') != 'pr':
        fail('captured PR URL must be classified as a PR')

    conflicting_issue_request = json.loads(json.dumps(valid_work_unit))
    conflicting_issue_request['_asgk_requested_kind'] = 'issue'
    conflicting_issue_request['pull_request'] = {
        'url': 'https://api.github.com/repos/example/repo/pulls/176',
    }
    assert_mutation(
        'work-unit issue request with PR markers',
        [
            'scripts/asgk.py', 'work-unit-check',
            '--json-file', '{payload}', '--authority-only', '--json',
        ],
        conflicting_issue_request,
        {'WU_KIND_INVALID'},
    )

    fallback_packet = json.loads(read(root, 'examples/task_packet.valid.json'))
    fallback_pseudo = json.loads(json.dumps(fallback_packet))
    fallback_pseudo['context_read_set'] = ['this task packet']
    pseudo_measurement = run_json_payload_command(
        root,
        [
            'scripts/asgk.py', 'context-budget-measure',
            '--task-packet', '{payload}', '--json',
        ],
        fallback_pseudo,
        expected_returncode=0,
    )
    if pseudo_measurement.get('pseudo_refs') != ['this task packet']:
        fail('this task packet must be a non-file context pseudo-reference')

    fallback_mutations = [
        (
            'task-packet non-string list item',
            'plan',
            [1],
            {'TP_LIST_ITEM_TYPE_INVALID'},
        ),
        (
            'task-packet blank list item',
            'plan',
            ['   '],
            {'TP_LIST_ITEM_EMPTY'},
        ),
        (
            'task-packet absolute read set',
            'context_read_set',
            ['/etc/hosts'],
            {'TP_READ_SET_OUTSIDE_REPO'},
        ),
        (
            'task-packet everything read set',
            'context_read_set',
            ['everything'],
            {'TP_READ_SET_OVERBROAD'},
        ),
        (
            'task-packet URL broad suffix',
            'context_read_set',
            ['https://example.invalid plus whole repository'],
            {'TP_READ_SET_OVERBROAD'},
        ),
        (
            'task-packet arbitrary prose read set',
            'context_read_set',
            ['read the relevant files'],
            {'TP_READ_SET_INVALID'},
        ),
        (
            'task-packet bare not_applicable validation',
            'project_specific_validation',
            ['not_applicable'],
            {'TP_PROJECT_VALIDATION_REASON_MISSING'},
        ),
        (
            'task-packet punctuation-only not_applicable validation',
            'project_specific_validation',
            ['N/A ( )'],
            {'TP_PROJECT_VALIDATION_REASON_MISSING'},
        ),
        (
            'task-packet protected fallback scope',
            'allowed_paths',
            ['AGENTS.md'],
            {'TP_FALLBACK_ESCALATION_REQUIRED'},
        ),
        (
            'task-packet traversal allowed path',
            'allowed_paths',
            ['docs/../README.md'],
            {'TP_ALLOWED_PATH_INVALID'},
        ),
    ]
    for label, field, value, expected_codes in fallback_mutations:
        mutation = json.loads(json.dumps(fallback_packet))
        mutation[field] = value
        mutation_result = assert_mutation(
            label,
            [
                'scripts/asgk.py', 'task-packet-check',
                '--file', '{payload}', '--json',
            ],
            mutation,
            expected_codes,
        )
        if (
            label == 'task-packet protected fallback scope'
            and mutation_result.get('task_packet', {}).get(
                'temporary_local_execution_authority'
            )
            is not False
        ):
            fail('failed fallback must not emit conditional local-work authority')

    hidden_packet = '<!--\n' + read(
        root,
        'examples/task_packet.example.yaml',
    ) + '\n-->'
    hidden_result = run_text_payload_command(
        root,
        [
            'scripts/asgk.py', 'task-packet-check',
            '--file', '{payload}', '--json',
        ],
        hidden_packet,
        expected_returncode=1,
    )
    if set(finding_codes(hidden_result)) != {'TP_MODE_MISSING'}:
        fail('hidden task packet must fail with TP_MODE_MISSING')

    duplicate_raw_packet = (
        read(root, 'examples/task_packet.example.yaml')
        + '\nallowed_paths:\n'
        + '  - examples/task_packet.example.yaml\n'
    )
    duplicate_raw_result = run_text_payload_command(
        root,
        [
            'scripts/asgk.py', 'task-packet-check',
            '--file', '{payload}', '--json',
        ],
        duplicate_raw_packet,
        expected_returncode=1,
    )
    if set(finding_codes(duplicate_raw_result)) != {
        'TP_TASK_FIELD_AMBIGUOUS'
    }:
        fail('duplicate raw packet key must fail with exact ambiguity code')
    duplicate_context_result = run_text_payload_command(
        root,
        [
            'scripts/asgk.py', 'context-budget-measure',
            '--task-packet', '{payload}', '--json',
        ],
        duplicate_raw_packet,
        expected_returncode=1,
    )
    if set(finding_codes(duplicate_context_result)) != {
        'TP_TASK_FIELD_AMBIGUOUS'
    }:
        fail('context budget must preserve raw packet ambiguity code')

    def indent_yaml(text, spaces):
        prefix = ' ' * spaces
        return '\n'.join(
            prefix + line if line else line
            for line in text.splitlines()
        )

    valid_raw_packet = read(root, 'examples/task_packet.example.yaml')

    def assert_packet_source_ambiguity(label, result):
        if set(finding_codes(result)) != {'TP_TASK_FIELD_AMBIGUOUS'}:
            fail(f'{label} must fail with exact ambiguity code')
        if 'temporary_local_execution_authority' in json.dumps(
            result,
            sort_keys=True,
        ):
            fail(f'{label} must not emit temporary local-work authority')

    competing_wrapper_packet = (
        valid_raw_packet
        + '\ntask_packet:\n'
        + indent_yaml(valid_raw_packet, 2)
        + '\n'
    )
    competing_wrapper_result = run_text_payload_command(
        root,
        [
            'scripts/asgk.py', 'task-packet-check',
            '--file', '{payload}', '--json',
        ],
        competing_wrapper_packet,
        expected_returncode=1,
    )
    assert_packet_source_ambiguity(
        'raw-plus-wrapper packet',
        competing_wrapper_result,
    )

    nested_wrapper_packet = (
        valid_raw_packet
        + '\ncontainer:\n'
        + '  bad_input:\n'
        + indent_yaml(valid_raw_packet, 4)
        + '\n'
    )
    nested_wrapper_result = run_text_payload_command(
        root,
        [
            'scripts/asgk.py', 'task-packet-check',
            '--file', '{payload}', '--json',
        ],
        nested_wrapper_packet,
        expected_returncode=1,
    )
    assert_packet_source_ambiguity(
        'nested packet wrapper',
        nested_wrapper_result,
    )

    wrapper_inside_wrapper_packet = (
        'task_packet:\n'
        '  bad_input:\n'
        + indent_yaml(valid_raw_packet, 4)
        + '\n'
    )
    wrapper_inside_result = run_text_payload_command(
        root,
        [
            'scripts/asgk.py', 'task-packet-check',
            '--file', '{payload}', '--json',
        ],
        wrapper_inside_wrapper_packet,
        expected_returncode=1,
    )
    assert_packet_source_ambiguity(
        'wrapper-inside-wrapper',
        wrapper_inside_result,
    )

    competing_yaml_wrappers = (
        'bad_input:\n'
        + indent_yaml(valid_raw_packet, 2)
        + '\ntask_packet:\n'
        + indent_yaml(valid_raw_packet, 2)
        + '\n'
    )
    competing_yaml_result = run_text_payload_command(
        root,
        [
            'scripts/asgk.py', 'task-packet-check',
            '--file', '{payload}', '--json',
        ],
        competing_yaml_wrappers,
        expected_returncode=1,
    )
    assert_packet_source_ambiguity(
        'competing YAML packet wrappers',
        competing_yaml_result,
    )

    wrapper_with_unrelated_field = (
        'task_packet:\n'
        + indent_yaml(valid_raw_packet, 2)
        + '\nunrelated_fixture_field: unexpected\n'
    )
    unrelated_wrapper_result = run_text_payload_command(
        root,
        [
            'scripts/asgk.py', 'task-packet-check',
            '--file', '{payload}', '--json',
        ],
        wrapper_with_unrelated_field,
        expected_returncode=1,
    )
    assert_packet_source_ambiguity(
        'wrapper plus unrelated top-level field',
        unrelated_wrapper_result,
    )

    yaml_source_cases = [
        (
            'raw-plus-wrapper packet',
            competing_wrapper_packet,
            competing_wrapper_result,
        ),
        (
            'nested packet wrapper',
            nested_wrapper_packet,
            nested_wrapper_result,
        ),
        (
            'wrapper-inside-wrapper',
            wrapper_inside_wrapper_packet,
            wrapper_inside_result,
        ),
        (
            'competing YAML packet wrappers',
            competing_yaml_wrappers,
            competing_yaml_result,
        ),
        (
            'wrapper plus unrelated top-level field',
            wrapper_with_unrelated_field,
            unrelated_wrapper_result,
        ),
    ]
    for label, source, canonical_result in yaml_source_cases:
        compact_result = run_text_payload_command(
            root,
            [
                'scripts/asgk.py', 'compact-task-packet-check',
                '--file', '{payload}', '--json',
            ],
            source,
            expected_returncode=1,
        )
        if canonical_result != compact_result:
            fail(f'{label} must have canonical/compact output parity')
        context_result = run_text_payload_command(
            root,
            [
                'scripts/asgk.py', 'context-budget-measure',
                '--task-packet', '{payload}', '--json',
            ],
            source,
            expected_returncode=1,
        )
        assert_packet_source_ambiguity(
            f'{label} context-budget projection',
            context_result,
        )

    competing_json_wrappers = {
        'bad_input': fallback_packet,
        'task_packet': json.loads(json.dumps(fallback_packet)),
    }
    competing_json_result = run_json_payload_command(
        root,
        [
            'scripts/asgk.py', 'task-packet-check',
            '--file', '{payload}', '--json',
        ],
        competing_json_wrappers,
        expected_returncode=1,
    )
    assert_packet_source_ambiguity(
        'competing JSON packet wrappers',
        competing_json_result,
    )

    json_raw_plus_wrapper = {
        'task_packet': json.loads(json.dumps(fallback_packet)),
        'mode': 'github_unavailable_fallback',
    }
    json_raw_plus_wrapper_result = run_json_payload_command(
        root,
        [
            'scripts/asgk.py', 'task-packet-check',
            '--file', '{payload}', '--json',
        ],
        json_raw_plus_wrapper,
        expected_returncode=1,
    )
    assert_packet_source_ambiguity(
        'JSON raw-plus-wrapper packet',
        json_raw_plus_wrapper_result,
    )
    for label, source, canonical_result in [
        (
            'competing JSON packet wrappers',
            competing_json_wrappers,
            competing_json_result,
        ),
        (
            'JSON raw-plus-wrapper packet',
            json_raw_plus_wrapper,
            json_raw_plus_wrapper_result,
        ),
    ]:
        compact_result = run_json_payload_command(
            root,
            [
                'scripts/asgk.py', 'compact-task-packet-check',
                '--file', '{payload}', '--json',
            ],
            source,
            expected_returncode=1,
        )
        if canonical_result != compact_result:
            fail(f'{label} must have canonical/compact output parity')
        context_result = run_json_payload_command(
            root,
            [
                'scripts/asgk.py', 'context-budget-measure',
                '--task-packet', '{payload}', '--json',
            ],
            source,
            expected_returncode=1,
        )
        assert_packet_source_ambiguity(
            f'{label} context-budget projection',
            context_result,
        )

    for wrapper in ('task_packet', 'bad_input'):
        valid_wrapped_yaml = (
            f'{wrapper}:\n'
            + indent_yaml(valid_raw_packet, 2)
            + '\n'
        )
        canonical_wrapped_result = run_text_payload_command(
            root,
            [
                'scripts/asgk.py', 'task-packet-check',
                '--file', '{payload}', '--json',
            ],
            valid_wrapped_yaml,
            expected_returncode=0,
        )
        compact_wrapped_result = run_text_payload_command(
            root,
            [
                'scripts/asgk.py', 'compact-task-packet-check',
                '--file', '{payload}', '--json',
            ],
            valid_wrapped_yaml,
            expected_returncode=0,
        )
        if canonical_wrapped_result != compact_wrapped_result:
            fail(f'valid YAML {wrapper} wrapper must have compact parity')

        valid_wrapped_json = {
            wrapper: json.loads(json.dumps(fallback_packet)),
            'negative_case': 'valid wrapper compatibility fixture',
        }
        canonical_json_result = run_json_payload_command(
            root,
            [
                'scripts/asgk.py', 'task-packet-check',
                '--file', '{payload}', '--json',
            ],
            valid_wrapped_json,
            expected_returncode=0,
        )
        compact_json_result = run_json_payload_command(
            root,
            [
                'scripts/asgk.py', 'compact-task-packet-check',
                '--file', '{payload}', '--json',
            ],
            valid_wrapped_json,
            expected_returncode=0,
        )
        if canonical_json_result != compact_json_result:
            fail(f'valid JSON {wrapper} wrapper must have compact parity')

    typed_yaml_packet = re.sub(
        r'(?m)^reason:.*$',
        'reason: null',
        valid_raw_packet,
        count=1,
    )
    typed_yaml_packet = re.sub(
        r'(?m)^objective:.*$',
        'objective: true',
        typed_yaml_packet,
        count=1,
    )
    typed_yaml_packet = re.sub(
        r'(?m)^  - "Retry GitHub issue creation before any PR\."$',
        '  - false',
        typed_yaml_packet,
        count=1,
    )
    typed_yaml_result = run_text_payload_command(
        root,
        [
            'scripts/asgk.py', 'task-packet-check',
            '--file', '{payload}', '--json',
        ],
        typed_yaml_packet,
        expected_returncode=1,
    )
    if set(finding_codes(typed_yaml_result)) != {
        'TP_FIELD_TYPE_INVALID',
        'TP_LIST_ITEM_TYPE_INVALID',
    }:
        fail('raw YAML implicit scalar types must match JSON schema types')

    for numeric_token in ('0x10', '0o10', '0b10'):
        base_numeric_packet = re.sub(
            r'(?m)^reason:.*$',
            f'reason: {numeric_token}',
            valid_raw_packet,
            count=1,
        )
        base_numeric_result = run_text_payload_command(
            root,
            [
                'scripts/asgk.py', 'task-packet-check',
                '--file', '{payload}', '--json',
            ],
            base_numeric_packet,
            expected_returncode=1,
        )
        if set(finding_codes(base_numeric_result)) != {
            'TP_FIELD_TYPE_INVALID'
        }:
            fail(
                f'YAML base-prefixed numeric {numeric_token} must retain type'
            )

    unicode_validation_packet = json.loads(json.dumps(fallback_packet))
    unicode_validation_packet['project_specific_validation'] = [
        'not_applicable because 純文件變更'
    ]
    run_json_payload_command(
        root,
        [
            'scripts/asgk.py', 'task-packet-check',
            '--file', '{payload}', '--json',
        ],
        unicode_validation_packet,
        expected_returncode=0,
    )

    refinement_bundle = json.loads(
        read(root, 'examples/compact_governance/task_packet_delta.valid.json')
    )
    competing_bundle_source = json.loads(json.dumps(refinement_bundle))
    competing_bundle_source['mode'] = 'github_unavailable_fallback'
    competing_bundle_source['allowed_paths'] = ['AGENTS.md']
    canonical_bundle_result = run_json_payload_command(
        root,
        [
            'scripts/asgk.py', 'task-packet-check',
            '--json-file', '{payload}', '--json',
        ],
        competing_bundle_source,
        expected_returncode=1,
    )
    compact_bundle_result = run_json_payload_command(
        root,
        [
            'scripts/asgk.py', 'compact-task-packet-check',
            '--json-file', '{payload}', '--json',
        ],
        competing_bundle_source,
        expected_returncode=1,
    )
    assert_packet_source_ambiguity(
        'fixture bundle with competing raw packet fields',
        canonical_bundle_result,
    )
    if canonical_bundle_result != compact_bundle_result:
        fail('competing fixture bundle source must have compact parity')

    refinement_mutations = [
        (
            'task-packet refinement traversal shape',
            ('task_packet', 'allowed_paths'),
            ['scripts/../AGENTS.md'],
            {'TP_ALLOWED_PATH_INVALID'},
        ),
        (
            'task-packet glob containment',
            ('task_packet', 'allowed_paths'),
            ['scripts/*.py'],
            {'TP_ALLOWED_PATH_EXPANSION'},
        ),
        (
            'task-packet read-set case mismatch',
            ('task_packet', 'context_read_set'),
            ['Current GitHub Issue'],
            {'TP_READ_SET_EXPANSION'},
        ),
        (
            'task-packet validation case mismatch',
            ('task_packet', 'project_specific_validation'),
            ['Python3 scripts/asgk.py task-packet-check'],
            {'TP_VALIDATION_EXPANSION'},
        ),
        (
            'task-packet unrelated repository issue URL',
            ('task_packet', 'durable_source_of_truth'),
            'https://github.com/unrelated/repository/issues/1001',
            {'TP_AUTHORITY_MISMATCH'},
        ),
        (
            'task-packet conflicting repository qualifier',
            ('task_packet', 'durable_source_of_truth'),
            'unrelated/repository issue #1001',
            {'TP_AUTHORITY_MISMATCH'},
        ),
    ]
    for label, (parent, field), value, expected_codes in refinement_mutations:
        mutation = json.loads(json.dumps(refinement_bundle))
        if label == 'task-packet read-set case mismatch':
            marker = 'project_specific_validation:\n'
            if marker not in mutation['issue']['body']:
                fail('case-mismatch fixture is missing its insertion point')
            mutation['issue']['body'] = mutation['issue']['body'].replace(
                marker,
                f'  - current GitHub issue\n{marker}',
                1,
            )
        mutation[parent][field] = value
        if label == 'task-packet unrelated repository issue URL':
            mutation['issue']['html_url'] = (
                'https://github.com/stereosurfer/'
                'agent-safe-dev-governance-kit/issues/1001'
            )
        result = assert_mutation(
            label,
            [
                'scripts/asgk.py', 'task-packet-check',
                '--json-file', '{payload}', '--json',
            ],
            mutation,
            expected_codes,
        )
        if label == 'task-packet refinement traversal shape':
            checked = set(result.get('mechanically_checked', []))
            skipped = set(result.get('not_checked', []))
            if 'allowed_paths non-expansion' in checked:
                fail('invalid packet shape must not claim allowed-path comparison')
            if 'allowed_paths non-expansion' not in skipped:
                fail('skipped allowed-path comparison must be disclosed')

    nonexact_source_heading = json.loads(json.dumps(refinement_bundle))
    nonexact_source_heading['issue']['body'] = (
        nonexact_source_heading['issue']['body'].replace(
            '## Required Task Fields',
            '## Required-Task-Fields',
            1,
        )
    )
    nonexact_source_result = assert_mutation(
        'task-packet source issue nonexact canonical heading',
        [
            'scripts/asgk.py', 'task-packet-check',
            '--json-file', '{payload}', '--json',
        ],
        nonexact_source_heading,
        {'TP_ISSUE_TASK_FIELD_AMBIGUOUS'},
    )
    for comparison in (
        'allowed_paths non-expansion',
        'context_read_set exact-item non-expansion',
        'project_specific_validation exact-item non-expansion',
    ):
        if (
            comparison
            in set(nonexact_source_result.get('mechanically_checked', []))
            or comparison
            not in set(nonexact_source_result.get('not_checked', []))
        ):
            fail(
                'nonexact source canonical heading must skip '
                f'{comparison}'
            )

    quoted_source_field_outside_fence = json.loads(
        json.dumps(refinement_bundle)
    )
    quoted_source_field_outside_fence['issue']['body'] = (
        quoted_source_field_outside_fence['issue']['body'].replace(
            '```yaml\n',
            '"allowed_paths":\n'
            '  - AGENTS.md\n\n'
            '```yaml\n',
            1,
        )
    )
    quoted_source_result = assert_mutation(
        'task-packet source issue quoted field outside canonical fence',
        [
            'scripts/asgk.py', 'task-packet-check',
            '--json-file', '{payload}', '--json',
        ],
        quoted_source_field_outside_fence,
        {'TP_ISSUE_TASK_FIELD_AMBIGUOUS'},
    )
    for comparison in (
        'allowed_paths non-expansion',
        'context_read_set exact-item non-expansion',
        'project_specific_validation exact-item non-expansion',
    ):
        if (
            comparison
            in set(quoted_source_result.get('mechanically_checked', []))
            or comparison
            not in set(quoted_source_result.get('not_checked', []))
        ):
            fail(
                'quoted source field outside canonical fence must skip '
                f'{comparison}'
            )

    refinement_pr_source = json.loads(json.dumps(refinement_bundle))
    refinement_pr_source['issue']['html_url'] = (
        'https://github.com/stereosurfer/'
        'agent-safe-dev-governance-kit/pull/1001'
    )
    assert_mutation(
        'task-packet PR payload cannot act as source issue',
        [
            'scripts/asgk.py', 'task-packet-check',
            '--json-file', '{payload}', '--json',
        ],
        refinement_pr_source,
        {'TP_ISSUE_SCOPE_INVALID'},
    )

    live_issue_api_pr_source = json.loads(json.dumps(refinement_bundle))
    live_issue_api_pr_source['issue']['_asgk_requested_kind'] = 'issue'
    live_issue_api_pr_source['issue']['pull_request'] = {
        'url': (
            'https://api.github.com/repos/stereosurfer/'
            'agent-safe-dev-governance-kit/pulls/1001'
        ),
    }
    assert_mutation(
        'task-packet Issues API PR cannot act as source issue',
        [
            'scripts/asgk.py', 'task-packet-check',
            '--json-file', '{payload}', '--json',
        ],
        live_issue_api_pr_source,
        {'TP_ISSUE_SCOPE_INVALID'},
    )

    source_issue_reason_alias = json.loads(json.dumps(refinement_bundle))
    source_issue_reason_alias['issue']['body'] = (
        source_issue_reason_alias['issue']['body'].replace(
            'reason: "Fixture supports task-packet non-expansion checks."',
            'reason: "Fixture supports task-packet non-expansion checks."\n'
            'intelligence_level_reason: "Legacy duplicate reason."',
            1,
        )
    )
    alias_source_result = assert_mutation(
        'task-packet source issue legacy reason alias',
        [
            'scripts/asgk.py', 'task-packet-check',
            '--json-file', '{payload}', '--json',
        ],
        source_issue_reason_alias,
        {'TP_ISSUE_REASON_ALIAS_FORBIDDEN'},
    )
    if (
        'allowed_paths non-expansion'
        in set(alias_source_result.get('mechanically_checked', []))
        or 'allowed_paths non-expansion'
        not in set(alias_source_result.get('not_checked', []))
    ):
        fail('source issue legacy alias must skip non-expansion comparison')

    mixed_source_issue = json.loads(json.dumps(refinement_bundle))
    mixed_source_issue['issue']['body'] += (
        '\n## objective\n\n'
        'A source issue cannot mix task-field representations.\n'
    )
    mixed_source_result = assert_mutation(
        'task-packet mixed source-issue task fields',
        [
            'scripts/asgk.py', 'task-packet-check',
            '--json-file', '{payload}', '--json',
        ],
        mixed_source_issue,
        {'TP_ISSUE_TASK_FIELD_AMBIGUOUS'},
    )
    if (
        'allowed_paths non-expansion'
        in set(mixed_source_result.get('mechanically_checked', []))
        or 'allowed_paths non-expansion'
        not in set(mixed_source_result.get('not_checked', []))
    ):
        fail('ambiguous source issue must disclose skipped non-expansion comparison')

    duplicate_source_key = json.loads(json.dumps(refinement_bundle))
    duplicate_source_key['issue']['body'] = (
        duplicate_source_key['issue']['body'].replace(
            '\n```\n',
            '\nobjective: second candidate\n'
            '```\n',
            1,
        )
    )
    assert_mutation(
        'task-packet duplicate source-issue YAML key',
        [
            'scripts/asgk.py', 'task-packet-check',
            '--json-file', '{payload}', '--json',
        ],
        duplicate_source_key,
        {'TP_ISSUE_TASK_FIELD_AMBIGUOUS'},
    )

    source_issue_chat = json.loads(json.dumps(refinement_bundle))
    source_issue_chat['issue']['body'] = source_issue_chat['issue']['body'].replace(
        'reason: "Fixture supports task-packet non-expansion checks."',
        'reason: "see chat"',
        1,
    )
    invalid_issue_result = assert_mutation(
        'task-packet invalid source issue chat authority',
        [
            'scripts/asgk.py', 'task-packet-check',
            '--json-file', '{payload}', '--json',
        ],
        source_issue_chat,
        {'TP_ISSUE_CHAT_AUTHORITY_FORBIDDEN'},
    )
    if (
        'allowed_paths non-expansion'
        in set(invalid_issue_result.get('mechanically_checked', []))
        or 'allowed_paths non-expansion'
        not in set(invalid_issue_result.get('not_checked', []))
    ):
        fail('invalid source issue must disclose skipped non-expansion comparison')

    source_issue_mutations = [
        (
            'task-packet source issue traversal path',
            'allowed_paths',
            ['docs/../README.md'],
            {'TP_ISSUE_ALLOWED_PATH_INVALID'},
        ),
        (
            'task-packet source issue overbroad read set',
            'context_read_set',
            ['entire repo'],
            {'TP_ISSUE_READ_SET_OVERBROAD'},
        ),
        (
            'task-packet source issue invalid prose read set',
            'context_read_set',
            ['read the relevant files'],
            {'TP_ISSUE_READ_SET_INVALID'},
        ),
        (
            'task-packet source issue bare not_applicable validation',
            'project_specific_validation',
            ['not_applicable'],
            {'TP_ISSUE_PROJECT_VALIDATION_REASON_MISSING'},
        ),
    ]
    for label, field, values, expected_codes in source_issue_mutations:
        mutation = json.loads(json.dumps(refinement_bundle))
        mutation['issue']['body'] = replace_list_field(
            mutation['issue']['body'],
            field,
            values,
        )
        assert_mutation(
            label,
            [
                'scripts/asgk.py', 'task-packet-check',
                '--json-file', '{payload}', '--json',
            ],
            mutation,
            expected_codes,
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        temporary_root = Path(tmpdir) / 'repo'
        temporary_root.mkdir()
        outside = Path(tmpdir) / 'outside.txt'
        outside.write_text('outside', encoding='utf-8')
        (temporary_root / 'escape.txt').symlink_to(outside)
        symlink_packet = json.loads(json.dumps(fallback_packet))
        symlink_packet['context_read_set'] = ['escape.txt']
        symlink_result, symlink_output = evaluate_task_packet(
            symlink_packet,
            json.dumps(symlink_packet, sort_keys=True),
            repo_root=temporary_root,
        )
        if (
            symlink_result != 'fail'
            or set(finding_codes(symlink_output))
            != {'TP_READ_SET_OUTSIDE_REPO'}
        ):
            fail('task-packet context symlink escape must fail with exact code')

def check_w3b_handoff_projection(root):
    schema = json.loads(read(root, 'schemas/handoff_packet.schema.json'))
    expected_schema_id = (
        'https://github.com/stereosurfer/'
        'agent-safe-dev-governance-kit/schemas/handoff_packet.schema.json'
    )
    if schema.get('$id') != expected_schema_id:
        fail('handoff schema id must use the canonical repository URL')
    if schema.get('unevaluatedProperties') is not False:
        fail('handoff schema must reject unknown top-level siblings')
    for metadata_root in ['positive_case', 'negative_case']:
        if schema.get('properties', {}).get(metadata_root, {}).get('type') != 'object':
            fail(f'handoff schema {metadata_root} metadata must be an object')

    definitions = schema.get('$defs', {})
    core_schema = definitions.get('core', {})
    if set(core_schema.get('required', [])) != set(CORE_REQUIRED_FIELDS):
        fail('handoff schema core required fields drifted from the evaluator')
    if set(core_schema.get('properties', {})) != set(CORE_REQUIRED_FIELDS):
        fail('handoff schema core properties drifted from the evaluator')
    for removed in {'completed', 'decisions', 'open_questions'}:
        if removed in core_schema.get('properties', {}):
            fail(f'handoff schema retained duplicate history field: {removed}')

    validation_schema = definitions.get('validationStatus', {})
    if set(validation_schema.get('required', [])) != set(VALIDATION_STATUS_FIELDS):
        fail('handoff schema validation_status required fields drifted')
    status_values = (
        validation_schema.get('properties', {})
        .get('status', {})
        .get('enum', [])
    )
    if set(status_values) != set(VALIDATION_STATUS_VALUES):
        fail('handoff schema validation status enum drifted')
    if validation_schema.get('additionalProperties') is not False:
        fail('handoff validation_status must reject unknown nested fields')
    impact_schema = definitions.get('currentStatusImpact', {})
    follow_up_schema = (
        impact_schema.get('properties', {})
        .get('follow_up_issue', {})
    )
    if follow_up_schema.get('pattern') != FOLLOW_UP_ISSUE_PATTERN:
        fail('handoff schema/evaluator follow-up issue shape drifted')
    material_schema = definitions.get('materialString', {})
    material_exclusions = material_schema.get('not', {}).get('anyOf', [])
    non_material_pattern = next(
        (
            item.get('pattern')
            for item in material_exclusions
            if isinstance(item, dict)
            and item.get('pattern', '').startswith('^\\s*')
        ),
        None,
    )
    if not non_material_pattern:
        fail('handoff schema material strings must reject generic placeholders')
    if not any(
        item.get('pattern') == FORBIDDEN_HANDOFF_CHARACTER_PATTERN_SOURCE
        for item in material_exclusions
        if isinstance(item, dict)
    ):
        fail('handoff schema material strings must reject zero-width format characters')
    compiled_non_material = re.compile(non_material_pattern)
    compiled_forbidden_format = re.compile(
        FORBIDDEN_HANDOFF_CHARACTER_PATTERN_SOURCE
    )
    for sample in [
        'pending',
        'unknown.',
        'none',
        'n...a',
        'not\tapplicable',
        'not\napplicable',
        'not _applicable',
        'not__applicable',
        'not ._ applicable',
        'none?',
        'unKnown',
        '\u00a0pending\u00a0',
        'not\u00a0applicable',
        '\u2003none\u2003',
        '\u200b',
        '\u202e',
        '\u2061',
        '\u180e',
        '\u0080',
        '\ud800',
        'none; no known blocker',
        'not applicable because this packet has no target PR',
    ]:
        evaluator_accepts = is_material_handoff_text(sample)
        schema_accepts = (
            compiled_non_material.search(sample) is None
            and compiled_forbidden_format.search(sample) is None
            and re.search(r'\S', sample) is not None
        )
        if evaluator_accepts != schema_accepts:
            fail(
                'handoff schema/evaluator material-string parity drifted for '
                f'{sample!r}'
            )

    roots = {
        root_name
        for option in schema.get('oneOf', [])
        for root_name in option.get('properties', {})
    }
    if roots != {CORE_HANDOFF_ROOT, COMPACT_HANDOFF_ROOT}:
        fail(f'handoff schema root projections drifted: {sorted(roots)}')
    for option in schema.get('oneOf', []):
        required_root = next(iter(option.get('required', [])), None)
        other_root = (
            COMPACT_HANDOFF_ROOT
            if required_root == CORE_HANDOFF_ROOT
            else CORE_HANDOFF_ROOT
        )
        if other_root not in option.get('not', {}).get('required', []):
            fail('handoff schema alternatives must explicitly reject the other root')
        for root_schema in option.get('properties', {}).values():
            if root_schema.get('unevaluatedProperties') is not False:
                fail('handoff schema projections must reject unknown core fields')

    positive = run_json_command(
        root,
        [
            'scripts/asgk.py', 'handoff-check',
            '--file', 'examples/handoff_packet.valid.yaml',
            '--fail-on-todo', '--json',
        ],
        expected_returncode=0,
        label='valid typed handoff',
    )
    if positive.get('result') != 'pass' or positive.get('findings') != []:
        fail('valid handoff must pass without findings')
    proof_boundary = str(positive.get('proof_boundary', ''))
    for term in ['does not prove', 'human gate', 'merge decision']:
        if term not in proof_boundary.lower():
            fail(f'handoff proof boundary missing limit: {term}')

    template_result = subprocess.run(
        [
            sys.executable,
            'scripts/asgk.py',
            'handoff-template',
            '--issue',
            '#333',
            '--pr',
            'none; PR not opened yet',
            '--branch',
            'codex/example',
            '--objective',
            'Exercise the draft template.',
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if template_result.returncode != 0:
        fail('handoff-template must emit a draft successfully')
    durable_source_block = '\n'.join(
        field_block_lines(
            template_result.stdout,
            'durable_source_of_truth',
        )
        or []
    )
    if 'none; PR not opened yet' in durable_source_block:
        fail('handoff-template must not treat a nonexistent PR as a durable source')
    template_check = run_text_payload_command(
        root,
        [
            'scripts/asgk.py', 'handoff-check',
            '--file', '{payload}', '--json',
        ],
        template_result.stdout,
        expected_returncode=1,
    )
    if set(finding_codes(template_check)) != {'HP_TODO_UNRESOLVED'}:
        fail('unfilled handoff-template output must fail TODO checking by default')

    template_control_result = subprocess.run(
        [
            sys.executable,
            'scripts/asgk.py',
            'handoff-template',
            '--issue',
            '#333\tW3B',
            '--pr',
            'none; PR not opened yet',
            '--branch',
            'codex/example',
            '--objective',
            'First line\nsecond line',
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if template_control_result.returncode != 0:
        fail('handoff-template must quote control whitespace safely')
    template_control_check = run_text_payload_command(
        root,
        [
            'scripts/asgk.py', 'handoff-check',
            '--file', '{payload}', '--json',
        ],
        template_control_result.stdout,
        expected_returncode=1,
    )
    if set(finding_codes(template_control_check)) != {'HP_TODO_UNRESOLVED'}:
        fail('handoff-template output with escaped whitespace must remain parseable')

    negative_cases = [
        (
            'wrong handoff root',
            'examples/negative/handoff.wrong-root.yaml',
            False,
            {'HP_PACKET_ROOT_MISSING'},
        ),
        (
            'missing active issue',
            'examples/negative/handoff.missing-active-issue.yaml',
            False,
            {'HP_FIELD_MISSING'},
        ),
        (
            'empty next safe action',
            'examples/negative/handoff.empty-next-safe-action.yaml',
            False,
            {'HP_FIELD_EMPTY'},
        ),
        (
            'invalid validation status',
            'examples/negative/handoff.unknown-validation-status.yaml',
            False,
            {'HP_VALIDATION_STATUS_INVALID'},
        ),
        (
            'missing allowed paths',
            'examples/negative/handoff.missing-allowed-paths.yaml',
            False,
            {'HP_FIELD_MISSING'},
        ),
        (
            'missing must read',
            'examples/negative/handoff.missing-must-read.yaml',
            False,
            {'HP_FIELD_MISSING'},
        ),
        (
            'scalar required list',
            'examples/negative/handoff.scalar-required-list.yaml',
            False,
            {'HP_FIELD_TYPE_INVALID'},
        ),
        (
            'scalar validation evidence',
            'examples/negative/handoff.invalid-validation-evidence.yaml',
            False,
            {'HP_FIELD_TYPE_INVALID'},
        ),
        (
            'unresolved TODO',
            'examples/negative/handoff.unresolved-todo.yaml',
            True,
            {'HP_TODO_UNRESOLVED'},
        ),
    ]
    for label, fixture, fail_on_todo, expected_codes in negative_cases:
        command = [
            'scripts/asgk.py', 'handoff-check',
            '--file', fixture,
            '--json',
        ]
        if fail_on_todo:
            command.insert(-1, '--fail-on-todo')
        payload = run_json_command(
            root,
            command,
            expected_returncode=1,
            label=label,
        )
        actual_codes = set(finding_codes(payload))
        if actual_codes != expected_codes:
            fail(
                f'{label} finding codes {sorted(actual_codes)} != '
                f'{sorted(expected_codes)}'
            )
        if label == 'wrong handoff root':
            checked = payload.get('mechanically_checked', [])
            not_checked = payload.get('not_checked', [])
            if any('required core field' in item for item in checked):
                fail('wrong-root handoff must not claim core fields were checked')
            if not any('required core fields' in item for item in not_checked):
                fail('wrong-root handoff must name skipped core checks')

    valid_handoff_text = read(root, 'examples/handoff_packet.valid.yaml')
    mutation_cases = [
        (
            'boolean scalar type',
            valid_handoff_text.replace(
                '  branch: "codex/asgk-2-w3b-handoff-status-convergence"',
                '  branch: true',
                1,
            ),
            {'HP_FIELD_TYPE_INVALID'},
        ),
        (
            'duplicate packet key',
            valid_handoff_text.replace(
                'handoff_packet:\n',
                'handoff_packet:\n  active_issue: "#duplicate"\n',
                1,
            ),
            {'HP_PACKET_AMBIGUOUS'},
        ),
        (
            'removed history field',
            valid_handoff_text.replace(
                '  next_safe_action:',
                '  completed:\n    - "old duplicate history"\n  next_safe_action:',
                1,
            ),
            {'HP_FIELD_UNKNOWN'},
        ),
        (
            'missing validation reason',
            re.sub(
                r'(?m)^    reason: "The fixture describes the pre-validation state\."\n',
                '',
                valid_handoff_text,
                count=1,
            ),
            {'HP_FIELD_MISSING'},
        ),
        (
            'missing validation status',
            re.sub(
                r'(?m)^    status: "not_run"\n',
                '',
                valid_handoff_text,
                count=1,
            ),
            {'HP_FIELD_MISSING'},
        ),
        (
            'packet root has scalar type',
            'handoff_packet: true\n',
            {'HP_PACKET_TYPE_INVALID'},
        ),
        (
            'unsupported top-level authority sibling',
            valid_handoff_text
            + '\nauthority_override: "see chat"\n',
            {'HP_PACKET_AMBIGUOUS'},
        ),
        (
            'scalar fixture metadata',
            re.sub(
                r'\Apositive_case:\n(?:  .+\n)+\n',
                'positive_case: invalid\n\n',
                valid_handoff_text,
                count=1,
            ),
            {'HP_PACKET_AMBIGUOUS'},
        ),
        (
            'competing handoff roots',
            valid_handoff_text + '\ncompact_handoff: {}\n',
            {'HP_PACKET_AMBIGUOUS'},
        ),
        (
            'chat-only authority',
            valid_handoff_text.replace(
                '  objective: "Prove the canonical typed handoff core and fixture agree."',
                '  objective: "see chat"',
                1,
            ),
            {'HP_CHAT_AUTHORITY_FORBIDDEN'},
        ),
        (
            'tab-separated chat-only authority',
            valid_handoff_text.replace(
                '  objective: "Prove the canonical typed handoff core and fixture agree."',
                '  objective: "see\\tchat"',
                1,
            ),
            {'HP_CHAT_AUTHORITY_FORBIDDEN'},
        ),
        (
            'newline-separated chat-only authority',
            valid_handoff_text.replace(
                '  objective: "Prove the canonical typed handoff core and fixture agree."',
                '  objective: "see\\nchat"',
                1,
            ),
            {'HP_CHAT_AUTHORITY_FORBIDDEN'},
        ),
        (
            'lowercase unresolved marker',
            valid_handoff_text.replace(
                '  objective: "Prove the canonical typed handoff core and fixture agree."',
                '  objective: "todo: fill this later"',
                1,
            ),
            {'HP_TODO_UNRESOLVED'},
        ),
        (
            'identifier-style unresolved marker',
            valid_handoff_text.replace(
                '  objective: "Prove the canonical typed handoff core and fixture agree."',
                '  objective: "AI_TODO_value"',
                1,
            ),
            {'HP_TODO_UNRESOLVED'},
        ),
        (
            'generic next-action placeholder',
            re.sub(
                r'(?m)^  next_safe_action: .*$',
                '  next_safe_action: "pending."',
                valid_handoff_text,
                count=1,
            ),
            {'HP_FIELD_EMPTY'},
        ),
        (
            'generic list placeholder',
            valid_handoff_text.replace(
                '    - "none; no known blocker in this fixture"',
                '    - "none."',
                1,
            ),
            {'HP_FIELD_EMPTY'},
        ),
        (
            'generic evidence placeholder',
            valid_handoff_text.replace(
                '      - "This fixture is the input to the validation command."',
                '      - "unknown"',
                1,
            ),
            {'HP_FIELD_EMPTY'},
        ),
        (
            'zero-width-only material',
            valid_handoff_text.replace(
                '  objective: "Prove the canonical typed handoff core and fixture agree."',
                '  objective: "\\u200b"',
                1,
            ),
            {'HP_FIELD_EMPTY'},
        ),
        (
            'bidi-format-only material',
            valid_handoff_text.replace(
                '  objective: "Prove the canonical typed handoff core and fixture agree."',
                '  objective: "\\u202e"',
                1,
            ),
            {'HP_FIELD_EMPTY'},
        ),
        (
            'escaped control character',
            valid_handoff_text.replace(
                '  active_issue: "#333 ASGK 2.0 W3B"',
                '  active_issue: "issue \\u0000 333"',
                1,
            ),
            {'HP_PACKET_AMBIGUOUS'},
        ),
        (
            'escaped lone surrogate',
            valid_handoff_text.replace(
                '  active_issue: "#333 ASGK 2.0 W3B"',
                '  active_issue: "\\ud800"',
                1,
            ),
            {'HP_PACKET_AMBIGUOUS'},
        ),
    ]
    for label, source, expected_codes in mutation_cases:
        payload = run_text_payload_command(
            root,
            [
                'scripts/asgk.py', 'handoff-check',
                '--file', '{payload}', '--json',
            ],
            source,
            expected_returncode=1,
        )
        if set(finding_codes(payload)) != expected_codes:
            fail(f'{label} must fail with exact handoff finding code')

    branch_line = '  branch: "codex/asgk-2-w3b-handoff-status-convergence"'
    for label, scalar in [
        ('inline YAML comment', 'true # actually a YAML boolean'),
        ('explicit YAML tag', '!!int 7'),
        ('YAML anchor', '&branch codex/example'),
        ('forbidden YAML indicator', '@not-valid-yaml'),
        ('exact sequence indicator', '-'),
        ('trailing mapping colon', 'invalid:'),
        ('concatenated quoted literals', '"first" "second"'),
        ('flow-style scalar', '[one, two]'),
        ('raw control character', 'material\x00value'),
        ('raw C1 control character', 'material\u0080value'),
    ]:
        payload = run_text_payload_command(
            root,
            [
                'scripts/asgk.py', 'handoff-check',
                '--file', '{payload}', '--json',
            ],
            valid_handoff_text.replace(
                branch_line,
                f'  branch: {scalar}',
                1,
            ),
            expected_returncode=1,
        )
        if set(finding_codes(payload)) != {'HP_PACKET_AMBIGUOUS'}:
            fail(f'{label} must fail closed as ambiguous YAML')

    for label, scalar in [
        ('scientific number', '1e3'),
        ('YAML timestamp', '2026-07-31'),
    ]:
        payload = run_text_payload_command(
            root,
            [
                'scripts/asgk.py', 'handoff-check',
                '--file', '{payload}', '--json',
            ],
            valid_handoff_text.replace(
                branch_line,
                f'  branch: {scalar}',
                1,
            ),
            expected_returncode=1,
        )
        if set(finding_codes(payload)) != {'HP_FIELD_TYPE_INVALID'}:
            fail(f'{label} must not pass as a string')

    yaml_single_quote = valid_handoff_text.replace(
        '  objective: "Prove the canonical typed handoff core and fixture agree."',
        "  objective: 'Prove the agent''s handoff remains material.'",
        1,
    )
    run_text_payload_command(
        root,
        [
            'scripts/asgk.py', 'handoff-check',
            '--file', '{payload}', '--json',
        ],
        yaml_single_quote,
        expected_returncode=0,
    )

    missing_handoff = run_json_command(
        root,
        [
            'scripts/asgk.py', 'handoff-check',
            '--file', 'examples/negative/does-not-exist.yaml',
            '--json',
        ],
        expected_returncode=1,
        label='missing handoff file',
    )
    if set(finding_codes(missing_handoff)) != {'HP_FILE_MISSING'}:
        fail('missing handoff file must report HP_FILE_MISSING')

    unreadable_handoff = run_json_command(
        root,
        [
            'scripts/asgk.py', 'handoff-check',
            '--file', '.',
            '--json',
        ],
        expected_returncode=1,
        label='handoff path is a directory',
    )
    if set(finding_codes(unreadable_handoff)) != {'HP_FILE_UNREADABLE'}:
        fail('non-file handoff path must report HP_FILE_UNREADABLE')

    empty_lists = run_json_command(
        root,
        [
            'scripts/asgk.py', 'handoff-check',
            '--file', 'examples/negative/handoff.empty-required-lists.yaml',
            '--json',
        ],
        expected_returncode=1,
        label='empty required handoff lists',
    )
    if set(finding_codes(empty_lists)) != {
        'HP_LIST_EMPTY',
        'HP_VALIDATION_EVIDENCE_MISSING',
    }:
        fail('empty required handoff lists must report exact list/evidence codes')

    compact_positive = run_json_command(
        root,
        [
            'scripts/asgk.py', 'compact-handoff-check',
            '--handoff', 'examples/compact_governance/handoff.compact.valid.yaml',
            '--current-status',
            'examples/compact_governance/current_status.compact.clean.md',
            '--json',
        ],
        expected_returncode=0,
        label='valid compact handoff',
    )
    if (
        compact_positive.get('result') != 'pass'
        or compact_positive.get('freshness_checked') is not True
        or compact_positive.get('findings') != []
    ):
        fail('valid compact handoff must run and pass core plus freshness checks')

    valid_compact_text = read(
        root,
        'examples/compact_governance/handoff.compact.valid.yaml',
    )
    impact_block_pattern = (
        r'(?m)^  current_status_impact:\n'
        r'(?:    .*\n?)+'
    )
    impact_mutations = [
        (
            'missing compact impact',
            re.sub(
                impact_block_pattern,
                '',
                valid_compact_text,
                count=1,
            ),
            {'CH_CURRENT_STATUS_IMPACT_MISSING'},
        ),
        (
            'missing compact impact field',
            re.sub(
                r'(?m)^    reason: "The supplied clean status fixture.*"\n',
                '',
                valid_compact_text,
                count=1,
            ),
            {'CH_CURRENT_STATUS_IMPACT_FIELD_MISSING'},
        ),
        (
            'invalid compact impact status',
            valid_compact_text.replace(
                '    status: "not_applicable"',
                '    status: "banana"',
                1,
            ),
            {'CH_CURRENT_STATUS_IMPACT_STATUS_INVALID'},
        ),
        (
            'generic compact impact reason',
            re.sub(
                r'(?m)^    reason: "The supplied clean status fixture.*"$',
                '    reason: "not applicable"',
                valid_compact_text,
                count=1,
            ),
            {'CH_CURRENT_STATUS_IMPACT_REASON_INVALID'},
        ),
        (
            'invalid compact impact boolean',
            valid_compact_text.replace(
                '    current_status_updated_in_this_pr: false',
                '    current_status_updated_in_this_pr: "false"',
                1,
            ),
            {'CH_CURRENT_STATUS_IMPACT_FIELD_INVALID'},
        ),
        (
            'inconsistent compact impact',
            valid_compact_text.replace(
                '    status: "not_applicable"',
                '    status: "updated"',
                1,
            ),
            {'CH_CURRENT_STATUS_IMPACT_INCONSISTENT'},
        ),
        (
            'unknown compact impact field',
            valid_compact_text.replace(
                '  current_status_impact:\n',
                '  current_status_impact:\n    extra_gate: true\n',
                1,
            ),
            {'CH_CURRENT_STATUS_IMPACT_FIELD_INVALID'},
        ),
        (
            'invalid compact follow-up issue',
            valid_compact_text.replace(
                '    follow_up_issue: "none"',
                '    follow_up_issue: "pending"',
                1,
            ),
            {'CH_CURRENT_STATUS_IMPACT_FIELD_INVALID'},
        ),
        (
            'newline compact follow-up issue',
            valid_compact_text.replace(
                '    follow_up_issue: "none"',
                '    follow_up_issue: "none\\n"',
                1,
            ),
            {'CH_CURRENT_STATUS_IMPACT_FIELD_INVALID'},
        ),
        (
            'line-separator compact follow-up issue',
            valid_compact_text.replace(
                '    follow_up_issue: "none"',
                '    follow_up_issue: "none\\u2028"',
                1,
            ),
            {'CH_CURRENT_STATUS_IMPACT_FIELD_INVALID'},
        ),
    ]
    for label, source, expected_codes in impact_mutations:
        payload = run_text_payload_command(
            root,
            [
                'scripts/asgk.py', 'compact-handoff-check',
                '--handoff', '{payload}',
                '--current-status', 'examples/negative/does-not-exist.md',
                '--json',
            ],
            source,
            expected_returncode=1,
        )
        if (
            set(finding_codes(payload)) != expected_codes
            or payload.get('freshness_checked') is not False
        ):
            fail(f'{label} must stop before freshness with exact CH code')

    compact_invalid_core = run_json_command(
        root,
        [
            'scripts/asgk.py', 'compact-handoff-check',
            '--handoff',
            'examples/negative/compact_governance/handoff.compact.invalid-core.yaml',
            '--current-status', 'examples/negative/does-not-exist.md',
            '--json',
        ],
        expected_returncode=1,
        label='compact invalid core',
    )
    if (
        set(finding_codes(compact_invalid_core)) != {'HP_FIELD_TYPE_INVALID'}
        or compact_invalid_core.get('freshness_checked') is not False
    ):
        fail('compact invalid core must preserve HP finding and skip freshness')

    compact_missing_status = run_json_command(
        root,
        [
            'scripts/asgk.py', 'compact-handoff-check',
            '--handoff', 'examples/compact_governance/handoff.compact.valid.yaml',
            '--current-status', 'examples/negative/does-not-exist.md',
            '--json',
        ],
        expected_returncode=1,
        label='compact missing current status',
    )
    if (
        set(finding_codes(compact_missing_status))
        != {'CH_CURRENT_STATUS_FILE_MISSING'}
        or compact_missing_status.get('freshness_checked') is not False
    ):
        fail('missing CURRENT_STATUS must stop with exact file finding')

    compact_unreadable_status = run_json_command(
        root,
        [
            'scripts/asgk.py', 'compact-handoff-check',
            '--handoff', 'examples/compact_governance/handoff.compact.valid.yaml',
            '--current-status', '.',
            '--json',
        ],
        expected_returncode=1,
        label='compact current status path is a directory',
    )
    if (
        set(finding_codes(compact_unreadable_status))
        != {'CH_CURRENT_STATUS_CHECK_FAILED'}
        or compact_unreadable_status.get('freshness_checked') is not False
    ):
        fail('non-file CURRENT_STATUS path must fail without overstating freshness')

    closeout_unreadable = subprocess.run(
        [
            sys.executable,
            'scripts/asgk.py',
            'closeout-check',
            '--file',
            '.',
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if (
        closeout_unreadable.returncode != 1
        or 'not a readable file' not in closeout_unreadable.stdout
        or 'Traceback' in closeout_unreadable.stdout
        or 'Traceback' in closeout_unreadable.stderr
    ):
        fail('closeout-check must bound non-file status input without traceback')

    def compact_with_status_text(
        label,
        status_source,
        *,
        completed_issues=(),
        completed_prs=(),
        completed_branches=(),
        expected_returncode,
    ):
        with tempfile.TemporaryDirectory() as tmpdir:
            status_path = Path(tmpdir) / 'CURRENT_STATUS.md'
            status_path.write_text(status_source, encoding='utf-8')
            command = [
                'scripts/asgk.py', 'compact-handoff-check',
                '--handoff',
                'examples/compact_governance/handoff.compact.valid.yaml',
                '--current-status',
                str(status_path),
            ]
            for issue in completed_issues:
                command.extend(['--completed-issue', issue])
            for pr in completed_prs:
                command.extend(['--completed-pr', pr])
            for branch in completed_branches:
                command.extend(['--completed-branch', branch])
            command.append('--json')
            return run_json_command(
                root,
                command,
                expected_returncode=expected_returncode,
                label=label,
            )

    compact_empty_status = compact_with_status_text(
        'compact empty current status',
        '',
        expected_returncode=1,
    )
    if (
        set(finding_codes(compact_empty_status))
        != {'CH_CURRENT_STATUS_CHECK_FAILED'}
        or compact_empty_status.get('freshness_checked') is not False
    ):
        fail('empty CURRENT_STATUS must fail structural status-check exactly')

    compact_stale = run_json_command(
        root,
        [
            'scripts/asgk.py', 'compact-handoff-check',
            '--handoff',
            'examples/negative/compact_governance/handoff.compact.hides-stale-current-status.yaml',
            '--current-status',
            'examples/negative/compact_governance/current_status.compact.stale-active.md',
            '--completed-issue', '#240',
            '--completed-pr', '#241',
            '--completed-branch', 'codex/compact-pr-body-profile-240',
            '--json',
        ],
        expected_returncode=1,
        label='compact stale current status',
    )
    if set(finding_codes(compact_stale)) != {
        'CH_STALE_COMPLETED_ISSUE',
        'CH_STALE_COMPLETED_PR',
        'CH_STALE_COMPLETED_BRANCH',
    }:
        fail('compact stale status must report exact supplied-ref freshness codes')

    compact_prefix_refs = run_json_command(
        root,
        [
            'scripts/asgk.py', 'compact-handoff-check',
            '--handoff',
            'examples/negative/compact_governance/handoff.compact.hides-stale-current-status.yaml',
            '--current-status',
            'examples/negative/compact_governance/current_status.compact.stale-active.md',
            '--completed-issue', '#24',
            '--completed-pr', '#24',
            '--completed-branch', 'codex/compact-pr-body-profile-24',
            '--json',
        ],
        expected_returncode=0,
        label='compact non-matching prefix refs',
    )
    if compact_prefix_refs.get('findings') != []:
        fail('compact freshness must not match caller refs by substring prefix')

    stale_status_text = read(
        root,
        'examples/negative/compact_governance/current_status.compact.stale-active.md',
    )
    url_status_text = stale_status_text.replace(
        'issue: "#240 Add compact PR body profile"',
        (
            'issue: "https://github.com/stereosurfer/'
            'agent-safe-dev-governance-kit/issues/240"'
        ),
        1,
    ).replace(
        'pr: "#241 Add compact PR body profile check"',
        (
            'pr: "https://github.com/stereosurfer/'
            'agent-safe-dev-governance-kit/pull/241"'
        ),
        1,
    )
    compact_url_refs = compact_with_status_text(
        'compact GitHub URL completed refs',
        url_status_text,
        completed_issues=('#240',),
        completed_prs=('#241',),
        expected_returncode=1,
    )
    if set(finding_codes(compact_url_refs)) != {
        'CH_STALE_COMPLETED_ISSUE',
        'CH_STALE_COMPLETED_PR',
    }:
        fail('compact freshness must normalize GitHub URL issue and PR refs')

    url_with_secondary_hash = url_status_text.replace(
        'issues/240"',
        'issues/240 supersedes #24"',
        1,
    )
    compact_url_precedence = compact_with_status_text(
        'compact leading GitHub URL ref precedence',
        url_with_secondary_hash,
        completed_issues=('#24',),
        expected_returncode=0,
    )
    if compact_url_precedence.get('findings') != []:
        fail('compact freshness must use the leading canonical ref only')

    compact_leading_zero_ref = compact_with_status_text(
        'compact numeric ref leading-zero normalization',
        stale_status_text,
        completed_issues=('#0240',),
        expected_returncode=1,
    )
    if set(finding_codes(compact_leading_zero_ref)) != {
        'CH_STALE_COMPLETED_ISSUE'
    }:
        fail('compact freshness must compare issue numbers numerically')

    clean_status_text = read(
        root,
        'examples/compact_governance/current_status.compact.clean.md',
    )
    premerge_status_text = re.sub(
        r'(?ms)(^## Next safe action\n\n).*',
        r'\1Merge only if checks pass.\n',
        clean_status_text,
        count=1,
    )
    compact_premerge_action = compact_with_status_text(
        'compact pre-merge next action',
        premerge_status_text,
        expected_returncode=1,
    )
    if set(finding_codes(compact_premerge_action)) != {
        'CH_NEXT_SAFE_ACTION_STALE'
    }:
        fail('compact freshness must identify pre-merge next-action residue')

    status_result = subprocess.run(
        [
            sys.executable,
            'scripts/asgk.py',
            'status-check',
            '--file',
            'docs/handoff/CURRENT_STATUS.md',
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if status_result.returncode != 0:
        fail(f'canonical CURRENT_STATUS failed status-check: {status_result.stdout}')

    closeout_prefix = subprocess.run(
        [
            sys.executable,
            'scripts/asgk.py',
            'closeout-check',
            '--file',
            'examples/negative/compact_governance/current_status.compact.stale-active.md',
            '--completed-issue',
            '#24',
            '--completed-pr',
            '#24',
            '--completed-branch',
            'codex/compact-pr-body-profile-24',
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if closeout_prefix.returncode != 0:
        fail('closeout-check must not match completed refs by substring prefix')

    closeout_exact = subprocess.run(
        [
            sys.executable,
            'scripts/asgk.py',
            'closeout-check',
            '--file',
            'examples/negative/compact_governance/current_status.compact.stale-active.md',
            '--completed-issue',
            '#0240',
            '--completed-pr',
            '#0241',
            '--completed-branch',
            'codex/compact-pr-body-profile-240',
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if (
        closeout_exact.returncode != 1
        or closeout_exact.stdout.count('still appears in active work') != 3
    ):
        fail('closeout-check must share exact completed-ref semantics')

    with tempfile.TemporaryDirectory() as tmpdir:
        changed_none = Path(tmpdir) / 'changed-none.txt'
        changed_status = Path(tmpdir) / 'changed-status.txt'
        changed_none.write_text('', encoding='utf-8')
        changed_status.write_text(
            'docs/handoff/CURRENT_STATUS.md\n',
            encoding='utf-8',
        )
        impact_body = Path(tmpdir) / 'pr-body.md'
        impact_body.write_text(
            '## Current Status Impact\n\n'
            'status: not_applicable\n'
            'reason: Recovery state is unchanged.\n'
            'current_status_updated_in_this_pr: false\n'
            'post_merge_safe: not_applicable\n'
            'follow_up_issue: pending\n',
            encoding='utf-8',
        )
        invalid_follow_up = subprocess.run(
            [
                sys.executable,
                'scripts/asgk.py',
                'current-status-impact-check',
                '--pr-body',
                str(impact_body),
                '--changed-paths-file',
                str(changed_none),
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if (
            invalid_follow_up.returncode != 1
            or 'follow_up_issue must be exactly none or one #<number>' not in invalid_follow_up.stdout
        ):
            fail('current-status-impact-check must enforce canonical follow-up issue shape')

        impact_body.write_text(
            '## Current Status Impact\n\n'
            'status: not_applicable\n'
            'reason: Recovery state is unchanged.\n'
            'current_status_updated_in_this_pr: false\n'
            'post_merge_safe: not_applicable\n'
            'follow_up_issue: NONE\n',
            encoding='utf-8',
        )
        uppercase_follow_up = subprocess.run(
            [
                sys.executable,
                'scripts/asgk.py',
                'current-status-impact-check',
                '--pr-body',
                str(impact_body),
                '--changed-paths-file',
                str(changed_none),
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if uppercase_follow_up.returncode != 1:
            fail('current-status-impact-check must enforce exact follow-up issue case')

        for malformed_follow_up in ['none"', '"none', '"\'none\'"']:
            impact_body.write_text(
                '## Current Status Impact\n\n'
                'status: not_applicable\n'
                'reason: Recovery state is unchanged.\n'
                'current_status_updated_in_this_pr: false\n'
                'post_merge_safe: not_applicable\n'
                f'follow_up_issue: {malformed_follow_up}\n',
                encoding='utf-8',
            )
            malformed_follow_up_result = subprocess.run(
                [
                    sys.executable,
                    'scripts/asgk.py',
                    'current-status-impact-check',
                    '--pr-body',
                    str(impact_body),
                    '--changed-paths-file',
                    str(changed_none),
                ],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
            )
            if malformed_follow_up_result.returncode != 1:
                fail('current-status-impact-check must reject malformed quote layers')

        impact_body.write_text(
            '## Current Status Impact\n\n'
            'status: "not_applicable"\n'
            'reason: Recovery state is unchanged.\n'
            'current_status_updated_in_this_pr: false\n'
            'post_merge_safe: "not_applicable"\n'
            'follow_up_issue: "none"\n',
            encoding='utf-8',
        )
        quoted_string_impact = subprocess.run(
            [
                sys.executable,
                'scripts/asgk.py',
                'current-status-impact-check',
                '--pr-body',
                str(impact_body),
                '--changed-paths-file',
                str(changed_none),
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if quoted_string_impact.returncode != 0:
            fail('current-status-impact-check must accept one balanced quote layer')

        impact_body.write_text(
            '## Current Status Impact\n\n'
            'status: not_applicable\n'
            'reason: Recovery state is unchanged.\n'
            'current_status_updated_in_this_pr: "false"\n'
            'post_merge_safe: not_applicable\n'
            'follow_up_issue: none\n',
            encoding='utf-8',
        )
        quoted_impact_boolean = subprocess.run(
            [
                sys.executable,
                'scripts/asgk.py',
                'current-status-impact-check',
                '--pr-body',
                str(impact_body),
                '--changed-paths-file',
                str(changed_none),
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if (
            quoted_impact_boolean.returncode != 1
            or 'must be true or false' not in quoted_impact_boolean.stdout
        ):
            fail('current-status-impact-check must preserve boolean types')

        impact_body.write_text(
            '## Current Status Impact\n\n'
            'status: not_applicable\n'
            'reason: Recovery state is unchanged.\n'
            'current_status_updated_in_this_pr: false\n'
            'post_merge_safe: not_applicable\n'
            'follow_up_issue: none\n'
            'follow_up_issue: "#999"\n',
            encoding='utf-8',
        )
        duplicate_follow_up = subprocess.run(
            [
                sys.executable,
                'scripts/asgk.py',
                'current-status-impact-check',
                '--pr-body',
                str(impact_body),
                '--changed-paths-file',
                str(changed_none),
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if (
            duplicate_follow_up.returncode != 1
            or 'exactly one follow_up_issue field' not in duplicate_follow_up.stdout
        ):
            fail('current-status-impact-check must reject duplicate follow-up fields')

        impact_body.write_text(
            '## Current Status Impact\n\n'
            'status: not_applicable\n'
            'reason: none?\n'
            'current_status_updated_in_this_pr: false\n'
            'post_merge_safe: not_applicable\n'
            'follow_up_issue: none\n',
            encoding='utf-8',
        )
        generic_impact_reason = subprocess.run(
            [
                sys.executable,
                'scripts/asgk.py',
                'current-status-impact-check',
                '--pr-body',
                str(impact_body),
                '--changed-paths-file',
                str(changed_none),
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if (
            generic_impact_reason.returncode != 1
            or 'reason is missing or non-specific' not in generic_impact_reason.stdout
        ):
            fail('current-status-impact-check must share material reason semantics')

        impact_body.write_text(
            '## Current Status Impact\n\n'
            'status: updated\n'
            'reason: The supplied recovery snapshot is post-merge-safe.\n'
            'current_status_updated_in_this_pr: true\n'
            'post_merge_safe: true\n'
            'follow_up_issue: none\n',
            encoding='utf-8',
        )
        prefix_impact = subprocess.run(
            [
                sys.executable,
                'scripts/asgk.py',
                'current-status-impact-check',
                '--pr-body',
                str(impact_body),
                '--changed-paths-file',
                str(changed_status),
                '--file',
                'examples/negative/compact_governance/current_status.compact.stale-active.md',
                '--this-pr',
                '#24',
                '--closing-issue',
                '#24',
                '--this-branch',
                'codex/compact-pr-body-profile-24',
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if prefix_impact.returncode != 0:
            fail('current-status-impact-check must not match refs by substring prefix')

        exact_impact = subprocess.run(
            [
                sys.executable,
                'scripts/asgk.py',
                'current-status-impact-check',
                '--pr-body',
                str(impact_body),
                '--changed-paths-file',
                str(changed_status),
                '--file',
                'examples/negative/compact_governance/current_status.compact.stale-active.md',
                '--this-pr',
                '#0241',
                '--closing-issue',
                '#0240',
                '--this-branch',
                'codex/compact-pr-body-profile-240',
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if exact_impact.returncode != 1:
            fail('current-status-impact-check must identify exact active refs')

        missing_status_impact = subprocess.run(
            [
                sys.executable,
                'scripts/asgk.py',
                'current-status-impact-check',
                '--pr-body',
                str(impact_body),
                '--changed-paths-file',
                str(changed_status),
                '--file',
                'examples/negative/does-not-exist.md',
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if (
            missing_status_impact.returncode != 1
            or 'status-check failed for current status file' not in missing_status_impact.stdout
            or 'Traceback' in missing_status_impact.stdout
            or 'Traceback' in missing_status_impact.stderr
        ):
            fail('current-status-impact-check must bound missing status input')

    status_policy = read(root, 'docs/control/CURRENT_STATUS_POLICY.md')
    status_text = read(root, 'docs/handoff/CURRENT_STATUS.md')
    with tempfile.TemporaryDirectory() as tmpdir:
        stale_status_path = Path(tmpdir) / 'current-status-with-history.md'
        stale_status_path.write_text(
            status_text
            + '\n## last Completed\n\n'
            + 'This duplicate history surface must be rejected.\n',
            encoding='utf-8',
        )
        stale_status_result = subprocess.run(
            [
                sys.executable,
                'scripts/asgk.py',
                'status-check',
                '--file',
                str(stale_status_path),
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if (
            stale_status_result.returncode != 1
            or 'forbidden history-log heading' not in stale_status_result.stdout
        ):
            fail('status-check must reject a Last completed history heading')

    def assert_status_rejected(label, source, expected_fragment):
        with tempfile.TemporaryDirectory() as tmpdir:
            candidate = Path(tmpdir) / 'CURRENT_STATUS.md'
            candidate.write_text(source, encoding='utf-8')
            result = subprocess.run(
                [
                    sys.executable,
                    'scripts/asgk.py',
                    'status-check',
                    '--file',
                    str(candidate),
                ],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
            )
            if (
                result.returncode != 1
                or expected_fragment not in result.stdout
            ):
                fail(f'status-check did not reject {label} with the expected reason')

    assert_status_rejected(
        'case-variant H3 Last completed heading',
        status_text
        + '\n### LAST COMPLETED\n\n'
        + 'This nested history surface must be rejected.\n',
        'forbidden history-log heading',
    )
    assert_status_rejected(
        'wrong-level duplicate Active work heading',
        status_text
        + '\n### Active work\n\n'
        + 'issue: "#decoy"\npr: none\nbranch: main\nstate: stale\n',
        'case-variant duplicate current status heading',
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        hidden_heading_path = Path(tmpdir) / 'CURRENT_STATUS.md'
        hidden_heading_path.write_text(
            status_text
            + '\n<!--\n### Last completed\nhidden historical prose\n-->\n',
            encoding='utf-8',
        )
        hidden_heading_result = subprocess.run(
            [
                sys.executable,
                'scripts/asgk.py',
                'status-check',
                '--file',
                str(hidden_heading_path),
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if hidden_heading_result.returncode != 0:
            fail('status-check must ignore headings inside HTML comments')

    active_block = markdown_section(status_text, 'Active work')
    assert_status_rejected(
        'duplicate Active work heading',
        status_text
        + '\n## Active work\n\n'
        + active_block
        + '\n',
        'duplicate current status heading',
    )
    assert_status_rejected(
        'case-variant Active work heading',
        status_text
        + '\n## ACTIVE WORK\n\n'
        + active_block
        + '\n',
        'case-variant duplicate current status heading',
    )
    assert_status_rejected(
        'duplicate issue field',
        status_text.replace(
            'issue: "#323 ASGK 2.0 program"',
            'issue: "#323 ASGK 2.0 program"\nissue: "#240 stale"',
            1,
        ),
        'exactly one issue field',
    )
    assert_status_rejected(
        'case-variant issue field',
        status_text.replace(
            'issue: "#323 ASGK 2.0 program"',
            'issue: "#323 ASGK 2.0 program"\nIssue: "#240 stale"',
            1,
        ),
        'exactly one issue field',
    )

    if re.search(r'^## Last completed\s*$', status_policy, re.M):
        fail('CURRENT_STATUS policy canonical shape retained Last completed')
    if re.search(r'^## Last completed\s*$', status_text, re.M):
        fail('CURRENT_STATUS retained a completed-work ledger heading')
    asgk_source = read(root, 'scripts/asgk.py')
    if 'stale issue #23 active state' in asgk_source:
        fail('status-check retained the hard-coded historical issue #23 assumption')


def check_validation_result_projection(root):
    schema = json.loads(read(root, 'schemas/validation_result.schema.json'))
    contract = read(root, 'contracts/validation_result.contract.yaml')
    expected_required = {
        'result',
        'evidence_source',
        'mechanically_checked',
        'not_checked',
        'human_gate',
        'proof_boundary',
        'findings',
    }
    if set(schema.get('required', [])) != expected_required:
        fail('validation-result schema required envelope fields drifted')
    properties = schema.get('properties', {})
    if set(properties.get('result', {}).get('enum', [])) != set(RESULT_VALUES):
        fail('validation-result schema result enum drifted from helper')
    gate = properties.get('human_gate', {})
    gate_values = (
        gate.get('properties', {})
        .get('status', {})
        .get('enum', [])
    )
    if set(gate_values) != set(HUMAN_GATE_STATUS_VALUES):
        fail('validation-result schema human-gate enum drifted from helper')
    if schema.get('additionalProperties') is not True:
        fail('validation-result schema must preserve command-specific payload')
    if gate.get('additionalProperties') is not False:
        fail('validation-result human_gate must reject extra keys')
    finding = schema.get('$defs', {}).get('finding', {})
    if set(finding.get('required', [])) != {'code', 'reason', 'blocking'}:
        fail('validation-result finding required fields drifted')
    if len(finding.get('oneOf', [])) != 2:
        fail('validation-result finding must require exactly one field or path')
    for token in (
        'version: 2.0.0',
        'finding_location_rule: exactly_one_of_field_or_path',
        'human_gate never reports approval passed',
        'human_gate required is valid only when result is blocked',
    ):
        if token not in contract:
            fail(f'validation-result contract missing invariant: {token}')

    checked = ['one mechanical surface']
    unchecked = ['semantic truth and human approval']
    boundary = 'Envelope test proves only common result-shape conformance.'
    valid_payloads = (
        {
            'result': 'pass',
            'evidence_source': 'bootstrap_self_test',
            'mechanically_checked': checked,
            'not_checked': unchecked,
            'human_gate': {
                'status': 'not_checked',
                'reason': 'No human approval was checked.',
            },
            'proof_boundary': boundary,
            'findings': [],
        },
        {
            'result': 'warning',
            'evidence_source': 'bootstrap_self_test',
            'mechanically_checked': checked,
            'not_checked': unchecked,
            'human_gate': {
                'status': 'not_applicable',
                'reason': 'This warning has no human decision gate.',
            },
            'proof_boundary': boundary,
            'findings': [
                make_finding(
                    'VR_TEST_WARNING',
                    'nonblocking warning',
                    field='test',
                    blocking=False,
                )
            ],
        },
        {
            'result': 'fail',
            'evidence_source': 'bootstrap_self_test',
            'mechanically_checked': checked,
            'not_checked': unchecked,
            'human_gate': {
                'status': 'not_checked',
                'reason': 'No human approval was checked.',
            },
            'proof_boundary': boundary,
            'findings': [
                make_finding(
                    'VR_TEST_FAILURE',
                    'blocking failure',
                    path='test.json',
                    blocking=True,
                )
            ],
        },
        {
            'result': 'blocked',
            'evidence_source': 'bootstrap_self_test',
            'mechanically_checked': checked,
            'not_checked': unchecked,
            'human_gate': {
                'status': 'required',
                'reason': 'A human decision is required at this boundary.',
            },
            'proof_boundary': boundary,
            'findings': [
                make_finding(
                    'VR_TEST_BLOCKED',
                    'blocking human boundary',
                    field='human_gate',
                    blocking=True,
                )
            ],
        },
    )
    for payload in valid_payloads:
        errors = validation_result_errors(payload)
        if errors:
            fail(
                'validation-result helper rejected a valid result variant: '
                + '; '.join(errors)
            )

    invalid_payloads = (
        {
            **valid_payloads[0],
            'findings': [
                make_finding(
                    'VR_TEST_PASS_FINDING',
                    'pass cannot carry findings',
                    field='result',
                    blocking=False,
                )
            ],
        },
        {
            **valid_payloads[1],
            'findings': [
                make_finding(
                    'VR_TEST_BLOCKING_WARNING',
                    'warning cannot block',
                    field='result',
                    blocking=True,
                )
            ],
        },
        {
            **valid_payloads[2],
            'findings': [],
        },
        {
            **valid_payloads[2],
            'human_gate': {
                'status': 'required',
                'reason': 'Required gates must map to blocked.',
            },
        },
        {
            **valid_payloads[2],
            'findings': [
                {
                    'code': 'invalid-code',
                    'field': 'test',
                    'path': 'test.json',
                    'reason': 'invalid finding identity',
                    'blocking': True,
                }
            ],
        },
    )
    if any(not validation_result_errors(payload) for payload in invalid_payloads):
        fail('validation-result helper accepted an invalid envelope mutation')

    internal = checked_validation_result(
        {
            'result': 'pass',
            'findings': [
                make_finding(
                    'VR_TEST_INTERNAL',
                    'invalid pass finding',
                    field='result',
                    blocking=True,
                )
            ],
        },
        evidence_source='bootstrap_self_test',
        mechanically_checked=checked,
        not_checked=unchecked,
        proof_boundary=boundary,
    )
    if (
        internal.get('result') != 'fail'
        or finding_codes(internal) != ['VR_INTERNAL_ENVELOPE_INVALID']
    ):
        fail('validation-result checked wrapper must fail closed on bad envelopes')


CANDIDATE_SCENARIO_SNAPSHOT_SCRIPT = r"""
import json
import sys

sys.path.insert(0, sys.argv[1])

from asgk_lib.scenario_registry import (
    CONTROLLED_ERROR_SCENARIOS,
    NEGATIVE_CASE_CHOICES,
    PARITY_SCENARIOS,
    RETAINED_JSON_SCENARIOS,
)

scenario_fields = (
    "name",
    "group",
    "command",
    "polarity",
    "expected_result",
    "expected_exit",
    "expected_codes",
    "proof_boundary",
    "expected_mechanically_checked",
    "expected_not_checked",
)

def snapshot(scenario):
    return {
        field: getattr(scenario, field)
        for field in scenario_fields
    }

print(json.dumps({
    "retained": [snapshot(item) for item in RETAINED_JSON_SCENARIOS],
    "controlled": [snapshot(item) for item in CONTROLLED_ERROR_SCENARIOS],
    "parity": [
        {
            "name": item.name,
            "group": item.group,
            "polarity": item.polarity,
        }
        for item in PARITY_SCENARIOS
    ],
    "negative_case_choices": list(NEGATIVE_CASE_CHOICES),
}))
"""


def _scenario_registry_snapshot(root):
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            CANDIDATE_SCENARIO_SNAPSHOT_SCRIPT,
            str(root / "scripts"),
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stdout + result.stderr).strip()
        fail(
            "inspected source scenario registry could not be loaded"
            + (f": {detail}" if detail else "")
        )
    try:
        payload = json.loads(result.stdout)
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        fail(f"inspected source scenario registry snapshot is invalid: {exc}")
    if (
        not isinstance(payload, dict)
        or set(payload)
        != {
            "retained",
            "controlled",
            "parity",
            "negative_case_choices",
        }
        or not all(
            isinstance(payload.get(field), list)
            for field in (
                "retained",
                "controlled",
                "parity",
                "negative_case_choices",
            )
        )
    ):
        fail("inspected source scenario registry snapshot has an invalid shape")
    return payload


def check_scenario_registry_projection(root):
    snapshot = _scenario_registry_snapshot(root)
    retained_scenarios = snapshot["retained"]
    controlled_scenarios = snapshot["controlled"]
    parity_scenarios = snapshot["parity"]
    negative_case_choices = snapshot["negative_case_choices"]
    expected_behaviors = {
        'policy-gate',
        'pr-status',
        'work-unit',
        'compact-task-packet',
        'handoff',
        'compact-handoff',
        'compact-issue-scope',
        'compact-scope-lock',
        'compact-pr-report',
        'compact-pr-body',
        'context-budget',
        'workspace-state',
        'source-validation',
    }
    actual_behaviors = {
        scenario.get("group") for scenario in retained_scenarios
    }
    if actual_behaviors != expected_behaviors:
        fail(
            'retained JSON behavior registry drifted: '
            f'{sorted(actual_behaviors)}'
        )
    names = [
        scenario.get("name")
        for scenario in (
            *retained_scenarios,
            *controlled_scenarios,
        )
    ]
    if len(names) != len(set(names)):
        fail('scenario registry contains duplicate scenario names')
    required_w3c_scenarios = {
        'compact_pr_report_mixed_failure_and_human_gate',
        'compact_pr_report_metadata_unavailable',
        'compact_scope_lock_projection_failure',
        'compact_scope_lock_capture_hash_missing_skips_equality',
        'compact_handoff_status_missing',
        'policy_body_file_missing',
        'policy_event_mode_override_forbidden',
        'policy_event_shape_invalid',
        'policy_event_pull_request_missing',
        'check_pr_invalid_files_skip_downstream_checks',
        'check_pr_missing_status_rollup_skips_ordering',
        'work_unit_missing_allowed_paths_and_execution_gates',
        'compact_pr_report_invalid_files_skip_restricted_boundary',
        'compact_pr_report_invalid_and_restricted_files_preserve_gate',
        'workspace_state_wrong_object_shape',
        'task_packet_unsupported_mode_skips_field_shape',
        'task_packet_pseudo_ref_does_not_claim_file_existence',
        'context_budget_unsupported_mode_skips_field_and_context_checks',
        'compact_handoff_invalid_impact_does_not_claim_consistency',
        'compact_handoff_stale_refs_do_not_claim_consistency',
        'compact_pr_body_malformed_findings_fail_closed',
        'check_pr_live_executable_missing',
        'work_unit_live_executable_missing',
        'task_packet_live_executable_missing',
        'compact_issue_scope_live_executable_missing',
        'compact_scope_lock_live_executable_missing',
        'compact_pr_report_live_executable_missing',
        'workspace_git_executable_missing',
        'source_inventory_reference_superset',
        'source_inventory_missing_required_path',
        'source_validation_input_mode_invalid',
        'source_inventory_file_unreadable',
        'source_inventory_json_invalid',
        'source_inventory_shape_invalid',
        'source_inventory_duplicate_key',
        'source_inventory_json_too_deep',
    }
    if not required_w3c_scenarios.issubset(set(names)):
        fail('scenario registry is missing W3C mixed-gate or executable-unavailable coverage')
    for behavior in sorted(expected_behaviors):
        polarities = {
            scenario.get("polarity")
            for scenario in retained_scenarios
            if scenario.get("group") == behavior
        }
        if polarities != {'positive', 'negative'}:
            fail(f'{behavior} must retain a positive and negative scenario')

    for scenario in (
        *retained_scenarios,
        *controlled_scenarios,
    ):
        if not isinstance(scenario, dict):
            fail("scenario registry snapshot contains a non-object scenario")
        name = scenario.get("name")
        command = scenario.get("command")
        if not isinstance(command, list) or not command or '--json' not in command:
            fail(f'{name} must name one machine-readable owner command')
        if scenario.get("expected_result") not in RESULT_VALUES:
            fail(f'{name} has unsupported expected result')
        if scenario.get("expected_exit") not in {0, 1}:
            fail(f'{name} has unsupported expected exit')
        proof_boundary = scenario.get("proof_boundary")
        if not isinstance(proof_boundary, str) or not proof_boundary.strip():
            fail(f'{name} has an empty proof boundary')
        for field_name in (
            'expected_mechanically_checked',
            'expected_not_checked',
        ):
            exact_items = scenario.get(field_name)
            if exact_items is not None and (
                not isinstance(exact_items, list)
                or not exact_items
                or any(not isinstance(item, str) or not item.strip() for item in exact_items)
            ):
                fail(f'{name} has invalid {field_name} expectations')
        polarity = scenario.get("polarity")
        expected_codes = scenario.get("expected_codes")
        if not isinstance(expected_codes, list):
            fail(f'{name} has invalid expected finding codes')
        if polarity == 'positive':
            if (
                scenario.get("expected_result") != 'pass'
                or scenario.get("expected_exit") != 0
                or expected_codes
            ):
                fail(f'{name} positive expectations are incoherent')
        elif polarity == 'negative':
            if scenario.get("expected_result") == 'pass' or not expected_codes:
                fail(f'{name} negative expectations are incomplete')
        else:
            fail(f'{name} has unsupported polarity')
        for code in expected_codes:
            if not re.fullmatch(r'[A-Z][A-Z0-9_]*', code):
                fail(f'{name} has invalid expected finding code: {code}')

    if (
        not controlled_scenarios
        or {scenario.get("group") for scenario in controlled_scenarios}
        != {'controlled-errors'}
        or not {
            scenario.get("expected_result")
            for scenario in controlled_scenarios
        }.issuperset({'fail', 'blocked'})
    ):
        fail('controlled-error scenarios must cover fail and blocked outcomes')

    parity_groups = {
        group: {
            scenario.get("polarity")
            for scenario in parity_scenarios
            if scenario.get("group") == group
        }
        for group in {'compact-task-packet', 'source-validation'}
    }
    if (
        len(parity_scenarios) != 4
        or set(scenario.get("group") for scenario in parity_scenarios)
        != set(parity_groups)
        or any(
            polarities != {'positive', 'negative'}
            for polarities in parity_groups.values()
        )
    ):
        fail(
            'task-packet alias and source-wrapper parity must each retain '
            'one positive and one negative case'
        )
    if not {'retained-json', 'controlled-errors', 'scenario-runner', 'all'}.issubset(
        set(negative_case_choices)
    ):
        fail('negative CLI choices do not expose the canonical scenario registry')


def check_negative_runner_projection(root):
    result = subprocess.run(
        [
            sys.executable,
            "scripts/asgk.py",
            "negative",
            "scenario-runner",
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    if result.returncode != 0 or "Traceback" in output:
        fail(
            "inspected source scenario runner self-tests failed"
            + (f": {output.strip()}" if output.strip() else "")
        )
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")


def check_source_validation_call_graph(root):
    wrapper = read(root, "scripts/validate_bootstrap.py")
    if "from asgk_lib.source_validation import main" not in wrapper:
        fail("validate_bootstrap.py must delegate to source_validation.main")
    for forbidden in (
        "REQUIRED_FILES",
        "REQUIRED_TERMS",
        "subprocess",
        "scenario_registry",
    ):
        if forbidden in wrapper:
            fail(
                "validate_bootstrap.py must not own validation policy or "
                f"orchestration: {forbidden}"
            )

    cli = read(root, "scripts/asgk.py")
    if "from asgk_lib.source_validation import run_source_validation" not in cli:
        fail("asgk validate must import the canonical source engine")
    if '"scripts/asgk.py", "validate"' not in cli:
        fail("doctor must reach source validation through asgk validate")
    if "scripts/check_project.py" in cli:
        fail("doctor must not invoke the legacy directory-only project checker")


def live_source_check_steps(root):
    return (
        ("canonical owner term checks", lambda: check_terms(root)),
        (
            "JSON parseability for present schema and example files",
            lambda: check_json(root),
        ),
        (
            "task-packet template field projection",
            lambda: check_yaml_like_fields(root),
        ),
        ("issue and PR template projection", lambda: check_templates(root)),
        (
            "merge-decision schema and example projection",
            lambda: check_merge_decision_projection(root),
        ),
        ("PR workflow lifecycle projection", lambda: check_pr_workflow_projection(root)),
        (
            "policy-gate routing fixture projection",
            lambda: check_policy_gate_routing_fixtures(root),
        ),
        (
            "policy-gate fail-closed projection",
            lambda: check_policy_gate_failure_projection(root),
        ),
        ("PR status projection", lambda: check_pr_status_projection(root)),
        (
            "W3A work-unit and task-packet projection",
            lambda: check_w3a_work_unit_and_task_packet_projection(root),
        ),
        (
            "W3B handoff and CURRENT_STATUS projection",
            lambda: check_w3b_handoff_projection(root),
        ),
        (
            "W3C validation-result projection",
            lambda: check_validation_result_projection(root),
        ),
        (
            "inspected source scenario registry structure",
            lambda: check_scenario_registry_projection(root),
        ),
        (
            "inspected source scenario runner self-tests",
            lambda: check_negative_runner_projection(root),
        ),
        (
            "doctor, validate, and compatibility-wrapper source call graph",
            lambda: check_source_validation_call_graph(root),
        ),
    )


def _result(
    *,
    result,
    evidence_source,
    mechanically_checked,
    not_checked,
    proof_boundary,
    findings,
    **payload,
):
    report = checked_validation_result(
        {
            "result": result,
            "findings": findings,
            **payload,
        },
        evidence_source=evidence_source,
        mechanically_checked=mechanically_checked,
        not_checked=not_checked,
        proof_boundary=proof_boundary,
    )
    return report


def _input_failure(code, reason, *, field, evidence_source, checked):
    return _result(
        result="fail",
        evidence_source=evidence_source,
        mechanically_checked=checked,
        not_checked=(
            "required ASGK source path membership",
            *SOURCE_INVENTORY_NOT_CHECKED,
        ),
        proof_boundary=SOURCE_INPUT_FAILURE_BOUNDARY,
        findings=[
            make_finding(
                code,
                reason,
                field=field,
                blocking=True,
            )
        ],
    )


def _canonical_inventory_paths(payload):
    if not isinstance(payload, dict) or set(payload) != {"paths"}:
        return None, (
            "source inventory must be an object with exactly one paths field"
        )
    raw_paths = payload.get("paths")
    if not isinstance(raw_paths, list) or not raw_paths:
        return None, "source inventory paths must be a non-empty array"

    paths = []
    for index, value in enumerate(raw_paths):
        if not isinstance(value, str) or not value:
            return None, f"source inventory paths[{index}] must be a string"
        if value != value.strip() or "\\" in value:
            return None, (
                f"source inventory paths[{index}] is not canonically normalized"
            )
        pure = PurePosixPath(value)
        if (
            value == "."
            or pure.is_absolute()
            or re.match(r"^[A-Za-z]:", value)
            or pure.as_posix() != value
            or any(part in {"", ".", ".."} for part in pure.parts)
            or any(
                ord(character) < 32 or ord(character) == 127
                for character in value
            )
            or re.search(r"[*?\[\]]", value)
        ):
            return None, (
                f"source inventory paths[{index}] must be an exact "
                "repository-relative path"
            )
        paths.append(value)
    if len(paths) != len(set(paths)):
        return None, "source inventory paths must be unique"
    return tuple(paths), None


def _inventory_object_without_duplicate_keys(pairs):
    payload = {}
    for key, value in pairs:
        if key in payload:
            raise DuplicateInventoryKey(
                f"source inventory repeats JSON object key: {key}"
            )
        payload[key] = value
    return payload


def evaluate_source_inventory(source_inventory_file):
    inventory_path = Path(source_inventory_file)
    evidence_source = f"supplied_source_inventory:{inventory_path}"
    try:
        raw = inventory_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return _input_failure(
            "SV_INVENTORY_FILE_UNREADABLE",
            f"source inventory file is unreadable: {exc}",
            field="source_inventory_file",
            evidence_source=evidence_source,
            checked=("supplied source inventory file readability",),
        )
    try:
        payload = json.loads(
            raw,
            object_pairs_hook=_inventory_object_without_duplicate_keys,
        )
    except DuplicateInventoryKey as exc:
        return _input_failure(
            "SV_INVENTORY_SHAPE_INVALID",
            str(exc),
            field="source_inventory",
            evidence_source=evidence_source,
            checked=(
                "supplied source inventory file readability",
                "supplied source inventory JSON parsing",
                "supplied source inventory JSON object shape",
            ),
        )
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        return _input_failure(
            "SV_INVENTORY_JSON_INVALID",
            f"source inventory is not valid JSON: {exc}",
            field="source_inventory_file",
            evidence_source=evidence_source,
            checked=(
                "supplied source inventory file readability",
                "supplied source inventory JSON parsing",
            ),
        )

    supplied_paths, shape_problem = _canonical_inventory_paths(payload)
    if shape_problem:
        return _input_failure(
            "SV_INVENTORY_SHAPE_INVALID",
            shape_problem,
            field="source_inventory.paths",
            evidence_source=evidence_source,
            checked=(
                "supplied source inventory file readability",
                "supplied source inventory JSON parsing",
                "supplied source inventory JSON object shape",
            ),
        )

    required = required_source_paths()
    supplied_set = set(supplied_paths)
    missing = [path for path in required if path not in supplied_set]
    findings = [
        make_finding(
            "SV_REQUIRED_PATH_MISSING",
            "retained ASGK source path is missing from the supplied inventory",
            path=path,
            blocking=True,
        )
        for path in missing
    ]
    return _result(
        result="fail" if findings else "pass",
        evidence_source=evidence_source,
        mechanically_checked=SOURCE_INVENTORY_CHECKED,
        not_checked=SOURCE_INVENTORY_NOT_CHECKED,
        proof_boundary=SOURCE_INVENTORY_PROOF_BOUNDARY,
        findings=findings,
        source_inventory={
            "required_path_count": len(required),
            "supplied_path_count": len(supplied_paths),
            "missing_paths": missing,
        },
    )


def evaluate_live_source(repo_root):
    root = Path(repo_root).resolve()
    required = required_source_paths()
    steps = live_source_check_steps(root)
    step_labels = tuple(label for label, _check in steps)
    provenance = {
        "inspected_source_root": str(root),
        "validator_reference_root": str(VALIDATOR_REFERENCE_ROOT),
        "required_set_owner": (
            str(Path(__file__).resolve())
            + ":required_source_paths"
        ),
        "execution_boundary": (
            "Encoded live checks may execute repository-local Python commands "
            "from inspected_source_root; use only with a trusted ASGK source tree."
        ),
    }
    missing = [path for path in required if not (root / path).is_file()]
    if missing:
        return (
            _result(
                result="fail",
                evidence_source=f"live_asgk_source_tree:{root}",
                mechanically_checked=("required ASGK source path existence",),
                not_checked=(
                    *step_labels,
                    *LIVE_SOURCE_DOMAIN_NOT_CHECKED,
                ),
                proof_boundary=LIVE_SOURCE_FAILURE_BOUNDARY,
                findings=[
                    make_finding(
                        "SV_REQUIRED_PATH_MISSING",
                        "retained ASGK source path is missing from the live source tree",
                        path=path,
                        blocking=True,
                    )
                    for path in missing
                ],
                source_inventory={
                    "required_path_count": len(required),
                    "missing_paths": missing,
                },
                source_validation_provenance=provenance,
            ),
            "",
        )

    captured = io.StringIO()
    failure = None
    completed_checks = ["required ASGK source path existence"]
    remaining_checks = []
    with contextlib.redirect_stdout(captured):
        for index, (label, check) in enumerate(steps):
            try:
                check()
            except SourceValidationFailure as exc:
                completed_checks.append(f"{label} (failed)")
                remaining_checks = list(step_labels[index + 1:])
                failure = str(exc)
                break
            except Exception as exc:
                completed_checks.append(f"{label} (failed)")
                remaining_checks = list(step_labels[index + 1:])
                failure = f"{type(exc).__name__}: {exc}"
                break
            else:
                completed_checks.append(label)

    findings = []
    if failure:
        findings.append(
            make_finding(
                "SV_SOURCE_CHECK_FAILED",
                failure,
                field="source_validation",
                blocking=True,
            )
        )
    return (
        _result(
            result="fail" if findings else "pass",
            evidence_source=f"live_asgk_source_tree:{root}",
            mechanically_checked=completed_checks,
            not_checked=(
                *remaining_checks,
                *LIVE_SOURCE_DOMAIN_NOT_CHECKED,
            ),
            proof_boundary=(
                LIVE_SOURCE_FAILURE_BOUNDARY
                if findings
                else LIVE_SOURCE_PROOF_BOUNDARY
            ),
            findings=findings,
            source_inventory={
                "required_path_count": len(required),
                "missing_paths": [],
            },
            source_validation_provenance=provenance,
        ),
        captured.getvalue(),
    )


def run_source_validation(
    *,
    repo_root=None,
    source_inventory_file=None,
    as_json=False,
):
    inventory_mode = source_inventory_file is not None
    if repo_root is not None and source_inventory_file is not None:
        report = _input_failure(
            "SV_INPUT_MODE_INVALID",
            "--repo-root and --source-inventory-file are mutually exclusive",
            field="input_mode",
            evidence_source="source_validation_cli_arguments",
            checked=("source validation input mode selection",),
        )
        captured = ""
    elif source_inventory_file is not None:
        report = evaluate_source_inventory(source_inventory_file)
        captured = ""
    else:
        report, captured = evaluate_live_source(repo_root or Path.cwd())

    if as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        if captured:
            print(captured, end="" if captured.endswith("\n") else "\n")
        findings = report.get("findings", [])
        missing_paths = [
            finding.get("path")
            for finding in findings
            if (
                isinstance(finding, dict)
                and finding.get("code") == "SV_REQUIRED_PATH_MISSING"
            )
        ]
        for path in missing_paths:
            label = (
                "Missing required inventory path"
                if inventory_mode
                else "Missing required file"
            )
            print(f"{label}: {path}")
        if report.get("result") == "pass":
            if inventory_mode:
                print("Source inventory required-path inclusion check passed.")
            else:
                print("Bootstrap validation passed.")
        elif missing_paths:
            if inventory_mode:
                noun = (
                    "required inventory path"
                    if len(missing_paths) == 1
                    else "required inventory paths"
                )
            else:
                noun = (
                    "required file"
                    if len(missing_paths) == 1
                    else "required files"
                )
            print(f"FAIL: {len(missing_paths)} {noun} missing")
        elif findings:
            print(f"FAIL: {findings[0].get('reason', 'source validation failed')}")
        else:
            print("FAIL: source validation failed")
    return 0 if report.get("result") == "pass" else 1


def build_parser():
    parser = argparse.ArgumentParser(
        description="Validate the retained ASGK source reference superset."
    )
    parser.add_argument(
        "--repo-root",
        help=(
            "Trusted ASGK source repository root; defaults to the current "
            "directory. Encoded live checks may execute repository-local Python."
        ),
    )
    parser.add_argument(
        "--source-inventory-file",
        help=(
            "Caller-supplied source path inventory for fixture/capture checks; "
            "does not inspect listed files."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit one common-envelope JSON object.",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return run_source_validation(
        repo_root=args.repo_root,
        source_inventory_file=args.source_inventory_file,
        as_json=args.json,
    )

if __name__ == '__main__':
    raise SystemExit(main())
