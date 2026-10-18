"""Report drift between a consuming repository and the pinned lab-repo-kit release.

Reads .lab-repo-kit/VERSION in the consuming repository and checks, against a checkout
of the kit at that tag:

- vendored policy files match the kit's policy/*.md, with none missing, modified, or surplus;
- every kit reference in .pre-commit-config.yaml and .github/workflows/*.yml(.yaml)
  (hook rev, ``uses:`` tag, pip-install tag, ``kit-ref``, ``KIT_REF``) equals ``v`` plus
  the vendored VERSION.

Reports only; never rewrites the consuming repository. Scanning is line-based, so no
YAML dependency is needed.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

KIT_URL_FRAGMENT = "Tran-Memory-Lab/lab-repo-kit"

_REPO_LINE = re.compile(r"^\s*-?\s*repo:\s*(\S+)")
_REV_LINE = re.compile(r"""^\s*rev:\s*['"]?([^\s'"#]+)""")
_USES = re.compile(r"""\buses:\s*['"]?[^\s'"@]*lab-repo-kit(?:/[^\s'"@]*)?@([^\s'"#]+)""")
_PIP = re.compile(r"""lab-repo-kit(?:\.git)?@([^\s'"#]+)""")
_KIT_REF = re.compile(r"""\bkit-ref:[ \t]*['"]?([^\s'"},#]+)""")
_KIT_REF_ENV = re.compile(r"""\bKIT_REF:[ \t]*['"]?([^\s'"},#]+)""")


def _is_expression(ref: str) -> bool:
    return ref.startswith("$") or "${" in ref


def _precommit_refs(path: Path) -> list[tuple[int, str, str]]:
    """Return (line, kind, ref) for the kit entry's ``rev:`` in a pre-commit config."""
    found: list[tuple[int, str, str]] = []
    in_kit = False
    for no, line in enumerate(path.read_text().splitlines(), 1):
        repo = _REPO_LINE.match(line)
        if repo:
            in_kit = KIT_URL_FRAGMENT in repo.group(1)
            continue
        rev = _REV_LINE.match(line)
        if in_kit and rev:
            found.append((no, "rev", rev.group(1)))
            in_kit = False
    return found


def _workflow_refs(path: Path) -> list[tuple[int, str, str]]:
    found: list[tuple[int, str, str]] = []
    for no, line in enumerate(path.read_text().splitlines(), 1):
        if line.lstrip().startswith("#"):
            continue
        if "uses:" in line:
            m = _USES.search(line)
            if m:
                found.append((no, "uses", m.group(1)))
                continue
        else:
            m = _PIP.search(line)
            if m:
                found.append((no, "pip", m.group(1)))
        for kind, pattern in (("kit-ref", _KIT_REF), ("KIT_REF", _KIT_REF_ENV)):
            m = pattern.search(line)
            if m:
                found.append((no, kind, m.group(1)))
    return [r for r in found if not _is_expression(r[2])]


def _summary(refs: list[tuple[int, str, str]]) -> str:
    counts = Counter((kind, ref) for _, kind, ref in refs)
    return ", ".join(
        (f"{kind} @{ref}" if kind in ("uses", "pip") else f"{kind} {ref}")
        + (f" (x{n})" if n > 1 else "")
        for (kind, ref), n in counts.items()
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--repo", default=".", help="consuming repository root")
    parser.add_argument("--kit", required=True, help="kit checkout at the pinned tag")
    args = parser.parse_args(argv)

    repo = Path(args.repo)
    vendored = repo / ".lab-repo-kit"
    kit = Path(args.kit)
    pinned = (vendored / "VERSION").read_text().strip()
    released = (kit / "VERSION").read_text().strip()
    expected = f"v{pinned}"
    drift: list[str] = []
    notes: list[str] = []
    checked = [f".lab-repo-kit/VERSION {pinned}", f"kit checkout {released}"]

    if pinned != released:
        drift.append(f"VERSION {pinned} != kit checkout {released}")

    kit_policy = {p.name for p in (kit / "policy").glob("*.md")}
    for name in sorted(kit_policy):
        src, dst = kit / "policy" / name, vendored / name
        if not dst.exists():
            drift.append(f"missing {dst}")
        elif dst.read_text() != src.read_text():
            drift.append(f"modified {dst}")
    for dst in sorted(vendored.glob("*.md")):
        if dst.name not in kit_policy:
            drift.append(f"surplus {dst}")

    def judge(label: str, refs: list[tuple[int, str, str]]) -> None:
        for no, _, ref in refs:
            if ref != expected:
                drift.append(f"{label}:{no} pins {ref}, expected {expected}")

    precommit = repo / ".pre-commit-config.yaml"
    if not precommit.is_file():
        notes.append("no .pre-commit-config.yaml; hook pin not checked")
    else:
        refs = _precommit_refs(precommit)
        if not refs:
            notes.append(
                f".pre-commit-config.yaml has no {KIT_URL_FRAGMENT} entry; hook pin not checked"
            )
        else:
            judge(".pre-commit-config.yaml", refs)
            checked.append(f".pre-commit-config.yaml rev {refs[0][2]}")

    workflows = repo / ".github" / "workflows"
    files = (
        sorted([*workflows.glob("*.yml"), *workflows.glob("*.yaml")]) if workflows.is_dir() else []
    )
    for wf in files:
        refs = _workflow_refs(wf)
        if refs:
            label = wf.relative_to(repo).as_posix()
            judge(label, refs)
            checked.append(f"{label}: {_summary(refs)}")

    print("checked: " + "; ".join(checked))
    for note in notes:
        print(f"note: {note}")
    for line in drift:
        print(f"drift: {line}")
    if not drift:
        print(f"vendored policy and pins match lab-repo-kit {expected}")
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
