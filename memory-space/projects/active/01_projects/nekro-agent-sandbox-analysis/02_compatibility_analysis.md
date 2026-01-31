# 沙盒权限问题兼容性分析

## 研究日期

2026-01-30

## 研究目标

结合文档站部署流程，分析沙盒权限问题的兼容性影响，提供平滑升级方案。

---

## 一、当前部署流程分析

### 1.1 文档站标准部署流程

**文档**: `docs/02_quick_start/deploy/linux.md`

```bash
# 方式一：标准部署（推荐）
sudo -E bash -c "$(curl -fsSL https://raw.githubusercontent.com/KroMiose/nekro-agent/main/docker/install.sh)" - --with-napcat

# 方式二：核心部署
sudo -E bash -c "$(curl -fsSL https://raw.githubusercontent.com/KroMiose/nekro-agent/main/docker/install.sh)"
```

**关键配置**:
- 默认安装目录: `~/srv/nekro_agent`
- 端口: `8021/tcp` (主服务), `6099/tcp` (Napcat)
- 运行方式: Docker Compose

### 1.2 安装脚本权限处理

**文件**: `docker/install.sh`

```bash
# 第 237-238 行
# 设置开放目录权限
sudo chmod -R 777 "$NEKRO_DATA_DIR"
```

**问题分析**:
| 步骤 | 操作 | 结果 |
|------|------|------|
| 1 | `mkdir -p "$NEKRO_DATA_DIR"` | 目录创建（sudo） |
| 2 | `sudo chmod -R 777` | 权限开放（777） |
| 3 | Docker 启动容器 | 容器内 nobody 写入 |
| 4 | 容器写入共享目录 | 文件归属 nobody |

### 1.3 开发环境配置

**文档**: `docs/05_app_dev/dev_linux.md`

```bash
# 拉取沙盒镜像
sudo bash sandbox.sh --pull

# 添加用户到 docker 组（可选）
sudo usermod -aG docker $USER

# 运行 Bot
nb run
```

---

## 二、兼容性影响分析

### 2.1 现有用户可能遇到的问题

#### 问题 1：目录权限混乱

**场景**: 旧版本用户升级后

```
升级前状态:
├── data/
│   ├── sandboxes/          (nobody:nobody, 777)
│   │   ├── .packages/      (nobody:nobody)
│   │   └── .pip_cache/     (nobody:nobody)
│   └── plugins/
│       └── workdir/        (用户:用户)

升级后:
├── data/
│   ├── sandboxes/          (nobody:nobody, 777)
│   │   ├── .packages/      (nobody:nobody) ⚠️ 无法修改
│   │   └── .pip_cache/     (nobody:nobody) ⚠️ 无法修改
│   └── plugins/
│       └── workdir/        (nobody:nobody) ⚠️ 无法编辑
```

**影响**:
- ❌ VSCode 无法保存插件文件
- ❌ git 无法提交更改的文件
- ❌ 动态包安装失败

#### 问题 2：沙盒镜像不兼容

**场景**: 使用旧版沙盒镜像运行新版代码

| 组件 | 旧版本 | 新版本 | 兼容问题 |
|------|--------|--------|----------|
| 沙盒镜像 | Python 3.10 | Python 3.11 | 依赖不兼容 |
| 动态包 | 无隔离 | 独立目录 | 路径冲突 |
| 权限配置 | chmod 777 | ACL 机制 | 所有权混乱 |

#### 问题 3：Docker Compose 配置变更

**场景**: 更新 docker-compose.yml 后

**旧配置**:
```yaml
sandbox:
  image: kromiose/nekro-agent-sandbox:latest
  user: "nobody"
```

**新配置（建议）**:
```yaml
sandbox:
  image: kromiose/nekro-agent-sandbox:v2.2.0
  user: "${HOST_UID:-1000}:${HOST_GID:-1000}"
```

**影响**:
- ❌ 现有容器无法启动
- ❌ 端口映射冲突
- ❌ 网络配置变化

### 2.2 不同用户群体的兼容性需求

| 用户群体 | 当前状态 | 兼容性需求 |
|----------|----------|------------|
| **Docker 部署用户** | 使用 install.sh | 脚本自动处理，无需手动干预 |
| **开发环境用户** | 使用 nb run | 需要手动配置权限 |
| **升级用户** | 从旧版本升级 | 需要数据迁移脚本 |
| **全新安装用户** | 新安装 | 不受影响 |

---

## 三、平滑升级方案

### 3.1 升级策略原则

