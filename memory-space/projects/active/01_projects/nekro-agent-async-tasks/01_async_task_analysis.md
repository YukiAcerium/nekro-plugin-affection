# 异步任务插件研究笔记

## 研究日期

2026-01-30

## 研究目标

分析 nekro-agent 预览版本的异步任务插件能力 API，补充文档站说明。

## 1. WebApp 插件异步任务实现分析

### 1.1 异步任务定义

**文件**: `nekro-plugin-webapp/__init__.py`

```python
@plugin.mount_async_task("webapp_dev")
async def _webapp_dev_task(
    handle: AsyncTaskHandle,
    requirement: str,
    webapp_task_id: str,
    existing_files: Optional[List[str]] = None,
) -> AsyncGenerator[TaskCtl, None]:
    """WebApp 开发异步任务

    通过 yield TaskCtl 报告状态，支持进度追踪和中断。
    """
```

### 1.2 关键特点

1. **异步生成器模式**: 使用 `AsyncGenerator[TaskCtl, None]`
2. **通过 yield 报告进度**: `yield TaskCtl.report_progress("🚀 开始开发...", 0)`
3. **任务控制信号**:
   - `TaskCtl.report_progress(message, percent)` - 报告进度
   - `TaskCtl.success(message, data)` - 任务成功
   - `TaskCtl.fail(message, error)` - 任务失败
   - `TaskCtl.cancel(message)` - 任务取消

4. **任务句柄 (AsyncTaskHandle)**:
   - `handle.wait(key, timeout)` - 等待外部信号
   - `handle.notify(key, data)` - 通知等待点恢复
   - `handle.notify_agent(message)` - 通知主 Agent
   - `handle.is_cancelled` - 检查是否已取消

### 1.3 任务启动与控制

```python
# 启动任务
await task.start(
    task_type="webapp_dev",
    task_id=task_id,
    chat_key=_ctx.chat_key,
    plugin=plugin,
    requirement=requirement.strip(),
    webapp_task_id=task_id,
)

# 检查任务状态
task.is_running("webapp_dev", task_id)

# 取消任务
await task.cancel("webapp_dev", task_id)

# 停止所有任务
await task.stop_all()
```

### 1.4 与主 Agent 交互

```python
# 通知主 Agent
await handle.notify_agent(
    f"✅ WebApp 部署成功! (ID: {task_id})\n📝 {desc_short}\n🔗 {url}",
)

# 实时反馈注入
state_obj = runtime_state.get_state(chat_key, task_id)
if state_obj and state_obj.inject_feedback(feedback):
    return f"⚡ 已注入反馈到任务 {task_id}"
```

---

## 2. Nekro-Agent 源码实现分析

### 2.1 核心组件

**文件**: `nekro_agent/services/plugin/task.py`

#### 2.1.1 TaskSignal (任务信号类型)

```python
class TaskSignal(str, Enum):
    PROGRESS = "progress"  # 进度更新
    SUCCESS = "success"    # 成功完成
    FAIL = "fail"          # 失败
    CANCEL = "cancel"      # 取消
```

#### 2.1.2 TaskCtl (任务控制信号)

```python
class TaskCtl(BaseModel):
    signal: TaskSignal
    message: str
    data: Optional[Any] = None
    progress: Optional[int] = Field(default=None, ge=0, le=100)

    @classmethod
    def report_progress(cls, message: str, percent: int = 0) -> "TaskCtl":
        return cls(signal=TaskSignal.PROGRESS, message=message, progress=percent)

    @classmethod
    def success(cls, message: str = "完成", data: Any = None) -> "TaskCtl":
        return cls(signal=TaskSignal.SUCCESS, message=message, data=data)

    @classmethod
    def fail(cls, message: str, error: Optional[Exception] = None) -> "TaskCtl":
        return cls(signal=TaskSignal.FAIL, message=message, data=error)

    @classmethod
    def cancel(cls, message: str = "已取消") -> "TaskCtl":
        return cls(signal=TaskSignal.CANCEL, message=message)

    @property
    def is_terminal(self) -> bool:
        """是否为终态"""
        return self.signal in (TaskSignal.SUCCESS, TaskSignal.FAIL, TaskSignal.CANCEL)
```

#### 2.1.3 AsyncTaskHandle (异步任务句柄)

```python
class AsyncTaskHandle:
    def __init__(self, task_id: str, chat_key: str, plugin: "NekroPlugin"):
        self.task_id = task_id
        self.chat_key = chat_key
        self.plugin = plugin
        self._waiters: Dict[str, asyncio.Future] = {}
        self._cancelled = False

    async def wait(self, key: str, timeout: Optional[float] = None) -> Any:
        """等待外部信号"""
        ...

    def notify(self, key: str, data: Any = None) -> bool:
        """通知等待点恢复"""
        ...

    def cancel_wait(self, key: str) -> bool:
        """取消特定等待点"""
        ...

    def cancel_all(self) -> int:
        """取消所有等待点"""
        ...

    async def notify_agent(self, message: str, trigger: bool = True) -> None:
        """通知主 Agent"""
        ...

    @property
    def is_cancelled(self) -> bool:
        """任务是否已取消"""
        return self._cancelled
```

