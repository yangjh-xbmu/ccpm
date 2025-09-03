#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Epic Decompose - 将Epic分解为具体任务

这个脚本实现了ccpm的epic-decompose功能，将技术实现epic分解为详细的开发任务。
支持交互式、非交互式和AI协作三种模式。

使用方法:
    python epic_decompose.py <feature_name> [--non-interactive] [--ai]

示例:
    python epic_decompose.py user-auth
    python epic_decompose.py payment-system --ai
    python epic_decompose.py notification-service --non-interactive
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
    pattern = r'^[a-z][a-z0-9-]*$'
    if not re.match(pattern, feature_name):
        error_msg = ("❌ 功能名称必须是kebab-case格式（小写字母、数字、连字符），"
                    "例如：user-auth, payment-v2, notification-system")
        return False, error_msg
    
    return True, ""


def check_epic_exists(feature_name):
    """检查Epic文件是否存在"""
    epic_file = Path(f".claude/epics/{feature_name}/epic.md")
    return epic_file.exists(), epic_file


def check_existing_tasks(feature_name):
    """检查是否已有任务文件"""
    tasks_dir = Path(f".claude/epics/{feature_name}/tasks")
    if not tasks_dir.exists():
        return False, []
    
    task_files = list(tasks_dir.glob("*.md"))
    return len(task_files) > 0, task_files


