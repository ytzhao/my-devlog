#!/usr/bin/env python3
"""
My DevLog Status Line for Claude Code

Outputs todo statistics in the format: 🥔[done_today/new_today/total_open]

Designed to be fast — no my_devlog package imports, only stdlib.
Intended for use with Claude Code's statusLine command configuration.

Usage:
    python -m my_devlog.statusline
    devlog-statusline
"""

import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

TODO_RE = re.compile(r"^\[\d{2}:\d{2}\]\s+(○|\[ \])\s+")
DONE_RE = re.compile(r"^\[\d{2}:\d{2}\]\s+(✓|\[v\])\s+")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SCAN_DAYS = 30


def _resolve_root() -> Path:
    """Resolve DevLog root without importing DevLogConfig."""
    env_root = os.environ.get("DEVLOG_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path.home() / ".my-devlog"


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    root = _resolve_root()
    date_str = datetime.now().strftime("%Y-%m-%d")
    daily_dir = root / "daily"
    today_path = daily_dir / f"{date_str}.md"

    # Count today's done and new todos
    done_count = 0
    todo_count = 0
    if today_path.exists():
        try:
            content = today_path.read_text(encoding="utf-8")
            for line in content.split("\n"):
                s = line.strip()
                if not s.startswith("["):
                    continue
                if TODO_RE.match(s):
                    todo_count += 1
                elif DONE_RE.match(s):
                    done_count += 1
        except Exception:
            pass

    # Count total open todos across recent daily files
    all_open = 0
    if daily_dir.exists():
        cutoff = (datetime.now() - timedelta(days=SCAN_DAYS)).strftime("%Y-%m-%d")
        for path in daily_dir.glob("*.md"):
            if not DATE_RE.match(path.stem) or path.stem < cutoff:
                continue
            try:
                content = path.read_text(encoding="utf-8")
                for line in content.split("\n"):
                    s = line.strip()
                    if s.startswith("[") and TODO_RE.match(s):
                        all_open += 1
            except Exception:
                pass

    print(f"🥔[{done_count}/{todo_count}/{all_open}]")


if __name__ == "__main__":
    main()
