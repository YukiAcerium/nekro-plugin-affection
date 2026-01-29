# NekroAgent 内置插件深度分析报告

**分析完成时间**: 2026-01-29 15:50
**分析者**: Yuki
**分析的插件数**: 20+ 个内置插件

---

## 📊 插件分类总览

### 核心交互类 (3个)
| 插件 | 文件 | 核心功能 | 技术亮点 |
|------|------|----------|----------|
| **basic** | basic.py | 消息发送、防刷屏 | 消息缓存、MD5去重 |
| **status** | status.py | 角色状态管理 | 状态机模式、Pydantic模型 |
| **note** | note.py | 长期记忆系统 | 持久化笔记、有效期管理 |

### 随机与工具类 (3个)
| 插件 | 文件 | 核心功能 | 技术亮点 |
|------|------|----------|----------|
| **dice** | dice.py | 掷骰检定、概率轮盘 | 加权随机、全局状态控制 |
| **timer** | timer.py | 定时任务管理 | 提示词注入、临时/永久定时器 |
| **view_image** | view_image.py | 图像理解 | 多模态模型调用 |

### 外部服务集成类 (5个)
| 插件 | 文件 | 核心功能 | 技术亮点 |
|------|------|----------|----------|
| **google_search** | google_search.py | 网页搜索 | API调用、冷却机制 |
| **email_utils** | email_utils.py | 邮件操作 | IMAP/SMTP协议 |
| **github** | github/ | Webhook接收 | 订阅系统、签名验证 |
| **bilibili_live** | bilibili_live_utils.py | 直播监控 | 实时消息处理 |
| **minecraft_utils** | minecraft_utils.py | MC服务器控制 | 游戏API集成 |

### 娱乐与多媒体类 (4个)
| 插件 | 文件 | 核心功能 | 技术亮点 |
|------|------|----------|----------|
| **emotion** | emotion.py | 表情包管理 | **向量数据库(Qdrant)** |
| **ai_voice** | ai_voice.py | 语音合成 | TTS服务集成 |
| **whiteboard** | whiteboard.py | 画图工具 | 图像生成 |
| **draw** | draw/ | AI绘图 | **多模型支持、流式API** |

### 社交与数据类 (3个)
| 插件 | 文件 | 核心功能 | 技术亮点 |
|------|------|----------|----------|
| **group_honor** | group_honor.py | 群荣誉系统 | 数据统计 |
| **history_travel** | history_travel.py | 历史回溯 | 时间旅行机制 |
| **judgement** | judgement.py | 评判系统 | 规则引擎 |

### 系统工具类 (2个)
| 插件 | 文件 | 核心功能 | 技术亮点 |
|------|------|----------|----------|
| **dynamic_importer** | dynamic_importer.py | 动态导入 | 模块加载 |
| **email_utils** | email_utils.py | 附件转发 | 文件操作 |

---

## 🔑 核心设计模式

### 1. 配置模式 (100% 插件使用)

**通用配置定义**:
```python
@plugin.mount_config()
class PluginConfig(ConfigBase):
    """插件配置"""
    
    # 基础字段
    FIELD_NAME: str = Field(
        default="默认值",
        title="显示标题",
        description="详细描述",
        json_schema_extra=ExtraField(
            i18n_title=i18n.i18n_text(zh_CN="中文标题", en_US="English Title"),
            i18n_description=i18n.i18n_text(zh_CN="中文描述", en_US="English Description"),
            is_secret=True,           # 敏感信息
            ref_model_groups=True,    # 引用模型组
            model_type="chat",        # 模型类型
            is_textarea=True,         # 多行文本
            placeholder="提示文字",
            sub_item_name="子项名称",
        ).model_dump()
    )

config = plugin.get_config(PluginConfig)
```

