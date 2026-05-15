"""Tests for my_devlog.search."""

import pytest
from pathlib import Path

from my_devlog.search import search_logs, list_projects


@pytest.fixture
def tmp_devlog(tmp_path):
    cfg_dir = tmp_path / ".my-devlog"
    cfg_dir.mkdir()
    (cfg_dir / "config.md").write_text(f"- **Root**: {tmp_path}\n", encoding="utf-8")
    (tmp_path / "daily").mkdir()
    return tmp_path


class TestSearchLogs:
    def test_search_by_keyword(self, tmp_devlog):
        daily = tmp_devlog / "daily" / "2026-05-12.md"
        daily.write_text(
            "# 2026-05-12\n[09:00] \u00b7 Implemented search @DevLog\n"
            "[10:00] \u00b7 Fixed bug @DevLog\n"
            "[11:00] \u00b7 Lunch break\n",
            encoding="utf-8",
        )
        results = search_logs("search", root_dir=str(tmp_devlog))
        assert len(results) == 1
        assert "Implemented search" in results[0]["line"]

    def test_search_by_project(self, tmp_devlog):
        daily = tmp_devlog / "daily" / "2026-05-12.md"
        daily.write_text(
            "# 2026-05-12\n[09:00] \u00b7 Work on Alpha @Alpha\n"
            "[10:00] \u00b7 Work on Beta @Beta\n",
            encoding="utf-8",
        )
        results = search_logs(project="Alpha", root_dir=str(tmp_devlog))
        assert len(results) == 1
        assert "Alpha" in results[0]["line"]

    def test_date_range_filter(self, tmp_devlog):
        for date, content in [
            ("2026-05-10.md", "# D\n[09:00] \u00b7 Old record\n"),
            ("2026-05-12.md", "# D\n[09:00] \u00b7 New record\n"),
        ]:
            (tmp_devlog / "daily" / date).write_text(content, encoding="utf-8")
        results = search_logs(
            "record", date_from="2026-05-11", date_to="2026-05-12",
            root_dir=str(tmp_devlog),
        )
        assert len(results) == 1
        assert results[0]["date"] == "2026-05-12"


class TestListProjects:
    def test_lists_projects(self, tmp_devlog):
        daily = tmp_devlog / "daily" / "2026-05-12.md"
        daily.write_text(
            "# 2026-05-12\n[09:00] \u00b7 Work @Alpha\n[10:00] \u00b7 Work @Beta\n",
            encoding="utf-8",
        )
        projects = list_projects(str(tmp_devlog))
        assert "Alpha" in projects
        assert "Beta" in projects
