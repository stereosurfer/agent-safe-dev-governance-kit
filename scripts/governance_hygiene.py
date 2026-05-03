#!/usr/bin/env python3
"""Dependency-light governance hygiene checker.

The checker validates newline-delimited changed-path lists. Its default mode is
positive validation: any blocked path returns a non-zero exit code.

For opt-in negative fixtures, pass ``--expect-blocked``. In that mode, the
command succeeds only when at least one blocked path is found. This lets the
repository prove that known-bad path fixtures are still blocked without loading
those fixtures as positive examples.
"""

from __future__ import annotations

import argparse
from pathlib import Path


PROTECTED_PATTERNS = [
    ".env",
    ".env.",
    "secrets/",
    "credentials/",
    "private_keys/",
    "node_modules/",
    ".git/",
]

BINARY_PRIVATE_SUFFIXES = [
    ".pdf",
    ".epub",
    ".docx",
    ".pptx",
    ".xlsx",
    ".png",
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
]

ALLOWED_GENERATED_PREFIXES = ["tests/fixtures/", "examples/"]
RUNTIME_ARTIFACT_PREFIXES = ["runs/", "corpus/", "artifacts/"]


def normalize_path(path: str) -> str:
    """Normalize path text from git/GitHub style lists.

    This is intentionally conservative. It does not resolve symlinks or touch the
    filesystem; it only normalizes textual path separators and leading ``./``.
    """

    cleaned = path.strip().replace("\\", "/")
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    return cleaned


def load_paths(paths_file: Path) -> list[str]:
    """Read path lines, ignoring blanks and comment lines.

    Negative fixtures commonly include YAML-ish metadata in comments. Those
    comments must not be treated as repository paths.
    """

    paths: list[str] = []
    for raw_line in paths_file.read_text(encoding="utf-8").splitlines():
        path = normalize_path(raw_line)
        if not path or path.startswith("#"):
            continue
        paths.append(path)
    return paths


def is_blocked(path: str) -> str | None:
    p = normalize_path(path)

    for pattern in PROTECTED_PATTERNS:
        if p == pattern.rstrip("/") or p.startswith(pattern):
            return f"protected path: {pattern}"

    if any(p.lower().endswith(suffix) for suffix in BINARY_PRIVATE_SUFFIXES):
        if not any(p.startswith(prefix) for prefix in ALLOWED_GENERATED_PREFIXES):
            return "private/binary source-like file outside fixture/example path"

    for prefix in RUNTIME_ARTIFACT_PREFIXES:
        if p.startswith(prefix) and not any(
            p.startswith(allowed_prefix) for allowed_prefix in ALLOWED_GENERATED_PREFIXES
        ):
            return f"runtime artifact path: {prefix}"

    return None


def collect_failures(paths: list[str]) -> list[tuple[str, str]]:
    failures: list[tuple[str, str]] = []
    for path in paths:
        reason = is_blocked(path)
        if reason:
            failures.append((path, reason))
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check changed paths for protected paths and runtime artifacts."
    )
    parser.add_argument("--paths-file", required=True, help="Newline-delimited path list.")
    parser.add_argument(
        "--expect-blocked",
        action="store_true",
        help="Succeed only when the paths file contains at least one blocked path.",
    )
    args = parser.parse_args()

    paths = load_paths(Path(args.paths_file))
    failures = collect_failures(paths)

    for path, reason in failures:
        print(f"BLOCKED {path}: {reason}")

    if args.expect_blocked:
        if failures:
            print(
                f"Governance hygiene negative check passed: {len(failures)} blocked path(s) detected."
            )
            return 0
        print("FAIL: expected at least one blocked path, but none were detected.")
        return 1

    if failures:
        print(f"FAIL: {len(failures)} blocked path(s) detected.")
        return 1

    print(f"Governance hygiene check passed: {len(paths)} path(s) checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
