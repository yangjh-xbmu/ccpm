#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRD Parse - 将PRD转换为技术实现epic

这个脚本实现了ccpm的prd-parse功能，将产品需求文档(PRD)转换为详细的技术实现epic。
支持交互式、非交互式和AI协作三种模式。

使用方法:
    python prd_parse.py <feature_name> [--non-interactive] [--ai]

示例:
    python prd_parse.py user-auth
    python prd_parse.py payment-system --ai
    python prd_parse.py notification-service --non-interactive
"""

import os
import sys
import argparse
import subprocess
import re
from pathlib import Path

# 尝试导入dotenv以支持.env文件
try:
    from dotenv import load_dotenv
    if not load_dotenv():
        print("警告：未找到.env文件，将使用系统环境变量")
except ImportError:
    pass  # 如果没有安装python-dotenv，继续使用系统环境变量

# AI配置
AI_API_KEY_ENV = "GEMINI_API_KEY"
AI_MODEL = "gemini-1.5-pro"

def validate_feature_name(feature_name):
    """验证功能名称格式"""
    if not feature_name:
        return False, "功能名称不能为空"
    
    # 检查格式：只允许小写字母、数字和连字符，必须以字母开头
    if not re.match(r'^[a-z][a-z0-9-]*$', feature_name):
        return False, "❌ 功能名称必须是kebab-case格式（小写字母、数字、连字符），例如：user-auth, payment-v2, notification-system"
    
    return True, ""

def check_prd_exists(feature_name):
    """检查PRD文件是否存在"""
    prd_file = Path(f".claude/prds/{feature_name}.md")
    return prd_file.exists(), prd_file

def validate_prd_frontmatter(prd_file):
    """验证PRD文件的frontmatter"""
    try:
        with open(prd_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有frontmatter
        if not content.startswith('---'):
            return False, "PRD文件缺少frontmatter"
        
        # 提取frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            return False, "PRD文件frontmatter格式错误"
        
        frontmatter = parts[1]
        required_fields = ['name:', 'description:', 'status:', 'created:']
        missing_fields = []
        
        for field in required_fields:
            if field not in frontmatter:
                missing_fields.append(field.rstrip(':'))
        
        if missing_fields:
            return False, f"PRD frontmatter缺少必需字段：{', '.join(missing_fields)}"
        
        return True, content
    
    except Exception as e:
        return False, f"读取PRD文件失败：{str(e)}"

def check_epic_exists(feature_name):
    """检查epic是否已存在"""
    epic_dir = Path(f".claude/epics/{feature_name}")
    epic_file = epic_dir / "epic.md"
    return epic_file.exists(), epic_file

def ensure_epic_directory(feature_name):
    """确保epic目录存在"""
    epic_dir = Path(f".claude/epics/{feature_name}")
    try:
        epic_dir.mkdir(parents=True, exist_ok=True)
        return True, epic_dir
    except Exception as e:
        return False, f"❌ 无法创建epic目录：{str(e)}"

def get_current_datetime():
    """获取当前ISO格式的日期时间"""
    try:
        result = subprocess.run(['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        # 如果系统命令失败，使用Python的datetime作为备选
        from datetime import datetime
        return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

def extract_prd_info(prd_content):
    """从PRD内容中提取关键信息"""
    lines = prd_content.split('\n')
    
    # 提取frontmatter中的描述
    description = ""
    in_frontmatter = False
    
    for line in lines:
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
            else:
                break
        elif in_frontmatter and line.startswith('description:'):
            description = line.split('description:', 1)[1].strip()
    
    # 提取主要章节内容
    sections = {
        'executive_summary': '',
        'problem_statement': '',
        'functional_requirements': '',
        'non_functional_requirements': '',
        'dependencies': ''
    }
    
    current_section = None
    content_lines = []
    
    for line in lines:
        if line.startswith('## Executive Summary'):
            current_section = 'executive_summary'
            content_lines = []
        elif line.startswith('## Problem Statement'):
            if current_section:
                sections[current_section] = '\n'.join(content_lines)
            current_section = 'problem_statement'
            content_lines = []
        elif line.startswith('### Functional Requirements'):
            if current_section:
                sections[current_section] = '\n'.join(content_lines)
            current_section = 'functional_requirements'
            content_lines = []
        elif line.startswith('### Non-Functional Requirements'):
            if current_section:
                sections[current_section] = '\n'.join(content_lines)
            current_section = 'non_functional_requirements'
            content_lines = []
        elif line.startswith('## Dependencies'):
            if current_section:
                sections[current_section] = '\n'.join(content_lines)
            current_section = 'dependencies'
            content_lines = []
        elif line.startswith('##') and current_section:
            # 新的章节开始，保存当前章节
            sections[current_section] = '\n'.join(content_lines)
            current_section = None
            content_lines = []
        elif current_section and line.strip():
            content_lines.append(line)
    
    # 保存最后一个章节
    if current_section and content_lines:
        sections[current_section] = '\n'.join(content_lines)
    
    return description, sections

def conduct_technical_analysis(feature_name, prd_info, mode='interactive'):
    """进行技术分析会话"""
    if mode == 'non-interactive':
        return create_default_technical_analysis(feature_name, prd_info)
    
    print(f"\n🔧 开始为功能 '{feature_name}' 进行技术分析")
    print("\n我是技术负责人，将分析PRD并制定技术实现方案。")
    print("让我们一起分析技术架构和实现策略...\n")
    
    analysis = {}
    
    # 第一阶段：架构决策
    print("=== 第一阶段：架构决策 ===")
    analysis['architecture_decisions'] = input("关键技术决策和理由（技术选型、设计模式等）：")
    analysis['technology_stack'] = input("技术栈选择（前端、后端、数据库等）：")
    
    # 第二阶段：技术方案
    print("\n=== 第二阶段：技术实现方案 ===")
    analysis['frontend_components'] = input("前端组件需求（UI组件、状态管理、交互模式）：")
    analysis['backend_services'] = input("后端服务需求（API端点、数据模型、业务逻辑）：")
    analysis['infrastructure'] = input("基础设施考虑（部署、扩展、监控）：")
    
    # 第三阶段：实现策略
    print("\n=== 第三阶段：实现策略 ===")
    analysis['implementation_phases'] = input("开发阶段划分：")
    analysis['risk_mitigation'] = input("风险缓解策略：")
    analysis['testing_approach'] = input("测试方法：")
    
    # 第四阶段：任务分解预览
    print("\n=== 第四阶段：任务分解预览 ===")
    analysis['task_categories'] = input("高级任务类别（用逗号分隔）：")
    
    # 第五阶段：工作量评估
    print("\n=== 第五阶段：工作量评估 ===")
    analysis['timeline_estimate'] = input("整体时间线评估：")
    analysis['resource_requirements'] = input("资源需求：")
    analysis['critical_path'] = input("关键路径项目：")
    
    print("\n✅ 技术分析完成！正在生成epic内容...")
    return analysis

def create_default_technical_analysis(feature_name, prd_info):
    """为非交互模式创建默认技术分析"""
    return {
        'architecture_decisions': '待技术团队确定架构决策和技术选型',
        'technology_stack': '待评估技术栈选择',
        'frontend_components': '待设计前端组件架构',
        'backend_services': '待设计后端服务架构',
        'infrastructure': '待评估基础设施需求',
        'implementation_phases': '待制定开发阶段计划',
        'risk_mitigation': '待识别和缓解技术风险',
        'testing_approach': '待制定测试策略',
        'task_categories': '设计, 开发, 测试, 部署',
        'timeline_estimate': '待评估开发时间线',
        'resource_requirements': '待评估资源需求',
        'critical_path': '待识别关键路径'
    }

def create_epic_content(feature_name, prd_description, analysis, created_time):
    """创建epic内容"""
    
    # 处理任务类别
    task_categories = analysis['task_categories'].split(',')
    task_breakdown = '\n'.join([f"- [ ] {cat.strip()}: 待详细分解" for cat in task_categories if cat.strip()])
    
    content = f"""---
