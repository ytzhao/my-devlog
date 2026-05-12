# Skill: DevLog Recording

## Description

When user inputs `/log-devlog`, `/log-todo`, `/log-done`, `/log-bug`, `/log-learn`, `/log-idea`, `/log-inbox`, process according to the following rules.

## Auto-Recording Rule

When the user describes any of the following during normal conversation, AUTOMATICALLY call `devlog_write_record` without asking for permission:

**Work progress:** completed, finished, done, implemented, deployed, merged, submitted, started working on, optimized, refactored, tested, reviewed
**Problems:** error, bug, crash, exception, failure, timeout, stuck, blocked, broken, not working
**Learning:** learned, read, studied, researched, discovered, realized, understood, documentation, principle
**Ideas & Plans:** idea, thought, maybe, could try, plan, design, proposal, next step, follow-up, TODO
**Decisions:** decided, chose, selected, picked, settled on, will use, going with

**Do NOT record:** greetings, small talk, confirmations ("ok", "got it", "thanks"), tool outputs, code dumps.
**Keep records concise: 1-2 sentences max.**

## Workflow

1. Read `.devlog/config.md` from current directory or parent directories to get root path and symbol scheme (unicode / ascii)
2. Determine symbol by command type:
   - `/log-devlog` → auto-detect (default `·` or `*`)
   - `/log-todo` → `○` or `[ ]`
   - `/log-done` → find `○` and mark `✓` or `[v]`
   - `/log-bug` → `×` or `x`
   - `/log-learn` → `-`
   - `/log-idea` → `!`
   - `/log-inbox` → write to inbox.md with full timestamp `[YYYY-MM-DD HH:MM]`
3. **Reduce interaction**: Infer project name from current working directory, add `@ProjectName` tag automatically. Only ask when跨-project or uncertain.
4. Write to `daily/YYYY-MM-DD.md` or `inbox.md`
5. **Do NOT write to `projects/` directly**, sync.py handles that automatically

## Tag Rules

- Use `@ProjectName` (e.g., `@MyProject`)
- **Do NOT** use `#ProjectName` (conflicts with Markdown H1 syntax)
