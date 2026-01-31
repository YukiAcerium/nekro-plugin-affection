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
