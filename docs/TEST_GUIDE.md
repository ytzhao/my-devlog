# My DevLog 功能测试指南

> 按此文档逐一验证 my-devlog 的核心功能。
> 环境：Windows PowerShell / Python 3.11+

---

## 测试前准备

```powershell
# 1. 进入项目目录
cd D:\Projects\my-devlog

# 2. 确认环境变量（指向测试目录或默认目录）
$env:DEVLOG_ROOT = "$env:USERPROFILE\.devlog"
# 或用当前项目做测试：
# $env:DEVLOG_ROOT = "D:\Projects\my-devlog"

# 3. 确认编码
chcp 65001

# 4. 验证 Python 模块可导入
python -c "from devlog.sync import DevLogSync; print('OK')"
```

---

## 测试 1：基础记录（kimi_tool write_record）

**目的**：验证 `/my-devlog` 等命令的底层工具是否正常工作。

```powershell
# 记录一条普通笔记
echo '{"content": "完成了登录页面设计 @TestProject"}' | python -m devlog.kimi_tool write_record
```

**预期输出**：
```
[OK] Recorded: [HH:MM] · 完成了登录页面设计 @TestProject | synced
```

**验证**：
```powershell
# 检查 daily 日志
Get-Content "$env:DEVLOG_ROOT\daily\$(Get-Date -Format 'yyyy-MM-dd').md" -Tail 10

# 确认记录存在，且包含时间戳、符号、内容、项目标签
```

---

## 测试 2：自动分类（加权分类）

**目的**：验证 AI 能根据内容语义自动选择正确符号。

```powershell
# 测试各类别，观察符号是否正确

# 2.1 完成类 → 应为 · (note)
echo '{"content": "完成了数据库设计"}' | python -m devlog.kimi_tool write_record

# 2.2 修复类 → 应为 · (note)，不是 × (problem)
echo '{"content": "修复了连接池bug"}' | python -m devlog.kimi_tool write_record

# 2.3 问题类 → 应为 × (problem)
echo '{"content": "遇到数据库连接超时"}' | python -m devlog.kimi_tool write_record

# 2.4 学习类 → 应为 - (learning)
echo '{"content": "了解了JWT刷新令牌机制"}' | python -m devlog.kimi_tool write_record

# 2.5 灵感类 → 应为 ! (idea)
echo '{"content": "想到可以用Redis做缓存"}' | python -m devlog.kimi_tool write_record

# 2.6 待办类 → 应为 ○ (todo)
echo '{"content": "还没写API文档"}' | python -m devlog.kimi_tool write_record
```

**预期结果**：
| 内容 | 符号 |
|------|------|
| 完成了数据库设计 | · |
| 修复了连接池bug | · |
| 遇到数据库连接超时 | × |
| 了解了JWT刷新令牌机制 | - |
| 想到可以用Redis做缓存 | ! |
| 还没写API文档 | ○ |

**验证**：
```powershell
Get-Content "$env:DEVLOG_ROOT\daily\$(Get-Date -Format 'yyyy-MM-dd').md"
# 逐行检查符号是否正确
```

---

## 测试 3：自动同步流水线（Sync Pipeline）

**目的**：验证写入记录后，projects/ 目录和 stats 表是否自动生成。

```powershell
# 3.1 写入一条带项目标签的记录
echo '{"content": "测试自动同步功能 @SyncTest"}' | python -m devlog.kimi_tool write_record

# 3.2 验证 projects/ 目录已生成
Test-Path "$env:DEVLOG_ROOT\projects\SyncTest\$(Get-Date -Format 'yyyy-MM-dd').md"

# 3.3 验证 projects/ 文件包含该记录
Get-Content "$env:DEVLOG_ROOT\projects\SyncTest\$(Get-Date -Format 'yyyy-MM-dd').md"

# 3.4 验证 daily log 里的 Stats 表格已更新
# 查找 Stats 表格中 Note 的 count 是否增加
```

