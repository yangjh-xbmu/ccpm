#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCPM PM PRD解析命令
重构后的PRD解析功能，将PRD转换为技术实现Epic
"""

from pathlib import Path
from typing import Dict, Any

from ..core.base import (BaseWorkflowStep, BaseContentGenerator,
                         BaseInteractionHandler)
from ..ai.client import ai_client, AIPromptBuilder
from ..utils.helpers import (ContentExtractor, ContentFormatter,
                             InteractionHelper, PathHelper)


class PRDParser:
    """PRD解析器"""
    
    def __init__(self):
        self.content_extractor = ContentExtractor()
    
    def parse_content(self, content: str) -> Dict[str, Any]:
        """解析PRD内容"""
        # 提取Frontmatter
        frontmatter = self.content_extractor.extract_frontmatter(content)
        
        # 提取各个章节
        sections = {
            'executive_summary': self.content_extractor.extract_section(content, "## 执行摘要"),
            'problem_statement': self.content_extractor.extract_section(content, "## 问题陈述"),
            'user_stories': self.content_extractor.extract_section(content, "## 用户故事"),
            'functional_requirements': self.content_extractor.extract_section(content, "## 功能需求"),
            'non_functional_requirements': self.content_extractor.extract_section(content, "## 非功能需求")
        }
        
        # 解析功能需求列表
        features = []
        if sections['functional_requirements']:
            lines = sections['functional_requirements'].split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('-') or line.startswith('*'):
                    features.append(line[1:].strip())
        
        return {
            'product_name': frontmatter.get('name', ''),
            'version': frontmatter.get('version', ''),
            'author': frontmatter.get('author', ''),
            'created_time': frontmatter.get('created', ''),
            'status': frontmatter.get('status', ''),
            'description': frontmatter.get('description', ''),
            'sections': sections,
            'features': features,
            'frontmatter': frontmatter
        }


class EpicContentGenerator(BaseContentGenerator):
    """Epic内容生成器"""

    def generate_content(self, feature_name: str, prd_description: str,
                         analysis: Dict[str, Any],
                         created_time: str) -> str:
        """生成Epic内容"""
        frontmatter = {
            'name': feature_name,
            'status': 'planning',
            'created': created_time,
            'progress': '0%',
            'prd': f'.claude/prds/{feature_name}.md',
            'github': 'TBD'
        }

        content_parts = [
            ContentFormatter.format_frontmatter(frontmatter),
            '',
            f'# {feature_name} - Technical Implementation Epic',
            '',
            '## Overview',
            prd_description,
            '',
            '## Architecture Decisions',
            analysis.get('architecture_decisions',
                         '待技术团队确定架构决策和技术选型'),
            '',
            '## Technical Approach',
            analysis.get('technical_approach', '待评估技术栈选择'),
            '',
            '## Implementation Strategy',
            analysis.get('implementation_strategy', '待制定实施计划'),
            '',
            '## Task Breakdown Preview',
            self._format_task_preview(analysis.get('task_preview', [])),
            '',
            '## Dependencies',
            analysis.get('dependencies', '待分析依赖关系'),
            '',
            '## Risk Assessment',
            analysis.get('risk_assessment', '待评估技术风险'),
            '',
            '## Success Criteria',
            analysis.get('success_criteria', '待定义验收标准'),
            '',
            '## Estimated Effort',
            analysis.get('estimated_effort', '待评估工作量'),
        ]

        return '\n'.join(content_parts)

    def get_template(self) -> str:
        """获取Epic模板"""
        return """
---
name: {feature_name}
status: planning
created: {created_time}
progress: 0%
prd: .claude/prds/{feature_name}.md
github: TBD
---

# {feature_name} - Technical Implementation Epic

## Overview
{overview}

## Architecture Decisions
{architecture_decisions}

## Technical Approach
{technical_approach}

## Implementation Strategy
{implementation_strategy}

## Task Breakdown Preview
{task_preview}

## Dependencies
{dependencies}

## Risk Assessment
{risk_assessment}

## Success Criteria
{success_criteria}