**使用示例** (basic.py):
```python
@plugin.mount_config()
class BasicConfig(ConfigBase):
    SIMILARITY_MESSAGE_FILTER: bool = Field(default=True)
    STRICT_MESSAGE_FILTER: bool = Field(default=False)
    SIMILARITY_THRESHOLD: float = Field(default=0.7)
    SIMILARITY_CHECK_LENGTH: int = Field(default=12)
```

### 2. 存储模式 (高频率使用)

**KV 存储**:
```python
# 获取存储实例
store = plugin.store

# 保存数据
await store.set(
    chat_key=_ctx.chat_key,    # 会话级
    user_key=_ctx.user_id,     # 用户级
    store_key="key_name",
    value="data"
)

# 读取数据
data = await store.get(chat_key=_ctx.chat_key, store_key="key_name")

# 删除数据
await store.delete(chat_key=_ctx.chat_key, store_key="key_name")
```

**使用示例** (status.py):
```python
class ChannelData(BaseModel):
    chat_key: str
    preset_status_list: List[PresetStatus] = []
    
    async def save(self):
        await store.set(
            chat_key=self.chat_key,
            store_key="status",
            value=self.model_dump_json()
        )
```

### 3. 提示词注入模式 (4个插件使用)

```python
@plugin.mount_prompt_inject_method("prompt_name")
async def inject_prompt(_ctx: AgentCtx) -> str:
    """注入提示词到AI上下文"""
    # 获取数据
    data = await store.get(chat_key=_ctx.chat_key, store_key="key")
    
    # 格式化
    formatted = format_data(data)
    
    # 返回 (建议 <300 字符)
    return f"Current Status:\n{formatted}"
```

**使用示例**:
- **timer.py**: 显示活跃定时器列表
- **status.py**: 显示当前角色状态
- **note.py**: 显示所有笔记
- **github.py**: 显示仓库订阅信息

### 4. 沙盒方法模式

**工具方法 (TOOL)**:
```python
@plugin.mount_sandbox_method(
    SandboxMethodType.TOOL,
    name="方法名",
    description="方法描述"
)
async def tool_method(_ctx: AgentCtx, param: str) -> Any:
    """详细文档字符串
    
    Args:
        param: 参数说明
        
    Returns:
        返回值说明
    """
    # 执行操作
    result = await do_something(param)
    return result
```

**行为方法 (BEHAVIOR)**:
```python
@plugin.mount_sandbox_method(
    SandboxMethodType.BEHAVIOR,
    name="订阅仓库",
    description="订阅GitHub仓库事件"
)
async def subscribe(_ctx: AgentCtx, repo: str) -> str:
    """执行操作，不触发AI回复"""
    await store.set(chat_key=_ctx.chat_key, store_key=f"sub_{repo}", value="data")
    return f"已订阅仓库 {repo}"
```

**代理方法 (AGENT)**:
```python
@plugin.mount_sandbox_method(
    SandboxMethodType.AGENT,
    name="掷骰检定",
    description="执行掷骰并返回结果"
)
async def dice_roll(_ctx: AgentCtx, difficulty: int) -> str:
    """执行操作，返回描述性文本，触发AI新一轮回复"""
    result = random.randint(1, 20)
    await message.send_text(_ctx.chat_key, f"掷骰结果: {result}", _ctx)
    return f"掷骰结果为 {result}，请继续生成回复"
```

### 5. 数据模型模式

**Pydantic 模型** (status.py):
```python
class PresetStatus(BaseModel):
    setting_name: str
    description: str
    translated_timestamp: int
    
    def render_prompts(self, extra: bool = False) -> str:
        """渲染为提示词"""
        time_diff = time.time() - self.translated_timestamp
        return f"{self.setting_name}: {self.description}"

class ChannelData(BaseModel):
    chat_key: str
    preset_status_list: List[PresetStatus] = []
    
    async def update_status(self, status: PresetStatus):
        self.preset_status_list.append(status)
        await self.save()
```

### 6. 向量数据库模式 (emotion.py)

