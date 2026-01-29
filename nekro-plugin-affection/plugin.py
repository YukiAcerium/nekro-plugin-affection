"""
# 好感度系统插件 (Affection System)

为 AI 提供一个完整的角色好感度追踪系统，模拟 RPG 游戏中的关系发展机制。

## 设计理念

AI 的对话记忆是滚动的，但"关系"应该是累积的。好感度系统充当 AI 的"情感记忆库"，让 AI 能够：
- 记住与每个角色的关系发展历程
- 根据好感度调整对话风格和行为
- 解锁特殊的互动内容和羁绊能力

## 主要功能

- **好感度追踪**: 为每个角色维护独立的好感度值（-100 到 +100）
- **关系等级**: 自动根据好感度划分关系等级（陌生人 → 熟人 → 朋友 → 密友 → 灵魂伴侣）
- **事件系统**: 记录和分析影响好感度的事件
- **羁绊系统**: 解锁特殊对话、角色状态、专属互动
- **智能提示**: 自动注入当前关系状态到 AI 上下文中

## 使用方法

此插件主要由 AI 在后台自动使用。例如：
- 当用户对 AI 表达感谢时，AI 会记录："用户表达感谢，好感+5"
- 当 AI 帮助用户解决问题时，AI 会记录："帮助用户完成重要任务，好感+10"
- AI 会根据当前好感度等级调整对话语气和内容
"""

import time
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from nekro_agent.api import core, i18n, schemas
from nekro_agent.api.plugin import (
    ConfigBase,
    ExtraField,
    NekroPlugin,
    SandboxMethodType,
)

plugin = NekroPlugin(
    name="好感度系统插件",
    module_name="affection",
    description="提供角色好感度追踪系统，支持关系等级、事件记录、羁绊解锁",
    version="0.1.0",
    author="Yuki",
    url="https://github.com/YukiAcerium/nekro-plugin-weather",
    i18n_name=i18n.i18n_text(
        zh_CN="好感度系统插件",
        en_US="Affection System Plugin",
    ),
    i18n_description=i18n.i18n_text(
        zh_CN="提供角色好感度追踪系统，支持关系等级、事件记录、羁绊解锁",
        en_US="Provides character affection tracking with relationship tiers, events, and bond unlocks",
    ),
)


# ============================================================================
# 配置 (Configuration)
# ============================================================================

@plugin.mount_config()
class AffectionConfig(ConfigBase):
    """好感度系统配置"""

    DEFAULT_AFFECTION: int = Field(
        default=0,
        title="默认好感度",
        description="新角色的初始好感度值（范围：-100 到 100）",
        json_schema_extra=ExtraField(
            i18n_title=i18n.i18n_text(
                zh_CN="默认好感度",
                en_US="Default Affection",
            ),
            i18n_description=i18n.i18n_text(
                zh_CN="新角色的初始好感度值（范围：-100 到 100）",
                en_US="Initial affection value for new characters (-100 to 100)",
            ),
        ).model_dump(),
    )
    MAX_HISTORY_EVENTS: int = Field(
        default=20,
        title="最大历史事件数",
        description="每个角色保留的最大事件记录数量",
        json_schema_extra=ExtraField(
            i18n_title=i18n.i18n_text(
                zh_CN="最大历史事件数",
                en_US="Max History Events",
            ),
            i18n_description=i18n.i18n_text(
                zh_CN="每个角色保留的最大事件记录数量",
                en_US="Maximum number of historical events to keep per character",
            ),
        ).model_dump(),
    )
    AFFECTION_PROMPT_LIMIT: int = Field(
        default=5,
        title="提示注入显示数量",
        description="注入到提示词中的最近事件数量",
        json_schema_extra=ExtraField(
            i18n_title=i18n.i18n_text(
                zh_CN="提示注入显示数量",
                en_US="Affection Prompt Limit",
            ),
            i18n_description=i18n.i18n_text(
                zh_CN="注入到提示词中的最近事件数量",
                en_US="Number of recent events to inject into prompt",
            ),
        ).model_dump(),
    )
    ENABLE_BOND_SYSTEM: bool = Field(
        default=True,
        title="启用羁绊系统",
        description="是否启用羁绊解锁功能",
        json_schema_extra=ExtraField(
            i18n_title=i18n.i18n_text(
                zh_CN="启用羁绊系统",
                en_US="Enable Bond System",
            ),
            i18n_description=i18n.i18n_text(
                zh_CN="是否启用羁绊系统",
                en_US="Whether to enable bond unlock features",
            ),
        ).model_dump(),
    )


