from __future__ import annotations

import re
from pathlib import Path

from asgk_lib.common import ROOT, rel
from asgk_lib.validation_result import checked_validation_result, make_finding


RELEASE_STATE_PROOF_BOUNDARY = (
    "Exit 0 proves only that the three named local documents were readable; "
    "README matched the supplied tag, title, and latest-completed-release "
    "assertions; and no configured tag-specific stale-state or duplicate-ledger "
    "pattern matched. It does not prove a tag or GitHub Release exists, validate "
    "GitHub metadata or a target commit, establish semantic release readiness or "
    "repository safety, authorize publication, satisfy a human gate, or assess "
    "any target repository; unnamed files and unrecognized wording were not "
    "checked."
)

RELEASE_STATE_NOT_CHECKED = (
    "unnamed files and unrecognized stale-state or ledger wording",
    "semantic truth, completeness, or release-readiness meaning of the documents",
    "Git tag or GitHub Release existence and metadata",
    "target commit identity, artifact contents, or distribution state",
    "human approval, publication authority, or rollback/revoke safety",
    "repository safety or target-repository state",
)

RELEASE_STATE_COMPLETE_CHECKED = (
    "release tag semver-like vX.Y.Z syntax",
    "release title materiality",
    (
        "README, CURRENT_STATUS, and SOURCE_ONLY_RELEASE_POLICY path existence "
        "and UTF-8 readability"
    ),
    (
        "README latest-completed source-only GitHub release marker presence "
        "and exact tag equality"
    ),
    "released tag literal presence in README",
    "release-title literal presence in README",
    (
        "configured tag-specific candidate, pending, and release-execution "
        "residue patterns across readable named documents"
    ),
    (
        "configured duplicate release-history ledger patterns in readable "
        "CURRENT_STATUS and SOURCE_ONLY_RELEASE_POLICY"
    ),
    "blocking-finding to common-result mapping",
)

RELEASE_STATE_HUMAN_GATE_REASON = (
    "This command checks only local release-state documents. It does not "
    "establish human approval for tag creation, GitHub Release publication, "
    "release close-out authority, or merge authority."
)


def release_version_tuple(tag: str) -> tuple[int, int, int] | None:
    match = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)", tag.strip())
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def find_latest_completed_readme_versions(text: str) -> list[str]:
    return re.findall(
        r"ASGK\s+(v\d+\.\d+\.\d+)\s+is\s+the\s+latest\s+completed\s+source-only\s+GitHub\s+release",
        text,
        flags=re.IGNORECASE,
    )


def release_state_stale_patterns(tag: str) -> list[tuple[str, str]]:
    escaped = re.escape(tag)
    return [
        (rf"{escaped}[^\n.]*candidate", f"{tag} is still described as candidate"),
        (rf"candidate[^\n.]*{escaped}", f"{tag} is still described as candidate"),
        (rf"{escaped}[^\n.]*pending", f"{tag} is still described as pending"),
        (rf"pending[^\n.]*{escaped}", f"{tag} is still described as pending"),
        (
            rf"{escaped}[^\n.]*requires[^\n.]*release execution",
            f"{tag} still appears to require release execution",
        ),
        (
            rf"{escaped}[^\n.]*tag or GitHub release requires",
            f"{tag} still appears to require tag or GitHub release creation",
        ),
        (
            rf"{escaped}[^\n.]*release execution[^\n.]*not_started",
            f"{tag} release execution is still marked not_started",
        ),
    ]


def release_ledger_patterns() -> dict[str, list[tuple[str, str]]]:
    return {
        "CURRENT_STATUS": [
            (
                r"Completed source-only releases are recorded in GitHub releases and release\s+issues:",
                "CURRENT_STATUS duplicates a release-history ledger",
            ),
        ],
        "SOURCE_ONLY_RELEASE_POLICY": [
            (
                r"^## v\d+\.\d+(?:\.\d+)? Release (?:Preparation|Execution) Record$",
                "SOURCE_ONLY_RELEASE_POLICY duplicates a per-release history ledger",
            ),
        ],
    }


def _display_path(value: str | Path) -> str:
    path = Path(value)
    if not path.is_absolute():
        return path.as_posix()
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _append_finding(
    findings: list[dict[str, object]],
    code: str,
    reason: str,
    *,
    field: str | None = None,
    path: str | None = None,
) -> None:
    findings.append(
        make_finding(
            code,
            reason,
            field=field,
            path=path,
            blocking=True,
        )
    )


