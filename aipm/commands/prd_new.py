#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCPM PM PRD创建命令
重构后的PRD创建功能，使用面向对象设计
"""

from pathlib import Path
from typing import Dict, Any

from ..core.base import (BaseWorkflowStep, BaseContentGenerator,
                         BaseInteractionHandler)
from ..ai.client import ai_client, AIPromptBuilder
from ..utils.helpers import ContentFormatter, InteractionHelper, PathHelper


class PRDContentGenerator(BaseContentGenerator):
    """PRD内容生成器"""

    def generate_content(self, feature_name: str, answers: Dict[str, Any],
                         created_time: str) -> str:
        """生成PRD内容"""
        frontmatter = {
            'name': feature_name,
            'description': answers.get('description', ''),
            'status': 'draft',
            'created': created_time
        }

        content_parts = [
            ContentFormatter.format_frontmatter(frontmatter),
            '',
            f'# {feature_name}',
            '',
            '## Executive Summary',
            answers.get('executive_summary', '待详细分析'),
            '',
            '## Problem Statement',
            answers.get('problem_statement', '待分析用户痛点'),
            '',
            '## User Stories',
            self._format_user_stories(answers.get('user_stories', [])),
            '',
            '## Requirements',
            '',
            '### Functional Requirements',
            self._format_requirements(
                answers.get('functional_requirements', [])),
            '',
            '### Non-Functional Requirements',
            self._format_requirements(
                answers.get('non_functional_requirements', [])),
            '',
            '### Technical Constraints',
            self._format_requirements(
                answers.get('technical_constraints', [])),
            '',
            '## Success Metrics',
            self._format_requirements(answers.get('success_metrics', [])),
            '',
            '## Timeline',
            answers.get('timeline', '待项目经理确定'),
            '',
            '## Resources',
            answers.get('resources', '待资源分配'),
        ]

        return '\n'.join(content_parts)

    def get_template(self) -> str:
        """获取PRD模板"""
        return """
---
name: {feature_name}
description: {description}
status: draft
created: {created_time}
---

# {feature_name}

## Executive Summary
{executive_summary}

## Problem Statement
{problem_statement}

## User Stories
{user_stories}

## Requirements

### Functional Requirements
{functional_requirements}

### Non-Functional Requirements
{non_functional_requirements}

### Technical Constraints
{technical_constraints}

## Success Metrics
{success_metrics}

## Timeline
{timeline}

