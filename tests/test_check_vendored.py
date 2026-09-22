from lab_repo_kit.check_vendored import main


def _kit(tmp_path, version="0.1.0", text="policy\n"):
    kit = tmp_path / "kit"
    (kit / "policy").mkdir(parents=True)
    (kit / "VERSION").write_text(version + "\n")
    (kit / "policy" / "lab-policy.md").write_text(text)
    return kit


def _repo(tmp_path, version="0.1.0", text="policy\n"):
    repo = tmp_path / "repo"
    (repo / ".lab-repo-kit").mkdir(parents=True)
    (repo / ".lab-repo-kit" / "VERSION").write_text(version + "\n")
    (repo / ".lab-repo-kit" / "lab-policy.md").write_text(text)
    return repo


def test_match(tmp_path):
    assert main(["--repo", str(_repo(tmp_path)), "--kit", str(_kit(tmp_path))]) == 0


def test_modified_policy_reported(tmp_path):
    repo = _repo(tmp_path, text="edited locally\n")
    assert main(["--repo", str(repo), "--kit", str(_kit(tmp_path))]) == 1


def test_version_mismatch_reported(tmp_path):
    repo = _repo(tmp_path, version="0.0.9")
    assert main(["--repo", str(repo), "--kit", str(_kit(tmp_path))]) == 1
