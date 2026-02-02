# MEMORY.md - 长期记忆

## 账号信息

### Miose (李享) - 我的主人
- **GitHub**: @KroMiose
- **Email**: li_xiangff@163.com
- **Role**: NekroAI 创始人，全栈工程师

### Yuki - 我 (AI 助手)
- **GitHub**: @YukiAcerium
- **Email**: yukiacerium@gmail.com
- **NekroAI 社区密钥**: `nk_i9yzyYhVSHVeDtXJhAllyeVP`
- **用途**: 用于发布我开发的 nekro-agent 插件到插件市场

## 邮件系统配置 (2026-01-29)

### Gmail Pub/Sub
- **GCP 项目**: `yuki-gmail-bot`
- **Gmail 账号**: `yukiacerium@gmail.com`
- **Pub/Sub 主题**: `projects/yuki-gmail-bot/topics/gog-gmail-watch`
- **Clawdbot hook token**: `Rz1TZ2hghZ1wzahAX38AGM9J9fzTaoIJ4CoCBTLH9U=`
- **gog serve**: `127.0.0.1:8788/gmail-pubsub`

### 重要提醒
- Tailscale Funnel 需要启用才能让 Gmail 推送公网可达
- 当前只有本地测试可用

## 已发布的插件

### social_memory (社交记忆系统) ✅
- **模块名**: `social_memory`
- **插件 ID**: `0e930e7e-42b3-455b-bfb5-cfb584c38dcc`
- **GitHub**: https://github.com/YukiAcerium/nekro-plugin-social-memory
- **发布时间**: 2026-01-29
- **功能**: 整合好感度追踪 + 用户记忆管理
  - 6 级关系等级（敌人 → 陌生人 → 熟人 → 朋友 → 密友 → 灵魂伴侣）
  - 5 种记忆类型（偏好/信息/约定/兴趣/习惯）
  - 6 个羁绊解锁特殊能力
  - 智能提示注入
- **设计灵感**: history_travel + note.py + emotion.py

## 试验性插件 (未发布)

### nekro_weather_plus (天气插件)
- **模块名**: `nekro_weather_plus`
- **用途**: 仅作为插件开发模板练习，不发布到市场
- **GitHub**: https://github.com/YukiAcerium/nekro-plugin-weather
- **功能**: 实时天气查询和预报

## API 端点

- **NekroAI 云端 API**: `https://community.nekro.ai`
- **认证方式**: `X-API-Key` 请求头
- **发布插件**: `POST /api/plugin`
- **查询插件**: `GET /api/plugin/{module_name}`

## 插件开发核心知识 (2024-02-更新)

### 系统学习完成

已系统学习 Nekro-Agent 插件开发，整理完整技能文档于 `/Users/clawd/clawd/skills/plugin-developer/`

**交付物：**
- `SKILL.md` - 完整开发指南（14章，1200+行）
- `HIGHLIGHTS.md` - 设计亮点和创新思路收集

### NekroPlugin 基类核心属性和方法

**必须定义：**
```python
plugin = NekroPlugin(
    name="插件名",
    module_name="模块名",
    description="描述",
    version="0.1.0",
    author="作者",
    url="GitHub地址",
    support_adapter=["onebot_v11", "telegram"],  # 可选
)
```

**核心回调方法：**
- `mount_init_method()` - 初始化
- `mount_sandbox_method()` - 工具方法
- `mount_prompt_inject_method()` - 提示词注入
- `mount_config()` - 配置项定义
- `mount_router()` - API 路由
- `mount_cleanup_method()` - 清理
- `mount_on_channel_reset()` - 会话重置
- `mount_on_user_message()` - 用户消息
- `mount_collect_methods()` - 动态方法收集

**配置系统 (Pydantic + ExtraField):**
```python
@plugin.mount_config()
class MyConfig(ConfigBase):
    API_KEY: str = Field(
        default="",
        json_schema_extra=ExtraField(is_secret=True).model_dump()
    )
    MODE: Literal["fast", "accurate"] = Field(default="balanced")
    MODEL: str = Field(
        default="default",
        json_schema_extra=ExtraField(ref_model_groups=True, model_type="chat").model_dump()
    )
```

**存储系统:**
```python
store = plugin.store  # PluginStore 实例
await store.set(chat_key="", user_key="", store_key="key", value="data")
data = await store.get(chat_key="", user_key="", store_key="key")
```

**AgentCtx 核心属性：**
```python
# 标识信息
_ctx.chat_key           # 聊天频道唯一标识
_ctx.channel_id         # 频道原始 ID
_ctx.channel_type       # 频道类型 (group/private)
_ctx.adapter_key        # 适配器标识

# 功能模块
_ctx.send_text()        # 发送文本
_ctx.send_image()       # 发送图片
_ctx.send_file()        # 发送文件
_ctx.fs                 # 文件系统工具
```

**沙盒方法类型:**
| 类型 | 用途 | 返回值 | AI 行为 |
|------|------|--------|---------|
| `TOOL` | 直接工具调用 | 任意可序列化 | 使用返回值继续任务 |
| `AGENT` | 需要 AI 处理的操作 | str | 触发新一轮回复 |
| `BEHAVIOR` | 执行副作用操作 | str | 记录结果，不立即回复 |
| `MULTIMODAL_AGENT` | 多模态内容处理 | 消息段列表 | 触发新一轮回复 |

### 高级功能

**动态路由 (FastAPI):**
```python
@plugin.mount_router()
def create_router() -> APIRouter:
    router = APIRouter()
    @router.get("/data")
    async def get_data(): return {"data": "test"}
    return router
```

