from lab_repo_kit.check_vendored import main

PRECOMMIT = """repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v9.9.9
    hooks:
      - id: ruff
  - repo: https://github.com/Tran-Memory-Lab/lab-repo-kit
    rev: {rev}
    hooks:
      - id: lab-raw-data-guard
"""

WORKFLOW = """name: lab-checks
on: [pull_request]
env:
  KIT_REF: {env}
jobs:
  raw-data:
    uses: Tran-Memory-Lab/lab-repo-kit/.github/workflows/raw-data-check.yml@{uses1}
    with: {{ kit-ref: {inline} }}
  kit-drift:
    uses: Tran-Memory-Lab/lab-repo-kit/.github/workflows/kit-drift.yml@{uses2}
    with:
      kit-ref: {block}
  other:
    steps:
      - run: pip install "git+https://github.com/Tran-Memory-Lab/lab-repo-kit@${{{{ inputs.kit-ref }}}}"
"""

GOOD = {
    "rev": "v0.2.0",
    "env": "v0.2.0",
    "uses1": "v0.2.0",
    "uses2": "v0.2.0",
    "inline": "v0.2.0",
    "block": "v0.2.0",
}


def _kit(tmp_path, version="0.2.0", text="policy\n"):
    kit = tmp_path / "kit"
    (kit / "policy").mkdir(parents=True)
    (kit / "VERSION").write_text(version + "\n")
    (kit / "policy" / "lab-policy.md").write_text(text)
    return kit


def _repo(tmp_path, version="0.2.0", text="policy\n", pins=None, precommit=True):
    pins = {**GOOD, **(pins or {})}
    repo = tmp_path / "repo"
    (repo / ".lab-repo-kit").mkdir(parents=True)
    (repo / ".lab-repo-kit" / "VERSION").write_text(version + "\n")
    (repo / ".lab-repo-kit" / "lab-policy.md").write_text(text)
    if precommit:
        (repo / ".pre-commit-config.yaml").write_text(PRECOMMIT.format(rev=pins["rev"]))
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "lab-checks.yml").write_text(WORKFLOW.format(**pins))
    return repo


def _run(tmp_path, repo):
    return main(["--repo", str(repo), "--kit", str(_kit(tmp_path))])


def test_match(tmp_path, capsys):
    assert _run(tmp_path, _repo(tmp_path)) == 0
    out = capsys.readouterr().out
    assert ".lab-repo-kit/VERSION 0.2.0; kit checkout 0.2.0" in out
    assert ".pre-commit-config.yaml rev v0.2.0" in out
    for part in ("uses @v0.2.0 (x2)", "kit-ref v0.2.0 (x2)", "KIT_REF v0.2.0"):
        assert part in out


def test_modified_policy_reported(tmp_path):
    assert _run(tmp_path, _repo(tmp_path, text="edited locally\n")) == 1


def test_version_mismatch_reported(tmp_path):
    assert _run(tmp_path, _repo(tmp_path, version="0.0.9")) == 1


def test_surplus_policy_reported(tmp_path, capsys):
    repo = _repo(tmp_path)
    (repo / ".lab-repo-kit" / "stale-old.md").write_text("old\n")
    assert _run(tmp_path, repo) == 1
    assert "drift: surplus" in capsys.readouterr().out


def test_each_pin_checked_independently(tmp_path, capsys):
    for key in ("rev", "uses1", "inline", "block", "env"):
        sub = tmp_path / key
        sub.mkdir()
        assert _run(sub, _repo(sub, pins={key: "v0.1.0"})) == 1, key
        out = capsys.readouterr().out
        assert "pins v0.1.0, expected v0.2.0" in out, key
        assert out.count("drift:") == 1, key


def test_missing_precommit_config_is_note(tmp_path, capsys):
    assert _run(tmp_path, _repo(tmp_path, precommit=False)) == 0
    assert "note: no .pre-commit-config.yaml" in capsys.readouterr().out
