"""Tests use synthetic files created in a temporary directory only."""

from pathlib import Path

from lab_repo_kit.raw_data_guard import check_file, main


def _write(root: Path, rel: str, text: str = "") -> str:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return str(path.relative_to(root))


def test_participant_header_flagged(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rel = _write(tmp_path, "analysis/table.csv", "participant_id,score\nX,1\n")
    assert any("participant columns" in r for r in check_file(rel))


def test_gaze_header_flagged(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rel = _write(tmp_path, "out/eye.tsv", "time\tgaze_x\tgaze_y\n0\t0\t0\n")
    assert any("raw gaze" in r for r in check_file(rel))


def test_media_and_archive_extensions_flagged(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for name in ("session.mp4", "audio.m4a", "bundle.zip", "rec.edf"):
        rel = _write(tmp_path, name)
        assert any("blocked extension" in r for r in check_file(rel)), name


def test_participant_path_flagged(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rel = _write(tmp_path, "data/raw/notes.txt", "x")
    assert any("participant-data path" in r for r in check_file(rel))


def test_size_flagged(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rel = _write(tmp_path, "big.txt", "x" * (5 * 1024 * 1024 + 1))
    assert any("larger than" in r for r in check_file(rel))


def test_synthetic_fixture_allowed_but_media_still_blocked(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ok = _write(tmp_path, "tests/fixtures/synthetic/toy.csv", "participant_id,gaze_x\nSYN1,0\n")
    assert check_file(ok) == []
    bad = _write(tmp_path, "tests/fixtures/synthetic/clip.mp4")
    assert check_file(bad)


def test_clean_code_passes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rel = _write(tmp_path, "src/model.py", "x = 1\n")
    assert main([rel]) == 0


def test_known_false_negative_renamed_file(tmp_path, monkeypatch):
    """Documented limitation: a renamed recording with a harmless extension passes."""
    monkeypatch.chdir(tmp_path)
    rel = _write(tmp_path, "notes/session.txt", "binary-looking video bytes")
    assert check_file(rel) == []
