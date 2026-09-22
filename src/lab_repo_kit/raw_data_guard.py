"""Flag files that look like raw participant data.

A guardrail, not proof. It checks path, extension, size, and CSV/TSV headers.
Known false negatives: renamed files, data inside archives or binary formats it
does not open, identifiers in free text, and headers it has no pattern for.
"""

from __future__ import annotations

import argparse
import csv
import fnmatch
import re
import sys
from pathlib import Path

MAX_BYTES = 5 * 1024 * 1024

BLOCKED_EXTENSIONS = {
    # uncurated video/audio
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
    ".webm",
    ".wav",
    ".m4a",
    ".mp3",
    ".flac",
    ".aac",
    ".ogg",
    # eye-tracking and physiology recordings
    ".edf",
    ".asc",
    ".idf",
    ".gazedata",
    ".tsv.gz",
    ".xdf",
    ".bdf",
    ".fif",
    # archives can hide anything
    ".zip",
    ".7z",
    ".tar",
    ".gz",
    ".rar",
    # spreadsheets and survey exports
    ".xlsx",
    ".xls",
    ".sav",
    ".qsf.csv",
}

BLOCKED_PATH_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"(^|/)raw(_?data)?/",
        r"(^|/)participants?/",
        r"(^|/)sub-[0-9]+",
        r"(^|/)P[0-9]{3,}[_/.-]",
        r"(^|/)uxf_data/",
        r"(^|/)recordings?/",
        r"(^|/)exports?/raw",
    )
]

PARTICIPANT_COLUMNS = {
    "participant_id",
    "participant",
    "ppid",
    "subject_id",
    "subject",
    "name",
    "first_name",
    "last_name",
    "email",
    "phone",
    "dob",
    "date_of_birth",
    "birth_date",
    "address",
    "mrn",
    "gtid",
    "sona_id",
    "ip_address",
    "prolific_pid",
}
GAZE_COLUMNS = {
    "gaze_x",
    "gaze_y",
    "gaze_origin_x",
    "gaze_direction_x",
    "pupil_diameter",
    "left_pupil",
    "right_pupil",
    "eye_openness",
    "fixation_x",
    "combined_gaze_x",
}

SYNTHETIC_DIR_GLOBS = ("*/fixtures/synthetic/*", "fixtures/synthetic/*")


def _is_synthetic(path: str) -> bool:
    return any(fnmatch.fnmatch(path, g) for g in SYNTHETIC_DIR_GLOBS)


def _extension(path: Path) -> str:
    name = path.name.lower()
    for ext in sorted(BLOCKED_EXTENSIONS, key=len, reverse=True):
        if name.endswith(ext):
            return ext
    return path.suffix.lower()


def _header(path: Path) -> list[str]:
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    try:
        with path.open(newline="", encoding="utf-8", errors="replace") as fh:
            row = next(csv.reader(fh, delimiter=delimiter), [])
    except OSError:
        return []
    return [c.strip().lower() for c in row]


def check_file(path_str: str) -> list[str]:
    """Return reasons this file looks like raw data (empty if none)."""
    reasons: list[str] = []
    path = Path(path_str)
    posix = path.as_posix()
    synthetic = _is_synthetic(posix)

    ext = _extension(path)
    if ext in BLOCKED_EXTENSIONS:
        reasons.append(f"blocked extension {ext}")
    if not synthetic:
        for pattern in BLOCKED_PATH_PATTERNS:
            if pattern.search(posix):
                reasons.append(f"participant-data path ({pattern.pattern})")
                break
    if path.is_file():
        if path.stat().st_size > MAX_BYTES:
            reasons.append(f"larger than {MAX_BYTES // (1024 * 1024)} MB")
        if not synthetic and path.suffix.lower() in {".csv", ".tsv"}:
            cols = set(_header(path))
            if cols & PARTICIPANT_COLUMNS:
                reasons.append(f"participant columns {sorted(cols & PARTICIPANT_COLUMNS)}")
            if cols & GAZE_COLUMNS:
                reasons.append(f"raw gaze columns {sorted(cols & GAZE_COLUMNS)}")
    return reasons


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*")
    args = parser.parse_args(argv)
    failed = 0
    for f in args.files:
        for reason in check_file(f):
            print(f"{f}: {reason}")
            failed = 1
    if failed:
        print(
            "\nLikely raw participant data. Keep it in approved institutional storage.\n"
            "Synthetic fixtures belong under fixtures/synthetic/ (extension and size checks still apply)."
        )
    return failed


if __name__ == "__main__":
    sys.exit(main())
