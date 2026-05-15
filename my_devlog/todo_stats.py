"""
My DevLog Todo Statistics

Compute todo counts across daily logs: done today, new today, total open.

Usage:
    from my_devlog.todo_stats import compute_todo_stats, TodoStats
    stats = compute_todo_stats()
    print(f"🥔[{stats.done_today}/{stats.new_today}/{stats.total_open}]")
"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .config import DevLogConfig

TODO_RE = re.compile(r"^\[\d{2}:\d{2}\]\s+(○|\[ \])\s+")
DONE_RE = re.compile(r"^\[\d{2}:\d{2}\]\s+(✓|\[v\])\s+")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class TodoStats:
    done_today: int
    new_today: int
    total_open: int


def compute_todo_stats(
    date_str: Optional[str] = None,
    root_dir: Optional[str] = None,
    scan_days: int = 30,
) -> TodoStats:
    """Compute todo statistics across daily logs.

    Args:
        date_str: Target date (YYYY-MM-DD), default today.
        root_dir: Override DevLog root directory.
        scan_days: How many recent days to scan for total_open.

    Returns:
        TodoStats with done_today, new_today, total_open.
    """
    config = DevLogConfig(root_dir)
    root = config.root_dir
    daily_dir = root / "daily"

    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    # Count today's done and new todos
    done_today = 0
    new_today = 0
    today_path = daily_dir / f"{date_str}.md"
    if today_path.exists():
        try:
            content = today_path.read_text(encoding="utf-8")
            for line in content.split("\n"):
                s = line.strip()
                if not s.startswith("["):
                    continue
                if TODO_RE.match(s):
                    new_today += 1
                elif DONE_RE.match(s):
                    done_today += 1
        except Exception:
            pass

    # Count total open todos across recent daily files
    total_open = 0
    if daily_dir.exists():
        cutoff = (datetime.now() - timedelta(days=scan_days)).strftime("%Y-%m-%d")
        for path in daily_dir.glob("*.md"):
            if not DATE_RE.match(path.stem) or path.stem < cutoff:
                continue
            try:
                content = path.read_text(encoding="utf-8")
                for line in content.split("\n"):
                    s = line.strip()
                    if s.startswith("[") and TODO_RE.match(s):
                        total_open += 1
            except Exception:
                pass

    return TodoStats(
        done_today=done_today,
        new_today=new_today,
        total_open=total_open,
    )
