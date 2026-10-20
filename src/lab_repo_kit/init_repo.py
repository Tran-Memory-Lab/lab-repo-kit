"""Initialize a new repository in Tran-Memory-Lab with taxonomy properties and topics.

Provides CLI functionality to:
1. Create a repository under Tran-Memory-Lab (optionally from a template)
2. Assign the organization-level custom property `repo-category`
3. Assign category baseline topics and custom topics
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from typing import Sequence

DEFAULT_ORG = "Tran-Memory-Lab"

ALLOWED_CATEGORIES = [
    "task-desktop",
    "experiment-vr",
    "shared-resource",
    "template",
    "infra",
]

DEFAULT_CATEGORY_TOPICS: dict[str, list[str]] = {
    "task-desktop": ["desktop-task"],
    "experiment-vr": ["vr-experiment"],
    "shared-resource": ["lab-resource"],
    "template": ["repo-template"],
    "infra": ["organization-profile"],
}

KNOWN_TEMPLATES: dict[str, str] = {
    "vr": f"{DEFAULT_ORG}/template-vr-experiment",
    "vr-experiment": f"{DEFAULT_ORG}/template-vr-experiment",
    "template-vr-experiment": f"{DEFAULT_ORG}/template-vr-experiment",
    "data": f"{DEFAULT_ORG}/template-data-pipeline",
    "data-pipeline": f"{DEFAULT_ORG}/template-data-pipeline",
    "template-data-pipeline": f"{DEFAULT_ORG}/template-data-pipeline",
}


def resolve_template(template: str | None, org: str = DEFAULT_ORG) -> str | None:
    """Resolve shorthand template aliases to full repo paths."""
    if not template:
        return None
    cleaned = template.strip().lower()
    if cleaned in KNOWN_TEMPLATES:
        return KNOWN_TEMPLATES[cleaned]
    if "/" not in template:
        return f"{org}/{template}"
    return template


def build_topic_list(category: str, extra_topics: Sequence[str] | None = None) -> list[str]:
    """Combine category baseline topics with extra user topics, deduplicated preserving order."""
    base = DEFAULT_CATEGORY_TOPICS.get(category, [])
    combined: list[str] = list(base)
    if extra_topics:
        for t in extra_topics:
            t_clean = t.strip().lower()
            if t_clean and t_clean not in combined:
                combined.append(t_clean)
    return combined


def init_repository(
    name: str,
    category: str,
    description: str | None = None,
    template: str | None = None,
    extra_topics: Sequence[str] | None = None,
    visibility: str = "private",
    org: str = DEFAULT_ORG,
    dry_run: bool = False,
) -> int:
    """Create and configure a repository with taxonomy metadata."""
    if category not in ALLOWED_CATEGORIES:
        print(f"Error: Invalid category '{category}'. Allowed: {', '.join(ALLOWED_CATEGORIES)}", file=sys.stderr)
        return 1

    if not dry_run and not shutil.which("gh"):
        print("Error: 'gh' CLI is required but not found in PATH.", file=sys.stderr)
        return 1

    # Strip org prefix if accidentally provided in name
    repo_name = name.split("/")[-1].strip()
    full_name = f"{org}/{repo_name}"
    resolved_tmpl = resolve_template(template, org=org)
    topics = build_topic_list(category, extra_topics)

    print("=" * 65)
    print(f"Repository Provisioning: {full_name}")
    print(f"  Category:    {category}")
    print(f"  Visibility:  {visibility}")
    print(f"  Template:    {resolved_tmpl or '(None)'}")
    print(f"  Description: {description or '(None)'}")
    print(f"  Topics:      {', '.join(topics)}")
    print("=" * 65)

    if dry_run:
        print("[Dry-run] Would execute:")
        print(f"  1. gh repo create {full_name} --{visibility} " + (f"--template {resolved_tmpl} " if resolved_tmpl else "") + (f'--description "{description}" ' if description else ""))
        print(f"  2. gh api --method PATCH /orgs/{org}/properties/values -F repo-category={category}")
        print(f"  3. gh api --method PUT /repos/{full_name}/topics -F names={topics}")
        return 0

    # 1. Create repository
    print(f"Step 1: Creating repository {full_name}...")
    create_cmd = ["gh", "repo", "create", full_name, f"--{visibility}"]
    if resolved_tmpl:
        create_cmd.extend(["--template", resolved_tmpl])
    if description:
        create_cmd.extend(["--description", description])

    res_create = subprocess.run(create_cmd, capture_output=True, text=True)
    if res_create.returncode != 0:
        print(f"Error creating repository: {res_create.stderr.strip()}", file=sys.stderr)
        return res_create.returncode
    print("  Repository created successfully.")

    # 2. Set repo-category custom property
    print(f"Step 2: Assigning repo-category='{category}'...")
    prop_payload = {
        "repository_names": [repo_name],
        "properties": [{"property_name": "repo-category", "value": category}],
    }
    res_prop = subprocess.run(
        ["gh", "api", "--method", "PATCH", f"/orgs/{org}/properties/values", "--input", "-"],
        input=json.dumps(prop_payload),
        capture_output=True,
        text=True,
    )
    if res_prop.returncode != 0:
        print(f"Error setting custom property: {res_prop.stderr.strip()}", file=sys.stderr)
        return res_prop.returncode
    print("  Custom property assigned.")

    # 3. Set topics
    print(f"Step 3: Assigning topics {topics}...")
    topic_payload = {"names": topics}
    res_topics = subprocess.run(
        ["gh", "api", "--method", "PUT", f"/repos/{full_name}/topics", "--input", "-"],
        input=json.dumps(topic_payload),
        capture_output=True,
        text=True,
    )
    if res_topics.returncode != 0:
        print(f"Error setting topics: {res_topics.stderr.strip()}", file=sys.stderr)
        return res_topics.returncode
    print("  Topics assigned.")

    print("\n✓ Repository setup complete!")
    print(f"  URL: https://github.com/{full_name}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Provision a new Tran-Memory-Lab repository with compliant taxonomy and topics."
    )
    parser.add_argument("name", help="Repository name (e.g. 'spatial-navigation-task')")
    parser.add_argument(
        "--category",
        "-c",
        choices=ALLOWED_CATEGORIES,
        default="task-desktop",
        help=f"Architectural role/modality (default: task-desktop). Allowed: {', '.join(ALLOWED_CATEGORIES)}",
    )
    parser.add_argument(
        "--topics",
        "-t",
        nargs="*",
        default=[],
        help="Additional repository topics (e.g. -t psychopy jspsych memory)",
    )
    parser.add_argument(
        "--template",
        help="Template repository (e.g. 'vr', 'data', or 'Tran-Memory-Lab/template-vr-experiment')",
    )
    parser.add_argument("--description", "-d", help="Short repository description")
    parser.add_argument(
        "--public",
        action="store_true",
        help="Make repository public (default is private)",
    )
    parser.add_argument(
        "--org",
        default=DEFAULT_ORG,
        help=f"Target GitHub organization (default: {DEFAULT_ORG})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print intended actions without making any changes",
    )

    args = parser.parse_args(argv)

    # Flatten topics if comma-separated values were passed
    flat_topics: list[str] = []
    for item in args.topics:
        for part in item.split(","):
            if part.strip():
                flat_topics.append(part.strip())

    visibility = "public" if args.public else "private"

    return init_repository(
        name=args.name,
        category=args.category,
        description=args.description,
        template=args.template,
        extra_topics=flat_topics,
        visibility=visibility,
        org=args.org,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    sys.exit(main())
