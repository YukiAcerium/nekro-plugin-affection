# Nekro-Agent 深度调研报告

**调研日期**: 2026-01-29
**调研人员**: Yuki
**状态**: 进行中 - 第一阶段完成

---

## 📊 项目概览

### 核心项目: nekro-agent

**基本信息**:
- **仓库**: KroMiose/nekro-agent
- **Stars**: 670 ⭐
- **创建时间**: 2024-07-26
- **最后更新**: 2026-01-29
- **主要语言**: Python (占比最高), Shell, JavaScript, CSS, HTML, Jinja, PowerShell
- **版本**: 2.1.0
- **主页**: https://nekro.ai
- **文档**: https://doc.nekro.ai

**描述**: 集代码执行能力/高度可扩展性为一体的多人跨平台聊天机器人：沙盒驱动｜可视化｜高扩展｜多模态

**核心标签**: agent, openai, chatbot, sandbox, multiuserchat, ai, python

---

## 🏛️ 系统架构

### 核心架构设计

```
外部平台 → 适配器层 → 输入流 → 消息分发器 → 核心共享服务 → 输出流 → 适配器层 → 外部平台
```

**关键特性**:
- 面向 **输入/输出流** 设计
- 适配器（Adapter）仅负责平台消息的接收和发送
- 所有复杂业务逻辑由核心引擎自动处理

### 项目目录结构

```
nekro-agent/
├── nekro_agent/          # 核心引擎
│   ├── adapters/         # 平台适配器
│   ├── api/              # API 路由
│   ├── core/             # 核心工具和配置
│   ├── models/           # 数据库模型
│   ├── routers/          # 路由
│   ├── schemas/          # 数据模式
│   ├── services/         # 核心服务
│   ├── systems/          # 系统模块
│   └── tools/            # 工具函数
├── frontend/             # Web UI (React 18 + MUI)
├── sandbox/              # 沙盒执行环境
├── plugins/              # 插件目录
├── docs/                 # 开发文档
└── docker/               # Docker 部署配置
```

---

## 🔌 适配器平台

### 已支持的平台

1. **OneBot v11** (QQ) - `onebot_v11`
2. **Discord** - `discord`
3. **Telegram** - `telegram`
4. **Minecraft** - `minecraft`
5. **Bilibili Live** (B站直播) - `bilibili_live`
6. **WeChat** (微信，通过 WeChatPad) - `wechatpad`
7. **Email** (邮件) - `email`
8. **SSE+SDK** (Server-Sent Events) - `sse`
9. **企业微信** - `wxwork`

---

## 🧩 核心系统模块

### 1. Agent System (代理系统)
路径: `nekro_agent/systems/agent/`
- 负责 AI 代理的执行和决策

### 2. Chat System (聊天系统)
路径: `nekro_agent/systems/chat/`
- 处理群聊/私聊的上下文智能聊天

### 3. Sandbox System (沙盒系统)
路径: `nekro_agent/systems/sandbox/`
- 基于 Docker 的安全代码执行环境
- 支持 RPC 通信与真实环境交互

### 4. Plugin System (插件系统)
路径: `nekro_agent/systems/plugin/`
- 高度可扩展的插件架构
- 支持云端插件市场

### 5. Space Cleanup (空间清理)
路径: `nekro_agent/systems/space_cleanup/`
- 自动清理沙盒执行环境

### 6. Cloud System (云服务)
路径: `nekro_agent/systems/cloud/`
- 云端资源共享（插件、人设等）

### 7. Timer Service (定时任务)
路径: `nekro_agent/services/timer_service.py`
- 支持定时自触发插件与节日祝福

### 8. Mail System (邮件服务)
路径: `nekro_agent/systems/mail/`
- 邮件收发支持 (SMTP/IMAP)

---

## 📦 核心依赖

### 主要依赖 (pyproject.toml)

**框架与适配器**:
- `nonebot2[fastapi]>=2.2.1,<3.0.0` - 核心框架
- `nonebot-adapter-onebot>=2.4.2,<3.0.0` - QQ 适配器
- `nonebot-adapter-minecraft>=1.4.0,<1.5` - Minecraft 适配器

**数据库与存储**:
- `tortoise-orm==0.24` - ORM 框架
- `asyncpg>=0.30.0,<1.0.0` - PostgreSQL 异步驱动
- `psycopg2-binary>=2.9.9,<3.0.0` - PostgreSQL 驱动
- `qdrant-client>=1.15.0,<1.16.0` - 向量数据库
- `mem0ai>=0.1.79,<1.0.0` - AI 记忆系统

**AI 与 LLM**:
- `openai>=1.107.0,<1.108.0` - OpenAI API
- `tiktoken>=0.7.0,<1.0.0` - Token 计数
- `mcp>=1.7.0,<2.0.0` - Model Context Protocol

