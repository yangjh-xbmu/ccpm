#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCPM PM Package
产品管理工作流程包

提供PRD创建、解析和Epic分解的完整工作流程
"""

__version__ = '1.0.0'
__author__ = 'CCPM Team'
__description__ = 'CCPM Product Management Workflow Package'

# 导入核心类
from .core.base import (
    ValidationError,
    FileOperationError,
    BaseValidator,
    BaseFileManager,
    BaseWorkflowStep,
    BaseContentGenerator,
    BaseInteractionHandler
)

# 导入AI客户端
from .ai.client import AIClient, AIPromptBuilder

# 导入工具类
from .utils.helpers import (
    ContentExtractor,
    ContentFormatter,
    InteractionHelper,
    PathHelper
)

# 导入命令类
from .commands.prd_new import PRDNewCommand
from .commands.prd_parse import PRDParseCommand
from .commands.epic_decompose import EpicDecomposeCommand

# 公共接口
__all__ = [
    # 版本信息
    '__version__',
    '__author__',
    '__description__',
    
    # 异常类
    'ValidationError',
    'FileOperationError',
    
    # 基础类
    'BaseValidator',
    'BaseFileManager',
    'BaseWorkflowStep',
    'BaseContentGenerator',
    'BaseInteractionHandler',
    
    # AI类
    'AIClient',
    'AIPromptBuilder',
    
    # 工具类
    'ContentExtractor',
    'ContentFormatter',
    'InteractionHelper',
    'PathHelper',
    
    # 命令类
    'PRDNewCommand',
    'PRDParseCommand',
    'EpicDecomposeCommand',
]


def create_prd(feature_name: str, mode: str = 'interactive'):
    """创建PRD的便捷函数"""
    command = PRDNewCommand(feature_name, mode)
    if command.validate_preconditions():
        result = command.execute()
        command.post_process(result)
        return result
    return None


def parse_prd(feature_name: str, mode: str = 'interactive'):
    """解析PRD的便捷函数"""
    command = PRDParseCommand(feature_name, mode)
    if command.validate_preconditions():
        result = command.execute()
        command.post_process(result)
        return result
    return None


def decompose_epic(feature_name: str, mode: str = 'interactive'):
    """分解Epic的便捷函数"""
    command = EpicDecomposeCommand(feature_name, mode)
    if command.validate_preconditions():
        result = command.execute()
        command.post_process(result)
        return result
    return None


def run_full_workflow(feature_name: str, mode: str = 'interactive'):
    """运行完整工作流程的便捷函数"""
    print(f"🚀 开始为功能 '{feature_name}' 运行完整PM工作流程")
    
    # 步骤1: 创建PRD
    print("\n📝 步骤1: 创建PRD")
    prd_result = create_prd(feature_name, mode)
    if not prd_result:
        print("❌ PRD创建失败，工作流程终止")
        return None
    
    # 步骤2: 解析PRD为Epic
    print("\n🔧 步骤2: 解析PRD为Epic")
    epic_result = parse_prd(feature_name, mode)
    if not epic_result:
        print("❌ Epic创建失败，工作流程终止")
        return None
    
    # 步骤3: 分解Epic为任务
    print("\n📋 步骤3: 分解Epic为任务")
    tasks_result = decompose_epic(feature_name, mode)
    if not tasks_result:
        print("❌ 任务分解失败，工作流程终止")
        return None
    
    print("\n✅ 完整PM工作流程执行成功!")
    print(f"📄 PRD文件: {prd_result['prd_file']}")
    print(f"🔧 Epic文件: {epic_result['epic_file']}")
    print(f"📋 任务文件: {tasks_result['tasks_file']}")
    
    return {
        'prd_result': prd_result,
        'epic_result': epic_result,
        'tasks_result': tasks_result
    }