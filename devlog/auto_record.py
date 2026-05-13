#!/usr/bin/env python3
"""
DevLog Auto-Record — Post-Session Batch Analyzer

Analyzes AI session history after a conversation ends, extracts valuable
content, and writes to daily log. Designed to be called by AI tool hooks
(Kimi Code / Claude Code) or run manually.

Usage:
    # Analyze latest Kimi session
    python -m devlog.auto_record --kimi

    # Analyze specific session file
    python -m devlog.auto_record --file ~/.kimi/sessions/xxx/context.jsonl

    # Dry-run (show what would be recorded without writing)
    python -m devlog.auto_record --kimi --dry-run
"""

import argparse
import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path

from .config import DevLogConfig
from .sync import DevLogSync

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)

# ── Keywords for auto-detection ──
# (pattern, weight) — higher weight for action-oriented keywords
PATTERNS = {
    "note": [
        (r"完成了?", 2),
        (r"搞定", 2),
        (r"做好", 2),
        (r"实现了?", 2),
        (r"写完", 2),
        (r"提交了?", 2),
        (r"发布了?", 2),
        (r"部署", 2),
        (r"上线", 2),
        (r"合并", 2),
        (r"修复", 2),
        (r"优化", 2),
        (r"重构", 2),
        (r"测试通过", 2),
        (r"review", 1),
        (r"开会", 1),
        (r"讨论了?", 1),
        (r"确认", 1),
        (r"验收", 1),
    ],
    "problem": [
        (r"报错", 2),
        (r"错误", 1),
        (r"bug", 1),
        (r"异常", 2),
        (r"失败", 2),
        (r"卡住", 2),
        (r"崩溃", 2),
        (r"超时", 2),
        (r"不?能运行", 2),
        (r"不?能工作", 2),
        (r"出问题了?", 2),
        (r"有问题", 2),
        (r"兼容", 1),
        (r"冲突", 2),
        (r"死锁", 2),
        (r"内存泄漏", 2),
    ],
    "learning": [
        (r"学到", 2),
        (r"了解", 1),
        (r"原来", 1),
        (r"发现", 1),
        (r"阅读", 1),
        (r"看了", 1),
        (r"查了", 1),
        (r"调研", 1),
        (r"学习了?", 2),
        (r"理解了?", 2),
        (r"才知道", 2),
        (r"原理", 1),
        (r"机制", 1),
        (r"文档", 1),
    ],
    "idea": [
        (r"可以", 1),
        (r"想到", 2),
        (r"也许", 1),
        (r"试试", 1),
        (r"建议", 1),
        (r"方案", 1),
        (r"思路", 1),
        (r"设计", 1),
        (r"规划", 1),
        (r"下一步", 1),
        (r"后续", 1),
        (r"todo", 1),
        (r"待办", 1),
        (r"计划", 1),
        (r"如果", 1),
        (r"不如", 1),
        (r"改成", 1),
    ],
    "todo": [
        (r"需要", 1),
        (r"应该", 1),
        (r"得", 1),
        (r"要", 1),
        (r"还没", 2),
        (r"尚未", 2),
        (r"待", 1),
        (r"准备", 1),
        (r"开始", 1),
        (r"接着", 1),
        (r"继续", 1),
    ],
}

# Compile regexes
_COMPILED = {
    cat: [(re.compile(p, re.IGNORECASE), w) for p, w in pats]
    for cat, pats in PATTERNS.items()
}

# Exclude patterns (greetings, confirmations, meta)
_EXCLUDE = [
    re.compile(r"^(hi|hello|hey|你好|在吗|帮忙|谢谢|thanks|ok|好的|明白|知道了)"),
    re.compile(r"^\s*(/|\\)"),  # slash commands
    re.compile(r"^(yes|no|y|n|是|否|对|不对)\s*$", re.IGNORECASE),
    re.compile(r"^\s*```"),  # code blocks
]


