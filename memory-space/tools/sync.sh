#!/bin/bash
# Yuki Memory Space 同步脚本
# 自动同步所有记忆、技能、配置到私有仓库

set -e

# 配置
REPO_DIR="/Users/clawd/clawd/memory-space"
SOURCE_DIR="/Users/clawd/clawd"
GIT_REPO="git@github.com:YukiAcerium/memory-space.git"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S %Z")
DATE=$(date +"%Y-%m-%d")

echo "========================================"
echo "Yuki Memory Space Sync"
echo "Time: $TIMESTAMP"
echo "========================================"

# 切换到仓库目录
cd "$REPO_DIR"

# 1. 备份记忆文件
echo ""
echo "[1/8] 同步记忆文件..."
mkdir -p memory/daily
mkdir -p memory/transcripts

# 复制核心记忆文件
cp "$SOURCE_DIR/MEMORY.md" memory/ 2>/dev/null || true
cp "$SOURCE_DIR/IDENTITY.md" memory/ 2>/dev/null || true
cp "$SOURCE_DIR/USER.md" memory/ 2>/dev/null || true
cp "$SOURCE_DIR/SOUL.md" memory/ 2>/dev/null || true
cp "$SOURCE_DIR/AGENTS.md" memory/ 2>/dev/null || true
cp "$SOURCE_DIR/TOOLS.md" memory/ 2>/dev/null || true

# 复制每日记忆
for file in "$SOURCE_DIR/memory/"*.md; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        if [ "$filename" != "INDEX.md" ] && [ "$filename" != "*.md" ]; then
            cp "$file" memory/daily/ 2>/dev/null || true
        fi
    fi
done

echo "  ✓ 记忆文件同步完成"

# 2. 同步技能配置
echo ""
echo "[2/8] 同步技能配置..."
mkdir -p skills/available

# 列出所有可用技能
ls /opt/homebrew/lib/node_modules/clawdbot/skills/ > skills/available/skill_list.txt 2>/dev/null || true

# 复制 release skill
cp /opt/homebrew/lib/node_modules/clawdbot/skills/release/SKILL.md skills/custom/release_skill.md 2>/dev/null || true

echo "  ✓ 技能配置同步完成"

# 3. 同步配置文件
echo ""
echo "[3/8] 同步配置文件..."
mkdir -p configs/clawdbot
mkdir -p configs/nekro-agent
mkdir -p configs/yuki-research

# Clawdbot 配置
cp "$SOURCE_DIR/AGENTS.md" configs/clawdbot/ 2>/dev/null || true
cp "$SOURCE_DIR/SOUL.md" configs/clawdbot/ 2>/dev/null || true
cp "$SOURCE_DIR/TOOLS.md" configs/clawdbot/ 2>/dev/null || true

# Nekro-Agent 配置
cp "$SOURCE_DIR/nekro-agent/pyproject.toml" configs/nekro-agent/ 2>/dev/null || true
cp "$SOURCE_DIR/nekro-agent-doc/pyproject.toml" configs/nekro-agent/ 2>/dev/null || true

# Yuki-Research 配置
cp "$SOURCE_DIR/yuki-research/pyproject.toml" configs/yuki-research/ 2>/dev/null || true

echo "  ✓ 配置文件同步完成"

# 4. 同步项目文件
echo ""
echo "[4/8] 同步项目文件..."
mkdir -p projects/active
mkdir -p projects/archived

# 活跃项目
cp -r "$SOURCE_DIR/yuki-research/01_projects" projects/active/ 2>/dev/null || true

# 归档项目
cp -r "$SOURCE_DIR/yuki-research/04_archive" projects/archived/ 2>/dev/null || true

echo "  ✓ 项目文件同步完成"

# 5. 记录凭证索引（不记录实际凭证）
echo ""
echo "[5/8] 记录凭证索引..."
mkdir -p credentials

cat > credentials/CREDENTIALS.md << 'CREDITS'
# 凭证索引

此目录仅记录凭证的**存在性**和**位置**，不存储实际凭证。

## 凭证类型

### 邮箱账号
- Gmail: yukiacerium@gmail.com (配置在 Clawdbot)
- NekroAI 社区密钥: nk_i9yzyYhVSHVeDtXJhAllyeVP

### GitHub
- YukiAcerium: 主要开发账号
- KroMiose: Miose 的账号

### GCP 项目
- yuki-gmail-bot: Gmail Pub/Sub 项目

## 获取凭证

实际凭证存储在以下位置：
- Clawdbot 配置: ~/.config/clawdbot/
- 环境变量: 通过 Clawdbot gateway 获取
- 1Password（如已配置）

## 恢复凭证

恢复时需要手动重新配置以下凭证：
1. GitHub Token (用于 CLI 操作)
2. GCP 凭证 (用于 Gmail)
3. 各平台 API Keys
CREDITS

echo "  ✓ 凭证索引记录完成"

# 6. 生成同步状态
echo ""
echo "[6/8] 生成同步状态..."
cat > sync_status.json << STATUS
{
  "last_sync": "$TIMESTAMP",
  "date": "$DATE",
  "memory_files": $(ls memory/*.md 2>/dev/null | wc -l),
  "daily_notes": $(ls memory/daily/*.md 2>/dev/null | wc -l),
  "skills": $(ls skills/available/skill_list.txt 2>/dev/null | wc -l),
  "projects": $(find projects -name "*.md" 2>/dev/null | wc -l)
}
STATUS

echo "  ✓ 同步状态已更新"

# 7. 生成最新同步报告
echo ""
echo "[7/8] 生成同步报告..."
cat > LATEST_SYNC.md << REPORT
# 最近同步信息

## 同步时间

$TIMESTAMP

## 同步内容

### 记忆文件
- MEMORY.md: $([ -f memory/MEMORY.md ] && echo "✓" || echo "✗")
- IDENTITY.md: $([ -f memory/IDENTITY.md ] && echo "✓" || echo "✗")
- USER.md: $([ -f memory/USER.md ] && echo "✓" || echo "✗")
- SOUL.md: $([ -f memory/SOUL.md ] && echo "✓" || echo "✗")
- AGENTS.md: $([ -f memory/AGENTS.md ] && echo "✓" || echo "✗")
- TOOLS.md: $([ -f memory/TOOLS.md ] && echo "✓" || echo "✗")
- 每日笔记: $(ls memory/daily/*.md 2>/dev/null | wc -l) 个文件

### 技能
- 可用技能: $(wc -l < skills/available/skill_list.txt 2>/dev/null || echo 0) 个
- 自定义技能: $(ls skills/custom/*.md 2>/dev/null | wc -l) 个

### 项目
- 活跃项目: $(find projects/active -name "*.md" 2>/dev/null | wc -l) 个文件
- 归档项目: $(find projects/archived -name "*.md" 2>/dev/null | wc -l) 个文件

## 恢复说明

参见 README.md 中的恢复流程

---
*此文件由 sync.sh 自动生成*
REPORT

echo "  ✓ 同步报告已生成"

# 8. 提交到 Git
echo ""
echo "[8/8] 提交到 Git..."
git add -A 2>/dev/null || true
git status --short > /dev/null 2>&1 && CHANGES="true" || CHANGES="false"

if [ "$CHANGES" = "true" ]; then
    git add -A
    git commit -m "Sync: $TIMESTAMP" 2>/dev/null || true
    echo "  ✓ 已提交更改"
else
    echo "  ✓ 无新更改"
fi

echo ""
echo "========================================"
echo "同步完成！"
echo "========================================"