def check_release_state_docs(
    *,
    tag: str,
    release_title: str,
    readme_path: str | Path,
    current_status_path: str | Path,
    release_policy_path: str | Path,
) -> dict[str, object]:
    findings: list[dict[str, object]] = []
    checked = list(RELEASE_STATE_COMPLETE_CHECKED[:3])
    not_checked = list(RELEASE_STATE_NOT_CHECKED)

    tag_valid = release_version_tuple(tag) is not None
    if not tag_valid:
        _append_finding(
            findings,
            "RS_TAG_INVALID",
            f"release tag must use semver-like vX.Y.Z syntax: {tag}",
            field="tag",
        )
    if not release_title.strip():
        _append_finding(
            findings,
            "RS_RELEASE_TITLE_MISSING",
            "release title must be a material string",
            field="release_title",
        )

    documents = (
        ("README", readme_path),
        ("CURRENT_STATUS", current_status_path),
        ("SOURCE_ONLY_RELEASE_POLICY", release_policy_path),
    )
    document_paths = {
        label: _display_path(path)
        for label, path in documents
    }
    texts: dict[str, str] = {}
    for label, raw_path in documents:
        path = rel(raw_path)
        display_path = document_paths[label]
        if not path.exists():
            _append_finding(
                findings,
                "RS_FILE_MISSING",
                f"required {label} release-state document is missing",
                path=display_path,
            )
            continue
        if not path.is_file():
            _append_finding(
                findings,
                "RS_FILE_UNREADABLE",
                f"required {label} release-state path is not a regular file",
                path=display_path,
            )
            continue
        try:
            texts[label] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            _append_finding(
                findings,
                "RS_FILE_UNREADABLE",
                f"required {label} release-state document is unreadable: {type(exc).__name__}",
                path=display_path,
            )

    readme = texts.get("README")
    if readme is not None and tag_valid:
        checked.extend(RELEASE_STATE_COMPLETE_CHECKED[3:5])
        latest_versions = find_latest_completed_readme_versions(readme)
        if not latest_versions:
            _append_finding(
                findings,
                "RS_README_LATEST_MISSING",
                (
                    "README does not identify the latest completed source-only "
                    "GitHub release"
                ),
                path=document_paths["README"],
            )
        elif any(version != tag for version in latest_versions):
            found = ", ".join(latest_versions)
            _append_finding(
                findings,
                "RS_README_LATEST_MISMATCH",
                f"README latest completed release is {found}, expected {tag}",
                path=document_paths["README"],
            )
        if tag not in readme:
            _append_finding(
                findings,
                "RS_README_TAG_MISSING",
                f"README does not mention released tag {tag}",
                path=document_paths["README"],
            )
    if readme is not None and release_title.strip():
        checked.append(RELEASE_STATE_COMPLETE_CHECKED[5])
        if release_title not in readme:
            _append_finding(
                findings,
                "RS_RELEASE_TITLE_MISSING",
                f"README does not contain the released title: {release_title}",
                path=document_paths["README"],
            )

    if texts:
        if tag_valid:
            checked.append(RELEASE_STATE_COMPLETE_CHECKED[6])
        else:
            not_checked.insert(
                0,
                (
                    "README exact tag equality, released-tag literal presence, "
                    "and tag-specific stale-state patterns because tag syntax "
                    "was invalid"
                ),
            )
        checked.append(RELEASE_STATE_COMPLETE_CHECKED[7])
        for label, text in texts.items():
            stale_reasons = (
                [
                    reason
                    for pattern, reason in release_state_stale_patterns(tag)
                    if re.search(pattern, text, flags=re.IGNORECASE)
                ]
                if tag_valid
                else []
            )
            if stale_reasons:
                _append_finding(
                    findings,
                    "RS_STALE_RELEASE_STATE",
                    "; ".join(dict.fromkeys(stale_reasons)),
                    path=document_paths[label],
                )

            ledger_reasons = [
                reason
                for pattern, reason in release_ledger_patterns().get(label, [])
                if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
            ]
            if ledger_reasons:
                _append_finding(
                    findings,
                    "RS_DUPLICATE_RELEASE_LEDGER",
                    "; ".join(dict.fromkeys(ledger_reasons)),
                    path=document_paths[label],
                )

    checked.append(RELEASE_STATE_COMPLETE_CHECKED[8])
    missing_labels = [
        label
        for label, _path in documents
        if label not in texts
    ]
    if missing_labels:
        not_checked.insert(
            0,
            (
                "content assertions for unavailable named documents: "
                + ", ".join(missing_labels)
            ),
        )

    report = {
        "result": "fail" if findings else "pass",
        "tag": tag,
        "release_title": release_title,
        "documents": [
            document_paths[label]
            for label, _path in documents
        ],
        "findings": findings,
    }
    return checked_validation_result(
        report,
        evidence_source="local_release_state_documents_and_command_arguments",
        mechanically_checked=checked,
        not_checked=not_checked,
        proof_boundary=RELEASE_STATE_PROOF_BOUNDARY,
        human_gate_reason=RELEASE_STATE_HUMAN_GATE_REASON,
    )
