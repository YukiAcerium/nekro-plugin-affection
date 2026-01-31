# 插件开发深度学习笔记

**学习日期**: 2026-01-29
**学习者**: Yuki
**目标**: 100% 掌握插件开发，达到维护文档站水平

---

## 📚 第一阶段：插件市场调研

### 调研的插件

#### 1. 高级绘图插件 (magic-draw) ⭐
- **作者**: KroMiose
- **GitHub**: https://github.com/KroMiose/nekro-plugin-magic-draw
- **功能**: 
  - GIF 动画生成
  - 透明背景 PNG 生成
  - 角色概念设定图生成

**技术特点**:
- 使用策略模式 (Strategy Pattern)
- 多个独立的生成策略
- 复杂的图像后处理流程
- 详细的配置选项

**核心代码结构**:
```
nekro-plugin-magic-draw/
├── __init__.py              # 导出 plugin 实例
├── plugin.py                # 插件定义和配置
├── strategies/              # 策略实现
│   ├── __init__.py
│   ├── base.py             # 策略基类
│   ├── gif_generator.py     # GIF 生成策略
│   ├── transparent_png_generator.py  # 透明 PNG 策略
│   └── costume_design_generator.py   # 角色设计策略
└── utils.py                # 工具函数
```

**关键实现**:
```python
# 策略注册表
STRATEGIES: Dict[str, Type[DrawingStrategy]] = {
    "gif_generation": GifGenerationStrategy,
    "transparent_png": TransparentPngStrategy,
    "costume_design": CostumeDesignStrategy,
}

# 主入口方法
@plugin.mount_sandbox_method(
    SandboxMethodType.TOOL,
    name="高级绘图魔法",
    description="执行高级绘图任务..."
)
async def magic_draw(_ctx: AgentCtx, strategy_name: str, **kwargs) -> str:
    # 策略模式执行
    strategy = STRATEGIES[strategy_name](config)
    result = await strategy.execute(_ctx, **kwargs)
    return result

# 提示词注入
@plugin.mount_prompt_inject_method("inject_magic_draw_strategies")
async def inject_strategies(_ctx: AgentCtx) -> str:
    # 向 AI 注入策略说明
    return "## 高级绘图插件可用功能\n..."
```

---

## 📖 第二阶段：官方文档学习

### 2.1 插件核心概念

#### 什么是插件？
Nekro Agent 插件是扩展核心功能的方式，通过 `NekroPlugin` 类定义和注册。

**插件能做什么**:
1. **增强 AI 能力**: 专业领域知识库、复杂计算、第三方 API 集成
2. **执行具体动作**: 发送消息/邮件、管理定时任务、控制智能家居
3. **与外部系统交互**: Web API 接入、数据同步、文件传输
4. **个性化用户体验**: 定制化内容、独特交互方式、语义搜索

#### 插件系统架构

```
┌─────────────────────────────────────────────┐
│              Nekro Agent Core               │
│  ┌─────────────────────────────────────┐│
│  │          插件注册 (NekroPlugin)        ││
│  └─────────────────────────────────────┘│
│  ┌─────────────────────────────────────┐│
│  │          事件驱动系统                ││
│  └─────────────────────────────────────┘│
│  ┌─────────────────────────────────────┐│
│  │          API 交互层                  ││
│  │  (消息发送、数据存储、配置管理)        ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────────┘
          ▲                    │
          │ RPC              │ 沙盒执行
          ▼                    ▼
┌─────────────────────────────────────────────┐
│              Plugin (独立进程/模块)           │
│  ┌─────────────────────────────────────┐│
│  │          沙盒方法定义                ││
│  └─────────────────────────────────────┘│
│  ┌─────────────────────────────────────┐│
│  │          配置与存储                  ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────────┘
```

#### 2.2 快速上手示例

**Hello Plugin 完整实现**:

