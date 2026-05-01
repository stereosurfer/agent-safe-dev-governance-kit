#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path

PROTECTED_PATTERNS = ['.env', '.env.', 'secrets/', 'credentials/', 'private_keys/', 'node_modules/', '.git/']
BINARY_PRIVATE_SUFFIXES = ['.pdf','.epub','.docx','.pptx','.xlsx','.png','.jpg','.jpeg','.tif','.tiff']
ALLOWED_GENERATED_PREFIXES = ['tests/fixtures/', 'examples/']


def is_blocked(path: str) -> str | None:
    p = path.replace('\\','/')
    for pat in PROTECTED_PATTERNS:
        if p == pat.rstrip('/') or p.startswith(pat):
            return f'protected path: {pat}'
    if any(p.lower().endswith(s) for s in BINARY_PRIVATE_SUFFIXES):
        if not any(p.startswith(prefix) for prefix in ALLOWED_GENERATED_PREFIXES):
            return 'private/binary source-like file outside fixture/example path'
    if p.startswith('runs/') or p.startswith('corpus/') or p.startswith('artifacts/'):
        if not any(p.startswith(prefix) for prefix in ALLOWED_GENERATED_PREFIXES):
            return 'runtime artifact path'
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--paths-file', required=True)
    ns = ap.parse_args()
    paths = Path(ns.paths_file).read_text().splitlines()
    failures = []
    for p in paths:
        p = p.strip()
        if not p: continue
        reason = is_blocked(p)
        if reason:
            failures.append((p, reason))
    if failures:
        for p, reason in failures:
            print(f'BLOCKED {p}: {reason}')
        return 1
    print('Governance hygiene check passed.')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