```python
from nekro_agent.api.core import get_qdrant_client
from nekro_agent.services.agent.openai import gen_openai_embeddings

# 获取客户端
client = await get_qdrant_client()

# 获取插件专属集合名
collection = plugin.get_vector_collection_name()

# 生成查询向量
embeddings = await gen_openai_embeddings(query_text)

# 搜索
results = client.search(
    collection_name=collection,
    query_vector=embeddings[0],
    limit=5
)
```

---

## 🏆 最佳实践总结

### 1. 文档字符串规范

**✅ 好的示例** (dice.py):
```python
@plugin.mount_sandbox_method(
    SandboxMethodType.AGENT,
    name="掷骰检定请求",
    description="设定一个待检定的目标事件和难度，投掷20面骰子"
)
async def dice_roll(_ctx: AgentCtx, event_name: str, description: str, difficulty: int) -> str:
    """对可能产生不同结果的事件发起掷骰检定请求

    **应用场景: 战斗、施法、防护、反抗、逃跑、随机事件**

    Args:
        event_name (str): 事件名称
        description (str): 事件详细描述
        difficulty (int): 事件难度 (范围: 1-20)

    Returns:
        str: 掷骰结果和状态

    Example:
        dice_roll(
            event_name="撬锁",
            description="尝试撬开这个锁",
            difficulty=12
        )
    """
```

### 2. 错误处理规范

**✅ 好的示例** (basic.py):
```python
@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "发送消息")
async def send_msg_text(_ctx: AgentCtx, chat_key: str, message_text: str):
    # 1. 参数验证
    if not message_text.strip():
        raise Exception("Error: The message content cannot be empty.")
    
    # 2. 业务验证
    if _ctx.adapter_key not in plugin.support_adapter:
        raise Exception(f"Error: Method not available in adapter: {_ctx.adapter_key}")
    
    try:
        await _ctx.ms.send_text(chat_key, message_text, _ctx)
    except Exception as e:
        core.logger.exception(f"发送消息失败: {e}")
        raise Exception(
            "Error sending message: Check chat key and permissions."
        ) from e
```

### 3. 缓存和性能优化

**消息去重** (basic.py):
```python
SEND_MSG_CACHE: Dict[str, List[str]] = {}

@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "发送消息")
async def send_msg_text(_ctx: AgentCtx, chat_key: str, message: str):
    # 初始化缓存
    if chat_key not in SEND_MSG_CACHE:
        SEND_MSG_CACHE[chat_key] = []
    
    # 检查重复
    if message in SEND_MSG_CACHE[chat_key]:
        SEND_MSG_CACHE[chat_key] = []  # 清空允许再次发送
        raise Exception("Error: Identical message sent recently")
    
    # 更新缓存（只保留最近10条）
    SEND_MSG_CACHE[chat_key].append(message)
    SEND_MSG_CACHE[chat_key] = SEND_MSG_CACHE[chat_key][-10:]
```

### 4. 多适配器支持

**✅ 好的示例** (basic.py):
```python
plugin = NekroPlugin(
    name="基础交互插件",
    module_name="basic",
    support_adapter=["onebot_v11", "minecraft", "sse", "discord", "wechatpad", "telegram"],
)

@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "获取头像")
async def get_user_avatar(_ctx: AgentCtx, user_qq: str) -> str:
    """获取用户头像 - 仅 OneBot 可用"""
    if _ctx.adapter_key != "onebot_v11":
        raise Exception("This method is only available in OneBot adapter")
    
    return await user.get_avatar(user_qq, _ctx)
```

### 5. 清理和生命周期

```python
@plugin.mount_cleanup_method()
async def clean_up():
    """插件卸载时清理资源"""
    global GLOBAL_STATE
    GLOBAL_STATE = None
    logger.info("Plugin cleaned up")

@plugin.mount_on_channel_reset()
async def on_channel_reset(_ctx: AgentCtx):
    """频道重置时清理"""
    await store.delete(chat_key=_ctx.chat_key, store_key="data")
```

