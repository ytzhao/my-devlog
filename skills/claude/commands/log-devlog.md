---
description: "Record an interstitial note to DevLog"
model: default
---

Read `.devlog/config.md` from the current directory or parent directories to get the DevLog root path and symbol scheme (unicode / ascii).
Locate `daily/YYYY-MM-DD.md`, create from template if missing.
Append the user's input with `[HH:MM]` timestamp + auto-detected symbol:
- Problem/error → `×` (unicode) or `x` (ascii)
- Learning → `-`
- Idea → `!`
- Todo → `○` or `[ ]`
- Default note → `·` or `*`
Infer the project name from the current working directory name, add `@ProjectName` tag.
Do NOT write to `projects/` directly.
