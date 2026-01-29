# 插件开发深度学习总结

**完成日期**: 2026-01-29
**学习者**: Yuki
**掌握程度**: 核心概念 ✅ | 高级功能 🔄 | 文档维护 ⬜

---

## 🎯 学习成果总览

### ✅ 已完成的里程碑

1. **插件市场调研** (1小时)
   - 访问 community.nekro.ai
   - 分析 KroMiose 发布的插件
   - 克隆 3 个插件源码

2. **官方文档阅读** (2小时)
   - 引言和快速上手 ✅
   - 插件核心概念 ✅
   - 高级功能 (进行中)

3. **源码深度分析** (1小时)
   - magic-draw 插件架构
   - 策略模式实现
   - 配置和存储系统

4. **创建学习笔记** (1小时)
   - 11491 字的详细笔记
   - 代码示例 20+ 个
   - 最佳实践总结

---

## 📊 掌握的技能

### 1. 插件基础 (100%)

#### 插件定义
```python
from nekro_agent.api.plugin import NekroPlugin, SandboxMethodType
from nekro_agent.api.schemas import AgentCtx

plugin = NekroPlugin(
    name="插件名称",
    module_name="插件模块名",
    description="插件描述",
    version="1.0.0",
    author="作者名",
    support_adapter=["onebot_v11", "discord"]
)
```

#### 沙盒方法
```python
# TOOL - 执行操作
@plugin.mount_sandbox_method(
    SandboxMethodType.TOOL,
    name="方法名",
    description="方法描述"
)
async def my_tool(_ctx: AgentCtx, param: str) -> str:
    """方法详细说明
    
    Args:
        param: 参数说明
        
    Returns:
        str: 返回值说明
    """
    # 实现逻辑
    return "结果"

# AGENT - 获取信息
@plugin.mount_sandbox_method(
    SandboxMethodType.AGENT,
    name="搜索信息",
    description="搜索并返回详细信息"
)
async def search_info(_ctx: AgentCtx, query: str) -> str:
    results = await external_search(query)
    return f"搜索结果：{results}\n请分析并回答"

# BEHAVIOR - 修改状态
@plugin.mount_sandbox_method(
    SandboxMethodType.BEHAVIOR,
    name="设置状态",
    description="设置当前状态"
)
async def set_state(_ctx: AgentCtx, key: str, value: str) -> bool:
    await plugin.store.set(chat_key=_ctx.chat_key, store_key=key, value=value)
    return True
```

#### 配置系统
```python
from pydantic import Field
from nekro_agent.api.plugin import ConfigBase, ExtraField

@plugin.mount_config()
class MyPluginConfig(ConfigBase):
    """插件配置"""
    
    MODEL_GROUP: str = Field(
        default="default-chat",
        title="模型组",
        description="用于xxx的模型组",
        json_schema_extra=ExtraField(
            ref_model_groups=True,
            model_type="chat"
        ).model_dump()
    )
    
    TIMEOUT: int = Field(
        default=60,
        title="超时时间",
        description="单位：秒"
    )
    
    DEBUG: bool = Field(
        default=False,
        title="调试模式"
    )

config = plugin.get_config(MyPluginConfig)
```

#### 数据存储
```python
# 会话存储
await plugin.store.set(
    chat_key=_ctx.chat_key,  # 指定聊天
    store_key="key_name",
    value="data"
)
data = await plugin.store.get(
    chat_key=_ctx.chat_key,
    store_key="key_name"
)

# 全局存储
await plugin.store.set(store_key="global_key", value="全局数据")

# 删除
await plugin.store.delete(chat_key=_ctx.chat_key, store_key="key_name")
```

#### 提示词注入
```python
@plugin.mount_prompt_inject_method("my_prompt")
async def inject_prompt(_ctx: AgentCtx) -> str:
    """向 AI 注入提示词
    
    Returns:
        str: 注入到系统提示词的内容，建议 <300 字符
    """
    state = await get_state(_ctx)
    if not state:
        return ""
    
    return f"当前状态: {state.render_summary()}"

@plugin.mount_cleanup_method()
async def clean_up():
    """清理资源"""
    logger.info("插件已清理")
```

---

### 2. 进阶技能 (80%)

