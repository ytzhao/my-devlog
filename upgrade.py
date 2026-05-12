#!/usr/bin/env python3
"""
DevLog Upgrader

Usage:
    python upgrade.py              # Pull latest and reinstall skills
    python upgrade.py --root PATH  # Upgrade with custom root
"""

import argparse
import subprocess
import sys
from pathlib import Path


def upgrade(root_dir=None):
    """Upgrade DevLog to the latest version."""
    package_dir = Path(__file__).parent.resolve()

    # Try git pull if inside a git repository
    git_dir = package_dir / ".git"
    if git_dir.exists():
        print("Pulling latest changes...")
        result = subprocess.run(
            ["git", "pull"],
            cwd=package_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"[WARN] git pull failed: {result.stderr.strip()}")
        else:
            print(result.stdout.strip() or "[OK] Already up to date")
    else:
        print("[INFO] Not a git repository, skipping git pull")
        print("       Download the latest release manually and run install.py")

    # Re-run install.py to update skills and structure
    install_script = package_dir / "install.py"
    if install_script.exists():
        print("\nRe-running install.py...")
        cmd = [sys.executable, str(install_script)]
        if root_dir:
            cmd += ["--root", root_dir]
        subprocess.run(cmd, check=False)
    else:
        print(f"[ERROR] install.py not found at {install_script}")

    print("\n[OK] Upgrade complete")


def main():
    parser = argparse.ArgumentParser(description="DevLog Upgrader")
    parser.add_argument("--root", help="DevLog root directory")
    args = parser.parse_args()
    upgrade(root_dir=args.root)


if __name__ == "__main__":
    main()
