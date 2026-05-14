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
- **⚡ Zero-Friction Logging**: One slash command (`/my-devlog`) to capture a thought in 2 seconds. Or let AI auto-record during conversation.
- **📂 Auto-Organization**: AI writes to `daily/`, scripts auto-sync to `projects/` by tag.
- **🔌 MCP Server**: Claude Code connects directly via MCP — reliable tool calls instead of shell command guessing.
- **🔍 Full-Text Search**: Search across all logs by keyword, date range, or project tag.
- **📊 Auto-Statistics**: Daily stats, weekly reviews, mood tracking, time tracking — all automatic.
- **🔀 Multi-AI Support**: Works with Claude Code, Kimi Code, OpenCode — or any AI with system prompts.
- **📤 Backup & Export**: JSON, Markdown, or ZIP export at any time.
- **🔗 Obsidian / Logseq**: Generate wiki-linked vaults or Logseq journals with one command.
- **🌐 Web UI**: Optional Streamlit dashboard for browsing and visualizing your logs.
- **🤖 Auto-Record**: AI automatically detects work progress, problems, learning, and ideas during chat — no explicit command needed.
- **🪝 Session Hooks**: Auto-sync and generate weekly reports when AI session ends.
- **💯 Local-First**: All data stays on your machine. No cloud, no vendor lock-in.

### 🚀 Quick Start

#### For Claude Code (Recommended — via Plugin + MCP)

```bash
# 1. Install the Python package (provides the MCP server)
pip install -e .

# 2. In Claude Code, install the plugin
/plugin install devlog@github-marketplace
# Or add the local repo as a marketplace:
/plugin marketplace add ./
/plugin install devlog@local

# 3. Done! Use slash commands directly
/my-devlog My first DevLog entry!
```

> The plugin automatically registers the MCP server. AI calls tools directly — no shell command guessing.

#### For Kimi Code

```bash
# 1. 安装 Python 包（提供 tool 运行时）
pip install -e .

# 2. 在 Kimi Code 中安装 Plugin
kimi plugin install https://github.com/ytzhao/my-devlog.git

# 3. 完成！Plugin 自动提供 Skills + Tools
# 可以直接使用 /my-devlog 等命令，也可以自然语言调用工具
```

> Kimi Plugin 包含 **Skills**（/my-devlog 等 Slash Command）+ **Native Tools**（devlog_write_record, devlog_sync 等），AI 会自动选择最合适的方式执行。

#### For OpenCode / Manual Install

```bash
# 1. Clone the repo
git clone https://github.com/ytzhao/my-devlog.git
cd my-devlog

# 2. Install
pip install -e .
python install.py

# 3. OpenCode: config copied to ~/.opencode/
```

### 📋 Slash Commands

| Command | What it does |
|---------|-------------|
| `/my-devlog <note>` | Record an interstitial note |
| `/my-devlog-todo <task>` | Add a todo item |
| `/my-devlog-done <keyword>` | Mark a todo as completed |
| `/my-devlog-bug <description>` | Record a bug or problem |
| `/my-devlog-learn <content>` | Record something you learned |
| `/my-devlog-idea <content>` | Capture an idea or inspiration |
| `/my-devlog-inbox <content>` | Quick dump to inbox (archive later) |
| `/my-devlog-review` | Generate today's review |
| `/my-devlog-sync` | Manually trigger sync script |
| `/my-devlog-weekly` | Generate weekly review |

### 🗂️ Directory Structure

