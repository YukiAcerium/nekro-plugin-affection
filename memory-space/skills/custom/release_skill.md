# NekroAgent 发布与更新日志技能

> 帮助正确发布版本和编写更新日志的完整指南

## 核心原则

1. **只使用已发布的 release 内容** - 不要自己发挥或简化
2. **验证每个贡献者** - 使用 GitHub API 查询真实的 username
3. **保持格式一致** - 与历史 release 格式完全一致
4. **源码分析要深入** - 逐个 commit 分析功能变更

---

## 常见错误警示

### 贡献者名字错误

| 错误写法 | 正确写法 | 问题原因 |
|----------|----------|----------|
| @Furina | @liugu2023 | Furina 是 GitHub name 字段，不是 username |
| @luoyunfa | @yang208115 | luoyunfa 是 GitHub name 字段，不是 username |
| @茗 | @wess09 | 茗 是 GitHub name 字段，不是 username |
| @liugu | @liugu2023 | liugu 是 co-author 邮箱，不是 GitHub 用户 |
| @zbc | @ZerBC | GitHub username 大小写敏感 |

### 格式错误

| 错误做法 | 正确做法 |
|----------|----------|
| 简化内容、删除技术细节 | 保持完整变更描述 |
| 使用"变更详情"等自定义格式 | 严格复制已发布 release 格式 |
| 自己发挥添加内容 | 只使用已发布的内容 |

---

## 技能使用流程

### 第一步：获取目标版本的 release 内容

```bash
# 获取最新 release 内容
gh release view v2.2.0 --repo KroMiose/nekro-agent --json body -q '.body' > release.md

# 或从网页获取
web_fetch https://github.com/KroMiose/nekro-agent/releases/tag/v2.2.0
```

### 第二步：验证贡献者信息

```bash
# 获取 PR 作者信息
gh pr view 186 -R KroMiose/nekro-agent --json author -q '.author.login'

# 获取 commit 作者信息
git log v2.1.0..HEAD --oneline --format="%h %an %s"

# 验证用户信息（检查 name 字段）
gh api users/liugu2023 -q '.login, .name'
# 输出: liugu2023, Furina
# 结论: liugu2023 的 name 是 Furina，所以 commit 显示 Furina
```

**关键命令**：

```bash
# 1. 获取 PR 作者
gh pr view <PR号> -R KroMiose/nekro-agent --json author -q '.author.login'

# 2. 获取 commit 作者
git log <range> --oneline --format="%h %an %s"

# 3. 验证 GitHub 用户信息
gh api users/<username> -q '.login, .name, .html_url'

# 4. 检查是否为首次贡献
gh pr list -R KroMiose/nekro-agent --author <username> --state merged --created-at
```

### 第三步：源码分析

```bash
# 获取版本范围内的所有 commit
git log v2.1.0..HEAD --oneline

# 按作者分类
git log v2.1.0..HEAD --oneline --format="%h %an %s" | \
  awk '{print $2}' | sort | uniq -c | sort -rn

# 查找特定功能的 commit
git log v2.1.0..HEAD --oneline --grep="JSON"     # JSON 相关
git log v2.1.0..HEAD --oneline --grep="email"    # Email 相关
git log v2.1.0..HEAD --oneline --grep="i18n"     # 国际化相关

# 查看具体文件的变更
git show <commit> --stat
```

### 第四步：保持格式一致

**必须复制的格式元素**：

```markdown
## 版本号：功能名称

## 重点更新：XXX

### XXX

- 变更详情: xxx
- 对您的影响:

xxx

- xxx

感谢 [@username](https://github.com/username) 贡献了此功能的实现

---

## 功能增强

### 功能名称

- 变更详情: xxx
- 对您的影响: xxx

感谢 [@username](https://github.com/username) 贡献了此功能的实现

---

## 性能优化与问题修复

### 分类名称

- 问题描述 ([#PR号](link)): 详细说明

---

## New Contributors

- [@username](https://github.com/username) made their first contribution in [#PR号](link)

---

Full Changelog: [v旧版本...v新版本](link)
```

---

## 贡献者验证清单

### 每个贡献者必须验证以下信息：

1. ✅ GitHub username (用于 @ 引用)
2. ✅ GitHub profile URL (用于链接)
3. ✅ 首次贡献的 PR 号
4. ✅ 确认是首次贡献（不在历史版本中）

### 验证脚本

```bash
#!/bin/bash
# verify_contributors.sh

REPO="KroMiose/nekro-agent"
OLD_VERSION="v2.1.0"
NEW_VERSION="v2.2.0"

echo "=== 验证 $NEW_VERSION 的贡献者 ==="
echo ""

# 获取新版本的 commit
COMMITS=$(git log $OLD_VERSION..$NEW_VERSION --oneline --format="%h %an %s")

# 提取非 KroMiose 的作者
echo "非 KroMiose 的贡献者:"
echo "$COMMITS" | grep -v "KroMiose" | awk '{print $2}' | sort | uniq
echo ""

# 检查每个贡献者
for author in $(echo "$COMMITS" | grep -v "KroMiose" | awk '{print $2}' | sort | uniq); do
  echo "=== $author ==="
  
  # 获取 GitHub 信息
  gh api users/$author -q '.login, .name, .html_url' 2>/dev/null || echo "用户不存在或 API 失败"
  
  # 检查是否是首次贡献
  first_pr=$(gh pr list -R $REPO --author $author --state merged --json createdAt --jq '.[0].createdAt' 2>/dev/null)
  echo "首次 PR: $first_pr"
  echo ""
done
```

