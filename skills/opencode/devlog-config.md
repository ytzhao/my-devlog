# DevLog Configuration for OpenCode

## Integration Methods

### Method A: System Prompt Injection

Add the following to OpenCode's system prompt or project configuration:

```
## DevLog Developer Journal System

This project uses DevLog to record development logs.

When the user inputs the following commands, execute the corresponding actions directly:
- /my-devlog <content> → Record to daily/YYYY-MM-DD.md
- /my-devlog-todo <content> → Add todo
- /my-devlog-done <keyword> → Mark todo complete
- /my-devlog-bug <description> → Record problem
- /my-devlog-learn <content> → Record learning
- /my-devlog-idea <content> → Record idea
- /my-devlog-inbox <content> → Write to inbox.md
- /my-devlog-review → Generate daily review
- /my-devlog-sync → Execute python -m devlog.sync
- /my-devlog-weekly → Generate weekly review

Rules:
1. Read .devlog/config.md from current directory or parents to get configuration
2. Use @ProjectName for tags (NOT #ProjectName)
3. AI only writes to daily/ and inbox.md, never to projects/ directly
4. Symbol scheme follows config: unicode (· × ○ ✓ →) or ascii (* x [ ] [v] >>)
```

### Method B: Custom Tool (if OpenCode supports)

Wrap `python -m devlog.sync` as a custom tool function for OpenCode to invoke.

## Reference

- Global config: `~/.devlog/.devlog/config.md`
- Skill definitions: See `skills/` directory in this package
