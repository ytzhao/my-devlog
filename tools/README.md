# Web Highlight Extension + Server

一套自用的网页高亮 → Markdown + 截图 → my-devlog 联动工具。

## 架构

```
┌─────────────────────┐      HTTP POST       ┌──────────────────────────┐
│  Browser Extension  │  ──────────────────► │  localhost:3721 (Python) │
│  (Chrome/Edge/Firefox)                     │  web_highlight_server.py │
└─────────────────────┘                      └──────────────────────────┘
                                                     │
                              ┌────────────────────┼────────────────────┐
                              ▼                    ▼                    ▼
                        assets/web-highlights   daily/YYYY-MM-DD.md   (screenshot)
                              │
                              └── YYYY-MM-DD/
                                  ├── page-title-HH-MM-SS.md
                                  └── page-title-HH-MM-SS.png
```

## 快速开始

### 1. 启动服务端

双击运行 `start-server.bat`，或在 PowerShell 中：

```powershell
cd D:\Projects\my-devlog
python tools\web_highlight_server.py
```

服务默认运行在 `http://localhost:3721`。

### 2. 安装浏览器扩展

**Chrome / Edge：**
1. 打开 `chrome://extensions/`（或 `edge://extensions/`）
2. 开启右上角「开发者模式」
3. 点击「加载已解压的扩展程序」
4. 选择 `D:\Projects\my-devlog\web-highlight-ext` 文件夹

**Firefox（如需）：**
- 需要额外打包为 `.zip` 后使用 `about:debugging` 加载临时扩展，或修改 manifest 为 V2。

### 3. 使用

1. 在任意网页上**选中文字**
2. 选区下方会出现浮动面板
3. 可输入 `#tag` 和 `Note`
4. 点击 **Save** → 自动完成：
   - 截取当前标签页截图
   - 生成 Markdown 归档到 `assets/web-highlights/YYYY-MM-DD/`
   - 追加一条记录到 `daily/YYYY-MM-DD.md` 的 Interstitial Log 中

## 文件说明

| 文件 | 作用 |
|------|------|
| `web_highlight_server.py` | 本地 HTTP 服务，接收扩展数据、写文件 |
| `start-server.bat` | Windows 一键启动脚本 |
| `web-highlight-ext/manifest.json` | 扩展清单 |
| `web-highlight-ext/content.js` | 内容脚本：选中文本检测 + 浮动面板 |
| `web-highlight-ext/background.js` | 后台脚本：截图 + HTTP 发送 |
| `web-highlight-ext/styles.css` | 浮动面板样式 |

## 联动格式

Daily log 中自动追加：

```markdown
[14:32] - Web: 五彩竞品调研报告 @web
```

Markdown 归档示例（`assets/web-highlights/2026-05-12/report-14-32-10.md`）：

```markdown
---
title: 五彩竞品调研报告
url: https://...
date: 2026-05-12T14:32:10
tags: [web-highlight, web]
---

## Highlight

> "网页划线高亮批注工具的市场调研..."

## Note

_(none)_

## Source

- **URL**: [https://...](https://...)
- **Saved at**: 2026-05-12 14:32

## Screenshot

![screenshot](report-14-32-10.png)
```

## 自定义

### 修改端口

同时修改两处：
1. `web_highlight_server.py` 顶部的 `PORT = 3721`
2. `content.js` 和 `background.js` 顶部的 `const SERVER = 'http://localhost:3721'`

### 修改 daily log symbol

在 `web_highlight_server.py` 中搜索 `symbols['learning']`，改为其他 symbol：
- `symbols['note']` → `·`
- `symbols['idea']` → `!`

### 忽略截图资产（Git）

`assets/web-highlights/` 下的图片可能很大，建议在 `.gitignore` 中加入：

```gitignore
assets/web-highlights/
```

## Troubleshooting

| 问题 | 解决 |
|------|------|
| ❌ Server offline | 确认 `python tools/web_highlight_server.py` 已运行 |
| 扩展无法加载 | 确认 `icons/` 目录下有三个 PNG 图标文件（可用任意图片代替） |
| CORS 错误 | 服务端已处理 CORS，检查端口是否一致 |
| 截图失败 | `activeTab` 权限只在当前标签页有效，确保点击 Save 时没有切换标签 |