**预期结果**：
- `projects/SyncTest/YYYY-MM-DD.md` 存在且包含记录
- `daily/YYYY-MM-DD.md` 中 Stats 表格的计数正确
- `projects/SyncTest/YYYY-MM.md` 月度汇总存在

---

## 测试 4：Daily Reflection 自动生成

**目的**：验证 reflection 能基于当天记录自动结构化生成。

```powershell
# 4.1 先写入几类不同记录（如果之前测试已写入，可直接用）
echo '{"content": "完成了模块A开发 @RefTest"}' | python -m devlog.kimi_tool write_record
echo '{"content": "遇到内存泄漏问题 @RefTest"}' | python -m devlog.kimi_tool write_record
echo '{"content": "了解了Python GIL机制 @RefTest"}' | python -m devlog.kimi_tool write_record
echo '{"content": "想到可以用协程优化 @RefTest"}' | python -m devlog.kimi_tool write_record
echo '{"content": "还没写单元测试 @RefTest"}' | python -m devlog.kimi_tool write_record

# 4.2 手动触发 reflection 生成
echo '{}' | python -m devlog.kimi_tool review
# 或直接用 sync 模块：
# python -m devlog.sync --reflection
```

**预期输出**：
```
[OK] Generated reflection for daily/YYYY-MM-DD.md
```

**验证**：
```powershell
# 查看 daily log 的 Reflections 区域
$daily = Get-Content "$env:DEVLOG_ROOT\daily\$(Get-Date -Format 'yyyy-MM-dd').md" -Raw
# 确认包含以下 section：
# - What I Did
# - Problems & Fixes
# - What I Learned
# - Ideas
# - Remaining
# - Projects 分布统计
```

---

## 测试 5：Auto Record（AI 会话自动分析）

**目的**：验证从 Kimi/Claude 会话文件中自动提取记录。

```powershell
# 5.1 创建一个模拟的 Kimi 会话文件
$sessionDir = "$env:TEMP\fake_kimi_session"
New-Item -ItemType Directory -Path $sessionDir -Force | Out-Null
$contextFile = "$sessionDir\context.jsonl"
@'
{"role":"user","content":"完成了用户认证模块的开发"}
{"role":"assistant","content":"好的，已记录"}
{"role":"user","content":"遇到OAuth回调地址配置错误"}
{"role":"user","content":"了解了PKCE流程的原理"}
{"role":"user","content":"想到可以用Redis存储session"}
{"role":"user","content":"还没写集成测试"}
'@ | Set-Content $contextFile -Encoding UTF8

# 5.2 运行 auto_record（指定文件）
python -m devlog.auto_record --file $contextFile --date $(Get-Date -Format 'yyyy-MM-dd')
```

**预期输出**：
```
[INFO] Analyzing session: ...
[INFO] Found X user messages
[INFO] After dedup: Y unique messages
[INFO] Auto-recorded Z entries to daily/YYYY-MM-DD.md
[INFO] Auto-synced projects & stats for YYYY-MM-DD
```

**验证**：
```powershell
# 检查 daily log 中是否包含以下记录（自动分类后的）
# · 完成了用户认证模块的开发
# × 遇到OAuth回调地址配置错误
# - 了解了PKCE流程的原理
# ! 想到可以用Redis存储session
# ○ 还没写集成测试

Get-Content "$env:DEVLOG_ROOT\daily\$(Get-Date -Format 'yyyy-MM-dd').md" | Select-String "用户认证|OAuth|PKCE|Redis|集成测试"
```

---

## 测试 6：待办管理（Todo CRUD）

**目的**：验证添加待办、标记完成、列出待办功能。

```powershell
# 6.1 添加待办
echo '{"content": "写API文档 @TodoTest"}' | python -m devlog.kimi_tool write_record
# 或直接测试 list_todos（需要先有待办记录）

# 6.2 列出未完成的待办
echo '{"date":"$(Get-Date -Format 'yyyy-MM-dd')"}' | python -m devlog.kimi_tool list_todos

# 6.3 标记完成
echo '{"keyword": "API", "date":"$(Get-Date -Format 'yyyy-MM-dd')"}' | python -m devlog.kimi_tool mark_done

# 6.4 再次列出，确认已消失
echo '{}' | python -m devlog.kimi_tool list_todos
```