**代码执行与安全**:
- `docker>=7.1.0,<8.0.0` - Docker SDK
- `aiodocker>=0.22.2,<1.0.0` - 异步 Docker

**Web 与通信**:
- `discord-py>=2.5.2,<3.0.0` - Discord API
- `python-telegram-bot>=22.4,<23.0` - Telegram API
- `websockets>=15.0.1,<16.0.0` - WebSocket 支持
- `aiohttp>=3.11.15,<4.0.0` - 异步 HTTP

**数据处理**:
- `pillow>=10.4.0,<11.0.0` - 图像处理
- `matplotlib>=3.10.3,<4.0.0` - 图表绘制
- `pandas>=2.3.0,<3.0.0` - 数据分析
- `openpyxl>=3.1.2,<4.0.0` - Excel 处理

---

## 🎨 前端技术栈

路径: `frontend/`

**技术栈**:
- **框架**: React 18 + TypeScript
- **UI 库**: Material UI (MUI)
- **构建工具**: Vite
- **样式**: TailwindCSS + UnoCSS
- **状态管理**: React Hooks + Stores
- **国际化**: 多语言支持 (中文/英文/日文)

**主要页面**:
- `App.tsx` - 主应用
- `pages/` - 各功能页面
  - `chat-channel/` - 聊天频道
  - `cloud/` - 云端市场
  - `dashboard/` - 管理仪表板
  - `login/` - 登录
  - `plugins/` - 插件管理
  - `presets/` - 人设管理
  - `sandbox/` - 沙盒监控
  - `settings/` - 系统设置

---

## 🔧 沙盒系统

路径: `sandbox/`

**核心组件**:
- `nekro_agent_sandbox/` - 沙盒代理核心
- `pyproject.toml` - 沙盒依赖配置
- `dockerfile` - Docker 构建文件

**特点**:
- 基于 Docker 的容器化执行
- 安全隔离的执行环境
- 支持 RPC 通信
- 自动清理机制

---

## 📚 相关项目生态

### Miose 个人仓库中的相关项目

| 项目名 | Stars | 描述 |
|--------|-------|------|
| **nonebot_plugin_naturel_gpt** | 511 | NoneBot AI 聊天插件前身 |
| **AstrBot** | ⭐ 40 | 一站式 LLM 聊天机器人平台 |
| **claude-code-nexus** | 228 | Claude API 代理平台 |
| **claude-code-proxy** | - | Claude Code 到 OpenAI 代理 |
| **Miose-Draw-Guess** | 14 | WebSocket 你画我猜游戏 |
| **nekro-live-studio** | - | Live2D 虚拟形象控制 |
| **LazyCat-Scripts** | - | 个人系统脚本库 |
| **miose-toolkit** | - | 个人工具箱/轮子库 |
| **wxauto4** | - | 微信客户端自动化 |

### NekroAI 组织仓库

| 项目名 | 描述 |
|--------|------|
| **one-tracker** | AI 模型价格比较/追踪工具 |
| **nekro-vstack-template** | AI 辅助编程全栈模板 (FastAPI + React) |
| **nekro-edge-template** | Cloudflare 全栈 Web 应用模板 |
| **nekro-community** | NekroAgent 社区站云服务 |
| **nekro-portal** | 门户服务 |
| **nekro-realms** | 领域服务 |
| **nekro-endpoint** | 边缘代理服务 |
| **nekro-chat** | 聊天服务 |

### 插件生态

| 插件名 | 功能 |
|--------|------|
| **nekro-plugin-template** | 插件开发模板 |
| **nekro-plugin-webapp** | Web 应用插件 |
| **nekro-plugin-magic-draw** | AI 绘图插件 |
| **nekro-plugin-cloudmusic-search** | 网易云点歌 |
| **nekro-plugin-galchat** | GalGame 聊天插件 |
| **nekro-plugin-tongyi_wanx** | 通义万相视频生成 |
| **nekro-plugin-block** | 内容过滤插件 |
| **nekro-plugin-clone** | 克隆插件 |

---

## 🌐 生态系统服务

### 官方服务

1. **文档中心**: https://doc.nekro.ai
2. **云社区**: https://community.nekro.ai
3. **One Tracker**: https://ot.nekro.ai (AI 模型价格追踪)
4. **社区 Discord**: https://discord.gg/eMsgwFnxUB
5. **QQ 交流群**: 636925153 (1群), 679808796 (2群)

### 边缘服务

- **NekroEndpoint**: https://ep.nekro.ai (Cloudflare 镜像/代理)

---

## 📖 文档资源

### 官方文档结构