```python
# hello_plugin/__init__.py
from .plugin import plugin
__all__ = ["plugin"]

# hello_plugin/plugin.py
from nekro_agent.api.plugin import NekroPlugin, SandboxMethodType
from nekro_agent.api.schemas import AgentCtx

plugin = NekroPlugin(
    name="你好插件",
    module_name="hello_plugin",
    description="一个简单的 Hello World 插件示例。",
    author="你的名字",
    version="0.1.0",
    url="https://your.plugin.repo.url"
)

@plugin.mount_sandbox_method(
    method_type=SandboxMethodType.TOOL,
    name="say_hello",
    description="返回一个问候语。"
)
async def say_hello_from_plugin(_ctx: AgentCtx) -> str:
    """插件的问候方法
    
    Returns:
        str: "Hello from Plugin!"
    """
    return "Hello from Plugin!"
```

#### 2.3 沙盒方法详解

**SandboxMethodType 类型**:

| 类型 | 用途 | 返回值 | AI 后续行为 |
|------|------|--------|------------|
| **TOOL** | 直接执行操作 | 简短确认 | 继续对话 |
| **AGENT** | 获取信息分析 | 详细内容 | 分析后回复 |
| **BEHAVIOR** | 修改状态 | 操作确认 | 考虑新状态 |
| **MULTIMODAL_AGENT** | 多媒体分析 | OpenAI 格式 | 观察后分析 |

**使用规范**:
```python
# ✅ TOOL - 执行操作
@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "发送消息")
async def send_message(_ctx: AgentCtx, content: str) -> str:
    await _ctx.ms.send_text(_ctx.chat_key, content, _ctx)
    return "消息已发送"

# ✅ AGENT - 获取信息
@plugin.mount_sandbox_method(SandboxMethodType.AGENT, "搜索")
async def search_info(_ctx: AgentCtx, query: str) -> str:
    results = await external_search(query)
    return f"搜索结果：{results}\n请分析并回答"

# ❌ 错误用法：用 AGENT 执行操作
@plugin.mount_sandbox_method(SandboxMethodType.AGENT, "发送消息")
async def bad_send(_ctx: AgentCtx, content: str) -> str:
    await _ctx.ms.send_text(_ctx.chat_key, content, _ctx)
    return "已发送"  # AGENT 不应该直接执行操作
```

#### 2.4 插件配置

```python
from nekro_agent.api.plugin import ConfigBase, ExtraField, NekroPlugin
from pydantic import Field

@plugin.mount_config()
class MagicDrawConfig(ConfigBase):
    """高级绘图插件配置"""
    
    BASIC_MODEL_GROUP: str = Field(
        default="default-chat",
        title="基础绘图模型组",
        description="用于辅助绘图任务的模型组",
        json_schema_extra=ExtraField(
            ref_model_groups=True,  # 引用模型组
            model_type="draw"       # 模型类型
        ).model_dump()
    )
    
    ADVANCED_MODEL_GROUP: str = Field(
        default="default-chat",
        title="高级绘图模型组",
        description="用于复杂绘图任务的模型组"
    )
    
    STREAM_MODE: bool = Field(
        default=True,
        title="使用流式 API",
        description="启用流式模式避免超时"
    )
    
    TIMEOUT: int = Field(
        default=300,
        title="请求超时时间",
        description="单位：秒"
    )

config = plugin.get_config(MagicDrawConfig)
```

#### 2.5 数据存储

```python
@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "保存数据")
async def save_data(_ctx: AgentCtx, key: str, value: str) -> bool:
    # 保存到当前聊天会话
    await plugin.store.set(
        chat_key=_ctx.chat_key,
        store_key=key,
        value=value
    )
    return True

@plugin.mount_sandbox_method(SandboxMethodType.AGENT, "读取数据")
async def read_data(_ctx: AgentCtx, key: str) -> str:
    # 从当前聊天会话读取
    data = await plugin.store.get(
        chat_key=_ctx.chat_key,
        store_key=key
    )
    return f"读取到的数据：{data}"

# 全局存储（不指定 chat_key）
await plugin.store.set(store_key="global_key", value="全局数据")
```

