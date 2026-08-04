#!/usr/bin/env python3
"""Compatibility entrypoint for the canonical ASGK source validator."""

from asgk_lib.source_validation import main


if __name__ == "__main__":
    raise SystemExit(main())
