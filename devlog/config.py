"""
DevLog configuration management.
Handles root directory resolution, symbol scheme, and user preferences.
"""

import os
import platform
from pathlib import Path


class DevLogConfig:
    """Manages DevLog configuration from environment and config files."""

    DEFAULT_DIR_NAME = ".devlog"
    CONFIG_FILENAME = "config.md"

    def __init__(self, root_dir=None):
        self.root = self._resolve_root(root_dir)
        self._config = self._load_config()

    def _resolve_root(self, override=None):
        """Resolve DevLog root directory with priority:
        1. Explicit override
        2. DEVLOG_ROOT environment variable
        3. Current directory's .devlog/config.md (if exists)
        4. User home directory ~/.devlog/
        """
        if override:
            return Path(override).expanduser().resolve()

        # 1. Environment variable
        env_root = os.environ.get("DEVLOG_ROOT")
        if env_root:
            return Path(env_root).expanduser().resolve()

        # 2. Check if we're inside a devlog tree (cwd or parents)
        cwd = Path.cwd()
        for parent in [cwd] + list(cwd.parents):
            config_path = parent / self.DEFAULT_DIR_NAME / self.CONFIG_FILENAME
            if config_path.exists():
                return parent

        # 3. Default to user home
        home = Path.home()
        return home / self.DEFAULT_DIR_NAME

    def _load_config(self):
        """Load config from root/.devlog/config.md"""
        config = {
            "root_dir": str(self.root),
            "symbol_set": "unicode",
            "user": os.environ.get("USER", os.environ.get("USERNAME", "user")),
        }

        config_path = self.root / self.DEFAULT_DIR_NAME / self.CONFIG_FILENAME
        if not config_path.exists():
            return config

        try:
            content = config_path.read_text(encoding="utf-8")
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("- **根目录**:") or line.startswith("- **Root**:"):
                    val = line.split(":", 1)[1].strip().strip("`")
                    config["root_dir"] = val
                elif line.startswith("- **符号方案**:") or line.startswith("- **Symbol Set**:"):
                    val = line.split(":", 1)[1].strip().split()[0]
                    config["symbol_set"] = val
        except Exception:
            pass

        return config

    @property
    def root_dir(self):
        return Path(self._config.get("root_dir", str(self.root)))

    @property
    def symbol_set(self):
        return self._config.get("symbol_set", "unicode")

    @property
    def user(self):
        return self._config.get("user", "user")

    def get_symbols(self):
        """Return symbol mapping based on configured scheme."""
        if self.symbol_set == "ascii":
            return {
                "note": "*",
                "problem": "x",
                "learning": "-",
                "idea": "!",
                "todo": "[ ]",
                "done": "[v]",
                "migrate": ">>",
            }
        return {
            "note": "·",
            "problem": "×",
            "learning": "-",
            "idea": "!",
            "todo": "○",
            "done": "✓",
            "migrate": "→",
        }

    def ensure_structure(self):
        """Create default directory structure if missing."""
        dirs = [
            self.root_dir / self.DEFAULT_DIR_NAME / "templates",
            self.root_dir / self.DEFAULT_DIR_NAME / "skills",
            self.root_dir / self.DEFAULT_DIR_NAME / "scripts",
            self.root_dir / "daily",
            self.root_dir / "projects",
            self.root_dir / "topics" / "bugfix",
            self.root_dir / "topics" / "learning",
            self.root_dir / "topics" / "ideas",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    def write_default_config(self):
        """Write default config.md if missing."""
        config_path = self.root_dir / self.DEFAULT_DIR_NAME / self.CONFIG_FILENAME
        if config_path.exists():
            return

        content = f"""# DevLog Global Configuration

## Basic Settings

- **Root Directory**: `{self.root_dir}`
- **Symbol Set**: `unicode`  # Options: unicode | ascii
- **Default Project**: None
- **User**: `{self.user}`

## Symbol Scheme Mapping

When `symbol-set: unicode`:
- Note: `·`
- Problem: `×`
- Learning: `-`
- Idea: `!`
- Todo: `○`
- Done: `✓`
- Migrate: `→`

When `symbol-set: ascii`:
- Note: `*`
- Problem: `x`
- Learning: `-`
- Idea: `!`
- Todo: `[ ]`
- Done: `[v]`
- Migrate: `>>`

## AI Tool Guidelines

- Read this file to get the root directory path, do not hardcode
- Use the symbol scheme specified above consistently
- Tag format: `@ProjectName` (do NOT use `#ProjectName` to avoid Markdown header conflict)
- AI only writes to `daily/` and `inbox.md`, do NOT write to `projects/` directly
"""
        config_path.write_text(content, encoding="utf-8")
