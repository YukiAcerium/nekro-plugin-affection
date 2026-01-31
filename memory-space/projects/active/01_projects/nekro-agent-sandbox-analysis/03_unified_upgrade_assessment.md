# 统一在线升级方案评估

## 研究日期

2026-01-30

## 研究目标

评估通过 EP (NekroEndpoint) 加速分发统一在线升级脚本的可行性，分析是否能同时解决沙盒权限问题，并评估风险及制定测试流程。

---

## 一、当前升级指令分析

### 1.1 现有升级方式

| 方式 | 命令 | 分发渠道 | 问题 |
|------|------|----------|------|
| **install.sh** | `sudo -E bash -c "$(curl -fsSL https://raw.githubusercontent.com/.../install.sh)"` | GitHub Raw | 网络问题 |
| **EP 加速** | `sudo -E bash -c "$(curl -fsSL https://ep.nekro.ai/e/.../install.sh)"` | Cloudflare Workers | ✅ 加速 |
| **Toolkit** | `nekro-agent-toolkit --upgrade ./na_data` | PyPI | 需单独安装 |

### 1.2 install.sh 关键流程

**文件**: `docker/install.sh`

```bash
# 第 237-238 行：权限设置（问题点）
sudo chmod -R 777 "$NEKRO_DATA_DIR"

# 第 348-351 行：拉取镜像
sudo docker pull kromiose/nekro-agent-sandbox

# 第 361-364 行：启动服务
sudo bash -c "$DOCKER_COMPOSE_CMD --env-file .env up -d"
```

### 1.3 EP 加速分发

```bash
# 当前 EP 脚本只是代理 install.sh
# URL: https://ep.nekro.ai/e/KroMiose/nekro-agent/main/docker/install.sh

# 实际执行流程：
# 1. EP 接收请求
# 2. EP 从 GitHub 获取脚本
# 3. EP 返回脚本内容
# 4. 用户 bash 执行脚本
```

---

## 二、统一升级方案设计

### 2.1 方案架构

```
┌─────────────────────────────────────────────────────────────┐
│                    统一升级入口                              │
├─────────────────────────────────────────────────────────────┤
│  https://ep.nekro.ai/e/KroMiose/nekro-agent/main/upgrade.sh │
└─────────────────────────────────────────────────────────────┘
                            ↓
                  ┌───────────────────┐
                  │   EP 边缘节点      │
                  │   (300+ 节点)      │
                  └───────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                                       ↓
┌───────────────┐                   ┌───────────────────┐
│  国内用户     │                   │  海外用户         │
│  (Cloudflare  │                   │  (GitHub Raw)    │
│   中国节点)   │                   │                  │
└───────────────┘                   └───────────────────┘
```

### 2.2 脚本功能规划

