"""Audit and verify organization repository taxonomy compliance.

Checks all repositories across Tran-Memory-Lab for:
1. Valid `repo-category` custom property
2. Active repository topics
3. Baseline category topic alignment
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from typing import Any, Sequence

DEFAULT_ORG = "Tran-Memory-Lab"

ALLOWED_CATEGORIES = [
    "task-desktop",
    "experiment-vr",
    "shared-resource",
    "template",
    "infra",
]

EXPECTED_BASELINE_TOPICS: dict[str, list[str]] = {
    "task-desktop": ["desktop-task"],
    "experiment-vr": ["vr-experiment"],
    "shared-resource": ["lab-resource"],
    "template": ["repo-template"],
    "infra": ["organization-profile", "community-health"],
}


def fetch_org_properties(org: str = DEFAULT_ORG) -> dict[str, str | None]:
    """Fetch custom property values for all repositories in the organization."""
    cmd = ["gh", "api", f"/orgs/{org}/properties/values"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Failed to query org properties: {res.stderr.strip()}")

    results: dict[str, str | None] = {}
    for item in json.loads(res.stdout):
        name = item.get("repository_name")
        props = {p["property_name"]: p["value"] for p in item.get("properties", [])}
        results[name] = props.get("repo-category")
    return results


def fetch_repo_topics(repo_name: str, org: str = DEFAULT_ORG) -> list[str]:
    """Fetch assigned topics for a specific repository."""
    cmd = ["gh", "api", f"/repos/{org}/{repo_name}/topics"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return []
    return json.loads(res.stdout).get("names", [])


def audit_repository(
    repo_name: str,
    category: str | None,
    topics: list[str],
    strict: bool = True,
) -> tuple[bool, list[str]]:
    """Audit a single repository for taxonomy compliance."""
    issues: list[str] = []

    # 1. Category check
    if not category:
        issues.append("Missing 'repo-category' custom property")
    elif category not in ALLOWED_CATEGORIES:
        issues.append(f"Invalid 'repo-category': '{category}'")

    # 2. Topic presence check
    if not topics:
        issues.append("No repository topics assigned")
    elif strict and category in EXPECTED_BASELINE_TOPICS:
        expected = EXPECTED_BASELINE_TOPICS[category]
        if not any(exp in topics for exp in expected):
            issues.append(f"Missing expected baseline topic(s) ({', '.join(expected)})")

    is_compliant = len(issues) == 0
    return is_compliant, issues


def run_audit(
    org: str = DEFAULT_ORG,
    target_repo: str | None = None,
    strict: bool = True,
    markdown_path: str | None = None,
) -> int:
    """Run full taxonomy audit across organization repositories."""
    if not shutil.which("gh"):
        print("Error: 'gh' CLI is required but not found in PATH.", file=sys.stderr)
        return 1

    print(f"Auditing taxonomy compliance for organization '{org}'...\n")
    try:
        org_props = fetch_org_properties(org)
    except Exception as e:
        print(f"Error fetching organization properties: {e}", file=sys.stderr)
        return 1

    repos_to_check = [target_repo] if target_repo else sorted(org_props.keys())

    audit_records: list[dict[str, Any]] = []
    total_violations = 0

    for repo in repos_to_check:
        category = org_props.get(repo)
        topics = fetch_repo_topics(repo, org=org)
        compliant, issues = audit_repository(repo, category, topics, strict=strict)
        if not compliant:
            total_violations += 1

        audit_records.append({
            "repo": repo,
            "category": category or "UNASSIGNED",
            "topics": topics,
            "compliant": compliant,
            "issues": issues,
        })

    # Print Console Summary
    header = f"{'Repository':<26} | {'repo-category':<17} | {'Status':<8} | {'Topics / Issues'}"
    print(header)
    print("-" * len(header) + "-" * 25)
    for rec in audit_records:
        status_str = "✓ PASS" if rec["compliant"] else "✗ FAIL"
        details = ", ".join(rec["topics"]) if rec["compliant"] else f"ISSUES: {'; '.join(rec['issues'])}"
        print(f"{rec['repo']:<26} | {rec['category']:<17} | {status_str:<8} | {details}")

    print("\n" + "=" * 65)
    print(f"Summary: {len(audit_records) - total_violations}/{len(audit_records)} repositories compliant.")
    if total_violations > 0:
        print(f"WARNING: {total_violations} repository taxonomy violation(s) detected.")
    else:
        print("All audited repositories meet organizational taxonomy standards.")
    print("=" * 65)

    # Output Markdown Report if requested or in GitHub Actions
    gh_step_summary = os.getenv("GITHUB_STEP_SUMMARY")
    target_md = markdown_path or gh_step_summary

    if target_md:
        md_lines = [
            f"# Organization Taxonomy Audit Report — {org}",
            "",
            f"**Status:** {'✅ All Repositories Compliant' if total_violations == 0 else f'⚠️ {total_violations} Non-Compliant Repositories Detected'}",
            "",
            "| Repository | `repo-category` | Status | Topics / Issues |",
            "| :--- | :--- | :--- | :--- |",
        ]
        for rec in audit_records:
            icon = "✅ Pass" if rec["compliant"] else "❌ Fail"
            topic_or_issue = f"`{', '.join(rec['topics'])}`" if rec["compliant"] else f"**Issues:** {', '.join(rec['issues'])}"
            md_lines.append(f"| `{rec['repo']}` | `{rec['category']}` | {icon} | {topic_or_issue} |")

        md_content = "\n".join(md_lines) + "\n"
        try:
            with open(target_md, "a" if gh_step_summary and target_md == gh_step_summary else "w") as f:
                f.write(md_content)
            if not gh_step_summary or target_md != gh_step_summary:
                print(f"Markdown report written to {target_md}")
        except Exception as e:
            print(f"Warning: Failed to write markdown report: {e}", file=sys.stderr)

    return 1 if total_violations > 0 else 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit Tran-Memory-Lab repository taxonomy compliance.")
    parser.add_argument("--org", default=DEFAULT_ORG, help=f"Organization name (default: {DEFAULT_ORG})")
    parser.add_argument("--repo", help="Check a single repository instead of all")
    parser.add_argument(
        "--no-strict",
        action="store_true",
        help="Skip category baseline topic matching check",
    )
    parser.add_argument("--markdown", "-m", help="Path to write Markdown report")

    args = parser.parse_args(argv)
    return run_audit(
        org=args.org,
        target_repo=args.repo,
        strict=not args.no_strict,
        markdown_path=args.markdown,
    )


if __name__ == "__main__":
    sys.exit(main())
