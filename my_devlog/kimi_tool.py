#!/usr/bin/env python3
"""
DevLog Kimi Plugin Tools

Lightweight wrapper for Kimi Code native tool calls.
Reads JSON arguments from stdin, executes the requested operation, prints result to stdout.

Usage (called by Kimi Code plugin system):
    echo '{"content": "My note", "project_tag": "MyProject"}' | python -m my_devlog.kimi_tool write_record
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from .auto_record import auto_record as _auto_record
from .config import DevLogConfig
from .mark_done import list_todos, mark_done as _mark_done
from .search import search_logs
from .sync import DevLogSync

logging.basicConfig(level=logging.WARNING)


def _read_args() -> dict:
    """Read JSON arguments from stdin."""
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def tool_write_record(args: dict) -> str:
    """Append a record to today's daily log."""
    sync = DevLogSync()
    date = args.get("date", datetime.now().strftime("%Y-%m-%d"))
    content = args.get("content", "")
    if not content:
        return "[ERROR] Missing 'content' argument"

    daily_path = sync._ensure_daily(date)
    daily_content = daily_path.read_text(encoding="utf-8")

    symbols = sync.symbols
    symbol = args.get("symbol", "auto")
    if symbol == "auto":
        from .auto_record import _classify_content
        cat = _classify_content(content)
        if cat == "problem":
            symbol = symbols["problem"]
        elif cat == "learning":
            symbol = symbols["learning"]
        elif cat == "idea":
            symbol = symbols["idea"]
        elif cat == "todo":
            symbol = symbols["todo"]
        else:
            symbol = symbols["note"]

    project_tag = args.get("project_tag", "")
    if not project_tag:
        cwd = Path.cwd().name
        if cwd and cwd not in (".", "~", "home"):
            project_tag = cwd

    time_str = datetime.now().strftime("%H:%M")
    tag_part = f" @{project_tag}" if project_tag else ""
    line = f"[{time_str}] {symbol} {content}{tag_part}"

    marker = "## 🕐 Interstitial Log"
    if marker in daily_content:
        idx = daily_content.find(marker) + len(marker)
        comment = "<!-- AI appends records here -->"
        cidx = daily_content.find(comment, idx)
        if cidx != -1:
            idx = cidx + len(comment)
        daily_content = daily_content[:idx] + "\n" + line + daily_content[idx:]
    else:
        daily_content += "\n" + line + "\n"

    daily_path.write_text(daily_content, encoding="utf-8")

    # ── Auto-sync projects & stats ──
    try:
        sync.sync_daily_to_projects(date)
        sync.generate_daily_stats(date)
        sync.generate_daily_reflection(date)
    except Exception as exc:
        return f"[OK] Recorded: {line}\n[WARN] Auto-sync failed: {exc}"

    return f"[OK] Recorded: {line} | synced"


def tool_sync(args: dict) -> str:
    """Sync daily to projects + stats."""
    sync = DevLogSync()
    date = args.get("date", datetime.now().strftime("%Y-%m-%d"))
    sync.sync_daily_to_projects(date)
    sync.generate_daily_stats(date)
    return f"[OK] Synced daily/{date}.md to projects/ and regenerated stats."


def tool_mark_done(args: dict) -> str:
    """Mark todo as done."""
    keyword = args.get("keyword", "")
    if not keyword:
        return "[ERROR] Missing 'keyword' argument"
    date = args.get("date", datetime.now().strftime("%Y-%m-%d"))
    ok = _mark_done(keyword, date)
    if ok:
        return f"[OK] Marked todo matching '{keyword}' as done."
    return f"[WARN] No todo matching '{keyword}' found."


def tool_list_todos(args: dict) -> str:
    """List open todos."""
    date = args.get("date", datetime.now().strftime("%Y-%m-%d"))
    todos = list_todos(date)
    if not todos:
        return "No open todos."
    return "\n".join(todos)


def tool_search(args: dict) -> str:
    """Search logs."""
    results = search_logs(
        keyword=args.get("keyword") or None,
        date_from=args.get("date_from") or None,
        date_to=args.get("date_to") or None,
        project=args.get("project") or None,
    )
    if not results:
        return "No matching records found."
    lines = []
    current_date = None
    for r in results:
        if r["date"] != current_date:
            current_date = r["date"]
            lines.append(f"\n# {current_date}")
        lines.append(f"  {r['line']}")
    lines.append(f"\nTotal: {len(results)} records")
    return "\n".join(lines)


def tool_read_daily(args: dict) -> str:
    """Read daily log."""
    date = args.get("date", datetime.now().strftime("%Y-%m-%d"))
    path = DevLogConfig().root_dir / "daily" / f"{date}.md"
    if not path.exists():
        return f"[INFO] Daily log for {date} does not exist."
    return path.read_text(encoding="utf-8")


def tool_archive_inbox(args: dict) -> str:
    """Archive inbox."""
    DevLogSync().archive_inbox()
    return "[OK] inbox.md archived."


def tool_generate_weekly(args: dict) -> str:
    """Generate weekly report."""
    sync = DevLogSync()
    week_start = args.get("week_start", "")
    if week_start:
        from datetime import timedelta
        ws = datetime.strptime(week_start, "%Y-%m-%d").date()
    else:
        today = datetime.now()
        ws = (today - timedelta(days=today.weekday() + 7)).date()
    sync.generate_weekly_report(ws)
    return f"[OK] Weekly report generated for week starting {ws}."


def tool_review(args: dict) -> str:
    """Generate daily reflection for today's log."""
    sync = DevLogSync()
    date = args.get("date", datetime.now().strftime("%Y-%m-%d"))
    try:
        sync.generate_daily_reflection(date)
        return f"[OK] Generated reflection for daily/{date}.md"
    except Exception as exc:
        return f"[ERROR] Failed to generate reflection: {exc}"


def tool_auto_record(args: dict) -> str:
    """Run auto-record to analyze latest AI session."""
    source = args.get("source", "kimi")
    date = args.get("date", datetime.now().strftime("%Y-%m-%d"))
    dry_run = args.get("dry_run", False)
    try:
        count = _auto_record(source=source, date_str=date, dry_run=dry_run)
        if dry_run:
            return f"[OK] Dry-run: would record {count} entries"
        return f"[OK] Auto-recorded {count} entries from {source} session"
    except Exception as exc:
        return f"[ERROR] Auto-record failed: {exc}"


TOOLS = {
    "write_record": tool_write_record,
    "sync": tool_sync,
    "mark_done": tool_mark_done,
    "list_todos": tool_list_todos,
    "search": tool_search,
    "read_daily": tool_read_daily,
    "archive_inbox": tool_archive_inbox,
    "generate_weekly": tool_generate_weekly,
    "review": tool_review,
    "auto_record": tool_auto_record,
}


def main():
    if len(sys.argv) < 2:
        print("[ERROR] No tool name provided", file=sys.stderr)
        sys.exit(1)

    tool_name = sys.argv[1]
    tool_fn = TOOLS.get(tool_name)
    if not tool_fn:
        print(f"[ERROR] Unknown tool: {tool_name}", file=sys.stderr)
        sys.exit(1)

    args = _read_args()
    try:
        result = tool_fn(args)
        print(result)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
