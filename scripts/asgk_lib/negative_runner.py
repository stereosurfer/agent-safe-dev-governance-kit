"""Compatibility projection of the canonical W3C scenario runner."""

from __future__ import annotations

from asgk_lib.scenario_runner import (
    run_changed_path_hygiene_checks,
    run_expected_failures,
    run_negative_case,
    run_textual_negative_checks,
)

__all__ = [
    "run_changed_path_hygiene_checks",
    "run_expected_failures",
    "run_negative_case",
    "run_textual_negative_checks",
]
