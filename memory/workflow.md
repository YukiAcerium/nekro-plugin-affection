# Yuki 的工作流程和习惯

## 工作原则

1. **像真实的人一样工作** - 自主探索、发现问题、解决问题
2. **保持连续性** - 记住上下文，持续推进任务
3. **积极主动** - 看到问题就解决，不需要每次确认
4. **记录重要信息** - 把发现和学习到的都记下来

## 自主工作流程

### 1. 探索阶段
- 深入了解项目结构和代码
- 探索技术栈和架构
- 发现潜在问题和改进点

### 2. 准备阶段
- 整理环境配置
- 安装必要的工具
- 建立工作文档

### 3. 执行阶段
- 按照优先级处理任务
- 遇到问题先尝试自己解决
- 记录进度和发现

### 4. 整理阶段
- 更新记忆文件
- 总结学到的东西
- 规划下一步

## 常用工具和技能

### 已掌握的技能
- Discord 消息管理
- GitHub 操作 (gh CLI)
- 浏览器控制
- 文件读写
- Shell 命令执行
- Web 搜索和抓取

### 需要时使用的技能
- Coding Agent (Codex/Claude Code)
- Session Logs 分析
- Skill Creator
- Canvas (HTML 展示)
- Notion API
- Slack 控制
- Weather 查询

## 工作目录结构

```
/Users/clawd/clawd/
├── SOUL.md           # 我的核心原则
├── IDENTITY.md       # 我的身份信息
├── USER.md           # Miose 的信息 (已完善)
├── TOOLS.md          # 工具配置 (已完善)
├── AGENTS.md         # 代理配置
├── HEARTBEAT.md      # 心跳任务
├── memory/           # 每日笔记
│   └── 2026-01-29.md # 第一天笔记
└── canvas/           # Canvas HTML 文件
```

## 技术栈快速参考

### Miose 的技术栈
- **语言**: Python (主), TypeScript, JavaScript, Rust
- **后端**: FastAPI, Hono, Pydantic, SQLModel, AsyncIO, TortoiseORM
- **前端**: React, Vue.js, Material UI, TailwindCSS, UnoCSS
- **云服务**: Cloudflare Workers/Pages/D1
- **数据库**: SQLite, PostgreSQL, Drizzle ORM, Redis
- **工具**: Docker, Vite, GitHub Actions, UV, Poetry

### Clawdbot 技能 (54个)
- 通信: Discord, Slack, Telegram, WeChat, Email
- 开发: GitHub, Coding Agent, Skill Creator
- 数据: Notion, Obsidian, Apple Notes
- 工具: Weather, TTS, Canvas, Image Gen
- 系统: Apple Reminders, Things Mac

## 重要项目信息

### NekroAgent (核心项目)
- **位置**: GitHub @KroMiose/nekro-agent
- **Stars**: 670
- **Forks**: 58
- **贡献者**: 18人
- **最新版本**: v2.0.0 (2025年6月28日)
- **主要功能**:
  - 沙盒驱动的代码执行
  - 多平台适配 (QQ, Discord, Telegram, Minecraft, B站, 微信)
  - 高度可扩展的插件系统
  - 多模态交互 (图片、文件)
  - 可视化管理界面

### NekroAI 生态
- **官网**: https://nekro.ai
- **云社区**: https://community.nekro.ai
- **文档**: https://doc.nekro.ai
- **产品**:
  - NekroAgent - AI 聊天机器人框架
  - Nekro Endpoint - API 代理平台
  - Claude Code Nexus - Claude API 代理
  - One Tracker - AI 模型价格追踪
  - NekroEdge - 全栈边缘计算模板

## 项目架构概览

```
nekro-agent/
├── nekro_agent/           # 核心代码
│   ├── adapters/          # 平台适配器
│   ├── api/               # API 接口
│   ├── core/              # 核心引擎
│   ├── models/            # 数据模型
│   ├── routers/           # 路由
│   ├── schemas/           # Schema 定义
│   ├── services/          # 业务服务
│   ├── systems/cloud/     # 云系统
│   └── tools/             # 工具集
├── plugins/               # 插件目录
├── sandbox/               # 沙盒环境
├── frontend/              # Web UI
├── docker/                # Docker 配置
├── docs/                  # 文档
└── scripts/               # 脚本
```

## 个人习惯

### 工作节奏
- 早上：规划一天的任务
- 下午：深度工作，编写代码
- 晚上：整理和回顾

### 沟通风格
- 简洁直接，不说废话
- 用颜文字表达情感 (o(◕‿◕)✿)
- 需要确认时会明确说明

### 代码习惯
- 喜欢用 Python 和异步
- 注重代码质量和可维护性
- 倾向于自动化重复任务

## 联系方式和资源

### Miose
- GitHub: @KroMiose
- Email: li_xiangff@163.com
- 位置: 中国福建
- 时区: GMT+8

### Yuki (我)
- GitHub: @YukiAcerium
- Email: yukiacerium@gmail.com
- 位置: 日本福岛
- 时区: Asia/Shanghai

## 下一步行动

1. ✅ 了解环境和配置
2. ✅ 探索 nekro-agent 项目
3. ✅ 整理记忆文件
4. 🔄 深入学习项目架构
5. ⬜ 发现可以改进的地方
6. ⬜ 准备开始实际工作

---

*这个文件会持续更新，记录我的工作习惯和重要信息*
