from __future__ import annotations

import contextlib
from collections import Counter
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile

from asgk_lib.common import ROOT
from asgk_lib.scenario_registry import (
    COMMANDS_PASS,
    EXPECTED_FAILURE,
    EXPECTED_SUCCESS,
    JSON_SCENARIOS,
    NEGATIVE_CASE_CHOICES,
    NEGATIVE_CASE_GROUPS,
    PARITY_SCENARIOS,
    JsonScenario,
    NegativeCaseGroup,
    ParityScenario,
)
from asgk_lib.validation_result import validation_result_errors


def format_command(args: tuple[str, ...]) -> str:
    return shlex.join(args)


def run_captured(command: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


TRACEBACK_MARKERS = (
    "Traceback (most recent call last):",
    "SyntaxError:",
    "ModuleNotFoundError:",
    "ImportError:",
)


class _DuplicateJsonKeyError(ValueError):
    pass


def _json_object_without_duplicate_keys(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateJsonKeyError(key)
        result[key] = value
    return result


def _scenario_tree_fingerprint(relative_path: str) -> str:
    pure_path = PurePosixPath(relative_path)
    if (
        not relative_path
        or pure_path.is_absolute()
        or any(part in {"", ".", ".."} for part in relative_path.split("/"))
        or pure_path.as_posix() != relative_path
    ):
        raise ValueError(
            f"scenario unchanged path is not normalized repo-relative: {relative_path}"
        )

    target = ROOT.joinpath(*pure_path.parts)
    digest = hashlib.sha256()

    def update(value: str | bytes) -> None:
        data = value if isinstance(value, bytes) else value.encode("utf-8")
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)

    def visit(path: Path, relative: PurePosixPath) -> None:
        try:
            path_stat = path.lstat()
        except FileNotFoundError:
            update("missing")
            update(relative.as_posix())
            return

        update(relative.as_posix())
        update(str(path_stat.st_mode))
        update(str(path_stat.st_uid))
        update(str(path_stat.st_gid))
        update(str(path_stat.st_size))
        update(str(path_stat.st_mtime_ns))
        update(str(path_stat.st_ctime_ns))

        if stat.S_ISLNK(path_stat.st_mode):
            update("symlink")
            update(os.readlink(path))
            return
        if stat.S_ISREG(path_stat.st_mode):
            update("file")
            with path.open("rb") as stream:
                while True:
                    chunk = stream.read(64 * 1024)
                    if not chunk:
                        break
                    update(chunk)
            return
        if stat.S_ISDIR(path_stat.st_mode):
            update("directory")
            children = sorted(path.iterdir(), key=lambda child: child.name)
            for child in children:
                visit(child, relative / child.name)
            return
        update("special")

    visit(target, pure_path)
    return digest.hexdigest()


def _scenario_unchanged_path_errors(
    scenario: JsonScenario,
    before: dict[str, str],
    after: dict[str, str],
) -> list[str]:
    return [
        f"scenario path changed during read-only command: {relative_path}"
        for relative_path in scenario.unchanged_paths
        if before.get(relative_path) != after.get(relative_path)
    ]


def _json_values_exact(actual: object, expected: object) -> bool:
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or set(actual) != set(expected):
            return False
        return all(
            _json_values_exact(actual[key], expected_value)
            for key, expected_value in expected.items()
        )
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            return False
        return all(
            _json_values_exact(actual_item, expected_item)
            for actual_item, expected_item in zip(actual, expected)
        )
    return actual == expected


def _json_string_contains(value: object, fragment: str) -> bool:
    if isinstance(value, str):
        return fragment in value
    if isinstance(value, list):
        return any(_json_string_contains(item, fragment) for item in value)
    if isinstance(value, dict):
        return any(
            fragment in str(key)
            or _json_string_contains(item, fragment)
            for key, item in value.items()
        )
    return False


def prepare_temp_input(
    scenario: JsonScenario,
    temp_root: Path,
) -> str | None:
    spec = scenario.temp_input
    if spec is None:
        return None
    if spec.source is not None:
        text = (ROOT / spec.source).read_text(encoding="utf-8")
    else:
        text = spec.content or ""
    for old, new in spec.replacements:
        if old not in text:
            raise ValueError(
                f"scenario {scenario.name} replacement source is missing: {old}"
            )
        text = text.replace(old, new)
    if spec.json_transform:
        payload = json.loads(text)
        if not isinstance(payload, dict):
            raise ValueError(
                f"scenario {scenario.name} transform requires a JSON object"
            )
        if spec.json_transform in {
            "compact_pr_restricted_boundary",
            "compact_pr_restricted_boundary_with_mechanical_failure",
            "compact_pr_restricted_boundary_with_invalid_file",
        }:
            restricted_path = "docs/control/VALIDATION_STRATEGY.md"
            payload["files"] = (
                [{"path": restricted_path}, {"path": ""}]
                if spec.json_transform
                == "compact_pr_restricted_boundary_with_invalid_file"
                else [{"path": restricted_path}]
            )
            references = payload.get("closingIssuesReferences")
            if not isinstance(references, list) or not references:
                raise ValueError(
                    "compact PR restricted-boundary transform needs closing issue metadata"
                )
            issue = references[0]
            if not isinstance(issue, dict) or not isinstance(issue.get("body"), str):
                raise ValueError(
                    "compact PR restricted-boundary transform needs an issue body"
                )
            issue["body"] = issue["body"].replace(
                "  - scripts/asgk.py",
                f"  - {restricted_path}",
            )
            if (
                spec.json_transform
                == "compact_pr_restricted_boundary_with_mechanical_failure"
            ):
                payload["mergeStateStatus"] = "DIRTY"
            text = json.dumps(payload)
        elif spec.json_transform == "check_pr_files_invalid":
            payload["files"] = [{"path": ""}]
            text = json.dumps(payload)
        elif spec.json_transform == "check_pr_status_rollup_missing":
            payload["statusCheckRollup"] = []
            text = json.dumps(payload)
        elif spec.json_transform in {
            "policy_quoted_result",
            "policy_uppercase_result",
            "policy_quoted_boolean",
        }:
            pull_request = payload.get("pull_request")
            if not isinstance(pull_request, dict) or not isinstance(
                pull_request.get("body"),
                str,
            ):
                raise ValueError(
                    "policy mutation requires pull_request.body text"
                )
            replacements = {
                "policy_quoted_result": (
                    "result: merge_allowed",
                    'result: "merge_allowed"',
                ),
                "policy_uppercase_result": (
                    "result: merge_allowed",
                    "result: MERGE_ALLOWED",
                ),
                "policy_quoted_boolean": (
                    "checks_passed: true",
                    'checks_passed: "true"',
                ),
            }
            old, new = replacements[spec.json_transform]
            if old not in pull_request["body"]:
                raise ValueError(
                    f"policy mutation source is missing: {old}"
                )
            pull_request["body"] = pull_request["body"].replace(old, new)
            text = json.dumps(payload)
        else:
            raise ValueError(
                f"unsupported scenario JSON transform: {spec.json_transform}"
            )
    path = temp_root / f"input{spec.suffix}"
    path.write_text(text, encoding="utf-8")
    return str(path)


def scenario_environment(
    scenario: JsonScenario,
    temp_root: Path,
) -> dict[str, str]:
    env = dict(os.environ)
    if scenario.environment is None:
        return env
    if scenario.environment not in {
        "gh_fail",
        "gh_invalid_json",
        "gh_missing",
        "git_missing",
    }:
        raise ValueError(f"unsupported scenario environment: {scenario.environment}")
    bin_dir = temp_root / "bin"
    bin_dir.mkdir()
    if scenario.environment in {"gh_missing", "git_missing"}:
        (bin_dir / "python3").symlink_to(Path(sys.executable).resolve())
        if scenario.environment == "gh_missing":
            git_path = shutil.which("git")
            if not git_path:
                raise ValueError("gh-missing scenario requires a discoverable git executable")
            (bin_dir / "git").symlink_to(Path(git_path).resolve())
        env["PATH"] = str(bin_dir)
        return env
    gh_path = bin_dir / "gh"
    if scenario.environment == "gh_fail":
        script = (
            "#!/bin/sh\n"
            "printf '%s\\n' 'deterministic gh lookup failure'\n"
            "exit 1\n"
        )
    else:
        script = "#!/bin/sh\nprintf '%s\\n' '{'\nexit 0\n"
    gh_path.write_text(script, encoding="utf-8")
    gh_path.chmod(0o755)
    env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
    return env


def scenario_output_errors(
    scenario: JsonScenario,
    *,
    returncode: int,
    stdout: str,
    stderr: str,
) -> tuple[list[str], dict[str, object] | None]:
    errors: list[str] = []
    if returncode < 0:
        errors.append(f"terminated by signal {-returncode}")
    if returncode != scenario.expected_exit:
        errors.append(
            f"exit {returncode} != expected {scenario.expected_exit}"
        )
    if stderr.strip():
        errors.append("stderr was not empty")
    combined = stdout + "\n" + stderr
    if any(marker in combined for marker in TRACEBACK_MARKERS):
        errors.append("traceback or import/syntax crash marker was emitted")
    raw_forbidden_output_detected = any(
        fragment in combined
        for fragment in scenario.forbidden_output_fragments
    )
    if raw_forbidden_output_detected:
        errors.append("a registered forbidden output fragment was emitted")

    payload: dict[str, object] | None = None
    try:
        decoded = json.loads(
            stdout,
            object_pairs_hook=_json_object_without_duplicate_keys,
        )
    except _DuplicateJsonKeyError:
        errors.append("stdout JSON contains a duplicate object key")
    except json.JSONDecodeError as exc:
        errors.append(f"stdout is not exactly one JSON value: {exc}")
    else:
        if not isinstance(decoded, dict):
            errors.append("JSON output is not an object")
        else:
            payload = decoded

    if payload is None:
        return errors, None

    if (
        not raw_forbidden_output_detected
        and any(
            _json_string_contains(payload, fragment)
            for fragment in scenario.forbidden_output_fragments
        )
    ):
        errors.append(
            "a registered forbidden output fragment was emitted through "
            "JSON string escaping"
        )

    envelope_errors = validation_result_errors(payload)
    errors.extend(
        f"invalid common envelope: {error}"
        for error in envelope_errors
    )
    if payload.get("result") != scenario.expected_result:
        errors.append(
            f"result {payload.get('result')!r} != expected "
            f"{scenario.expected_result!r}"
        )
    raw_findings = payload.get("findings")
    actual_codes = Counter(
        str(finding.get("code"))
        for finding in raw_findings
        if isinstance(finding, dict)
    ) if isinstance(raw_findings, list) else Counter()
    expected_codes = Counter(scenario.expected_codes)
    if actual_codes != expected_codes:
        errors.append(
            f"finding-code multiset {dict(actual_codes)} != expected "
            f"{dict(expected_codes)}"
        )
    if payload.get("proof_boundary") != scenario.proof_boundary:
        errors.append("proof_boundary does not match the registered exact value")
    if (
        scenario.expected_mechanically_checked is not None
        and payload.get("mechanically_checked")
        != list(scenario.expected_mechanically_checked)
    ):
        errors.append(
            "mechanically_checked does not match the registered exact value"
        )
    if (
        scenario.expected_not_checked is not None
        and payload.get("not_checked")
        != list(scenario.expected_not_checked)
    ):
        errors.append("not_checked does not match the registered exact value")
    gate = payload.get("human_gate")
    actual_gate_status = (
        gate.get("status") if isinstance(gate, dict) else None
    )
    if actual_gate_status != scenario.expected_human_gate_status:
        errors.append(
            f"human_gate.status {actual_gate_status!r} != expected "
            f"{scenario.expected_human_gate_status!r}"
        )
    if (
        scenario.expected_domain_result is not None
        and payload.get("domain_result") != scenario.expected_domain_result
    ):
        errors.append(
            f"domain_result {payload.get('domain_result')!r} != expected "
            f"{scenario.expected_domain_result!r}"
        )
    if (
        scenario.expected_domain_result is not None
        and payload.get("derived_state") != scenario.expected_domain_result
    ):
        errors.append(
            f"derived_state {payload.get('derived_state')!r} != expected "
            f"{scenario.expected_domain_result!r}"
        )
    for field, expected_value in scenario.expected_payload_fields:
        if (
            field not in payload
            or not _json_values_exact(payload.get(field), expected_value)
        ):
            errors.append(
                f"payload field {field!r} does not match the registered exact value"
            )
    if (
        scenario.expected_top_level_keys is not None
        and set(payload) != set(scenario.expected_top_level_keys)
    ):
        errors.append(
            "top-level payload keys do not match the registered exact set"
        )
    return errors, payload


def execute_json_scenario(
    scenario: JsonScenario,
) -> tuple[list[str], subprocess.CompletedProcess[str] | None]:
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir)
            temp_input = prepare_temp_input(scenario, temp_root)
            command = [
                temp_input if item == "{temp_input}" else item
                for item in scenario.command
            ]
            if any(item is None for item in command):
                raise ValueError(
                    f"scenario {scenario.name} uses temp placeholder without input"
                )
            before = {
                relative_path: _scenario_tree_fingerprint(relative_path)
                for relative_path in scenario.unchanged_paths
            }
            result = subprocess.run(
                command,
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=scenario_environment(scenario, temp_root),
            )
            after = {
                relative_path: _scenario_tree_fingerprint(relative_path)
                for relative_path in scenario.unchanged_paths
            }
            unchanged_path_errors = _scenario_unchanged_path_errors(
                scenario,
                before,
                after,
            )
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        return [f"scenario preparation failed: {exc}"], None
    errors, _payload = scenario_output_errors(
        scenario,
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )
    errors.extend(unchanged_path_errors)
    return errors, result