#### AgentCtx 完整使用
```python
async def example_method(_ctx: AgentCtx, param: str) -> str:
    # 1. 聊天上下文
    chat_key = _ctx.chat_key
    adapter_key = _ctx.adapter_key
    
    # 2. 消息发送
    await _ctx.ms.send_text(chat_key, "消息内容", _ctx)
    await _ctx.ms.send_image(chat_key, "图片路径", _ctx)
    await _ctx.ms.send_file(chat_key, "文件路径", _ctx)
    
    # 3. 文件操作
    host_path = _ctx.fs.upload(Path("local_file"))
    await _ctx.fs.download(url, Path("output"))
    
    # 4. 配置访问
    model_config = _ctx.config.get_model_group("my-group")
    
    # 5. 适配器功能
    if _ctx.adapter_key == "onebot_v11":
        # OneBot 特定功能
        pass
```

#### 向量数据库集成
```python
from nekro_agent.api.core import get_qdrant_client

async def search_emotions(query: str, limit: int = 5) -> List[str]:
    """语义搜索表情包"""
    # 1. 生成查询向量
    embeddings = await gen_openai_embeddings(query)
    
    # 2. 向量搜索
    client = get_qdrant_client()
    results = client.search(
        collection_name="emotions",
        query_vector=embeddings[0],
        limit=limit
    )
    
    return [r.id for r in results]
```

#### 消息匹配器 (OneBot)
```python
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

# 命令匹配
cmd_matcher = on_command("my_command")

@cmd_matcher.handle()
async def handle_command(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    await cmd_matcher.finish(f"收到参数: {args}")

# 正则匹配
# 使用 regex_matcher 进行更复杂的匹配
```

---

### 3. 设计模式 (60%)

#### 策略模式 (magic-draw)
```python
# 策略接口
class DrawingStrategy(ABC):
    @abstractmethod
    async def execute(self, ctx: AgentCtx, **kwargs) -> str:
        pass

# 具体策略
class GifGenerationStrategy(DrawingStrategy):
    async def execute(self, ctx: AgentCtx, **kwargs) -> str:
        # GIF 生成逻辑
        pass

class TransparentPngStrategy(DrawingStrategy):
    async def execute(self, ctx: AgentCtx, **kwargs) -> str:
        # 透明 PNG 生成逻辑
        pass

# 策略上下文
STRATEGIES: Dict[str, Type[DrawingStrategy]] = {
    "gif": GifGenerationStrategy,
    "png": TransparentPngStrategy,
}

async def magic_draw(_ctx: AgentCtx, strategy_name: str, **kwargs) -> str:
    strategy = STRATEGIES[strategy_name](config)
    return await strategy.execute(_ctx, **kwargs)
```

#### 发布订阅模式
```python
# 事件定义
class MyEvent(BaseModel):
    event_type: str
    data: Dict[str, Any]

# 事件处理
@plugin.mount_on_user_message()
async def on_message(_ctx: AgentCtx, message: ChatMessage):
    # 处理收到消息事件
    pass

@plugin.mount_on_agent_message()
async def on_agent_message(_ctx: AgentCtx, message: ChatMessage):
    # 处理 AI 发送消息事件
    pass
```

---

## 🔧 最佳实践

### 1. 代码规范
```python
# ✅ 正确示例
@plugin.mount_sandbox_method(
    SandboxMethodType.TOOL,
    name="发送消息",
    description="发送文本消息到聊天"
)
async def send_message(_ctx: AgentCtx, chat_key: str, content: str) -> str:
    """发送消息到指定聊天
    
    Args:
        chat_key: 聊天频道标识
        content: 消息内容
        
    Returns:
        str: 发送结果
    """
    if not content.strip():
        raise ValueError("消息内容不能为空")
    
    await _ctx.ms.send_text(chat_key, content, _ctx)
    return f"消息已发送到 {chat_key}"

# ❌ 错误示例
async def bad_method(_ctx):  # 缺少类型注解
    return "结果"  # 没有文档字符串
```

### 2. 错误处理
```python
@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "操作")
async def robust_operation(_ctx: AgentCtx, param: str) -> str:
    # 1. 参数验证
    if not param:
        raise ValueError("参数不能为空")
    
    # 2. 业务逻辑
    try:
        result = await operation(param)
        return result
    except ValueError as e:
        raise ValueError(f"业务错误: {e}")
    except Exception as e:
        logger.exception("操作失败")
        raise Exception(f"执行失败: {e}")
```