# 获取配置
config = plugin.get_config(AffectionConfig)
store = plugin.store


# ============================================================================
# 数据模型 (Data Models)
# ============================================================================

class AffectionTier(str, Enum):
    """关系等级枚举"""
    ENEMY = "enemy"           # 敌人 (-100 ~ -60)
    STRANGER = "stranger"     # 陌生人 (-59 ~ -20)
    ACQUAINTANCE = "acquaintance"  # 熟人 (-19 ~ 10)
    FRIEND = "friend"         # 朋友 (11 ~ 50)
    CLOSE_FRIEND = "close_friend"  # 密友 (51 ~ 80)
    SOULMATE = "soulmate"     # 灵魂伴侣 (81 ~ 100)


class AffectionEvent(BaseModel):
    """好感度事件"""
    timestamp: int
    change_amount: int
    event_type: str  # "positive", "negative", "neutral"
    description: str
    context: Optional[str] = None  # 额外上下文

    @classmethod
    def create(
        cls,
        change_amount: int,
        event_type: str,
        description: str,
        context: Optional[str] = None,
    ) -> "AffectionEvent":
        """创建事件"""
        return cls(
            timestamp=int(time.time()),
            change_amount=change_amount,
            event_type=event_type,
            description=description,
            context=context,
        )


class BondStatus(BaseModel):
    """羁绊状态"""
    bond_id: str
    unlocked: bool = False
    unlock_time: int = 0
    level: int = 1  # 羁绊等级 1-5

    @classmethod
    def create(cls, bond_id: str) -> "BondStatus":
        """创建羁绊状态"""
        return cls(bond_id=bond_id)


class CharacterAffection(BaseModel):
    """角色好感度数据"""
    character_id: str
    character_name: str
    affection_value: int = 0
    total_positive: int = 0  # 累计正面事件
    total_negative: int = 0  # 累计负面事件
    first_met_time: int = 0
    last_interaction_time: int = 0
    events: List[AffectionEvent] = []
    bonds: Dict[str, BondStatus] = {}

    @classmethod
    def create(
        cls,
        character_id: str,
        character_name: str,
        initial_affection: int = 0,
    ) -> "CharacterAffection":
        """创建角色数据"""
        now = int(time.time())
        return cls(
            character_id=character_id,
            character_name=character_name,
            affection_value=initial_affection,
            first_met_time=now,
            last_interaction_time=now,
        )

    def add_event(
        self,
        event: AffectionEvent,
        max_events: int = 20,
    ) -> None:
        """添加事件并维护历史"""
        self.events.append(event)
        self.events = self.events[-max_events:]
        self.last_interaction_time = event.timestamp

        # 更新累计统计
        if event.change_amount > 0:
            self.total_positive += event.change_amount
        elif event.change_amount < 0:
            self.total_negative += abs(event.change_amount)

    def get_tier(self) -> AffectionTier:
        """获取当前关系等级"""
        value = self.affection_value
        if value >= 81:
            return AffectionTier.SOULMATE
        elif value >= 51:
            return AffectionTier.CLOSE_FRIEND
        elif value >= 11:
            return AffectionTier.FRIEND
        elif value >= -19:
            return AffectionTier.ACQUAINTANCE
        elif value >= -59:
            return AffectionTier.STRANGER
        else:
            return AffectionTier.ENEMY

    def get_unlocked_bonds(self) -> List[str]:
        """获取已解锁的羁绊列表"""
        return [
            bond_id
            for bond_id, status in self.bonds.items()
            if status.unlocked
        ]

    def render_tier_description(self) -> str:
        """渲染等级描述"""
        tier = self.get_tier()
        tier_names = {
            AffectionTier.ENEMY: "敌人",
            AffectionTier.STRANGER: "陌生人",
            AffectionTier.ACQUAINTANCE: "熟人",
            AffectionTier.FRIEND: "朋友",
            AffectionTier.CLOSE_FRIEND: "密友",
            AffectionTier.SOULMATE: "灵魂伴侣",
        }
        return f"[{tier_names[tier]}]"


