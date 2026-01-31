# Nekro-Agent AI 自动化测试框架设计

## 研究日期

2026-01-30

## 问题陈述

**当前困境**：
- `bot --load-test` 只验证插件能加载
- 无法验证：
  - 消息处理逻辑是否正确
  - 与 LLM API 的交互是否正常
  - 状态管理是否正确
  - 错误恢复机制是否工作

**根本原因**：
- NoneBot2 插件设计为事件驱动，需要真实消息触发
- 插件依赖外部服务（OneBot 协议、LLM API）
- 缺乏隔离的测试环境

---

## 一、测试框架架构

### 1.1 核心设计理念

```
┌─────────────────────────────────────────────────────────────────────┐
│                      AI 自动化测试代理                              │
│  • 理解插件功能                                                      │
│  • 生成测试场景                                                      │
│  • 执行测试                                                          │
│  • 分析结果                                                          │
│  • 修复问题                                                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      测试执行引擎                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐              │
│  │ 虚拟协议端   │   │  LLM 模拟器  │   │  状态捕获器  │              │
│  │ (Mock Bot)  │   │ (Mock API)  │   │ (Trace)     │              │
│  └─────────────┘   └─────────────┘   └─────────────┘              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      被测插件                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 测试类型

| 类型 | 说明 | 使用场景 |
|------|------|----------|
| **加载测试** | 验证插件能正确加载 | CI 基础检查 |
| **单元测试** | 测试单个函数/方法 | 核心逻辑 |
| **集成测试** | 测试多组件协作 | API 调用 |
| **端到端测试** | 模拟真实对话场景 | 功能验证 |
| **LLM 交互测试** | 测试与 LLM API 的交互 | Agent 功能 |

---

## 二、关键技术组件

### 2.1 Mock Bot（虚拟协议端）

```python
# tests/mocks/bot.py

from nonebot.adapters.onebot.v11 import Bot, Event, Message, GroupMessageEvent
from nonebot import on_message
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MockMessage:
    """模拟消息"""
    message_id: int
    message: Message
    user_id: int
    group_id: Optional[int] = None
    time: datetime = field(default_factory=datetime.now)


class MockBot(Bot):
    """模拟 OneBot 协议端"""
    
    def __init__(self, self_id: str = "123456789"):
        super().__init__(self_id=self_id)
        self.sent_messages: list[MockMessage] = []
        self.received_messages: list[MockMessage] = []
    
    async def send(self, event: Event, message: Message, **kwargs):
        """记录发送的消息"""
        msg = MockMessage(
            message_id=len(self.sent_messages) + 1,
            message=message,
            user_id=event.get_user_id() if hasattr(event, 'get_user_id') else 0,
            group_id=event.group_id if hasattr(event, 'group_id') else None,
        )
        self.sent_messages.append(msg)
        return {"message_id": msg.message_id}
    
    async def call_api(self, api: str, **kwargs):
        """模拟 API 调用"""
        return {"status": "ok", "retcode": 0, "data": {}}


class MockEventFactory:
    """创建模拟事件"""
    
    @staticmethod
    def private_message(user_id: int = 10001, message: str = "test"):
        """私聊消息"""
        return GroupMessageEvent(
            time=int(datetime.now().timestamp()),
            self_id=123456789,
            message_id=1,
            message=Message(message),
            message_type="private",
            user_id=user_id,
        )
    
    @staticmethod
    def group_message(group_id: int = 10001, user_id: int = 10001, message: str = "test"):
        """群聊消息"""
        return GroupMessageEvent(
            time=int(datetime.now().timestamp()),
            self_id=123456789,
            message_id=1,
            message=Message(message),
            message_type="group",
            group_id=group_id,
            user_id=user_id,
        )
```

### 2.2 Mock LLM API

```python
# tests/mocks/llm.py

from unittest.mock import AsyncMock, MagicMock
from openai import AsyncOpenAI
from typing import AsyncGenerator


