#!/usr/bin/env python3
"""
DevLog MCP Server

Exposes DevLog core functionality as MCP tools, resources, and prompts.
Connects Claude Code (and any MCP client) directly to your DevLog system.

Usage:
    # Claude Code auto-detects via .mcp.json
    # Or run manually:
    python -m devlog.mcp_server

Configuration:
    Set DEVLOG_ROOT env var to override the default root directory.
"""

import json
import re
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from .config import DevLogConfig
from .mark_done import list_todos, mark_done as _mark_done
from .search import list_projects as _list_projects, search_logs
from .sync import DevLogSync

# ── Initialize FastMCP ──
mcp = FastMCP(
    "devlog",
    instructions=(
        "DevLog MCP Server — AI-native interstitial journaling system.\n"
        "Provides tools to read/write daily logs, sync to projects, "
        "search records, manage todos, generate stats/weekly reports, "
        "and export/backup data.\n"
        "All data stays local (Markdown files)."
    ),
)

# Shared instances (lazy resolution via config)
def _sync() -> DevLogSync:
    return DevLogSync()


def _root() -> Path:
    return DevLogConfig().root_dir


# ═══════════════════════════════════════════════════════════════
# TOOLS
# ═══════════════════════════════════════════════════════════════

@mcp.tool(
    name="devlog_read_daily",
    description="Read the daily log for a given date (YYYY-MM-DD). Returns markdown content.",
)
def devlog_read_daily(date: str) -> str:
    """Read daily/{date}.md."""
    path = _root() / "daily" / f"{date}.md"
    if not path.exists():
        return f"[INFO] Daily log for {date} does not exist."
    return path.read_text(encoding="utf-8")


@mcp.tool(
    name="devlog_write_record",
    description=(
        "Append a record to today's daily log (or a specific date). "
        "Auto-detects symbol from content keywords (problem/bug → ×, "
        "learn → -, idea → !, todo → ○, default → ·). "
        "Infers project tag from current directory if not provided."
    ),
)
def devlog_write_record(
    content: str,
    symbol: str = "auto",
    project_tag: str = "",
    date: str = "",
) -> str:
    """Append a single record line to daily/{date}.md."""
    sync = _sync()
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    daily_path = sync._ensure_daily(date)
    daily_content = daily_path.read_text(encoding="utf-8")

    # Auto-detect symbol
    symbols = sync.symbols
    if symbol == "auto":
        lowered = content.lower()
        if any(w in lowered for w in ("bug", "error", "problem", "fix", "crash")):
            symbol = symbols["problem"]
        elif any(w in lowered for w in ("learn", "read", "study", "understand")):
            symbol = symbols["learning"]
        elif any(w in lowered for w in ("idea", "think", "maybe", "could", "what if")):
            symbol = symbols["idea"]
        elif any(w in lowered for w in ("todo", "need to", "should", "plan")):
            symbol = symbols["todo"]
        else:
            symbol = symbols["note"]

    # Infer project tag
    if not project_tag:
        cwd = Path.cwd().name
        if cwd and cwd not in (".", "~", "home"):
            project_tag = cwd

    # Build line
    time_str = datetime.now().strftime("%H:%M")
    tag_part = f" @{project_tag}" if project_tag else ""
    line = f"[{time_str}] {symbol} {content}{tag_part}"

    # Append after interstitial marker
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
    return f"[OK] Recorded: {line}"


@mcp.tool(
    name="devlog_sync",
    description="Sync daily log to projects/ directory (extract @ProjectName tags).",
)
def devlog_sync(date: str = "") -> str:
    """Run sync_daily_to_projects + generate_daily_stats for a date."""
    sync = _sync()
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    sync.sync_daily_to_projects(date)
    sync.generate_daily_stats(date)
    return f"[OK] Synced daily/{date}.md to projects/ and regenerated stats."


@mcp.tool(
    name="devlog_archive_inbox",
    description="Archive inbox.md records into daily/ files by timestamp.",
)
def devlog_archive_inbox() -> str:
    """Run archive_inbox."""
    _sync().archive_inbox()
    return "[OK] inbox.md archived."


@mcp.tool(
    name="devlog_generate_stats",
    description="Generate the Daily Stats table for a given date (default today).",
)
def devlog_generate_stats(date: str = "") -> str:
    """Regenerate stats for date."""
    sync = _sync()
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    sync.generate_daily_stats(date)
    return f"[OK] Stats generated for {date}."


@mcp.tool(
    name="devlog_generate_weekly",
    description="Generate weekly report for the previous week (or a specific week start date).",
)
def devlog_generate_weekly(week_start: str = "") -> str:
    """Generate weekly report."""
    sync = _sync()
    if week_start:
        ws = datetime.strptime(week_start, "%Y-%m-%d").date()
    else:
        today = datetime.now()
        ws = (today - timedelta(days=today.weekday() + 7)).date()
    sync.generate_weekly_report(ws)
    return f"[OK] Weekly report generated for week starting {ws}."


@mcp.tool(
    name="devlog_mark_done",
    description="Mark a todo as done by keyword search in today's daily log.",
)
def devlog_mark_done(keyword: str, date: str = "") -> str:
    """Mark todo done."""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    ok = _mark_done(keyword, date)
    if ok:
        return f"[OK] Marked todo matching '{keyword}' as done."
    return f"[WARN] No todo matching '{keyword}' found."


@mcp.tool(
    name="devlog_list_todos",
    description="List all open (unfinished) todos for a given date (default today).",
)
def devlog_list_todos(date: str = "") -> str:
    """List open todos."""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    todos = list_todos(date)
    if not todos:
        return "No open todos."
    return "\n".join(todos)


