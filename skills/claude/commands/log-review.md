---
description: "Generate DevLog daily review"
model: default
---

Read `.devlog/config.md` to get the DevLog root path.
Read `daily/YYYY-MM-DD.md`, count records by type, list completed todos, unfinished todos, problems, and ideas.
Remind user to run `sync.py --daily-stats` for auto-generated statistics.
Ask if unfinished todos should be migrated to tomorrow.