class MockLLMResponse:
    """模拟 LLM 响应"""
    
    def __init__(self, content: str, delay: float = 0.1):
        self.content = content
        self.delay = delay
    
    def to_dict(self):
        return {
            "choices": [
                {
                    "message": {
                        "content": self.content
                    }
                }
            ]
        }


class MockLLMClient:
    """模拟 LLM 客户端"""
    
    def __init__(self):
        self.responses: dict[str, MockLLMResponse] = {}
        self.call_history: list[dict] = []
        self.response_index: dict[str, int] = {}
    
    def add_response(self, query_pattern: str, response: MockLLMResponse):
        """添加预定义的响应"""
        self.responses[query_pattern] = response
    
    async def chat(self, messages: list[dict], **kwargs) -> MockLLMResponse:
        """模拟 chat completion 调用"""
        # 记录调用
        self.call_history.append({
            "messages": messages,
            "kwargs": kwargs,
            "time": datetime.now().isoformat(),
        })
        
        # 查找匹配的预定义响应
        last_user_msg = messages[-1]["content"] if messages else ""
        
        for pattern, response in self.responses.items():
            if pattern in last_user_msg.lower():
                return response
        
        # 默认响应
        return MockLLMResponse("我是一个模拟的 AI 助手")
```

### 2.3 插件测试运行器

```python
# tests/runner.py

import asyncio
from nonebot import get_driver
from nonebot.testing import AdapterTestContext
from tests.mocks.bot import MockBot
from tests.mocks.llm import MockLLMClient


class PluginTestRunner:
    """插件测试运行器"""
    
    def __init__(self, plugin_module: str):
        self.plugin_module = plugin_module
        self.mock_bot = MockBot()
        self.mock_llm = MockLLMClient()
        self.test_results: list[dict] = []
    
    async def run_test(self, name: str, test_func):
        """运行单个测试"""
        result = {
            "name": name,
            "status": "pending",
            "error": None,
            "output": None,
        }
        
        try:
            output = await test_func()
            result["output"] = output
            result["status"] = "passed"
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "failed"
        
        self.test_results.append(result)
        return result
    
    async def simulate_message(self, user_id: int, message: str, group_id: int = None):
        """模拟发送消息到插件"""
        from tests.mocks.bot import MockEventFactory
        
        event = MockEventFactory.group_message(
            group_id=group_id or 10001,
            user_id=user_id,
            message=message,
        )
        
        # 获取插件的 matcher 并手动触发
        # ... 实际触发逻辑
        
        return self.mock_bot.sent_messages
    
    async def verify_response(self, expected_content: str) -> bool:
        """验证响应内容"""
        if not self.mock_bot.sent_messages:
            return False
        
        last_msg = self.mock_bot.sent_messages[-1].message.extract_plain_text()
        return expected_content in last_msg
    
    def get_report(self) -> str:
        """生成测试报告"""
        passed = sum(1 for r in self.test_results if r["status"] == "passed")
        failed = sum(1 for r in self.test_results if r["status"] == "failed")
        
        lines = [
            f"测试结果: {passed} 通过, {failed} 失败",
            "",
        ]
        
        for result in self.test_results:
            status = "✅" if result["status"] == "passed" else "❌"
            lines.append(f"{status} {result['name']}")
            if result["error"]:
                lines.append(f"   错误: {result['error']}")
        
        return "\n".join(lines)
```

---

## 三、AI 驱动的测试设计

### 3.1 测试生成器

```python
# tests/ai_generator.py

from openai import AsyncOpenAI
from typing import List, Dict
import json


class AITestGenerator:
    """AI 驱动的测试生成器"""
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate_tests(self, plugin_code: str) -> List[Dict]:
        """根据插件代码生成测试用例"""
        
        prompt = f"""
分析以下 NoneBot2 插件代码，生成测试用例。

要求：
1. 分析插件的功能、触发条件、消息处理逻辑
2. 生成 5-10 个测试用例，覆盖：
   - 正常流程
   - 边界情况
   - 错误处理
3. 每个测试用例包含：
   - 测试名称
   - 输入消息
   - 预期输出
   - 测试目的

返回 JSON 数组格式。

插件代码：
```python
{plugin_code}
```
"""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("test_cases", [])
```

### 3.2 LLM-as-Judge 验证器

```python
# tests/judge.py

