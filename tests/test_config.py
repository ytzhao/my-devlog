"""Tests for my_devlog.config."""

import pytest
from pathlib import Path

from my_devlog.config import DevLogConfig


class TestLanguage:
    def test_detect_language_zh(self, tmp_path):
        cfg_dir = tmp_path / ".my-devlog"
        cfg_dir.mkdir()
        (cfg_dir / "config.md").write_text("- **Language**: `zh`\n", encoding="utf-8")
        config = DevLogConfig(root_dir=str(tmp_path))
        assert config.language == "zh"

    def test_detect_language_en(self, tmp_path):
        cfg_dir = tmp_path / ".my-devlog"
        cfg_dir.mkdir()
        (cfg_dir / "config.md").write_text("- **Language**: `en`\n", encoding="utf-8")
        config = DevLogConfig(root_dir=str(tmp_path))
        assert config.language == "en"

    def test_default_language_when_missing(self, tmp_path):
        cfg_dir = tmp_path / ".my-devlog"
        cfg_dir.mkdir()
        config = DevLogConfig(root_dir=str(tmp_path))
        assert config.language in ("zh", "en", "auto")