#### 2.1.4 TaskRunner (任务运行器)

全局单例，管理任务生命周期：

```python
class TaskRunner:
    def register_task_type(self, task_type: str, func: AsyncTaskFunc) -> None:
        """注册任务类型"""

    async def start(self, task_type: str, task_id: str, chat_key: str, plugin: "NekroPlugin", *args, **kwargs) -> AsyncTaskHandle:
        """启动任务"""

    def get_handle(self, task_type: str, task_id: str) -> Optional[AsyncTaskHandle]:
        """获取任务句柄"""

    def get_state(self, task_type: str, task_id: str) -> Optional[TaskCtl]:
        """获取任务最新状态"""

    def is_running(self, task_type: str, task_id: str) -> bool:
        """检查任务是否正在运行"""

    async def cancel(self, task_type: str, task_id: str) -> bool:
        """取消任务"""

    async def stop_all(self) -> int:
        """停止所有任务"""
```

### 2.2 插件方法定义

**文件**: `nekro_agent/services/plugin/base.py`

```python
def mount_async_task(
    self,
    task_type: str,
) -> Callable[[Callable[..., AsyncGenerator[Any, None]]], Callable[..., AsyncGenerator[Any, None]]]:
    """挂载异步任务

    用于注册异步任务函数，任务函数通过 yield TaskCtl 报告状态，
    通过 AsyncTaskHandle.wait() 暂停等待外部信号。

    Args:
        task_type: 任务类型标识，用于启动和查询任务

    Returns:
        装饰器函数
    """
```

---

## 3. 交叉验证结果

### 3.1 源码与实现一致性 ✅

| 功能 | Nekro-Agent 源码 | WebApp 插件实现 | 状态 |
|------|------------------|-----------------|------|
| mount_async_task | ✅ 定义 | ✅ 使用 | 一致 |
| AsyncTaskHandle | ✅ 定义 | ✅ 使用 | 一致 |
| TaskCtl | ✅ 定义 | ✅ 使用 | 一致 |
| task.start() | ✅ 实现 | ✅ 调用 | 一致 |
| task.cancel() | ✅ 实现 | ✅ 调用 | 一致 |
| task.is_running() | ✅ 实现 | ✅ 调用 | 一致 |
| handle.notify_agent() | ✅ 实现 | ✅ 调用 | 一致 |

### 3.2 文档缺失情况

**当前文档站**: https://github.com/KroMiose/nekro-agent-doc

**缺失的文档**:

1. ❌ `mount_async_task()` 方法说明
2. ❌ `TaskCtl` 类使用指南
3. ❌ `AsyncTaskHandle` 类使用指南
4. ❌ `TaskRunner` / `task` 全局 API 说明
5. ❌ 异步任务最佳实践
6. ❌ 与主 Agent 交互机制说明
7. ❌ 任务状态管理说明

---

## 4. 文档补充方案

### 4.1 新增文档结构

建议在 `docs/04_plugin_dev/02_plugin_basics/` 下新增：

```
2.5_async_tasks.md    # 异步任务工具说明
```

### 4.2 文档章节规划

1. **异步任务概述**
   - 什么是异步任务
   - 使用场景
   - 与普通沙盒方法的区别

2. **核心 API**
   - mount_async_task() 装饰器
   - TaskCtl 控制信号
   - AsyncTaskHandle 任务句柄
   - task 全局 API

3. **完整示例**
   - 视频生成任务
   - 文件处理任务
   - 多步骤任务

4. **与主 Agent 交互**
   - notify_agent() 通知机制
   - 实时反馈注入
   - 任务状态同步

5. **最佳实践**
   - 任务设计模式
   - 错误处理
   - 资源清理

---

## 5. 研究结论

### 5.1 核心发现

1. **异步任务框架完整**: Nekro-Agent 提供了完整的异步任务框架
2. **实现一致性高**: WebApp 插件正确使用了所有异步任务 API
3. **文档严重缺失**: 异步任务相关文档完全缺失

### 5.2 下一步行动

1. ✅ 源码分析完成
2. ✅ WebApp 插件分析完成
3. ⏳ 编写文档草稿
4. ⏳ 提交 PR 到文档站

---

## 参考链接

- **WebApp 插件**: https://github.com/KroMiose/nekro-plugin-webapp/tree/refactor/simplified-single-agent
- **Nekro-Agent 源码**: https://github.com/KroMiose/nekro-agent
- **文档站**: https://github.com/KroMiose/nekro-agent-doc
- **研究仓库**: https://github.com/NekroAI/async-plugin-research
