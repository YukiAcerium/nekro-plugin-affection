# NekroAgent 沙盒-插件协同工作系统分析报告

## 研究日期

2026-01-30

## 研究目标

深入分析 NekroAgent 的沙盒对话系统实现，找出权限相关问题的根本原因。

## 问题概述

### 症状

1. **需要 sudo 权限运行开发模式**: 开发时必须使用 `sudo nb run`，否则会出现各种容器权限问题
2. **文件所有权问题**: 工作目录下的插件源码可能被变成 root 所有，导致 VSCode 等编辑器无法正常编辑
3. **沙盒目录权限混乱**: 沙盒共享目录 (`sandboxes/`) 内的文件所有权混乱

---

## 系统架构分析

### 1. 沙盒运行器核心流程

**文件**: `nekro_agent/services/sandbox/runner.py`

#### 1.1 容器创建流程

```python
# 1. 创建容器密钥
container_key = f"sandbox_{from_chat_key}"
host_shared_dir = Path(HOST_SHARED_DIR / container_key)

# 2. 创建共享目录（关键步骤）
host_shared_dir.mkdir(parents=True, exist_ok=True)
HOST_PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
HOST_PIP_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# 3. 设置目录权限（问题点）
Path.chmod(host_shared_dir, 0o777)
Path.chmod(HOST_PIP_CACHE_DIR, 0o777)
Path.chmod(HOST_PACKAGE_DIR, 0o777)

# 4. 启动 Docker 容器
docker = aiodocker.Docker()
container = await docker.containers.run(
    config={
        "Image": IMAGE_NAME,
        "User": "nobody",  # ⚠️ 容器内使用非特权用户
        "HostConfig": {
            "Binds": [
                f"{HOST_PIP_CACHE_DIR}:{CONTAINER_PIP_CACHE_DIR}:rw",
                f"{HOST_PACKAGE_DIR}:{CONTAINER_PACKAGE_DIR}:rw",
                f"{host_shared_dir}:{CONTAINER_SHARE_DIR}:rw",
            ],
        },
    },
)
```

#### 1.2 关键问题

| 步骤 | 问题描述 |
|------|----------|
| 创建目录 | 目录由运行进程的用户创建（普通用户或 root） |
| chmod 777 | 设置为所有用户可写 |
| 容器挂载 | 容器内 nobody 用户写入 |
| 文件归属 | 写入的文件归属 nobody 用户 |

### 2. 目录结构与所有权

**文件**: `nekro_agent/core/os_env.py`

```python
# 沙盒相关目录
SANDBOX_SHARED_HOST_DIR = DATA_DIR + "/sandboxes"           # 沙盒共享目录
SANDBOX_PIP_CACHE_DIR = DATA_DIR + "/sandboxes/.pip_cache"  # pip 缓存
SANDBOX_PACKAGE_DIR = DATA_DIR + "/sandboxes/.packages"     # 动态包目录

# 插件相关目录
PLUGIN_DYNAMIC_PACKAGE_DIR = DATA_DIR + "/plugins/.dynamic_packages"  # 插件动态包
WORKDIR_PLUGIN_DIR = DATA_DIR + "/plugins/workdir"                    # 本地插件目录
```

### 3. 容器镜像 Dockerfile 分析

**文件**: `sandbox/dockerfile`

```dockerfile
# 基础镜像
FROM python:3.11-slim-bullseye

# 创建目录并设置权限
RUN mkdir -p /app /app/shared /app/packages && \
    chown -R nobody:nogroup /app && \    # ⚠️ 设置容器内归属
    chmod -R 777 /app /app/shared /app/packages &&  # ⚠️ 容器内可写
    chmod 755 /bin/bash

# 复制所有文件
COPY . /app
```

**问题**: 容器内 `/app/packages` 设为 777，但这个目录会被挂载到主机

### 4. 动态包安装机制

**文件**: `nekro_agent/services/sandbox/ext_caller_code.py`

```python
def dynamic_importer(
    package_spec: str,
    repo_dir: Optional[str] = "/app/packages",  # ⚠️ 默认容器内路径
):
    # 容器内安装包
    install_cmd = [
        sys.executable,
        "-m", "pip", "install",
        "--target", repo_dir,  # 安装到容器内目录
        package_spec,
    ]
    subprocess.run(install_cmd, ...)
```

