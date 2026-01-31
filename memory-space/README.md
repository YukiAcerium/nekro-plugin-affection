# Yuki Memory Space

> Yuki 的长期知识管理系统 - 即使将来出问题也能恢复

## 项目结构

```
memory-space/
├── README.md                    # 本文件
├── sync_status.json            # 同步状态记录
├── LATEST_SYNC.md              # 最近一次完整同步的信息
│
├── memory/                     # 所有记忆文件
│   ├── MEMORY.md              # 长期记忆
│   ├── IDENTITY.md            # 身份信息
│   ├── USER.md                # 用户信息
│   ├── SOUL.md                # 灵魂配置
│   ├── AGENTS.md              # 工作空间配置
│   ├── TOOLS.md               # 工具配置
│   └── daily/                  # 每日记忆 (YYYY-MM-DD.md)
│
├── skills/                     # 技能配置
│   ├── available/             # 可用技能列表
│   ├── custom/                # 自定义技能
│   └── SKILL_MAPPING.md       # 技能映射表
│
├── configs/                   # 配置文件
│   ├── clawdbot/             # Clawdbot 配置
│   ├── nekro-agent/          # Nekro-Agent 配置
│   └── yuki-research/        # Yuki-Research 配置
│
├── projects/                  # 项目文件
│   ├── active/               # 活跃项目
│   └── archived/             # 归档项目
│
├── credentials/              # 凭证信息（敏感）
│   ├── CREDENTIALS.md        # 凭证索引
│   └── encrypted/            # 加密的凭证文件
│
├── tools/                    # 工具脚本
│   ├── sync.sh               # 同步脚本
│   └── restore.sh            # 恢复脚本
│
└── docs/                     # 文档
    └── SYNC_SCHEDULE.md      # 同步计划文档
```

## 同步策略

- **每天 6:00** (Asia/Shanghai): 自动全量同步
- **触发式**: 重要操作后手动触发

## 恢复流程

1. 克隆此仓库
2. 运行 `./tools/restore.sh`
3. 按照脚本提示恢复各个模块

## 上次同步

请查看 `LATEST_SYNC.md`

## 自动同步

使用 cron job 设置：

```bash
# 每天 6:00 执行同步
0 6 * * * cd /path/to/memory-space && ./tools/sync.sh >> sync.log 2>&1
```
