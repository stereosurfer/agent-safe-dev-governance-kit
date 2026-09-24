"""Compatibility import for preview.1 tests; the root library owns behavior."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from asgk_lib.github_workflow import *  # noqa: F401,F403
