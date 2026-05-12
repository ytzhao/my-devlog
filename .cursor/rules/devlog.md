# DevLog Cursor / Windsurf Rules

## Project Context

This project is **My DevLog** — an AI-native interstitial journaling system for developers.
It uses Markdown-based bullet journaling with AI coding assistant integration.

## Coding Conventions

- Python 3.9+ with type hints where practical
- Use `pathlib.Path` for all file operations
- Always specify `encoding="utf-8"` for text I/O
- Use standard library only (no external dependencies for core)
- Follow existing print/logging style: `[OK]`, `[INFO]`, `[WARN]`, `[ERROR]`

## File Structure

```
devlog/
  __init__.py      # Package exports
  config.py        # DevLogConfig — root resolution, symbols, structure
  sync.py          # DevLogSync — archive, sync, stats, weekly
  mark_done.py     # mark_done(keyword) — todo completion
  init.py          # init_devlog() — installer logic
```

## Key Behaviors

- AI tools only write to `daily/` and `inbox.md`
- `sync.py` generates `projects/` and `stats` from `daily/`
- Symbol schemes: `unicode` (default) or `ascii`
- Tag format: `@ProjectName` (never `#ProjectName`)

## Testing

- Run tests: `python -m pytest tests/ -v`
- Add tests for any new sync logic or regex changes