1. **向后兼容**: 旧配置继续工作
2. **渐进式迁移**: 分阶段推出新功能
3. **自动化处理**: 尽可能自动修复问题
4. **用户可选择**: 提供手动干预选项

### 3.2 Docker 部署用户（推荐方案）

#### 方案 A：自动迁移脚本

```bash
#!/bin/bash
# migrate_sandbox_permissions.sh

set -e

NEKRO_DATA_DIR="${NEKRO_DATA_DIR:-${HOME}/srv/nekro_agent}"

echo "=== NekroAgent 沙盒权限迁移脚本 ==="
echo "数据目录: $NEKRO_DATA_DIR"
echo ""

# 1. 停止服务
echo "1. 停止服务..."
cd "$NEKRO_DATA_DIR"
sudo docker compose down || sudo docker-compose down

# 2. 备份数据
echo "2. 备份数据..."
if [ ! -d "data/sandboxes_backup" ]; then
    cp -r "data/sandboxes" "data/sandboxes_backup"
    echo "已备份 sandboxes 目录"
fi

# 3. 重置目录所有权
echo "3. 重置目录所有权..."
CURRENT_USER=$(whoami)
CURRENT_GROUP=$(id -gn $CURRENT_USER)

# 重置沙盒目录
sudo chown -R "$CURRENT_USER:$CURRENT_GROUP" "data/sandboxes/"
sudo chmod -R 755 "data/sandboxes/"

# 重置插件工作目录
sudo chown -R "$CURRENT_USER:$CURRENT_GROUP" "data/plugins/workdir/"
sudo chmod -R 755 "data/plugins/workdir/"

# 4. 清理旧容器
echo "4. 清理旧沙盒容器..."
sudo docker ps -a | grep nekro-agent-sandbox | awk '{print $1}' | xargs -r sudo docker rm -f

# 5. 拉取新镜像
echo "5. 拉取新沙盒镜像..."
sudo docker pull kromiose/nekro-agent-sandbox:v2.2.0

# 6. 更新 docker-compose.yml
echo "6. 更新配置..."
if [ -f "docker-compose.yml" ]; then
    cp "docker-compose.yml" "docker-compose.yml.bak"
    echo "已备份 docker-compose.yml"
fi

# 7. 启动服务
echo "7. 启动服务..."
sudo docker compose up -d || sudo docker-compose up -d

echo ""
echo "=== 迁移完成 ==="
echo "请执行以下操作："
echo "1. 添加用户到 docker 组: sudo usermod -aG docker $CURRENT_USER"
echo "2. 重启 shell 使权限生效"
echo "3. 验证服务正常运行"
```

#### 方案 B：用户手动操作

```bash
# 1. 停止服务
cd ~/srv/nekro_agent
sudo docker compose down

# 2. 重置权限
sudo chown -R $(whoami):$(id -gn $(whoami)) data/sandboxes/
sudo chmod -R 755 data/sandboxes/

# 3. 清理旧容器
sudo docker ps -a | grep nekro-agent-sandbox | awk '{print $1}' | xargs -r sudo docker rm -f

# 4. 拉取新镜像
sudo docker pull kromiose/nekro-agent-sandbox:v2.2.0

# 5. 启动服务
sudo docker compose up -d
```

### 3.3 开发环境用户

#### 推荐工作流程

```bash
# 1. 添加用户到 docker 组（只需一次）
sudo usermod -aG docker $USER
# 重启 terminal 或执行: newgrp docker

# 2. 运行应用（不需要 sudo）
nb run --reload --reload-excludes ext_workdir

# 3. 如遇权限问题，运行清理脚本
./cleanup_sandbox.sh

# cleanup_sandbox.sh 内容：
#!/bin/bash
docker ps -a | grep nekro-agent-sandbox | awk '{print $1}' | xargs -r docker rm -f
sudo chown -R $(whoami):$(id -gn $(whoami)) data/sandboxes/
sudo chown -R $(whoami):$(id -gn $(whoami)) data/plugins/workdir/
```

### 3.4 配置文件兼容性

#### docker-compose.yml 兼容性配置

```yaml
version: '3.8'

services:
  nekro-agent:
    image: kromiose/nekro-agent:${VERSION:-v2.2.0}
    # ... 其他配置

  # 沙盒服务（可选，如果使用外部沙盒）
  sandbox:
    image: kromiose/nekro-agent-sandbox:${SANDBOX_VERSION:-v2.2.0}
    # 兼容性配置
    user: "${HOST_UID:-1000}:${HOST_GID:-1000}"
    volumes:
      - ${NEKRO_DATA_DIR:-./data}/sandboxes:/app/shared:rw
    environment:
      - HOST_UID=${HOST_UID:-1000}
      - HOST_GID=${HOST_GID:-1000}
```

