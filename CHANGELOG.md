# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Multi-language support** — `templates/daily.en.md` + locale-aware template selection (`zh`/`en`/`auto`)
- **Mood tracking** — daily mood score `(mood: 4/5)` extracted in weekly reports with average
- **Time tracking** — support `[09:00-10:30]` time ranges with automatic duration calculation
- **Hashtag support** — `#priority-high`, `#tag-frontend` parsed and shown in daily stats / weekly reports
- **Backup & Export** — `devlog/backup.py` with `--export-json`, `--export-md`, `--backup` (ZIP)
- **Obsidian / Logseq adapter** — `devlog/obsidian.py` converts `@ProjectName` to `[[wiki-links]]` and generates index pages
- **Web UI** — `devlog/webui.py` Streamlit dashboard (optional dependency `pip install my-devlog[web]`)
- `devlog/mark_done.py` — script to mark todos as done by keyword search
- `uninstall.py` — remove DevLog data and AI skills
- `upgrade.py` — git pull + re-run installer
- `pyproject.toml` — pip-installable package with `devlog-sync` and `devlog-mark-done` CLI entry points
- `tests/` — pytest test suite covering sync, archive, stats, and mark_done logic
- `examples/git-hooks/post-commit` — auto-sync devlog after each git commit
- `.cursor/rules/devlog.md` — Cursor/Windsurf project rules
- `CONTRIBUTING.md` and `CHANGELOG.md`
- `devlog/search.py` — full-text search across daily logs

### Changed
- Stats table replacement now uses `<!-- STATS_TABLE_START/END -->` anchors for robustness (with legacy fallback)
- `sync_daily_to_projects()` uses incremental section updates via `<!-- TODAY_RECORDS_START/END -->` anchors
- `_parse_log_line()` regex now strictly matches single symbols or known pairs
- `archive_inbox()` clears inbox by keeping only header lines (fixed infinite growth bug)
- `docs/使用手册.md` renamed to `docs/USAGE.md`

### Fixed
- Project logs no longer overwrite user-added "Problems & Solutions" sections on each sync
- Unicode encoding errors in config loading now emit warnings instead of silent failure

## [0.1.0] - 2026-05-12

### Added
- Initial MVP release
- Daily Markdown journal with Unicode/ASCII symbol schemes
- Inbox quick-capture with auto-archive to daily logs
- Project tag extraction (`@ProjectName`) and per-project daily/monthly logs
- Daily statistics table generation
- Weekly report aggregation
- AI skill files for Claude Code, Kimi Code, and OpenCode
- One-click `install.py`
