#!/usr/bin/env python3
"""Evaluate explicit caller-supplied mechanical claims against a target tree.

This module owns no target layout, required-file set, adoption plan, or
governance-depth judgment. It reads only accepted paths under the supplied
target root and never writes to that root.
"""
from __future__ import annotations

import codecs
import hashlib
import json
import os
import stat
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence

from asgk_lib.validation_result import checked_validation_result, make_finding


TARGET_EVIDENCE_PROOF_BOUNDARY = (
    "Exit 0 proves only that every accepted caller-supplied mechanical claim "
    "matched the named observable target paths or literal text during this "
    "read-only run. It does not inspect unnamed target state or prove claim "
    "completeness or sufficiency, semantic correctness, security, privacy, "
    "license sufficiency, target fit, architecture or layout, governance "
    "depth, minimum adaptation, adoption or upgrade readiness or completeness, "
    "evaluator recommendation, human approval, implementation authority, PR "
    "readiness, or merge authority."
)

TARGET_EVIDENCE_DOMAIN_NOT_CHECKED = (
    "unnamed target paths, text, or other repository state",
    "completeness or sufficiency of caller-supplied claims",
    "semantic correctness, security, privacy, or license sufficiency",
    "target fit, architecture or layout, governance depth, or minimum adaptation",
    "adoption or upgrade readiness or completeness",
    "evaluator recommendation or implementation authority",
    "human approval, PR readiness, or merge authority",
    "concurrent target mutation during the read-only observation",
)

TARGET_EVIDENCE_COMPLETE_CHECKED = (
    "caller claim presence",
    "target root availability and directory shape",
    "claim path syntax, normalization, and resolved-root containment",
    "explicit path presence or absence for accepted path claims",
    "absent-path handling or case-sensitive literal containment for accepted in-root UTF-8 regular-file text claims",
    "aggregate target-evidence domain/common result mapping",
)

TARGET_EVIDENCE_NO_CLAIMS_CHECKED = (
    "caller claim presence",
    "target root availability and directory shape",
    "aggregate target-evidence domain/common result mapping",
)

TARGET_EVIDENCE_NO_CLAIMS_NOT_CHECKED = (
    "claim path syntax, normalization, and resolved-root containment because no claims were supplied",
    "target path or literal-text state because no claims were supplied",
    *TARGET_EVIDENCE_DOMAIN_NOT_CHECKED,
)

DOMAIN_RESULT_MAP = {
    "claims_match": "pass",
    "claims_mismatch": "fail",
    "incomplete": "blocked",
}

PATH_CLAIM_KINDS = frozenset({"expect_path", "forbid_path"})
TEXT_CLAIM_KINDS = frozenset({"expect_text", "forbid_text"})
GLOB_CHARACTERS = frozenset("*?[]")
READ_CHUNK_BYTES = 64 * 1024
MAX_SYMLINK_EXPANSIONS = 40
OPEN_DIRECTORY_FLAGS = (
    os.O_RDONLY
    | getattr(os, "O_CLOEXEC", 0)
    | getattr(os, "O_DIRECTORY", 0)
    | getattr(os, "O_NOFOLLOW", 0)
)
OPEN_FILE_FLAGS = (
    os.O_RDONLY
    | getattr(os, "O_CLOEXEC", 0)
    | getattr(os, "O_NOFOLLOW", 0)
)


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="surrogatepass")).hexdigest()


def _claim_inputs(
    *,
    expect_paths: Iterable[str],
    forbid_paths: Iterable[str],
    expect_texts: Iterable[Sequence[str]],
    forbid_texts: Iterable[Sequence[str]],
) -> list[tuple[str, str, str | None]]:
    claims: list[tuple[str, str, str | None]] = []
    claims.extend(("expect_path", path, None) for path in expect_paths)
    claims.extend(("forbid_path", path, None) for path in forbid_paths)
    claims.extend(
        ("expect_text", pair[0], pair[1])
        for pair in expect_texts
    )
    claims.extend(
        ("forbid_text", pair[0], pair[1])
        for pair in forbid_texts
    )
    return claims


