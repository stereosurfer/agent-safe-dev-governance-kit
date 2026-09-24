#!/usr/bin/env python3
"""Shared validation and safe-output helpers for the canonical GitHub workflow."""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


class Invalid(ValueError):
    def __init__(self, code, field, reason):
        self.finding = dict(code=code, field=field, reason=reason, blocking=True)
        super().__init__(reason)


def require(ok, code, field, reason):
    if not ok:
        raise Invalid(code, field, reason)


def record(value, keys, field):
    require(type(value) is dict and set(value) == set(keys.split()),
            'SHAPE', field, 'Expected exactly: ' + keys)


def words(value, field):
    require(type(value) is str and bool(value.strip()) and len(value) <= 10000,
            'TEXT', field, 'Expected nonempty text of at most 10000 characters')


def strings(value, field, nonempty=False):
    require(type(value) is list and (not nonempty or len(value) > 0),
            'LIST', field, 'Expected a list' + (' with content' if nonempty else ''))
    for item in value:
        words(item, field)
    require(len(value) == len(set(value)), 'DUPLICATE', field, 'Duplicate entries')


def path_name(value, field):
    words(value, field)
    require(not value.startswith('/') and '\\' not in value and ':' not in value
            and not any(ord(c) < 32 or ord(c) == 127 for c in value)
            and all(p not in ('', '.', '..') for p in value.split('/'))
            and not any(c in value for c in '*?[]'),
            'PATH', field, 'Expected exact normalized relative file path')


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def timestamp(value, field):
    words(value, field)
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if result.tzinfo is None or result.utcoffset().total_seconds() != 0:
            raise ValueError()
        return result
    except ValueError:
        raise Invalid('TIME', field, 'Expected ISO-8601 UTC timestamp')


def load(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'DUPLICATE_KEY', key, 'Duplicate JSON key')
            result[key] = value
        return result
    def constant(value):
        raise Invalid('JSON', 'input', 'Non-finite JSON number: ' + value)
    with Path(path).open(encoding='utf-8') as stream:
        return json.load(stream, object_pairs_hook=pairs, parse_constant=constant)


def save_bundle(out, files):
    out = Path(out)
    require(not out.exists() and not out.is_symlink(), 'OUTPUT_EXISTS', 'out', 'Choose a new output directory')
    require(out.parent.is_dir(), 'OUTPUT_PARENT', 'out', 'Parent directory must exist')
    for name in files:
        path_name(name, 'output')
    out.mkdir()
    for name, value in files.items():
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('x', encoding='utf-8') as stream:
            stream.write(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + '\n')
