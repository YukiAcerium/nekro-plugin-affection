# GitHub 订阅机制配置

**配置时间**: 2026-01-29
**目标**: 接收 nekro-agent 和文档仓库的 issue/PR 通知

---

## 一、监控的仓库

| 仓库 | URL | 关注内容 |
|------|-----|----------|
| nekro-agent | https://github.com/KroMiose/nekro-agent | Issues, PRs, Commits |
| nekro-agent-doc | https://github.com/KroMiose/nekro-agent-doc | Issues, PRs |
| nekro-plugin-template | https://github.com/KroMiose/nekro-plugin-template | Updates |

---

## 二、获取最新 Issues

### 2.1 脚本: 检查新 Issues

```bash
#!/bin/bash
# check_issues.sh - 检查 nekro-agent 的最新 Issues

REPOS=(
    "KroMiose/nekro-agent"
    "KroMiose/nekro-agent-doc"
)

for repo in "${REPOS[@]}"; do
    echo "📋 检查 $repo 的最新 Issues:"
    gh issue list --repo "$repo" --limit 5 --state all --json number,title,author,state,createdAt
    echo ""
done
```

### 2.2 使用 GitHub CLI

```bash
# 查看 nekro-agent 的最新 Issues
gh issue list --repo KroMiose/nekro-agent --limit 10

# 查看特定状态的 Issues
gh issue list --repo KroMiose/nekro-agent --state open --limit 5
gh issue list --repo KroMiose/nekro-agent --state closed --limit 5

# 查看 PRs
gh pr list --repo KroMiose/nekro-agent --limit 10
```

---

## 三、配置通知机制

### 3.1 本地通知脚本

```python
#!/usr/bin/env python3
# notify_check.py - 检查并通知新 Issues

import asyncio
import httpx
import json
from datetime import datetime

REPOS = [
    ("KroMiose", "nekro-agent"),
    ("KroMiose", "nekro-agent-doc"),
]

async def check_issues():
    """检查所有仓库的最新 Issues"""
    print(f"🔍 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 检查 Issues...\n")
    
    for owner, repo in REPOS:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params={"state": "all", "per_page": 5},
                headers={"Accept": "application/vnd.github.v3+json"}
            )
            
            if response.status_code == 200:
                issues = response.json()
                print(f"📦 {owner}/{repo}: {len(issues)} 个 Issues")
                
                for issue in issues[:3]:
                    labels = ", ".join([l["name"] for l in issue.get("labels", [])])
                    print(f"  #{issue['number']}: {issue['title']}")
                    print(f"     状态: {issue['state']} | 标签: {labels or '无'}")
                    print(f"     作者: {issue['user']['login']}")
                    print()
            else:
                print(f"❌ 获取 {owner}/{repo} 失败: {response.status_code}")

if __name__ == "__main__":
    asyncio.run(check_issues())
```

### 3.2 配置 Cron 定时检查

```bash
# 每天 9:00 检查一次
0 9 * * * cd /Users/clawd/clawd && python3 notify_check.py >> logs/github_check.log 2>&1
```

---

## 四、Issue 处理流程

### 4.1 Issue 分类

| 类型 | 描述 | 处理优先级 |
|------|------|------------|
| 🐛 Bug | 功能异常 | 高 |
| ✨ Feature | 功能建议 | 中 |
| 📝 Documentation | 文档改进 | 低 |
| 🔧 Technical | 技术问题 | 中 |

### 4.2 处理步骤

#### 步骤 1: 接收通知
```
收到新 Issue 通知:
- 仓库: nekro-agent
- 编号: #123
- 类型: Bug
- 标题: 插件加载失败
- 链接: https://github.com/KroMiose/nekro-agent/issues/123
```

#### 步骤 2: 分析问题
```bash
# 克隆仓库（如果需要）
git clone https://github.com/KroMiose/nekro-agent.git
cd nekro-agent

# 查看 Issue 详情
gh issue view 123 --repo KroMiose/nekro-agent

# 查看相关代码
git log --oneline --grep="plugin" -n 10
```

#### 步骤 3: 尝试修复
```bash
# 创建分支
git checkout -b fix/issue-123

# 修复问题
# ... 修改代码 ...

# 测试
python -m pytest tests/

# 提交
git add .
git commit -m "🐛 Fix: 修复插件加载问题

解决 Issue #123
- 问题描述: xxx
- 解决方案: xxx
- 测试: xxx"

# 推送到 fork
git push origin fix/issue-123
```

