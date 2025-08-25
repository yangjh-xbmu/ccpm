#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCPM 脚本使用示例

这个脚本演示了如何使用 CCPM 项目管理脚本的基本功能
"""

import os
import subprocess


def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"命令: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True,
                                text=True)
        
        if result.stdout:
            print("输出:")
            print(result.stdout)
        
        if result.stderr:
            print("错误:")
            print(result.stderr)
        
        if result.returncode != 0:
            print(f"命令执行失败，退出码: {result.returncode}")
            return False
        
        return True
        
    except Exception as e:
        print(f"执行命令时出错: {e}")
        return False


def main():
    """主函数 - 演示 CCPM 脚本使用"""
    print("CCPM 项目管理脚本使用示例")
    print("=" * 40)
    
    # 检查当前目录
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    
    # 检查是否在正确的项目目录
    if not os.path.exists('.env'):
        print("\n⚠️  警告: 未找到 .env 文件")
        print("请确保在 CCPM 项目根目录下运行此脚本")
        return
    
    # 激活虚拟环境的命令前缀
    if os.path.exists('venv'):
        venv_prefix = "source venv/bin/activate &&"
    else:
        venv_prefix = ""
    
    print("\n📋 可用的操作示例:")
    print("1. 查看 issue_close.py 帮助信息")
    print("2. 查看 epic_sync.py 帮助信息")
    print("3. 列出当前项目的任务文件")
    print("4. 退出")
    
    while True:
        try:
            choice = input("\n请选择操作 (1-4): ").strip()
            
            if choice == '1':
                cmd = (f"{venv_prefix} python .trae/scripts/pm/"
                       "issue_close.py --help")
                run_command(cmd, "查看 issue_close.py 帮助信息")
                
            elif choice == '2':
                cmd = (f"{venv_prefix} python .trae/scripts/pm/"
                       "epic_sync.py --help")
                run_command(cmd, "查看 epic_sync.py 帮助信息")
                
            elif choice == '3':
                print("\n📁 当前项目的任务文件:")
                for root, dirs, files in os.walk('.'):
                    for file in files:
                        if file.endswith('.md') and file != 'README.md':
                            file_path = os.path.join(root, file)
                            print(f"  {file_path}")
                            
            elif choice == '4':
                print("\n👋 再见！")
                break
                
            else:
                print("\n❌ 无效选择，请输入 1-4")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，退出程序")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")


if __name__ == "__main__":
    main()