```
~/.devlog/                          # Your DevLog root (or DEVLOG_ROOT)
├── .devlog/
│   ├── config.md                   # Global config (symbols, language, root path)
│   ├── templates/                  # Markdown templates (daily.md, daily.en.md)
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
| **Claude Code** | `/plugin install devlog@github-marketplace` | ✅ MCP + Plugin |
| **Kimi Code** | `kimi plugin install` | ✅ Plugin (Skills + Tools) |
| **OpenCode** | `~/.opencode/` | ✅ Config |
| **Cursor / Copilot** | Custom instructions | 🔄 Adaptable |

### 🔌 MCP Server (Claude Code)

When the DevLog plugin is installed, Claude Code connects via **MCP (Model Context Protocol)**. The AI directly calls typed functions instead of guessing shell commands.

**Available MCP Tools:**

| Tool | Description |
|------|-------------|
| `devlog_read_daily` | Read daily log for a date |
| `devlog_write_record` | Append a record (auto-detects symbol) |
| `devlog_sync` | Sync daily → projects + stats |
| `devlog_archive_inbox` | Archive inbox to daily/ |
| `devlog_generate_stats` | Regenerate daily statistics |
| `devlog_generate_weekly` | Generate weekly report |
| `devlog_mark_done` | Mark todo as done by keyword |
| `devlog_list_todos` | List open todos |
| `devlog_search` | Search by keyword/date/project |
| `devlog_list_projects` | List all projects |
| `devlog_get_config` | Read configuration |
| `devlog_create_backup` | ZIP backup |
| `devlog_export_json` | Export to JSON |
| `devlog_export_md` | Export to single Markdown |

**Available MCP Resources:**

| Resource | Description |
|----------|-------------|
| `devlog://daily/{date}` | Daily log content |
| `devlog://inbox` | Inbox content |
| `devlog://config` | Configuration |
| `devlog://projects/{project}/{date}` | Project log |
| `devlog://weekly/{date}` | Weekly report |

### ⚙️ CLI Commands (Manual / Scripts)

All commands support `--root` to override the default directory.

#### Core Sync

```bash
# Default: sync today + generate stats
python -m devlog.sync

# Archive inbox to daily/
python -m devlog.sync --archive-inbox

# Generate daily statistics table
python -m devlog.sync --daily-stats

# Generate weekly report
python -m devlog.sync --weekly

# Specify date
python -m devlog.sync --sync --date 2026-05-12

# Full pipeline
python -m devlog.sync --archive-inbox --sync --daily-stats
```

#### Todo Management

```bash
# Mark todo as done by keyword
python -m devlog.mark_done "API"

# List open todos
python -m devlog.mark_done --list
```

#### Search

```bash
# Search by keyword
python -m devlog.search "database"

# Date range
python -m devlog.search "bug" --from 2026-05-01 --to 2026-05-12

# Filter by project
python -m devlog.search --project MyProject

# List all projects
python -m devlog.search --list-projects
```

#### Backup & Export

```bash
# Export to JSON
python -m devlog.backup --export-json devlog-data.json

# Export to Markdown
python -m devlog.backup --export-md devlog-all.md

# ZIP backup
python -m devlog.backup --backup devlog-backup.zip
```

#### Obsidian / Logseq

```bash
# Generate Obsidian vault
python -m devlog.obsidian --obsidian

# Generate Logseq journals
python -m devlog.obsidian --logseq
```

#### Web UI (Optional)

```bash
pip install -e ".[web]"
streamlit run devlog/webui.py
```

### 🔧 Advanced Features

#### Auto-Recording

DevLog can automatically capture valuable content from your AI conversations without explicit `/my-devlog` commands.

**How it works:**
- AI detects when you describe work progress, problems, learning, ideas, or decisions
- Automatically calls `devlog_write_record` in the background
- Keeps records concise (1-2 sentences)

**Example conversation:**
```
You: Just finished the login API, testing now
AI: [auto-records] → [14:30] · Finished login API, now testing

You: Hmm, the JWT token keeps expiring too fast
AI: [auto-records] → [14:35] × JWT token expires too fast

You: Oh I see, I need to set a longer expiry in the config
AI: [auto-records] → [14:36] - Need longer JWT expiry in config
```

**Post-Session Batch Mode:**
If you prefer not to record in real-time, run batch analysis after a session:
```bash
# Analyze latest Kimi session and batch-write to daily log
python -m devlog.auto_record --kimi

# Analyze latest Claude session
python -m devlog.auto_record --claude

# Preview without writing
python -m devlog.auto_record --kimi --dry-run
```

**Session-End Hook (Kimi Code):**
Add to `~/.kimi/config.toml`:
```toml
[[hooks]]
event = "Stop"
command = "python -m devlog.auto_record --kimi"
```