from openai import AsyncOpenAI
from typing import Tuple


class LLMJudge:
    """使用 LLM 验证测试结果"""
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def verify_response(
        self,
        test_name: str,
        user_message: str,
        bot_response: str,
        expected_behavior: str,
    ) -> Tuple[bool, str]:
        """
        验证机器人响应是否符合预期
        
        Returns:
            (is_correct, reason)
        """
        
        prompt = f"""
你是一个 QA 测试专家，验证机器人的响应是否正确。

测试名称: {test_name}
用户消息: {user_message}
机器人响应: {bot_response}
预期行为: {expected_behavior}

请判断：
1. 机器人的响应是否正确？
2. 如果不正确，具体问题是什么？

返回 JSON 格式：
{{
  "correct": true/false,
  "reason": "详细说明"
}}
"""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        
        result = json.loads(response.choices[0].message.content)
        return result["correct"], result["reason"]
```

### 3.3 自修复测试循环

```python
# tests/self_fix_loop.py

from tests.runner import PluginTestRunner
from tests.ai_generator import AITestGenerator
from tests.judge import LLMJudge


class SelfFixingTestRunner:
    """自修复测试运行器"""
    
    def __init__(self, plugin_module: str, openai_api_key: str):
        self.runner = PluginTestRunner(plugin_module)
        self.generator = AITestGenerator(openai_api_key)
        self.judge = LLMJudge(openai_api_key)
    
    async def run_with_auto_fix(self, max_iterations: int = 3) -> dict:
        """运行测试，自动修复问题"""
        
        iteration = 0
        fixed_issues = []
        
        while iteration < max_iterations:
            iteration += 1
            print(f"=== 测试迭代 {iteration}/{max_iterations} ===")
            
            # 运行测试
            results = await self.run_all_tests()
            
            # 检查失败
            failures = [r for r in results if r["status"] == "failed"]
            
            if not failures:
                print("✅ 所有测试通过！")
                return {"success": True, "iterations": iteration}
            
            # 分析失败原因
            for failure in failures:
                analysis = await self.analyze_failure(failure)
                
                if analysis.get("can_auto_fix"):
                    fix = await self.suggest_fix(failure, analysis)
                    fixed_issues.append({
                        "failure": failure["name"],
                        "fix": fix,
                    })
                    
                    # 应用修复
                    await self.apply_fix(fix)
                else:
                    return {
                        "success": False,
                        "iteration": iteration,
                        "unfixed": failures,
                    }
        
        return {
            "success": False,
            "iterations": iteration,
            "fixed": fixed_issues,
        }
    
    async def analyze_failure(self, failure: dict) -> dict:
        """分析测试失败原因"""
        
        prompt = f"""
分析以下测试失败的原因：

测试名称: {failure['name']}
错误信息: {failure['error']}

请判断：
1. 失败的根本原因是什么？
2. 是否可以自动修复？
3. 需要什么信息来修复？

返回 JSON 格式。
"""
        
        # 调用 LLM 分析
        ...
    
    async def suggest_fix(self, failure: dict, analysis: dict) -> str:
        """建议修复方案"""
        ...
    
    async def apply_fix(self, fix: str):
        """应用修复"""
        # 修改代码
        ...
