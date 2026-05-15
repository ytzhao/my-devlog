"""
My DevLog - AI-native interstitial journaling system for developers.

A markdown-based bullet journal system that integrates with AI coding assistants
(Claude Code, Kimi Code, OpenCode) to track daily work, bugs, learning, and ideas.

Usage:
    from my_devlog import DevLogSync
    sync = DevLogSync()
    sync.sync_daily_to_projects()
"""

__version__ = "0.1.1"
__author__ = "ytzhao"

from .sync import DevLogSync
from .config import DevLogConfig

__all__ = ["DevLogSync", "DevLogConfig"]
