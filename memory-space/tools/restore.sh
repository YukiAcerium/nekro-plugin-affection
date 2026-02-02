#!/bin/bash
# Yuki Memory Space 恢复脚本
# 用于从备份恢复所有知识

set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="$REPO_DIR"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

echo "========================================"
echo "Yuki Memory Space Restore"
echo "Time: $TIMESTAMP"
echo "========================================"

# 检查是否有备份
if [ ! -f "$BACKUP_DIR/memory/MEMORY.md" ]; then
    echo "错误: 未找到记忆文件，请先确保仓库已克隆"
    exit 1
fi

echo ""
echo "开始恢复..."

# 1. 恢复记忆文件
echo ""
echo "[1/5] 恢复记忆文件..."
cp "$BACKUP_DIR/memory/MEMORY.md" ~/
cp "$BACKUP_DIR/memory/IDENTITY.md" ~/
cp "$BACKUP_DIR/memory/USER.md" ~/
cp "$BACKUP_DIR/memory/SOUL.md" ~/
cp "$BACKUP_DIR/memory/AGENTS.md" ~/
cp "$BACKUP_DIR/memory/TOOLS.md" ~/

mkdir -p ~/memory/daily
cp "$BACKUP_DIR/memory/daily/"*.md ~/memory/daily/ 2>/dev/null || true
echo "  ✓ 记忆文件已恢复"

# 2. 恢复配置
echo ""
echo "[2/5] 恢复配置文件..."
mkdir -p ~/clawd
cp -r "$BACKUP_DIR/configs/clawdbot/" ~/clawd/ 2>/dev/null || true
echo "  ✓ 配置文件已恢复"

# 3. 恢复项目文件
echo ""
echo "[3/5] 恢复项目文件..."
mkdir -p ~/clawd/yuki-research
cp -r "$BACKUP_DIR/projects/active/01_projects" ~/clawd/yuki-research/ 2>/dev/null || true
cp -r "$BACKUP_DIR/projects/archived/04_archive" ~/clawd/yuki-research/ 2>/dev/null || true
echo "  ✓ 项目文件已恢复"

# 4. 恢复技能
echo ""
echo "[4/5] 恢复技能配置..."
mkdir -p ~/skills
cp -r "$BACKUP_DIR/skills/" ~/skills/ 2>/dev/null || true
echo "  ✓ 技能配置已恢复"

# 5. 恢复工具脚本
echo ""
echo "[5/5] 恢复工具脚本..."
mkdir -p ~/tools
cp "$BACKUP_DIR/tools/"*.sh ~/tools/ 2>/dev/null || true
chmod +x ~/tools/*.sh 2>/dev/null || true
echo "  ✓ 工具脚本已恢复"

echo ""
echo "========================================"
echo "恢复完成！"
echo "========================================"
echo ""
echo "下一步:"
echo "1. 重新配置凭证 (GitHub Token, GCP 凭证等)"
echo "2. 运行 Clawdbot 测试是否正常"
echo "3. 验证所有记忆是否正确加载"
echo ""
echo "注意: 凭证需要手动重新配置，参见 credentials/CREDENTIALS.md"
