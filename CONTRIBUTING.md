# Contributing to My DevLog

Thank you for your interest in contributing! This project welcomes bug fixes, feature suggestions, and documentation improvements.

## How to Contribute

### Reporting Issues

- Use [GitHub Issues](https://github.com/yourusername/my-devlog/issues)
- Include Python version, OS, and steps to reproduce
- For bugs in sync logic, attach a minimal sample of the Markdown file that triggers the issue

### Pull Requests

1. Fork the repository and create a feature branch
2. Make your changes with clear commit messages
3. Add or update tests in `tests/` if you modify core logic
4. Ensure all tests pass: `python -m pytest tests/ -v`
5. Update relevant documentation (`README.md`, `docs/USAGE.md`)
6. Submit the PR with a description of what changed and why

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/my-devlog.git
cd my-devlog

# Run tests
python -m pytest tests/ -v

# Run sync manually for local testing
python -m devlog.sync --sync --date 2026-05-12
```

## Code Style

- Python 3.9+ compatible
- Use `pathlib.Path` for filesystem operations
- Always specify `encoding="utf-8"` for text file I/O
- Keep core dependencies at zero (standard library only)
- Follow existing logging style: `[OK]`, `[INFO]`, `[WARN]`, `[ERROR]`

## Release Process

1. Update version in `devlog/__init__.py` and `pyproject.toml`
2. Update `CHANGELOG.md`
3. Tag the release: `git tag vX.Y.Z`
4. Push tags: `git push --tags`
