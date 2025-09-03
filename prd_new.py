#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRD New - 创建新的产品需求文档
实现 /pm:prd-new 命令的功能
支持AI协作生成PRD内容
"""

import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
    if not load_dotenv():
        print("警告：未找到.env文件，将使用系统环境变量")
except ImportError:
    pass  # 如果没有安装python-dotenv，继续使用系统环境变量

try:
    import google.generativeai as genai
except ImportError:
    print("❌ 请安装google-generativeai库: pip install google-generativeai")
    sys.exit(1)


# AI配置
AI_MODEL = "gemini-2.5-pro"
AI_API_KEY_ENV = "GEMINI_API_KEY"


def configure_ai() -> bool:
    """
    配置AI模型
    """
    api_key = os.getenv(AI_API_KEY_ENV)
    if not api_key:
        print(f"❌ 请设置环境变量 {AI_API_KEY_ENV}")
        print("   export GEMINI_API_KEY=your_api_key")
        return False

    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"❌ AI配置失败: {str(e)}")
        return False


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
    使用系统命令获取真实时间，遵循ccpm标准
    """
    import subprocess
    try:
        # 使用系统命令获取真实时间，与ccpm保持一致
        result = subprocess.run(['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'],
                                capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        # 如果系统命令失败，回退到Python实现
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_ai_prompts() -> Dict[str, str]:
    """
    获取AI提示词模板
    """
    return {
        'problem_analysis': """
你是一位资深的产品经理。基于以下功能信息，请详细分析问题和重要性：

功能名称：{feature_name}
功能描述：{description}
目标用户：{target_users}

请提供：
1. 问题描述：详细描述这个功能要解决的具体问题
2. 重要性分析：解释为什么现在需要这个功能，包括业务价值和用户价值

要求：
- 内容具体、可操作
- 基于用户需求和业务目标
- 避免空泛的描述
""",

        'use_cases': """
你是一位资深的产品经理。基于以下功能信息，请详细设计使用场景：

功能名称：{feature_name}
功能描述：{description}
目标用户：{target_users}

请提供：
1. 主要使用场景：3-5个具体的使用场景
2. 用户旅程：详细的用户操作流程

要求：
- 场景具体、真实
- 覆盖不同类型的用户
- 包含完整的操作流程
""",

        'core_features': """
你是一位资深的产品经理。基于以下功能信息，请详细设计核心功能：

功能名称：{feature_name}
功能描述：{description}
目标用户：{target_users}
使用场景：{use_cases}

请提供：
1. 核心功能列表：详细的功能点
2. 用户交互流程：具体的操作步骤
3. 功能优先级：按重要性排序

要求：
- 功能具体、可实现
- 交互流程清晰
- 考虑用户体验
""",

        'success_metrics': """
你是一位资深的产品经理。基于以下功能信息，请设计成功指标：

功能名称：{feature_name}
功能描述：{description}
核心功能：{core_features}

请提供：
1. 关键指标：3-5个可量化的指标
2. 目标值：每个指标的具体目标
3. 监控方法：如何收集和分析数据

要求：
- 指标可量化、可监控
- 目标值合理、可达成
- 与业务目标对齐
"""
    }


def create_default_answers(feature_name):
    """
    为非交互模式创建默认答案
    """
    return {
        'description': f"{feature_name} 功能的产品需求文档",
        'problem': "待详细分析",
        'importance': "提升用户体验和产品价值",
        'target_users': "产品的目标用户群体",
        'user_pain_points': "待分析用户痛点",
        'use_cases': "待详细分析使用场景",
        'user_journey': "待设计用户旅程",
        'core_features': "待详细设计核心功能",
        'user_interactions': "待设计交互流程",
        'performance': "待性能测试和优化",
        'security': "遵循安全最佳实践",
        'scalability': "待评估扩展需求",
        'success_metrics': "待定义具体的成功指标",
        'kpis': "待确定关键指标",
        'constraints': "待技术评估",
        'timeline': "待项目规划",
        'dependencies': "待依赖分析",
        'out_of_scope': "待明确功能边界"
    }


def conduct_brainstorming_session(feature_name):
    """
    进行全面的brainstorming会话，遵循ccpm标准
    探索边缘情况，确保PRD的全面覆盖
    """
    print(f"\n🚀 开始为功能 '{feature_name}' 进行brainstorming会话")
    print("\n我是产品经理，将通过深入探讨来创建全面的PRD。")
    print("让我们一起探索这个功能的各个方面...\n")

    # 第一阶段：发现与上下文
    print("=== 第一阶段：发现与上下文 ===")
    description = input("请简要描述这个功能（一行概述）：").strip() or "待详细描述"

    print("\n让我们深入了解问题背景...")
    problem = input("这个功能要解决什么具体问题？").strip() or "待详细分析"
    importance = input("为什么现在需要这个功能？业务价值是什么？").strip() or "待评估业务价值"

    print("\n现在让我们了解用户...")
    target_users = input("目标用户是谁？请描述用户画像：").strip() or "待确定目标用户"
    user_pain_points = input("用户当前遇到的痛点是什么？").strip() or "待分析用户痛点"

    # 第二阶段：用户故事与场景
    print("\n=== 第二阶段：用户故事与使用场景 ===")
    print("让我们探索具体的使用场景...")
    use_cases = input("请描述3-5个主要使用场景：").strip() or "待详细分析使用场景"
    user_journey = input("描述典型的用户操作流程：").strip() or "待设计用户旅程"

    # 第三阶段：功能需求
    print("\n=== 第三阶段：功能需求 ===")
    print("现在让我们定义具体的功能...")
    core_features = input("核心功能和能力有哪些？").strip() or "待详细设计核心功能"
    user_interactions = input("用户如何与这些功能交互？").strip() or "待设计交互流程"

    # 第四阶段：非功能性需求
    print("\n=== 第四阶段：非功能性需求 ===")
    performance = input("性能要求（响应时间、并发量等）：").strip() or "待性能测试和优化"
    security = input("安全考虑（权限、数据保护等）：").strip() or "遵循安全最佳实践"
    scalability = input("可扩展性需求：").strip() or "待评估扩展需求"

    # 第五阶段：成功标准
    print("\n=== 第五阶段：成功标准 ===")
    success_metrics = input("如何衡量功能成功？具体指标：").strip() or "待定义具体的成功指标"
    kpis = input("关键KPI指标：").strip() or "待确定关键指标"

    # 第六阶段：约束与依赖
    print("\n=== 第六阶段：约束与依赖 ===")
    constraints = input("技术限制或约束：").strip() or "待技术评估"
    timeline = input("时间限制：").strip() or "待项目规划"
    dependencies = input("依赖的外部系统或团队：").strip() or "待依赖分析"

    # 第七阶段：边界定义
    print("\n=== 第七阶段：边界定义 ===")
    out_of_scope = input("明确不包含的功能（重要！）：").strip() or "待明确功能边界"

    print("\n✅ Brainstorming会话完成！正在整理PRD内容...")

    return {
        'description': description,
        'problem': problem,
        'importance': importance,
        'target_users': target_users,
        'user_pain_points': user_pain_points,
        'use_cases': use_cases,
        'user_journey': user_journey,
        'core_features': core_features,
        'user_interactions': user_interactions,
        'performance': performance,
        'security': security,
        'scalability': scalability,
        'success_metrics': success_metrics,
        'kpis': kpis,
        'constraints': constraints,
        'timeline': timeline,
        'dependencies': dependencies,
        'out_of_scope': out_of_scope
    }


def generate_ai_content(prompt: str, max_retries: int = 3) -> Optional[str]:
    """
    使用AI生成内容
    """
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel(AI_MODEL)
            response = model.generate_content(prompt)

            if response.text:
                return response.text.strip()
            else:
                print(f"⚠️ AI响应为空，尝试 {attempt + 1}/{max_retries}")

        except Exception as e:
            print(f"⚠️ AI调用失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)  # 等待2秒后重试

    return None


def confirm_or_edit_content(content: str, section_name: str) -> str:
    """
    让用户确认或编辑AI生成的内容
    """
    print(f"\n📝 AI生成的{section_name}内容：")
    print("-" * 50)
    print(content)
    print("-" * 50)

    while True:
        choice = input("\n请选择操作：\n1. 接受此内容\n2. 手动编辑\n3. 重新生成\n"
                       "请输入选择 (1/2/3): ").strip()

        if choice == '1':
            return content
        elif choice == '2':
            print(f"\n请编辑{section_name}内容（输入空行结束）：")
            lines = []
            while True:
                line = input()
                if line == "":
                    break
                lines.append(line)
            if lines:
                return "\n".join(lines)
            else:
                print("❌ 内容不能为空，请重新选择")
        elif choice == '3':
            return "REGENERATE"
        else:
            print("❌ 无效选择，请输入1、2或3")


def ask_user_questions_with_ai(feature_name: str) -> Dict[str, Any]:
    """
    使用AI协作收集PRD信息
    """
    print(f"\n🚀 开始为功能 '{feature_name}' 创建PRD（AI协作模式）")
    print("\n📋 请提供基本信息，AI将帮助生成详细内容：\n")

    # 收集基本信息
    basic_info = {
        'description': (input("请简要描述这个功能（一行概述）：").strip() or
                        "待定"),
        'target_users': (input("目标用户是谁？").strip() or
                         "待定"),
        'performance': (input("性能要求（如响应时间、并发量等，可选）：").strip() or
                        "待性能测试和优化"),
        'security': (input("安全考虑（如权限、数据保护等，可选）：").strip() or
                     "遵循安全最佳实践"),
        'constraints': (input("技术限制或约束（可选）：").strip() or
                        "待技术评估"),
        'timeline': (input("时间限制（可选）：").strip() or
                     "待项目规划"),
        'out_of_scope': (input("明确不包含的功能（可选）：").strip() or
                         "待明确功能边界"),
        'dependencies': (input("依赖的外部系统或团队（可选）：").strip() or
                         "待依赖分析")
    }

    print("\n🤖 正在使用AI生成详细内容...")

    # 获取AI提示词模板
    prompts = get_ai_prompts()

    # 使用AI生成问题分析
    print("\n🔍 生成问题分析...")
    problem_prompt = prompts['problem_analysis'].format(
        feature_name=feature_name,
        description=basic_info['description'],
        target_users=basic_info['target_users']
    )

    while True:
        problem_content = generate_ai_content(problem_prompt)
        if problem_content:
            result = confirm_or_edit_content(problem_content, "问题分析")
            if result != "REGENERATE":
                # 解析问题分析内容
                lines = result.split('\n')
                problem_desc = []
                importance = []
                current_section = None

                for line in lines:
                    line = line.strip()
                    if '问题描述' in line or '1.' in line:
                        current_section = 'problem'
                        continue
                    elif '重要性' in line or '2.' in line:
                        current_section = 'importance'
                        continue
                    elif line and current_section == 'problem':
                        problem_desc.append(line)
                    elif line and current_section == 'importance':
                        importance.append(line)

                basic_info['problem'] = ('\n'.join(problem_desc) if problem_desc
                                         else result)
                basic_info['importance'] = ('\n'.join(importance) if importance
                                            else "提升用户体验和产品价值")
                break
        else:
            print("❌ AI生成失败，请手动输入问题描述：")
            problem_input = input("这个功能要解决什么问题？").strip()
            basic_info['problem'] = problem_input or "待详细分析"
            importance_input = input("为什么现在需要这个功能？").strip()
            basic_info['importance'] = importance_input or "提升用户体验和产品价值"
            break

    # 使用AI生成使用场景
    print("\n📱 生成使用场景...")
    use_cases_prompt = prompts['use_cases'].format(
        feature_name=feature_name,
        description=basic_info['description'],
        target_users=basic_info['target_users']
    )

    while True:
        use_cases_content = generate_ai_content(use_cases_prompt)
        if use_cases_content:
            result = confirm_or_edit_content(use_cases_content, "使用场景")
            if result != "REGENERATE":
                basic_info['use_cases'] = result
                break
        else:
            print("❌ AI生成失败，请手动输入使用场景：")
            use_cases_input = input("主要使用场景有哪些？").strip()
            basic_info['use_cases'] = use_cases_input or "待详细分析用户使用场景"
            break

    # 使用AI生成核心功能
    print("\n⚙️ 生成核心功能...")
    core_features_prompt = prompts['core_features'].format(
        feature_name=feature_name,
        description=basic_info['description'],
        target_users=basic_info['target_users'],
        use_cases=basic_info['use_cases']
    )

    while True:
        core_features_content = generate_ai_content(core_features_prompt)
        if core_features_content:
            result = confirm_or_edit_content(core_features_content, "核心功能")
            if result != "REGENERATE":
                basic_info['core_features'] = result
                break
        else:
            print("❌ AI生成失败，请手动输入核心功能：")
            features_input = input("核心功能和能力有哪些？").strip()
            basic_info['core_features'] = features_input or "待详细设计核心功能"
            break

    # 使用AI生成成功指标
    print("\n📊 生成成功指标...")
    success_metrics_prompt = prompts['success_metrics'].format(
        feature_name=feature_name,
        description=basic_info['description'],
        core_features=basic_info['core_features']
    )

    while True:
        success_metrics_content = generate_ai_content(success_metrics_prompt)
        if success_metrics_content:
            result = confirm_or_edit_content(success_metrics_content, "成功指标")
            if result != "REGENERATE":
                basic_info['success_metrics'] = result
                break
        else:
            print("❌ AI生成失败，请手动输入成功指标：")
            metrics_input = input("成功指标（如何衡量功能成功）：").strip()
            basic_info['success_metrics'] = metrics_input or "待定义具体的成功指标"
            break

    print("\n✅ AI协作内容生成完成！")
    return basic_info


def create_prd_content(feature_name, answers, created_time):
    """
    创建PRD内容，严格遵循ccpm标准格式
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
{answers.get('problem', '待详细分析')}

**重要性分析：**
{answers.get('importance', '待评估业务价值')}

**用户痛点：**
{answers.get('user_pain_points', '待分析用户痛点')}

## User Stories

**目标用户画像：**
{answers['target_users']}

**主要使用场景：**
{answers['use_cases']}

**用户旅程：**
{answers.get('user_journey', '待设计用户旅程')}

**验收标准：**
- 用户能够成功完成核心功能操作
- 用户体验符合预期
- 性能指标达到要求

## Requirements

### Functional Requirements

**核心功能：**
{answers['core_features']}

**用户交互流程：**
{answers.get('user_interactions', '待设计交互流程')}

### Non-Functional Requirements

**性能要求：**
{answers['performance']}

**安全考虑：**
{answers['security']}

**可扩展性：**
{answers.get('scalability', '待评估扩展需求')}

## Success Criteria

**成功指标：**
{answers['success_metrics']}

**关键KPI：**
{answers.get('kpis', '待确定关键指标')}

**可衡量的结果：**
- 功能使用率
- 用户满意度
- 性能指标达成

## Constraints & Assumptions

**技术限制：**
{answers['constraints']}

**时间约束：**
{answers['timeline']}

**资源限制：**
待评估开发资源需求

## Out of Scope

{answers['out_of_scope']}

## Dependencies

**外部依赖：**
{answers['dependencies']}

**内部团队依赖：**
待确认团队协作需求

## Implementation Notes

待技术团队进行详细设计和架构评估。

---

**质量检查清单：**
- [ ] 所有章节内容完整（无占位符文本）
- [ ] 用户故事包含验收标准
- [ ] 成功标准可衡量
- [ ] 依赖关系明确识别
- [ ] 范围外项目明确列出
"""
    return content


def perform_quality_checks(answers):
    """
    执行PRD质量检查，遵循ccpm标准
    """
    issues = []

    # 检查是否有占位符文本
    placeholder_patterns = ['待', '待定', '待详细', '待分析', '待设计', '待评估']

    for key, value in answers.items():
        if any(pattern in str(value) for pattern in placeholder_patterns):
            issues.append(f"- {key}: 包含占位符文本")

    # 检查关键字段是否为空
    required_fields = ['description', 'problem',
                       'target_users', 'core_features']
    for field in required_fields:
        if not answers.get(field) or answers[field].strip() == "":
            issues.append(f"- {field}: 必填字段为空")

    return issues


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


def show_post_creation_summary(feature_name, answers, created_time, prd_file):
    """
    显示创建后的摘要和下一步建议，遵循ccpm标准
    """
    print(f"\n✅ PRD已创建：{prd_file}")

    print("\n📋 PRD概要：")
    print(f"- 功能名称：{feature_name}")
    print(f"- 描述：{answers['description']}")
    print(f"- 状态：backlog")
    print(f"- 创建时间：{created_time}")

    print("\n🎯 捕获的关键信息：")
    if answers.get('problem'):
        print(f"- 解决问题：{answers['problem'][:50]}...")
    if answers.get('target_users'):
        print(f"- 目标用户：{answers['target_users'][:50]}...")
    if answers.get('core_features'):
        print(f"- 核心功能：{answers['core_features'][:50]}...")

    print(f"\n🚀 准备创建实现epic？运行：/pm:prd-parse {feature_name}")
    print("\n💡 提示：使用 /pm:prd-edit 可以进一步完善PRD内容")


def main():
    """
    主函数
    """
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("用法: python prd_new.py <feature_name> [--ai|--non-interactive]")
        print("示例: python prd_new.py user-authentication")
        print("      python prd_new.py user-authentication --ai")
        print("      python prd_new.py user-authentication --non-interactive")
        sys.exit(1)

    feature_name = sys.argv[1]
    mode = 'interactive'  # 默认交互模式

    if len(sys.argv) == 3:
        if sys.argv[2] == '--ai':
            mode = 'ai'
        elif sys.argv[2] == '--non-interactive':
            mode = 'non-interactive'
        else:
            print("❌ 无效参数。支持的参数：--ai, --non-interactive")
            sys.exit(1)

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
            print(f"使用不同的名称或运行: /pm:prd-parse {feature_name} 从现有PRD创建epic")
            sys.exit(0)

    # 5. AI模式配置检查
    if mode == 'ai':
        if not configure_ai():
            sys.exit(1)
        print("✅ AI配置成功")

    # 6. 收集PRD信息
    if mode == 'ai':
        answers = ask_user_questions_with_ai(feature_name)
    elif mode == 'non-interactive':
        answers = create_default_answers(feature_name)
    else:
        answers = conduct_brainstorming_session(feature_name)

    # 7. 获取当前时间
    created_time = get_current_datetime()

    # 8. 质量检查（仅在交互模式下进行）
    if mode != 'non-interactive':
        print("\n🔍 执行质量检查...")
        quality_issues = perform_quality_checks(answers)
        if quality_issues:
            print("\n⚠️ 发现以下质量问题：")
            for issue in quality_issues:
                print(issue)

            if mode == 'interactive':
                continue_anyway = input("\n是否继续创建PRD？(yes/no): ")
                if continue_anyway.lower() not in ['yes', 'y']:
                    print("PRD创建已取消。请完善信息后重试。")
                    sys.exit(0)
        else:
            print("✅ 质量检查通过")

    # 9. 创建PRD内容
    content = create_prd_content(feature_name, answers, created_time)

    # 10. 保存PRD
    success, error_msg = save_prd(prd_file, content)
    if not success:
        print(error_msg)
        sys.exit(1)

    # 11. 显示创建后摘要
    show_post_creation_summary(feature_name, answers, created_time, prd_file)


if __name__ == "__main__":
    main()
