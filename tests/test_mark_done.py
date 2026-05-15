"""Tests for my_devlog.mark_done."""

import pytest
from pathlib import Path

from my_devlog.mark_done import mark_done, list_todos


@pytest.fixture
def tmp_devlog(tmp_path):
    cfg_dir = tmp_path / ".my-devlog"
    cfg_dir.mkdir()
    (cfg_dir / "config.md").write_text(f"- **Root**: {tmp_path}\n", encoding="utf-8")
    (tmp_path / "daily").mkdir()
    return tmp_path


class TestMarkDone:
    def test_marks_todo_done(self, tmp_devlog):
        daily = tmp_devlog / "daily" / "2026-05-12.md"
        daily.write_text(
            "# 2026-05-12\n\n## Log\n"
            "[09:00] \u25cb Buy milk\n"
            "[10:00] \u25cb Write code\n",
            encoding="utf-8",
        )
        ok = mark_done("milk", "2026-05-12", str(tmp_devlog))
        assert ok is True
        text = daily.read_text(encoding="utf-8")
        assert "\u2713 Buy milk" in text
        assert "\u25cb Write code" in text

    def test_no_match_returns_false(self, tmp_devlog):
        daily = tmp_devlog / "daily" / "2026-05-12.md"
        daily.write_text(
            "# 2026-05-12\n\n## Log\n[09:00] \u25cb Write code\n",
            encoding="utf-8",
        )
        ok = mark_done("milk", "2026-05-12", str(tmp_devlog))
        assert ok is False

    def test_missing_file_returns_false(self, tmp_devlog):
        ok = mark_done("anything", "2026-05-12", str(tmp_devlog))
        assert ok is False


class TestListTodos:
    def test_lists_open_todos(self, tmp_devlog):
        daily = tmp_devlog / "daily" / "2026-05-12.md"
        daily.write_text(
            "# 2026-05-12\n\n## Log\n"
            "[09:00] \u25cb Buy milk\n"
            "[10:00] \u2713 Done already\n"
            "[11:00] \u25cb Write code\n",
            encoding="utf-8",
        )
        todos = list_todos("2026-05-12", str(tmp_devlog))
        assert len(todos) == 2
        assert any("Buy milk" in t for t in todos)
        assert any("Write code" in t for t in todos)

    def test_empty_list_when_no_todos(self, tmp_devlog):
        daily = tmp_devlog / "daily" / "2026-05-12.md"
        daily.write_text(
            "# 2026-05-12\n\n## Log\n[09:00] \u00b7 Just a note\n",
            encoding="utf-8",
        )
        todos = list_todos("2026-05-12", str(tmp_devlog))
        assert todos == []