```

---

## 四、完整测试工作流

### 4.1 工作流设计

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AI 自动化测试工作流                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1️⃣ 代码分析阶段                                                         │
│     ├── 读取插件源码                                                     │
│     ├── 理解功能逻辑                                                     │
│     └── 生成测试用例 (AI)                                               │
│                                                                          │
│  2️⃣ 测试执行阶段                                                         │
│     ├── 启动 Mock Bot                                                   │
│     ├── Mock LLM 响应                                                   │
│     ├── 模拟消息发送                                                     │
│     └── 记录响应                                                         │
│                                                                          │
│  3️⃣ 结果验证阶段                                                         │
│     ├── 规则匹配验证                                                     │
│     └── LLM 语义验证 (AI)                                               │
│                                                                          │
│  4️⃣ 问题修复阶段                                                         │
│     ├── 分析失败原因 (AI)                                               │
│     ├── 生成修复方案 (AI)                                               │
│     ├── 应用代码修复                                                     │
│     └── 重新测试                                                         │
│                                                                          │
│  5️⃣ 报告生成阶段                                                         │
│     ├── 测试覆盖率                                                       │
│     ├── 通过/失败统计                                                    │
│     └── 改进建议 (AI)                                                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 配置文件

```yaml
# tests/config.yaml

plugins:
  - path: "plugins/example_plugin"
    tests:
      - name: "basic_chat"
        inputs:
          - "你好"
          - "你是谁"
          - "帮我个忙"
        expected:
          - contains: ["你好", "Hi"]
          - contains: ["AI", "助手"]
          - contains: ["好的", "可以"]

llm:
  provider: "openai"
  model: "gpt-4o"
  mock:
    enabled: true
    responses:
      - pattern: "你好"
        response: "你好！我是测试助手。"
      - pattern: ".*"
        response: "收到，我理解了。"

report:
  format: "markdown"
  output: "test_results.md"
```

### 4.3 测试脚本

```bash
#!/bin/bash
# run_ai_test.sh

PLUGIN_PATH=$1
OPENAI_API_KEY=${2:-$OPENAI_API_KEY}

echo "=== AI 自动化测试 ==="
echo "插件: $PLUGIN_PATH"

# 安装依赖
uv sync

# 运行测试
uv run python -m tests.main \
    --plugin "$PLUGIN_PATH" \
    --api-key "$OPENAI_API_KEY" \
    --output test_results.md

# 检查结果
if [ $? -eq 0 ]; then
    echo "✅ 测试通过"
else
    echo "❌ 测试失败，查看 test_results.md 获取详情"
fi
```

---

## 五、沙盒测试

### 5.1 沙盒测试设计

```python
# tests/sandbox_test.py

import asyncio
from nekro_agent.services.sandbox.runner import SandboxRunner


class SandboxTestRunner:
    """沙盒环境测试"""
    
    def __init__(self):
        self.runner = None
    
    async def test_code_execution(self, code: str) -> dict:
        """测试代码在沙盒中执行"""
        
        result = {
            "code": code,
            "status": "pending",
            "output": None,
            "error": None,
            "execution_time": None,
        }
        
        try:
            start = asyncio.get_event_loop().time()
            
            # 在沙盒中执行代码
            self.runner = SandboxRunner()
            output = await self.runner.run(code)
            
            end = asyncio.get_event_loop().time()
            
            result["output"] = output
            result["execution_time"] = end - start
            result["status"] = "passed"
            
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "failed"
        
        return result
    
    async def test_package_import(self, package: str) -> dict:
        """测试包能否在沙盒中导入"""
        
        code = f"""
import {package}
print(f"Successfully imported {package}")
print(f"Version: {getattr({package}, '__version__', 'unknown')}")
"""
        
        return await self.test_code_execution(code)
```

---

## 六、测试用例示例

### 6.1 插件测试示例

```python
# tests/plugins/example_test.py

import asyncio
from tests.runner import PluginTestRunner


async def test_example_plugin():
    """测试示例插件"""
    
    runner = PluginTestRunner("plugins.example_plugin")
    
    # 测试 1: 基础响应
    await runner.run_test(
        "test_basic_response",
        lambda: runner.simulate_message(10001, "你好")
    )
    
    # 验证响应
    assert runner.mock_bot.sent_messages, "未收到响应"
    assert "你好" in runner.mock_bot.sent_messages[-1].message.extract_plain_text()
    
    # 测试 2: 错误处理
    result = await runner.run_test(
        "test_error_handling",
        lambda: runner.simulate_message(10001, "/invalid_command")
    )
    
    assert result["status"] == "passed", f"错误处理测试失败: {result['error']}"
    
    # 打印报告
    print(runner.get_report())
