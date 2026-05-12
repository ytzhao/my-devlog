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
PATTERNS = {
    "note": [
        r"完成了?",
        r"搞定",
        r"做好",
        r"实现了?",
        r"写完",
        r"提交了?",
        r"发布了?",
        r"部署",
        r"上线",
        r"合并",
        r"修复",
        r"优化",
        r"重构",
        r"测试通过",
        r"review",
        r"开会",
        r"讨论了?",
        r"确认",
        r"验收",
    ],
    "problem": [
        r"报错",
        r"错误",
        r"bug",
        r"异常",
        r"失败",
        r"卡住",
        r"崩溃",
        r"超时",
        r"不?能运行",
        r"不?能工作",
        r"出问题了?",
        r"有问题",
        r"兼容",
        r"冲突",
        r"死锁",
        r"内存泄漏",
    ],
    "learning": [
        r"学到",
        r"了解",
        r"原来",
        r"发现",
        r"阅读",
        r"看了",
        r"查了",
        r"调研",
        r"学习了?",
        r"理解了?",
        r"才知道",
        r"原理",
        r"机制",
        r"文档",
    ],
    "idea": [
        r"可以",
        r"想到",
        r"也许",
        r"试试",
        r"建议",
        r"方案",
        r"思路",
        r"设计",
        r"规划",
        r"下一步",
        r"后续",
        r"todo",
        r"待办",
        r"计划",
        r"如果",
        r"不如",
        r"改成",
    ],
    "todo": [
        r"需要",
        r"应该",
        r"得",
        r"要",
        r"还没",
        r"尚未",
        r"待",
        r"准备",
        r"开始",
        r"接着",
        r"继续",
    ],
}

# Compile regexes
_COMPILED = {
    cat: [re.compile(p, re.IGNORECASE) for p in pats]
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
    """Classify user message into a category or None."""
    # Skip excluded patterns
    for pat in _EXCLUDE:
        if pat.search(text):
            return None

    # Skip too short
    if len(text.strip()) < 8:
        return None

    scores = {cat: 0 for cat in _COMPILED}
    for cat, pats in _COMPILED.items():
        for pat in pats:
            if pat.search(text):
                scores[cat] += 1

    best = max(scores, key=scores.get)
    if scores[best] > 0:
        return best
    return None


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
            # Extract text after symbol
            m = re.search(r"\]\s+[·×○✓→*x!\-]|\[ \]|\[v\]|>>\s+(.+)", stripped)
            if m:
                existing_lines.add(m.group(1).strip()[:40].lower())

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
        line = f"[{time_str}] {symbol} {r['content'].strip()}"
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

    # Classify and merge
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
