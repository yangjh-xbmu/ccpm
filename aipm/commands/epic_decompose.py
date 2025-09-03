#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCPM PM Epic分解命令
重构后的Epic分解功能，将Epic分解为具体任务
"""

from pathlib import Path
from typing import Dict, Any, List

from ..core.base import (BaseWorkflowStep, BaseContentGenerator,
                         BaseInteractionHandler)
from ..ai.client import ai_client, AIPromptBuilder
from ..utils.helpers import (ContentExtractor, ContentFormatter,
                             InteractionHelper, PathHelper)


class TaskContentGenerator(BaseContentGenerator):
    """任务内容生成器"""

    def generate_content(self, feature_name: str, epic_info: Dict[str, Any],
                         tasks: List[Dict[str, Any]],
                         created_time: str) -> str:
        """生成任务内容"""
        frontmatter = {
            'name': feature_name,
            'status': 'planning',
            'created': created_time,
            'epic': f'{feature_name}/epic.md',
            'total_tasks': len(tasks),
            'completed_tasks': 0,
            'progress': '0%'
        }

        content_parts = [
            ContentFormatter.format_frontmatter(frontmatter),
            '',
            f'# {feature_name} - Task Breakdown',
            '',
            '## Epic Overview',
            epic_info.get('description', ''),
            '',
            '## Task List',
            self._format_task_list(tasks),
            '',
            '## Task Details',
            self._format_task_details(tasks),
            '',
            '## Progress Tracking',
            '- [ ] All tasks planned',
            '- [ ] Development started',
            '- [ ] Testing completed',
            '- [ ] Ready for deployment',
        ]

        return '\n'.join(content_parts)

    def get_template(self) -> str:
        """获取任务模板"""
        return """
---
name: {feature_name}
status: planning
created: {created_time}
epic: {feature_name}/epic.md
total_tasks: {total_tasks}
completed_tasks: 0
progress: 0%
---

# {feature_name} - Task Breakdown

## Epic Overview
{epic_overview}

## Task List
{task_list}

## Task Details
{task_details}

