# My DevLog 使用手册

> 本文档面向 DevLog 系统的最终用户。
> 目标：用 5 分钟学会这套系统，然后每天只需 10 秒记录一条笔记。

---

## 1. 快速开始（Quick Start）

### 1.1 安装

```bash
# 方式 1：git clone
git clone https://github.com/ytzhao/my-devlog.git
cd my-devlog
python install.py

# 方式 2：指定自定义目录
python install.py --root ~/Documents/MyDevLog
```

安装完成后，你的 `~/.devlog/`（或自定义目录）结构如下：

```
~/.devlog/
├── .devlog/
│   ├── config.md          ← 全局配置
│   ├── templates/         ← 模板
│   ├── skills/            ← AI 技能定义
│   └── scripts/
│       └── sync.py        ← 同步脚本
├── daily/                 ← 每天的主日志
├── projects/              ← 项目聚合（脚本生成）
├── topics/                ← 跨项目知识沉淀
└── inbox.md               ← 快速收集箱
```

### 1.2 第一步：测试

在任何目录启动你的 AI 工具，输入：

```
/my-devlog 测试一下 DevLog 系统是否正常工作
```

如果 AI 回复"已记录..."，说明系统就绪。

---

## 2. 符号系统（Bullet Journal）

### 2.1 Unicode 方案（默认，推荐）

| 符号 | 含义 | 使用场景 |
|------|------|---------|
| `·` | 笔记/事件 | 完成的工作、会议记录 |
| `×` | 问题/踩坑 | Bug、报错、卡住的地方 |
| `-` | 学习/输入 | 学到的新知识、阅读的文章 |
| `!` | 灵感/想法 | 突然想到的点子 |
| `○` | 待办 | 待完成的任务 |
| `✓` | 已完成 | 待办完成后标记 |
| `→` | 迁移 | 未完成的任务移到明天 |

### 2.2 ASCII 备用方案（终端显示异常时使用）

编辑 `~/.devlog/.devlog/config.md`，将 `symbol-set` 改为 `ascii`：

| 符号 | 含义 |
|------|------|
| `*` | 笔记 |
| `x` | 问题 |
| `-` | 学习 |
| `!` | 灵感 |
| `[ ]` | 待办 |
| `[v]` | 已完成 |
| `>>` | 迁移 |

---

## 3. 标签规范

- **项目标签**：`@项目名`（如 `@MyProject`）
- **禁止**：`#项目名`（会与 Markdown 标题语法冲突）
- **自动推断**：AI 通常会自动识别你当前所在的项目目录，自动添加标签

---

## 4. Slash Command 完整清单

> 在任何已配置 DevLog 的 AI 工具中，输入以下命令即可快速操作。

| 命令 | 示例 | 效果 |
|------|------|------|
| `/my-devlog <内容>` | `/my-devlog 完成了登录页面设计` | 记录一条笔记，`·` |
| `/my-devlog-todo <内容>` | `/my-devlog-todo 写 API 文档` | 添加待办，`○` |
| `/my-devlog-done <关键词>` | `/my-devlog-done API` | 标记待办完成，`○→✓` |
| `/my-devlog-bug <描述>` | `/my-devlog-bug 数据库连接超时` | 记录踩坑，`×` |
| `/my-devlog-learn <内容>` | `/my-devlog-learn 了解了 JWT 刷新令牌机制` | 记录学习，`-` |
| `/my-devlog-idea <内容>` | `/my-devlog-idea 给系统加一个暗黑模式切换` | 记录灵感，`!` |
| `/my-devlog-inbox <内容>` | `/my-devlog-inbox 记得下周Review代码` | 丢入收集箱 |
| `/my-devlog-review` | `/my-devlog-review` | 生成今日回顾 |
| `/my-devlog-sync` | `/my-devlog-sync` | 手动触发同步脚本 |
| `/my-devlog-weekly` | `/my-devlog-weekly` | 生成本周回顾 |

---

## 5. 一天的工作流

### 5.1 工作时（状态切换时记录）

```
[开始一个新任务]
你: /my-devlog 开始设计数据库模型
AI: 已记录 → [10:00] · 开始设计数据库模型

[遇到问题]
你: /my-devlog-bug 外键约束导致插入失败
AI: 已记录 → [11:30] × 外键约束导致插入失败
     解决方案？
你: 先插父表再插子表
AI: 已追加 → 解决：先插父表再插子表

[学到一招]
你: /my-devlog-learn SQLAlchemy 的 relationship 可以自动处理级联
AI: 已记录 → [14:00] - SQLAlchemy 的 relationship 可以自动处理级联

[完成任务]
你: /my-devlog-done 数据库模型
AI: 已标记 → [16:00] ✓ 设计数据库模型

[突发灵感]
你: /my-devlog-idea 可以用 Redis 缓存用户权限，减少数据库查询
AI: 已记录 → [16:30] ! 可以用 Redis 缓存用户权限
```

### 5.2 下班前（回顾与同步）

```
你: /my-devlog-review
AI: 【今日回顾】2026-05-11
    记录数: 5 | 待办完成: 1/1 | 问题: 1 | 灵感: 1
    ✓ 今日完成: 设计数据库模型
    × 今日踩坑: 外键约束导致插入失败
    ! 灵感待评估: 可以用 Redis 缓存用户权限

你: /my-devlog-sync
AI: 已执行 sync.py，项目日志已同步到 projects/MyProject/
```

### 5.3 周五（周回顾）

```
你: /my-devlog-weekly
AI: 已生成周回顾 daily/weekly-2026-05-04.md
    本周共记录 28 条，投入最多项目: @MyProject (18条)
    踩坑 3 处，学习 5 项，灵感 2 个
```

