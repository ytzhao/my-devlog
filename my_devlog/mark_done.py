#!/usr/bin/env python3
"""
DevLog Mark Done Script

Mark a todo item as done by keyword search.

Usage:
    python -m my_devlog.mark_done <keyword> [--date YYYY-MM-DD] [--root PATH]
    python -m my_devlog.mark_done --list [--date YYYY-MM-DD] [--root PATH]
"""

import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

from .config import DevLogConfig

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)


def mark_done(keyword: str, date_str: str = None, root_dir: str = None) -> bool:
    """Search for a todo matching *keyword* in daily/date_str.md and mark it done.

    Returns True if a match was found and updated, False otherwise.
    """
    config = DevLogConfig(root_dir)
    root = config.root_dir
    symbols = config.get_symbols()

    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    daily_path = root / "daily" / f"{date_str}.md"
    if not daily_path.exists():
        logging.error("Daily log not found: %s", daily_path)
        return False

    content = daily_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    todo_symbols = (symbols["todo"], "[ ]")
    done_symbols = (symbols["done"], "[v]")

    # Build regex to match todo lines
    todo_pattern = re.compile(
        rf'^(\[\d{{2}}:\d{{2}}\]\s+)({re.escape(symbols["todo"])}|\[ \])(\s+.*)$'
    )

    keyword_lower = keyword.lower()
    matches = []

    for idx, line in enumerate(lines):
        m = todo_pattern.match(line)
        if m and keyword_lower in line.lower():
            matches.append((idx, m))

    if not matches:
        logging.warning("No todo matching '%s' found in %s", keyword, daily_path.name)
        return False

    # Pick the most recent (last) match
    idx, m = matches[-1]
    prefix, _symbol, suffix = m.groups()
    new_line = prefix + symbols["done"] + suffix
    lines[idx] = new_line

    daily_path.write_text("\n".join(lines), encoding="utf-8")
    logging.info("Marked todo as done in %s: %s", daily_path.name, new_line.strip())
    return True


def list_todos(date_str: str = None, root_dir: str = None):
    """List all open todos for the given date."""
    config = DevLogConfig(root_dir)
    root = config.root_dir
    symbols = config.get_symbols()

    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    daily_path = root / "daily" / f"{date_str}.md"
    if not daily_path.exists():
        logging.error("Daily log not found: %s", daily_path)
        return []

    content = daily_path.read_text(encoding="utf-8")
    todo_pattern = re.compile(
        rf'^\[\d{{2}}:\d{{2}}\]\s+({re.escape(symbols["todo"])}|\[ \])\s+.*$'
    )
    todos = [line.strip() for line in content.split("\n") if todo_pattern.match(line)]
    return todos


def main():
    parser = argparse.ArgumentParser(description="DevLog Mark Done")
    parser.add_argument("keyword", nargs="?", help="Keyword to search for in todos")
    parser.add_argument("--date", help="Date (YYYY-MM-DD), default today")
    parser.add_argument("--list", action="store_true", help="List open todos instead")
    parser.add_argument("--root", help="Override DevLog root directory")

    args = parser.parse_args()

    if args.list:
        todos = list_todos(args.date, args.root)
        if todos:
            print(f"Open todos ({len(todos)}):")
            for t in todos:
                print(f"  {t}")
        else:
            print("No open todos found.")
        return

    if not args.keyword:
        parser.error("keyword is required (or use --list)")

    ok = mark_done(args.keyword, args.date, args.root)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
