"""Report drift between vendored .lab-repo-kit/ files and the pinned kit release.

Reads .lab-repo-kit/VERSION in the consuming repository and compares each vendored
file with the same file in a checkout of the kit at that tag. Reports only; never
rewrites the consuming repository.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="consuming repository root")
    parser.add_argument("--kit", required=True, help="kit checkout at the pinned tag")
    args = parser.parse_args(argv)

    vendored = Path(args.repo) / ".lab-repo-kit"
    kit = Path(args.kit)
    pinned = (vendored / "VERSION").read_text().strip()
    released = (kit / "VERSION").read_text().strip()
    drift = []
    if pinned != released:
        drift.append(f"VERSION {pinned} != kit checkout {released}")
    for src in sorted((kit / "policy").glob("*.md")):
        dst = vendored / src.name
        if not dst.exists():
            drift.append(f"missing {dst}")
        elif dst.read_text() != src.read_text():
            drift.append(f"modified {dst}")
    for line in drift:
        print(f"drift: {line}")
    if not drift:
        print(f"vendored policy matches lab-repo-kit v{pinned}")
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