@mcp.tool(
    name="devlog_search",
    description="Search daily logs by keyword, date range, or project tag.",
)
def devlog_search(
    keyword: str = "",
    date_from: str = "",
    date_to: str = "",
    project: str = "",
) -> str:
    """Search logs."""
    results = search_logs(
        keyword=keyword or None,
        date_from=date_from or None,
        date_to=date_to or None,
        project=project or None,
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


@mcp.tool(
    name="devlog_list_projects",
    description="List all projects mentioned in daily logs with record counts.",
)
def devlog_list_projects() -> str:
    """List projects."""
    projects = _list_projects()
    if not projects:
        return "No projects found."
    lines = ["Projects found:"]
    for proj, count in sorted(projects.items(), key=lambda x: -x[1]):
        lines.append(f"  @{proj}: {count} records")
    return "\n".join(lines)


@mcp.tool(
    name="devlog_get_config",
    description="Read DevLog configuration (root path, symbol set, language).",
)
def devlog_get_config() -> str:
    """Return config summary."""
    cfg = DevLogConfig()
    symbols = cfg.get_symbols()
    return (
        f"Root: {cfg.root_dir}\n"
        f"Symbol Set: {cfg.symbol_set}\n"
        f"Language: {cfg.language}\n"
        f"Symbols: {symbols}"
    )


@mcp.tool(
    name="devlog_create_backup",
    description="Create a ZIP backup of the entire DevLog directory.",
)
def devlog_create_backup(output_path: str = "devlog-backup.zip") -> str:
    """Create ZIP backup."""
    root = _root()
    out = Path(output_path)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in root.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(root)
                zf.write(file_path, arcname)
    size = out.stat().st_size
    return f"[OK] Backup created: {out} ({size} bytes)"


@mcp.tool(
    name="devlog_export_json",
    description="Export all daily logs to a JSON file.",
)
def devlog_export_json(output_path: str = "devlog-export.json") -> str:
    """Export to JSON."""
    sync = _sync()
    records = []
    daily_dir = _root() / "daily"
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
    out = Path(output_path)
    out.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    return f"[OK] Exported {len(records)} days to {out}."


@mcp.tool(
    name="devlog_export_md",
    description="Export all daily logs to a single Markdown file.",
)
def devlog_export_md(output_path: str = "devlog-export.md") -> str:
    """Export to single Markdown."""
    root = _root()
    lines = ["# DevLog Export\n", f"> Generated: {datetime.now().isoformat()}\n"]
    daily_dir = root / "daily"
    for path in sorted(daily_dir.glob("*.md")):
        if not re.match(r"\d{4}-\d{2}-\d{2}$", path.stem):
            continue
        lines.append(f"\n---\n\n# {path.stem}\n")
        lines.append(path.read_text(encoding="utf-8"))
    out = Path(output_path)
    out.write_text("\n".join(lines), encoding="utf-8")
    return f"[OK] Exported to {out}."


# ═══════════════════════════════════════════════════════════════
# RESOURCES
# ═══════════════════════════════════════════════════════════════

@mcp.resource("devlog://daily/{date}")
def read_daily_resource(date: str) -> str:
    """Daily log content."""
    return devlog_read_daily(date)


@mcp.resource("devlog://inbox")
def read_inbox() -> str:
    """Inbox content."""
    inbox = _root() / "inbox.md"
    if not inbox.exists():
        return "[INFO] inbox.md does not exist."
    return inbox.read_text(encoding="utf-8")


@mcp.resource("devlog://config")
def read_config() -> str:
    """DevLog configuration."""
    return devlog_get_config()


@mcp.resource("devlog://projects/{project}/{date}")
def read_project_resource(project: str, date: str) -> str:
    """Project daily log content."""
    path = _root() / "projects" / project / f"{date}.md"
    if not path.exists():
        return f"[INFO] Project log for {project}/{date} does not exist."
    return path.read_text(encoding="utf-8")


@mcp.resource("devlog://weekly/{date}")
def read_weekly_resource(date: str) -> str:
    """Weekly report content."""
    path = _root() / "daily" / f"weekly-{date}.md"
    if not path.exists():
        return f"[INFO] Weekly report for week starting {date} does not exist."
    return path.read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════════════════
# PROMPTS
# ═══════════════════════════════════════════════════════════════

@mcp.prompt(name="log_devlog")
def prompt_log_devlog() -> str:
    return (
        "Record an interstitial note to DevLog. "
        "Use the devlog_write_record tool with the user's message. "
        "Auto-detect the symbol (problem → ×, learn → -, idea → !, todo → ○, default → ·). "
        "Infer the project tag from the current working directory."
    )


@mcp.prompt(name="log_todo")
def prompt_log_todo() -> str:
    return (
        "Add a todo item to DevLog. "
        "Use the devlog_write_record tool with symbol='○' (or '[ ]' for ascii)."
    )


@mcp.prompt(name="log_bug")
def prompt_log_bug() -> str:
    return (
        "Record a bug or problem to DevLog. "
        "Use the devlog_write_record tool with symbol='×' (or 'x' for ascii)."
    )


@mcp.prompt(name="log_done")
def prompt_log_done() -> str:
    return (
        "Mark a todo as completed. "
        "Use the devlog_mark_done tool with the user's keyword."
    )


@mcp.prompt(name="log_sync")
def prompt_log_sync() -> str:
    return (
        "Sync today's DevLog to projects and regenerate stats. "
        "Use devlog_archive_inbox, then devlog_sync, then devlog_generate_stats."
    )


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

def main():
    mcp.run()


if __name__ == "__main__":
    main()
