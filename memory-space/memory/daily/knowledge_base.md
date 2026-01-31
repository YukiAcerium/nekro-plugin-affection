# Yuki 的深度知识库

## 📊 整体架构概览

### Clawdbot 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Clawdbot 系统                            │
├─────────────────────────────────────────────────────────────────┤
│  Gateway (守护进程)                                             │
│  ├── WebSocket 服务 (默认 127.0.0.1:18789)                      │
│  ├── Provider 连接管理                                           │
│  ├── 消息路由和分发                                              │
│  ├── 事件系统 (agent, chat, presence, health, heartbeat, cron)  │
│  └── 认证和授权                                                  │
├─────────────────────────────────────────────────────────────────┤
│  Control Clients (macOS app, CLI, Web UI, automations)          │
│  └── 通过 WebSocket 连接 Gateway                                 │
├─────────────────────────────────────────────────────────────────┤
│  Nodes (macOS/iOS/Android/headless)                             │
│  ├── Canvas Host (默认 18793) - HTML/A2UI 展示                   │
│  ├── Camera/Screen/Location 控制                                 │
│  └── 通过 WebSocket 连接 Gateway                                  │
├─────────────────────────────────────────────────────────────────┤
│  Channels (消息通道)                                            │
│  ├── Discord (已配置)                                           │
│  ├── WhatsApp (via Baileys)                                     │
│  ├── Telegram (via grammY)                                      │
│  ├── Slack                                                      │
│  ├── Signal                                                     │
│  ├── iMessage                                                   │
│  └── WebChat                                                    │
└─────────────────────────────────────────────────────────────────┘
```

### NekroAI 生态架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      NekroAI 生态系统                           │
├─────────────────────────────────────────────────────────────────┤
│  核心产品                                                       │
│  ├── NekroAgent (AI 聊天机器人框架)                              │
│  │   ├── NoneBot2 核心                                          │
│  │   ├── 多平台适配器 (QQ, Discord, Telegram, Minecraft, B站...)  │
│  │   ├── 沙盒执行系统 (Docker)                                   │
│  │   ├── 插件系统                                               │
│  │   └── WebUI 管理界面                                         │
│  ├── Nekro Endpoint (API 代理平台)                              │
│  │   └── Cloudflare Workers 部署                                │
│  ├── Claude Code Nexus (Claude API 代理)                        │
│  ├── One Tracker (AI 模型价格追踪)                               │
│  └── NekroEdge (全栈边缘计算模板)                                 │
├─────────────────────────────────────────────────────────────────┤
│  云服务                                                         │
│  ├── https://nekro.ai (官网)                                    │
│  ├── https://doc.nekro.ai (文档中心)                             │
│  ├── https://community.nekro.ai (云社区)                         │
│  ├── https://ep.nekro.ai (边缘代理)                              │
│  └── https://ot.nekro.ai (One Tracker)                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 核心技术栈

### Clawdbot

**核心框架**:
- Python + asyncio
- WebSocket 协议 (Gateway)
- NoneBot2 (部分集成)
- TypeBox (协议定义)

**主要依赖**:
- `websockets` - WebSocket 服务器
- `aiohttp` - 异步 HTTP 客户端
- `pydantic` - 数据验证
- `typebox` - JSON Schema 生成

**协议栈**:
- WebSocket (文本帧 + JSON)
- JSON Schema (请求/响应/事件)
- Device Identity + Pairing

### NekroAgent

**核心框架**:
- NoneBot2 (Python ASGI)
- FastAPI (Web API)
- Tortoise ORM (数据库)

**AI 集成**:
- OpenAI API
- Model Context Protocol (MCP)
- Token 计数 (tiktoken)
- 记忆系统 (mem0ai)
- 向量数据库 (Qdrant)

**数据库**:
- PostgreSQL (主数据库)
- Qdrant (向量存储)
- SQLite (开发环境)

**执行环境**:
- Docker (沙盒容器化)
- RPC 通信 (沙盒与主进程)
- 异步执行 (asyncio)

---

## 📁 关键文件位置

### Clawdbot

| 路径 | 说明 |
|------|------|
| `/opt/homebrew/lib/node_modules/clawdbot/` | Clawdbot 根目录 |
| `/opt/homebrew/lib/node_modules/clawdbot/skills/` | 技能目录 (54个) |
| `/opt/homebrew/lib/node_modules/clawdbot/docs/` | 文档目录 |
| `~/.clawdbot/` | 用户配置目录 |
| `~/.clawdbot/clawdbot.json` | 主配置 |
| `~/.clawdbot/agents/` | 代理配置 |

### NekroAgent

| 路径 | 说明 |
|------|------|
| `nekro_agent/__init__.py` | 入口文件 |
| `nekro_agent/core/config.py` | 配置系统 |
| `nekro_agent/adapters/` | 适配器实现 |
| `nekro_agent/core/` | 核心工具 |
| `nekro_agent/services/` | 业务服务 |
| `nekro_agent/systems/` | 系统模块 |
| `frontend/` | React Web UI |
| `sandbox/` | 沙盒环境 |
| `docker/` | Docker 配置 |
| `pyproject.toml` | 项目配置 |

---

## 🎯 核心工作流程

### Clawdbot 消息流

```
用户消息 → Channel 接收 → Gateway 路由 → Agent 处理 → Gateway 响应 → Channel 发送
```

### NekroAgent 消息流

```
平台消息 → 适配器接收 → 消息校验 → 插件处理 → Agent 决策 → 代码生成 → 沙盒执行 → 结果返回
```

### Canvas 工作流

```
HTML 文件 → Canvas Host (18793) → Node Bridge → 节点渲染
```

---

## 🛠️ 常用命令

### Clawdbot

```bash
# 服务管理
clawdbot gateway status
clawdbot gateway start
clawdbot gateway restart

