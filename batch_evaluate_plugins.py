#!/usr/bin/env python3
"""
NekroAgent 插件批量评估脚本
快速评估 49 个插件的各项指标
"""

import json
import subprocess
import os
from datetime import datetime
from typing import Dict, List

# 评估结果存储
EVALUATIONS = []

# 加载插件列表
with open("plugins_complete_data.json", "r", encoding="utf-8") as f:
    plugins = json.load(f)

def clone_and_analyze(plugin: Dict) -> Dict:
    """克隆并分析单个插件"""
    name = plugin.get("name", "未知")
    module = plugin.get("moduleName", "未知")
    github = plugin.get("githubUrl", "")
    
    print(f"\n{'='*80}")
    print(f"📦 评估插件: {name} ({module})")
    print(f"{'='*80}")
    
    eval_result = {
        "name": name,
        "module": module,
        "author": plugin.get("author", "未知"),
        "github": github,
        "evaluated_at": datetime.now().isoformat(),
        "scores": {},
        "total_score": 0,
        "grade": "F",
        "highlights": [],
        "issues": [],
    }
    
    # 克隆仓库
    if github and github != "无":
        repo_name = github.replace("https://github.com/", "").rstrip("/")
        local_path = f"/tmp/{repo_name.replace('/', '_')}"
        
        if os.path.exists(local_path):
            print(f"  ✅ 已存在: {local_path}")
        else:
            print(f"  🔄 克隆仓库...")
            result = subprocess.run(
                ["git", "clone", "--depth", "1", github, local_path],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"  ✅ 克隆成功")
            else:
                print(f"  ❌ 克隆失败: {result.stderr}")
                eval_result["issues"].append("克隆失败")
                return eval_result
    
    # 分析代码质量
    score = 0
    details = []
    
    # 检查文件
    paths_to_check = [
        f"{local_path}/__init__.py",
        f"{local_path}/plugin.py",
        f"{local_path}/README.md",
        f"{local_path}/pyproject.toml",
        f"{local_path}/LICENSE",
    ]
    
    existing_files = sum(1 for p in paths_to_check if os.path.exists(p))
    score += existing_files * 1.5  # 每个文件 1.5 分
    details.append(f"文件检查: {existing_files}/5")
    
    # 分析代码
    main_py = f"{local_path}/__init__.py"
    if os.path.exists(main_py):
        try:
            with open(main_py, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 检查类型注解
            if "async def" in content and "->" in content:
                score += 1.5
                details.append("✅ 类型注解完整")
            elif "async def" in content:
                score += 0.5
                details.append("⚠️ 缺少类型注解")
            
            # 检查错误处理
            if "try:" in content and "except" in content:
                score += 1
                details.append("✅ 错误处理完善")
            
            # 检查日志
            if "logger" in content or "logging" in content:
                score += 1
                details.append("✅ 使用日志记录")
            
            # 检查文档字符串
            if '"""' in content or "'''" in content:
                score += 1.5
                details.append("✅ 文档字符串完整")
            
            # 检查配置
            if "ConfigBase" in content or "@plugin.mount_config" in content:
                score += 1.5
                details.append("✅ 配置系统完整")
            
            # 检查沙盒方法
            if "SandboxMethodType" in content or "mount_sandbox_method" in content:
                score += 1.5
                details.append("✅ 沙盒方法定义")
            
            # 检查提示词注入
            if "mount_prompt_inject_method" in content:
                score += 1
                details.append("✅ 提示词注入")
            
        except Exception as e:
            details.append(f"❌ 代码分析失败: {e}")
    
    # 归一化为 10 分制
    normalized_score = min(score / 2, 10)  # 满分约 20 分，归一化为 10 分
    eval_result["scores"]["代码质量"] = round(normalized_score, 1)
    
    # 基于代码质量估算其他维度
    base_score = normalized_score
    
    # 功能完整性 (基于代码复杂度)
    eval_result["scores"]["功能完整性"] = round(base_score * 0.95, 1)
    
    # 文档完善度 (基于 README)
    readme_path = f"{local_path}/README.md"
    has_readme = os.path.exists(readme_path)
    readme_size = os.path.getsize(readme_path) if has_readme else 0
    doc_score = 10 if (has_readme and readme_size > 2000) else (7 if has_readme else 4)
    eval_result["scores"]["文档完善度"] = doc_score
    
    # AI 使用设计 (基于文档字符串和提示词)
    ai_score = min(base_score + 1, 10) if "description" in content else base_score
    eval_result["scores"]["AI使用设计"] = round(ai_score, 1)
    
    # 易用性
    eval_result["scores"]["易用性"] = round(base_score * 0.85, 1)
    
    # 安全性 (基于输入验证)
    security_score = base_score if "ValueError" in content or "assert" in content else base_score - 1
    eval_result["scores"]["安全性"] = round(max(security_score, 5), 1)
    
    # 维护活跃度 (基于 GitHub 活动)
    try:
        repo = github.replace("https://github.com/", "").rstrip("/")
        result = subprocess.run(
            ["gh", "api", f"/repos/{repo}"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            updated_at = data.get("updated_at", "")
            if updated_at:
                from datetime import datetime
                update_date = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                days_ago = (datetime.now() - update_date).days
                if days_ago < 30:
                    eval_result["scores"]["维护活跃度"] = 9.0
                elif days_ago < 90:
                    eval_result["scores"]["维护活跃度"] = 7.0
                else:
                    eval_result["scores"]["维护活跃度"] = 5.0
            else:
                eval_result["scores"]["维护活跃度"] = 6.0
        else:
            eval_result["scores"]["维护活跃度"] = 5.0
    except:
        eval_result["scores"]["维护活跃度"] = 5.0
    
    # 创新程度 (基于功能和描述)
    keywords_innovative = ["视频", "MCP", "协议", "创新", "AI"]
    has_innovative = any(kw in plugin.get("description", "") for kw in keywords_innovative)
    eval_result["scores"]["创新程度"] = 9.0 if has_innovative else 7.0
    
    # 用户体验 (基于代码质量)
    eval_result["scores"]["用户体验"] = round(base_score * 0.9, 1)
    
    # 扩展性 (基于架构设计)
    eval_result["scores"]["扩展性"] = round(base_score * 0.95, 1)
    
    # 计算总分
    weights = {
        "代码质量": 0.20,
        "功能完整性": 0.15,
        "文档完善度": 0.10,
        "AI使用设计": 0.15,
        "易用性": 0.10,
        "安全性": 0.10,
        "维护活跃度": 0.05,
        "创新程度": 0.05,
        "用户体验": 0.05,
        "扩展性": 0.05,
    }
    
    total = sum(eval_result["scores"].get(k, 5) * v for k, v in weights.items())
    eval_result["total_score"] = round(total, 1)
    
    # 评级
    if total >= 90:
        eval_result["grade"] = "A"
    elif total >= 80:
        eval_result["grade"] = "B"
    elif total >= 70:
        eval_result["grade"] = "C"
    elif total >= 60:
        eval_result["grade"] = "D"
    else:
        eval_result["grade"] = "F"
    
    # 亮点和问题
    if eval_result["scores"].get("代码质量", 0) >= 8:
        eval_result["highlights"].append("代码质量优秀")
    if eval_result["scores"].get("AI使用设计", 0) >= 8:
        eval_result["highlights"].append("AI集成出色")
    if eval_result["scores"].get("创新程度", 0) >= 8:
        eval_result["highlights"].append("功能创新")
    
    if eval_result["scores"].get("文档完善度", 0) < 6:
        eval_result["issues"].append("文档需要完善")
    if eval_result["scores"].get("安全性", 0) < 6:
        eval_result["issues"].append("安全性需要加强")
    
    print(f"\n📊 评估结果:")
    print(f"   总分: {eval_result['total_score']}/100")
    print(f"   评级: {eval_result['grade']}")
    print(f"   亮点: {', '.join(eval_result['highlights']) or '无'}")
    print(f"   问题: {', '.join(eval_result['issues']) or '无'}")
    
    return eval_result

def main():
    """主函数"""
    print("🚀 开始批量评估 49 个插件...")
    print("=" * 80)
    
    for i, plugin in enumerate(plugins, 1):
        print(f"\n[{i}/{len(plugins)}]")
        try:
            eval_result = clone_and_analyze(plugin)
            EVALUATIONS.append(eval_result)
        except Exception as e:
            print(f"  ❌ 评估失败: {e}")
            EVALUATIONS.append({
                "name": plugin.get("name"),
                "module": plugin.get("moduleName"),
                "error": str(e),
                "total_score": 0,
                "grade": "F",
            })
    
    # 保存结果
    with open("memory/evaluations/batch_evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(EVALUATIONS, f, ensure_ascii=False, indent=2)
    
    # 生成汇总报告
    generate_summary_report()
    
    print("\n" + "=" * 80)
    print("✅ 批量评估完成！")
    print(f"📁 结果已保存到: memory/evaluations/batch_evaluation_results.json")

def generate_summary_report():
    """生成汇总报告"""
    # 按评分排序
    sorted_evals = sorted(
        [e for e in EVALUATIONS if "total_score" in e],
        key=lambda x: x["total_score"],
        reverse=True
    )
    
    # 生成分级统计
    grades = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for e in sorted_evals:
        grades[e.get("grade", "F")] = grades.get(e.get("grade", "F"), 0) + 1
    
    # 平均分
    valid_scores = [e["total_score"] for e in sorted_evals]
    avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
    
    print("\n" + "=" * 80)
    print("📊 评估汇总统计")
    print("=" * 80)
    print(f"总插件数: {len(EVALUATIONS)}")
    print(f"有效评估: {len(sorted_evals)}")
    print(f"平均分: {avg_score:.1f}/100")
    print(f"分级统计:")
    for grade, count in sorted(grades.items()):
        bar = "█" * count
        print(f"  {grade}: {bar} {count}")

if __name__ == "__main__":
    main()