# ============================================================================
# 预定义羁绊 (Predefined Bonds)
# ============================================================================

# 羁绊定义：达到特定条件时解锁的特殊能力/对话
BOND_DEFINITIONS = {
    "first_meet": {
        "name": "初次相遇",
        "description": "你们第一次见面的美好记忆",
        "condition": "always",  # 初始解锁
        "tier": AffectionTier.STRANGER,
    },
    "shared_laugh": {
        "name": "欢笑共鸣",
        "description": "一起分享快乐时光",
        "condition": "event_count_positive >= 5",
        "tier": AffectionTier.FRIEND,
    },
    "deep_conversation": {
        "name": "深入交流",
        "description": "进行过一次深入的心灵对话",
        "condition": "event_count_positive >= 10",
        "tier": AffectionTier.CLOSE_FRIEND,
    },
    "trusted_confidant": {
        "name": "信赖倾诉",
        "description": "成为彼此可以倾诉心事的对象",
        "condition": "event_count_positive >= 20",
        "tier": AffectionTier.SOULMATE,
    },
    "storm_together": {
        "name": "共渡难关",
        "description": "一起面对并克服了困难",
        "condition": "event_type_crisis_handled >= 3",
        "tier": AffectionTier.FRIEND,
    },
    "heart_to_heart": {
        "name": "心心相印",
        "description": "建立了深厚的情感纽带",
        "condition": "affection >= 80",
        "tier": AffectionTier.SOULMATE,
    },
}


# ============================================================================
# 存储操作 (Storage Operations)
# ============================================================================

async def get_character_data(
    chat_key: str,
    character_id: str,
) -> Optional[CharacterAffection]:
    """获取角色好感度数据"""
    data = await store.get(
        chat_key=chat_key,
        store_key=f"affection_{character_id}",
    )
    if data:
        return CharacterAffection.model_validate_json(data)
    return None


async def save_character_data(
    chat_key: str,
    character: CharacterAffection,
) -> None:
    """保存角色好感度数据"""
    await store.set(
        chat_key=chat_key,
        store_key=f"affection_{character.character_id}",
        value=character.model_dump_json(),
    )


async def get_all_characters(chat_key: str) -> Dict[str, CharacterAffection]:
    """获取所有角色数据"""
    data = await store.get(chat_key=chat_key, store_key="all_characters")
    if data:
        import json
        raw = json.loads(data)
        return {
            char_id: CharacterAffection.model_validate(data)
            for char_id, data in raw.items()
        }
    return {}


# ============================================================================
# 提示词注入 (Prompt Injection)
# ============================================================================

