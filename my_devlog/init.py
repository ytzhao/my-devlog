"""
DevLog initialization logic.
Creates directory structure, default config, and inbox.
"""

import shutil
import sys
from pathlib import Path

from .config import DevLogConfig


def init_devlog(root_dir=None, install_skills=True):
    """Initialize DevLog directory structure.
    
    Args:
        root_dir: DevLog root directory. Defaults to ~/.my-devlog/
        install_skills: Whether to copy AI skill files to global config dirs
    """
    config = DevLogConfig(root_dir)
    root = config.root_dir

    print(f"Initializing DevLog at: {root}")

    # Create directory structure
    config.ensure_structure()
    print("[OK] Directory structure created")

    # Write default config
    config.write_default_config()
    print("[OK] Default config written")

    # Create inbox.md
    inbox_path = root / "inbox.md"
    if not inbox_path.exists():
        inbox_content = (
            "# Inbox — Quick Capture\n\n"
            "> append-only collection box, auto-archived by sync.py.\n"
            "> Run `sync.py --archive-inbox` to distribute records to daily/.\n\n"
        )
        inbox_path.write_text(inbox_content, encoding="utf-8")
        print("[OK] inbox.md created")

    # Install AI skills if requested
    if install_skills:
        _install_ai_skills()

    print(f"\nDevLog initialized successfully!")
    print(f"Root: {root}")
    print(f"\nNext steps:")
    print("  1. Set DEVLOG_ROOT environment variable (optional):")
    print(f"     export DEVLOG_ROOT={root}")
    print("  2. Start your AI tool and use /my-devlog to record your first note")
    print("  3. Run sync.py to generate project logs and statistics")


def _install_ai_skills():
    """Copy AI skill files to user's global config directories."""
    home = Path.home()
    package_dir = Path(__file__).parent.parent

    # Claude Code
    claude_dir = home / ".claude" / "commands"
    claude_source = package_dir / "skills" / "claude" / "commands"
    if claude_source.exists():
        claude_dir.mkdir(parents=True, exist_ok=True)
        for f in claude_source.glob("*.md"):
            shutil.copy2(f, claude_dir / f.name)
        print(f"[OK] Claude Code skills installed to {claude_dir}")

    # Kimi Code
    kimi_dir = home / ".kimi" / "skills"
    kimi_source = package_dir / "skills" / "kimi" / "skills"
    if kimi_source.exists():
        kimi_dir.mkdir(parents=True, exist_ok=True)
        for f in kimi_source.glob("*.md"):
            shutil.copy2(f, kimi_dir / f.name)
        print(f"[OK] Kimi Code skills installed to {kimi_dir}")

    # OpenCode
    opencode_dir = home / ".opencode"
    opencode_source = package_dir / "skills" / "opencode"
    if opencode_source.exists():
        opencode_dir.mkdir(parents=True, exist_ok=True)
        for f in opencode_source.glob("*.md"):
            shutil.copy2(f, opencode_dir / f.name)
        print(f"[OK] OpenCode config installed to {opencode_dir}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Initialize DevLog")
    parser.add_argument("--root", help="DevLog root directory (default: ~/.my-devlog/)")
    parser.add_argument("--no-skills", action="store_true",
                        help="Skip installing AI skill files")
    args = parser.parse_args()

    init_devlog(root_dir=args.root, install_skills=not args.no_skills)


if __name__ == "__main__":
    main()