```bash
#!/bin/bash
# upgrade.sh - 统一升级脚本

set -e

VERSION="${1:-latest}"
NEKRO_DATA_DIR="${NEKRO_DATA_DIR:-${HOME}/srv/nekro_agent}"

echo "=== NekroAgent 统一升级脚本 ==="
echo "版本: $VERSION"
echo "数据目录: $NEKRO_DATA_DIR"
echo ""

# 1. 检查环境
check_environment() {
    echo "1. 检查运行环境..."
    # 检查 Docker
    command -v docker >/dev/null 2>&1 || { echo "❌ Docker 未安装"; exit 1; }
    # 检查权限
    docker ps >/dev/null 2>&1 || { echo "⚠️  需要 sudo 权限或 docker 组"; }
    echo "✅ 环境检查完成"
}

# 2. 备份数据
backup_data() {
    echo "2. 备份数据..."
    BACKUP_DIR="${NEKRO_DATA_DIR}/backups/upgrade_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份配置
    cp -r "${NEKRO_DATA_DIR}/data" "$BACKUP_DIR/"
    cp -r "${NEKRO_DATA_DIR}/.env" "$BACKUP_DIR/" 2>/dev/null || true
    cp -r "${NEKRO_DATA_DIR}/docker-compose*.yml" "$BACKUP_DIR/" 2>/dev/null || true
    
    echo "✅ 备份完成: $BACKUP_DIR"
}

# 3. 修复权限（关键功能）
fix_permissions() {
    echo "3. 修复权限..."
    
    CURRENT_USER=$(whoami)
    CURRENT_GROUP=$(id -gn $CURRENT_USER)
    
    # 重置沙盒目录所有权
    if [ -d "${NEKRO_DATA_DIR}/data/sandboxes" ]; then
        sudo chown -R "$CURRENT_USER:$CURRENT_GROUP" "${NEKRO_DATA_DIR}/data/sandboxes/"
        sudo chmod -R 755 "${NEKRO_DATA_DIR}/data/sandboxes/"
        echo "✅ 已修复 sandboxes 权限"
    fi
    
    # 重置插件目录所有权
    if [ -d "${NEKRO_DATA_DIR}/data/plugins/workdir" ]; then
        sudo chown -R "$CURRENT_USER:$CURRENT_GROUP" "${NEKRO_DATA_DIR}/data/plugins/workdir/"
        sudo chmod -R 755 "${NEKRO_DATA_DIR}/data/plugins/workdir/"
        echo "✅ 已修复 plugins/workdir 权限"
    fi
    
    echo "✅ 权限修复完成"
}

# 4. 清理旧容器
cleanup_containers() {
    echo "4. 清理旧容器..."
    
    # 清理沙盒容器
    CONTAINERS=$(sudo docker ps -a | grep nekro-agent-sandbox | awk '{print $1}')
    if [ -n "$CONTAINERS" ]; then
        echo "$CONTAINERS" | xargs -r sudo docker rm -f
        echo "✅ 已清理 $CONTAINERS 个旧容器"
    else
        echo "ℹ️  无旧容器需要清理"
    fi
}

# 5. 更新服务
update_services() {
    echo "5. 更新服务..."
    
    cd "$NEKRO_DATA_DIR"
    
    # 拉取最新镜像
    echo "   拉取最新镜像..."
    sudo docker compose pull || sudo docker-compose pull
    
    # 重启服务
    echo "   重启服务..."
    sudo docker compose up -d || sudo docker-compose up -d
    
    echo "✅ 服务更新完成"
}

# 6. 验证服务
verify_services() {
    echo "6. 验证服务..."
    
    sleep 5
    
    # 检查容器状态
    RUNNING=$(sudo docker compose ps --status running | grep -c "Up" || echo "0")
    echo "   运行中容器: $RUNNING"
    
    if [ "$RUNNING" -gt 0 ]; then
        echo "✅ 服务运行正常"
    else
        echo "⚠️  服务可能未正常运行，请检查日志"
        echo "   查看日志: cd $NEKRO_DATA_DIR && docker compose logs"
    fi
}

# 主流程
main() {
    check_environment
    read -r -p "是否继续升级？[Y/n] " yn
    [ -z "$yn" ] && yn=y
    [[ "$yn" =~ ^[Yy]$ ]] || exit 0
    
    backup_data
    fix_permissions
    cleanup_containers
    update_services
    verify_services
    
    echo ""
    echo "=== 升级完成 ==="
    echo "如遇到问题，请查看日志: cd $NEKRO_DATA_DIR && docker compose logs"
}

main "$@"
```

### 2.3 EP 配置