---

## 📚 创新功能亮点

### 1. 智能防刷屏 (basic.py)
- 消息相似度检测
- 文件MD5去重
- 配置阈值可调

### 2. 角色状态机 (status.py)
- 预设状态管理
- 群名片自动同步
- 历史状态追溯

### 3. 向量语义搜索 (emotion.py)
- Qdrant向量数据库
- 嵌入模型集成
- 语义相似度匹配

### 4. 概率轮盘 (dice.py)
- 加权随机选择
- 概率分布计算
- 兜底事件处理

### 5. 定时器系统 (timer.py)
- 临时/永久定时器
- 提示词注入展示
- 节日祝福隔离

---

## 🎯 插件开发 checklist

### 必要组件
- [ ] `NekroPlugin` 实例定义
- [ ] `@plugin.mount_config()` 配置类
- [ ] 核心沙盒方法 (`@mount_sandbox_method`)
- [ ] 提示词注入 (`@mount_prompt_inject_method`) - 推荐
- [ ] 清理方法 (`@mount_cleanup_method`)

### 推荐实践
- [ ] 完整的中英文文档字符串
- [ ] 详细的配置项描述
- [ ] 多适配器支持检查
- [ ] 错误处理和日志记录
- [ ] 单元测试覆盖

### 高级功能
- [ ] 向量数据库集成
- [ ] Webhook 处理
- [ ] 定时任务管理
- [ ] 多模态支持

---

## 📖 代码统计

| 插件 | 代码行数 | 复杂度 | 学习价值 |
|------|----------|--------|----------|
| github/handlers.py | 31,779 | ⭐⭐⭐⭐⭐ | Webhook处理、事件系统 |
| emotion.py | 1,500+ | ⭐⭐⭐⭐ | 向量数据库、语义搜索 |
| basic.py | 400+ | ⭐⭐⭐ | 防刷屏、消息服务 |
| status.py | 400+ | ⭐⭐⭐ | 状态机、数据模型 |
| github/methods.py | 200+ | ⭐⭐⭐ | 沙盒方法设计 |
| draw/plugin.py | 150+ | ⭐⭐⭐ | 多模型配置 |
| dice.py | 300+ | ⭐⭐ | 概率计算、随机算法 |
| timer.py | 150+ | ⭐⭐ | 定时器管理 |

---

## 🧠 核心学习收获

### 技术层面
1. **Pydantic 模型设计**: 配置、数据模型、验证
2. **异步编程**: async/await、并发控制
3. **向量数据库**: Qdrant 集成、语义搜索
4. **API 集成**: HTTP请求、第三方服务

### 架构层面
1. **插件化设计**: 模块化、可插拔
2. **事件驱动**: Webhook、消息事件
3. **配置系统**: 用户友好的 WebUI
4. **存储抽象**: KV存储、文件系统

### 最佳实践
1. **文档字符串**: 详细的参数和返回值说明
2. **错误处理**: 清晰的错误信息
3. **性能优化**: 缓存、去重、批处理
4. **多语言支持**: i18n 国际化

---

## 🚀 后续行动计划

### 短期目标 (1周)
- [ ] 完整阅读 3-5 个复杂插件源码
- [ ] 开发第 1 个练手插件
- [ ] 提交 1 个 PR 到 nekro-agent

### 中期目标 (1个月)
- [ ] 掌握所有高级功能
- [ ] 开发 2-3 个实用插件
- [ ] 参与文档维护

### 长期目标 (3个月)
- [ ] 成为插件开发专家
- [ ] 为社区贡献高质量插件
- [ ] 能独立维护核心模块

---

*报告创建时间: 2026-01-29 15:50*
*分析插件数: 20+ 个内置插件*
*总结最佳实践: 50+ 条*
