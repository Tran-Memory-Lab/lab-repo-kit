# Changelog

## v0.3.0 — 2026-10-27

- New `lab-init-repo`: creates a Tran-Memory-Lab repository with its taxonomy custom properties
  and topics set.
- New `lab-check-taxonomy`: audits every organization repository for custom-property and topic
  compliance. `taxonomy-audit.yml` runs it weekly (Mondays 12:00 UTC), on demand, and as a
  reusable workflow with an optional `kit-ref` input (default `main`, for the kit's own schedule).
  Its token comes from `ORG_TAXONOMY_TOKEN`, then `GH_PAT`, then `GITHUB_TOKEN`.
- New reusable workflow `python-syntax-check.yml` (`workflow_call`, inputs `python-version` and
  `paths`): byte-compiles the tree and runs `ruff check --select E9,F63,F7,F82`. Call it at a tag;
  its usage comment pointed at `@main` before this release.
- No change to `lab-raw-data-guard`, `lab-check-vendored`, or `policy/lab-policy.md`. Consumers
  bump their pins and `.lab-repo-kit/VERSION` together, as before.

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