## Progress Tracking
- [ ] All tasks planned
- [ ] Development started
- [ ] Testing completed
- [ ] Ready for deployment
"""

    def _format_task_list(self, tasks: List[Dict[str, Any]]) -> str:
        """格式化任务列表"""
        if not tasks:
            return "- 暂无任务"

        formatted = []
        for i, task in enumerate(tasks, 1):
            name = task.get('name', f'Task {i}')
            category = task.get('category', 'development')
            priority = task.get('priority', 'medium')
            effort = task.get('effort', 'TBD')

            priority_icon = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(priority, '⚪')

            formatted.append(
                f"{i}. {priority_icon} **{name}** ({category}) - {effort}")

        return '\n'.join(formatted)

    def _format_task_details(self, tasks: List[Dict[str, Any]]) -> str:
        """格式化任务详情"""
        if not tasks:
            return "暂无任务详情"

        formatted = []
        for i, task in enumerate(tasks, 1):
            name = task.get('name', f'Task {i}')
            description = task.get('description', '待补充描述')
            acceptance_criteria = task.get('acceptance_criteria', '待定义验收标准')
            dependencies = task.get('dependencies', '无')

            task_detail = [
                f"### {i}. {name}",
                '',
                '**描述:**',
                description,
                '',
                '**验收标准:**',
                acceptance_criteria,
                '',
                '**依赖关系:**',
                dependencies,
                ''
            ]

            formatted.extend(task_detail)

        return '\n'.join(formatted)


class TaskDecompositionHandler(BaseInteractionHandler):
    """任务分解处理器"""

    def collect_user_input(self, feature_name: str,
                           epic_info: Dict[str, Any],
                           mode: str = 'interactive') -> List[Dict[str, Any]]:
        """收集任务分解输入"""
        if mode == 'ai':
            return self._collect_ai_tasks(feature_name, epic_info)
        elif mode == 'non-interactive':
            return self._create_default_tasks(feature_name, epic_info)
        else:
            return self._collect_interactive_tasks(feature_name, epic_info)

    def confirm_action(self, message: str) -> bool:
        """确认操作"""
        return InteractionHelper.confirm_action(message)

    def _collect_interactive_tasks(self, feature_name: str,
                                   epic_info: Dict[str, Any]
                                   ) -> List[Dict[str, Any]]:
        """收集交互式任务分解"""
        print(f"\n📋 开始为功能 '{feature_name}' 分解任务")
        print("请定义具体的开发任务:\n")

        tasks = []
        task_num = 1

        while True:
            print(f"\n--- 任务 {task_num} ---")

            name = InteractionHelper.get_user_input(
                "任务名称", f"Task {task_num}")

            if not name or name.lower() in ['quit', 'exit', 'done']:
                break

            category = InteractionHelper.get_multiple_choice(
                "任务类别",
                ['frontend', 'backend', 'database', 'testing',
                 'deployment', 'other'],
                'development'
            )

            priority = InteractionHelper.get_multiple_choice(
                "优先级",
                ['high', 'medium', 'low'],
                'medium'
            )

            description = InteractionHelper.get_user_input(
                "任务描述", "待补充描述")

            effort = InteractionHelper.get_user_input(
                "预估工作量", "TBD")

            acceptance_criteria = InteractionHelper.get_user_input(
                "验收标准", "待定义验收标准")

            dependencies = InteractionHelper.get_user_input(
                "依赖关系", "无")

            task = {
                'name': name,
                'category': category,
                'priority': priority,
                'description': description,
                'effort': effort,
                'acceptance_criteria': acceptance_criteria,
                'dependencies': dependencies
            }

            tasks.append(task)
            task_num += 1

            if not InteractionHelper.confirm_action("继续添加任务?"):
                break

        return tasks

    def _collect_ai_tasks(self, feature_name: str,
                          epic_info: Dict[str, Any]
                          ) -> List[Dict[str, Any]]:
        """使用AI进行任务分解"""
        print(f"\n🤖 使用AI协作模式分解功能 '{feature_name}' 的任务")

        if ai_client.is_available():
            print("\n🔄 AI正在进行任务分解...")
            epic_content = epic_info.get('content', '')
            prompt = AIPromptBuilder.build_task_decomposition_prompt(
                feature_name, epic_content)
            ai_content = ai_client.generate_content(prompt)

            if ai_content:
                return self._parse_ai_tasks(ai_content)

        print("⚠️ AI不可用，使用默认任务")
        return self._create_default_tasks(feature_name, epic_info)

    def _create_default_tasks(self, feature_name: str,
                              epic_info: Dict[str, Any]
                              ) -> List[Dict[str, Any]]:
        """创建默认任务"""
        return [
            {
                'name': '需求分析和设计',
                'category': 'planning',
                'priority': 'high',
                'description': '分析功能需求，设计技术方案',
                'effort': '2-3天',
                'acceptance_criteria': '完成技术设计文档',
                'dependencies': '无'
            },
            {
                'name': '核心功能开发',
                'category': 'development',
                'priority': 'high',
                'description': '实现核心业务逻辑',
                'effort': '5-7天',
                'acceptance_criteria': '功能正常运行，通过单元测试',
                'dependencies': '需求分析完成'
            },
            {
                'name': '集成测试',
                'category': 'testing',
                'priority': 'medium',
                'description': '进行系统集成测试',
                'effort': '2-3天',
                'acceptance_criteria': '所有测试用例通过',
                'dependencies': '核心功能开发完成'
            },
            {
                'name': '部署上线',
                'category': 'deployment',
                'priority': 'medium',
                'description': '部署到生产环境',
                'effort': '1天',
                'acceptance_criteria': '功能在生产环境正常运行',
                'dependencies': '集成测试通过'
            }
        ]

    def _parse_ai_tasks(self, ai_content: str) -> List[Dict[str, Any]]:
        """解析AI任务分解"""
        tasks = []

        # 尝试从AI内容中提取任务
        task_section = ContentExtractor.extract_ai_section(
            ai_content, 'Tasks')
        if not task_section:
            task_section = ContentExtractor.extract_ai_section(
                ai_content, 'Task List')

        if task_section:
            # 简单解析任务列表
            lines = task_section.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('*') or
                             line[0].isdigit()):
                    # 提取任务名称
                    task_name = line.split('.', 1)[-1].strip()
                    task_name = task_name.lstrip('- *').strip()

                    if task_name:
                        tasks.append({
                            'name': task_name,
                            'category': 'development',
                            'priority': 'medium',
                            'description': '由AI生成的任务',
                            'effort': 'TBD',
                            'acceptance_criteria': '待定义验收标准',
                            'dependencies': '待分析'
                        })

        # 如果没有解析到任务，返回默认任务
        if not tasks:
            return self._create_default_tasks('', {})

        return tasks


class EpicDecomposeCommand(BaseWorkflowStep):
    """Epic分解命令"""

    def __init__(self, feature_name: str, mode: str = 'interactive'):
        super().__init__(feature_name, mode)
        self.content_generator = TaskContentGenerator()
        self.decomposition_handler = TaskDecompositionHandler()

    def validate_preconditions(self) -> bool:
        """验证前置条件"""
        # 验证功能名称
        is_valid, error_msg = self.validator.validate_feature_name(
            self.feature_name)
        if not is_valid:
            print(error_msg)
            return False

        # 检查Epic文件是否存在
        epic_path = Path(PathHelper.get_epic_path(self.feature_name))
        if not self.file_manager.file_exists(epic_path):
            print(f"❌ Epic文件不存在: {epic_path}")
            cmd = f"python -m ccpm_pm.commands.prd_parse {self.feature_name}"
            print(f"请先运行: {cmd}")
            return False

        # 验证Epic Frontmatter
        epic_content = self.file_manager.read_file(epic_path)
        required_fields = ['name', 'status', 'created']
        is_valid, error_msg = self.validator.validate_frontmatter(
            epic_content, required_fields)
        if not is_valid:
            print(f"❌ Epic Frontmatter验证失败: {error_msg}")
            return False

        # 检查任务文件是否已存在
        tasks_path = Path(PathHelper.get_tasks_path(self.feature_name))
        if self.file_manager.file_exists(tasks_path):
            print(f"⚠️ 任务文件已存在: {tasks_path}")
            if not self.decomposition_handler.confirm_action(
                    "是否覆盖现有任务?"):
                return False

        return True

    def execute(self) -> Dict[str, Any]:
        """执行Epic分解"""
        # 读取Epic文件
        epic_path = Path(PathHelper.get_epic_path(self.feature_name))
        epic_content = self.file_manager.read_file(epic_path)

        # 提取Epic信息
        epic_info = self._extract_epic_info(epic_content)

        # 进行任务分解
        tasks = self.decomposition_handler.collect_user_input(
            self.feature_name, epic_info, self.mode)

        # 生成任务内容
        created_time = self.file_manager.get_current_datetime()
        tasks_content = self.content_generator.generate_content(
            self.feature_name, epic_info, tasks, created_time)

        # 保存任务文件
        tasks_path = Path(PathHelper.get_tasks_path(self.feature_name))
        self.file_manager.write_file(tasks_path, tasks_content)

        return {
            'tasks_file': str(tasks_path),
            'epic_info': epic_info,
            'tasks': tasks,
            'created_time': created_time,
            'content': tasks_content
        }

    def post_process(self, result: Dict[str, Any]) -> bool:
        """后处理"""
        # 显示创建摘要
        print("\n✅ 任务分解完成!")
        print(f"📄 文件位置: {result['tasks_file']}")
        print(f"📋 任务数量: {len(result['tasks'])}")
        print(f"⏰ 创建时间: {result['created_time']}")

        # 显示任务摘要
        print("\n📋 任务摘要:")
        for i, task in enumerate(result['tasks'], 1):
            name = task.get('name', f'Task {i}')
            category = task.get('category', 'unknown')
            priority = task.get('priority', 'medium')
            effort = task.get('effort', 'TBD')

            priority_icon = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(priority, '⚪')

            print(f"   {i}. {priority_icon} {name} ({category}) - {effort}")

        # 显示下一步建议
        print("\n🚀 下一步操作:")
        print("   - 开始开发任务")
        print("   - 更新任务状态")
        print("   - 跟踪项目进度")

        return True

    def _extract_epic_info(self, epic_content: str) -> Dict[str, Any]:
        """提取Epic信息"""
        frontmatter = ContentExtractor.extract_frontmatter(epic_content)

        # 提取Overview部分
        overview = ContentExtractor.extract_section(
            epic_content, 'Overview')

        return {
            'name': frontmatter.get('name', self.feature_name),
            'status': frontmatter.get('status', 'planning'),
            'created': frontmatter.get('created', ''),
            'description': overview or '功能概述',
            'content': epic_content
        }
