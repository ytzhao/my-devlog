#!/usr/bin/env python3
"""
DevLog Search

Search across daily logs by keyword, date range, or project tag.

Usage:
    python -m devlog.search <keyword> [--date YYYY-MM-DD] [--from DATE] [--to DATE] [--project NAME]
    python -m devlog.search --list-projects
"""

import argparse
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path

from .config import DevLogConfig

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)


def search_logs(
    keyword: str = None,
    date_str: str = None,
    date_from: str = None,
    date_to: str = None,
    project: str = None,
    root_dir: str = None,
):
    """Search daily logs and return matching lines with metadata."""
    config = DevLogConfig(root_dir)
    root = config.root_dir
    daily_dir = root / "daily"

    if not daily_dir.exists():
        logging.error("Daily directory not found: %s", daily_dir)
        return []

    # Resolve date range
    if date_str:
        date_from = date_to = date_str
    else:
        if not date_from:
            date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not date_to:
            date_to = datetime.now().strftime("%Y-%m-%d")

    results = []
    keyword_lower = keyword.lower() if keyword else None
    project_pattern = re.compile(rf"@{re.escape(project)}(?:\b|\W)") if project else None

    for path in sorted(daily_dir.glob("*.md")):
        name = path.stem
        if not re.match(r"\d{4}-\d{2}-\d{2}$", name):
            continue
        if name < date_from or name > date_to:
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except Exception as exc:
            logging.warning("Cannot read %s: %s", path.name, exc)
            continue

        for line in content.split("\n"):
            line_stripped = line.strip()
            if not line_stripped.startswith("["):
                continue

            if keyword_lower and keyword_lower not in line.lower():
                continue

            if project_pattern and not project_pattern.search(line):
                continue

            results.append({"date": name, "line": line_stripped})

    return results


def list_projects(root_dir: str = None):
    """List all projects mentioned across daily logs."""
    config = DevLogConfig(root_dir)
    root = config.root_dir
    daily_dir = root / "daily"

    projects = {}
    for path in daily_dir.glob("*.md"):
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for tag in re.findall(r"@(\S+)", content):
            projects[tag] = projects.get(tag, 0) + 1
    return projects


def main():
    parser = argparse.ArgumentParser(description="DevLog Search")
    parser.add_argument("keyword", nargs="?", help="Keyword to search for")
    parser.add_argument("--date", help="Single date (YYYY-MM-DD)")
    parser.add_argument("--from", dest="date_from", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to", help="End date (YYYY-MM-DD)")
    parser.add_argument("--project", help="Filter by @ProjectName")
    parser.add_argument("--list-projects", action="store_true",
                        help="List all projects and record counts")
    parser.add_argument("--root", help="Override DevLog root directory")

    args = parser.parse_args()

    if args.list_projects:
        projects = list_projects(args.root)
        if projects:
            print("Projects found:")
            for proj, count in sorted(projects.items(), key=lambda x: -x[1]):
                print(f"  @{proj}: {count} records")
        else:
            print("No projects found.")
        return

    if not args.keyword and not args.project:
        parser.error("Provide a keyword, --project, or use --list-projects")

    results = search_logs(
        keyword=args.keyword,
        date_str=args.date,
        date_from=args.date_from,
        date_to=args.to,
        project=args.project,
        root_dir=args.root,
    )

    if not results:
        print("No matching records found.")
        return

    current_date = None
    for r in results:
        if r["date"] != current_date:
            current_date = r["date"]
            print(f"\n# {current_date}")
        print(f"  {r['line']}")
    print(f"\nTotal: {len(results)} records")


if __name__ == "__main__":
    main()