仓库: `KroMiose/nekro-agent-doc`

```
docs/
├── 01_intro/           # 介绍
├── 02_quick_start/     # 快速开始
├── 04_plugin_dev/      # 插件开发
├── 05_app_dev/         # 应用开发
├── 06_troubleshooting/ # 故障排除
└── en/                 # 英文文档
```

### 开发文档

- `Extension_Development.md` - 扩展开发指南
- `Plugin_Router_Design.md` - 插件路由设计
- `Plugin_Router_Final_Summary.md` - 插件路由最终总结

---

## 🚀 部署方式

### 一键部署脚本

```bash
# 从 GitHub
sudo -E bash -c "$(curl -fsSL https://raw.githubusercontent.com/KroMiose/nekro-agent/main/docker/install.sh)" - --with-napcat

# 从 NekroEndpoint (Cloudflare 镜像)
sudo -E bash -c "$(curl -fsSL https://ep.nekro.ai/e/KroMiose/nekro-agent/main/docker/install.sh)" - --with-napcat
```

### Docker 镜像

- **稳定版**: `kromiose/nekro-agent:latest`
- **预览版**: `kromiose/nekro-agent:preview`

---

## 🎯 核心功能特性

### ✅ 已实现功能

- [x] 多平台适配 (QQ, Discord, Telegram, Minecraft, B站, 微信, 邮件, SSE)
- [x] 智能聊天 (群聊/私聊上下文)
- [x] 自定义人设与云端市场
- [x] 沙盒执行 (Docker 容器化)
- [x] 多模态交互 (图片、文件)
- [x] 插件系统与云端插件市场
- [x] 一键部署 (docker-compose)
- [x] 热重载 (配置热更新)
- [x] 定时任务
- [x] WebUI 可视化管理
- [x] 事件通知支持
- [x] 外置思维链 (CoT) 能力
- [x] 第三方插件与 AI 生成插件

### 🔜 开发中/计划中

- 更多适配器平台
- 国际化改造
- 插件编辑器优化

---

## 💡 技术亮点

1. **沙盒驱动**: AI 生成代码在安全容器中执行
2. **插件架构**: 高度可扩展，支持云端共享
3. **原生多人场景**: 精确理解复杂群聊需求
4. **降本增效**: 拒绝无效提示词滥用
5. **自动纠错**: 深耕提示词纠错与反馈机制
6. **异步架构**: 事件驱动的高效响应

---

## 📈 演进历史

- **2024-07-26**: 项目创建
- **2025-03-08**: 文档仓库创建
- **2025-08-27**: one-tracker 项目启动
- **2025-12-27**: nekro-community 云服务启动
- **2026-01-29**: 当前版本 2.1.0, 670 ⭐

**演进路径**:
```
nonebot_plugin_naturel_gpt (2022) → nekro-agent (2024) → NekroAI 生态系统 (2025+)
```

---

## 🔗 相关链接

**官方资源**:
- GitHub: https://github.com/KroMiose/nekro-agent
- 官网: https://nekro.ai
- 文档: https://doc.nekro.ai
- 社区: https://community.nekro.ai
- Discord: https://discord.gg/eMsgwFnxUB

**镜像与代理**:
- NekroEndpoint: https://ep.nekro.ai
- One Tracker: https://ot.nekro.ai

**社区贡献**:
- QQ 1群: 636925153
- QQ 2群: 679808796

---

## 🔧 核心实现细节

### 1. 配置系统 (Core Config)

**配置文件**: `nekro_agent/core/config.py`

```python
class CoreConfig(ConfigBase):
    """核心配置"""
    ENABLE_NEKRO_CLOUD: bool = Field(default=True, title="启用 NekroAI 云服务")
    NEKRO_CLOUD_API_KEY: str = Field(default="", title="NekroAI 云服务 API Key")

class ModelConfigGroup(ConfigBase):
    """模型配置组"""
    GROUP_NAME: str = Field(default="", title="模型组名称")
    CHAT_MODEL: str = Field(default="", title="聊天模型名称")
    MODEL_TYPE: Literal["chat", "embedding", "draw"] = Field(default="chat")
    ENABLE_VISION: bool = Field(default=False, title="启用视觉功能")
    ENABLE_COT: bool = Field(default=False, title="启用外置思维链")
```

### 2. 适配器系统 (Adapter System)

**适配器基类**: `nekro_agent/adapters/interface/base.py`

```python
class BaseAdapter(ABC, Generic[TConfig]):
    """适配器基类"""
    
    @property
    @abstractmethod
    def key(self) -> str:
        """适配器唯一标识"""
        raise NotImplementedError

    @property
    @abstractmethod
    def metadata(self) -> AdapterMetadata:
        """适配器元数据"""
        raise NotImplementedError
```

