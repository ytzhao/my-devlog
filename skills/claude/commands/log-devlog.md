---
description: "Record an interstitial note to DevLog"
model: default
---

Use the `devlog_write_record` MCP tool to append a note to today's daily log.
- Pass the user's message as the `content` argument.
- Leave `symbol` as "auto" to let the server detect the appropriate symbol.
- The server infers the project tag from the current working directory.
- Do NOT write to `projects/` directly.