#### Time Tracking

Use time ranges and DevLog calculates durations automatically:

```markdown
[09:00-10:30] · Designed database model @MyProject
[14:00-15:15] × Debugged connection pool issue
```

#### Mood Tracking

Add a mood score at the end of your daily log:

```markdown
(mood: 4/5)
```

#### Hashtags

Use hashtags for custom categorization:

```markdown
[10:00] · Completed login API #priority-high #backend
```

#### Git Hook Auto-Sync

```bash
cp examples/git-hooks/post-commit .git/hooks/post-commit
chmod +x .git/hooks/post-commit   # Linux/macOS
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

> ASCII fallback: `*` `x` `-` `!` `[ ]` `[v]` `>>`

### ⚙️ Configuration

Edit `~/.devlog/.devlog/config.md`:

```markdown
- **Root Directory**: `~/.devlog`
- **Symbol Set**: `unicode`     # unicode | ascii
- **Language**: `auto`          # zh | en | auto
```

Or use the `DEVLOG_ROOT` environment variable:

```bash
# Linux / macOS
export DEVLOG_ROOT=~/my-devlog

# Windows PowerShell
$env:DEVLOG_ROOT = "C:\Users\YourName\my-devlog"
```

### 📖 Documentation

- [Usage Manual (中文)](docs/USAGE.md)
- [CHANGELOG](CHANGELOG.md)
- [CONTRIBUTING](CONTRIBUTING.md)

### 🤝 Contributing

Issues and PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

### 📄 License

[MIT](LICENSE) — Free to use, modify, and distribute.

---

<a name="中文"></a>
## 中文

### DevLog 是什么？

**DevLog** 是一套面向 AI 编程助手用户的 Markdown 子弹笔记系统。通过与 Claude Code、Kimi Code、OpenCode 等 AI 工具集成，你只需要用 Slash Command（如 `/my-devlog`）说话，AI 就会自动帮你记录、整理、归档每天的开发日志。

### ✨ 核心特性

- **🤖 AI 原生**：对 AI 说话就能记录，无需手动操作文件
- **⚡ 零摩擦记录**：一条 Slash Command，2 秒 capture 一个想法；或让 AI 在对话中自动识别并记录
- **📂 自动归档**：AI 只写 `daily/`，脚本自动按 `@项目名` 标签分发到 `projects/`
- **🔌 MCP Server**：Claude Code 通过 MCP 直连，AI 直接调用函数而非猜 shell 命令
- **🔍 全文搜索**：支持关键词、日期范围、项目标签搜索
- **📊 自动统计**：每日统计、周回顾、情绪追踪、工时统计，全部自动生成
- **📤 备份导出**：随时导出 JSON / Markdown / ZIP
- **🔗 双链笔记**：一键生成 Obsidian wiki-link 库或 Logseq 日记
- **🌐 Web 面板**：可选 Streamlit 可视化看板
- **🤖 自动记录**：AI 在聊天中自动识别工作进展、问题、学习、想法 —— 无需显式触发命令
- **🪝 会话 Hook**：AI 会话结束时自动同步、生成本周回顾
- **💯 本地优先**：所有数据保存在本地，不上传云端，无厂商锁定

### 🚀 快速开始

#### Claude Code 用户（推荐 — Plugin + MCP）

```bash
# 1. 安装 Python 包（提供 MCP Server）
pip install -e .

# 2. 在 Claude Code 中安装插件
/plugin install devlog@github-marketplace
# 或者添加本地仓库为 marketplace：
/plugin marketplace add ./
/plugin install devlog@local

# 3. 完成！直接使用 Slash Command
/my-devlog 我的第一条 DevLog 笔记！
```

> 插件自动注册 MCP Server，AI 直接调用工具函数，无需猜测 shell 命令。

#### Kimi Code

```bash
# 1. 安装 Python 包（提供 tool 运行时）
pip install -e .

# 2. 在 Kimi Code 中安装 Plugin
kimi plugin install https://github.com/ytzhao/my-devlog.git