def _classify_content(text: str) -> str | None:
    """Classify user message into a category or None using weighted scoring."""
    # Skip excluded patterns
    for pat in _EXCLUDE:
        if pat.search(text):
            return None

    # Skip too short
    if len(text.strip()) < 5:
        return None

    scores = {cat: 0 for cat in _COMPILED}
    for cat, pats in _COMPILED.items():
        for pat, weight in pats:
            if pat.search(text):
                scores[cat] += weight

    best_score = max(scores.values())
    if best_score <= 0:
        return None

    # Tie-breaker priority: problem > todo > learning > idea > note
    priority = ["problem", "todo", "learning", "idea", "note"]
    candidates = [cat for cat, s in scores.items() if s == best_score]
    for cat in priority:
        if cat in candidates:
            return cat
    return candidates[0]


def _extract_project_tag(text: str) -> str:
    """Extract project tag from text, or return empty string."""
    # Explicit @Tag
    m = re.search(r"@(\S+)", text)
    if m:
        return m.group(1)

    # Common project indicators
    indicators = [
        r"(?:项目|project)[：:]\s*([A-Za-z0-9_\-]+)",
        r"在\s*([A-Za-z0-9_\-]+?)\s*(?:项目|里|中|上)",
    ]
    for pat in indicators:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1)

    return ""


def _parse_kimi_context(path: Path) -> list[dict]:
    """Parse Kimi Code context.jsonl into user messages."""
    records = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                role = obj.get("role", "")
                if role != "user":
                    continue
                content = obj.get("content", "")
                if not content or not isinstance(content, str):
                    continue
                records.append({"role": role, "content": content.strip()})
    except Exception as exc:
        logging.error("Failed to parse %s: %s", path, exc)
    return records


def _parse_claude_context(path: Path) -> list[dict]:
    """Parse Claude Code conversation.jsonl into user messages."""
    records = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                # Claude format varies; try common keys
                msg = obj.get("message", obj)
                role = msg.get("role", "")
                if role not in ("user", "human"):
                    continue
                content = msg.get("content", "")
                if isinstance(content, list):
                    texts = [c.get("text", "") for c in content if isinstance(c, dict)]
                    content = " ".join(texts)
                if not content or not isinstance(content, str):
                    continue
                records.append({"role": role, "content": content.strip()})
    except Exception as exc:
        logging.error("Failed to parse %s: %s", path, exc)
    return records


