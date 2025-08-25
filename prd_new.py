#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRD New - 创建新的产品需求文档
实现 /pm:prd-new 命令的功能
"""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def validate_feature_name(feature_name):
    """
    验证功能名称格式
    必须是 kebab-case 格式：小写字母、数字、连字符，以字母开头
    """
    if not feature_name:
        return False, "功能名称不能为空"
    
    # 检查格式：小写字母、数字、连字符，以字母开头
    pattern = r'^[a-z][a-z0-9-]*$'
    if not re.match(pattern, feature_name):
        return False, ("❌ 功能名称必须是 kebab-case 格式（小写字母、数字、连字符）。"
                       "示例：user-auth, payment-v2, notification-system")
    
    return True, ""


def check_existing_prd(feature_name, prds_dir):
    """
    检查是否已存在同名PRD
    """
    prd_file = prds_dir / f"{feature_name}.md"
    return prd_file.exists()


def ensure_prds_directory(prds_dir):
    """
    确保PRD目录存在
    """
    try:
        prds_dir.mkdir(parents=True, exist_ok=True)
        return True, ""
    except Exception:
        return False, f"❌ 无法创建PRD目录。请手动创建：{prds_dir}"


def get_current_datetime():
    """
    获取当前ISO格式的日期时间
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ask_user_questions(feature_name, interactive=True):
    """
    向用户询问PRD相关问题
    """
    print(f"\n🚀 开始为功能 '{feature_name}' 创建PRD")
    
    if not interactive:
        # 非交互模式，使用默认值
        return {
            'description': f"{feature_name} 功能的产品需求文档",
            'problem': "待详细分析",
            'importance': "提升用户体验和产品价值",
            'target_users': "产品的目标用户群体",
            'use_cases': "待详细分析用户使用场景",
            'core_features': "待详细设计核心功能",
            'performance': "待性能测试和优化",
            'security': "遵循安全最佳实践",
            'success_metrics': "待定义具体的成功指标",
            'constraints': "待技术评估",
            'timeline': "待项目规划",
            'out_of_scope': "待明确功能边界",
            'dependencies': "待依赖分析"
        }
    
    print("请回答以下问题来完善PRD内容：\n")
    
    questions = {
        'description': "请简要描述这个功能（一行概述）：",
        'problem': "这个功能要解决什么问题？",
        'importance': "为什么现在需要这个功能？",
        'target_users': "目标用户是谁？",
        'use_cases': "主要使用场景有哪些？",
        'core_features': "核心功能和能力有哪些？",
        'performance': "性能要求（如响应时间、并发量等）：",
        'security': "安全考虑（如权限、数据保护等）：",
        'success_metrics': "成功指标（如何衡量功能成功）：",
        'constraints': "技术限制或约束：",
        'timeline': "时间限制：",
        'out_of_scope': "明确不包含的功能：",
        'dependencies': "依赖的外部系统或团队："
    }
    
    answers = {}
    for key, question in questions.items():
        answer = input(f"{question} ")
        answers[key] = answer if answer.strip() else "待定"
    
    return answers


def create_prd_content(feature_name, answers, created_time):
    """
    创建PRD内容
    """
    content = f"""---
name: {feature_name}
description: {answers['description']}
status: backlog
created: {created_time}
---

# PRD: {feature_name}

## Executive Summary

{answers['description']}

## Problem Statement

**问题描述：**
{answers['problem']}

**重要性：**
{answers['importance']}

## User Stories

**目标用户：**
{answers['target_users']}

**使用场景：**
{answers['use_cases']}

**用户旅程：**
- 用户发现问题
- 用户寻找解决方案
- 用户使用该功能
- 用户获得价值

## Requirements

### Functional Requirements

**核心功能：**
{answers['core_features']}

**用户交互流程：**
- 待详细设计

### Non-Functional Requirements

**性能要求：**
{answers['performance']}

**安全考虑：**
{answers['security']}

**可扩展性：**
- 支持未来功能扩展
- 模块化设计

## Success Criteria

**成功指标：**
{answers['success_metrics']}

**关键指标：**
- 用户采用率
- 功能使用频率
- 用户满意度

## Constraints & Assumptions

**技术限制：**
{answers['constraints']}

**时间约束：**
{answers['timeline']}

**资源限制：**
- 开发资源
- 测试资源
- 运维资源

**假设条件：**
- 用户具备基本操作能力
- 系统环境稳定

## Out of Scope

**明确不包含的功能：**
{answers['out_of_scope']}

## Dependencies

**外部依赖：**
{answers['dependencies']}

**内部团队依赖：**
- 开发团队
- 测试团队
- 产品团队
- 运维团队

## Implementation Notes

**技术栈建议：**
- 待技术评估

**架构考虑：**
- 待架构设计

**测试策略：**
- 单元测试
- 集成测试
- 用户验收测试
"""
    return content


def save_prd(prd_file, content):
    """
    保存PRD文件
    """
    try:
        with open(prd_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, ""
    except Exception as e:
        return False, f"❌ 保存PRD文件失败：{str(e)}"


def main():
    """
    主函数
    """
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("用法: python prd_new.py <feature_name> [--non-interactive]")
        print("示例: python prd_new.py user-authentication")
        print("      python prd_new.py user-authentication --non-interactive")
        sys.exit(1)
    
    feature_name = sys.argv[1]
    interactive = True
    
    if len(sys.argv) == 3 and sys.argv[2] == '--non-interactive':
        interactive = False
    
    # 1. 输入验证
    is_valid, error_msg = validate_feature_name(feature_name)
    if not is_valid:
        print(error_msg)
        sys.exit(1)
    
    # 2. 设置路径
    current_dir = Path.cwd()
    prds_dir = current_dir / ".claude" / "prds"
    
    # 3. 确保目录存在
    success, error_msg = ensure_prds_directory(prds_dir)
    if not success:
        print(error_msg)
        sys.exit(1)
    
    # 4. 检查是否已存在
    prd_file = prds_dir / f"{feature_name}.md"
    if check_existing_prd(feature_name, prds_dir):
        response = input(f"⚠️ PRD '{feature_name}' 已存在。是否要覆盖？(yes/no): ")
        if response.lower() != 'yes':
            print(f"建议使用不同的名称或运行: "
                  f"python prd_parse.py {feature_name} 从现有PRD创建epic")
            sys.exit(0)
    
    # 5. 收集PRD信息
    answers = ask_user_questions(feature_name, interactive)
    
    # 6. 获取当前时间
    created_time = get_current_datetime()
    
    # 7. 创建PRD内容
    content = create_prd_content(feature_name, answers, created_time)
    
    # 8. 保存PRD
    success, error_msg = save_prd(prd_file, content)
    if not success:
        print(error_msg)
        sys.exit(1)
    
    # 9. 成功提示
    print(f"\n✅ PRD 已创建：{prd_file}")
    print("\n📋 PRD 概要：")
    print(f"- 功能名称：{feature_name}")
    print(f"- 描述：{answers['description']}")
    print("- 状态：backlog")
    print(f"- 创建时间：{created_time}")
    print(f"\n🚀 准备创建实现epic？运行：python prd_parse.py {feature_name}")

if __name__ == "__main__":
    main()