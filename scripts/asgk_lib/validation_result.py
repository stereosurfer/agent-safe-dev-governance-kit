from __future__ import annotations

from collections.abc import Iterable, Mapping
import re
from typing import Any


RESULT_VALUES = frozenset({"pass", "fail", "blocked", "warning"})
HUMAN_GATE_STATUS_VALUES = frozenset(
    {"not_checked", "not_applicable", "required"}
)
FINDING_CODE_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")

DEFAULT_HUMAN_GATE_REASON = (
    "This mechanical validator does not establish or infer human approval."
)


def make_finding(
    code: str,
    reason: str,
    *,
    field: str | None = None,
    path: str | None = None,
    blocking: bool,
    **extra: object,
) -> dict[str, object]:
    if (field is None) == (path is None):
        raise ValueError("a validation finding requires exactly one of field or path")
    if not FINDING_CODE_PATTERN.fullmatch(code):
        raise ValueError(
            "a validation finding code must match ^[A-Z][A-Z0-9_]*$"
        )
    if not reason.strip():
        raise ValueError("a validation finding reason must be material")
    location = field if field is not None else path
    if not isinstance(location, str) or not location.strip():
        raise ValueError("a validation finding location must be material")
    finding: dict[str, object] = {
        "code": code,
        "reason": reason,
        "blocking": blocking,
    }
    if field is not None:
        finding["field"] = field
    else:
        finding["path"] = path
    finding.update(extra)
    return finding


def human_gate(
    status: str = "not_checked",
    *,
    reason: str = DEFAULT_HUMAN_GATE_REASON,
) -> dict[str, str]:
    if status not in HUMAN_GATE_STATUS_VALUES:
        raise ValueError(f"unsupported human-gate status: {status}")
    return {"status": status, "reason": reason}


def validation_result_errors(value: object) -> list[str]:
    if not isinstance(value, Mapping):
        return ["validation result must be an object"]

    errors: list[str] = []
    result = value.get("result")
    if result not in RESULT_VALUES:
        errors.append(
            "result must be exactly pass, fail, blocked, or warning"
        )

    evidence_source = value.get("evidence_source")
    if not isinstance(evidence_source, str) or not evidence_source.strip():
        errors.append("evidence_source must be a material string")

    for field_name in ("mechanically_checked", "not_checked"):
        field_value = value.get(field_name)
        if not isinstance(field_value, list):
            errors.append(f"{field_name} must be an array")
            continue
        if not field_value:
            errors.append(f"{field_name} must contain at least one material item")
        for index, item in enumerate(field_value):
            if not isinstance(item, str) or not item.strip():
                errors.append(
                    f"{field_name}[{index}] must be a material string"
                )

    gate = value.get("human_gate")
    if not isinstance(gate, Mapping):
        errors.append("human_gate must be an object")
    else:
        gate_status = gate.get("status")
        if gate_status not in HUMAN_GATE_STATUS_VALUES:
            errors.append(
                "human_gate.status must be not_checked, not_applicable, or required"
            )
        gate_reason = gate.get("reason")
        if not isinstance(gate_reason, str) or not gate_reason.strip():
            errors.append("human_gate.reason must be a material string")
        extra_gate_keys = set(gate) - {"status", "reason"}
        if extra_gate_keys:
            errors.append(
                "human_gate contains unsupported keys: "
                + ", ".join(sorted(str(key) for key in extra_gate_keys))
            )
        if gate_status == "required" and result != "blocked":
            errors.append(
                "human_gate.status required is valid only for blocked results"
            )

    proof_boundary = value.get("proof_boundary")
    if not isinstance(proof_boundary, str) or not proof_boundary.strip():
        errors.append("proof_boundary must be a material string")

    findings = value.get("findings")
    if not isinstance(findings, list):
        errors.append("findings must be an array")
        return errors

    blocking_count = 0
    for index, finding in enumerate(findings):
        prefix = f"findings[{index}]"
        if not isinstance(finding, Mapping):
            errors.append(f"{prefix} must be an object")
            continue
        code = finding.get("code")
        if (
            not isinstance(code, str)
            or FINDING_CODE_PATTERN.fullmatch(code) is None
        ):
            errors.append(
                f"{prefix}.code must match ^[A-Z][A-Z0-9_]*$"
            )
        reason = finding.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{prefix}.reason must be a material string")
        blocking = finding.get("blocking")
        if not isinstance(blocking, bool):
            errors.append(f"{prefix}.blocking must be boolean")
        elif blocking:
            blocking_count += 1
        has_field_key = "field" in finding
        has_path_key = "path" in finding
        if has_field_key == has_path_key:
            errors.append(
                f"{prefix} must contain exactly one field or path key"
            )
        else:
            location_key = "field" if has_field_key else "path"
            location = finding.get(location_key)
            if not isinstance(location, str) or not location.strip():
                errors.append(
                    f"{prefix}.{location_key} must be a material string"
                )

    if result == "pass" and findings:
        errors.append("pass results must not contain findings")
    if result == "warning" and (not findings or blocking_count):
        errors.append(
            "warning results require nonblocking findings and no blocking finding"
        )
    if result in {"fail", "blocked"} and blocking_count == 0:
        errors.append(f"{result} results require at least one blocking finding")

    return errors