@plugin.mount_prompt_inject_method("affection_prompt_inject")
async def affection_prompt_inject(_ctx: schemas.AgentCtx) -> str:
    """好感度系统提示注入

    将当前角色的关系状态注入到 AI 上下文中
    """
    # 获取目标角色 ID（默认为用户）
    target_id = _ctx.from_user_id
    target_name = "用户"  # 可以从用户信息中获取真实名称

    # 尝试获取用户真实名称
    user_info = await core.get_user_info(_ctx.from_user_id, _ctx.chat_key)
    if user_info and hasattr(user_info, "nickname"):
        target_name = user_info.nickname

    # 获取好感度数据
    character = await get_character_data(_ctx.chat_key, target_id)

    if not character:
        return (
            f"## 关系状态\n"
            f"- 角色: {target_name}\n"
            f"- 关系: 初次见面，还不太了解\n"
            f"- 建议: 可以主动介绍自己，了解对方的兴趣爱好"
        )

    # 构建提示词
    tier_desc = character.render_tier_description()
    tier = character.get_tier()

    # 关系描述映射
    relationship_descriptions = {
        AffectionTier.ENEMY: "对方似乎对你有防备或敌意，需要小心谨慎地互动",
        AffectionTier.STRANGER: "你们刚刚认识，还不太熟悉",
        AffectionTier.ACQUAINTANCE: "你们已经认识，有一定的了解",
        AffectionTier.FRIEND: "你们是朋友，相处融洽",
        AffectionTier.CLOSE_FRIEND: "你们是很亲密的朋友，互相信任",
        AffectionTier.SOULMATE: "你们是灵魂伴侣，关系非常深厚",
    }

    prompt_parts = [
        f"## 与 {target_name} 的关系状态",
        f"- 当前关系: {tier_desc}",
        f"- 好感度: {character.affection_value}/100",
        f"- 关系描述: {relationship_descriptions[tier]}",
        "",
        "### 最近的互动记录:",
    ]

    # 添加最近事件
    recent_events = character.events[-config.AFFECTION_PROMPT_LIMIT:]
    if not recent_events:
        prompt_parts.append("- 暂无互动记录")
    else:
        for event in recent_events:
            emoji = "😊" if event.change_amount > 0 else ("😔" if event.change_amount < 0 else "💬")
            time_str = time.strftime("%m-%d %H:%M", time.gmtime(event.timestamp))
            prompt_parts.append(f"- {emoji} [{time_str}] {event.description}")

    # 添加羁绊信息
    if config.ENABLE_BOND_SYSTEM:
        unlocked_bonds = character.get_unlocked_bonds()
        if unlocked_bonds:
            prompt_parts.append("")
            prompt_parts.append("### 已解锁羁绊:")
            for bond_id in unlocked_bonds:
                if bond_id in BOND_DEFINITIONS:
                    bond = BOND_DEFINITIONS[bond_id]
                    prompt_parts.append(f"- {bond['name']}: {bond['description']}")

    return "\n".join(prompt_parts)


# ============================================================================
# 沙盒方法 (Sandbox Methods)
# ============================================================================

@plugin.mount_sandbox_method(
    SandboxMethodType.TOOL,
    name="获取好感度",
    description="获取指定角色的当前好感度和关系等级",
)
async def get_affection(
    _ctx: schemas.AgentCtx,
    character_id: str,
    character_name: str,
) -> dict:
    """Get Affection (获取好感度)

    获取指定角色的当前好感度状态。如果角色不存在，会创建新记录。

    Args:
        character_id (str): 角色的唯一标识符（通常是用户ID或自定义ID）
        character_name (str): 角色的显示名称

    Returns:
        dict: 包含以下字段:
            - character_id: 角色ID
            - character_name: 角色名称
            - affection_value: 好感度值 (-100 到 100)
            - tier: 关系等级 (enemy/stranger/acquaintance/friend/close_friend/soulmate)
            - tier_name: 关系等级名称（中文）
            - total_positive: 累计正面互动次数
            - total_negative: 累计负面互动次数
            - first_met: 初次相遇时间戳
            - last_interaction: 最后互动时间戳
            - unlocked_bonds: 已解锁的羁绊列表

    Example:
        ```python
        # 获取当前用户的好感度
        status = get_affection(
            character_id="user_123",
            character_name="小明"
        )
        print(f"当前关系: {status['tier_name']}, 好感度: {status['affection_value']}")
        ```
    """
    # 获取或创建角色数据
    character = await get_character_data(_ctx.chat_key, character_id)
    if not character:
        character = CharacterAffection.create(
            character_id=character_id,
            character_name=character_name,
            initial_affection=config.DEFAULT_AFFECTION,
        )
        await save_character_data(_ctx.chat_key, character)

    tier = character.get_tier()

    return {
        "character_id": character.character_id,
        "character_name": character.character_name,
        "affection_value": character.affection_value,
        "tier": tier.value,
        "tier_name": {
            AffectionTier.ENEMY: "敌人",
            AffectionTier.STRANGER: "陌生人",
            AffectionTier.ACQUAINTANCE: "熟人",
            AffectionTier.FRIEND: "朋友",
            AffectionTier.CLOSE_FRIEND: "密友",
            AffectionTier.SOULMATE: "灵魂伴侣",
        }[tier],
        "total_positive": character.total_positive,
        "total_negative": character.total_negative,
        "first_met": character.first_met_time,
        "last_interaction": character.last_interaction_time,
        "unlocked_bonds": character.get_unlocked_bonds(),
    }


