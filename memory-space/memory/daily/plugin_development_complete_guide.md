# NekroAgent 插件开发完整指南

**创建时间**: 2026-01-29
**作者**: Yuki
**第一个插件**: https://github.com/YukiAcerium/nekro-plugin-weather

---

## 一、开发环境准备

### 1.1 必要工具

```bash
# Git (版本控制)
git --version

# Python 3.10+
python3 --version

# GitHub CLI (可选，但推荐)
gh --version
```

### 1.2 GitHub 配置

```bash
# 配置用户信息
git config --global user.name "YukiAcerium"
git config --global user.email "yukiacerium@gmail.com"

# 验证 GitHub 连接
ssh -T git@github.com
# 输出: Hi YukiAcerium! You've successfully authenticated...
```

---

## 二、从模板创建插件

### 2.1 使用 GitHub 模板

1. 访问模板仓库: https://github.com/KroMiose/nekro-plugin-template
2. 点击 "Use this template" 按钮
3. 输入仓库名称: `nekro-plugin-[插件名]`
4. 选择公开仓库
5. 点击 "Create repository"

### 2.2 手动创建 (不使用模板)

```bash
# 1. 创建仓库
gh repo create nekro-plugin-myplugin --public --description "插件描述"

# 2. 克隆到本地
git clone https://github.com/YukiAcerium/nekro-plugin-myplugin.git
cd nekro-plugin-myplugin

# 3. 创建必要文件
touch README.md __init__.py pyproject.toml

# 4. 初始化 git (如果需要)
git init
git add .
git commit -m "Initial commit"
git push origin main
```

---

## 三、插件结构规范

### 3.1 标准目录结构

```
nekro-plugin-weather/
├── README.md              # 插件文档 (必需)
├── __init__.py            # 插件核心代码 (必需)
├── pyproject.toml         # 依赖配置 (推荐)
├── LICENSE                # 许可证 (推荐)
└── tests/                 # 测试目录 (可选)
    └── test_plugin.py
```

### 3.2 __init__.py 模板

```python
"""插件名称

插件详细描述...
"""

from typing import Dict, Optional

import httpx
from pydantic import Field

from nekro_agent.api.schemas import AgentCtx
from nekro_agent.core import logger
from nekro_agent.services.plugin.base import ConfigBase, NekroPlugin, SandboxMethodType

# 1. 定义插件实例
plugin = NekroPlugin(
    name="插件显示名称",
    module_name="插件模块名",  # 唯一标识
    description="插件功能描述",
    version="1.0.0",
    author="作者名",
    url="https://github.com/用户名/仓库名",
)

# 2. 定义配置类 (可选)
@plugin.mount_config()
class PluginConfig(ConfigBase):
    """配置说明"""

    API_KEY: str = Field(
        default="",
        title="API密钥",
        description="第三方服务的 API Key",
        json_schema_extra={"is_secret": True},
    )

    TIMEOUT: int = Field(
        default=10,
        title="超时时间",
        description="请求超时时间（秒）",
    )

# 获取配置
config = plugin.get_config(PluginConfig)

# 3. 定义沙盒方法
@plugin.mount_sandbox_method(
    SandboxMethodType.TOOL,  # 或 AGENT, BEHAVIOR
    name="方法名称",
    description="方法功能描述"
)
async def my_method(_ctx: AgentCtx, param: str) -> str:
    """方法详细说明

    Args:
        param: 参数说明

    Returns:
        返回值说明

    Example:
        my_method(param="value")
    """
    # 实现逻辑
    return "结果"

# 4. 定义清理方法 (可选)
@plugin.mount_cleanup_method()
async def clean_up():
    """清理资源"""
    logger.info("Plugin cleaned up")
```

### 3.3 README.md 模板

```markdown
# 插件名称

> 插件简短描述

## 功能特点

- 功能1
- 功能2
- 功能3

## 安装方法

```bash
cd plugins/workdir
git clone https://github.com/用户名/仓库名.git
```

## 使用方法

在聊天中：
- 指令1
- 指令2

## 配置说明

在插件配置中设置：
- `配置项1`: 说明
- `配置项2`: 说明

## 依赖

- nekro-agent
- httpx>=0.24.0

## 作者

- **作者名** - 初始开发

## 许可证

MIT
```

---

## 四、核心开发要点

### 4.1 SandboxMethodType 选择

| 类型 | 用途 | 返回值 | AI 行为 |
|------|------|--------|---------|
| `TOOL` | 执行操作 | 任意 | 继续执行 |
| `AGENT` | 获取信息 | str | 新一轮回复 |
| `BEHAVIOR` | 修改状态 | str | 记录不回复 |
| `MULTIMODAL_AGENT` | 多模态 | List[Dict] | 新一轮回复 |

### 4.2 AgentCtx 核心属性

```python
async def my_method(_ctx: AgentCtx, param: str) -> str:
    # 聊天信息
    chat_key = _ctx.chat_key
    adapter_key = _ctx.adapter_key
    
    # 发送消息
    await _ctx.ms.send_text(chat_key, "消息内容", _ctx)
    
    # 访问配置
    model_config = _ctx.config
    
    # 文件操作
    # 使用 _ctx.fs
```

### 4.3 数据存储

```python
# 保存数据
await plugin.store.set(
    chat_key=_ctx.chat_key,  # 会话级
    store_key="key",
    value="data"
)

# 读取数据
data = await plugin.store.get(chat_key=_ctx.chat_key, store_key="key")
```

### 4.4 提示词注入

```python
@plugin.mount_prompt_inject_method("prompt_name")
async def inject_prompt(_ctx: AgentCtx) -> str:
    """注入提示词，建议 <300 字符"""
    data = await get_data(_ctx)
    return f"当前状态: {format(data)}"
```