def complete_validation_result(
    report: Mapping[str, object],
    *,
    evidence_source: str,
    mechanically_checked: Iterable[str],
    not_checked: Iterable[str],
    proof_boundary: str,
    human_gate_status: str = "not_checked",
    human_gate_reason: str = DEFAULT_HUMAN_GATE_REASON,
    result_map: Mapping[str, str] | None = None,
) -> dict[str, object]:
    output = dict(report)
    original_result = str(output.get("result") or "")
    mapped_result = (
        result_map.get(original_result, original_result)
        if result_map is not None
        else original_result
    )
    if mapped_result != original_result:
        output.setdefault("domain_result", original_result)
    output["result"] = mapped_result
    output["evidence_source"] = evidence_source
    output["mechanically_checked"] = list(dict.fromkeys(mechanically_checked))
    output["not_checked"] = list(dict.fromkeys(not_checked))
    output["human_gate"] = human_gate(
        human_gate_status,
        reason=human_gate_reason,
    )
    output["proof_boundary"] = proof_boundary
    output.setdefault("findings", [])
    return output


def internal_envelope_failure(
    errors: Iterable[str],
    *,
    evidence_source: str,
    proof_boundary: str,
) -> dict[str, object]:
    material_errors = [error for error in errors if error.strip()]
    reason = "; ".join(material_errors) or "validation envelope is invalid"
    return {
        "result": "fail",
        "evidence_source": evidence_source,
        "mechanically_checked": [
            "common validation-result envelope shape",
        ],
        "not_checked": [
            "the validator's intended domain claim",
            "human approval, merge authority, or semantic correctness",
        ],
        "human_gate": human_gate(),
        "proof_boundary": proof_boundary,
        "findings": [
            make_finding(
                "VR_INTERNAL_ENVELOPE_INVALID",
                reason,
                field="validation_result",
                blocking=True,
            )
        ],
    }


def checked_validation_result(
    report: Mapping[str, object],
    *,
    evidence_source: str,
    mechanically_checked: Iterable[str],
    not_checked: Iterable[str],
    proof_boundary: str,
    human_gate_status: str = "not_checked",
    human_gate_reason: str = DEFAULT_HUMAN_GATE_REASON,
    result_map: Mapping[str, str] | None = None,
) -> dict[str, object]:
    output = complete_validation_result(
        report,
        evidence_source=evidence_source,
        mechanically_checked=mechanically_checked,
        not_checked=not_checked,
        proof_boundary=proof_boundary,
        human_gate_status=human_gate_status,
        human_gate_reason=human_gate_reason,
        result_map=result_map,
    )
    errors = validation_result_errors(output)
    if errors:
        return internal_envelope_failure(
            errors,
            evidence_source=evidence_source,
            proof_boundary=(
                "The common envelope self-check failed. No domain validation "
                "claim, approval, or merge authority was established."
            ),
        )
    return output
