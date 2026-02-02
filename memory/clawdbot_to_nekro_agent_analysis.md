# Clawdbot 能力解析与 Nekro-Agent 插件复刻方案

> **分析日期**: 2026-02-02
> **分析目标**: 全面解析 Clawdbot 当前能力，输出 nekro-agent 插件复刻方案

---

## 一、Clawdbot 核心能力总览

### 1.1 能力分类框架

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Clawdbot 能力矩阵                                │
├─────────────────────────────────────────────────────────────────────────┤
│  📱 消息通信   │  💾 数据管理   │  🛠️ 开发工具   │  📊 生产力工具        │
│  ├─ Discord   │  ├─ 文件系统   │  ├─ GitHub     │  ├─ Gmail/Calendar    │
│  ├─ Slack     │  ├─ Notion     │  ├─ Shell/Exec │  ├─ Sheets/Docs       │
│  ├─ WhatsApp  │  ├─ Obsidian   │  ├─ CI/CD      │  ├─ Session Logs      │
│  ├─ Telegram  │  ├─ Apple Notes│  ├─ Web Search │  ├─ Memory System     │
│  └─ iMessage  │  └─ 1Password  │  └─ Browser    │  └─ Weather           │
├─────────────────────────────────────────────────────────────────────────┤
│  🎨 媒体 AI      │  🔧 系统集成     │  🎯 核心引擎                        │
│  ├─ TTS 语音     │  ├─ 摄像头       │  ├─ 多模型支持 (OpenAI/Claude/MiniMax)│
│  ├─ 图片生成     │  ├─ Home Assistant│├─ 插件系统 (Skill)                  │
│  ├─ 语音识别     │  ├─ Cron 定时    │  ├─ 存储系统 (KV + 文件)             │
│  └─ Canvas 渲染  │  └─ 节点控制     │  └─ 向量数据库 (Qdrant)              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 二、核心能力深度解析与插件映射

### 2.1 GitHub 集成 (gh CLI)

**当前实现**:
- PR 检查与状态: `gh pr checks`
- Issue 管理: `gh issue create/list`
- CI/CD workflow 查看: `gh run view --log-failed`
- API 高级查询: `gh api repos/...`

**Nekro-Agent 插件**: `nekro-plugin-github`

```python
@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "gh_pr_checks", "检查 PR CI 状态")
async def gh_pr_checks(_ctx: AgentCtx, owner: str, repo: str, pr: int) -> str:
    result = subprocess.run(["gh", "pr", "checks", str(pr), "--repo", f"{owner}/{repo}"], 
                          capture_output=True, text=True)
    return result.stdout or result.stderr

@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "gh_run_logs", "查看 CI 运行日志")
async def gh_run_logs(_ctx: AgentCtx, owner: str, repo: str, run_id: str, failed_only: bool = False) -> str:
    cmd = ["gh", "run", "view", run_id, "--repo", f"{owner}/{repo}"]
    if failed_only:
        cmd.extend(["--log-failed"])
    return subprocess.run(cmd, capture_output=True, text=True).stdout
```

---

### 2.2 Google Workspace (gog CLI)

**功能映射**:

| Clawdbot (gog) | Nekro-Agent 插件方法 |
|----------------|---------------------|
| `gog gmail search` | `gmail_search(query, max_results)` |
| `gog gmail send` | `gmail_send(to, subject, body)` |
| `gog calendar events` | `calendar_events(calendar_id, start, end)` |
| `gog calendar create` | `calendar_create(calendar_id, title, time)` |
| `gog drive search` | `drive_search(query)` |
| `gog sheets get` | `sheets_get(sheet_id, range)` |
| `gog sheets update` | `sheets_update(sheet_id, range, values)` |
| `gog docs cat` | `docs_cat(doc_id)` |

**插件**: `nekro-plugin-google-workspace`

---

### 2.3 Notion 集成

**当前实现**: Notion API (2025-09-03 版本)

**Nekro-Agent 插件**: `nekro-plugin-notion`

```python
@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "notion_search", "搜索页面")
async def notion_search(_ctx: AgentCtx, query: str) -> list:
    """搜索 Notion 页面和数据库"""

@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "notion_get_page", "获取页面")
async def notion_get_page(_ctx: AgentCtx, page_id: str) -> dict:
    """获取页面内容和元数据"""

@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "notion_query_db", "查询数据库")
async def notion_query_db(_ctx: AgentCtx, db_id: str, filter_obj: dict = None) -> list:
    """查询 Notion 数据库"""
```

---

### 2.4 Session 日志分析

**当前实现**: JSONL 文件解析 + jq

**Nekro-Agent 插件**: `nekro-plugin-session-logs`

```python
@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "session_list", "列出历史会话")
async def session_list(_ctx: AgentCtx, agent_id: str = None) -> list:

@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "session_search", "搜索会话内容")
async def session_search(_ctx: AgentCtx, keyword: str, agent_id: str = None) -> list:

@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "session_cost", "计算会话成本")
async def session_cost(_ctx: AgentCtx, session_id: str) -> float:
```

---

### 2.5 Web 工具

**当前实现**:
- Brave Search API (`web_search`)
- Web Fetch (`web_fetch` - HTML → markdown)

**Nekro-Agent 插件**: `nekro-plugin-web-tools`

```python
@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "web_search", "网络搜索")
async def web_search(_ctx: AgentCtx, query: str, count: int = 10) -> list:

@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "web_fetch", "获取网页内容")
async def web_fetch(_ctx: AgentCtx, url: str, extract_mode: str = "markdown") -> str:
```

---