name: {feature_name}
status: backlog
created: {created_time}
progress: 0%
prd: .claude/prds/{feature_name}.md
github: [Will be updated when synced to GitHub]
---

# Epic: {feature_name}

## Overview
{prd_description}

## Architecture Decisions
{analysis['architecture_decisions']}

**技术栈选择：**
{analysis['technology_stack']}

## Technical Approach

### Frontend Components
{analysis['frontend_components']}

### Backend Services
{analysis['backend_services']}

### Infrastructure
{analysis['infrastructure']}

## Implementation Strategy

**开发阶段：**
{analysis['implementation_phases']}

**风险缓解：**
{analysis['risk_mitigation']}

**测试方法：**
{analysis['testing_approach']}

## Task Breakdown Preview
高级任务类别：
{task_breakdown}

## Dependencies
待技术评估确定具体依赖关系

## Success Criteria (Technical)
- 所有功能需求得到技术实现
- 性能指标达到PRD要求
- 代码质量符合团队标准
- 测试覆盖率达到要求

## Estimated Effort

**整体时间线：**
{analysis['timeline_estimate']}

**资源需求：**
{analysis['resource_requirements']}

**关键路径：**
{analysis['critical_path']}
"""
    
    return content

def save_epic(epic_file, content):
    """保存epic文件"""
    try:
        with open(epic_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, ""
    except Exception as e:
        return False, f"❌ 保存epic文件失败：{str(e)}"

def show_epic_creation_summary(feature_name, analysis, created_time, epic_file):
    """显示epic创建后的摘要"""
    task_count = len([cat.strip() for cat in analysis['task_categories'].split(',') if cat.strip()])
    
    print(f"\n✅ Epic已创建：{epic_file}")
    print("\n📋 Epic概要：")
    print(f"- 功能名称：{feature_name}")
    print(f"- 状态：backlog")
    print(f"- 创建时间：{created_time}")
    print(f"- 进度：0%")
    
    print("\n🎯 技术分析结果：")
    print(f"- 任务类别数量：{task_count}")
    print(f"- 架构决策：{analysis['architecture_decisions'][:50]}...")
    print(f"- 时间线评估：{analysis['timeline_estimate']}")
    
    print(f"\n🚀 准备分解为具体任务？运行：python epic_decompose.py {feature_name}")
    print("\n💡 提示：使用 /pm:epic-edit 可以进一步完善Epic内容")

def configure_ai():
    """配置AI客户端"""
    api_key = os.getenv(AI_API_KEY_ENV)
    if not api_key:
        print(f"❌ 错误：未设置 {AI_API_KEY_ENV} 环境变量")
        print("请在 .env 文件中设置您的API密钥")
        sys.exit(1)
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(AI_MODEL)
        print(f"✅ AI配置成功，使用模型：{AI_MODEL}")
        return model
    except ImportError:
        print("❌ 错误：未安装 google-generativeai 库")
        print("请运行：pip install google-generativeai")
        sys.exit(1)
    except Exception as e:
        print(f"❌ AI配置失败：{str(e)}")
        sys.exit(1)

def ai_technical_analysis(model, feature_name, prd_content):
    """使用AI进行技术分析"""
    prompt = f"""