#### 2.6 提示词注入

```python
@plugin.mount_prompt_inject_method("my_prompt_inject")
async def inject_prompt(_ctx: AgentCtx) -> str:
    """向 AI 注入提示词
    
    Returns:
        str: 注入到系统提示词的内容
    """
    # 获取当前状态
    state = await get_state(_ctx)
    
    if not state:
        return ""  # 无状态时返回空
    
    # 格式化注入内容（建议 <300 字符）
    return f"当前状态:\n{state.render_summary()}"

@plugin.mount_cleanup_method()
async def clean_up():
    """清理插件资源"""
    logger.info("插件资源已清理")
```

#### 2.7 AgentCtx 上下文对象

```python
async def example_method(_ctx: AgentCtx, param: str) -> str:
    # _ctx 包含以下核心属性：
    
    # 1. 聊天上下文
    _ctx.chat_key           # 聊天频道标识
    _ctx.chat_type         # 聊天类型 (group/private)
    _ctx.adapter_key       # 适配器类型
    
    # 2. 消息服务
    _ctx.ms.send_text(chat_key, message, _ctx)
    _ctx.ms.send_image(chat_key, image_path, _ctx)
    _ctx.ms.send_file(chat_key, file_path, _ctx)
    
    # 3. 文件系统
    _ctx.fs.upload(path)           # 上传文件
    _ctx.fs.download(url)         # 下载文件
    
    # 4. 配置访问
    config = _ctx.config         # 全局配置
    adapter_config = _ctx.adapter_config  # 适配器配置
    
    # 5. 适配器功能
    if _ctx.adapter_key == "onebot_v11":
        # OneBot 特定功能
        pass
```

---

## 🔧 第三阶段：源码深度分析

### magic-draw 插件源码分析

#### 1. 策略模式实现

```python
# strategies/base.py
class DrawingStrategy(ABC):
    """绘图策略基类"""
    
    def __init__(self, config: MagicDrawConfig):
        self.config = config
    
    @abstractmethod
    async def execute(self, ctx: AgentCtx, **kwargs) -> str:
        """执行绘图任务
        
        Returns:
            str: 生成的文件路径（沙盒路径）
        """
        pass
    
    def get_description(self) -> str:
        """获取策略描述，供 AI 参考"""
        return "策略描述..."

# strategies/gif_generator.py
class GifGenerationStrategy(DrawingStrategy):
    async def execute(self, ctx: AgentCtx, **kwargs) -> str:
        content = kwargs.get("content", "")
        style = kwargs.get("style", "pixel art")
        fps = kwargs.get("fps", self.config.GIF_DEFAULT_FPS)
        
        # 1. 生成 4x4 网格图
        prompt = self._build_gif_prompt(content, style)
        image_path = await self._generate_image(ctx, prompt)
        
        # 2. 切割为 16 帧
        frames = self._split_image(image_path)
        
        # 3. 处理边缘
        frames = self._filter_edges(frames)
        
        # 4. 生成 GIF
        gif_path = self._create_gif(frames, fps)
        
        return gif_path
```

#### 2. 配置验证

```python
# utils.py - 工具函数
def validate_content(content: str) -> bool:
    """验证绘图内容描述"""
    if len(content) < 5:
        raise ValueError("内容描述太短")
    if len(content) > 1000:
        raise ValueError("内容描述太长")
    return True

def format_gif_prompt(content: str, style: str) -> str:
    """格式化 GIF 生成提示词"""
    return f"""生成一个 {style} 风格的 GIF 动画序列。
内容：{content}
要求：
- 4x4 网格布局，共 16 帧
- 每帧之间需要平滑过渡
- 使用纯色背景（颜色：#FFFFFF）
- 画面清晰，分辨率至少 512x512
"""
```

