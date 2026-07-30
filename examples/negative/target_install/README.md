# Target Install Negative Fixtures

These fixtures exercise the current legacy target-install checker. They are
mechanical regression inputs, not target-fit or adoption-readiness examples.

Run them with:

```bash
python3 scripts/asgk.py negative target-install
```

They are not wired into default CI.

`missing_required_files` proves only that the current checker enforces its
legacy fixed file list. It does not prove that a target without those
ASGK-named files has a semantic governance defect. The historical-evidence
fixture separately checks the universal source-state isolation boundary.
