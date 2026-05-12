#!/usr/bin/env python3
"""
DevLog Obsidian / Logseq Adapter

Generates Obsidian-compatible daily notes with wiki-links and Logseq-compatible blocks.

Usage:
    python -m devlog.obsidian [--root PATH] [--output-dir PATH]
"""

import argparse
import logging
import re
from pathlib import Path

from .config import DevLogConfig

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)


def to_obsidian(root_dir=None, output_dir=None):
    """Convert daily logs to Obsidian daily note format with wiki-links."""
    config = DevLogConfig(root_dir)
    root = config.root_dir
    out = Path(output_dir) if output_dir else root / "obsidian"
    out.mkdir(parents=True, exist_ok=True)

    daily_dir = root / "daily"
    for path in sorted(daily_dir.glob("*.md")):
        if not re.match(r"\d{4}-\d{2}-\d{2}$", path.stem):
            continue

        content = path.read_text(encoding="utf-8")
        # Convert @ProjectName to [[ProjectName]] wiki-links
        obsidian_content = re.sub(r"@(\S+)", r"[[\1]]", content)
        # Add YAML frontmatter
        frontmatter = f"---\ndate: {path.stem}\ntags: [devlog]\n---\n\n"
        (out / path.name).write_text(frontmatter + obsidian_content, encoding="utf-8")
        logging.info("Converted %s -> Obsidian", path.name)

    # Create index page
    index = ["# DevLog Index\n"]
    for path in sorted(out.glob("*.md")):
        if path.name == "Index.md":
            continue
        index.append(f"- [[{path.stem}]]")
    (out / "Index.md").write_text("\n".join(index), encoding="utf-8")
    logging.info("Obsidian vault generated at %s", out)


def to_logseq(root_dir=None, output_dir=None):
    """Convert daily logs to Logseq journal format."""
    config = DevLogConfig(root_dir)
    root = config.root_dir
    out = Path(output_dir) if output_dir else root / "logseq" / "journals"
    out.mkdir(parents=True, exist_ok=True)

    daily_dir = root / "daily"
    for path in sorted(daily_dir.glob("*.md")):
        if not re.match(r"\d{4}-\d{2}-\d{2}$", path.stem):
            continue

        content = path.read_text(encoding="utf-8")
        logseq_name = path.stem.replace("-", "_") + ".md"
        # Logseq uses block refs and property syntax
        logseq_content = content.replace("## ", "### ")  # downshift headers
        (out / logseq_name).write_text(logseq_content, encoding="utf-8")
        logging.info("Converted %s -> Logseq", path.name)

    logging.info("Logseq journals generated at %s", out)


def main():
    parser = argparse.ArgumentParser(description="DevLog Obsidian / Logseq Adapter")
    parser.add_argument("--obsidian", action="store_true", help="Generate Obsidian vault")
    parser.add_argument("--logseq", action="store_true", help="Generate Logseq journals")
    parser.add_argument("--output-dir", help="Output directory")
    parser.add_argument("--root", help="Override DevLog root directory")
    args = parser.parse_args()

    if args.obsidian:
        to_obsidian(args.root, args.output_dir)
    elif args.logseq:
        to_logseq(args.root, args.output_dir)
    else:
        to_obsidian(args.root, args.output_dir)


if __name__ == "__main__":
    main()