**预期结果**：
- list_todos 第一步能显示 `[ ] 写API文档 @TodoTest`
- mark_done 后显示 `[OK] Marked todo matching 'API' as done.`
- 再次 list_todos 不再显示该条目（或显示为 ✓）

---

## 测试 7：Inbox 归档

**目的**：验证 inbox.md 的记录能按时间归档到 daily/。

```powershell
# 7.1 创建测试 inbox
@'
# Inbox

[2026-05-13 09:00] · 临时想法1 @InboxTest
[2026-05-13 10:30] × 发现一个bug @InboxTest
[2026-05-12 08:00] · 昨天的想法 @InboxTest
'@ | Set-Content "$env:DEVLOG_ROOT\inbox.md" -Encoding UTF8

# 7.2 执行归档
python -m devlog.sync --archive-inbox
```

**预期输出**：
```
[OK] Archived 2 records to daily/2026-05-13.md
[OK] Archived 1 records to daily/2026-05-12.md
[OK] inbox.md archived 3 records and cleared
```

**验证**：
```powershell
# 检查对应日期的 daily log 是否包含 inbox 记录
Get-Content "$env:DEVLOG_ROOT\daily\2026-05-13.md" | Select-String "临时想法1|发现一个bug"
Get-Content "$env:DEVLOG_ROOT\daily\2026-05-12.md" | Select-String "昨天的想法"

# 检查 inbox.md 是否已清空（只剩标题）
Get-Content "$env:DEVLOG_ROOT\inbox.md"
```

---

## 测试 8：搜索功能

**目的**：验证跨日期、跨项目的日志搜索。

```powershell
# 8.1 先确保有搜索目标（前面测试已产生大量记录）

# 8.2 按关键词搜索
echo '{"keyword": "Redis"}' | python -m devlog.kimi_tool search

# 8.3 按项目搜索
echo '{"project": "RefTest"}' | python -m devlog.kimi_tool search

# 8.4 按日期范围搜索
echo '{"keyword": "完成", "date_from": "2026-05-01", "date_to": "2026-05-31"}' | python -m devlog.kimi_tool search
```

**预期结果**：
- 搜索结果按日期分组显示
- 匹配的记录包含关键词、项目标签、时间戳
- 最后显示 `Total: X records`

---

## 测试 9：周报生成

**目的**：验证周报能聚合本周所有记录。

```powershell
# 9.1 触发周报生成
echo '{}' | python -m devlog.kimi_tool generate_weekly
# 或：python -m devlog.sync --weekly
```

**预期输出**：
```
[OK] Weekly report generated for week starting YYYY-MM-DD.
```

**验证**：
```powershell
# 检查 weekly 文件是否生成
$weeklyFile = Get-ChildItem "$env:DEVLOG_ROOT\daily\weekly-*.md" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Get-Content $weeklyFile.FullName

# 确认包含：
# - 本周总记录数
# - Todo 完成率
# - 项目时间分布
# - 问题汇总
# - 灵感汇总
```

---

## 测试 10：Web 高亮服务器

**目的**：验证浏览器扩展后端能接收高亮并自动归档。

```powershell
# 10.1 启动服务器（后台运行，或新开窗口）
python tools\web_highlight_server.py
```

**10.2 模拟浏览器发送高亮数据**（另开一个 PowerShell）：
```powershell
$body = @{
    title = "测试文章标题"
    url = "https://example.com/test"
    text = "这是一段测试高亮文本"
    note = "我的笔记"
    tag = "article"
    screenshot = ""
} | ConvertTo-Json -Depth 3

Invoke-RestMethod -Uri "http://localhost:3721/highlight" -Method POST -Body $body -ContentType "application/json"
```

