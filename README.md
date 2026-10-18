# lab-repo-kit

Versioned shared tooling for Tran Memory Lab repositories: the raw-data hook, validators,
reusable CI workflows, and agent-policy text for vendoring. Consuming repositories pin a release
tag (`v0.1.0`) and update only through an explicit pull request; nothing here updates a repository on its own.

This is a **Reusable Package & Tooling** repository. Consumers depend on tagged semantic versions — never point a downstream repository at a floating branch or untagged commit.

## Installation

Consuming repositories pin the release tag (`v0.1.0`) across their pre-commit configuration, reusable CI workflows, and vendored `.lab-repo-kit/VERSION` stamp. For local development or direct CLI invocation:

```bash
# Install a pinned release tag
pip install "git+https://github.com/Tran-Memory-Lab/lab-repo-kit.git@v0.1.0"

# Local editable install for development
pip install -e . pytest
```

## Quick start & usage

### Pinned consumption (`v0.1.0`)

Keep these three pins equal across every consuming repository:

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

### Updating a consuming repository to a new release

Open one pull request that bumps the hook `rev`, both workflow `@tag`s and `kit-ref`s, re-copies
`policy/*.md`, and updates `.lab-repo-kit/VERSION`. `kit-drift` fails until all agree.

## Public API & CLI reference

| Entry point / Artifact | Purpose | Stability |
|---|---|---|
| `lab-raw-data-guard` (`lab_repo_kit.raw_data_guard:main`) | Pre-commit hook and CLI validator checking paths, extensions, file size, and CSV/TSV headers | Experimental (`0.x`) |
| `lab-check-vendored` (`lab_repo_kit.check_vendored:main`) | Report-only drift check verifying `.lab-repo-kit/` and `.lab-repo-kit/VERSION` match the pinned release | Experimental (`0.x`) |
| `.github/workflows/raw-data-check.yml` | Reusable workflow (`workflow_call`, `kit-ref` input) running `lab-raw-data-guard` in CI | Experimental (`0.x`) |
| `.github/workflows/kit-drift.yml` | Reusable workflow (`workflow_call`, `kit-ref` input) checking vendored `.lab-repo-kit/` drift | Experimental (`0.x`) |
| `policy/lab-policy.md` | Agent-policy fragment copied into `.lab-repo-kit/lab-policy.md` in consuming repositories | Experimental (`0.x`) |

### What the raw-data guard does and does not catch

It flags blocked extensions (video, audio, eye-tracking recordings, archives, spreadsheets),
participant-data paths (`raw/`, `participants/`, `sub-01`, `P001_`, `uxf_data/`), files over
5 MB, and CSV/TSV headers with participant-identifier or raw-gaze columns. Files under
`fixtures/synthetic/` skip the path and header checks but not the extension and size checks.

**Known false negatives:** renamed files with harmless extensions, data inside archives or
unopened binary formats, identifiers in free text or unlisted column names, and anything
committed with `--no-verify`. On GitHub Free, CI on private repositories reports failures but
cannot block a merge. These are guardrails; reviewers still have to look.

## Repository layout

| Path | Role |
|---|---|
| `src/lab_repo_kit/` | Package source (`raw_data_guard.py`, `check_vendored.py`) |
| `policy/` | Vendored agent-policy fragments (`policy/lab-policy.md`) |
| `.github/workflows/` | Package CI (`ci.yml`) and reusable workflows (`raw-data-check.yml`, `kit-drift.yml`) |
| `.pre-commit-hooks.yaml` | Pre-commit hook definition (`lab-raw-data-guard`) |
| `tests/` | Unit and contract test suite (`fixtures/synthetic/` contains synthetic-only test data) |
| `pyproject.toml` | Package metadata, console script entry points, and Ruff configuration |
| `VERSION` | Canonical version string (`0.1.0`) |
| `CHANGELOG.md` | Release history and semantic-versioning notes |

## Development, tests & release policy

```bash
pip install -e . pytest
pytest -q
```

Test data is synthetic only.

- **Semantic versioning:** Breaking changes to CLI flags, reusable workflow inputs, or vendored policy filenames bump the major version (minor while `0.x`) and are recorded in `CHANGELOG.md`.
- **Releases:** Every release updates `VERSION` and `CHANGELOG.md` and is published as an annotated git tag (`vX.Y.Z`).

## Contributing

Open an issue or pull request against `main`, ensure `pytest -q` passes with synthetic-only fixtures, and keep `VERSION` and `CHANGELOG.md` synchronized when preparing a tagged release.

<!-- Public/Archival Release Checklist (uncomment and populate when publishing publicly):
## Public release, license & citation
- [ ] Add `LICENSE` (e.g., MIT or Apache-2.0) and verify dependency license compatibility.
- [ ] Add `CITATION.cff` and Zenodo DOI badge if the package is cited in academic work.
- [ ] Add CI status and release version badges at the top of `README.md`.
-->