```javascript
// EP 边缘函数配置
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    if (url.pathname === '/e/KroMiose/nekro-agent/main/upgrade.sh') {
      // 获取版本参数
      const version = url.searchParams.get('v') || 'main';
      
      // 从 GitHub 获取升级脚本
      const scriptUrl = `https://raw.githubusercontent.com/KroMiose/nekro-agent/${version}/docker/upgrade.sh`;
      const response = await fetch(scriptUrl);
      
      if (!response.ok) {
        return new Response('脚本不存在', { status: 404 });
      }
      
      let script = await response.text();
      
      // 添加版本标识
      script = script.replace(
        '#!/bin/bash',
        `# Generated by NekroAgent EP Upgrade Service\n# Version: ${version}\n#!/bin/bash`
      );
      
      return new Response(script, {
        headers: {
          'Content-Type': 'application/x-shellscript',
          'Content-Disposition': 'attachment; filename="upgrade.sh"',
          'Cache-Control': 'no-store',
        },
      });
    }
    
    return new Response('Not Found', { status: 404 });
  },
};
```

---

## 三、风险评估

### 3.1 技术风险

| 风险 | 级别 | 影响 | 缓解措施 |
|------|------|------|----------|
| **脚本执行失败** | 🔴 高 | 用户无法升级 | 增加错误处理和回滚机制 |
| **权限修复破坏现有配置** | 🔴 高 | 文件所有权混乱 | 备份优先，用户确认 |
| **Docker 镜像兼容问题** | 🟡 中 | 服务启动失败 | 版本检查，回滚支持 |
| **网络问题导致脚本不完整** | 🟡 中 | 升级中断 | 多源重试，超时处理 |
| **并发升级冲突** | 🟡 中 | 数据损坏 | 锁机制，状态检查 |

### 3.2 用户体验风险

| 风险 | 级别 | 影响 | 缓解措施 |
|------|------|------|----------|
| **需要 sudo 权限** | 🔴 高 | 用户体验差 | 提前配置 docker 组 |
| **升级时间过长** | 🟡 中 | 用户等待焦虑 | 进度显示，估计时间 |
| **升级后功能异常** | 🟡 中 | 用户不满 | 全面测试，灰度发布 |
| **回滚操作复杂** | 🟡 中 | 问题难以恢复 | 一键回滚脚本 |

### 3.3 安全风险

| 风险 | 级别 | 影响 | 缓解措施 |
|------|------|------|----------|
| **脚本注入攻击** | 🔴 高 | 服务器被入侵 | 脚本签名验证 |
| **权限提升** | 🟡 中 | 权限滥用 | 最小权限原则 |
| **数据泄露** | 🟡 中 | 隐私泄露 | 加密传输，权限控制 |

---

## 四、测试流程设计

### 4.1 测试环境

```yaml
测试环境矩阵:
  - 操作系统:
      - Ubuntu 20.04/22.04
      - Debian 11/12
      - CentOS 7/8
      - macOS 13+
      - Windows 11 (WSL2)
  
  - Docker 配置:
      - Docker 组用户
      - sudo 用户
      - root 用户
  
  - 数据状态:
      - 全新安装
      - 部分升级（v2.0 → v2.1）
      - 完整升级（v1.x → v2.x）
      - 权限混乱状态
```

### 4.2 测试用例

#### 4.2.1 基础功能测试

| 用例编号 | 测试场景 | 预期结果 | 测试方法 |
|----------|----------|----------|----------|
| TC001 | 全新安装后升级 | 升级成功，服务正常 | 脚本执行，验证服务 |
| TC002 | 跨大版本升级 (v1.x → v2.x) | 迁移成功，数据完整 | 检查数据，验证配置 |
| TC003 | 多次连续升级 | 每次成功，最终正常 | 循环升级，检查状态 |
| TC004 | 升级中途取消 | 回滚到原始状态 | 中断执行，检查目录 |

#### 4.2.2 权限测试

| 用例编号 | 测试场景 | 预期结果 | 测试方法 |
|----------|----------|----------|----------|
| TC005 | nobody 用户文件存在时升级 | 权限被修复 | 检查文件归属 |
| TC006 | root 用户创建的文件 | 归属转移 | chown 验证 |
| TC007 | 并发升级同一目录 | 报错阻止 | 多进程测试 |
| TC008 | 升级后动态包安装 | 正常安装 | pip install 测试 |

#### 4.2.3 异常处理测试

| 用例编号 | 测试场景 | 预期结果 | 测试方法 |
|----------|----------|----------|----------|
| TC009 | Docker 未安装 | 错误提示，退出 | 执行脚本，检查输出 |
| TC010 | 网络中断 | 错误提示，重试 | 断网测试 |
| TC011 | 磁盘空间不足 | 错误提示，退出 | 模拟磁盘满 |
| TC012 | 容器启动失败 | 回滚，错误报告 | 强制错误测试 |

### 4.3 自动化测试流程

```yaml
# .github/workflows/upgrade-test.yml
name: Upgrade Script Test

on:
  schedule:
    - cron: '0 0 * * 0'  # 每周运行
  push:
    paths:
      - 'docker/upgrade.sh'
      - 'docker/install.sh'

jobs:
  test-upgrade:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        os: [ubuntu-20.04, ubuntu-22.04, debian-11, debian-12]
        docker-setup: [sudo, docker-group]
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Docker
        run: |
          # 安装 Docker
          curl -fsSL https://get.docker.com | sh
          # 配置 docker 组
          if [ "${{ matrix.docker-setup }}" == "docker-group" ]; then
            sudo usermod -aG docker $USER
          fi
      
      - name: Install Test Dependencies
        run: |
          pip install docker-compose
      
      - name: Prepare Test Environment
        run: |
          # 创建测试数据目录
          mkdir -p $HOME/test_na/data/sandboxes
          echo "TEST=1" > $HOME/test_na/.env
      
      - name: Run Upgrade Test
        run: |
          bash docker/upgrade.sh --test --data-dir $HOME/test_na
      
      - name: Verify Result
        run: |
          # 验证升级结果
          docker ps | grep nekro-agent || echo "服务未启动"
          ls -la $HOME/test_na/data/sandboxes/ | grep nobody && echo "权限未修复"
