#!/usr/bin/env python3
"""
Web Highlight Server — DevLog Browser Extension Backend

Receives highlight data from the browser extension, saves:
  1. Screenshot PNG  → assets/web-highlights/YYYY-MM-DD/
  2. Markdown archive → assets/web-highlights/YYYY-MM-DD/
  3. Daily log entry  → daily/YYYY-MM.md (Interstitial Log section)

Usage:
    python tools/web_highlight_server.py
    # Server runs on http://localhost:3721
"""

import base64
import json
import os
import re
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import unquote

# Fix Windows console encoding for emoji output
if sys.platform == "win32":
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
    except Exception:
        pass

# Resolve devlog package from project root
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from devlog.config import DevLogConfig
from devlog.sync import DevLogSync

PORT = 3721

# If DEVLOG_ROOT is not set, try to auto-detect project root by looking for pyproject.toml
if not os.environ.get("DEVLOG_ROOT"):
    script_dir = Path(__file__).resolve().parent
    for parent in [script_dir] + list(script_dir.parents):
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            os.environ["DEVLOG_ROOT"] = str(parent)
            break

ROOT = PROJECT_ROOT


def slugify(text: str, max_len: 40) -> str:
    """Create a filesystem-safe slug from page title."""
    s = re.sub(r"[^\w\s-]", "", text).strip().lower()
    s = re.sub(r"[-\s]+", "-", s)
    return s[:max_len]


class HighlightHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Suppress default request logs; print only what we care about
        pass

    def _send_json(self, status_code: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path != "/highlight":
            self._send_json(404, {"error": "not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body.decode("utf-8"))
        except Exception as exc:
            self._send_json(400, {"error": f"bad request: {exc}"})
            return

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        time_slug = now.strftime("%H-%M-%S")

        # ── Paths ──
        asset_dir = ROOT / "assets" / "web-highlights" / date_str
        asset_dir.mkdir(parents=True, exist_ok=True)

        title = data.get("title", "untitled") or "untitled"
        url = data.get("url", "")
        text = data.get("text", "")
        note = data.get("note", "")
        tag = data.get("tag", "web")
        screenshot_b64 = data.get("screenshot", "")

        # ── 1. Save screenshot ──
        screenshot_path = None
        if screenshot_b64 and "," in screenshot_b64:
            try:
                img_bytes = base64.b64decode(screenshot_b64.split(",", 1)[1])
                screenshot_name = f"{slugify(title, 30)}-{time_slug}.png"
                screenshot_path = asset_dir / screenshot_name
                screenshot_path.write_bytes(img_bytes)
            except Exception as exc:
                print(f"[WARN] Screenshot save failed: {exc}")

        # ── 2. Save Markdown archive ──
        md_name = f"{slugify(title, 30)}-{time_slug}.md"
        md_path = asset_dir / md_name

        rel_screenshot = screenshot_path.name if screenshot_path else ""
        md_content = f"""---
title: {title}
url: {url}
date: {now.isoformat()}
tags: [web-highlight, {tag}]
---

## Highlight

> {text}

## Note

{note or "_(none)_"}

## Source

- **URL**: [{url}]({url})
- **Saved at**: {date_str} {time_str}
"""
        if rel_screenshot:
            md_content += f"\n## Screenshot\n\n![screenshot]({rel_screenshot})\n"

        md_path.write_text(md_content, encoding="utf-8")

        # ── 3. Append to daily log ──
        sync = DevLogSync(root_dir=ROOT)
        daily_path = sync._ensure_daily(date_str)
        daily_content = daily_path.read_text(encoding="utf-8")

        symbols = sync.symbols
        display_title = title[:50] + "…" if len(title) > 50 else title
        line = f"[{time_str}] {symbols['learning']} Web: {display_title} @{tag}"

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

        print(f"[OK] {time_str} | {display_title} | screenshot={'yes' if screenshot_path else 'no'}")
        if screenshot_path:
            print(f"       Screenshot: {screenshot_path}")
        self._send_json(
            200,
            {
                "status": "ok",
                "md_path": str(md_path.relative_to(ROOT)),
                "screenshot": str(screenshot_path.relative_to(ROOT)) if screenshot_path else None,
                "daily": f"daily/{date_str}.md",
            },
        )


def main():
    server = HTTPServer(("localhost", PORT), HighlightHandler)
    print(f"🖍️  Web Highlight Server running at http://localhost:{PORT}")
    print(f"   Root: {ROOT}")
    print("   Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")


if __name__ == "__main__":
    main()