## Resources
{resources}
"""

    def _format_user_stories(self, stories: list) -> str:
        """格式化用户故事"""
        if not stories:
            return "- 待补充用户故事"

        formatted = []
        for story in stories:
            if isinstance(story, dict):
                role = story.get('role', '用户')
                action = story.get('action', '执行操作')
                benefit = story.get('benefit', '获得价值')
                formatted.append(f"- 作为{role}，我希望{action}，以便{benefit}")
            else:
                formatted.append(f"- {story}")

        return '\n'.join(formatted)

    def _format_requirements(self, requirements: list) -> str:
        """格式化需求列表"""
        if not requirements:
            return "- 待补充"

        return '\n'.join(f"- {req}" for req in requirements)


class PRDInteractionHandler(BaseInteractionHandler):
    """PRD交互处理器"""

    def collect_user_input(self, feature_name: str, mode: str = 'interactive') -> Dict[str, Any]:
        """收集用户输入"""
        if mode == 'ai':
            return self._collect_ai_input(feature_name)
        elif mode == 'non-interactive':
            return self._create_default_answers(feature_name)
        else:
            return self._collect_interactive_input(feature_name)

    def confirm_action(self, message: str) -> bool:
        """确认操作"""
        return InteractionHelper.confirm_action(message)

    def _collect_interactive_input(self, feature_name: str) -> Dict[str, Any]:
        """收集交互式输入"""
        print(f"\n🚀 开始创建功能 '{feature_name}' 的PRD")
        print("请回答以下问题来生成PRD内容：\n")

        answers = {}

        # 基本信息
        answers['description'] = InteractionHelper.get_user_input(
            "功能描述", required=True)

        # 问题陈述
        answers['problem_statement'] = InteractionHelper.get_user_input(
            "要解决的问题", required=True)

        # 用户故事
        print("\n📝 用户故事 (输入空行结束):")
        stories = []
        while True:
            story = InteractionHelper.get_user_input("用户故事")
            if not story:
                break
            stories.append(story)
        answers['user_stories'] = stories

        # 功能需求
        print("\n⚙️ 功能需求 (输入空行结束):")
        func_reqs = []
        while True:
            req = InteractionHelper.get_user_input("功能需求")
            if not req:
                break
            func_reqs.append(req)
        answers['functional_requirements'] = func_reqs

        # 非功能需求
        print("\n🔧 非功能需求 (输入空行结束):")
        non_func_reqs = []
        while True:
            req = InteractionHelper.get_user_input("非功能需求")
            if not req:
                break
            non_func_reqs.append(req)
        answers['non_functional_requirements'] = non_func_reqs

        # 成功指标
        print("\n📊 成功指标 (输入空行结束):")
        metrics = []
        while True:
            metric = InteractionHelper.get_user_input("成功指标")
            if not metric:
                break
            metrics.append(metric)
        answers['success_metrics'] = metrics

        return answers

    def _collect_ai_input(self, feature_name: str) -> Dict[str, Any]:
        """使用AI收集输入"""
        print(f"\n🤖 使用AI协作模式创建功能 '{feature_name}' 的PRD")

        # 收集基本信息
        basic_info = {
            'description': InteractionHelper.get_user_input(
                "功能描述", required=True
            ),
            'target_users': InteractionHelper.get_user_input(
                "目标用户", "一般用户"
            ),
            'business_value': InteractionHelper.get_user_input(
                "商业价值", required=True
            )
        }

        # 使用AI生成详细内容
        if ai_client.is_available():
            print("\n🔄 AI正在分析并生成PRD内容...")
            prompt = AIPromptBuilder.build_prd_analysis_prompt(
                feature_name, basic_info)
            ai_content = ai_client.generate_content(prompt)

            if ai_content:
                return self._parse_ai_content(ai_content, basic_info)

        print("⚠️ AI不可用，使用默认内容")
        return self._create_default_answers(feature_name)

    def _create_default_answers(self, feature_name: str) -> Dict[str, Any]:
        """创建默认答案"""
        return {
            'description': f'{feature_name}功能实现',
            'problem_statement': '待详细分析用户需求和痛点',
            'user_stories': ['待补充用户故事'],
            'functional_requirements': ['待补充功能需求'],
            'non_functional_requirements': ['待补充非功能需求'],
            'technical_constraints': ['待评估技术约束'],
            'success_metrics': ['待定义成功指标'],
            'timeline': '待项目经理确定',
            'resources': '待资源分配'
        }

    def _parse_ai_content(self, ai_content: str, basic_info: Dict[str, Any]) -> Dict[str, Any]:
        """解析AI生成的内容"""
        from ..utils.helpers import ContentExtractor

        answers = basic_info.copy()

        # 提取各个章节
        sections = {
            'executive_summary': 'Executive Summary',
            'problem_statement': 'Problem Statement',
            'user_stories': 'User Stories',
            'functional_requirements': 'Functional Requirements',
            'non_functional_requirements': 'Non-Functional Requirements',
            'technical_constraints': 'Technical Constraints'
        }

        for key, section_name in sections.items():
            content = ContentExtractor.extract_ai_section(
                ai_content, section_name)
            if content:
                list_keys = ['user_stories', 'functional_requirements',
                             'non_functional_requirements', 'technical_constraints']
                if key in list_keys:
                    # 将列表格式的内容转换为数组
                    items = [line.strip('- ').strip()
                             for line in content.split('\n')
                             if line.strip().startswith('-')]
                    answers[key] = items if items else [content]
                else:
                    answers[key] = content

        return answers


class PRDNewCommand(BaseWorkflowStep):
    """PRD创建命令"""

    def __init__(self, feature_name: str, mode: str = 'interactive'):
        super().__init__(feature_name, mode)
        self.content_generator = PRDContentGenerator()
        self.interaction_handler = PRDInteractionHandler()

    def validate_preconditions(self) -> bool:
        """验证前置条件"""
        # 验证功能名称
        is_valid, error_msg = self.validator.validate_feature_name(
            self.feature_name)
        if not is_valid:
            print(error_msg)
            return False

        # 检查PRD是否已存在
        prd_path = Path(PathHelper.get_prd_path(self.feature_name))
        if self.file_manager.file_exists(prd_path):
            print(f"❌ PRD文件已存在: {prd_path}")
            if not self.interaction_handler.confirm_action("是否覆盖现有文件?"):
                return False

        # 确保PRD目录存在
        prds_dir = Path(".claude/prds")
        self.file_manager.ensure_directory(prds_dir)

        return True

    def execute(self) -> Dict[str, Any]:
        """执行PRD创建"""
        # 收集用户输入
        answers = self.interaction_handler.collect_user_input(
            self.feature_name, self.mode)

        # 生成PRD内容
        created_time = self.file_manager.get_current_datetime()
        prd_content = self.content_generator.generate_content(
            self.feature_name, answers, created_time
        )

        # 保存PRD文件
        prd_path = Path(PathHelper.get_prd_path(self.feature_name))
        self.file_manager.write_file(prd_path, prd_content)

        return {
            'prd_file': str(prd_path),
            'answers': answers,
            'created_time': created_time,
            'content': prd_content
        }

    def post_process(self, result: Dict[str, Any]) -> bool:
        """后处理"""
        # 显示创建摘要
        print("\n✅ PRD创建成功!")
        print(f"📄 文件位置: {result['prd_file']}")
        print(f"⏰ 创建时间: {result['created_time']}")

        # 显示下一步建议
        print("\n🚀 下一步操作:")
        print(f"   python -m ccpm_pm.commands.prd_parse {self.feature_name}")
        print(f"   或运行: ccpm pm:prd-parse {self.feature_name}")

        return True
