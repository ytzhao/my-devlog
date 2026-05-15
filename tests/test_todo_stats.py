"""Tests for my_devlog.todo_stats."""

import pytest
from pathlib import Path

from my_devlog.todo_stats import compute_todo_stats, TodoStats


@pytest.fixture
def tmp_devlog(tmp_path):
    cfg_dir = tmp_path / ".my-devlog"
    cfg_dir.mkdir()
    (cfg_dir / "config.md").write_text(f"- **Root**: {tmp_path}\n", encoding="utf-8")
    (tmp_path / "daily").mkdir()
    return tmp_path


class TestComputeTodoStats:
    def test_today_counts(self, tmp_devlog):
        daily = tmp_devlog / "daily" / "2026-05-15.md"
        daily.write_text(
            "# 2026-05-15\n\n"
            "[09:00] ○ Buy milk\n"
            "[10:00] ✓ Write code\n"
            "[11:00] ○ Call mom\n",
            encoding="utf-8",
        )
        stats = compute_todo_stats("2026-05-15", str(tmp_devlog))
        assert stats == TodoStats(done_today=1, new_today=2, total_open=2)

    def test_total_open_across_days(self, tmp_devlog):
        today = tmp_devlog / "daily" / "2026-05-15.md"
        yesterday = tmp_devlog / "daily" / "2026-05-14.md"
        today.write_text("[09:00] ○ Today todo\n", encoding="utf-8")
        yesterday.write_text(
            "[09:00] ○ Yesterday todo\n[10:00] ✓ Done\n",
            encoding="utf-8",
        )
        stats = compute_todo_stats("2026-05-15", str(tmp_devlog))
        assert stats.done_today == 0
        assert stats.new_today == 1
        assert stats.total_open == 2

    def test_no_todos(self, tmp_devlog):
        daily = tmp_devlog / "daily" / "2026-05-15.md"
        daily.write_text(
            "# No todos today\n[09:00] · Just a note\n",
            encoding="utf-8",
        )
        stats = compute_todo_stats("2026-05-15", str(tmp_devlog))
        assert stats == TodoStats(done_today=0, new_today=0, total_open=0)

    def test_missing_daily_file(self, tmp_devlog):
        stats = compute_todo_stats("2026-05-15", str(tmp_devlog))
        assert stats == TodoStats(done_today=0, new_today=0, total_open=0)

    def test_ascii_symbols(self, tmp_devlog):
        daily = tmp_devlog / "daily" / "2026-05-15.md"
        daily.write_text(
            "[09:00] [ ] Buy milk\n[10:00] [v] Done\n",
            encoding="utf-8",
        )
        stats = compute_todo_stats("2026-05-15", str(tmp_devlog))
        assert stats == TodoStats(done_today=1, new_today=1, total_open=1)

    def test_mixed_symbols(self, tmp_devlog):
        daily = tmp_devlog / "daily" / "2026-05-15.md"
        daily.write_text(
            "[09:00] ○ Unicode todo\n"
            "[10:00] [ ] ASCII todo\n"
            "[11:00] ✓ Unicode done\n"
            "[12:00] [v] ASCII done\n",
            encoding="utf-8",
        )
        stats = compute_todo_stats("2026-05-15", str(tmp_devlog))
        assert stats == TodoStats(done_today=2, new_today=2, total_open=2)