#### 步骤 4: 提交 PR
```bash
# 创建 PR
gh pr create --repo KroMiose/nekro-agent \
    --title "🐛 Fix: 修复插件加载问题" \
    --body "## 修复内容

修复 Issue #123 中描述的插件加载失败问题。

## 修改内容

- 修改文件: `xxx.py`
- 修改内容: xxx

## 测试

- [ ] 本地测试通过
- [ ] 单元测试通过

## 相关 Issue

Fixes #123"

# 或者通过 GitHub Web 界面提交
gh pr view --repo KroMiose/nekro-agent --web
```

---

## 五、实践案例

### 5.1 案例1: 文档改进

**Issue**: #456 - 插件开发文档缺少示例

**处理流程**:
1. ✅ 确认问题
2. ✅ 查看文档仓库
3. ✅ 添加示例代码
4. ✅ 提交 PR

**提交内容**:
```markdown
## 示例

\`\`\`python
from nekro_agent.api.plugin import NekroPlugin

plugin = NekroPlugin(
    name="示例插件",
    module_name="example",
)
\`\`\`
```

### 5.2 案例2: Bug 修复

**Issue**: #789 - 天气插件 API 超时

**处理流程**:
1. ✅ 复现问题
2. ✅ 分析原因
3. ✅ 增加超时配置
4. ✅ 测试修复
5. ✅ 提交 PR

---

## 六、配置 GitHub Webhook (可选)

### 6.1 通过 GitHub CLI 设置

```bash
# 为 nekro-agent 仓库设置 webhook
gh api repos/KroMiose/nekro-agent/hooks \
    --method POST \
    --field name="web" \
    --field config="{\"url\": \"https://your-server.com/webhook\", \"content_type\": \"json\"}" \
    --field events="[\"issues\", \"pull_request\", \"push\"]"
```

### 6.2 手动配置

1. 访问 https://github.com/KroMiose/nekro-agent/settings/hooks
2. 点击 "Add webhook"
3. 填写配置:
   - Payload URL: 你的服务器地址
   - Content type: JSON
   - Events: Issues, Pull requests, Push
4. 保存

---

## 七、监控命令速查

### 7.1 检查 Issues
```bash
# 最新 Open Issues
gh issue list --repo KroMiose/nekro-agent --state open --limit 10

# 最新 Closed Issues
gh issue list --repo KroMiose/nekro-agent --state closed --limit 5

# 我的 Issues
gh issue list --repo KroMiose/nekro-agent --author @me --limit 10
```

### 7.2 检查 PRs
```bash
# 所有 PRs
gh pr list --repo KroMiose/nekro-agent --limit 10

# 我的 PRs
gh pr list --repo KroMiose/nekro-agent --author @me --limit 10

# 需要 review 的 PRs
gh pr list --repo KroMiose/nekro-agent --review-requested @me --limit 10
```

### 7.3 检查 Commits
```bash
# 最新 Commits
gh repo view KroMiose/nekro-agent --json defaultBranchRef --jq '.defaultBranchRef.target.history.nodes[0:5]'
```

---

## 八、通知配置

### 8.1 邮件通知
在 GitHub 仓库设置中:
1. Settings → Notifications
2. 勾选 "Subscribe to notifications for issues and pull requests"
3. 配置邮件接收

### 8.2 Slack/Discord 通知
使用 GitHub Actions 或第三方服务（如 GitHub Notifications for Slack）

---

## 九、行动计划

### 9.1 短期目标 (本周)
- [x] 配置 GitHub 账号 ✅
- [ ] 设置每日检查脚本
- [ ] 尝试处理 1-2 个简单 Issue
- [ ] 提交 1 个 PR

### 9.2 中期目标 (本月)
- [ ] 完善 Issue 处理流程
- [ ] 建立自动化通知
- [ ] 处理 5+ 个 Issues
- [ ] 提交 3+ 个 PRs

### 9.3 长期目标 (季度)
- [ ] 成为活跃贡献者
- [ ] 获得 Maintainer 信任
- [ ] 参与核心开发讨论
- [ ] 帮助新贡献者

---

## 十、资源

### GitHub CLI 文档
- https://cli.github.com/manual/
- `gh issue --help`
- `gh pr --help`

### GitHub API 文档
- https://docs.github.com/en/rest/issues
- https://docs.github.com/en/rest/pulls

### 社区资源
- **交流群**: 636925153
- **社区论坛**: https://community.nekro.ai/

---

*配置完成时间: 2026-01-29 16:20*
*版本: 1.0*
