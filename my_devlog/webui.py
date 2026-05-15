#!/usr/bin/env python3
"""
DevLog Web UI (Streamlit)

Optional dependency: pip install streamlit

Usage:
    streamlit run devlog/webui.py
"""

import re
from datetime import datetime, timedelta
from pathlib import Path

try:
    import streamlit as st
except ImportError:
    raise SystemExit(
        "Streamlit is required. Install with: pip install streamlit"
    )

from .config import DevLogConfig
from .sync import DevLogSync

st.set_page_config(page_title="DevLog Dashboard", layout="wide")
st.title("📓 DevLog Dashboard")

config = DevLogConfig()
root = config.root_dir
sync = DevLogSync(root_dir=str(root))

tab_stats, tab_search, tab_weekly = st.tabs(["📊 Stats", "🔍 Search", "📅 Weekly"])

with tab_stats:
    daily_dir = root / "daily"
    dates = sorted(
        [p.stem for p in daily_dir.glob("*.md") if re.match(r"\d{4}-\d{2}-\d{2}$", p.stem)]
    )
    if not dates:
        st.info("No daily logs found.")
    else:
        selected = st.selectbox("Select date", dates, index=len(dates) - 1)
        path = daily_dir / f"{selected}.md"
        content = path.read_text(encoding="utf-8")
        st.markdown(content)

with tab_search:
    keyword = st.text_input("Keyword")
    if keyword:
        results = []
        for path in sorted(daily_dir.glob("*.md")):
            if not re.match(r"\d{4}-\d{2}-\d{2}$", path.stem):
                continue
            for line in path.read_text(encoding="utf-8").split("\n"):
                if keyword.lower() in line.lower() and line.strip().startswith("["):
                    results.append((path.stem, line.strip()))
        st.write(f"Found {len(results)} records")
        for date, line in results:
            st.markdown(f"**{date}** — `{line}`")

with tab_weekly:
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday() + 7)
    week_label = f"{week_start.strftime('%Y-%m-%d')} ~ {(week_start + timedelta(days=6)).strftime('%Y-%m-%d')}"
    st.subheader(week_label)

    all_stats = {"note": 0, "problem": 0, "learning": 0, "idea": 0, "todo": 0, "done": 0, "total": 0}
    for i in range(7):
        date = week_start + timedelta(days=i)
        path = daily_dir / f"{date.strftime('%Y-%m-%d')}.md"
        if path.exists():
            for line in path.read_text(encoding="utf-8").split("\n"):
                parsed = sync._parse_log_line(line)
                if parsed:
                    cat = sync._classify_symbol(parsed["symbol"])
                    if cat in all_stats:
                        all_stats[cat] += 1
                        all_stats["total"] += 1

    cols = st.columns(3)
    cols[0].metric("Total Records", all_stats["total"])
    cols[1].metric("Problems", all_stats["problem"])
    cols[2].metric("Ideas", all_stats["idea"])

    st.bar_chart(
        {
            "Note": [all_stats["note"]],
            "Problem": [all_stats["problem"]],
            "Learning": [all_stats["learning"]],
            "Idea": [all_stats["idea"]],
            "Todo": [all_stats["todo"]],
            "Done": [all_stats["done"]],
        }
    )