def execute_parity_scenario(
    scenario: ParityScenario,
) -> tuple[list[str], tuple[subprocess.CompletedProcess[str], subprocess.CompletedProcess[str]]]:
    left = subprocess.run(
        list(scenario.left_command),
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    right = subprocess.run(
        list(scenario.right_command),
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    errors: list[str] = []
    if (left.returncode, left.stdout, left.stderr) != (
        right.returncode,
        right.stdout,
        right.stderr,
    ):
        errors.append("canonical and compact-alias command outputs differ")
    return errors, (left, right)


def run_json_scenarios(group: str | None = None) -> int:
    scenarios = [
        scenario
        for scenario in JSON_SCENARIOS
        if group is None or scenario.group == group
    ]
    failures: list[tuple[JsonScenario, list[str], subprocess.CompletedProcess[str] | None]] = []
    for scenario in scenarios:
        errors, result = execute_json_scenario(scenario)
        if errors:
            failures.append((scenario, errors, result))
    parity = [
        scenario
        for scenario in PARITY_SCENARIOS
        if group is None or scenario.group == group
    ]
    parity_failures: list[tuple[ParityScenario, list[str]]] = []
    for scenario in parity:
        errors, _results = execute_parity_scenario(scenario)
        if errors:
            parity_failures.append((scenario, errors))
    if failures or parity_failures:
        for scenario, errors, result in failures:
            print(f"FAIL: exact scenario failed: {scenario.name}")
            for error in errors:
                print(f"- {error}")
            if result is not None:
                print_captured_output(result.stdout)
                print_captured_output(result.stderr)
        for scenario, errors in parity_failures:
            print(f"FAIL: parity scenario failed: {scenario.name}")
            for error in errors:
                print(f"- {error}")
        print(
            f"FAIL: {len(failures) + len(parity_failures)} exact scenario(s) failed."
        )
        return 1
    print(
        f"Exact JSON scenarios passed: {len(scenarios)} command scenario(s), "
        f"{len(parity)} parity scenario(s)."
    )
    return 0


def run_scenario_runner_self_tests() -> int:
    pass_scenario = JsonScenario(
        "runner_pass_self_test",
        "scenario-runner",
        ("unused",),
        "positive",
        "pass",
        0,
        (),
        "self-test boundary",
        expected_mechanically_checked=("runner",),
        expected_not_checked=("domain truth",),
    )
    failure_scenario = JsonScenario(
        "runner_failure_self_test",
        "scenario-runner",
        ("unused",),
        "negative",
        "fail",
        1,
        ("SELF_FAILURE",),
        "self-test boundary",
    )
    domain_scenario = JsonScenario(
        "runner_domain_self_test",
        "scenario-runner",
        ("unused",),
        "negative",
        "blocked",
        1,
        ("SELF_FAILURE",),
        "self-test boundary",
        expected_human_gate_status="required",
        expected_domain_result="requires_human",
        expected_mechanically_checked=("runner",),
        expected_not_checked=("domain truth",),
    )
    guarded_claims = [
        {
            "index": 1,
            "kind": "expect_text",
            "path": "notes/example",
            "literal_length": 14,
            "literal_sha256": "digest",
            "status": "matched",
        }
    ]
    payload_scenario = JsonScenario(
        "runner_payload_self_test",
        "scenario-runner",
        ("unused",),
        "positive",
        "pass",
        0,
        (),
        "self-test boundary",
        expected_mechanically_checked=("runner",),
        expected_not_checked=("domain truth",),
        expected_payload_fields=(
            ("writes_performed", False),
            ("claim_count", 1),
            ("claims", guarded_claims),
        ),
        expected_top_level_keys=(
            "claim_count",
            "claims",
            "evidence_source",
            "findings",
            "human_gate",
            "mechanically_checked",
            "not_checked",
            "proof_boundary",
            "result",
            "writes_performed",
        ),
        forbidden_output_fragments=("secret-literal",),
    )
    immutability_scenario = JsonScenario(
        "runner_immutability_self_test",
        "scenario-runner",
        ("unused",),
        "positive",
        "pass",
        0,
        (),
        "self-test boundary",
        unchanged_paths=("fixture",),
    )
    valid_pass_payload = {
        "result": "pass",
        "evidence_source": "self_test",
        "mechanically_checked": ["runner"],
        "not_checked": ["domain truth"],
        "human_gate": {
            "status": "not_checked",
            "reason": "No human approval is inferred.",
        },
        "proof_boundary": "self-test boundary",
        "findings": [],
    }
    failure_finding = {
        "code": "SELF_FAILURE",
        "field": "runner",
        "reason": "self-test failure",
        "blocking": True,
    }
    valid_failure_payload = {
        **valid_pass_payload,
        "result": "fail",
        "findings": [failure_finding],
    }
    valid_domain_payload = {
        **valid_pass_payload,
        "result": "blocked",
        "domain_result": "requires_human",
        "derived_state": "requires_human",
        "human_gate": {
            "status": "required",
            "reason": "A human gate is required by the self-test scenario.",
        },
        "findings": [failure_finding],
    }
    valid_payload_guard = {
        **valid_pass_payload,
        "writes_performed": False,
        "claim_count": 1,
        "claims": guarded_claims,
    }
    valid_json = json.dumps(valid_pass_payload)
    valid_payload_json = json.dumps(valid_payload_guard)
    mutations = {
        "wrong_exit": (pass_scenario, 1, valid_json, ""),
        "signal": (pass_scenario, -9, valid_json, ""),
        "traceback": (
            pass_scenario,
            0,
            "Traceback (most recent call last):\n" + valid_json,
            "",
        ),
        "malformed_json": (pass_scenario, 0, "{", ""),
        "mixed_json_text": (pass_scenario, 0, valid_json + "\nextra", ""),
        "stderr": (pass_scenario, 0, valid_json, "unexpected"),
        "malformed_envelope": (
            failure_scenario,
            1,
            json.dumps({**valid_failure_payload, "findings": None}),
            "",
        ),
        "wrong_result": (
            failure_scenario,
            1,
            json.dumps({**valid_failure_payload, "result": "blocked"}),
            "",
        ),
        "wrong_code_multiset": (
            failure_scenario,
            1,
            json.dumps({
                **valid_failure_payload,
                "findings": [
                    failure_finding,
                    {
                        **failure_finding,
                        "reason": "duplicate self-test failure",
                    },
                ],
            }),
            "",
        ),
        "wrong_boundary": (
            pass_scenario,
            0,
            json.dumps({**valid_pass_payload, "proof_boundary": "wrong"}),
            "",
        ),
        "wrong_mechanically_checked": (
            pass_scenario,
            0,
            json.dumps({
                **valid_pass_payload,
                "mechanically_checked": ["different claim"],
            }),
            "",
        ),
        "wrong_not_checked": (
            pass_scenario,
            0,
            json.dumps({
                **valid_pass_payload,
                "not_checked": ["different limit"],
            }),
            "",
        ),
        "wrong_human_gate": (
            domain_scenario,
            1,
            json.dumps({
                **valid_domain_payload,
                "human_gate": {
                    "status": "not_checked",
                    "reason": "No human approval is inferred.",
                },
            }),
            "",
        ),
        "wrong_domain_result": (
            domain_scenario,
            1,
            json.dumps({
                **valid_domain_payload,
                "domain_result": "fail_closed",
            }),
            "",
        ),
        "wrong_derived_state": (
            domain_scenario,
            1,
            json.dumps({
                **valid_domain_payload,
                "derived_state": "fail_closed",
            }),
            "",
        ),
        "wrong_payload_field": (
            payload_scenario,
            0,
            json.dumps({
                **valid_payload_guard,
                "writes_performed": True,
            }),
            "",
        ),
        "boolean_payload_field_as_integer": (
            payload_scenario,
            0,
            json.dumps({
                **valid_payload_guard,
                "writes_performed": 0,
            }),
            "",
        ),
        "integer_payload_field_as_float": (
            payload_scenario,
            0,
            json.dumps({
                **valid_payload_guard,
                "claim_count": 1.0,
            }),
            "",
        ),
        "claim_index_as_boolean": (
            payload_scenario,
            0,
            json.dumps({
                **valid_payload_guard,
                "claims": [
                    {
                        **guarded_claims[0],
                        "index": True,
                    }
                ],
            }),
            "",
        ),
        "literal_length_as_float": (
            payload_scenario,
            0,
            json.dumps({
                **valid_payload_guard,
                "claims": [
                    {
                        **guarded_claims[0],
                        "literal_length": 14.0,
                    }
                ],
            }),
            "",
        ),
        "wrong_exact_claim_records": (
            payload_scenario,
            0,
            json.dumps({
                **valid_payload_guard,
                "claims": [
                    {
                        **guarded_claims[0],
                        "literal": "secret-literal",
                    }
                ],
            }),
            "",
        ),
        "unexpected_top_level_payload_key": (
            payload_scenario,
            0,
            json.dumps({
                **valid_payload_guard,
                "target_content": "redacted",
            }),
            "",
        ),
        "forbidden_output_fragment": (
            payload_scenario,
            0,
            json.dumps({
                **valid_payload_guard,
                "human_gate": {
                    "status": "not_checked",
                    "reason": "secret-literal",
                },
            }),
            "",
        ),
        "escaped_forbidden_output_fragment": (
            payload_scenario,
            0,
            json.dumps({
                **valid_payload_guard,
                "human_gate": {
                    "status": "not_checked",
                    "reason": "secret-literal",
                },
            }).replace("secret-literal", "secret\\u002dliteral"),
            "",
        ),
        "duplicate_top_level_json_key": (
            payload_scenario,
            0,
            valid_payload_json.replace(
                "{",
                '{"writes_performed": true, ',
                1,
            ),
            "",
        ),
        "duplicate_nested_json_key": (
            payload_scenario,
            0,
            valid_payload_json.replace(
                '"human_gate": {',
                '"human_gate": {"status": "required", ',
                1,
            ),
            "",
        ),
    }
    failures: list[str] = []
    baseline_errors, _payload = scenario_output_errors(
        payload_scenario,
        returncode=0,
        stdout=json.dumps(valid_payload_guard),
        stderr="",
    )
    if baseline_errors:
        failures.append("valid_payload_baseline")
    failures.extend(
        name
        for name, (scenario, returncode, stdout, stderr) in mutations.items()
        if not scenario_output_errors(
            scenario,
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
        )[0]
    )
    if not _scenario_unchanged_path_errors(
        immutability_scenario,
        {"fixture": "before"},
        {"fixture": "after"},
    ):
        failures.append("changed_path_fingerprint")
    if _scenario_unchanged_path_errors(
        immutability_scenario,
        {"fixture": "same"},
        {"fixture": "same"},
    ):
        failures.append("unchanged_path_fingerprint")
    if failures:
        print(
            "FAIL: scenario runner accepted mutation(s): "
            + ", ".join(failures)
        )
        return 1
    print(
        "Scenario runner self-tests passed: "
        f"{len(mutations) + 1} mutation(s) rejected; "
        "payload and immutability baselines passed."
    )
    return 0


def print_captured_output(output: str) -> None:
    if output.strip():
        print(output.rstrip())


def run_many(commands: tuple[tuple[str, ...], ...]) -> int:
    failures: list[tuple[tuple[str, ...], str]] = []
    for command in commands:
        result = run_captured(command)
        if result.returncode != 0:
            failures.append((command, result.stdout))
    if failures:
        for command, output in failures:
            print(f"FAIL: command failed: {format_command(command)}")
            print_captured_output(output)
        print(f"FAIL: {len(failures)} command(s) failed.")
        return 1
    print(f"Checks passed: {len(commands)} command(s).")
    return 0


def run_expected_failures(commands: tuple[tuple[str, ...], ...]) -> int:
    unexpected_passes: list[tuple[tuple[str, ...], str]] = []
    unexpected_crashes: list[tuple[tuple[str, ...], str]] = []
    unexpected_exit_codes: list[
        tuple[tuple[str, ...], int, str]
    ] = []
    for command in commands:
        result = run_captured(command)
        if result.returncode == 0:
            unexpected_passes.append((command, result.stdout))
        elif result.returncode != 1:
            unexpected_exit_codes.append(
                (command, result.returncode, result.stdout)
            )
        elif any(
            marker in result.stdout
            for marker in (
                "Traceback (most recent call last):",
                "SyntaxError:",
                "ModuleNotFoundError:",
                "ImportError:",
            )
        ):
            unexpected_crashes.append((command, result.stdout))
    if unexpected_passes or unexpected_crashes or unexpected_exit_codes:
        for command, output in unexpected_passes:
            print(f"FAIL: expected command to fail, but it passed: {format_command(command)}")
            print_captured_output(output)
        for command, output in unexpected_crashes:
            print(
                "FAIL: expected governance rejection, but command crashed: "
                f"{format_command(command)}"
            )
            print_captured_output(output)
        for command, returncode, output in unexpected_exit_codes:
            print(
                "FAIL: expected governance rejection with exit code 1, but "
                f"command returned {returncode}: {format_command(command)}"
            )
            print_captured_output(output)
        print(
            "FAIL: "
            f"{len(unexpected_passes)} expected-failure check(s) unexpectedly passed; "
            f"{len(unexpected_crashes)} crashed with exit code 1; "
            f"{len(unexpected_exit_codes)} returned another code or signal."
        )
        return 1
    print(f"Expected-failure checks passed: {len(commands)} command(s) failed as expected.")
    return 0


def run_expected_successes(commands: tuple[tuple[str, ...], ...]) -> int:
    failures: list[tuple[tuple[str, ...], str]] = []
    for command in commands:
        result = run_captured(command)
        if result.returncode != 0:
            failures.append((command, result.stdout))
    if failures:
        for command, output in failures:
            print(f"FAIL: expected command to pass, but it failed: {format_command(command)}")
            print_captured_output(output)
        print(f"FAIL: {len(failures)} expected-success check(s) failed.")
        return 1
    print(f"Expected-success checks passed: {len(commands)} command(s) passed as expected.")
    return 0


def run_case_group(group: NegativeCaseGroup) -> int:
    if group.mode == COMMANDS_PASS:
        return run_many(group.commands)
    if group.mode == EXPECTED_FAILURE:
        return run_expected_failures(group.commands)
    if group.mode == EXPECTED_SUCCESS:
        return run_expected_successes(group.commands)
    print(f"FAIL: unsupported negative case mode: {group.mode}")
    return 1


def run_negative_case_capture(case: str) -> tuple[int, str]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        result = run_negative_case(case)
    return result, buffer.getvalue()


def run_changed_path_hygiene_checks() -> int:
    return run_case_group(NEGATIVE_CASE_GROUPS["changed-paths"])


def run_textual_negative_checks() -> int:
    return run_case_group(NEGATIVE_CASE_GROUPS["textual"])


def run_negative_case(case: str) -> int:
    if case == "all":
        children = list(NEGATIVE_CASE_GROUPS)
        failures: list[tuple[str, str]] = []
        for child in children:
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                result = run_case_group(NEGATIVE_CASE_GROUPS[child])
            output = buffer.getvalue()
            if result != 0:
                failures.append((child, output))
        exact_buffer = io.StringIO()
        with contextlib.redirect_stdout(exact_buffer):
            exact_result = run_json_scenarios()
            runner_result = run_scenario_runner_self_tests()
        if exact_result or runner_result:
            failures.append(("retained-json-or-runner", exact_buffer.getvalue()))
        if failures:
            for child, output in failures:
                print(f"FAIL: negative case group failed: {child}")
                print_captured_output(output)
            print(f"FAIL: {len(failures)} negative case group(s) failed.")
            return 1
        print(
            "Negative and exact scenario checks passed: "
            f"{len(children)} legacy group(s), {len(JSON_SCENARIOS)} JSON "
            f"scenario(s), {len(PARITY_SCENARIOS)} parity scenario(s)."
        )
        return 0

    if case == "retained-json":
        return run_json_scenarios()
    if case == "scenario-runner":
        return run_scenario_runner_self_tests()
    if case == "controlled-errors":
        return run_json_scenarios("controlled-errors")

    group = NEGATIVE_CASE_GROUPS.get(case)
    exact_exists = any(scenario.group == case for scenario in JSON_SCENARIOS)
    parity_exists = any(scenario.group == case for scenario in PARITY_SCENARIOS)
    if group is None and not exact_exists and not parity_exists:
        print(f"FAIL: unsupported negative case group: {case}")
        return 1
    legacy_result = run_case_group(group) if group is not None else 0
    exact_result = (
        run_json_scenarios(case)
        if exact_exists or parity_exists
        else 0
    )
    return 1 if legacy_result or exact_result else 0