@plugin.mount_sandbox_method(
    SandboxMethodType.BEHAVIOR,
    name="记录好感度变化",
    description="记录一次影响好感度的事件",
)
async def record_affection_change(
    _ctx: schemas.AgentCtx,
    character_id: str,
    character_name: str,
    change_amount: int,
    event_type: str,
    description: str,
    context: Optional[str] = None,
) -> dict:
    """Record Affection Change (记录好感度变化)

    记录一次影响好感度的事件。系统会自动：
    - 更新好感度值（限制在 -100 到 100 之间）
    - 记录事件到历史
    - 检查并解锁符合条件的羁绊

    Args:
        character_id (str): 角色的唯一标识符
        character_name (str): 角色的显示名称
        change_amount (int): 好感度变化值（正数增加，负数减少，范围：-20 到 +20）
        event_type (str): 事件类型 ("positive", "negative", "neutral", "crisis")
        description (str): 事件的简短描述
        context (str, optional): 额外上下文信息

    Returns:
        dict: 更新后的状态，包含:
            - success: 是否成功
            - new_affection: 更新后的好感度
            - tier_changed: 关系等级是否改变
            - new_tier: 新的关系等级
            - unlocked_bonds: 新解锁的羁绊列表（如果有）

    Example:
        ```python
        # 用户表达感谢
        result = record_affection_change(
            character_id="user_123",
            character_name="小明",
            change_amount=5,
            event_type="positive",
            description="用户真诚地表达了感谢",
            context="帮助用户完成了重要任务"
        )

        # 用户提出批评
        result = record_affection_change(
            character_id="user_123",
            character_name="小明",
            change_amount=-3,
            event_type="negative",
            description="用户对回复速度表示不满",
            context="等待时间过长"
        )
        ```
    """
    # 验证 change_amount 范围
    change_amount = max(-20, min(20, change_amount))

    # 获取或创建角色数据
    character = await get_character_data(_ctx.chat_key, character_id)
    if not character:
        character = CharacterAffection.create(
            character_id=character_id,
            character_name=character_name,
            initial_affection=config.DEFAULT_AFFECTION,
        )

    # 记录旧等级
    old_tier = character.get_tier()

    # 创建并添加事件
    event = AffectionEvent.create(
        change_amount=change_amount,
        event_type=event_type,
        description=description,
        context=context,
    )
    character.add_event(event, max_events=config.MAX_HISTORY_EVENTS)

    # 更新好感度值（限制范围）
    character.affection_value = max(-100, min(100, character.affection_value + change_amount))

    # 保存数据
    await save_character_data(_ctx.chat_key, character)

    # 检查羁绊解锁
    new_tier = character.get_tier()
    unlocked_bonds = []

    if config.ENABLE_BOND_SYSTEM:
        for bond_id, bond_def in BOND_DEFINITIONS.items():
            # 检查是否满足解锁条件
            if bond_id not in character.bonds:
                character.bonds[bond_id] = BondStatus.create(bond_id)

            bond_status = character.bonds[bond_id]

            if not bond_status.unlocked:
                should_unlock = False

                # 检查羁绊条件
                if bond_def["condition"] == "always":
                    should_unlock = True
                elif bond_def["condition"].startswith("affection >="):
                    threshold = int(bond_def["condition"].split(">=")[1])
                    should_unlock = character.affection_value >= threshold
                elif bond_def["condition"] == "event_count_positive >= 5":
                    should_unlock = character.total_positive >= 5
                elif bond_def["condition"] == "event_count_positive >= 10":
                    should_unlock = character.total_positive >= 10
                elif bond_def["condition"] == "event_count_positive >= 20":
                    should_unlock = character.total_positive >= 20
                elif bond_def["condition"] == "event_type_crisis_handled >= 3":
                    # 计算处理危机事件的次数
                    crisis_count = sum(
                        1 for e in character.events
                        if e.event_type == "crisis" and e.change_amount > 0
                    )
                    should_unlock = crisis_count >= 3
                elif bond_def["condition"] == "affection >= 80":
                    should_unlock = character.affection_value >= 80

                # tier 条件
                elif bond_def["condition"] == "tier >= friend":
                    should_unlock = new_tier in [
                        AffectionTier.FRIEND,
                        AffectionTier.CLOSE_FRIEND,
                        AffectionTier.SOULMATE,
                    ]

                if should_unlock:
                    bond_status.unlocked = True
                    bond_status.unlock_time = int(time.time())
                    unlocked_bonds.append(bond_id)

        # 保存更新后的羁绊状态
        if unlocked_bonds:
            await save_character_data(_ctx.chat_key, character)

    return {
        "success": True,
        "new_affection": character.affection_value,
        "tier_changed": old_tier != new_tier,
        "new_tier": new_tier.value,
        "new_tier_name": {
            AffectionTier.ENEMY: "敌人",
            AffectionTier.STRANGER: "陌生人",
            AffectionTier.ACQUAINTANCE: "熟人",
            AffectionTier.FRIEND: "朋友",
            AffectionTier.CLOSE_FRIEND: "密友",
            AffectionTier.SOULMATE: "灵魂伴侣",
        }[new_tier],
        "unlocked_bonds": unlocked_bonds,
    }


