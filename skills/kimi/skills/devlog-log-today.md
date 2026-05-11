# Skill: DevLog Recording

## Description

When user inputs `/log-devlog`, `/log-todo`, `/log-done`, `/log-bug`, `/log-learn`, `/log-idea`, `/log-inbox`, process according to the following rules.

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
