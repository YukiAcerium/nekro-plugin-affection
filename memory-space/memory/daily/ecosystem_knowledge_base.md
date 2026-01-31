# NekroAgent 生态系统知识库

**创建时间**: 2026-01-29
**维护者**: Yuki
**版本**: 1.0.0

---

## 📚 目录结构

### 一、核心概念
1. [插件系统架构](#插件系统架构)
2. [插件开发基础](#插件开发基础)
3. [核心 API 参考](#核心-api-参考)

### 二、内置插件分析
4. [核心交互类插件](#核心交互类插件)
5. [随机工具类插件](#随机工具类插件)
6. [外部服务集成类插件](#外部服务集成类插件)
7. [娱乐多媒体类插件](#娱乐多媒体类插件)
8. [社交数据类插件](#社交数据类插件)

### 三、插件开发指南
9. [快速开始](#快速开始)
10. [设计模式](#设计模式)
11. [最佳实践](#最佳实践)
12. [常见问题](#常见问题)

### 四、开发资源
13. [官方文档](#官方文档)
14. [示例插件](#示例插件)
15. [工具和依赖](#工具和依赖)

---

## 一、插件系统架构

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    Nekro Agent Core                     │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Plugin System                      │   │
│  │  - Plugin Loader    - Event System              │   │
│  │  - RPC Handler      - Storage Manager           │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │              API Layer                          │   │
│  │  - Message Service  - Config System             │   │
│  │  - Vector DB        - Timer Service             │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
           ▲                              │
           │ RPC                      │ Events
           ▼                              ▼
┌─────────────────────────────────────────────────────────┐
│                 Plugins (Plugins)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │  basic   │ │  dice    │ │ emotion  │ │  github  │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 核心组件

#### 1. NekroPlugin
**作用**: 插件的核心实例，用于注册所有功能

**必需参数**:
```python
plugin = NekroPlugin(
    name="插件名称",              # UI 显示名称
    module_name="模块名",         # 唯一标识符
    description="描述",           # 功能描述
    version="1.0.0",             # 版本号
    author="作者",               # 作者名
    url="https://...",           # 仓库地址
    support_adapter=[],          # 支持的适配器
)
```

**提供的装饰器**:
- `@plugin.mount_config()` - 注册配置
- `@plugin.mount_sandbox_method()` - 注册沙盒方法
- `@plugin.mount_prompt_inject_method()` - 注入提示词
- `@plugin.mount_cleanup_method()` - 清理资源
- `@plugin.mount_on_user_message()` - 用户消息事件
- `@plugin.mount_on_channel_reset()` - 频道重置事件

#### 2. AgentCtx
**作用**: 提供访问系统资源的上下文

**核心属性**:
```python
class AgentCtx:
    chat_key: str           # 聊天频道标识
    adapter_key: str        # 适配器类型
    chat_type: str          # 聊天类型
    from_user_id: str       # 用户 ID
    
    # 消息服务
    ms: MessageService
    
    # 文件系统
    fs: FileSystem
    
    # 配置
    config: Dict
    adapter_config: Dict
```

#### 3. SandboxMethodType
**作用**: 定义沙盒方法的行为模式

| 类型 | 用途 | 返回值 | AI 行为 |
|------|------|--------|---------|
| `TOOL` | 执行操作 | 任意类型 | 继续执行 |
| `AGENT` | 获取信息 | str | 新一轮回复 |
| `BEHAVIOR` | 修改状态 | str | 记录但不回复 |
| `MULTIMODAL_AGENT` | 多模态内容 | List[Dict] | 新一轮回复 |

---

## 二、插件开发基础

### 最小插件结构

```
my_plugin/
├── __init__.py           # 必须：导出 plugin 实例
├── plugin.py             # 插件核心代码（可与 __init__.py 合并）
├── pyproject.toml        # 依赖配置（可选）
└── README.md             # 文档（可选）
```

### 插件实例定义

```python
# __init__.py
from .plugin import plugin
__all__ = ["plugin"]

# plugin.py
from nekro_agent.api.plugin import NekroPlugin

plugin = NekroPlugin(
    name="我的插件",
    module_name="my_plugin",
    description="插件描述",
    version="1.0.0",
    author="作者",
    url="https://github.com/..."
)
```

### 沙盒方法定义

```python
from nekro_agent.api.plugin import NekroPlugin, SandboxMethodType
from nekro_agent.api.schemas import AgentCtx

@plugin.mount_sandbox_method(
    SandboxMethodType.TOOL,
    name="方法名称",
    description="方法功能描述"
)
async def my_method(_ctx: AgentCtx, param: str) -> str:
    """方法详细说明
    
    Args:
        param: 参数说明
        
    Returns:
        返回值说明
    """
    # 实现逻辑
    return "结果"
```

### 配置定义

```python
from nekro_agent.api.plugin import ConfigBase, ExtraField
from pydantic import Field

@plugin.mount_config()
class MyConfig(ConfigBase):
    """配置说明"""
    
    FIELD_NAME: str = Field(
        default="默认值",
        title="显示标题",
        description="字段描述",
        json_schema_extra=ExtraField(
            is_secret=True,           # 敏感信息
            ref_model_groups=True,    # 引用模型组
            model_type="chat",        # chat/embedding/draw
            is_textarea=True,         # 多行文本
            placeholder="提示文字",
        ).model_dump()
    )

config = plugin.get_config(MyConfig)
```

### 数据存储

```python
# 保存数据
await plugin.store.set(
    chat_key=_ctx.chat_key,      # 会话级
    user_key=_ctx.user_id,       # 用户级（可选）
    store_key="key_name",        # 键名
    value="data"                 # 值（字符串）
)

# 读取数据
data = await plugin.store.get(
    chat_key=_ctx.chat_key,
    store_key="key_name"
)

# 删除数据
await plugin.store.delete(
    chat_key=_ctx.chat_key,
    store_key="key_name"
)
```

### 提示词注入

```python
@plugin.mount_prompt_inject_method("prompt_name")
async def inject_prompt(_ctx: AgentCtx) -> str:
    """注入提示词（建议 <300 字符）"""
    data = await plugin.store.get(chat_key=_ctx.chat_key, store_key="data")
    return f"当前状态: {format_data(data)}"
```

---

## 三、核心 API 参考

### 插件 API

| API | 作用 | 示例 |
|-----|------|------|
| `plugin.mount_config()` | 注册配置类 | `@plugin.mount_config()` |
| `plugin.mount_sandbox_method()` | 注册沙盒方法 | `@plugin.mount_sandbox_method(...)` |
| `plugin.mount_prompt_inject_method()` | 注册提示词注入 | `@plugin.mount_prompt_inject_method()` |
| `plugin.mount_cleanup_method()` | 注册清理方法 | `@plugin.mount_cleanup_method()` |
| `plugin.get_config()` | 获取配置实例 | `config = plugin.get_config(Config)` |
| `plugin.store` | 访问存储 | `await plugin.store.set(...)` |
| `plugin.get_plugin_path()` | 获取插件数据目录 | `path = plugin.get_plugin_path()` |
| `plugin.get_vector_collection_name()` | 获取向量集合名 | `collection = plugin.get_vector_collection_name()` |

### SandboxMethodType 枚举

| 枚举值 | 用途 | 返回值类型 | AI 行为 |
|--------|------|------------|---------|
| `SandboxMethodType.TOOL` | 工具方法 | 任意可序列化 | 继续执行 |
| `SandboxMethodType.AGENT` | 代理方法 | str | 新一轮回复 |
| `SandboxMethodType.BEHAVIOR` | 行为方法 | str | 记录不回复 |
| `SandboxMethodType.MULTIMODAL_AGENT` | 多模态代理 | List[Dict] | 新一轮回复 |

### 消息服务 (_ctx.ms)

| 方法 | 作用 | 参数 |
|------|------|------|
| `send_text()` | 发送文本 | `chat_key`, `message`, `_ctx` |
| `send_image()` | 发送图片 | `chat_key`, `image_path`, `_ctx` |
| `send_file()` | 发送文件 | `chat_key`, `file_path`, `_ctx` |

### 配置字段类型

| 字段类型 | Pydantic 类型 | ExtraField 参数 |
|----------|---------------|-----------------|
| 文本 | `str` | `is_textarea=True` |
| 数值 | `int/float` | - |
| 开关 | `bool` | - |
| 密码 | `str` | `is_secret=True` |
| 模型组 | `str` | `ref_model_groups=True`, `model_type="chat"` |
| 下拉选择 | `Literal["a", "b"]` | - |

---

## 四、内置插件分析

### 核心交互类

| 插件 | 文件 | 核心功能 | 代码行数 |
|------|------|----------|----------|
| **basic** | basic.py | 消息发送、防刷屏 | 400+ |
| **status** | status.py | 角色状态管理 | 400+ |
| **note** | note.py | 长期记忆系统 | 300+ |

### 随机工具类

| 插件 | 文件 | 核心功能 | 亮点特性 |
|------|------|----------|----------|
| **dice** | dice.py | 掷骰检定 | 概率轮盘、全局控制 |
| **timer** | timer.py | 定时任务 | 提示词注入 |
| **view_image** | view_image.py | 图像理解 | 多模态模型 |

### 外部服务类

| 插件 | 文件 | 核心功能 | 技术栈 |
|------|------|----------|--------|
| **google_search** | google_search.py | 网页搜索 | Google API |
| **email_utils** | email_utils.py | 邮件操作 | IMAP/SMTP |
| **github** | github/ | Webhook接收 | 订阅系统 |
| **bilibili_live** | bilibili_live_utils.py | 直播监控 | HTTP API |
| **minecraft_utils** | minecraft_utils.py | MC控制 | 游戏API |

### 娱乐多媒体类

| 插件 | 文件 | 核心功能 | 亮点 |
|------|------|----------|------|
| **emotion** | emotion.py | 表情包管理 | **向量数据库** |
| **draw** | draw/ | AI绘图 | 多模型支持 |
| **ai_voice** | ai_voice.py | 语音合成 | TTS集成 |
| **whiteboard** | whiteboard.py | 画图工具 | 图像生成 |

### 社交数据类

| 插件 | 文件 | 核心功能 |
|------|------|----------|
| **group_honor** | group_honor.py | 群荣誉统计 |
| **history_travel** | history_travel.py | 历史回溯 |
| **judgement** | judgement.py | 评判系统 |
| **dynamic_importer** | dynamic_importer.py | 动态导入 |

---

## 五、设计模式

### 1. 配置模式

```python
@plugin.mount_config()
class PluginConfig(ConfigBase):
    FIELD: str = Field(
        default="value",
        title="Title",
        description="Description",
        json_schema_extra=ExtraField(
            is_secret=True,
            ref_model_groups=True,
            model_type="chat"
        ).model_dump()
    )

config = plugin.get_config(PluginConfig)
```

### 2. 存储模式

```python
# 数据模型
class ChannelData(BaseModel):
    chat_key: str
    data: List[Item] = []
    
    async def save(self):
        await plugin.store.set(
            chat_key=self.chat_key,
            store_key="data",
            value=self.model_dump_json()
        )
```

### 3. 提示词注入模式

```python
@plugin.mount_prompt_inject_method("name")
async def inject_prompt(_ctx: AgentCtx) -> str:
    data = await get_data(_ctx)
    return format_for_ai(data)  # <300 字符
```

### 4. 事件处理模式

```python
@plugin.mount_on_user_message()
async def on_message(_ctx: AgentCtx, message: ChatMessage):
    # 处理用户消息
    pass

@plugin.mount_on_channel_reset()
async def on_reset(_ctx: AgentCtx):
    # 清理频道数据
    await plugin.store.delete(chat_key=_ctx.chat_key, store_key="*")
```

### 5. 向量数据库模式

```python
# 获取客户端
client = await core.get_qdrant_client()

# 获取集合名
collection = plugin.get_vector_collection_name()

# 搜索
results = client.search(
    collection_name=collection,
    query_vector=embeddings[0],
    limit=5
)
```

---

## 六、最佳实践

### 1. 文档字符串规范

```python
@plugin.mount_sandbox_method(
    SandboxMethodType.TOOL,
    name="方法名",
    description="一句话描述"
)
async def my_method(_ctx: AgentCtx, param: str) -> str:
    """方法详细说明
    
    **应用场景**: 适用场景描述
    
    Args:
        param (str): 参数说明
        
    Returns:
        str: 返回值说明
        
    Example:
        my_method(param="value")
    """
```

### 2. 错误处理

```python
async def my_method(_ctx: AgentCtx, param: str) -> str:
    # 1. 参数验证
    if not param:
        raise ValueError("参数不能为空")
    
    # 2. 业务逻辑
    try:
        result = await operation(param)
    except ValueError as e:
        raise ValueError(f"业务错误: {e}")
    except Exception as e:
        logger.exception("操作失败")
        raise Exception(f"执行失败: {e}")
    
    return result
```

### 3. 缓存优化

```python
# 模块级缓存
_CACHE: Dict[str, Any] = {}

async def my_method(_ctx: AgentCtx, key: str) -> str:
    if key in _CACHE:
        return _CACHE[key]
    
    result = await expensive_operation(key)
    _CACHE[key] = result
    return result
```

### 4. 多适配器支持

```python
plugin = NekroPlugin(
    name="插件名",
    module_name="module",
    support_adapter=["onebot_v11", "discord", "telegram"]
)

@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "方法")
async def method(_ctx: AgentCtx, param: str) -> str:
    if _ctx.adapter_key not in plugin.support_adapter:
        raise Exception(f"Adapter not supported: {_ctx.adapter_key}")
```

### 5. 清理资源

```python
@plugin.mount_cleanup_method()
async def clean_up():
    global GLOBAL_STATE
    GLOBAL_STATE = None
    logger.info("Plugin cleaned up")
```

---

## 七、常见问题

### Q1: 插件不加载？
- 检查 `__init__.py` 是否正确导出 `plugin` 实例
- 检查 `module_name` 是否唯一
- 查看日志中的错误信息

### Q2: 沙盒方法无法调用？
- 确认方法使用 `async def` 定义
- 确认第一个参数是 `_ctx: AgentCtx`
- 确认返回类型注解正确

### Q3: 配置不生效？
- 使用 `@plugin.mount_config()` 装饰配置类
- 使用 `plugin.get_config(Config)` 获取实例
- 检查配置字段名称是否正确

### Q4: 存储数据格式？
- `value` 必须是字符串
- 复杂对象使用 `model_dump_json()` 序列化
- 读取后使用 `model_validate_json()` 反序列化

---

## 八、官方资源

### 文档
- **官方文档**: https://doc.nekro.ai/
- **插件开发指南**: https://doc.nekro.ai/docs/04_plugin_dev/intro.html
- **API 参考**: https://doc.nekro.ai/docs/04_plugin_dev/04_system_api_reference.html

### 示例插件
- **模板插件**: https://github.com/KroMiose/nekro-plugin-template
- **高级绘图**: https://github.com/KroMiose/nekro-plugin-magic-draw
- **内置插件**: `/Users/clawd/clawd/nekro-agent/plugins/builtin/`

### 社区
- **插件市场**: https://community.nekro.ai/plugins.html
- **交流群**: 636925153
- **GitHub**: https://github.com/KroMiose/nekro-agent

---

## 九、本地资源

### 已克隆的仓库
| 仓库 | 本地路径 | 用途 |
|------|----------|------|
| nekro-agent | `/Users/clawd/clawd/nekro-agent/` | 核心源码 |
| nekro-agent-doc | `/Users/clawd/clawd/nekro-agent-doc/` | 官方文档 |
| nekro-plugin-template | `/Users/clawd/clawd/nekro-plugin-template/` | 开发模板 |
| nekro-plugin-magic-draw | `/Users/clawd/clawd/nekro-plugin-magic-draw/` | 示例插件 |

### 学习笔记
| 文件 | 大小 | 内容 |
|------|------|------|
| plugin_development_study.md | 11KB | 详细学习笔记 |
| plugin_development_mastery.md | 9KB | 掌握程度总结 |
| plugin_development_final_report.md | 5KB | 最终报告 |
| builtin_plugins_analysis.md | 1KB | 插件分析框架 |
| builtin_plugins_final_analysis.md | 10KB | 完整插件分析 |
| ecosystem_knowledge_base.md | 12KB | **本文档** |

**总计**: 6 个学习文件，48KB+ 文档

---

## 十、快速参考

### 插件开发 checklist

- [ ] 1. 创建插件目录结构
- [ ] 2. 定义 `NekroPlugin` 实例
- [ ] 3. 添加配置类（如需要）
- [ ] 4. 实现沙盒方法
- [ ] 5. 添加提示词注入（如需要）
- [ ] 6. 实现清理方法
- [ ] 7. 编写文档字符串
- [ ] 8. 测试插件功能

### 常用代码片段

**最小插件**:
```python
from nekro_agent.api.plugin import NekroPlugin, SandboxMethodType
from nekro_agent.api.schemas import AgentCtx

plugin = NekroPlugin(name="插件名", module_name="模块名", description="描述")

@plugin.mount_sandbox_method(SandboxMethodType.TOOL, name="方法名")
async def method(_ctx: AgentCtx) -> str:
    return "结果"
```

**带配置**:
```python
@plugin.mount_config()
class Config(ConfigBase):
    FIELD: str = Field(default="value")

config = plugin.get_config(Config)
```

**带存储**:
```python
await plugin.store.set(chat_key=_ctx.chat_key, store_key="key", value="data")
```

---

*本文档由 Yuki 维护*
*最后更新: 2026-01-29 15:55*
*版本: 1.0.0*