# 3. 完成！Plugin 自动提供 Skills + Tools
```

> Kimi Plugin 包含 **Skills**（/my-devlog 等 Slash Command）+ **Native Tools**（devlog_write_record, devlog_sync 等），AI 会自动选择最合适的方式执行。

#### OpenCode / 手动安装

```bash
# 1. 克隆仓库
git clone https://github.com/ytzhao/my-devlog.git
cd my-devlog

# 2. 安装
pip install -e .
python install.py

# 3. OpenCode: 配置已复制到 ~/.opencode/
```

### 📋 Slash Command 清单

| 命令 | 功能 |
|------|------|
| `/my-devlog <内容>` | 记录间歇性笔记 |
| `/my-devlog-todo <内容>` | 添加待办 |
| `/my-devlog-done <关键词>` | 标记待办完成 |
| `/my-devlog-bug <描述>` | 记录踩坑 |
| `/my-devlog-learn <内容>` | 记录学习 |
| `/my-devlog-idea <内容>` | 记录灵感 |
| `/my-devlog-inbox <内容>` | 快速丢入收集箱 |
| `/my-devlog-review` | 今日回顾 |
| `/my-devlog-sync` | 手动同步 |
| `/my-devlog-weekly` | 周回顾 |

### 🗂️ 目录结构

```
~/.devlog/                          # DevLog 根目录（或 DEVLOG_ROOT 环境变量）
├── .devlog/
│   ├── config.md                   # 全局配置（符号方案、语言、路径）
│   ├── templates/                  # Markdown 模板（daily.md / daily.en.md）
│   ├── skills/                     # AI 技能定义
│   └── scripts/
│       └── sync.py                 # 自动同步与统计脚本
├── daily/                          # 每日主日志（AI 直接写入）
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
| **Claude Code** | `/plugin install devlog@github-marketplace` | ✅ MCP + Plugin |
| **Kimi Code** | `~/.kimi/skills/` | ✅ Skills |
| **OpenCode** | `~/.opencode/` | ✅ Config |
| **Cursor / Copilot** | 自定义指令 | 🔄 可适配 |

### 🔌 MCP Server（Claude Code）

安装 DevLog 插件后，Claude Code 通过 **MCP（Model Context Protocol）** 连接 DevLog。AI 直接调用类型化的函数，而不是猜测 shell 命令。

**MCP Tools：**

| 工具 | 说明 |
|------|------|
| `devlog_read_daily` | 读取指定日期的 daily log |
| `devlog_write_record` | 追加记录（自动识别符号） |
| `devlog_sync` | 同步 daily → projects + 统计 |
| `devlog_archive_inbox` | 归档 inbox 到 daily/ |
| `devlog_generate_stats` | 重新生成每日统计 |
| `devlog_generate_weekly` | 生成本周回顾 |
| `devlog_mark_done` | 按关键词标记待办完成 |
| `devlog_list_todos` | 列出待办 |
| `devlog_search` | 搜索日志 |
| `devlog_list_projects` | 列出所有项目 |
| `devlog_get_config` | 读取配置 |
| `devlog_create_backup` | ZIP 备份 |
| `devlog_export_json` | 导出 JSON |
| `devlog_export_md` | 导出 Markdown |

**MCP Resources：**

| 资源 | 说明 |
|------|------|
| `devlog://daily/{date}` | 每日日志 |
| `devlog://inbox` | 收集箱 |
| `devlog://config` | 配置信息 |
| `devlog://projects/{project}/{date}` | 项目日志 |
| `devlog://weekly/{date}` | 周回顾 |

### ⚙️ 命令行工具（手动 / 脚本）

所有命令都支持 `--root` 参数指定自定义目录。

#### 核心同步

```bash
# 默认：同步今日 + 生成统计
python -m devlog.sync

# 归档收集箱到 daily/
python -m devlog.sync --archive-inbox

# 生成今日统计表格
python -m devlog.sync --daily-stats

# 生成本周回顾
python -m devlog.sync --weekly

# 指定日期操作
python -m devlog.sync --sync --date 2026-05-12

# 一键全量：归档 + 同步 + 统计
python -m devlog.sync --archive-inbox --sync --daily-stats
```

