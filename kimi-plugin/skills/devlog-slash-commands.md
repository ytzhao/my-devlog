# Skill: DevLog Slash Commands

## Command Reference

| Command | Function |
|---------|----------|
| `/my-devlog <content>` | Record interstitial note |
| `/my-devlog-todo <content>` | Add todo item |
| `/my-devlog-done <keyword>` | Mark todo as completed |
| `/my-devlog-bug <description>` | Record bug/problem |
| `/my-devlog-learn <content>` | Record learning notes |
| `/my-devlog-idea <content>` | Record idea/inspiration |
| `/my-devlog-inbox <content>` | Quick capture to inbox |
| `/my-devlog-review` | Generate daily review |
| `/my-devlog-sync` | Manual sync trigger |
| `/my-devlog-weekly` | Generate weekly review |

## Configuration Paths

- DevLog root: `~/.devlog/` (or `DEVLOG_ROOT` env var)
- Global config: `~/.devlog/.devlog/config.md`
- Sync script: `python -m devlog.sync`