@plugin.mount_sandbox_method(
    SandboxMethodType.TOOL,
    name="获取互动历史",
    description="获取角色好感度的互动历史记录",
)
async def get_affection_history(
    _ctx: schemas.AgentCtx,
    character_id: str,
    limit: int = 10,
) -> list:
    """Get Affection History (获取互动历史)

    获取指定角色的好感度变化历史记录。

    Args:
        character_id (str): 角色的唯一标识符
        limit (int): 返回的最大记录数量（默认10）

    Returns:
        list: 历史事件列表，每个事件包含:
            - timestamp: 时间戳
            - change_amount: 变化值
            - event_type: 事件类型
            - description: 描述
            - context: 上下文（如果有）

    Example:
        ```python
        # 获取最近5条互动记录
        history = get_affection_history(
            character_id="user_123",
            limit=5
        )
        for event in history:
            print(f"{event['description']} ({event['change_amount']:+d})")
        ```
    """
    character = await get_character_data(_ctx.chat_key, character_id)
    if not character:
        return []

    # 返回最近的事件
    recent_events = character.events[-limit:]
    return [
        {
            "timestamp": event.timestamp,
            "change_amount": event.change_amount,
            "event_type": event.event_type,
            "description": event.description,
            "context": event.context,
        }
        for event in recent_events
    ]


