# My DevLog 📝

> AI-Native Interstitial Journaling for Developers
>
> 开发者专属的 AI 原生间歇性笔记系统

[English](#english) | [中文](#中文)

---

<a name="english"></a>
## English

### What is DevLog?

**DevLog** is a markdown-based bullet journal system designed for developers who use AI coding assistants (Claude Code, Kimi Code, OpenCode, etc.). It helps you track your daily work, bugs, learning, and ideas — all through simple slash commands in your AI tool.

### ✨ Features

- **🤖 AI-Native**: Speak to your AI assistant, it records everything. No manual file editing.
- **⚡ Zero-Friction Logging**: One slash command (`/log-devlog`) to capture a thought in 2 seconds.
- **📂 Auto-Organization**: AI writes to `daily/`, scripts auto-sync to `projects/` by tag.
- **🔀 Multi-AI Support**: Works with Claude Code, Kimi Code, OpenCode — or any AI with system prompts.
- **📊 Auto-Statistics**: Daily stats, weekly reviews — all generated automatically.
- **💯 Local-First**: All data stays on your machine. No cloud, no vendor lock-in.

### 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/ytzhao/my-devlog.git
cd my-devlog

# 2. Install (creates ~/.devlog/ and installs AI skills)
python install.py

# 3. Start your AI tool and log your first note
# In Claude Code / Kimi Code / OpenCode:
/log-devlog My first DevLog entry!
```

### 📋 Slash Commands

| Command | What it does |
|---------|-------------|
| `/log-devlog <note>` | Record an interstitial note |
| `/log-todo <task>` | Add a todo item |
| `/log-done <keyword>` | Mark a todo as completed |
| `/log-bug <description>` | Record a bug or problem |
| `/log-learn <content>` | Record something you learned |
| `/log-idea <content>` | Capture an idea or inspiration |
| `/log-inbox <content>` | Quick dump to inbox (archive later) |
| `/log-review` | Generate today's review |
| `/log-sync` | Manually trigger sync script |
| `/log-weekly` | Generate weekly review |

### 🗂️ Directory Structure

```
~/.devlog/                          # Your DevLog root (or DEVLOG_ROOT)
├── .devlog/
│   ├── config.md                   # Global config (symbols, root path)
│   ├── templates/                  # Markdown templates
│   ├── skills/                     # AI skill definitions
│   └── scripts/
│       └── sync.py                 # Auto-sync & statistics script
├── daily/
│   └── 2026-05-11.md               # Daily master log (AI writes here)
├── projects/                       # Project views (auto-generated)
│   └── MyProject/
│       ├── 2026-05.md              # Monthly aggregation
│       └── 2026-05-11.md           # Daily detail
├── topics/                         # Cross-project knowledge
│   ├── bugfix/
│   ├── learning/
│   └── ideas/
└── inbox.md                        # Quick capture box
```

### 🛠️ Supported AI Tools

| Tool | Setup | Status |
|------|-------|--------|
| **Claude Code** | `~/.claude/commands/` | ✅ Ready |
| **Kimi Code** | `~/.kimi/skills/` | ✅ Ready |
| **OpenCode** | System prompt injection | ✅ Ready |
| **Cursor / Copilot** | Custom instructions | 🔄 Adaptable |

### 📖 Documentation

- [Usage Manual (中文)](docs/使用手册.md)
- [Implementation Report (中文)](docs/实施报告.md) *(for reference)*

### ⚙️ Manual Sync

```bash
# Default: sync today + generate stats
python -m devlog.sync

# Archive inbox to daily/
python -m devlog.sync --archive-inbox

# Generate weekly report
python -m devlog.sync --weekly

# Custom root directory
python -m devlog.sync --root ~/my-custom-log
```

### 🏷️ Symbol System (Bullet Journal)

| Symbol | Meaning | Usage |
|--------|---------|-------|
| `·` | Note / Event | Completed work, meeting notes |
| `×` | Problem / Bug | Errors, stuck points, solutions |
| `-` | Learning | Articles read, knowledge gained |
| `!` | Idea / Inspiration | Sudden insights, product ideas |
| `○` | Todo | Pending tasks |
| `✓` | Done | Completed todos |
| `→` | Migrated | Moved to another day |

> ASCII fallback available: `*` `x` `-` `!` `[ ]` `[v]` `>>`

### 🤝 Contributing

Issues and PRs welcome! This is a personal tool grown from daily needs — your feedback makes it better.

### 📄 License

[MIT](LICENSE) — Free to use, modify, and distribute.

---

<a name="中文"></a>
## 中文

### DevLog 是什么？

**DevLog** 是一套面向 AI 编程助手用户的 Markdown 子弹笔记系统。通过与 Claude Code、Kimi Code、OpenCode 等 AI 工具集成，你只需要用 Slash Command（如 `/log-devlog`）说话，AI 就会自动帮你记录、整理、归档每天的开发日志。

### ✨ 核心特性

- **🤖 AI 原生**：对 AI 说话就能记录，无需手动操作文件
- **⚡ 零摩擦记录**：一条 Slash Command，2 秒 capture 一个想法
- **📂 自动归档**：AI 只写 `daily/`，脚本自动按 `@项目名` 标签分发到 `projects/`
- **🔀 多 AI 兼容**：支持 Claude Code、Kimi Code、OpenCode，甚至任何支持系统提示的 AI
- **📊 自动统计**：每日统计表格、每周回顾报告，全部自动生成
- **💯 本地优先**：所有数据保存在本地，不上传云端，无厂商锁定

### 🚀 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/ytzhao/my-devlog.git
cd my-devlog

# 2. 安装（创建 ~/.devlog/ 并安装 AI 技能）
python install.py

# 3. 启动你的 AI 工具，记录第一条笔记
# 在 Claude Code / Kimi Code / OpenCode 中输入：
/log-devlog 我的第一条 DevLog 笔记！
```

### 📋 Slash Command 清单

| 命令 | 功能 |
|------|------|
| `/log-devlog <内容>` | 记录间歇性笔记 |
| `/log-todo <内容>` | 添加待办 |
| `/log-done <关键词>` | 标记待办完成 |
| `/log-bug <描述>` | 记录踩坑 |
| `/log-learn <内容>` | 记录学习 |
| `/log-idea <内容>` | 记录灵感 |
| `/log-inbox <内容>` | 快速丢入收集箱 |
| `/log-review` | 今日回顾 |
| `/log-sync` | 手动同步 |
| `/log-weekly` | 周回顾 |

### 🗂️ 目录结构

```
~/.devlog/                          # DevLog 根目录（或 DEVLOG_ROOT 环境变量）
├── .devlog/
│   ├── config.md                   # 全局配置（符号方案、路径）
│   ├── templates/                  # Markdown 模板
│   ├── skills/                     # AI 技能定义
│   └── scripts/
│       └── sync.py                 # 自动同步与统计脚本
├── daily/
│   └── 2026-05-11.md               # 每日主日志（AI 直接写入）
├── projects/                       # 项目聚合视图（脚本自动生成）
│   └── 我的项目/
│       ├── 2026-05.md              # 按月聚合
│       └── 2026-05-11.md           # 当日详细
├── topics/                         # 跨项目知识沉淀
│   ├── bugfix/                     # 踩坑经验库
│   ├── learning/                   # 学习笔记
│   └── ideas/                      # 灵感仓库
└── inbox.md                        # 快速收集箱
```

### 🛠️ 支持的 AI 工具

| 工具 | 配置方式 | 状态 |
|------|---------|------|
| **Claude Code** | `~/.claude/commands/` | ✅ 已支持 |
| **Kimi Code** | `~/.kimi/skills/` | ✅ 已支持 |
| **OpenCode** | 系统提示注入 | ✅ 已支持 |
| **Cursor / Copilot** | 自定义指令 | 🔄 可适配 |

### 📖 文档

- [使用手册](docs/使用手册.md)
- [实施报告](docs/实施报告.md) *(供参考)*

### ⚙️ 手动运行同步脚本

```bash
# 默认：同步今日 + 生成统计
python -m devlog.sync

# 归档收集箱到 daily/
python -m devlog.sync --archive-inbox

# 生成本周回顾
python -m devlog.sync --weekly

# 指定自定义根目录
python -m devlog.sync --root ~/my-custom-log
```

### 🏷️ 符号系统（子弹笔记）

| 符号 | 含义 | 使用场景 |
|------|------|---------|
| `·` | 笔记/事件 | 完成的工作、会议记录 |
| `×` | 问题/踩坑 | Bug、报错、卡住的地方 |
| `-` | 学习/输入 | 阅读的文章、学到的知识 |
| `!` | 灵感/想法 | 突然想到的点子 |
| `○` | 待办 | 待完成的任务 |
| `✓` | 已完成 | 待办完成后标记 |
| `→` | 迁移 | 移到明天或其他日期 |

> 提供 ASCII 备用方案：`*` `x` `-` `!` `[ ]` `[v]` `>>`

### 🤝 贡献

欢迎提交 Issue 和 PR！这是一个从日常需求中生长出来的个人工具，你的反馈会让它变得更好。

### 📄 许可证

[MIT](LICENSE) — 自由使用、修改和分发。