#### 环境变量兼容

```bash
# .env 文件新增配置
# 沙盒配置
HOST_UID=${HOST_UID:-1000}
HOST_GID=${HOST_GID:-1000}
SANDBOX_VERSION=v2.2.0
```

---

## 四、版本迁移时间线

### 4.1 迁移阶段

| 阶段 | 版本 | 时间 | 变更内容 |
|------|------|------|----------|
| **Phase 1** | v2.2.0 | 当前 | 发布迁移脚本和文档 |
| **Phase 2** | v2.2.1 | +2 周 | 优化权限处理逻辑 |
| **Phase 3** | v2.3.0 | +1 月 | 默认使用用户身份运行 |
| **Phase 4** | v2.4.0 | +3 月 | 移除旧权限模式 |

### 4.2 各阶段用户操作

| 阶段 | Docker 部署用户 | 开发环境用户 |
|------|----------------|--------------|
| v2.2.0 | 运行迁移脚本 | 手动配置权限 |
| v2.2.1 | 无需操作 | 无需操作 |
| v2.3.0 | 更新镜像 | 更新代码 |
| v2.4.0 | 更新镜像 | 更新代码 |

---

## 五、故障排查

### 5.1 常见问题

#### 问题 1：目录权限错误

**错误信息**:
```
PermissionError: [Errno 13] Permission denied: '/home/user/srv/nekro_agent/data/sandboxes/xxx'
```

**解决方案**:
```bash
# 运行清理脚本
./cleanup_sandbox.sh

# 或手动修复
sudo chown -R $(whoami):$(id -gn $(whoami)) data/sandboxes/
```

#### 问题 2：沙盒容器无法启动

**错误信息**:
```
docker.errors.APIError: 500 Server Error: Internal Server Error
```

**解决方案**:
```bash
# 清理旧容器
sudo docker rm -f $(sudo docker ps -a | grep nekro-agent-sandbox | awk '{print $1}')

# 重新拉取镜像
sudo docker pull kromiose/nekro-agent-sandbox:v2.2.0
```

#### 问题 3：动态包安装失败

**错误信息**:
```
RuntimeError: 安装 xxx 失败
```

**解决方案**:
```bash
# 清理包目录
sudo chown -R $(whoami):$(id -gn $(whoami)) data/sandboxes/.packages/
rm -rf data/sandboxes/.packages/*

# 重启服务
sudo docker compose restart
```

### 5.2 回滚方案

如果升级后出现问题，可以回滚到旧版本：

```bash
# 1. 停止服务
cd ~/srv/nekro_agent
sudo docker compose down

# 2. 恢复备份
cp -r data/sandboxes_backup/* data/sandboxes/

# 3. 恢复 docker-compose.yml
cp docker-compose.yml.bak docker-compose.yml

# 4. 拉取旧版镜像
sudo docker pull kromiose/nekro-agent-sandbox:v2.1.0

# 5. 启动服务
sudo docker compose up -d
```

---

## 六、总结

### 6.1 兼容性矩阵

| 场景 | 旧版本用户 | 新版本用户 |
|------|------------|------------|
| Docker 部署 | 需要运行迁移脚本 | 无需操作 |
| 开发环境 | 需要配置权限 | 默认兼容 |
| 插件开发 | 可能遇到权限问题 | 已解决 |
| 升级操作 | 需要手动迁移 | 自动处理 |

### 6.2 关键建议

1. **Docker 部署用户**: 升级前运行迁移脚本
2. **开发环境用户**: 配置 docker 组，避免 sudo
3. **升级顺序**: 先迁移数据，再更新代码
4. **备份**: 升级前备份重要数据

### 6.3 下一步行动

- [ ] 编写自动化迁移脚本
- [ ] 更新文档站部署文档
- [ ] 测试迁移脚本兼容性
- [ ] 准备回滚方案

---

## 附录：相关文档链接

- [Linux 部署文档](https://doc.nekro.ai/docs/02_quick_start/deploy/linux.html)
- [Linux 开发环境](https://doc.nekro.ai/docs/05_app_dev/dev_linux.html)
- [沙盒权限问题分析](01_sandbox_permission_analysis.md)