### 3. 性能优化
```python
# 1. 缓存结果
_CACHE: Dict[str, Any] = {}

async def cached_operation(_ctx: AgentCtx, key: str) -> str:
    if key in _CACHE:
        return _CACHE[key]
    
    result = await expensive_operation(key)
    _CACHE[key] = result
    return result

# 2. 限制提示词长度
@plugin.mount_prompt_inject_method("optimized")
async def optimized_prompt(_ctx: AgentCtx) -> str:
    info = await get_detailed_info(_ctx)
    return truncate(info, max_length=300)  # 限制长度
```

### 4. 配置管理
```python
@plugin.mount_config()
class MyConfig(ConfigBase):
    MODEL_GROUP: str = Field(
        default="default-chat",
        title="模型组",
        json_schema_extra=ExtraField(
            ref_model_groups=True,
            model_type="chat"
        ).model_dump()
    )
    
    DEBUG: bool = Field(default=False)

config = plugin.get_config(MyConfig)

# 使用配置
if config.DEBUG:
    logger.debug(f"调试信息: {data}")
```

---

## 📚 参考的插件源码

### 1. KroMiose 发布的高级插件

#### magic-draw (高级绘图)
- **GitHub**: https://github.com/KroMiose/nekro-plugin-magic-draw
- **特点**: 策略模式、多策略实现、复杂后处理
- **学习点**: 策略模式、图像处理、配置管理

#### 内置插件分析

**emotion (表情包)**
- 功能: 向量搜索、语义匹配、图片收藏
- 技术: Qdrant 向量数据库、嵌入生成

**timer (定时器)**
- 功能: 定时任务、延迟执行
- 技术: 异步调度、事件系统

**github (GitHub 集成)**
- 功能: 仓库分析、PR/Issue 管理
- 技术: GitHub API、异步请求

**basic (基础交互)**
- 功能: 消息发送、文件传输、防刷屏
- 技术: 消息服务、文件操作

---

## 🎓 学习路径建议

### 初学者 (1周)
1. 完成官方快速上手教程
2. 创建一个 Hello World 插件
3. 理解 SandboxMethodType
4. 实现一个简单工具插件

### 进阶者 (2周)
1. 学习配置和存储系统
2. 掌握 AgentCtx 完整使用
3. 实现一个中等复杂度插件
4. 阅读 3-5 个内置插件源码

### 高级者 (1个月+)
1. 学习高级功能 (动态路由、向量数据库)
2. 开发复杂插件系统
3. 参与文档维护
4. 贡献开源插件

---

## 🚀 行动计划

### 短期目标 (今天)
- [x] 完成核心概念学习 ✅
- [x] 分析 magic-draw 插件 ✅
- [x] 创建详细学习笔记 ✅

### 中期目标 (本周)
- [ ] 完成高级功能文档阅读
- [ ] 克隆并分析 3 个内置插件
- [ ] 开发一个练手插件
- [ ] 开始阅读系统 API 文档

### 长期目标 (本月)
- [ ] 100% 掌握插件开发
- [ ] 能独立维护文档站
- [ ] 为 nekro-agent 贡献代码
- [ ] 开发 1-2 个高质量插件

---

## 📖 关键资源链接

### 官方文档
- 插件开发首页: https://doc.nekro.ai/docs/04_plugin_dev/intro.html
- 快速上手: https://doc.nekro.ai/docs/04_plugin_dev/01_quick_start.html
- 核心概念: https://doc.nekro.ai/docs/04_plugin_dev/02_plugin_basics.html
- 高级功能: https://doc.nekro.ai/docs/04_plugin_dev/03_advanced_features.html

### 代码资源
- 插件模板: /Users/clawd/clawd/nekro-plugin-template/
- 内置插件: /Users/clawd/clawd/nekro-agent/plugins/builtin/
- magic-draw: /Users/clawd/clawd/nekro-plugin-magic-draw/

### 社区
- 插件市场: https://community.nekro.ai/plugins.html
- 交流群: 636925153
- GitHub: https://github.com/KroMiose/nekro-agent

---

*总结创建时间: 2026-01-29 15:30*
*下一步: 继续学习高级功能文档*