def _normalized_claim_path(raw_path: str) -> tuple[PurePosixPath | None, str | None]:
    if not raw_path:
        return None, "claim path is empty"
    try:
        raw_path.encode("utf-8")
    except UnicodeEncodeError:
        return None, "claim path contains a non-Unicode-scalar value"
    if any(unicodedata.category(character) == "Cc" for character in raw_path):
        return None, "claim path contains a control character"
    if "\\" in raw_path:
        return None, "claim path must use normalized POSIX separators"
    if any(character in GLOB_CHARACTERS for character in raw_path):
        return None, "claim path contains unsupported glob syntax"
    if (
        len(raw_path) >= 2
        and raw_path[0] in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        and raw_path[1] == ":"
    ):
        return None, "claim path contains a drive-prefixed form"

    pure_path = PurePosixPath(raw_path)
    if pure_path.is_absolute():
        return None, "claim path must be repository-relative"

    raw_parts = raw_path.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        return None, "claim path contains an empty, dot, or parent segment"

    if pure_path.as_posix() != raw_path:
        return None, "claim path is not in exact normalized form"
    return pure_path, None


def _descriptor_containment_supported() -> bool:
    return (
        bool(getattr(os, "O_DIRECTORY", 0))
        and bool(getattr(os, "O_NOFOLLOW", 0))
        and os.open in os.supports_dir_fd
        and os.stat in os.supports_dir_fd
        and os.stat in os.supports_follow_symlinks
        and os.readlink in os.supports_dir_fd
    )


def _open_target_root(
    repo_root: str | Path,
) -> tuple[Path | None, int | None, str | None]:
    if not _descriptor_containment_supported():
        return (
            None,
            None,
            "descriptor-contained path observation is unavailable on this platform",
        )
    root_fd: int | None = None
    try:
        root_path = Path(repo_root).resolve(strict=True)
        root_fd = os.open(os.path.sep, OPEN_DIRECTORY_FLAGS)
        for component in root_path.parts[1:]:
            next_fd = os.open(
                component,
                OPEN_DIRECTORY_FLAGS,
                dir_fd=root_fd,
            )
            os.close(root_fd)
            root_fd = next_fd
        root_stat = os.fstat(root_fd)
        if not stat.S_ISDIR(root_stat.st_mode):
            os.close(root_fd)
            return None, None, "the supplied target root is not a directory"
    except (OSError, RuntimeError, UnicodeError) as exc:
        if root_fd is not None:
            os.close(root_fd)
        return None, None, f"target root could not be opened safely: {type(exc).__name__}"
    return root_path, root_fd, None


def _absolute_symlink_target_parts(
    root_path: Path,
    target: str,
) -> tuple[list[str] | None, str | None]:
    target_parts = [
        part
        for part in target.split(os.sep)
        if part not in {"", "."}
    ]
    root_parts = list(root_path.parts[1:])
    if target_parts[: len(root_parts)] != root_parts:
        return None, "claim path resolves outside the target root"
    return target_parts[len(root_parts) :], None