你是一位资深的技术架构师，需要将以下PRD转换为详细的技术实现epic。

功能名称：{feature_name}

PRD内容：
{prd_content}

请提供以下技术分析（用中文回答）：

1. 架构决策：关键技术决策和理由
2. 技术栈：推荐的技术栈选择
3. 前端组件：需要的UI组件和交互模式
4. 后端服务：API设计和数据模型
5. 基础设施：部署和扩展考虑
6. 实现阶段：开发阶段划分
7. 风险缓解：潜在风险和缓解策略
8. 测试方法：测试策略和方法
9. 任务类别：高级任务分类（用逗号分隔）
10. 时间评估：整体开发时间线
11. 资源需求：所需的开发资源
12. 关键路径：关键的依赖项目

请为每个方面提供具体、实用的建议。
"""
    
    try:
        print("🤖 AI正在分析PRD并生成技术方案...")
        response = model.generate_content(prompt)
        
        # 解析AI响应
        analysis_text = response.text
        
        # 简单的文本解析来提取各个部分
        analysis = {
            'architecture_decisions': extract_ai_section(analysis_text, '架构决策'),
            'technology_stack': extract_ai_section(analysis_text, '技术栈'),
            'frontend_components': extract_ai_section(analysis_text, '前端组件'),
            'backend_services': extract_ai_section(analysis_text, '后端服务'),
            'infrastructure': extract_ai_section(analysis_text, '基础设施'),
            'implementation_phases': extract_ai_section(analysis_text, '实现阶段'),
            'risk_mitigation': extract_ai_section(analysis_text, '风险缓解'),
            'testing_approach': extract_ai_section(analysis_text, '测试方法'),
            'task_categories': extract_ai_section(analysis_text, '任务类别'),
            'timeline_estimate': extract_ai_section(analysis_text, '时间评估'),
            'resource_requirements': extract_ai_section(analysis_text, '资源需求'),
            'critical_path': extract_ai_section(analysis_text, '关键路径')
        }
        
        print("✅ AI技术分析完成！")
        return analysis
        
    except Exception as e:
        print(f"❌ AI分析失败：{str(e)}")
        print("切换到交互模式...")
        return None

def extract_ai_section(text, section_name):
    """从AI响应中提取特定章节的内容"""
    lines = text.split('\n')
    content_lines = []
    in_section = False
    
    for line in lines:
        if section_name in line and ('：' in line or ':' in line):
            in_section = True
            # 如果同一行有内容，提取它
            if '：' in line:
                content = line.split('：', 1)[1].strip()
            elif ':' in line:
                content = line.split(':', 1)[1].strip()
            else:
                content = ''
            if content:
                content_lines.append(content)
        elif in_section and line.strip():
            if any(keyword in line for keyword in ['架构决策', '技术栈', '前端组件', '后端服务', '基础设施', '实现阶段', '风险缓解', '测试方法', '任务类别', '时间评估', '资源需求', '关键路径']):
                # 新的章节开始
                break
            content_lines.append(line.strip())
        elif in_section and not line.strip():
            # 空行，继续
            continue
    
    result = ' '.join(content_lines).strip()
    return result if result else f"待分析{section_name}"

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='将PRD转换为技术实现epic')
    parser.add_argument('feature_name', help='功能名称')
    parser.add_argument('--non-interactive', action='store_true', help='非交互模式')
    parser.add_argument('--ai', action='store_true', help='AI协作模式')
    
    args = parser.parse_args()
    feature_name = args.feature_name
    
    # 确定工作模式
    if args.ai:
        mode = 'ai'
    elif args.non_interactive:
        mode = 'non-interactive'
    else:
        mode = 'interactive'
    
    print(f"\n🔧 PRD Parse - 将PRD转换为Epic")
    print(f"功能名称: {feature_name}")
    print(f"工作模式: {mode}")
    
    # 1. 验证功能名称格式
    valid, error_msg = validate_feature_name(feature_name)
    if not valid:
        print(error_msg)
        sys.exit(1)
    
    # 2. 检查PRD是否存在
    prd_exists, prd_file = check_prd_exists(feature_name)
    if not prd_exists:
        print(f"❌ PRD不存在：{feature_name}. 请先运行：python prd_new.py {feature_name}")
        sys.exit(1)
    
    # 3. 验证PRD frontmatter
    valid_prd, prd_content = validate_prd_frontmatter(prd_file)
    if not valid_prd:
        print(f"❌ PRD frontmatter无效：{prd_content}")
        sys.exit(1)
    
    # 4. 检查epic是否已存在
    epic_exists, epic_file = check_epic_exists(feature_name)
    if epic_exists:
        if mode == 'non-interactive':
            print(f"⚠️ Epic '{feature_name}' 已存在，将覆盖现有文件")
        else:
            overwrite = input(f"⚠️ Epic '{feature_name}' 已存在。是否覆盖？(yes/no): ")
            if overwrite.lower() not in ['yes', 'y']:
                print(f"操作已取消。查看现有epic：python epic_show.py {feature_name}")
                sys.exit(0)
    
    # 5. 确保epic目录存在
    success, epic_dir = ensure_epic_directory(feature_name)
    if not success:
        print(epic_dir)  # 错误消息
        sys.exit(1)
    
    # 6. 提取PRD信息
    prd_description, prd_sections = extract_prd_info(prd_content)
    
    # 7. 获取当前时间
    created_time = get_current_datetime()
    
    # 8. 进行技术分析
    if mode == 'ai':
        # AI协作模式
        model = configure_ai()
        analysis = ai_technical_analysis(model, feature_name, prd_content)
        if analysis is None:
            # AI失败，回退到交互模式
            analysis = conduct_technical_analysis(feature_name, prd_sections, 'interactive')
    else:
        # 交互或非交互模式
        analysis = conduct_technical_analysis(feature_name, prd_sections, mode)
    
    # 9. 创建epic内容
    content = create_epic_content(feature_name, prd_description, analysis, created_time)
    
    # 10. 保存epic
    epic_file = epic_dir / "epic.md"
    success, error_msg = save_epic(epic_file, content)
    if not success:
        print(error_msg)
        sys.exit(1)
    
    # 11. 显示创建后摘要
    show_epic_creation_summary(feature_name, analysis, created_time, epic_file)

if __name__ == "__main__":
    main()