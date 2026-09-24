#!/usr/bin/env python3
"""Compatibility entry for the canonical root GitHub workflow implementation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from asgk_lib.workflow_common import (  # noqa: F401
    Invalid, canonical, digest, load, path_name, record, require, save_bundle,
    strings, timestamp, words,
)


def main(argv=None):
    from asgk_lib.github_workflow import main as workflow_main
    return workflow_main(argv)


if __name__ == "__main__":
    sys.exit(main())