**预期输出**（在服务器窗口）：
```
[OK] Auto-synced projects & stats for YYYY-MM-DD
[OK] HH:MM | 测试文章标题 | screenshot=no
```

**验证**：
```powershell
# 检查 daily log 是否包含 Web 高亮记录
Get-Content "$env:DEVLOG_ROOT\daily\$(Get-Date -Format 'yyyy-MM-dd').md" | Select-String "Web:"

# 检查 assets 目录是否生成文件
Get-ChildItem "$env:DEVLOG_ROOT\assets\web-highlights\$(Get-Date -Format 'yyyy-MM-dd')\"
```

---

## 测试 11：命令行 sync 全量操作

**目的**：验证 `python -m devlog.sync` 的各种参数组合。

```powershell
# 11.1 指定日期全量同步
python -m devlog.sync --sync --date 2026-05-13

# 11.2 仅生成统计
python -m devlog.sync --daily-stats --date 2026-05-13

# 11.3 仅生成 reflection
python -m devlog.sync --reflection --date 2026-05-13

# 11.4 归档 + 同步 + 统计（一键全量）
python -m devlog.sync --archive-inbox --sync --daily-stats

# 11.5 生成周报
python -m devlog.sync --weekly
```

**预期结果**：
- 每个命令执行成功，输出 `[OK] ...`
- `--sync` 后 projects/ 目录更新
- `--daily-stats` 后 Stats 表格数字正确
- `--reflection` 后 Reflections 区域更新
- `--weekly` 后 weekly-*.md 文件生成

---

## 测试 12：边界情况

### 12.1 空内容记录
```powershell
echo '{"content": ""}' | python -m devlog.kimi_tool write_record
# 预期：[ERROR] Missing 'content' argument
```

### 12.2 重复内容去重
```powershell
# 连续两次写入相同内容
echo '{"content": "去重测试内容"}' | python -m devlog.kimi_tool write_record
echo '{"content": "去重测试内容"}' | python -m devlog.kimi_tool write_record
# 预期：daily log 中只有一条（第二条的 sync 仍执行，但记录不重复追加）
```

### 12.3 无记录日期的 reflection
```powershell
echo '{"date": "2020-01-01"}' | python -m devlog.kimi_tool review
# 预期：[SKIP] daily/2020-01-01.md does not exist
```

### 12.4 auto_record 空会话
```powershell
"" | Set-Content "$env:TEMP\empty_session.jsonl" -Encoding UTF8
python -m devlog.auto_record --file "$env:TEMP\empty_session.jsonl"
# 预期：[INFO] No new records to write 或 0 entries
```

---

## 测试清理

测试完成后，清理测试数据：

```powershell
# 删除测试生成的 daily 文件（谨慎操作！）
# Remove-Item "$env:DEVLOG_ROOT\daily\$(Get-Date -Format 'yyyy-MM-dd').md"

# 删除测试项目目录
# Remove-Item "$env:DEVLOG_ROOT\projects\TestProject" -Recurse -Force
# Remove-Item "$env:DEVLOG_ROOT\projects\SyncTest" -Recurse -Force
# ... 其他测试项目

# 清空 inbox
# "# Inbox`n`n" | Set-Content "$env:DEVLOG_ROOT\inbox.md" -Encoding UTF8
```

---

## 测试通过标准

所有测试满足以下条件视为通过：

- [ ] 记录功能正常写入 daily log，符号分类正确
- [ ] 写入后自动 sync 到 projects/，无需手动触发
- [ ] Stats 表格自动更新，计数准确
- [ ] Reflection 自动生成，包含所有 section
- [ ] Auto-record 能解析会话文件并正确分类
- [ ] Todo 增删改查正常
- [ ] Inbox 归档按日期分发正确
- [ ] 搜索能跨日期、跨项目检索
- [ ] 周报生成包含完整统计
- [ ] Web 高亮服务器接收并归档正常
- [ ] 边界情况处理无误（空内容、重复、不存在日期等）

---

> 如有测试失败，请记录失败的功能点和错误信息，反馈给开发团队。
