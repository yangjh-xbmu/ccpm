#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIPM CLI启动脚本（AI增强版）
默认启用AI增强功能的命令行工具
"""

import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def modify_args_for_ai_default():
    """修改命令行参数，默认启用AI功能"""
    # 检查是否已经有AI相关参数
    if '--ai-enhance' not in sys.argv and '--no-ai-enhance' not in sys.argv:
        # 如果是prd create命令，默认添加--ai-enhance
        if 'prd' in sys.argv and 'create' in sys.argv:
            sys.argv.append('--ai-enhance')
    
    if '--ai-decompose' not in sys.argv and '--no-ai-decompose' not in sys.argv:
        # 如果是epic decompose命令，默认添加--ai-decompose
        if 'epic' in sys.argv and 'decompose' in sys.argv:
            sys.argv.append('--ai-decompose')

def show_ai_status():
    """显示AI功能状态"""
    try:
        from aipm_config import get_config
        config = get_config()
        
        if config.get('google_api_key'):
            print("🤖 AI功能已启用 (默认模式)")
        else:
            print("⚠️  AI功能未配置 - 请设置GOOGLE_API_KEY环境变量")
            print("   或运行: python aipm_config.py 创建配置文件")
    except ImportError:
        print("⚠️  配置模块未找到")

# 导入并运行CLI
if __name__ == '__main__':
    try:
        # 显示AI状态（仅在非help命令时）
        if '--help' not in sys.argv and '-h' not in sys.argv and '--version' not in sys.argv:
            show_ai_status()
        
        # 修改参数以默认启用AI
        modify_args_for_ai_default()
        
        from aipm.cli import main
        main()
    except ImportError as e:
        print(f"错误: 无法导入AIPM模块: {e}")
        print("请确保您在正确的目录中运行此脚本")
        sys.exit(1)
    except Exception as e:
        print(f"运行错误: {e}")
        sys.exit(1)