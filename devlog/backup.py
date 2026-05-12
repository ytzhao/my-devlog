#!/usr/bin/env python3
"""
DevLog Backup & Export

Usage:
    python -m devlog.backup --export-json          # Export all logs to JSON
    python -m devlog.backup --export-md OUTPUT.md  # Export to single Markdown
    python -m devlog.backup --backup ARCHIVE.zip   # Create ZIP backup
"""

import argparse
import json
import logging
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

from .config import DevLogConfig
from .sync import DevLogSync

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)


def export_json(root_dir=None, output="devlog-export.json"):
    """Export all daily logs to a JSON file."""
    config = DevLogConfig(root_dir)
    root = config.root_dir
    sync = DevLogSync(root_dir=str(root))

    records = []
    daily_dir = root / "daily"
    for path in sorted(daily_dir.glob("*.md")):
        if not re.match(r"\d{4}-\d{2}-\d{2}$", path.stem):
            continue
        content = path.read_text(encoding="utf-8")
        day_records = []
        for line in content.split("\n"):
            parsed = sync._parse_log_line(line)
            if parsed:
                day_records.append(parsed)
        records.append({"date": path.stem, "records": day_records})

    out_path = Path(output)
    out_path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    logging.info("Exported %s days to %s", len(records), out_path)
    return out_path


def export_markdown(root_dir=None, output="devlog-export.md"):
    """Export all daily logs to a single Markdown file."""
    config = DevLogConfig(root_dir)
    root = config.root_dir

    lines = ["# DevLog Export\n", f"> Generated: {datetime.now().isoformat()}\n"]
    daily_dir = root / "daily"
    for path in sorted(daily_dir.glob("*.md")):
        if not re.match(r"\d{4}-\d{2}-\d{2}$", path.stem):
            continue
        lines.append(f"\n---\n\n# {path.stem}\n")
        lines.append(path.read_text(encoding="utf-8"))

    out_path = Path(output)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logging.info("Exported to %s", out_path)
    return out_path


def create_backup(root_dir=None, output="devlog-backup.zip"):
    """Create a ZIP backup of the entire DevLog root."""
    config = DevLogConfig(root_dir)
    root = config.root_dir
    out_path = Path(output)

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in root.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(root)
                zf.write(file_path, arcname)

    logging.info("Backup created: %s (%s bytes)", out_path, out_path.stat().st_size)
    return out_path


def main():
    parser = argparse.ArgumentParser(description="DevLog Backup & Export")
    parser.add_argument("--export-json", metavar="FILE", nargs="?", const="devlog-export.json",
                        help="Export to JSON")
    parser.add_argument("--export-md", metavar="FILE", nargs="?", const="devlog-export.md",
                        help="Export to single Markdown")
    parser.add_argument("--backup", metavar="FILE", nargs="?", const="devlog-backup.zip",
                        help="Create ZIP backup")
    parser.add_argument("--root", help="Override DevLog root directory")
    args = parser.parse_args()

    if args.export_json:
        export_json(args.root, args.export_json)
    elif args.export_md:
        export_markdown(args.root, args.export_md)
    elif args.backup:
        create_backup(args.root, args.backup)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