### 3. 数据库模型 (Database Models)

**核心模型**: DBUser, DBChatChannel, DBChatMessage, DBExecCode, DBPluginData, DBPreset

```python
class DBUser(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=128)
    adapter_key = fields.CharField(max_length=64)
    platform_userid = fields.CharField(max_length=256)
    perm_level = fields.IntField()
    ban_until = fields.DatetimeField(null=True)
    ext_data = fields.JSONField(default=dict)
```

### 4. API 路由 (API Routes)

| 路由文件 | 前缀 | 功能 |
|---------|------|------|
| `adapters.py` | `/adapters` | 适配器管理 |
| `plugins.py` | `/plugins` | 插件管理 |
| `sandbox.py` | `/sandbox` | 沙盒日志 |
| `presets.py` | `/presets` | 人设管理 |

### 5. 插件系统 (Plugin System)

**插件收集器**: `nekro_agent/services/plugin/collector.py`

- 扫描插件目录: `BUILTIN_PLUGIN_DIR`, `WORKDIR_PLUGIN_DIR`, `PACKAGES_DIR`
- 导入插件模块并注册钩子
- 支持云端插件安装/卸载

### 6. 沙盒系统 (Sandbox System)

**Docker 工具**: `nekro_agent/tools/docker_util.py`

```python
async def get_docker_client() -> aiodocker.Docker:
    return aiodocker.Docker()

async def restart_self(timeout: int = 30) -> bool:
    container = await get_self_container()
    asyncio.create_task(container.restart(timeout=timeout))
    return True
```

### 7. 云服务 API (Cloud API)

```python
# 云端插件 API
from nekro_agent.systems.cloud.api.plugin import get_plugin_detail, install_plugin

# 云端人设 API  
from nekro_agent.systems.cloud.api.preset import get_preset, create_preset
```

---

## 🛡️ 安全机制

- **消息校验**: 检测伪造消息、防止注入攻击
- **权限系统**: Role.Admin / Role.User 权限等级
- **沙盒隔离**: Docker 容器化、网络隔离
- **文件系统安全**: 路径穿越检测、访问控制

---

## 📊 数据流架构

```
用户消息 → 适配器接收 → 消息校验 → 插件处理 → Agent 决策 → 代码生成 → 沙盒执行 → 结果返回 → 消息发送
```

---

## 🔄 事件驱动架构

- **消息事件**: collect_message, parse_message, format_message, send_message
- **通知事件**: 群通知、好友通知、系统通知
- **定时任务**: 节日祝福、定时触发、空间清理

---

## 🎨 WebUI 架构

**前端技术栈**: React 18 + TypeScript + Material UI + Vite

**主要页面**: Dashboard, Chat Channel, Plugins, Presets, Sandbox, Settings, Logs, Cloud

---

## 🔗 项目依赖关系

```
nekro-agent
├── nonebot2 (核心框架)
├── nonebot-adapter-onebot (QQ 适配器)
├── tortoise-orm (数据库 ORM)
├── qdrant-client (向量数据库)
├── mem0ai (记忆系统)
├── docker (容器管理)
├── openai (AI API)
└── mcp (Model Context Protocol)
```

---

## 📈 性能优化

- **异步架构**: asyncio, aiodocker, asyncpg
- **缓存策略**: 配置缓存、插件元数据缓存
- **资源管理**: 沙盒空间自动清理、连接池管理

---

## 🎯 待深入调研

### 第二阶段调研任务

1. [ ] **Agent 系统深入分析** - 提示词模板、代码生成、错误处理
2. [ ] **插件系统深入分析** - 钩子系统、沙盒方法注册
3. [ ] **沙盒系统深入分析** - Docker 镜像、RPC 协议
4. [ ] **云服务系统深入分析** - 同步机制、身份验证
5. [ ] **前端 WebUI 深入分析** - 状态管理、API 集成
6. [ ] **数据库架构深入分析** - 表结构、索引优化
7. [ ] **部署架构深入分析** - Docker Compose、网络拓扑
8. [ ] **安全审计** - 输入验证、权限控制、沙盒策略
9. [ ] **生态整合分析** - 与 OneAPI/Dify/Cloudflare 集成
10. [ ] **性能基准测试** - 并发能力、内存占用

---

## 📚 参考资源

- **文档中心**: https://doc.nekro.ai
- **GitHub**: https://github.com/KroMiose/nekro-agent
- **官网**: https://nekro.ai
- **Discord**: https://discord.gg/eMsgwFnxUB
- **QQ 群**: 636925153 / 679808796

---

*报告更新日期: 2026-01-29*
*调研者: Yuki*
*版本: 2.0 (深度调研版)*