**问题**: 
- 默认 `repo_dir="/app/packages"` 是容器内路径
- 容器内安装的包归属 nobody 用户
- 这些包被挂载到主机后，主机普通用户无法修改

---

## 问题根源分析

### 问题 1：开发模式需要 sudo

**原因**：
```bash
# sandbox.sh 使用 sudo 运行 docker
sudo docker pull kromiose/nekro-agent-sandbox
sudo docker build -t nekro-agent-sandbox:latest .
```

**详细分析**：
1. Docker daemon 默认需要 root 权限运行
2. 虽然可以将用户加入 `docker` 组来避免 sudo，但还有更深层的问题
3. 沙盒目录的创建和权限设置需要特殊处理

### 问题 2：文件所有权混乱

**时序图**：

```
普通用户启动应用
    ↓
应用创建 sandboxes/ 目录（普通用户所有）
    ↓
容器以 nobody 用户运行
    ↓
容器写入文件到共享目录（nobody 所有）
    ↓
后续操作可能导致 root 访问（sudo 运行时）
    ↓
文件变成 root 所有
    ↓
普通用户无法编辑
```

**核心问题**：
1. 目录由普通用户创建，容器内 nobody 用户写入
2. 如果某次以 sudo 运行，文件会变成 root 所有
3. `Path.chmod(0o777)` 不能解决所有权问题

### 问题 3：动态包安装权限

**流程**：
```
主机目录 (普通用户:普通用户, 755)
    ↓ 挂载到容器
容器内 /app/packages (nobody:nogroup, 777)
    ↓
pip install --target /app/packages
    ↓
安装的包归属 nobody 用户
    ↓ 挂载回主机
主机目录 (nobody 用户所有)
```

**后果**：
- 主机普通用户无法删除或修改这些包
- VSCode 等编辑器无法索引这些文件

---

## 权限问题详细分析

### 1. 沙盒共享目录权限流

| 阶段 | 操作 | 目录所有者 | 目录权限 |
|------|------|-----------|----------|
| 启动 | `host_shared_dir.mkdir()` | 运行用户 | 755 |
| 运行 | `Path.chmod(0o777)` | 运行用户 | 777 |
| 容器 | 写入文件 | nobody | - |
| 结果 | 文件归属 nobody | - | - |

### 2. 动态包安装权限流

| 阶段 | 操作 | 文件所有者 |
|------|------|-----------|
| 容器内 | `pip install --target /app/packages` | nobody |
| 主机挂载 | 映射到 `sandboxes/.packages/` | nobody |
| 主机访问 | 普通用户尝试修改 | ❌ 权限 denied |

### 3. 沙盒镜像权限流

```dockerfile
# 容器内创建
RUN mkdir -p /app/packages && \
    chown -R nobody:nogroup /app && \  # 容器内用户
    chmod -R 777 /app/packages         # 所有用户可写
```

**问题**：
- 镜像内目录归属 nobody
- 挂载主机目录后，主机用户无法写入

---

## 关键代码问题点

### 1. runner.py 第 171-175 行

```python
# 设置目录权限
try:
    Path.chmod(host_shared_dir, 0o777)
    Path.chmod(HOST_PIP_CACHE_DIR, 0o777)
    Path.chmod(HOST_PACKAGE_DIR, 0o777)
except Exception as e:
    logger.error(f"设置目录权限失败: {e}")
```

**问题**：
- `chmod 777` 只解决权限，不解决所有权
- 容器内写入的文件仍归属 nobody

### 2. ext_caller_code.py 第 73 行

```python
def dynamic_importer(
    package_spec: str,
    repo_dir: Optional[str] = "/app/packages",  # 容器内路径
):
```

**问题**：
- 默认路径是容器内路径
- 应该使用主机共享目录作为持久化路径

### 3. sandbox.sh 第 4 行

```bash
sudo docker pull kromiose/nekro-agent-sandbox
```

**问题**：
- 需要 sudo 才能运行
- 应该指导用户配置 docker 组

---

## 解决方案建议

### 方案 1：统一使用普通用户运行

#### 1.1 添加用户到 docker 组

```bash
sudo usermod -aG docker $USER
# 重启 shell 使生效
```

#### 1.2 修改目录权限机制

```python
# 在创建目录后，使用 setfacl 设置默认 ACL
import subprocess

def create_sandbox_dir_with_acl(path: Path, owner: str):
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["setfacl", "-d", "-m", f"u:{owner}:rwx", str(path)])
    subprocess.run(["setfacl", "-d", "-m", f"g:{owner}:rwx", str(path)])
    subprocess.run(["setfacl", "-d", "-m", "o::rwx", str(path)])
```