## Estimated Effort
{estimated_effort}
"""

    def _format_task_preview(self, tasks: list) -> str:
        """格式化任务预览"""
        if not tasks:
            return "- 待epic-decompose命令生成详细任务"

        formatted = []
        for i, task in enumerate(tasks, 1):
            if isinstance(task, dict):
                name = task.get('name', f'Task {i}')
                category = task.get('category', 'unknown')
                effort = task.get('effort', 'TBD')
                formatted.append(f"{i}. **{name}** ({category}) - {effort}")
            else:
                formatted.append(f"{i}. {task}")

        return '\n'.join(formatted)


class TechnicalAnalysisHandler(BaseInteractionHandler):
    """技术分析处理器"""

    def collect_user_input(self, feature_name: str,
                           prd_info: Dict[str, Any],
                           mode: str = 'interactive') -> Dict[str, Any]:
        """收集技术分析输入"""
        if mode == 'ai':
            return self._collect_ai_analysis(feature_name, prd_info)
        elif mode == 'non-interactive':
            return self._create_default_analysis(feature_name, prd_info)
        else:
            return self._collect_interactive_analysis(feature_name, prd_info)

    def confirm_action(self, message: str) -> bool:
        """确认操作"""
        return InteractionHelper.confirm_action(message)

    def _collect_interactive_analysis(self, feature_name: str,
                                      prd_info: Dict[str, Any]
                                      ) -> Dict[str, Any]:
        """收集交互式技术分析"""
        print(f"\n🔧 开始为功能 '{feature_name}' 进行技术分析")
        print("请提供以下技术实现信息：\n")

        analysis = {}

        # 架构决策
        analysis['architecture_decisions'] = (
            InteractionHelper.get_user_input(
                "架构决策和技术选型", "待技术团队确定"))

        # 技术方法
        analysis['technical_approach'] = (
            InteractionHelper.get_user_input(
                "技术实现方法", "待评估技术栈"))

        # 实施策略
        analysis['implementation_strategy'] = (
            InteractionHelper.get_user_input(
                "实施策略", "待制定实施计划"))

        # 依赖关系
        analysis['dependencies'] = (
            InteractionHelper.get_user_input(
                "技术依赖", "待分析依赖关系"))

        # 风险评估
        analysis['risk_assessment'] = (
            InteractionHelper.get_user_input(
                "技术风险评估", "待评估技术风险"))

        # 成功标准
        analysis['success_criteria'] = (
            InteractionHelper.get_user_input(
                "技术成功标准", "待定义验收标准"))

        return analysis

    def _collect_ai_analysis(self, feature_name: str,
                             prd_info: Dict[str, Any]) -> Dict[str, Any]:
        """使用AI进行技术分析"""
        print(f"\n🤖 使用AI协作模式分析功能 '{feature_name}' 的技术实现")

        if ai_client.is_available():
            print("\n🔄 AI正在进行技术分析...")
            prd_content = prd_info.get('content', '')
            prompt = AIPromptBuilder.build_technical_analysis_prompt(
                feature_name, prd_content)
            ai_content = ai_client.generate_content(prompt)

            if ai_content:
                return self._parse_ai_analysis(ai_content)

        print("⚠️ AI不可用，使用默认分析")
        return self._create_default_analysis(feature_name, prd_info)

    def _create_default_analysis(self, feature_name: str,
                                 prd_info: Dict[str, Any]
                                 ) -> Dict[str, Any]:
        """创建默认技术分析"""
        return {
            'architecture_decisions': (
                '待技术团队确定架构决策和技术选型'),
            'technical_approach': '待评估技术栈选择',
            'implementation_strategy': '待制定详细实施计划',
            'dependencies': (
                '待分析技术依赖和外部系统集成'),
            'risk_assessment': (
                '待评估技术风险和缓解策略'),
            'success_criteria': '待定义技术验收标准',
            'estimated_effort': '待评估开发工作量'
        }

    def _parse_ai_analysis(self, ai_content: str) -> Dict[str, Any]:
        """解析AI技术分析"""
        analysis = {}

        sections = {
            'architecture_decisions': 'Architecture Decisions',
            'technical_approach': 'Technical Approach',
            'implementation_strategy': 'Implementation Strategy',
            'dependencies': 'Dependencies',
            'risk_assessment': 'Risk Assessment',
            'success_criteria': 'Success Criteria'
        }

        for key, section_name in sections.items():
            content = ContentExtractor.extract_ai_section(
                ai_content, section_name)
            if content:
                analysis[key] = content

        return analysis


class PRDParseCommand(BaseWorkflowStep):
    """PRD解析命令"""

    def __init__(self, feature_name: str, mode: str = 'interactive'):
        super().__init__(feature_name, mode)
        self.content_generator = EpicContentGenerator()
        self.analysis_handler = TechnicalAnalysisHandler()

    def validate_preconditions(self) -> bool:
        """验证前置条件"""
        # 验证功能名称
        is_valid, error_msg = self.validator.validate_feature_name(
            self.feature_name)
        if not is_valid:
            print(error_msg)
            return False

        # 检查PRD文件是否存在
        prd_path = Path(PathHelper.get_prd_path(self.feature_name))
        if not self.file_manager.file_exists(prd_path):
            print(f"❌ PRD文件不存在: {prd_path}")
            print(f"请先运行: python -m ccpm_pm.commands.prd_new "
                  f"{self.feature_name}")
            return False

        # 验证PRD Frontmatter
        prd_content = self.file_manager.read_file(prd_path)
        required_fields = ['name', 'description', 'status', 'created']
        is_valid, error_msg = self.validator.validate_frontmatter(
            prd_content, required_fields)
        if not is_valid:
            print(f"❌ PRD Frontmatter验证失败: {error_msg}")
            return False

        # 检查Epic是否已存在
        epic_path = Path(PathHelper.get_epic_path(self.feature_name))
        if self.file_manager.file_exists(epic_path):
            print(f"⚠️ Epic文件已存在: {epic_path}")
            if not self.analysis_handler.confirm_action(
                    "是否覆盖现有Epic?"):
                return False

        # 确保Epic目录存在
        epic_dir = Path(self.feature_name)
        self.file_manager.ensure_directory(epic_dir)

        return True

    def execute(self) -> Dict[str, Any]:
        """执行PRD解析"""
        # 读取PRD文件
        prd_path = Path(PathHelper.get_prd_path(self.feature_name))
        prd_content = self.file_manager.read_file(prd_path)

        # 提取PRD信息
        prd_info = self._extract_prd_info(prd_content)

        # 进行技术分析
        analysis = self.analysis_handler.collect_user_input(
            self.feature_name, prd_info, self.mode)

        # 生成Epic内容
        created_time = self.file_manager.get_current_datetime()
        epic_content = self.content_generator.generate_content(
            self.feature_name, prd_info['description'],
            analysis, created_time)

        # 保存Epic文件
        epic_path = Path(PathHelper.get_epic_path(self.feature_name))
        self.file_manager.write_file(epic_path, epic_content)

        return {
            'epic_file': str(epic_path),
            'prd_info': prd_info,
            'analysis': analysis,
            'created_time': created_time,
            'content': epic_content
        }

    def post_process(self, result: Dict[str, Any]) -> bool:
        """后处理"""
        # 显示创建摘要
        print("\n✅ Epic创建成功!")
        print(f"📄 文件位置: {result['epic_file']}")
        print(f"⏰ 创建时间: {result['created_time']}")

        # 显示下一步建议
        print("\n🚀 下一步操作:")
        cmd = (f"python -m ccpm_pm.commands.epic_decompose "
               f"{self.feature_name}")
        print(f"   {cmd}")
        print(f"   或运行: ccpm pm:epic-decompose {self.feature_name}")

        return True

    def _extract_prd_info(self, prd_content: str) -> Dict[str, Any]:
        """提取PRD信息"""
        frontmatter = ContentExtractor.extract_frontmatter(prd_content)

        return {
            'name': frontmatter.get('name', self.feature_name),
            'description': frontmatter.get('description', ''),
            'status': frontmatter.get('status', 'draft'),
            'created': frontmatter.get('created', ''),
            'content': prd_content
        }