def _observe_claim_path(
    *,
    root_path: Path,
    root_fd: int,
    claim_path: PurePosixPath,
    open_text_file: bool,
) -> tuple[bool | None, int | None, str | None, str | None]:
    """Observe one claim through directory FDs without following path lookups.

    The returned problem kind is one of ``invalid``, ``path_unreadable``,
    ``not_file``, or ``text_unreadable``. A returned file descriptor is owned
    by the caller.
    """

    pending_parts = list(claim_path.parts)
    current_parts: list[str] = []
    try:
        directory_fds = [os.dup(root_fd)]
    except OSError as exc:
        return (
            None,
            None,
            "path_unreadable",
            f"target root descriptor could not be duplicated: {type(exc).__name__}",
        )
    named_final_present = False
    symlink_expansions = 0

    try:
        while True:
            if not pending_parts:
                if open_text_file:
                    return (
                        named_final_present,
                        None,
                        "not_file",
                        "The text claim path is not a readable regular file.",
                    )
                return named_final_present, None, None, None

            component = pending_parts.pop(0)
            if component in {"", "."}:
                continue
            if component == "..":
                if len(directory_fds) == 1:
                    return (
                        None,
                        None,
                        "invalid",
                        "claim path resolves outside the target root",
                    )
                os.close(directory_fds.pop())
                current_parts.pop()
                continue

            is_final_component = not pending_parts
            current_fd = directory_fds[-1]
            try:
                entry_stat = os.stat(
                    component,
                    dir_fd=current_fd,
                    follow_symlinks=False,
                )
            except FileNotFoundError:
                if named_final_present:
                    if open_text_file:
                        return (
                            True,
                            None,
                            "not_file",
                            "The text claim path is not a present regular file.",
                        )
                    return True, None, None, None
                return False, None, None, None
            except OSError as exc:
                return (
                    None,
                    None,
                    "path_unreadable",
                    f"path presence could not be observed: {type(exc).__name__}",
                )

            if stat.S_ISLNK(entry_stat.st_mode):
                if is_final_component:
                    named_final_present = True
                symlink_expansions += 1
                if symlink_expansions > MAX_SYMLINK_EXPANSIONS:
                    return (
                        None,
                        None,
                        "invalid",
                        "claim path contains too many symbolic-link expansions",
                    )
                try:
                    link_target = os.readlink(component, dir_fd=current_fd)
                except OSError as exc:
                    return (
                        None,
                        None,
                        "path_unreadable",
                        f"symbolic-link target could not be observed: {type(exc).__name__}",
                    )
                if os.path.isabs(link_target):
                    absolute_parts, expansion_problem = (
                        _absolute_symlink_target_parts(root_path, link_target)
                    )
                    if (
                        expansion_problem is not None
                        or absolute_parts is None
                    ):
                        return (
                            None,
                            None,
                            "invalid",
                            expansion_problem
                            or "symbolic-link target could not be contained",
                        )
                    while len(directory_fds) > 1:
                        os.close(directory_fds.pop())
                    current_parts = []
                    pending_parts = [*absolute_parts, *pending_parts]
                else:
                    pending_parts = [
                        *link_target.split(os.sep),
                        *pending_parts,
                    ]
                continue

            if is_final_component:
                named_final_present = True
                if not open_text_file:
                    return True, None, None, None
                if not stat.S_ISREG(entry_stat.st_mode):
                    return (
                        True,
                        None,
                        "not_file",
                        "The text claim path is not a readable regular file.",
                    )
                text_fd: int | None = None
                try:
                    text_fd = os.open(
                        component,
                        OPEN_FILE_FLAGS,
                        dir_fd=current_fd,
                    )
                    opened_stat = os.fstat(text_fd)
                except OSError as exc:
                    if text_fd is not None:
                        os.close(text_fd)
                    return (
                        True,
                        None,
                        "text_unreadable",
                        f"text evidence could not be opened safely: {type(exc).__name__}",
                    )
                if not stat.S_ISREG(opened_stat.st_mode):
                    os.close(text_fd)
                    return (
                        True,
                        None,
                        "not_file",
                        "The text claim path is not a readable regular file.",
                    )
                return True, text_fd, None, None

            if not stat.S_ISDIR(entry_stat.st_mode):
                return (
                    None,
                    None,
                    "path_unreadable",
                    "an intermediate claim-path component is not a directory",
                )
            try:
                next_fd = os.open(
                    component,
                    OPEN_DIRECTORY_FLAGS,
                    dir_fd=current_fd,
                )
            except OSError as exc:
                return (
                    None,
                    None,
                    "path_unreadable",
                    f"claim-path directory could not be opened safely: {type(exc).__name__}",
                )
            directory_fds.append(next_fd)
            current_parts.append(component)
    finally:
        for directory_fd in reversed(directory_fds):
            os.close(directory_fd)


def _literal_present(file_fd: int, literal: str) -> tuple[bool | None, str | None]:
    decoder = codecs.getincrementaldecoder("utf-8")("strict")
    overlap = max(len(literal) - 1, 0)
    tail = ""
    found = False
    try:
        while True:
            chunk = os.read(file_fd, READ_CHUNK_BYTES)
            if not chunk:
                break
            decoded = decoder.decode(chunk, final=False)
            combined = tail + decoded
            if literal in combined:
                found = True
            tail = combined[-overlap:] if overlap else ""
        final_text = decoder.decode(b"", final=True)
    except UnicodeDecodeError:
        return None, "text evidence is not valid UTF-8"
    except OSError as exc:
        return None, f"text evidence could not be read: {type(exc).__name__}"
    return found or literal in (tail + final_text), None


def _input_record(
    index: int,
    kind: str,
    raw_path: str,
    literal: str | None,
) -> dict[str, object]:
    record: dict[str, object] = {
        "index": index,
        "kind": kind,
        "status": "not_checked",
    }
    normalized, _problem = _normalized_claim_path(raw_path)
    if normalized is not None:
        record["path"] = normalized.as_posix()
    else:
        record["path_input_length"] = len(raw_path)
        record["path_sha256"] = _digest(raw_path)
    if literal is not None:
        record["literal_length"] = len(literal)
        record["literal_sha256"] = _digest(literal)
    return record


