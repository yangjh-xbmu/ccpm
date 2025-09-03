#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIPM包工作流程测试脚本
测试完整的PRD创建和Epic分解工作流程
"""

import sys
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))


def test_prd_workflow():
    """测试PRD创建工作流程"""
    print("\n🔍 测试PRD创建工作流程...")
    
    try:
        from aipm.commands.prd_new import PRDContentGenerator
        from aipm.core.base import BaseFileManager
        
        # 测试功能名称
        feature_name = "test-feature"
        
        # 创建内容生成器
        generator = PRDContentGenerator()
        
        # 模拟用户输入
        answers = {
            'description': '测试功能描述',
            'executive_summary': '这是一个测试功能的执行摘要',
            'problem_statement': '解决测试中的问题',
            'user_stories': [
                '作为用户，我希望能够测试功能',
                '作为开发者，我希望能够验证实现'
            ],
            'functional_requirements': [
                '系统必须支持测试操作',
                '系统必须提供测试反馈'
            ],
            'non_functional_requirements': [
                '响应时间小于1秒',
                '支持并发用户数100+'
            ]
        }
        
        # 生成PRD内容
        file_manager = BaseFileManager()
        created_time = file_manager.get_current_datetime()
        
        content = generator.generate_content(feature_name, answers, created_time)
        
        print("✅ PRD内容生成成功")
        print(f"内容长度: {len(content)} 字符")
        
        # 验证内容包含必要部分
        required_sections = [
            '# test-feature',
            '## Executive Summary',
            '## Problem Statement',
            '## User Stories',
            '## Requirements'
        ]
        
        for section in required_sections:
            if section in content:
                print(f"✅ 包含章节: {section}")
            else:
                print(f"❌ 缺少章节: {section}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ PRD工作流程测试失败: {e}")
        return False


def test_epic_decompose_workflow():
    """测试Epic分解工作流程"""
    print("\n🔍 测试Epic分解工作流程...")
    
    try:
        from aipm.commands.epic_decompose import TaskContentGenerator
        from aipm.core.base import BaseFileManager
        
        # 测试功能名称
        feature_name = "test-epic"
        
        # 创建任务内容生成器
        generator = TaskContentGenerator()
        
        # 模拟Epic信息
        epic_info = {
            'name': feature_name,
            'description': '测试Epic的描述信息',
            'objectives': ['目标1', '目标2'],
            'scope': '测试范围说明'
        }
        
        # 模拟任务列表
        tasks = [
            {
                'name': '设计数据库模型',
                'category': 'backend',
                'priority': 'high',
                'effort': '2天',
                'description': '设计和实现数据库表结构',
                'acceptance_criteria': '数据库表创建完成并通过测试',
                'dependencies': '无'
            },
            {
                'name': '实现API接口',
                'category': 'backend',
                'priority': 'high',
                'effort': '3天',
                'description': '实现RESTful API接口',
                'acceptance_criteria': (
                    'API接口功能完整并通过单元测试'
                ),
                'dependencies': '数据库模型'
            },
            {
                'name': '前端界面开发',
                'category': 'frontend',
                'priority': 'medium',
                'effort': '4天',
                'description': '开发用户界面组件',
                'acceptance_criteria': (
                    '界面符合设计稿并通过用户测试'
                ),
                'dependencies': 'API接口'
            }
        ]
        
        # 生成任务内容
        file_manager = BaseFileManager()
        created_time = file_manager.get_current_datetime()
        
        content = generator.generate_content(
            feature_name, epic_info, tasks, created_time
        )
        
        print("✅ 任务分解内容生成成功")
        print(f"内容长度: {len(content)} 字符")
        print(f"任务数量: {len(tasks)}")
        
        # 验证内容包含必要部分
        required_sections = [
            f'# {feature_name} - Task Breakdown',
            '## Epic Overview',
            '## Task List',
            '## Task Details',
            '## Progress Tracking'
        ]
        
        for section in required_sections:
            if section in content:
                print(f"✅ 包含章节: {section}")
            else:
                print(f"❌ 缺少章节: {section}")
                return False
        
        # 验证任务信息
        for i, task in enumerate(tasks, 1):
            task_name = task['name']
            if task_name in content:
                print(f"✅ 包含任务: {task_name}")
            else:
                print(f"❌ 缺少任务: {task_name}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Epic分解工作流程测试失败: {e}")
        return False


def test_file_operations():
    """测试文件操作功能"""
    print("\n🔍 测试文件操作功能...")
    
    try:
        from aipm.core.base import BaseFileManager
        
        file_manager = BaseFileManager()
        
        # 创建测试目录和文件
        test_dir = Path("test_temp")
        test_file = test_dir / "test.md"
        
        # 测试目录创建
        file_manager.ensure_directory(test_dir)
        if test_dir.exists():
            print("✅ 测试目录创建成功")
        else:
            print("❌ 测试目录创建失败")
            return False
        
        # 测试文件写入
        test_content = "# 测试文件\n\n这是测试内容。"
        file_manager.write_file(test_file, test_content)
        
        if file_manager.file_exists(test_file):
            print("✅ 测试文件创建成功")
        else:
            print("❌ 测试文件创建失败")
            return False
        
        # 测试文件读取
        read_content = file_manager.read_file(test_file)
        if read_content == test_content:
            print("✅ 文件读取内容正确")
        else:
            print("❌ 文件读取内容不匹配")
            return False
        
        # 清理测试文件
        shutil.rmtree(test_dir)
        print("✅ 测试文件清理完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 文件操作测试失败: {e}")
        return False


def test_content_extraction():
    """测试内容提取功能"""
    print("\n🔍 测试内容提取功能...")
    
    try:
        from aipm.utils.helpers import ContentExtractor
        
        # 测试Frontmatter提取
        test_content = """---
name: test-feature
status: draft
created: 2024-01-01
---

# Test Feature

## Overview
This is a test feature.

## Requirements
- Requirement 1
- Requirement 2
"""
        
        frontmatter = ContentExtractor.extract_frontmatter(test_content)
        
        expected_fields = ['name', 'status', 'created']
        for field in expected_fields:
            if field in frontmatter:
                print(f"✅ Frontmatter包含字段: {field} = {frontmatter[field]}")
            else:
                print(f"❌ Frontmatter缺少字段: {field}")
                return False
        
        # 测试章节提取
        overview = ContentExtractor.extract_section(test_content, "Overview")
        if "This is a test feature." in overview:
            print("✅ 章节提取成功")
        else:
            print("❌ 章节提取失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 内容提取测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("="*60)
    print("AIPM包工作流程测试")
    print("="*60)
    
    tests = [
        ("PRD创建工作流程", test_prd_workflow),
        ("Epic分解工作流程", test_epic_decompose_workflow),
        ("文件操作功能", test_file_operations),
        ("内容提取功能", test_content_extraction),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print(f"\n{'='*60}")
    print(f"测试结果: {passed}/{total} 通过")
    print(f"{'='*60}")
    
    if passed == total:
        print("🎉 所有工作流程测试通过！")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关功能")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)