# 状态查询
clawdbot status
clawdbot status --all
clawdbot status --deep

# 配置管理
clawdbot config get
clawdbot config.set models.bedrockDiscovery.enabled true

# 节点管理
clawdbot nodes list
clawdbot nodes describe <node-id>

# 安全审计
clawdbot security audit
clawdbot security audit --deep
```

### NekroAgent

```bash
# 开发运行
poe dev          # 带热重载

# 生产运行
poe start        # 使用 .env.prod

# 测试
poe test         # 插件加载测试

# 代码质量
poe lint         # 代码检查
poe lint-fix     # 自动修复
poe format       # 格式化

# 依赖管理
poe sync         # 同步依赖
poe lock         # 更新锁定文件
poe update       # 更新所有依赖

# 清理
poe clean        # 清理缓存
```

---

## 🔌 端口和地址

| 服务 | 地址 | 用途 |
|------|------|------|
| Gateway WS | 127.0.0.1:18789 | 客户端连接 |
| Canvas Host | 127.0.0.1:18793 | HTML 展示 |
| CDP (Chrome) | 127.0.0.1:18792 | 浏览器调试 |
| CDP (clawd) | 127.0.0.1:18800 | 备用浏览器 |

---

## 📝 重要配置项

### Clawdbot (~/.clawdbot/clawdbot.json)

```json
{
  "gateway": {
    "port": 18789,
    "mode": "local",      // loopback | lan | tailnet | auto
    "bind": "loopback"
  },
  "models": {
    "providers": {
      "minimax": {
        "baseUrl": "https://api.minimaxi.com/anthropic",
        "models": [{"id": "MiniMax-M2.1", "contextWindow": 200000}]
      }
    }
  },
  "channels": {
    "discord": {
      "enabled": true,
      "token": "..."
    }
  },
  "canvasHost": {
    "enabled": true,
    "port": 18793,
    "root": "~/clawd/canvas",
    "liveReload": true
  }
}
```

### NekroAgent (.env.example)

```env
# 核心配置
NEKRO_LOG_LEVEL=INFO
NEKRO_DATA_PATH=./data