#### 待办管理

```bash
# 按关键词标记待办完成
python -m devlog.mark_done "API"

# 列出今日所有待办
python -m devlog.mark_done --list
```

#### 搜索

```bash
# 按关键词搜索
python -m devlog.search "数据库"

# 搜索日期范围
python -m devlog.search "bug" --from 2026-05-01 --to 2026-05-12

# 按项目标签过滤
python -m devlog.search --project MyProject

# 列出所有项目及记录数
python -m devlog.search --list-projects
```

#### 备份与导出

```bash
# 导出为 JSON
python -m devlog.backup --export-json devlog-data.json

# 导出为单个 Markdown 文件
python -m devlog.backup --export-md devlog-all.md

# 创建 ZIP 备份
python -m devlog.backup --backup devlog-backup.zip
```

#### Obsidian / Logseq

```bash
# 生成 Obsidian vault（@项目名 转为 [[wiki-link]]）
python -m devlog.obsidian --obsidian

# 生成 Logseq journals
python -m devlog.obsidian --logseq
```

#### Web UI（可选）

```bash
pip install -e ".[web]"
streamlit run devlog/webui.py
```

### 🔧 进阶功能

#### 自动记录

DevLog 可以在你使用 AI 工具对话时，自动识别有价值的内容并记录，无需显式输入 `/my-devlog`。

**工作原理：**
- AI 检测到你描述工作进展、问题、学习、想法或决策时
- 自动在后台调用 `devlog_write_record`
- 保持记录简洁（1-2 句话）

**对话示例：**
```
你：刚写完登录 API，现在在测试
AI: [自动记录] → [14:30] · 刚写完登录 API，现在在测试

你：JWT token 过期太快了
AI: [自动记录] → [14:35] × JWT token 过期太快

你：哦我知道了，需要在配置里设置更长的过期时间
AI: [自动记录] → [14:36] - 需要在配置里设置更长的 JWT 过期时间
```

**会后批量模式：**
如果你不想实时记录，可以在会话结束后批量分析：
```bash
# 分析最新 Kimi 会话并批量写入 daily log
python -m devlog.auto_record --kimi

# 分析最新 Claude 会话
python -m devlog.auto_record --claude

# 预览（不写入）
python -m devlog.auto_record --kimi --dry-run
```

**会话结束 Hook（Kimi Code）：**
在 `~/.kimi/config.toml` 中添加：
```toml
[[hooks]]
event = "Stop"
command = "python -m devlog.auto_record --kimi"
```

#### 时间追踪

在日志中使用时间区间，DevLog 会自动计算工时：

```markdown
[09:00-10:30] · 设计数据库模型 @MyProject
[14:00-15:15] × 调试连接池问题
```

#### 情绪追踪

在每日日志末尾添加情绪评分：

```markdown
(mood: 4/5)
```

#### Hashtag 标签

使用 hashtag 进行自定义分类：

```markdown
[10:00] · 完成登录接口 #priority-high #backend
```

#### Git Hook 自动同步

```bash
# 复制 hook 到项目
cp examples/git-hooks/post-commit .git/hooks/post-commit
chmod +x .git/hooks/post-commit   # Linux/macOS
```

每次 `git commit` 后自动触发 `devlog-sync --sync`。

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

### ⚙️ 配置

编辑 `~/.devlog/.devlog/config.md`：

```markdown
- **Root Directory**: `~/.devlog`
- **Symbol Set**: `unicode`     # unicode | ascii
- **Language**: `auto`          # zh | en | auto
```

或通过环境变量指定根目录：

```bash
# Linux / macOS
export DEVLOG_ROOT=~/my-devlog

# Windows PowerShell
$env:DEVLOG_ROOT = "C:\Users\YourName\my-devlog"
```

### 📖 文档

- [使用手册](docs/USAGE.md)
- [CHANGELOG](CHANGELOG.md)
- [CONTRIBUTING](CONTRIBUTING.md)

### 🤝 贡献

欢迎提交 Issue 和 PR！详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

### 📄 许可证

[MIT](LICENSE) — 自由使用、修改和分发。
