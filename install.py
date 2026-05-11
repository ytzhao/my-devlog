#!/usr/bin/env python3
"""
DevLog One-Click Installer

Usage:
    python install.py                    # Install with default settings
    python install.py --root ~/my-log    # Install to custom directory
    python install.py --no-skills        # Skip AI skill installation
"""

import sys
from pathlib import Path

# Add package to path for installation
sys.path.insert(0, str(Path(__file__).parent))

from devlog.init import init_devlog


def main():
    import argparse
    parser = argparse.ArgumentParser(description="DevLog Installer")
    parser.add_argument("--root", help="DevLog root directory (default: ~/.devlog/)")
    parser.add_argument("--no-skills", action="store_true",
                        help="Skip installing AI skill files")
    args = parser.parse_args()

    print("=" * 50)
    print("  My DevLog - AI-Native Developer Journal")
    print("=" * 50)
    print()

    init_devlog(root_dir=args.root, install_skills=not args.no_skills)


if __name__ == "__main__":
    main()