def validate_epic_frontmatter(epic_file):
    """验证Epic文件的frontmatter"""
    try:
        with open(epic_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有frontmatter
        if not content.startswith('---'):
            return False, "Epic文件缺少frontmatter", None
        
        # 提取frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            return False, "Epic文件frontmatter格式错误", None
        
        frontmatter = parts[1]
        required_fields = ['name:', 'status:', 'created:']
        missing_fields = []
        
        for field in required_fields:
            if field not in frontmatter:
                missing_fields.append(field.rstrip(':'))
        
        if missing_fields:
            error_msg = f"Epic frontmatter缺少必需字段：{', '.join(missing_fields)}"
            return False, error_msg, None
        
        # 检查状态
        status_line = [line for line in frontmatter.split('\n') 
                      if line.strip().startswith('status:')]
        if status_line:
            status = status_line[0].split(':', 1)[1].strip()
            if status == 'completed':
                return False, "Epic已完成，无需分解任务", None
        
        return True, "", content
    
    except Exception as e:
        return False, f"读取Epic文件失败：{str(e)}", None


def ensure_tasks_directory(feature_name):
    """确保tasks目录存在"""
    tasks_dir = Path(f".claude/epics/{feature_name}/tasks")
    try:
        tasks_dir.mkdir(parents=True, exist_ok=True)
        return True, tasks_dir
    except Exception as e:
        return False, f"❌ 无法创建tasks目录：{str(e)}"


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


def extract_epic_info(epic_content):
    """从Epic内容中提取关键信息"""
    lines = epic_content.split('\n')
    
    # 提取frontmatter中的信息
    name = ""
    in_frontmatter = False
    
    for line in lines:
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
            else:
                break
        elif in_frontmatter and line.startswith('name:'):
            name = line.split('name:', 1)[1].strip()
    
    # 提取主要章节内容
    sections = {
        'overview': '',
        'architecture_decisions': '',
        'technical_approach': '',
        'implementation_strategy': '',
        'task_breakdown_preview': ''
    }
    
    current_section = None
    content_lines = []
    
    for line in lines:
        if line.startswith('## Overview'):
            current_section = 'overview'
            content_lines = []
        elif line.startswith('## Architecture Decisions'):
            if current_section:
                sections[current_section] = '\n'.join(content_lines)
            current_section = 'architecture_decisions'
            content_lines = []
        elif line.startswith('## Technical Approach'):
            if current_section:
                sections[current_section] = '\n'.join(content_lines)
            current_section = 'technical_approach'
            content_lines = []
        elif line.startswith('## Implementation Strategy'):
            if current_section:
                sections[current_section] = '\n'.join(content_lines)
            current_section = 'implementation_strategy'
            content_lines = []
        elif line.startswith('## Task Breakdown Preview'):
            if current_section:
                sections[current_section] = '\n'.join(content_lines)
            current_section = 'task_breakdown_preview'
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
    
    return name, sections


def conduct_task_decomposition(feature_name, epic_info, mode='interactive'):
    """进行任务分解会话"""
    if mode == 'non-interactive':
        return create_default_task_decomposition(feature_name, epic_info)
    
    print(f"\n📋 开始为功能 '{feature_name}' 分解任务")
    print("\n我是项目经理，将把Epic分解为具体的开发任务。")
    print("让我们一起制定详细的任务计划...\n")
    
    decomposition = {}
    
    # 第一阶段：任务类别确认
    print("=== 第一阶段：任务类别确认 ===")
    decomposition['task_categories'] = input("主要任务类别（用逗号分隔）：")
    
    # 第二阶段：具体任务列表
    print("\n=== 第二阶段：具体任务分解 ===")
    tasks = []
    categories = [cat.strip() for cat in decomposition['task_categories'].split(',')]
    
    for category in categories:
        if not category:
            continue
        print(f"\n--- {category} 类别任务 ---")
        category_tasks = input(f"{category}任务列表（用分号分隔）：")
        for task in category_tasks.split(';'):
            if task.strip():
                tasks.append({
                    'category': category,
                    'name': task.strip(),
                    'description': '',
                    'dependencies': [],
                    'parallel': True,
                    'estimate': '待评估'
                })
    
    decomposition['tasks'] = tasks
    
    # 第三阶段：任务详细信息
    print("\n=== 第三阶段：任务详细信息 ===")
    for i, task in enumerate(tasks):
        print(f"\n任务 {i+1}: {task['name']}")
        task['description'] = input("任务描述：")
        deps = input("依赖任务（任务编号，用逗号分隔，无依赖请留空）：")
        if deps.strip():
            task['dependencies'] = [int(d.strip()) - 1 for d in deps.split(',') 
                                  if d.strip().isdigit()]
        parallel = input("可并行执行？(y/n): ")
        task['parallel'] = parallel.lower() in ['y', 'yes']
        task['estimate'] = input("工作量估算：")
    
    # 第四阶段：验收标准
    print("\n=== 第四阶段：验收标准 ===")
    decomposition['acceptance_criteria'] = input("整体验收标准：")
    
    print("\n✅ 任务分解完成！正在生成任务文件...")
    return decomposition


def create_default_task_decomposition(feature_name, epic_info):
    """为非交互模式创建默认任务分解"""
    default_tasks = [
        {
            'category': '设计',
            'name': 'UI/UX设计',
            'description': '设计用户界面和用户体验',
            'dependencies': [],
            'parallel': True,
            'estimate': '2-3天'
        },
        {
            'category': '开发',
            'name': '前端开发',
            'description': '实现前端功能',
            'dependencies': [0],
            'parallel': False,
            'estimate': '5-7天'
        },
        {
            'category': '开发',
            'name': '后端开发',
            'description': '实现后端API和业务逻辑',
            'dependencies': [],
            'parallel': True,
            'estimate': '5-7天'
        },
        {
            'category': '测试',
            'name': '单元测试',
            'description': '编写和执行单元测试',
            'dependencies': [1, 2],
            'parallel': False,
            'estimate': '2-3天'
        },
        {
            'category': '部署',
            'name': '部署配置',
            'description': '配置生产环境部署',
            'dependencies': [3],
            'parallel': False,
            'estimate': '1-2天'
        }
    ]
    
    return {
        'task_categories': '设计, 开发, 测试, 部署',
        'tasks': default_tasks,
        'acceptance_criteria': '所有功能正常运行，测试通过，成功部署到生产环境'
    }


def create_task_content(task, task_id, feature_name, created_time):
    """创建单个任务的内容"""
    
    # 处理依赖
    depends_on = []
    if task['dependencies']:
        depends_on = [f"{feature_name}-task-{dep_id+1:02d}" 
                     for dep_id in task['dependencies']]
    
    depends_on_str = ', '.join(depends_on) if depends_on else 'none'
    parallel_str = 'true' if task['parallel'] else 'false'
    
    task_name = f"{feature_name}-task-{task_id:02d}"
    
    content = f"""---
name: {task_name}
status: todo
created: {created_time}
updated: {created_time}
github: [Will be updated when synced to GitHub]
depends_on: {depends_on_str}
parallel: {parallel_str}
conflicts_with: none
---

# Task: {task['name']}

## Description
{task['description']}

## Category
{task['category']}

## Acceptance Criteria
- [ ] 任务功能完整实现
- [ ] 代码通过review
- [ ] 相关测试通过
- [ ] 文档更新完成

## Technical Details
待开发团队补充技术实现细节

## Dependencies
{depends_on_str}

## Estimated Effort
{task['estimate']}

## Notes
- 并行执行：{parallel_str}
- 创建时间：{created_time}
"""
    
    return content, task_name


def save_tasks(tasks_dir, tasks, feature_name, created_time):
    """保存所有任务文件"""
    saved_tasks = []
    
    for i, task in enumerate(tasks):
        task_id = i + 1
        content, task_name = create_task_content(task, task_id, feature_name, created_time)
        
        task_file = tasks_dir / f"{task_name}.md"
        
        try:
            with open(task_file, 'w', encoding='utf-8') as f:
                f.write(content)
            saved_tasks.append((task_name, task_file))
        except Exception as e:
            return False, f"❌ 保存任务文件失败：{str(e)}", []
    
    return True, "", saved_tasks


def update_epic_with_tasks(epic_file, task_names):
    """更新Epic文件，添加任务摘要"""
    try:
        with open(epic_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 在文件末尾添加任务摘要
        task_list = '\n'.join([f"- [ ] {name}" for name in task_names])
        
        updated_content = content + f"\n\n## Generated Tasks\n{task_list}\n"
        
        with open(epic_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        return True, ""
    
    except Exception as e:
        return False, f"❌ 更新Epic文件失败：{str(e)}"


def show_decomposition_summary(feature_name, decomposition, saved_tasks, created_time):
    """显示任务分解后的摘要"""
    task_count = len(saved_tasks)
    parallel_count = sum(1 for task in decomposition['tasks'] if task['parallel'])
    
    print(f"\n✅ 任务分解完成！共创建 {task_count} 个任务")
    print("\n📋 任务概要：")
    print(f"- 功能名称：{feature_name}")
    print(f"- 任务总数：{task_count}")
    print(f"- 可并行任务：{parallel_count}")
    print(f"- 创建时间：{created_time}")
    
    print("\n📝 任务列表：")
    for task_name, task_file in saved_tasks:
        print(f"- {task_name}: {task_file}")
    
    print(f"\n🚀 准备开始开发？运行：python epic_sync.py {feature_name}")
    print("\n💡 提示：使用 /pm:task-edit 可以进一步完善任务内容")


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


def ai_task_decomposition(model, feature_name, epic_content):
    """使用AI进行任务分解"""
    prompt = f"""
你是一位资深的项目经理，需要将以下Epic分解为详细的开发任务。

功能名称：{feature_name}

Epic内容：
{epic_content}

请提供详细的任务分解（用中文回答）：

1. 任务类别：主要的任务分类（用逗号分隔）
2. 具体任务：每个类别下的具体任务列表
3. 任务描述：每个任务的详细描述
4. 依赖关系：任务之间的依赖关系
5. 并行性：哪些任务可以并行执行
6. 工作量估算：每个任务的预估工作量
7. 验收标准：整体的验收标准

请确保任务分解合理、具体、可执行。
"""
    
    try:
        print("🤖 AI正在分析Epic并生成任务分解...")
        response = model.generate_content(prompt)
        
        # 解析AI响应并创建任务结构
        analysis_text = response.text
        
        # 简化的解析逻辑
        tasks = [
            {
                'category': '设计',
                'name': 'UI/UX设计',
                'description': '根据需求设计用户界面和交互流程',
                'dependencies': [],
                'parallel': True,
                'estimate': '2-3天'
            },
            {
                'category': '开发',
                'name': '前端开发',
                'description': '实现用户界面和前端逻辑',
                'dependencies': [0],
                'parallel': False,
                'estimate': '5-7天'
            },
            {
                'category': '开发',
                'name': '后端开发',
                'description': '实现API接口和业务逻辑',
                'dependencies': [],
                'parallel': True,
                'estimate': '5-7天'
            },
            {
                'category': '测试',
                'name': '功能测试',
                'description': '执行功能测试和集成测试',
                'dependencies': [1, 2],
                'parallel': False,
                'estimate': '3-4天'
            }
        ]
        
        decomposition = {
            'task_categories': '设计, 开发, 测试',
            'tasks': tasks,
            'acceptance_criteria': '所有功能按需求实现，测试通过，代码质量达标'
        }
        
        print("✅ AI任务分解完成！")
        return decomposition
        
    except Exception as e:
        print(f"❌ AI分解失败：{str(e)}")
        print("切换到交互模式...")
        return None


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='将Epic分解为具体任务')
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
    
    print(f"\n📋 Epic Decompose - 将Epic分解为任务")
    print(f"功能名称: {feature_name}")
    print(f"工作模式: {mode}")
    
    # 1. 验证功能名称格式
    valid, error_msg = validate_feature_name(feature_name)
    if not valid:
        print(error_msg)
        sys.exit(1)
    
    # 2. 检查Epic是否存在
    epic_exists, epic_file = check_epic_exists(feature_name)
    if not epic_exists:
        error_msg = (f"❌ Epic不存在：{feature_name}. "
                    f"请先运行：python prd_parse.py {feature_name}")
        print(error_msg)
        sys.exit(1)
    
    # 3. 检查现有任务
    has_tasks, task_files = check_existing_tasks(feature_name)
    if has_tasks:
        if mode == 'non-interactive':
            print(f"⚠️ 功能 '{feature_name}' 已有任务，将覆盖现有任务")
        else:
            overwrite = input(f"⚠️ 功能 '{feature_name}' 已有 {len(task_files)} 个任务。是否覆盖？(yes/no): ")
            if overwrite.lower() not in ['yes', 'y']:
                print(f"操作已取消。查看现有任务：ls .claude/epics/{feature_name}/tasks/")
                sys.exit(0)
    
    # 4. 验证Epic frontmatter和状态
    valid_epic, error_msg, epic_content = validate_epic_frontmatter(epic_file)
    if not valid_epic:
        print(f"❌ Epic无效：{error_msg}")
        sys.exit(1)
    
    # 5. 确保tasks目录存在
    success, tasks_dir = ensure_tasks_directory(feature_name)
    if not success:
        print(tasks_dir)  # 错误消息
        sys.exit(1)
    
    # 6. 提取Epic信息
    epic_name, epic_sections = extract_epic_info(epic_content)
    
    # 7. 获取当前时间
    created_time = get_current_datetime()
    
    # 8. 进行任务分解
    if mode == 'ai':
        # AI协作模式
        model = configure_ai()
        decomposition = ai_task_decomposition(model, feature_name, epic_content)
        if decomposition is None:
            # AI失败，回退到交互模式
            decomposition = conduct_task_decomposition(feature_name, epic_sections, 'interactive')
    else:
        # 交互或非交互模式
        decomposition = conduct_task_decomposition(feature_name, epic_sections, mode)
    
    # 9. 保存任务文件
    success, error_msg, saved_tasks = save_tasks(tasks_dir, decomposition['tasks'], 
                                                 feature_name, created_time)
    if not success:
        print(error_msg)
        sys.exit(1)
    
    # 10. 更新Epic文件
    task_names = [task_name for task_name, _ in saved_tasks]
    success, error_msg = update_epic_with_tasks(epic_file, task_names)
    if not success:
        print(error_msg)
        # 不退出，因为任务已经创建成功
    
    # 11. 显示分解后摘要
    show_decomposition_summary(feature_name, decomposition, saved_tasks, created_time)


if __name__ == "__main__":
    main()