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
- Work that only a person can check (in a headset, a browser, on a rig) stays open after merge
  until that person records the evidence on the issue. Its pull request references the issue
  without a closing keyword.
- Never report a scientific result, a data-quality claim, or rig behaviour as verified because
  tests or CI passed.

## Work tracking

- The board, its fields and their options, the issue forms, and the closing-keyword rule are
  defined per repository in `docs/agents/TRACKING.md`. Read it before filing, moving, or closing
  an issue. This file does not repeat field names, because they differ between repositories.
- A repository without `docs/agents/TRACKING.md` names its work authority in `AGENTS.md`.

## Shared kit

- This repository pins `lab-repo-kit` in `.lab-repo-kit/VERSION`, in the reusable-workflow `@tag`,
  and in `.pre-commit-config.yaml` `rev:`. Keep all three equal.
- Never update the kit automatically or from `main`. An update is one pull request that changes
  all three pins and re-vendors this file.

## Git

- Stage specific files. Never `git add .` or `git commit -a`.
- Do not push to `main` or merge without explicit human authorization.
