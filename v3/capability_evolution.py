#!/usr/bin/env python3
"""Compatibility import for the canonical root capability catalog implementation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from asgk_lib.capability_evolution import *  # noqa: F401,F403


if __name__ == '__main__':
    sys.exit(main())
