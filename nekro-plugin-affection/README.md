# nekro-plugin-affection

为 AI 提供一个完整的角色好感度追踪系统，模拟 RPG 游戏中的关系发展机制。

## 设计理念

AI 的对话记忆是滚动的，但"关系"应该是累积的。好感度系统充当 AI 的"情感记忆库"，让 AI 能够：
- 记住与每个角色的关系发展历程
- 根据好感度调整对话风格和行为
- 解锁特殊的互动内容和羁绊能力

## 主要功能

### 好感度追踪
- 为每个角色维护独立的好感度值（-100 到 +100）
- 自动根据好感度划分关系等级

### 关系等级
| 等级 | 好感度范围 | 描述 |
|------|-----------|------|
| 敌人 | -100 ~ -60 | 对你有防备或敌意 |
| 陌生人 | -59 ~ -20 | 刚刚认识，不太熟悉 |
| 熟人 | -19 ~ 10 | 有一定了解 |
| 朋友 | 11 ~ 50 | 相处融洽 |
| 密友 | 51 ~ 80 | 互相信任 |
| 灵魂伴侣 | 81 ~ 100 | 关系非常深厚 |

### 事件系统
记录以下类型的好感度变化事件：
- **positive**: 正面事件（感谢、赞扬等）
- **negative**: 负面事件（批评、不满等）
- **neutral**: 中性事件（日常对话等）
- **crisis**: 危机事件（一起面对困难）

### 羁绊系统
达到特定条件时解锁特殊羁绊：
- `first_meet`: 初次相遇（初始解锁）
- `shared_laugh`: 欢笑共鸣（累计正面互动 ≥ 5）
- `deep_conversation`: 深入交流（累计正面互动 ≥ 10）
- `trusted_confidant`: 信赖倾诉（累计正面互动 ≥ 20）
- `storm_together`: 共渡难关（处理危机 ≥ 3）
- `heart_to_heart`: 心心相印（好感度 ≥ 80）

## 使用方法

### 安装

```bash
# 通过插件市场安装
# 或克隆到本地
git clone https://github.com/YukiAcerium/nekro-plugin-affection.git
cp -r nekro-plugin-affection/nekro_plugin_affection <nekro-agent-plugins-path>/
```

### AI 自动使用

此插件主要由 AI 在后台自动使用。例如：

```python
# 记录一次正面互动
record_affection_change(
    character_id="user_123",
    character_name="小明",
    change_amount=5,
    event_type="positive",
    description="用户真诚地表达了感谢",
    context="帮助用户完成了重要任务"
)

# 获取当前关系状态
status = get_affection(
    character_id="user_123",
    character_name="小明"
)
# 返回: {tier_name: "朋友", affection_value: 25, ...}
```

### 提示词注入

插件会自动将当前关系状态注入到 AI 上下文中：

```
## 与 小明 的关系状态
- 当前关系: [朋友]
- 好感度: 25/100
- 关系描述: 你们是朋友，相处融洽

### 最近的互动记录:
- 😊 [01-25 14:30] 用户真诚地表达了感谢
- 😊 [01-25 12:00] 一起讨论了有趣的话题
```

## 配置说明

在 `nekro-agent.yaml` 中配置：

```yaml
plugins:
  affection:
    DEFAULT_AFFECTION: 0          # 新角色初始好感度
    MAX_HISTORY_EVENTS: 20        # 最大历史事件数
    AFFECTION_PROMPT_LIMIT: 5     # 提示注入显示数量
    ENABLE_BOND_SYSTEM: true      # 启用羁绊系统
```

## 沙盒方法

| 方法名 | 类型 | 描述 |
|--------|------|------|
| `获取好感度` | TOOL | 获取指定角色的当前好感度和关系等级 |
| `记录好感度变化` | BEHAVIOR | 记录一次影响好感度的事件 |
| `获取互动历史` | TOOL | 获取角色好感度的互动历史记录 |
| `获取羁绊信息` | TOOL | 查询可解锁的羁绊列表及其条件 |
| `重置好感度` | BEHAVIOR | 重置指定角色的好感度数据 |

## 开发计划

- [ ] 添加更多预定义羁绊
- [ ] 支持自定义羁绊条件
- [ ] 添加好感度变化趋势分析
- [ ] 支持批量操作（批量记录事件）
- [ ] 添加可视化统计面板

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
