"""Tests for my_devlog.sync core logic."""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from my_devlog.config import DevLogConfig
from my_devlog.sync import DevLogSync


@pytest.fixture
def tmp_devlog(tmp_path):
    """Create a temporary DevLog directory structure."""
    cfg_dir = tmp_path / ".my-devlog"
    cfg_dir.mkdir()
    (cfg_dir / "config.md").write_text(f"- **Root**: {tmp_path}\n", encoding="utf-8")
    (cfg_dir / "templates").mkdir()
    (tmp_path / "daily").mkdir()
    return tmp_path


@pytest.fixture
def sync(tmp_devlog):
    return DevLogSync(root_dir=str(tmp_devlog))


class TestParseLogLine:
    def test_unicode_symbols(self, sync):
        assert sync._parse_log_line("[09:30] \u00b7 Note entry @ProjectA") == {
            "time": "09:30",
            "symbol": "\u00b7",
            "content": "Note entry @ProjectA",
            "tags": ["ProjectA"],
            "hashtags": [],
        }

    def test_ascii_todo(self, sync):
        assert sync._parse_log_line("[10:00] [ ] Ascii todo @X") == {
            "time": "10:00",
            "symbol": "[ ]",
            "content": "Ascii todo @X",
            "tags": ["X"],
            "hashtags": [],
        }

    def test_done_symbol(self, sync):
        assert sync._parse_log_line("[11:00] [v] Done item") is not None

    def test_migrate(self, sync):
        assert sync._parse_log_line("[12:00] >> Migrated item") is not None

    def test_double_symbol_rejected(self, sync):
        # P0-4 fix: double symbols should not match
        assert sync._parse_log_line("[13:00] \u00b7\u00b7 Double symbol") is None

    def test_no_symbol_rejected(self, sync):
        assert sync._parse_log_line("[14:00] Plain text no symbol") is None

    def test_no_time_rejected(self, sync):
        assert sync._parse_log_line("No time prefix") is None

    def test_time_range_parsing(self, sync):
        result = sync._parse_log_line("[09:00-10:30] \u00b7 Worked on feature")
        assert result is not None
        assert result["time"] == "09:00"
        assert result["end_time"] == "10:30"
        assert result["duration"] == 90

    def test_hashtag_extraction(self, sync):
        result = sync._parse_log_line("[09:00] \u00b7 Note #priority-high #frontend")
        assert result is not None
        assert result["hashtags"] == ["priority-high", "frontend"]


class TestClassifySymbol:
    def test_note(self, sync):
        assert sync._classify_symbol("\u00b7") == "note"
        assert sync._classify_symbol("*") == "note"

    def test_problem(self, sync):
        assert sync._classify_symbol("\u00d7") == "problem"
        assert sync._classify_symbol("x") == "problem"

    def test_todo(self, sync):
        assert sync._classify_symbol("\u25cb") == "todo"
        assert sync._classify_symbol("[ ]") == "todo"

    def test_done(self, sync):
        assert sync._classify_symbol("\u2713") == "done"
        assert sync._classify_symbol("[v]") == "done"

    def test_migrate(self, sync):
        assert sync._classify_symbol(">>") == "migrate"
        assert sync._classify_symbol("\u2192") == "migrate"

    def test_other(self, sync):
        assert sync._classify_symbol("?") == "other"