---

## 📝 第四阶段：最佳实践总结

### 开发规范

#### 1. 文件结构
```
my_plugin/
├── __init__.py           # 必须：导出 plugin 实例
├── plugin.py             # 插件核心代码
├── pyproject.toml        # 依赖配置
└── README.md            # 插件文档
```

#### 2. 命名规范
```python
# ✅ 正确
plugin = NekroPlugin(
    name="🪄高级绘图✨",
    module_name="magic_draw",  # 与目录名一致
)

# ❌ 错误
module_name="MyPlugin"  # 与目录名不一致
```

#### 3. 错误处理
```python
@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "方法名")
async def robust_method(_ctx: AgentCtx, param: str) -> str:
    # 1. 参数验证
    if not param or not param.strip():
        raise ValueError("参数不能为空")
    
    try:
        result = await operation(param)
        return result
    except ValueError as e:
        raise ValueError(f"参数错误: {e}")
    except Exception as e:
        logger.exception("操作失败")
        raise Exception(f"执行失败: {e}")
```

#### 4. 性能优化
```python
# 1. 使用缓存
_CACHE: Dict[str, Any] = {}

async def cached_method(_ctx: AgentCtx, key: str) -> str:
    if key in _CACHE:
        return _CACHE[key]
    
    result = await expensive_operation(key)
    _CACHE[key] = result
    return result

# 2. 限制提示词长度
@plugin.mount_prompt_inject_method("optimized_prompt")
async def optimized_prompt(_ctx: AgentCtx) -> str:
    full_content = await get_state_info(_ctx)
    return truncate_content(full_content, max_length=300)  # <300 字符
```

---

## 🎯 第五阶段：学习路径

### 掌握程度自检

#### 初级 (✅ 已掌握)
- [x] 插件基本概念
- [x] 创建简单插件
- [x] 理解 NekroPlugin 定义
- [x] 实现 TOOL 类型方法
- [x] 基础配置定义

#### 中级 (🔄 学习中)
- [ ] 理解所有 SandboxMethodType
- [ ] 提示词注入机制
- [ ] 数据存储使用
- [ ] AgentCtx 完整使用
- [ ] 错误处理规范

#### 高级 (⬜ 待学习)
- [ ] 动态路由 (FastAPI)
- [ ] 文件系统交互
- [ ] 向量数据库集成
- [ ] 多模态方法
- [ ] 插件模板开发

---

## 📚 参考资源

### 官方文档
- 插件开发引言: https://doc.nekro.ai/docs/04_plugin_dev/00_introduction.html
- 快速上手: https://doc.nekro.ai/docs/04_plugin_dev/01_quick_start.html
- 插件核心概念: https://doc.nekro.ai/docs/04_plugin_dev/02_plugin_basics.html
- 高级功能: https://doc.nekro.ai/docs/04_plugin_dev/03_advanced_features.html

### 示例插件
- 高级绘图插件: https://github.com/KroMiose/nekro-plugin-magic-draw
- 插件模板: https://github.com/KroMiose/nekro-plugin-template
- 内置插件: /Users/clawd/clawd/nekro-agent/plugins/builtin/

### 社区资源
- 插件市场: https://community.nekro.ai/plugins.html
- 社区交流群: 636925153

---

## 🚀 下一步行动

### 本周目标
1. [ ] 完成所有核心概念文档阅读
2. [ ] 克隆并分析 3-5 个 KroMiose 的插件
3. [ ] 编写一个示例插件练手
4. [ ] 开始维护文档站

### 学习计划
- Day 1: 核心概念和快速上手 ✅
- Day 2: 高级功能和源码分析
- Day 3: 实践练习
- Day 4+: 参与文档维护

---

*笔记创建时间: 2026-01-29 15:15*
*最后更新: 2026-01-29 15:15*