### 方案 2：容器内使用与主机相同的用户

#### 2.1 修改 Dockerfile

```dockerfile
# 不设置固定用户，让容器使用运行时的用户
RUN mkdir -p /app && chmod 777 /app
```

#### 2.2 修改 runner.py

```python
# 获取主机运行用户的 UID/GID
import os
host_uid = os.getuid()
host_gid = os.getgid()

container = await docker.containers.run(
    config={
        "User": f"{host_uid}:{host_gid}",  # 使用主机用户
        "HostConfig": {
            "Binds": [...],
        },
    },
)
```

### 方案 3：分离容器内包和主机包

#### 3.1 修改动态包安装逻辑

```python
# 使用主机目录作为动态包存储
HOST_DYNAMIC_PACKAGE_DIR = Path(SANDBOX_PACKAGE_DIR)

def dynamic_importer(
    package_spec: str,
    repo_dir: Optional[str] = None,  # 默认为主机目录
):
    repo_dir = repo_dir or str(HOST_DYNAMIC_PACKAGE_DIR)
    # ...
```

#### 3.2 修改容器挂载

```python
# 主机包目录只读挂载到容器
"HostConfig": {
    "Binds": [
        f"{HOST_PACKAGE_DIR}:{CONTAINER_PACKAGE_DIR}:ro",  # 只读
    ],
}
```

### 方案 4：清理脚本

```bash
#!/bin/bash
# cleanup_sandbox.sh

# 重置 sandboxes 目录所有权
sudo chown -R $USER:$USER ./data/sandboxes/
sudo chown -R $USER:$USER ./data/plugins/workdir/

# 清理过期容器
docker ps -a | grep nekro-agent-sandbox | awk '{print $1}' | xargs -r docker rm -f
```

---

## 最佳实践建议

### 1. 开发环境设置

```bash
# 1. 添加用户到 docker 组
sudo usermod -aG docker $USER

# 2. 重启 shell 或重新登录

# 3. 运行应用（不需要 sudo）
nb run

# 4. 如遇权限问题，运行清理脚本
./cleanup_sandbox.sh
```

### 2. 目录权限管理

建议在应用启动时：
1. 检查目录权限
2. 自动修复权限问题
3. 使用 ACL 实现细粒度权限控制

### 3. Docker 配置

```bash
# 创建 docker 组（如果不存在）
sudo groupadd docker

# 添加当前用户到 docker 组
sudo usermod -aG docker $USER

# 重启 docker 服务
sudo systemctl restart docker

# 验证
docker ps  # 不需要 sudo
```

---

## 总结

### 问题根本原因

| 问题 | 根本原因 | 影响 |
|------|----------|------|
| 需要 sudo | Docker daemon 需要 root，目录权限设置不完善 | 开发体验差 |
| 文件所有权混乱 | 容器内使用 nobody 用户，主机使用普通用户 | 编辑器无法工作 |
| 包安装权限问题 | 容器内安装包归属 nobody，映射到主机 | 无法更新包 |

### 解决方案优先级

1. **高优先级**：指导用户配置 docker 组，避免 sudo
2. **中优先级**：修改容器使用主机用户身份运行
3. **低优先级**：实现自动权限修复机制

### 推荐方案

采用 **方案 2（容器内使用与主机相同的用户）** 作为长期解决方案，配合 **方案 4（清理脚本）** 作为临时解决方案。

---

## 参考文档

- [Linux 开发环境准备](../../05_app_dev/dev_linux.md)
- [Docker 权限管理](https://docs.docker.com/engine/install/linux-postinstall/)
- [ACL 权限管理](https://man7.org/linux/man-pages/man5/acl.5.html)

---

## 附录：关键文件清单

| 文件 | 作用 | 问题 |
|------|------|------|
| `nekro_agent/services/sandbox/runner.py` | 沙盒运行器 | chmod 777 不解决所有权 |
| `nekro_agent/core/os_env.py` | 环境变量定义 | 目录路径配置 |
| `nekro_agent/services/sandbox/ext_caller_code.py` | 动态包安装 | 默认容器内路径 |
| `sandbox/dockerfile` | 容器镜像定义 | nobody 用户 |
| `sandbox.sh` | 镜像管理脚本 | 使用 sudo |
