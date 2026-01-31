# 发布检查清单

## 贡献者验证（必须执行）

```bash
# 错误写法 vs 正确写法
@Furina → @liugu2023  (Furina 是 name，不是 username)
@luoyunfa → @yang208115 (luoyunfa 是 name，不是 username)
@茗 → @wess09 (茗 是 name，不是 username)
@liugu → @liugu2023 (liugu 是 co-author 邮箱)
@zbc → @ZerBC (大小写敏感)
```

## 验证命令

```bash
# 1. 获取 commit 作者
git log v2.1.0..HEAD --oneline --format="%h %an %s"

# 2. 验证 GitHub 用户
gh api users/liugu2023 -q '.login, .name, .html_url'

# 3. 检查首次贡献
gh pr list -R KroMiose/nekro-agent --author XG2020 --state merged
```

## 发布前检查

- [ ] release 内容与 GitHub 完全一致
- [ ] 所有 @username 都是真实的 GitHub username
- [ ] 格式与历史 release 一致
- [ ] New Contributors 只包含首次贡献者
