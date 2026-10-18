"""Tests use synthetic files created in a temporary directory only."""

import re
import subprocess
import sys
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


BOM = "\ufeff"


def test_bom_does_not_hide_participant_column(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for ext, sep in (("csv", ","), ("tsv", "\t")):
        body = f"participant_id{sep}score\nX{sep}1\n"
        plain = _write(tmp_path, f"plain.{ext}", body)
        bom = _write(tmp_path, f"bom.{ext}", BOM + body)
        assert check_file(plain) == check_file(bom)
        assert any("participant_id" in r for r in check_file(bom))


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_help_named_file_flagged_via_subprocess(tmp_path):
    (tmp_path / "--help").write_text("participant_id,score\nX,1\n")
    (tmp_path / "-h").write_text("ok\n")
    (tmp_path / "data.csv").write_text("participant_id,score\nX,1\n")
    cmd = [sys.executable, "-m", "lab_repo_kit.raw_data_guard", "--"]
    # Names that argparse would read as options sit after the -- separator.
    (tmp_path / "--he.csv").write_text("participant_id,score\nX,1\n")
    proc = subprocess.run(
        [*cmd, "--help", "-h", "--he.csv", "data.csv"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "--he.csv: participant columns" in proc.stdout
    assert "usage:" not in proc.stdout


def test_abbreviation_not_accepted():
    proc = subprocess.run(
        [sys.executable, "-m", "lab_repo_kit.raw_data_guard", "--he"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    assert "usage:" not in proc.stdout


def test_callers_pass_separator():
    hook = (REPO_ROOT / ".pre-commit-hooks.yaml").read_text()
    entry = re.search(r"^\s*entry:\s*(.+)$", hook, re.MULTILINE).group(1).strip()
    assert entry.split() == ["lab-raw-data-guard", "--"]
    for name in ("raw-data-check.yml", "ci.yml"):
        text = (REPO_ROOT / ".github" / "workflows" / name).read_text()
        lines = [ln for ln in text.splitlines() if "xargs" in ln and "lab-raw-data-guard" in ln]
        assert lines, name
        assert all(re.search(r"lab-raw-data-guard\s+--\s*$", ln) for ln in lines), name
