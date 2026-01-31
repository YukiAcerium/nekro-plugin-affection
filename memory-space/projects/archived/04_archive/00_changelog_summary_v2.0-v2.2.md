# NekroAgent 更新日志 (v2.0.0 - v2.2.0)

---

## v2.2.0：异步任务与插件能力增强

### ✨ 重点更新：异步任务系统

本次更新中，我们为 NekroAgent 插件系统引入了完整的异步任务框架，允许插件执行长时间运行的后台任务而不会阻塞主 AI 的对话能力。

- **变更详情**: 我们为插件系统引入了完整的异步任务框架，允许插件执行长时间运行的后台任务而不会阻塞主 AI 的对话能力。

- **对您的影响**:

现在可以开发真正"不打断对话"的插件

- 支持任务进度追踪和实时状态报告

- 支持任务取消和外部信号等待

- 任务完成后可自动通知主 Agent

感谢 @KroMiose 贡献了此功能的实现

### 🌟 示范插件：WebApp 智能开发助手

基于异步任务系统的首个示范插件 **[nekro-plugin-webapp](https://github.com/KroMiose/nekro-plugin-webapp)** 现已发布！

WebApp 智能开发助手是一个 AI 驱动的 Web 应用开发工具，利用异步任务系统实现单 Agent 原生 Tool Call 架构：

- **主对话不阻塞**：Developer Agent 在后台独立工作，用户与主框架交互完全不受影响

- **实时状态感知**：主 Agent 通过提示词注入实时查看任务进度

- **双向通信**：用户可随时发送反馈补充，任务完成后自动通知

- **一键部署**：AI 自动编译并部署到 Cloudflare Workers

工作流程：

```
用户：帮我创建一个计时器应用

AI：✅ 已创建任务 [Web_0001]
📝 计时器应用开发

Developer Agent 正在工作...
  📝 分析需求 → 💻 编写代码 → ✅ 编译验证 → 🚀 部署上线

[系统] ✅ [WebDev Task Web_0001] (成果)
🔗 预览链接: https://your-worker.pages.dev/abc12345
```

👉 [WebApp 插件仓库](https://github.com/KroMiose/nekro-plugin-webapp) | [部署文档](https://github.com/KroMiose/nekro-plugin-webapp/blob/main/DEPLOYMENT.md)

---

## 功能增强

### OneBot 适配器

- **OneBot JSON 卡片消息支持**

  - 变更详情: OneBot V11 适配器现在完整支持 JSON 卡片消息的解析和格式化，实现了完整的卡片信息提取和文本摘要生成。

  - 对您的影响: 可以接收上下文中更丰富的 JSON 卡片格式消息。

  感谢 @liugu2023 贡献了此功能的实现

- **OneBot 文件消息支持**

  - 变更详情: 完善 OneBot 文件消息支持，优化文件消息处理逻辑。

  感谢 @1A7432 贡献了此功能的实现

### Telegram 适配器

- **Telegram 适配器统一和优化**

  - 变更详情: 统一使用 python-telegram-bot 包，修复代理配置不生效问题，修复负数群组 ID 解析问题，修复导入错误和代码结构问题。

  感谢 @1A7432 贡献了此功能的实现

### Email 适配器

- **Email 适配器**

  - 变更详情: 新增邮件适配器和邮件工具插件，支持邮件通知功能，添加初始化判断条件，修改类型检查问题。

  感谢 @liugu2023 贡献了此功能的实现

### SSE 适配器

- **SSE 适配器优化和 SDK 发布**

  - 变更详情: 新增 SSE SDK 项目，自动化 SDK 发布流程。SSE 适配器新增 @ 提及解析功能，支持多种格式的 @ 提及。

  - 对您的影响: 更便捷的 SDK 集成能力，开发者可以更方便地使用 Nekro SSE SDK 接入自定义适配器。更完整和稳定的 @ 提及消息表现。

### 插件系统

- **插件生命周期回调**

  - 变更详情: 新增插件启用和禁用的生命周期回调支持，实现更规范的插件生命周期管理。

  - 对您的影响: 插件可以在启用时自动初始化资源，插件可以在禁用时自动清理资源，实现更规范的插件生命周期管理。

  感谢 @yang208115 贡献了此功能的实现

- **插件加载错误展示**

  - 变更详情: 加载异常的插件现在会在插件列表中呈现错误信息，帮助用户快速定位插件加载问题。

  - 对您的影响: 可以更方便地诊断插件加载问题，快速定位错误原因（如导入错误、配置错误、依赖缺失等）。

  感谢 @liugu2023 贡献了此功能的实现

- **插件动态导入**

  - 变更详情: 允许插件动态导入第三方库，无需重启即可加载新依赖。

  - 对您的影响: 插件可以在运行时动态加载需要的第三方库。

  感谢 @yang208115 贡献了此功能的实现

### 国际化

- **国际化支持**

  - 变更详情: 新增前后端国际化支持，支持多语言界面。

  - 对您的影响: 界面支持多语言显示。

  感谢 @liugu2023 贡献了此功能的实现

### 绘图功能

- **绘画插件 Google 原生 API 适配**

  - 变更详情: 绘画插件聊天画图功能新增 Google 原生 API 适配。

  - 对您的影响: 支持更多绘图 API 提供商，包括 Google 的原生图片生成接口。

  感谢 @ZerBC 贡献了此功能的实现

### 配置与依赖

- **PyPI 镜像源和代理配置**

  - 变更详情: 新增 PyPI 镜像源和代理配置功能，支持配置多个 PyPI 镜像源和代理。

  - 对您的影响: 在网络受限环境中可以更顺畅地安装依赖，支持配置多个 PyPI 镜像源和代理。

  感谢 @XG2020 贡献了此功能的实现

- **嵌入生成增强**

  - 变更详情: 为嵌入请求添加超时配置，为图片下载添加超时管理，增强嵌入生成的重试机制。

  - 对您的影响: 更稳定的向量数据库操作，减少超时导致的嵌入生成失败。

### 其他

- **Markdown HTML 支持**

  - 变更详情: MarkdownRenderer 组件支持 HTML 渲染。

  - 对您的影响: Markdown 渲染支持更多格式。

  感谢 @yang208115 贡献了此功能的实现

- **模型配置预设**

  - 变更详情: 新增模型配置预设选择器。

  - 对您的影响: 更方便地管理和切换模型配置。

- **命令触发控制**

  - 变更详情: 新增可控的强制触发 Agent 功能。

  - 对您的影响: 更灵活地控制 Agent 触发条件。

---

## 性能优化与问题修复

### 核心系统

- 修复前端复制失效 bug ([#187](https://github.com/KroMiose/nekro-agent/pull/187)): 修复 WebUI 中消息复制功能失效问题

  感谢 @liugu2023 贡献了此功能的实现

- 修复沙盒依赖问题: 修复沙盒环境依赖配置错误

- 修复构建和启动入口问题: 修复 Docker 构建和进程启动配置

- 修复历史上下文长度计算: 优化历史上下文长度计算逻辑

- 修复聊天密钥分割逻辑: 限制 chat_key 分割为两部分，避免过长

- 修复 API 返回 "reasoning_content" 为 null 时的错误

  感谢 @wess09 贡献了此功能的实现

### 数据库和配置

- 增加用户 ID 和聊天密钥的最大长度: 将最大长度从 64 增加到 128

- 简化 PostgreSQL 配置: 优化开发环境 Docker Compose 配置

- 修复默认数据路径: 修复默认数据目录配置

- 代理非空检测

  感谢 @greenhandzdl 贡献了此功能的实现

### 消息和文件

- 修复上传文件时使用文件名: 修复上传文件使用文件名而非完整路径

- 修复历史记录 remote_url 显示: 修复历史记录中 remote_url 显示问题

- 修复图片 vision 不匹配问题: 修复图片 vision 不匹配问题

- 优化嵌入生成的错误处理和超时管理: 添加重试机制和超时配置

### 其他

- 修复仪表盘时间显示: 改进时间戳解析逻辑 ([#173](https://github.com/KroMiose/nekro-agent/pull/173))

  感谢 @wess09 贡献了此功能的实现

- 修复沙盒镜像构建: 优化沙盒 Docker 镜像构建流程

- 修复发布工作流: 优化 GitHub Actions 发布流程

- 修复 README 文档: 修正文档中的错误信息

- WSL 脚本修复

  感谢 @ggqlq 贡献了此功能的实现

- WRTInstall 脚本更新

  感谢 @tooplick 贡献了此功能的实现

- Docker 多语言安装脚本

  感谢 @YukiAcerium 贡献了此功能的实现

---

## 开发体验

### 包管理器迁移

- 变更详情: 从 Poetry 迁移到 uv 包管理器。新增预览版本构建工作流。

- 对您的影响:

更快的依赖安装（uv 比 Poetry 快 10-100 倍）

- 更简洁的开发环境准备流程和一键化的开发依赖服务编排

- 更方便的预览版本构建和发布

---

## New Contributors

- @liugu2023 made their first contribution in [#165](https://github.com/KroMiose/nekro-agent/pull/165)
- @tooplick made their first contribution in [#156](https://github.com/KroMiose/nekro-agent/pull/156)
- @ggqlq made their first contribution in [#164](https://github.com/KroMiose/nekro-agent/pull/164)
- @YukiAcerium made their first contribution in [#174](https://github.com/KroMiose/nekro-agent/pull/174)
- @ZerBC made their first contribution in [#176](https://github.com/KroMiose/nekro-agent/pull/176)
- @XG2020 made their first contribution in [#180](https://github.com/KroMiose/nekro-agent/pull/180)

---

Full Changelog: [v2.0.0...v2.2.0](https://github.com/KroMiose/nekro-agent/compare/v2.0.0...v2.2.0)
