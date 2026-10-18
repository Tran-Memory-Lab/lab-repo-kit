# Changelog

## v0.2.0 — 2026-10-18

- Fix: a tracked file named `--help`, `-h`, or an argparse abbreviation such as `--he` made
  `lab-raw-data-guard` print help and exit 0. The hook entry, `raw-data-check.yml`, and `ci.yml`
  now pass `--` before filenames, and the parser sets `allow_abbrev=False`. **Callers that invoke
  `lab-raw-data-guard` themselves must pass `--` before filenames.**
- Fix: a UTF-8 BOM no longer hides a leading `participant_id` column in a CSV or TSV header.
- `lab-check-vendored` is stricter. It now reports vendored `.lab-repo-kit/*.md` files absent from
  the kit's `policy/` as `surplus`, and checks that every kit pin equals `v` + `.lab-repo-kit/VERSION`:
  the `.pre-commit-config.yaml` `rev`, `uses: ...@tag`, pip-install `@tag`, `kit-ref`, and `KIT_REF`
  in `.github/workflows/*.yml|yaml`. Consumers must bump all pins together. It prints which
  identities it checked; a missing pre-commit config is a note, not drift.

## v0.1.0 — 2026-09-21

- `lab-raw-data-guard`: path, extension, size, and CSV/TSV header checks; pre-commit hook.
- `lab-check-vendored`: report-only drift check for `.lab-repo-kit/`.
- Reusable workflows `raw-data-check.yml` and `kit-drift.yml` (`workflow_call`, `kit-ref` input).
- Agent-policy fragment `policy/lab-policy.md` for vendoring.
