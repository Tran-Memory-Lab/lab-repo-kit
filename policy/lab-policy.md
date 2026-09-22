<!-- Vendored from Tran-Memory-Lab/lab-repo-kit. Do not edit here; update the kit and bump
     .lab-repo-kit/VERSION in a pull request. -->
# Tran Memory Lab shared agent policy

## Data boundary

- Never commit raw participant data, raw gaze or eye-tracking logs, raw exports, participant
  identifiers, or uncurated video or audio. Raw materials stay in approved institutional storage.
- Commit only synthetic fixtures, de-identified toy datasets, schemas, and test manifests.
  Synthetic fixtures live under `fixtures/synthetic/`.
- The raw-data hook and CI check are guardrails, not proof. Renamed files and data inside
  archives can pass them. If you are unsure whether a file is participant data, do not commit it;
  ask.

## Merge is not verification

- A merged pull request shows review and integration only. It is never physical rig verification
  and never scientific verification.
- For a headset-required issue (`Rig Verification: Needs Headset Check`), write `Refs #N` in the
  pull request description, never `Closes`, `Fixes`, or `Resolves`. The issue stays open in
  `In Review` until a person records rig evidence, sets `Verified on Rig`, and closes it.
- Code-only issues may use `Closes #N`.
- Never report a scientific result, a data-quality claim, or rig behaviour as verified because
  tests or CI passed.

## Shared kit

- This repository pins `lab-repo-kit` in `.lab-repo-kit/VERSION`, in the reusable-workflow `@tag`,
  and in `.pre-commit-config.yaml` `rev:`. Keep all three equal.
- Never update the kit automatically or from `main`. An update is one pull request that changes
  all three pins and re-vendors this file.

## Git

- Stage specific files. Never `git add .` or `git commit -a`.
- Do not push to `main` or merge without explicit human authorization.