---

## 源码分析清单

### 必须分析的 commit 类型：

| 类型 | 分析方法 |
|------|----------|
| **feat** | 查看新增了哪些功能，修改了哪些文件 |
| **fix** | 查看修复了什么问题，影响范围 |
| **refactor** | 查看重构了哪些模块 |
| **docs** | 查看文档变更内容 |

### 分析模板：

```markdown
### 功能名称

**Commit**: [hash](link)
**作者**: username
**文件**: 修改的文件列表

**功能描述**:
- 从源码中提取功能描述
- 避免使用 commit message 的简短描述

**核心代码位置**:
- `path/to/file.py` - 主要逻辑
```

---

## 发布前检查清单

### 内容检查

- [ ] 更新日志内容与已发布 release 完全一致
- [ ] 所有链接可访问
- [ ] 格式与历史 release 一致

### 贡献者检查

- [ ] 每个贡献者都有 GitHub 链接
- [ ] 贡献者 username 正确（不是 name 字段）
- [ ] PR 号正确
- [ ] 确认是首次贡献

### 格式检查

- [ ] 使用正确的标题格式
- [ ] 保持 `变更详情:` / `对您的影响:` 结构
- [ ] 贡献者链接格式正确
- [ ] New Contributors 格式正确

---

## GitHub CLI 常用命令速查

```bash
# Release 相关
gh release view v2.2.0 --repo KroMiose/nekro-agent
gh release create v2.2.0 --repo KroMiose/nekro-agent --title "v2.2.0" --notes-file release.md

# PR 相关
gh pr list -R KroMiose/nekro-agent --state merged
gh pr view 186 -R KroMiose/nekro-agent --json author,title,body
gh pr checks 186 -R KroMiose/nekro-agent

# Commit 相关
git log --oneline v2.1.0..HEAD
git log --oneline --format="%h %an %s"
git show <commit> --stat

# 用户相关
gh api users/username -q '.login, .name, .html_url'
gh pr list -R KroMiose/nekro-agent --author username --state merged
```

---

## 错误处理

### 常见问题和解决方案

| 问题 | 解决方案 |
|------|----------|
| 用户名找不到 | 使用 `gh api users/<username>` 验证 |
| 不知道用户名 | 从 commit log 中提取，格式为 `git log --format="%an"` |
| 区分 name 和 login | `gh api users/<username> -q '.login, .name'` |
| 首次贡献者不确定 | 检查 `gh pr list --author` 的最早 PR 创建时间 |
| co-author 处理 | co-author 邮箱不是 GitHub 用户，不单独列出 |

### 调试命令

```bash
# 检查 commit 作者
git show <commit> --format=fuller

# 检查 commit 中的 co-author
git log <commit> -1 --format="%b" | grep -i "co-authored"

# 检查用户在 GitHub 的信息
curl -s https://api.github.com/users/<username> | jq '.login, .name, .html_url'
```

---

## 输出示例

### 正确的 New Contributors 格式

```markdown
## New Contributors

- [@YukiAcerium](https://github.com/YukiAcerium) made their first contribution in [#174](https://github.com/KroMiose/nekro-agent/pull/174)

- [@ZerBC](https://github.com/ZerBC) made their first contribution in [#176](https://github.com/KroMiose/nekro-agent/pull/176)

- [@XG2020](https://github.com/XG2020) made their first contribution in [#180](https://github.com/KroMiose/nekro-agent/pull/180)
```

### 正确的贡献者感谢格式

```markdown
感谢 [@liugu2023](https://github.com/liugu2023) 贡献了此功能的实现
```

### 正确的 PR 引用格式

```markdown
- 修复前端复制失效 bug ([#187](https://github.com/KroMiose/nekro-agent/pull/187))
```

---

## 完整工作流程示例

```bash
#!/bin/bash
# generate_changelog.sh

OLD_VERSION="v2.1.0"
NEW_VERSION="v2.2.0"
REPO="KroMiose/nekro-agent"

echo "=== 生成 $NEW_VERSION 更新日志 ==="
echo ""

# 1. 获取 release 内容
echo "获取 release 内容..."
gh release view $NEW_VERSION -R $REPO --json body -q '.body' > release.md

# 2. 获取贡献者
echo "获取贡献者..."
git log $OLD_VERSION..HEAD --oneline --format="%h %an %s" > commits.txt

# 3. 提取非 KroMiose 的贡献者
echo "贡献者:"
cat commits.txt | grep -v "KroMiose" | awk '{print $2}' | sort | uniq

# 4. 验证每个贡献者
for author in $(cat commits.txt | grep -v "KroMiose" | awk '{print $2}' | sort | uniq); do
  echo ""
  echo "=== 验证 $author ==="
  gh api users/$author -q '.login, .name, .html_url' 2>/dev/null || echo "用户不存在"
done

echo ""
echo "=== 完成 ==="
```

---

## 总结

### 关键要点

1. **只复制已发布的内容** - 不要自己写或简化
2. **验证每个贡献者** - 使用 GitHub API 查询真实 username
3. **区分 name 和 login** - GitHub name 不是 username
4. **保持格式一致** - 与历史 release 完全一致

### 快速检查

- [ ] 所有 @username 都能在 GitHub 上找到
- [ ] 所有 PR 链接都能访问
- [ ] 格式与最近发布的 release 一致
- [ ] New Contributors 只包含真正的首次贡献者
