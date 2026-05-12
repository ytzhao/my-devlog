#!/usr/bin/env python3
"""
DevLog Uninstaller

Usage:
    python uninstall.py              # Uninstall default ~/.devlog/
    python uninstall.py --root PATH  # Uninstall custom directory
    python uninstall.py --skills-only # Only remove AI skills, keep data
"""

import argparse
import shutil
import sys
from pathlib import Path


def uninstall(root_dir=None, skills_only=False):
    """Remove DevLog installation."""
    if root_dir:
        root = Path(root_dir).expanduser().resolve()
    else:
        root = Path.home() / ".devlog"

    if skills_only:
        _remove_ai_skills()
        print("[OK] AI skills removed")
        return

    if root.exists():
        confirm = input(f"Remove DevLog root directory: {root}? [y/N] ")
        if confirm.lower() == "y":
            shutil.rmtree(root)
            print(f"[OK] Removed {root}")
        else:
            print("Cancelled")
            sys.exit(0)
    else:
        print(f"[INFO] Root directory does not exist: {root}")

    _remove_ai_skills()
    print("[OK] DevLog uninstalled")


def _remove_ai_skills():
    """Remove installed AI skill files from global config dirs."""
    home = Path.home()

    targets = [
        home / ".claude" / "commands",
        home / ".kimi" / "skills",
        home / ".opencode",
    ]

    for target_dir in targets:
        if not target_dir.exists():
            continue
        for f in target_dir.glob("log-*.md"):
            if f.name.startswith("log-"):
                f.unlink()
                print(f"[OK] Removed skill: {f}")
        # Clean up devlog-specific skills
        for f in target_dir.glob("devlog*"):
            if f.is_file():
                f.unlink()
                print(f"[OK] Removed skill: {f}")


def main():
    parser = argparse.ArgumentParser(description="DevLog Uninstaller")
    parser.add_argument("--root", help="DevLog root directory (default: ~/.devlog/)")
    parser.add_argument("--skills-only", action="store_true",
                        help="Only remove AI skills, keep all data")
    args = parser.parse_args()
    uninstall(root_dir=args.root, skills_only=args.skills_only)


if __name__ == "__main__":
    main()