def evaluate_target_evidence(
    repo_root: str | Path,
    *,
    expect_paths: Iterable[str] = (),
    forbid_paths: Iterable[str] = (),
    expect_texts: Iterable[Sequence[str]] = (),
    forbid_texts: Iterable[Sequence[str]] = (),
) -> dict[str, object]:
    claim_inputs = _claim_inputs(
        expect_paths=expect_paths,
        forbid_paths=forbid_paths,
        expect_texts=expect_texts,
        forbid_texts=forbid_texts,
    )
    claim_records = [
        _input_record(index, kind, raw_path, literal)
        for index, (kind, raw_path, literal) in enumerate(claim_inputs, start=1)
    ]
    findings: list[dict[str, object]] = []

    root_path, root_fd, root_problem = _open_target_root(repo_root)
    if root_problem is not None or root_path is None or root_fd is None:
        findings.append(
            make_finding(
                "TE_TARGET_ROOT_UNAVAILABLE",
                "The supplied target root is unavailable or is not a directory.",
                field="repo_root",
                blocking=True,
            )
        )

    if not claim_inputs:
        findings.append(
            make_finding(
                "TE_CLAIMS_MISSING",
                "At least one caller-supplied target claim is required.",
                field="claims",
                blocking=True,
            )
        )

    saw_mismatch = False
    saw_incomplete = bool(findings)
    checked_path_claim = False
    checked_text_claim = False

    if root_path is not None and root_fd is not None:
        try:
            for record, (kind, raw_path, literal) in zip(
                claim_records,
                claim_inputs,
            ):
                claim_index = int(record["index"])
                claim_field = f"claims[{claim_index}]"
                claim_path, path_problem = _normalized_claim_path(raw_path)
                if path_problem is not None or claim_path is None:
                    findings.append(
                        make_finding(
                            "TE_CLAIM_PATH_INVALID",
                            path_problem or "claim path is invalid",
                            field=claim_field,
                            blocking=True,
                        )
                    )
                    saw_incomplete = True
                    continue

                if literal is not None and literal == "":
                    findings.append(
                        make_finding(
                            "TE_LITERAL_EMPTY",
                            "Literal-text claims require a non-empty caller literal.",
                            path=claim_path.as_posix(),
                            blocking=True,
                        )
                    )
                    saw_incomplete = True
                    continue
                if literal is not None:
                    try:
                        literal.encode("utf-8")
                    except UnicodeEncodeError:
                        findings.append(
                            make_finding(
                                "TE_LITERAL_INVALID",
                                "Literal-text claims require a Unicode-scalar value.",
                                path=claim_path.as_posix(),
                                blocking=True,
                            )
                        )
                        saw_incomplete = True
                        continue

                if kind not in PATH_CLAIM_KINDS | TEXT_CLAIM_KINDS:
                    findings.append(
                        make_finding(
                            "TE_CLAIM_KIND_INVALID",
                            "The claim kind is unsupported.",
                            field=claim_field,
                            blocking=True,
                        )
                    )
                    saw_incomplete = True
                    continue

                present, text_fd, observation_kind, observation_problem = (
                    _observe_claim_path(
                        root_path=root_path,
                        root_fd=root_fd,
                        claim_path=claim_path,
                        open_text_file=kind in TEXT_CLAIM_KINDS,
                    )
                )
                if observation_kind == "invalid":
                    findings.append(
                        make_finding(
                            "TE_CLAIM_PATH_INVALID",
                            observation_problem
                            or "claim path could not be contained",
                            path=claim_path.as_posix(),
                            blocking=True,
                        )
                    )
                    saw_incomplete = True
                    continue
                if observation_kind == "path_unreadable" or present is None:
                    findings.append(
                        make_finding(
                            "TE_PATH_UNREADABLE",
                            observation_problem
                            or "path presence could not be observed",
                            path=claim_path.as_posix(),
                            blocking=True,
                        )
                    )
                    saw_incomplete = True
                    continue

                if kind in PATH_CLAIM_KINDS:
                    checked_path_claim = True
                    matched = present if kind == "expect_path" else not present
                    record["status"] = "matched" if matched else "mismatched"
                    if not matched:
                        code = (
                            "TE_EXPECT_PATH_MISSING"
                            if kind == "expect_path"
                            else "TE_FORBID_PATH_PRESENT"
                        )
                        reason = (
                            "The expected path was not present."
                            if kind == "expect_path"
                            else "The forbidden path was present."
                        )
                        findings.append(
                            make_finding(
                                code,
                                reason,
                                path=claim_path.as_posix(),
                                blocking=True,
                            )
                        )
                        saw_mismatch = True
                    continue

                if not present and kind == "forbid_text":
                    checked_text_claim = True
                    record["status"] = "matched"
                    continue

                if not present or observation_kind == "not_file":
                    findings.append(
                        make_finding(
                            "TE_TEXT_TARGET_NOT_FILE",
                            observation_problem
                            or "The text claim path is not a present regular file.",
                            path=claim_path.as_posix(),
                            blocking=True,
                        )
                    )
                    saw_incomplete = True
                    continue

                if observation_kind == "text_unreadable" or text_fd is None:
                    findings.append(
                        make_finding(
                            "TE_TEXT_UNREADABLE",
                            observation_problem
                            or "text evidence could not be evaluated",
                            path=claim_path.as_posix(),
                            blocking=True,
                        )
                    )
                    saw_incomplete = True
                    continue

                try:
                    contains_literal, text_problem = _literal_present(
                        text_fd,
                        literal or "",
                    )
                finally:
                    os.close(text_fd)
                if contains_literal is None:
                    code = (
                        "TE_TEXT_NOT_UTF8"
                        if text_problem == "text evidence is not valid UTF-8"
                        else "TE_TEXT_UNREADABLE"
                    )
                    findings.append(
                        make_finding(
                            code,
                            text_problem or "text evidence could not be evaluated",
                            path=claim_path.as_posix(),
                            blocking=True,
                        )
                    )
                    saw_incomplete = True
                    continue

                checked_text_claim = True
                matched = (
                    contains_literal
                    if kind == "expect_text"
                    else not contains_literal
                )
                record["status"] = "matched" if matched else "mismatched"
                if not matched:
                    code = (
                        "TE_EXPECT_TEXT_NOT_FOUND"
                        if kind == "expect_text"
                        else "TE_FORBID_TEXT_FOUND"
                    )
                    reason = (
                        "The expected caller literal was not found."
                        if kind == "expect_text"
                        else "The forbidden caller literal was found."
                    )
                    findings.append(
                        make_finding(
                            code,
                            reason,
                            path=claim_path.as_posix(),
                            blocking=True,
                        )
                    )
                    saw_mismatch = True
        finally:
            os.close(root_fd)

    domain_result = (
        "incomplete"
        if saw_incomplete
        else "claims_mismatch"
        if saw_mismatch
        else "claims_match"
    )

    mechanically_checked = [
        "caller claim presence",
        "target root availability and directory shape",
    ]
    if root_path is not None and root_fd is not None and claim_inputs:
        mechanically_checked.append(
            "claim path syntax, normalization, and resolved-root containment"
        )
    if checked_path_claim:
        mechanically_checked.append(
            "explicit path presence or absence for accepted path claims"
        )
    if checked_text_claim:
        mechanically_checked.append(
            "absent-path handling or case-sensitive literal containment for "
            "accepted in-root UTF-8 regular-file text claims"
        )
    mechanically_checked.append(
        "aggregate target-evidence domain/common result mapping"
    )

    not_checked = list(TARGET_EVIDENCE_DOMAIN_NOT_CHECKED)
    if not claim_inputs:
        not_checked = list(TARGET_EVIDENCE_NO_CLAIMS_NOT_CHECKED)
    elif root_path is None or root_fd is None:
        not_checked.insert(
            0,
            "claim path containment and target state because the target root was unavailable",
        )
    elif any(record["status"] == "not_checked" for record in claim_records):
        not_checked.insert(
            0,
            "target evidence for claim records marked not_checked",
        )

    return checked_validation_result(
        {
            "result": domain_result,
            "derived_state": domain_result,
            "writes_performed": False,
            "claim_count": len(claim_records),
            "claims": claim_records,
            "findings": findings,
        },
        evidence_source="live_target_tree_and_caller_claims",
        mechanically_checked=mechanically_checked,
        not_checked=not_checked,
        proof_boundary=TARGET_EVIDENCE_PROOF_BOUNDARY,
        result_map=DOMAIN_RESULT_MAP,
    )


def print_target_evidence_result(
    report: dict[str, object],
    *,
    as_json: bool,
) -> int:
    if as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Target evidence state: {report.get('domain_result', 'incomplete')}")
        print("Writes performed: false")
        for claim in report.get("claims", []):
            if not isinstance(claim, dict):
                continue
            location = claim.get("path") or "<invalid path input>"
            print(
                f"- claim {claim.get('index')}: {claim.get('kind')} "
                f"{location} -> {claim.get('status')}"
            )
        for finding in report.get("findings", []):
            if not isinstance(finding, dict):
                continue
            location = finding.get("path") or finding.get("field") or "unknown"
            print(
                f"- {finding.get('code')}: {location}: "
                f"{finding.get('reason')}"
            )
        print(str(report.get("proof_boundary") or TARGET_EVIDENCE_PROOF_BOUNDARY))
    return 0 if report.get("domain_result") == "claims_match" else 1