---

## 6. 各 AI 工具的使用方式

### 6.1 Claude Code

**前提**：运行 `install.py` 时已自动安装到 `~/.claude/commands/`

**使用**：直接输入 `/my-devlog`、`/my-devlog-todo` 等命令

**进阶**：
- 命令文件位于 `~/.claude/commands/*.md`，可自行修改
- 若版本较低不支持 Markdown Command Spec，可通过系统提示注入工作

### 6.2 Kimi Code

**前提**：运行 `install.py` 时已自动安装到 `~/.kimi/skills/`

**使用**：直接输入 `/my-devlog`、`/my-devlog-todo` 等命令

**进阶**：
- 技能文件位于 `~/.kimi/skills/devlog-*.md`

### 6.3 OpenCode

**前提**：运行 `install.py` 时已自动安装到 `~/.opencode/`

**使用**：直接输入 `/my-devlog`、`/my-devlog-todo` 等命令

**进阶**：
- OpenCode 通过系统提示注入识别命令
- 若支持自定义工具，可将 `sync.py` 封装为工具函数

---

## 7. sync.py 手动维护操作

虽然 AI 可以执行 `/my-devlog-sync`，你也可以手动运行脚本：

### 7.1 常用命令

```bash
# 同步今日日志到 projects/
python -m devlog.sync --sync

# 归档 inbox 收集箱
python -m devlog.sync --archive-inbox

# 生成今日统计表格
python -m devlog.sync --daily-stats

# 生成指定日期的统计
python -m devlog.sync --daily-stats --date 2026-05-11

# 生成本周回顾
python -m devlog.sync --weekly

# 一键全量（归档 + 同步 + 统计）
python -m devlog.sync --archive-inbox --sync --daily-stats

# 指定自定义根目录
python -m devlog.sync --root ~/my-custom-log
```

### 7.2 设置环境变量（可选）

```bash
# Linux / macOS
export DEVLOG_ROOT=~/my-devlog

# Windows (PowerShell)
$env:DEVLOG_ROOT = "C:\Users\YourName\my-devlog"

# Windows (CMD)
set DEVLOG_ROOT=C:\Users\YourName\my-devlog
```

### 7.3 Windows 终端乱码处理

如果输出中文显示为乱码，先执行：

```bash
chcp 65001
```

再运行 `sync.py`。（不影响文件内容，仅影响终端显示。）

---

## 8. 文件速查

| 你想做的事 | 去哪里找 |
|-----------|---------|
| 看今天的工作记录 | `~/.devlog/daily/YYYY-MM-DD.md` |
| 看某个项目的汇总 | `~/.devlog/projects/项目名/YYYY-MM-DD.md` |
| 看某个月的项目汇总 | `~/.devlog/projects/项目名/YYYY-MM.md` |
| 看本周回顾 | `~/.devlog/daily/weekly-YYYY-MM-DD.md` |
| 快速丢入临时想法 | `~/.devlog/inbox.md` |
| 查看/修改系统配置 | `~/.devlog/.devlog/config.md` |
| 修改 AI 技能定义 | `~/.devlog/.devlog/skills/*.md` |
| 修改日志模板 | `~/.devlog/.devlog/templates/*.md` |
| 沉淀踩坑经验 | `~/.devlog/topics/bugfix/*.md` |
| 沉淀学习笔记 | `~/.devlog/topics/learning/*.md` |
| 沉淀灵感清单 | `~/.devlog/topics/ideas/*.md` |

---

## 9. 常见问题（FAQ）

### Q1：我换了电脑，DevLog 怎么迁移？

**A**：整个 `~/.devlog/` 目录是纯文本 Markdown 文件，直接复制到新机即可。修改 `~/.devlog/.devlog/config.md` 中的根目录路径后同步脚本自动适配。

### Q2：AI 没有识别我的 `/my-devlog` 命令？

**A**：检查以下配置是否存在：
- Claude Code: `~/.claude/commands/my-devlog.md`
- Kimi Code: `~/.kimi/skills/devlog-log-today.md`
- 重新运行 `python install.py` 可修复

### Q3：我想修改默认的符号方案？

**A**：编辑 `~/.devlog/.devlog/config.md`，将 `symbol-set: unicode` 改为 `symbol-set: ascii`。

### Q4：inbox 里面的记录什么时候会被归档？

**A**：以下方式均可触发归档：
- 运行 `python -m devlog.sync --archive-inbox`
- 让 AI 执行 `/my-devlog-sync`（默认行为包含归档）
- 配置 Git Hook 在每次 commit 后自动触发

### Q5：项目日志和 daily 日志内容重复吗？

**A**：`daily/` 是**主日志**（所有记录），`projects/` 是**提取视图**（只包含带 `@项目名` 标签的记录）。`projects/` 由 `sync.py` 自动生成，AI 不直接写入，无需手动维护。

### Q6：记录错了怎么修改？

**A**：直接编辑 `daily/YYYY-MM-DD.md`，修改后重新运行 `python -m devlog.sync --sync` 即可更新项目日志。

---

## 10. 最佳实践建议

1. **状态切换时记录**：开始一件事、结束一件事、被打断、恢复工作时，都是记录的最佳时机
2. **一句话原则**：每条记录控制在 1~2 句话，不要太长
3. **善用 /my-devlog-inbox**：临时想法先丢入 inbox，晚上统一归档，不打断当前工作流
4. **每天下班前 /my-devlog-review**：养成回顾习惯，及时发现未完成的待办
5. **每周五 /my-devlog-weekly**：周期性复盘，沉淀经验教训

---

> **祝你记录愉快。好的日志习惯，是高效开发者的秘密武器。**