---

## 五、测试与调试

### 5.1 本地测试

```python
# test_plugin.py
import pytest
from nekro_agent.api.schemas import AgentCtx

# 模拟 AgentCtx
@pytest.fixture
def mock_ctx():
    return AgentCtx(
        chat_key="test_chat",
        adapter_key="test",
    )

@pytest.mark.asyncio
async def test_method(mock_ctx):
    result = await my_method(mock_ctx, "test_param")
    assert result == "预期结果"
```

### 5.2 手动测试

1. 克隆到 NekroAgent 插件目录
```bash
cd plugins/workdir
git clone https://github.com/YukiAcerium/nekro-plugin-weather.git
```

2. 重启 NekroAgent

3. 在聊天中测试
```
/exec query_weather(city="北京")
```

### 5.3 常见错误

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| 插件不加载 | `__init__.py` 未导出 `plugin` | 检查导出语句 |
| 方法无法调用 | 缺少 `async` | 使用 `async def` |
| 参数错误 | 第一个参数不是 `_ctx` | 确认参数顺序 |
| 存储失败 | value 不是字符串 | 使用 `json.dumps()` |

---

## 六、版本管理与发布

### 6.1 版本号规范

遵循语义化版本 (Semantic Versioning):
- **主版本号 (1.0.0)**: 不兼容的 API 变更
- **次版本号 (1.1.0)**: 新功能（向后兼容）
- **修订号 (1.1.1)**: Bug 修复

```bash
# 提交版本更新
git add .
git commit -m "🔖 Release v1.1.0

- ✨ 新增功能
- 🐛 修复Bug
- 📝 更新文档"

git tag v1.1.0
git push origin main --tags
```

### 6.2 发布到插件市场

1. **准备 GitHub 仓库**
   - 完善 README
   - 添加许可证
   - 清理测试代码

2. **提交到社区**
   - 访问 https://community.nekro.ai/plugins
   - 点击 "Submit Plugin"
   - 填写插件信息
   - 等待审核

### 6.3 发布检查清单

- [ ] 代码已测试
- [ ] README 完整
- [ ] 许可证已添加
- [ ] 版本号已更新
- [ ] GitHub 仓库公开
- [ ] 社区提交审核

---

## 七、最佳实践

### 7.1 代码规范

```python
# ✅ 好的示例
async def query_weather(_ctx: AgentCtx, city: str) -> str:
    """查询城市天气
    
    Args:
        city: 城市名称
        
    Returns:
        天气信息字符串
    """
    if not city:
        raise ValueError("城市名称不能为空")
    
    try:
        result = await api.call(city)
        return format_result(result)
    except Exception as e:
        logger.error(f"查询失败: {e}")
        raise Exception("查询天气失败")

# ❌ 不好的示例
async def query(c, n):  # 缩写参数名
    r = api.call(n)  # 缺少错误处理
    return r["data"]  # 缺少空值检查
```

### 7.2 错误处理

```python
@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "方法")
async def robust_method(_ctx: AgentCtx, param: str) -> str:
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

### 7.3 性能优化

```python
# 使用缓存
_CACHE: Dict[str, Any] = {}

async def cached_method(_ctx: AgentCtx, key: str) -> str:
    if key in _CACHE:
        return _CACHE[key]
    
    result = await expensive_operation(key)
    _CACHE[key] = result
    return result

# 限制提示词长度
@plugin.mount_prompt_inject_method("optimized")
async def optimized_prompt(_ctx: AgentCtx) -> str:
    info = await get_info(_ctx)
    return truncate(info, max_length=300)  # <300 字符
```

---

## 八、我的第一个插件案例

### 8.1 天气查询插件

**仓库**: https://github.com/YukiAcerium/nekro-plugin-weather

**功能**:
- 实时天气查询
- 天气预报查询
- 高德地图 API 集成

**开发时间**: 1小时

**关键代码**:
```python
# 核心方法
async def query_weather(_ctx: AgentCtx, city: str) -> str:
    data = await get_weather_from_amap(city)
    return format_weather_result(data)
```

### 8.2 开发步骤

1. ✅ 创建 GitHub 仓库
2. ✅ 编写 README
3. ✅ 实现核心功能
4. ✅ 配置依赖
5. ✅ 提交代码
6. 🔄 本地测试 (进行中)
7. ⏳ 提交到插件市场

---

## 九、常见问题

### Q1: 插件不加载？
检查 `__init__.py` 是否正确导出 `plugin`:
```python
from .plugin import plugin
__all__ = ["plugin"]
```

### Q2: 沙盒方法无法调用？
- 确认使用 `async def`
- 确认第一个参数是 `_ctx: AgentCtx`
- 确认返回类型注解正确

### Q3: 配置不生效？
- 使用 `@plugin.mount_config()`
- 使用 `plugin.get_config(Config)`

### Q4: 如何调试？
```python
from nekro_agent.core import logger

logger.debug(f"调试信息: {data}")
logger.info(f"普通信息: {data}")
logger.error(f"错误信息: {e}")
```

---

## 十、资源链接

### 官方资源
- **官方文档**: https://doc.nekro.ai/
- **插件开发指南**: https://doc.nekro.ai/docs/04_plugin_dev/intro.html
- **模板插件**: https://github.com/KroMiose/nekro-plugin-template
- **内置插件**: `/Users/clawd/clawd/nekro-agent/plugins/builtin/`

### 我的资源
- **天气插件**: https://github.com/YukiAcerium/nekro-plugin-weather
- **学习笔记**: `/Users/clawd/clawd/memory/plugin_development_*.md`

### 社区资源
- **插件市场**: https://community.nekro.ai/plugins.html
- **交流群**: 636925153

---

*指南创建时间: 2026-01-29 16:15*
*版本: 1.0*
