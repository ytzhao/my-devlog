# Skill: DevLog Slash Commands

## Command Reference

| Command | Function |
|---------|----------|
| `/log-devlog <content>` | Record interstitial note |
| `/log-todo <content>` | Add todo item |
| `/log-done <keyword>` | Mark todo as completed |
| `/log-bug <description>` | Record bug/problem |
| `/log-learn <content>` | Record learning notes |
| `/log-idea <content>` | Record idea/inspiration |
| `/log-inbox <content>` | Quick capture to inbox |
| `/log-review` | Generate daily review |
| `/log-sync` | Manual sync trigger |
| `/log-weekly` | Generate weekly review |

## Configuration Paths

- DevLog root: `~/.devlog/` (or `DEVLOG_ROOT` env var)
- Global config: `~/.devlog/.devlog/config.md`
- Sync script: `python -m devlog.sync`