@plugin.mount_sandbox_method(
    SandboxMethodType.TOOL,
    name="获取羁绊信息",
    description="查询可解锁的羁绊列表及其条件",
)
async def get_bond_info(
    _ctx: schemas.AgentCtx,
    character_id: str,
) -> dict:
    """Get Bond Info (获取羁绊信息)

    获取指定角色的羁绊状态和所有可解锁羁绊的条件。

    Args:
        character_id (str): 角色的唯一标识符

    Returns:
        dict: 羁绊信息，包含:
            - total_bonds: 总羁绊数
            - unlocked_count: 已解锁数量
            - bonds: 详细羁绊状态列表

    Example:
        ```python
        bond_info = get_bond_info(character_id="user_123")
        for bond in bond_info['bonds']:
            if not bond['unlocked']:
                print(f"未解锁: {bond['name']} - 需要: {bond['condition_description']}")
        ```
    """
    character = await get_character_data(_ctx.chat_key, character_id)
    if not character:
        character = CharacterAffection.create(
            character_id=character_id,
            character_name="未知",
        )

    bonds_data = []

    for bond_id, bond_def in BOND_DEFINITIONS.items():
        if bond_id not in character.bonds:
            character.bonds[bond_id] = BondStatus.create(bond_id)

        status = character.bonds[bond_id]

        # 计算解锁进度
        progress = 0.0
        condition_desc = ""

        if bond_def["condition"] == "always":
            progress = 1.0
            condition_desc = "初始解锁"
        elif bond_def["condition"] == "affection >= 80":
            progress = min(1.0, character.affection_value / 80)
            condition_desc = f"好感度 ≥ 80 (当前: {character.affection_value})"
        elif bond_def["condition"] == "event_count_positive >= 5":
            progress = min(1.0, character.total_positive / 5)
            condition_desc = f"累计正面互动 ≥ 5 (当前: {character.total_positive})"
        elif bond_def["condition"] == "event_count_positive >= 10":
            progress = min(1.0, character.total_positive / 10)
            condition_desc = f"累计正面互动 ≥ 10 (当前: {character.total_positive})"
        elif bond_def["condition"] == "event_count_positive >= 20":
            progress = min(1.0, character.total_positive / 20)
            condition_desc = f"累计正面互动 ≥ 20 (当前: {character.total_positive})"
        elif bond_def["condition"] == "event_type_crisis_handled >= 3":
            crisis_count = sum(
                1 for e in character.events
                if e.event_type == "crisis" and e.change_amount > 0
            )
            progress = min(1.0, crisis_count / 3)
            condition_desc = f"共渡难关 ≥ 3 (当前: {crisis_count})"
        elif bond_def["condition"] == "tier >= friend":
            tier = character.get_tier()
            tier_order = [
                AffectionTier.ENEMY,
                AffectionTier.STRANGER,
                AffectionTier.ACQUAINTANCE,
                AffectionTier.FRIEND,
                AffectionTier.CLOSE_FRIEND,
                AffectionTier.SOULMATE,
            ]
            tier_index = tier_order.index(tier)
            required_index = tier_order.index(AffectionTier.FRIEND)
            progress = min(1.0, tier_index / required_index) if required_index > 0 else 1.0
            tier_names = {
                AffectionTier.ENEMY: "敌人",
                AffectionTier.STRANGER: "陌生人",
                AffectionTier.ACQUAINTANCE: "熟人",
                AffectionTier.FRIEND: "朋友",
                AffectionTier.CLOSE_FRIEND: "密友",
                AffectionTier.SOULMATE: "灵魂伴侣",
            }
            condition_desc = f"关系达到朋友或以上 (当前: {tier_names[tier]})"

        bonds_data.append({
            "bond_id": bond_id,
            "name": bond_def["name"],
            "description": bond_def["description"],
            "unlocked": status.unlocked,
            "unlock_time": status.unlock_time,
            "progress": round(progress * 100, 1),
            "condition_description": condition_desc,
        })

    return {
        "total_bonds": len(BOND_DEFINITIONS),
        "unlocked_count": sum(1 for b in bonds_data if b["unlocked"]),
        "bonds": bonds_data,
    }


@plugin.mount_sandbox_method(
    SandboxMethodType.BEHAVIOR,
    name="重置好感度",
    description="重置指定角色的好感度数据（谨慎使用）",
)
async def reset_affection(
    _ctx: schemas.AgentCtx,
    character_id: str,
    reason: str,
) -> dict:
    """Reset Affection (重置好感度)

    重置指定角色的好感度数据。这应该是一个谨慎使用的功能。

    Args:
        character_id (str): 角色的唯一标识符
        reason (str): 重置原因（会被记录）

    Returns:
        dict: 重置结果

    Example:
        ```python
        result = reset_affection(
            character_id="user_123",
            reason="用户要求重置关系"
        )
        ```
    """
    character = await get_character_data(_ctx.chat_key, character_id)
    if not character:
        return {"success": False, "message": "角色不存在"}

    # 记录重置前的状态
    old_value = character.affection_value
    old_tier = character.get_tier().value

    # 创建新的角色数据
    character = CharacterAffection.create(
        character_id=character_id,
        character_name=character.character_name,
        initial_affection=config.DEFAULT_AFFECTION,
    )

    # 添加重置事件
    reset_event = AffectionEvent.create(
        change_amount=0,
        event_type="neutral",
        description=f"好感度已重置（原因：{reason}）",
        context=f"重置前: {old_value} ({old_tier})",
    )
    character.events.append(reset_event)

    await save_character_data(_ctx.chat_key, character)

    return {
        "success": True,
        "message": f"已重置 {character.character_name} 的好感度",
        "old_value": old_value,
        "old_tier": old_tier,
        "new_value": character.affection_value,
    }


# ============================================================================
# 生命周期回调 (Lifecycle Callbacks)
# ============================================================================

@plugin.mount_cleanup_method()
async def cleanup():
    """清理插件资源"""
    core.logger.info("好感度系统插件已清理")