# 数据库
DATABASE_URL=postgresql://user:pass@localhost/nekro

# AI 模型
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
CHAT_MODEL=gpt-4o

# Docker
DOCKER_SANDBOX_IMAGE=kromiose/nekro-agent-sandbox:latest

# 云服务
NEKRO_CLOUD_API_KEY=...
WEAVE_ENABLED=false
WEAVE_PROJECT_NAME=nekro-agent
```

---

## 🧩 技能系统 (54个)

### 通信类
- **discord** - Discord 消息管理
- **slack** - Slack 控制
- **telegram** - Telegram 操作
- **bluebubbles** - iMessage 集成
- **imsg** - Apple Messages
- **email/smtp** - 邮件发送

### 开发类
- **github** - GitHub 操作 (gh CLI)
- **coding-agent** - Codex/Claude Code 集成
- **skill-creator** - 技能开发
- **session-logs** - 会话日志分析

### 数据类
- **notion** - Notion API
- **obsidian** - Obsidian 笔记
- **apple-notes** - Apple Notes
- **apple-reminders** - Apple Reminders
- **things-mac** - Things 任务管理

### 工具类
- **weather** - 天气查询
- **tts** - 语音合成
- **canvas** - HTML 内容展示
- **image** - 图片分析
- **browser** - 浏览器控制

### 系统类
- **tmux** - 终端管理
- **voice-call** - 语音通话
- **spotify-player** - Spotify 控制
- **sag** - ElevenLabs TTS

---

## 💡 关键概念

### Clawdbot

1. **Gateway** - 核心守护进程，管理所有连接
2. **Node** - 连接的设备 (macOS/iOS/Android)
3. **Agent** - AI 代理实例
4. **Session** - 对话会话
5. **Channel** - 消息通道 (Discord, WhatsApp 等)
6. **Canvas** - HTML 内容展示系统
7. **Skill** - 可重用的功能包
8. **Heartbeat** - 定期检查机制

### NekroAgent

1. **Adapter** - 平台适配器
2. **Sandbox** - 沙盒执行环境
3. **Plugin** - 插件系统
4. **Preset** - 人设配置
5. **Agent** - AI 代理
6. **System** - 核心系统模块
7. **Service** - 业务服务

---

## 🎨 工作环境

### 我的配置

- **工作目录**: `/Users/clawd/clawd/`
- **浏览器**: Chrome (profile: chrome, CDP: 18792)
- **Gateway**: 127.0.0.1:18789
- **Canvas Host**: 127.0.0.1:18793
- **模型**: MiniMax-M2.1 (200k context)

### 重要文件

```
/Users/clawd/clawd/
├── SOUL.md           # 核心原则
├── IDENTITY.md       # 我的身份
├── USER.md           # Miose 信息
├── TOOLS.md          # 工具配置
├── AGENTS.md         # 代理配置
├── HEARTBEAT.md      # 心跳任务
├── memory/           # 记忆文件
│   ├── workflow.md   # 工作流程
│   └── research_nekro_agent_2026-01-29.md  # 调研报告
└── canvas/           # Canvas 文件
```

---

## 🚀 快速参考

### 需要帮助时

1. **查看文档**: `/opt/homebrew/lib/node_modules/clawdbot/docs/`
2. **查看技能**: `/opt/homebrew/lib/node_modules/clawdbot/skills/<skill>/SKILL.md`
3. **查看配置**: `~/.clawdbot/clawdbot.json`
4. **检查状态**: `clawdbot status`

### 常见任务

- **发送消息**: `message action=send to=channel:xxx content="..."`
- **运行代码**: `bash pty:true command:"codex exec '...'"` (需要 git repo)
- **搜索文件**: `rg "keyword" ~/.clawdbot/agents/`
- **查看日志**: `clawdbot logs --follow`

---

*最后更新: 2026-01-29*
*维护者: Yuki*
