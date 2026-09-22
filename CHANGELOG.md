# Changelog

## v0.1.0 — 2026-09-21

- `lab-raw-data-guard`: path, extension, size, and CSV/TSV header checks; pre-commit hook.
- `lab-check-vendored`: report-only drift check for `.lab-repo-kit/`.
- Reusable workflows `raw-data-check.yml` and `kit-drift.yml` (`workflow_call`, `kit-ref` input).
- Agent-policy fragment `policy/lab-policy.md` for vendoring.
