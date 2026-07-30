# Missing Required Files Fixture

This fixture intentionally omits files required by the current legacy
`target-install-check` implementation and should fail that mechanical command.

The failure proves only that the checker enforces a fixed ASGK file list. It
does not prove that the target repository is semantically incomplete, that
equivalent target-owned governance is absent, or that ASGK adoption is needed.
