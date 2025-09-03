#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIPM CLI演示脚本

演示如何使用AIPM命令行工具的各种功能
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"命令: {cmd}")
    print(f"{'='*60}")
    
    try:
        # 使用python -m方式运行，避免安装问题
        if cmd.startswith('aipm'):
            cmd = cmd.replace('aipm', 'python -m aipm.cli', 1)
        
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=Path(__file__).parent / 'aipm'
        )
        
        if result.stdout:
            print("输出:")
            print(result.stdout)
        
        if result.stderr:
            print("错误:")
            print(result.stderr)
        
        if result.returncode != 0:
            print(f"⚠️  命令执行失败，返回码: {result.returncode}")
        else:
            print("✅ 命令执行成功")
            
    except Exception as e:
        print(f"❌ 执行出错: {e}")

def main():
    """主演示函数"""
    print("AIPM CLI功能演示")
    print("=================")
    
    # 确保在正确的目录
    os.chdir(Path(__file__).parent)
    
    # 1. 显示版本信息
    run_command("aipm --version", "显示版本信息")
    
    # 2. 显示帮助信息
    run_command("aipm --help", "显示帮助信息")
    
    # 3. PRD相关命令帮助
    run_command("aipm prd --help", "PRD命令帮助")
    
    # 4. Epic相关命令帮助
    run_command("aipm epic --help", "Epic命令帮助")
    
    # 5. 创建PRD（批处理模式）
    run_command(
        'aipm prd create --product-name "演示产品" --author "测试用户" --batch --output "demo_prd.md"',
        "创建PRD文档（批处理模式）"
    )
    
    # 6. 分解Epic（批处理模式）
    run_command(
        'aipm epic decompose --title "用户认证功能" --batch --output "demo_tasks.md"',
        "分解Epic为任务（批处理模式）"
    )
    
    # 7. 解析PRD（如果文件存在）
    prd_file = Path("aipm/demo_prd.md")
    if prd_file.exists():
        run_command(
            f'aipm prd parse "{prd_file}" --output "demo_prd_parsed.json"',
            "解析PRD文档"
        )
    
    print("\n" + "="*60)
    print("🎉 AIPM CLI演示完成！")
    print("="*60)
    
    # 显示生成的文件
    print("\n📁 生成的文件:")
    demo_files = [
        "aipm/demo_prd.md",
        "aipm/demo_tasks.md", 
        "aipm/demo_prd_parsed.json"
    ]
    
    for file_path in demo_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (未生成)")
    
    print("\n💡 提示:")
    print("  - 使用 'python -m aipm.cli --help' 查看完整帮助")
    print("  - 设置 GOOGLE_API_KEY 环境变量启用AI功能")
    print("  - 使用 'pip install -e aipm/' 安装包后可直接使用 'aipm' 命令")

if __name__ == "__main__":
    main()