```

### 6.2 集成测试示例

```python
# tests/integration/test_full_flow.py

import asyncio
from tests.runner import PluginTestRunner
from tests.mocks.llm import MockLLMClient


async def test_full_conversation_flow():
    """测试完整对话流程"""
    
    runner = PluginTestRunner("plugins.conversation")
    mock_llm = MockLLMClient()
    
    # 配置 Mock LLM 响应
    mock_llm.add_response("天气", "今天天气晴朗，适合出行。")
    mock_llm.add_response(".*", "我理解你的意思。")
    
    # 模拟对话
    messages = [
        "你好",
        "今天天气怎么样？",
        "谢谢",
    ]
    
    for msg in messages:
        await runner.simulate_message(10001, msg)
    
    # 验证对话连贯性
    assert len(runner.mock_bot.sent_messages) == len(messages)
    
    # 检查 LLM 调用历史
    assert len(mock_llm.call_history) > 0, "LLM 未被调用"
    
    print("✅ 完整对话流程测试通过")
```

---

## 七、输出与报告

### 7.1 测试报告格式

```markdown
# 插件测试报告

## 基本信息

| 项目 | 值 |
|------|-----|
| 插件 | example_plugin |
| 测试时间 | 2026-01-30 18:30 |
| 总测试数 | 10 |
| 通过 | 9 |
| 失败 | 1 |

## 测试详情

### ✅ test_basic_chat
- 输入: "你好"
- 输出: "你好！有什么可以帮你的吗？"
- 状态: 通过

### ❌ test_error_handling
- 输入: "/invalid_command"
- 输出: None
- 错误: AttributeError: 'NoneType' object...
- 状态: 失败

## 建议修复

根据 AI 分析，错误发生在 `example.py:42`，建议：
1. 添加参数验证
2. 返回错误提示消息
```

---

## 八、实施计划

### 8.1 阶段一：基础框架（Week 1）

| 任务 | 输出 |
|------|------|
| 实现 Mock Bot | `tests/mocks/bot.py` |
| 实现 Mock LLM | `tests/mocks/llm.py` |
| 实现 Plugin Test Runner | `tests/runner.py` |
| 编写示例测试 | `tests/plugins/example_test.py` |

### 8.2 阶段二：AI 增强（Week 2）

| 任务 | 输出 |
|------|------|
| AI 测试生成器 | `tests/ai_generator.py` |
| LLM 验证器 | `tests/judge.py` |
| 自修复循环 | `tests/self_fix_loop.py` |

### 8.3 阶段三：CI 集成（Week 3）

| 任务 | 输出 |
|------|------|
| GitHub Actions | `.github/workflows/ai-test.yml` |
| 测试配置 | `tests/config.yaml` |
| 报告生成 | `tests/reporter.py` |

---

## 九、总结

### 9.1 核心价值

| 能力 | 说明 |
|------|------|
| **真正的测试** | 不是 load-test，而是功能验证 |
| **AI 驱动** | 自动生成测试、自动验证、自动修复 |
| **隔离环境** | Mock 外部依赖，不影响生产 |
| **持续改进** | 失败 → 分析 → 修复 → 重试 |

### 9.2 下一步

1. 实现 Mock Bot 和 Mock LLM
2. 编写第一个插件测试
3. 集成 AI 验证
4. 加入 CI/CD

---

## 附录：完整文件结构

```
tests/
├── __init__.py
├── config.yaml              # 测试配置
├── main.py                  # 入口脚本
├── runner.py                # 测试运行器
├── reporter.py              # 报告生成
│
├── mocks/
│   ├── __init__.py
│   ├── bot.py              # Mock Bot
│   └── llm.py              # Mock LLM
│
├── ai_generator.py         # AI 测试生成
├── judge.py                # LLM 验证
├── self_fix_loop.py        # 自修复循环
│
├── plugins/
│   └── example_test.py     # 插件测试示例
│
└── integration/
    └── test_full_flow.py   # 集成测试示例
```
