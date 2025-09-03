#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIPM CLI 演示脚本
展示 AIPM 命令行工具的各种功能
"""

import os
import subprocess
from pathlib import Path


def run_command(cmd: str, description: str = "") -> None:
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    if description:
        print(f"📋 {description}")
    print(f"🔧 执行命令: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        if result.stdout:
            print("📤 输出:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️ 错误信息:")
            print(result.stderr)
        
        if result.returncode != 0:
            print(f"❌ 命令执行失败，退出码: {result.returncode}")
        else:
            print("✅ 命令执行成功")
            
    except Exception as e:
        print(f"❌ 执行出错: {e}")


def cleanup_demo_files():
    """清理演示文件"""
    demo_files = [
        "demo_prd.md",
        "demo_tasks.md", 
        "demo_prd_parsed.json"
    ]
    
    for file in demo_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"🗑️ 已删除: {file}")


def main():
    """主演示函数"""
    print("🚀 AIPM CLI 功能演示")
    print("=" * 60)
    
    # 清理之前的演示文件
    cleanup_demo_files()
    
    # 1. 显示版本信息
    run_command(
        "python -m aipm.cli --version",
        "显示 AIPM 版本信息"
    )
    
    # 2. 显示帮助信息
    run_command(
        "python -m aipm.cli --help",
        "显示 AIPM 帮助信息"
    )
    
    # 3. 显示PRD命令帮助
    run_command(
        "python -m aipm.cli prd --help",
        "显示 PRD 命令帮助"
    )
    
    # 4. 显示Epic命令帮助
    run_command(
        "python -m aipm.cli epic --help",
        "显示 Epic 命令帮助"
    )
    
    # 5. 创建PRD文档（批处理模式）
    run_command(
        "python -m aipm.cli prd create --product-name \"演示产品\" "
        "--author \"演示用户\" --batch --output demo_prd.md",
        "创建 PRD 文档（批处理模式）"
    )
    
    # 6. 分解Epic为任务（批处理模式）
    run_command(
        "python -m aipm.cli epic decompose --title \"用户认证系统\" "
        "--batch --output demo_tasks.md",
        "分解 Epic 为任务（批处理模式）"
    )
    
    # 7. 解析PRD文档
    run_command(
        "python -m aipm.cli prd parse demo_prd.md "
        "--output demo_prd_parsed.json",
        "解析 PRD 文档"
    )
    
    # 8. 显示生成的文件
    print("\n" + "="*60)
    print("📁 生成的文件列表:")
    print("="*60)
    
    demo_files = [
        "demo_prd.md",
        "demo_tasks.md",
        "demo_prd_parsed.json"
    ]
    
    for file in demo_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file} ({size} bytes)")
        else:
            print(f"❌ {file} (未生成)")
    
    print("\n🎉 AIPM CLI 演示完成！")
    print("\n💡 提示:")
    print("- 使用 --batch 参数可以跳过交互式输入")
    print("- 使用 --ai-enhance 或 --ai-decompose 可以启用AI功能"
          "（需要配置API密钥）")
    print("- 查看生成的文件了解更多详情")


if __name__ == "__main__":
    main()