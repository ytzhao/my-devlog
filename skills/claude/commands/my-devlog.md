---
description: "DevLog — AI-native developer journal. Record work, bugs, learning, ideas, todos. AI auto-detects and records during conversation."
model: default
---

## Explicit Command

When user invokes `/my-devlog <content>`, use `devlog_write_record` MCP tool:
- Pass the user's message as `content`.
- Leave `symbol` as "auto" to auto-detect (problem→×, learn→-, idea→!, todo→○, default→·).

## Auto-Recording

During normal conversation, AUTOMATICALLY call `devlog_write_record` when the user describes:

- **Work progress**: completed, finished, done, implemented, deployed, merged, optimized, refactored, fixed
- **Problems**: error, bug, crash, exception, stuck, blocked, broken, not working
- **Learning**: learned, read, studied, researched, discovered, realized, understood
- **Ideas**: idea, thought, maybe, could try, should try
- **Decisions**: decided, chose, selected, will use, switching to
- **Todos**: need to, should, TODO, next step, follow-up

**Do NOT record**: greetings, small talk, confirmations, tool outputs, trivial requests.

**Rules**: Keep records concise (1-2 sentences). Infer project tag from current working directory. Do NOT write to `projects/` directly.

## Special Actions

When user's intent clearly matches one of these, use the corresponding MCP tool:

| User intent | MCP tool |
|---|---|
| Mark todo done | `devlog_mark_done` with keyword |
| List open todos | `devlog_list_todos` |
| Today's review | `devlog_read_daily` for today, then summarize |
| Sync / archive | `devlog_archive_inbox` → `devlog_sync` → `devlog_generate_stats` |
| Weekly review | `devlog_generate_weekly` then `devlog_read_daily` for the report |
| Search logs | `devlog_search` with keyword/date/project |