### 2.6 TTS 语音合成

**当前实现**:
- sag (ElevenLabs)
- sherpa-onnx-tts (本地)

**Nekro-Agent 插件**: `nekro-plugin-tts`

```python
@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "tts_elevenlabs", "ElevenLabs TTS")
async def tts_elevenlabs(_ctx: AgentCtx, text: str, voice_id: str = None) -> str:

@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "tts_local", "本地 TTS")
async def tts_local(_ctx: AgentCtx, text: str, speaker: str = "zh") -> str:
```

---

### 2.7 图像能力

**当前实现**:
- openai-image-gen (DALL-E)
- image 分析工具

**Nekro-Agent 插件**: `nekro-plugin-image`

```python
@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "image_generate", "生成图片")
async def image_generate(_ctx: AgentCtx, prompt: str, size: str = "1024x1024") -> str:

@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "image_analyze", "分析图片")
async def image_analyze(_ctx: AgentCtx, image_path: str, prompt: str = None) -> str:
```

---

### 2.8 天气查询

**当前实现**: wttr.in + Open-Meteo

**Nekro-Agent 插件**: `nekro-plugin-weather`

```python
@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "weather_current", "当前天气")
async def weather_current(_ctx: AgentCtx, location: str = None) -> str:

@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "weather_forecast", "天气预报")
async def weather_forecast(_ctx: AgentCtx, location: str = None, days: int = 3) -> str:
```

---

### 2.9 浏览器控制

**当前实现**: Playwright + CDP

**Nekro-Agent 插件**: `nekro-plugin-browser`

```python
@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "browser_navigate", "导航到 URL")
async def browser_navigate(_ctx: AgentCtx, url: str, profile: str = "default") -> str:

@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "browser_screenshot", "页面截图")
async def browser_screenshot(_ctx: AgentCtx, url: str = None, selector: str = None) -> str:

@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "browser_act", "执行浏览器操作")
async def browser_act(_ctx: AgentCtx, action: str, target: str = None) -> str:
```

---

### 2.10 记忆系统

**当前实现**:
- MEMORY.md (长期记忆)
- memory/*.md (每日笔记)
- plugin store (KV)
- 向量数据库 (Qdrant)

**Nekro-Agent 插件**: `nekro-plugin-memory-system`

```python
@plugin.mount_prompt_inject_method("long_term_memory")
async def inject_long_term_memory(_ctx: AgentCtx) -> str:
    """注入长期记忆内容"""

@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "memory_save", "保存记忆")
async def memory_save(_ctx: AgentCtx, key: str, content: str, memory_type: str = "general") -> str:

@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "memory_search", "搜索记忆")
async def memory_search(_ctx: AgentCtx, query: str, memory_type: str = None) -> list:
```

---

## 三、插件实施路线图

### 3.1 第一阶段：核心能力 (P0-P1)

| 插件名称 | 依赖 | 工作量 | 状态 |
|----------|------|--------|------|
| `nekro-plugin-github` | gh CLI | 3h | 待开发 |
| `nekro-plugin-google-workspace` | gog CLI | 4h | 待开发 |
| `nekro-plugin-web-tools` | Brave API | 2h | 待开发 |
| `nekro-plugin-notion` | Notion API | 3h | 待开发 |
| `nekro-plugin-weather` | wttr.in | 1h | 待开发 |
| `nekro-plugin-memory-system` | 文件系统 | 4h | 待开发 |

### 3.2 第二阶段：扩展能力 (P2-P3)

| 插件名称 | 依赖 | 工作量 |
|----------|------|--------|
| `nekro-plugin-tts` | ElevenLabs/本地 | 3h |
| `nekro-plugin-image` | DALL-E API | 2h |
| `nekro-plugin-session-logs` | 文件系统 | 2h |
| `nekro-plugin-browser` | Playwright | 4h |
| `nekro-plugin-apple` | Apple Script | 3h |

**总计**: ~31h (约一周)

---

## 四、关键技术决策

### 4.1 CLI 封装策略

```python
# ✅ 推荐：封装 CLI 工具（与 Clawdbot 一致）
async def github_pr_checks(_ctx: AgentCtx, owner: str, repo: str, pr: int) -> str:
    result = subprocess.run(["gh", "pr", "checks", ...], capture_output=True, text=True)
    return result.stdout
```

### 4.2 配置管理

- 使用 `plugin.store` 存储 KV 配置
- 敏感信息使用 `ExtraField(is_secret=True)`
- 本地配置文件: `~/.config/nekro-agent/<plugin>/config.json`

### 4.3 复用现有能力

- **消息平台**: 直接使用 nekro-agent 适配器层
- **文件系统**: 复用 `_ctx.fs` 和 `plugin.store`
- **向量数据库**: 使用 `plugin.get_vector_collection_name()`

---

## 五、总结

### 5.1 核心差异

| 维度 | Clawdbot | Nekro-Agent |
|------|----------|-------------|
| 语言 | TypeScript | Python |
| 插件格式 | .skill (zip) | Python module |
| 消息集成 | Native plugins | Adapter layer |
| 存储 | JSON + KV | Plugin store |
| AI 集成 | 多模型 SDK | 统一接口 |

### 5.2 复写优势

1. **Python 生态**: 直接使用 requests, aiohttp
2. **类型安全**: 基于pyright 类型检查
3. **沙盒隔离**: AI 代码在沙盒中执行
4. **架构统一**: 与 nekro-agent 核心深度集成

---

*报告生成时间: 2026-02-02*
*文件位置: /Users/clawd/clawd/memory/clawdbot_to_nekro_agent_analysis.md*
