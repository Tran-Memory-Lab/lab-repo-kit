# lab-repo-kit

Versioned shared tooling for Tran Memory Lab repositories: the raw-data hook, validators,
reusable CI workflows, and agent-policy text for vendoring. Consuming repositories pin a release
tag and update only through an explicit pull request. Nothing here updates a repository on its own.

## Pinned consumption (v0.1.0)

Keep these three pins equal.

**1. Pre-commit hook** — `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/Tran-Memory-Lab/lab-repo-kit
    rev: v0.1.0
    hooks:
      - id: lab-raw-data-guard
```

**2. Reusable workflows** — `.github/workflows/lab-checks.yml`:

```yaml
name: lab-checks
on: [pull_request, push]
jobs:
  raw-data:
    uses: Tran-Memory-Lab/lab-repo-kit/.github/workflows/raw-data-check.yml@v0.1.0
    with: { kit-ref: v0.1.0 }
  kit-drift:
    uses: Tran-Memory-Lab/lab-repo-kit/.github/workflows/kit-drift.yml@v0.1.0
    with: { kit-ref: v0.1.0 }
```

**3. Vendored policy** — copy `policy/*.md` into `.lab-repo-kit/` and write `0.1.0` to
`.lab-repo-kit/VERSION`. Reference `.lab-repo-kit/lab-policy.md` from the repository's
`AGENTS.md`; do not edit the vendored copy.

## Updating to a new release

One pull request that bumps the hook `rev`, both workflow `@tag`s and `kit-ref`s, re-copies
`policy/*.md`, and updates `.lab-repo-kit/VERSION`. `kit-drift` fails until all agree.

## What the raw-data guard does and does not catch

It flags blocked extensions (video, audio, eye-tracking recordings, archives, spreadsheets),
participant-data paths (`raw/`, `participants/`, `sub-01`, `P001_`, `uxf_data/`), files over
5 MB, and CSV/TSV headers with participant-identifier or raw-gaze columns. Files under
`fixtures/synthetic/` skip the path and header checks but not the extension and size checks.

**Known false negatives:** renamed files with harmless extensions, data inside archives or
unopened binary formats, identifiers in free text or unlisted column names, and anything
committed with `--no-verify`. On GitHub Free, CI on private repositories reports failures but
cannot block a merge. These are guardrails; reviewers still have to look.

## Development

```bash
pip install -e . pytest
pytest -q
```

Test data is synthetic only.