def _find_latest_kimi_session() -> Path | None:
    """Find the most recently modified Kimi session context.jsonl."""
    base = Path.home() / ".kimi" / "sessions"
    if not base.exists():
        return None

    candidates = []
    for session_dir in base.iterdir():
        if not session_dir.is_dir():
            continue
        for sub in session_dir.iterdir():
            ctx = sub / "context.jsonl"
            if ctx.exists():
                candidates.append((ctx.stat().st_mtime, ctx))

    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def _find_latest_claude_session() -> Path | None:
    """Find the most recently modified Claude session."""
    base = Path.home() / ".claude" / "sessions"
    if not base.exists():
        return None

    candidates = []
    for session_dir in base.iterdir():
        if not session_dir.is_dir():
            continue
        for f in session_dir.glob("*.jsonl"):
            candidates.append((f.stat().st_mtime, f))

    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def _deduplicate(records: list[dict]) -> list[dict]:
    """Remove duplicate or near-duplicate content."""
    seen = set()
    out = []
    for r in records:
        # Simple dedup: first 30 chars normalized
        key = re.sub(r"\s+", "", r["content"])[:30].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def _merge_with_daily(records: list[dict], date_str: str, dry_run: bool = False) -> int:
    """Merge extracted records into daily log, avoiding duplicates."""
    sync = DevLogSync()
    daily_path = sync._ensure_daily(date_str)
    existing = daily_path.read_text(encoding="utf-8")

    # Extract existing content lines for dedup
    existing_lines = set()
    for line in existing.split("\n"):
        stripped = line.strip()
        if stripped.startswith("[") and "]" in stripped:
            # Extract text after symbol: [HH:MM] SYMBOL CONTENT
            m = re.search(
                r'^\[(\d{2}:\d{2})\]\s+'
                r'([·×○✓→*x!\-\[\]v>]+)\s+'
                r'(.+)$',
                stripped,
            )
            if m:
                existing_lines.add(m.group(3).strip()[:40].lower())

    written = 0
    symbols = sync.symbols
    cat_symbols = {
        "note": symbols["note"],
        "problem": symbols["problem"],
        "learning": symbols["learning"],
        "idea": symbols["idea"],
        "todo": symbols["todo"],
    }

    time_str = datetime.now().strftime("%H:%M")
    new_lines = []

    for r in records:
        cat = _classify_content(r["content"])
        if not cat:
            continue

        # Deduplicate against existing daily log
        content_norm = r["content"].strip()[:40].lower()
        if content_norm in existing_lines:
            continue
        existing_lines.add(content_norm)

        symbol = cat_symbols.get(cat, symbols["note"])
        content = r["content"].strip()

        # Auto-extract project tag if missing
        project_tag = _extract_project_tag(content)
        tag_part = f" @{project_tag}" if project_tag else ""

        line = f"[{time_str}] {symbol} {content}{tag_part}"
        new_lines.append(line)
        written += 1

    if not new_lines:
        return 0

    if dry_run:
        print("[DRY-RUN] Would append to daily/" + date_str + ".md:")
        for line in new_lines:
            print("  " + line)
        return written

    # Append to daily log
    marker = "## 🕐 Interstitial Log"
    if marker in existing:
        idx = existing.find(marker) + len(marker)
        comment = "<!-- AI appends records here -->"
        cidx = existing.find(comment, idx)
        if cidx != -1:
            idx = cidx + len(comment)
        insert_text = "\n" + "\n".join(new_lines) + "\n"
        new_content = existing[:idx] + insert_text + existing[idx:]
    else:
        insert_text = "\n" + "\n".join(new_lines) + "\n"
        new_content = existing + insert_text

    daily_path.write_text(new_content, encoding="utf-8")
    logging.info("Auto-recorded %s entries to daily/%s.md", written, date_str)

    # ── Auto-sync: projects + stats + reflection ──
    try:
        sync.sync_daily_to_projects(date_str)
        sync.generate_daily_stats(date_str)
        logging.info("Auto-synced projects & stats for %s", date_str)
    except Exception as exc:
        logging.warning("Auto-sync failed: %s", exc)

    return written


def auto_record(
    source: str = "kimi",
    file_path: str = "",
    date_str: str = "",
    dry_run: bool = False,
) -> int:
    """Main entry: analyze session and write to daily log."""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    # Resolve source file
    if file_path:
        src = Path(file_path)
    elif source == "kimi":
        src = _find_latest_kimi_session()
    elif source == "claude":
        src = _find_latest_claude_session()
    else:
        logging.error("Unknown source: %s", source)
        return 0

    if not src or not src.exists():
        logging.warning("No session file found for source: %s", source)
        return 0

    logging.info("Analyzing session: %s", src)

    # Parse
    if source == "kimi":
        records = _parse_kimi_context(src)
    elif source == "claude":
        records = _parse_claude_context(src)
    else:
        # Generic: try both
        records = _parse_kimi_context(src)
        if not records:
            records = _parse_claude_context(src)

    logging.info("Found %s user messages", len(records))

    # Deduplicate
    records = _deduplicate(records)
    logging.info("After dedup: %s unique messages", len(records))

    # Classify and merge (includes auto-sync)
    written = _merge_with_daily(records, date_str, dry_run=dry_run)
    if written == 0:
        logging.info("No new records to write")
    return written


def main():
    parser = argparse.ArgumentParser(description="DevLog Auto-Record")
    parser.add_argument("--kimi", action="store_true", help="Analyze latest Kimi session")
    parser.add_argument("--claude", action="store_true", help="Analyze latest Claude session")
    parser.add_argument("--file", help="Specific session file to analyze")
    parser.add_argument("--date", help="Target date (YYYY-MM-DD), default today")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    source = "kimi"
    if args.claude:
        source = "claude"

    auto_record(
        source=source,
        file_path=args.file,
        date_str=args.date,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