```

### 4.4 手动测试清单

```markdown
## 上线前手动测试清单

### 环境准备
- [ ] 准备测试服务器（至少 2 台）
- [ ] 准备不同操作系统环境
- [ ] 配置测试数据（包含权限问题）
- [ ] 确认网络环境稳定

### 测试执行
- [ ] TC001: 全新安装升级
- [ ] TC002: 跨版本升级
- [ ] TC003: 连续升级
- [ ] TC004: 中途取消
- [ ] TC005: 权限修复
- [ ] TC006: root 文件归属
- [ ] TC007: 并发升级
- [ ] TC008: 动态包安装
- [ ] TC009: Docker 未安装
- [ ] TC010: 网络中断
- [ ] TC011: 磁盘空间不足
- [ ] TC012: 容器启动失败

### 结果确认
- [ ] 所有测试用例通过
- [ ] 无权限问题残留
- [ ] 服务稳定运行 24 小时
- [ ] 回滚脚本可用
```

---

## 五、实施计划

### 5.1 阶段一：开发阶段 (Week 1-2)

| 任务 | 时间 | 负责人 | 输出 |
|------|------|--------|------|
| 开发统一升级脚本 | Week 1 | Dev | upgrade.sh |
| 配置 EP 边缘函数 | Week 1 | Dev | worker.js |
| 编写回滚脚本 | Week 2 | Dev | rollback.sh |
| 开发权限修复模块 | Week 2 | Dev | permission_fix.sh |

### 5.2 阶段二：测试阶段 (Week 3-4)

| 任务 | 时间 | 负责人 | 输出 |
|------|------|--------|------|
| 自动化测试开发 | Week 3 | QA | test.yml |
| 手动测试执行 | Week 3-4 | QA | 测试报告 |
| 性能测试 | Week 4 | QA | 性能报告 |
| 安全审计 | Week 4 | Sec | 审计报告 |

### 5.3 阶段三：发布阶段 (Week 5)

| 任务 | 时间 | 负责人 | 输出 |
|------|------|--------|------|
| 灰度发布 (10%) | Week 5 | Dev | 发布日志 |
| 全量发布 | Week 5 | Dev | 公告 |
| 文档更新 | Week 5 | Doc | 新文档 |
| 监控上线 | Week 5 | Ops | 监控面板 |

---

## 六、总结

### 6.1 方案可行性

| 评估项 | 评分 | 说明 |
|--------|------|------|
| **技术可行性** | ⭐⭐⭐⭐⭐ | 技术成熟，风险可控 |
| **用户价值** | ⭐⭐⭐⭐⭐ | 一键解决权限问题 |
| **维护成本** | ⭐⭐⭐⭐ | 脚本需持续更新 |
| **安全风险** | ⭐⭐⭐⭐ | 有风险但可控 |

### 6.2 关键成功因素

1. ✅ 统一的升级入口（通过 EP 加速）
2. ✅ 权限自动修复（脚本内置）
3. ✅ 完善的备份机制
4. ✅ 一键回滚支持
5. ✅ 全面的自动化测试

### 6.3 推荐行动

**立即执行**:
1. 开发 `upgrade.sh` 统一升级脚本
2. 配置 EP 边缘函数
3. 增加权限修复模块
4. 编写回滚脚本

**后续优化**:
5. 完善自动化测试
6. 灰度发布验证
7. 全量推广

---

## 附录：相关链接

- **升级脚本**: `https://ep.nekro.ai/e/KroMiose/nekro-agent/main/upgrade.sh`
- **安装脚本**: `https://ep.nekro.ai/e/KroMiose/nekro-agent/main/docker/install.sh`
- **Toolkit**: https://github.com/greenhandzdl/nekro-agent-toolkit
- **权限分析**: 01_sandbox_permission_analysis.md
- **兼容性分析**: 02_compatibility_analysis.md