class TestSyncDailyToProjects:
    def test_creates_project_log(self, sync, tmp_devlog):
        daily = tmp_devlog / "daily" / "2026-05-12.md"
        daily.write_text(
            "# 2026-05-12\n\n## Log\n[09:00] \u00b7 Test note @MyProject\n",
            encoding="utf-8",
        )
        sync.sync_daily_to_projects("2026-05-12")
        proj = tmp_devlog / "projects" / "MyProject" / "2026-05-12.md"
        assert proj.exists()
        text = proj.read_text(encoding="utf-8")
        assert "Test note @MyProject" in text
        assert "TODAY_RECORDS_START" in text
        assert "TODAY_RECORDS_END" in text

    def test_incremental_update_preserves_user_content(self, sync, tmp_devlog):
        daily = tmp_devlog / "daily" / "2026-05-12.md"
        daily.write_text(
            "# 2026-05-12\n\n## Log\n[09:00] \u00b7 First note @MyProject\n",
            encoding="utf-8",
        )
        sync.sync_daily_to_projects("2026-05-12")

        # User adds custom section
        proj = tmp_devlog / "projects" / "MyProject" / "2026-05-12.md"
        text = proj.read_text(encoding="utf-8")
        text = text.replace(
            "<!-- Auto-extracted problem records",
            "Fixed the cache issue.\n\n<!-- Auto-extracted problem records",
        )
        proj.write_text(text, encoding="utf-8")

        # Re-sync with updated content
        daily.write_text(
            "# 2026-05-12\n\n## Log\n[09:00] \u00b7 Updated note @MyProject\n",
            encoding="utf-8",
        )
        sync.sync_daily_to_projects("2026-05-12")

        new_text = proj.read_text(encoding="utf-8")
        assert "Updated note" in new_text
        assert "Fixed the cache issue" in new_text


class TestArchiveInbox:
    def test_archives_to_daily(self, sync, tmp_devlog):
        inbox = tmp_devlog / "inbox.md"
        inbox.write_text(
            "# Inbox\n\n"
            "[2026-05-12 09:00] \u00b7 Inbox note @ProjectA\n"
            "[2026-05-12 10:00] \u25cb Inbox todo\n",
            encoding="utf-8",
        )
        sync.archive_inbox()
        daily = tmp_devlog / "daily" / "2026-05-12.md"
        assert daily.exists()
        text = daily.read_text(encoding="utf-8")
        assert "Inbox note" in text
        assert "Inbox todo" in text

    def test_clears_inbox_header_only(self, sync, tmp_devlog):
        inbox = tmp_devlog / "inbox.md"
        inbox.write_text(
            "# Inbox\n> header\n\n"
            "[2026-05-12 09:00] \u00b7 Note\n"
            "Some plain text that should be cleared\n",
            encoding="utf-8",
        )
        sync.archive_inbox()
        text = inbox.read_text(encoding="utf-8")
        assert "# Inbox" in text
        assert "Note" not in text
        assert "plain text" not in text


class TestGenerateDailyStats:
    def test_generates_stats_with_anchors(self, sync, tmp_devlog):
        daily = tmp_devlog / "daily" / "2026-05-12.md"
        tpl = sync._default_daily_template()
        content = tpl.replace("{{DATE}}", "2026-05-12").replace("{{WEEKDAY}}", "Mon")
        daily.write_text(content, encoding="utf-8")

        # Add some records
        daily.write_text(
            daily.read_text(encoding="utf-8")
            + "\n## \u2570 Interstitial Log\n[09:00] \u00b7 Note 1\n[10:00] \u00d7 Problem 1\n",
            encoding="utf-8",
        )
        sync.generate_daily_stats("2026-05-12")

        text = daily.read_text(encoding="utf-8")
        assert "STATS_TABLE_START" in text
        assert "STATS_TABLE_END" in text
        assert "| Note" in text
        assert "| 1 |" in text or "| 0 |" in text

    def test_skips_empty_file(self, sync, tmp_devlog, capsys):
        daily = tmp_devlog / "daily" / "2026-05-12.md"
        tpl = sync._default_daily_template()
        content = tpl.replace("{{DATE}}", "2026-05-12").replace("{{WEEKDAY}}", "Mon")
        daily.write_text(content, encoding="utf-8")
        sync.generate_daily_stats("2026-05-12")
        captured = capsys.readouterr()
        assert "skipping stats" in captured.out or "no records" in captured.out


class TestDefaultDailyTemplate:
    def test_has_stats_anchors(self, sync):
        tpl = sync._default_daily_template()
        assert "<!-- STATS_TABLE_START -->" in tpl
        assert "<!-- STATS_TABLE_END -->" in tpl

    def test_english_template(self, sync):
        tpl = sync._default_daily_template(lang="en")
        assert "Keywords:" in tpl
        assert "Mood Tracker" in tpl

    def test_chinese_template(self, sync):
        tpl = sync._default_daily_template(lang="zh")
        assert "关键词" in tpl
        assert "情绪追踪" in tpl