**向量数据库 (Qdrant):**
```python
collection_name = plugin.get_vector_collection_name()
client = await core.get_qdrant_client()
```

**动态包导入:**
```python
requests = dynamic_import_pkg("requests>=2.25.0")
```

**文件交互:**
```python
# 插件向 AI 传递文件
sandbox_path = await _ctx.fs.mixed_forward_file(url, file_name="x.png")

# AI 向插件传递文件
host_path = _ctx.fs.get_file(sandbox_path)
```

### 典型插件结构

1. **note.py** - 持久化记忆系统，Pydantic 模型 + 提示注入
2. **history_travel.py** - 历史记录检索，关键词搜索 + 上下文漫游
3. **emotion.py** - 向量数据库集成，语义搜索 + 图片管理
4. **basic.py** - 基础工具，缓存机制 + 防刷屏 + 适配器抽象
5. **draw/__init__.py** - 绘画工具包，多模型支持

### 关键设计模式

1. **插件生命周期**：Init → Normal → Cleanup
2. **事件回调系统**：6种事件类型覆盖全流程
3. **配置热更新**：修改配置即时生效
4. **存储隔离**：chat_key/user_key/全局三级隔离
5. **适配器兼容**：通过 adapter_key 适配多平台

## 插件开发 Skill 仓库 (2026-01-30)

### GitHub 仓库
https://github.com/YukiAcerium/nekro-agent-skills

### 仓库结构
```
nekro-agent-skills/
├── README.md              # 详细说明和使用指南
├── .gitignore
└── plugin-developer/
    ├── SKILL.md          # 34KB, 14章完整开发指南
    └── HIGHLIGHTS.md     # 9KB 设计亮点收集
```

### SKILL.md 核心章节（14章）
1. 插件开发概述 - 系统架构和核心概念
2. 插件结构 - 标准目录和文件规范
3. 核心概念 - NekroPlugin、生命周期、沙盒方法
4. 配置系统 - Pydantic + ExtraField 完整指南
5. 存储机制 - KV存储和文件系统
6. 提示词注入 - 动态注入机制
7. 事件系统 - 6种事件类型详解
8. 高级功能 - 动态路由、向量数据库、文件交互
9. 最佳实践 - 代码规范、安全性、性能优化
10. CI/CD - GitHub Actions 工作流
11. 发布流程 - 打包和市场发布
12. 示例插件解析 - 典型插件深度分析
13. 常见问题 - FAQ 和解决方案
14. 参考资源 - 文档链接和工具

## 文档与源码交叉验证 (2026-01-30)

### 发现的问题
- **总计**: 19 个问题
- **严重**: 3 个（返回值描述错误、弃用方法）
- **中等**: 13 个（文档遗漏）
- **其他**: 3 个（源码问题、缺少示例）

### 已修复的问题
1. **PluginStore.set() 返回值** - 0=创建成功, 1=更新成功
2. **PluginStore.delete() 返回值** - 0=删除成功, 1=记录不存在
3. **get_plugin_path() 弃用** - 替换为 get_plugin_data_dir()

### GitHub Issue & PRs
- **Issue (中文)**: KroMiose/nekro-agent-doc#58
- **PR (中文)**: #59 - https://github.com/KroMiose/nekro-agent-doc/pull/59
- **PR (英文)**: #60 - https://github.com/KroMiose/nekro-agent-doc/pull/60

### 验证方法
所有问题均已根据源码验证：
- `nekro_agent/services/plugin/base.py` (set/delete 方法)
- `nekro_agent/api/plugin.py` (API 导出)
- `nekro_agent/services/plugin/schema.py` (Schema 定义)

### 待修复的文档遗漏
- get_plugin_data_dir()
- mount_webhook_method()
- mount_async_task()
- enable()/disable() 机制
- on_enabled()/on_disabled() 装饰器
- get_vector_collection_name()
- get_docs()
- get_name()/get_description()
- trigger_callbacks()
- dynamic_import_pkg
- ExtraField 完整参数

## 重要提醒（已修复）

### PluginStore 返回值
- `set()`: 0=创建新记录成功, 1=更新已有记录成功
- `delete()`: 0=删除成功, 1=记录不存在（删除失败）

### 弃用的方法
- ~~`get_plugin_path()`~~ → 使用 `get_plugin_data_dir()`

---

## 记忆空间系统 (2026-01-31)

### 项目信息

- **仓库**: https://github.com/YukiAcerium/memory-space (私有)
- **本地路径**: /Users/clawd/clawd/memory-space
- **自动同步**: 每天 6:00 (Asia/Shanghai)

### 同步内容

1. **记忆文件**: MEMORY.md, IDENTITY.md, USER.md, SOUL.md, AGENTS.md, TOOLS.md
2. **每日笔记**: 2025-01-25 至今的所有笔记
3. **技能配置**: 55+ 可用技能列表
4. **项目文件**: yuki-research 所有项目
5. **配置文件**: Clawdbot, Nekro-Agent 配置
6. **凭证索引**: 仅索引，不包含实际凭证

### 工具脚本

- `tools/sync.sh`: 同步脚本
- `tools/restore.sh`: 恢复脚本

### 恢复流程

1. 克隆仓库: `git clone git@github.com:YukiAcerium/memory-space.git`
2. 运行恢复: `cd memory-space && ./tools/restore.sh`
3. 重新配置凭证

### 目的

确保即使将来出问题，也能恢复所有知识和配置。
