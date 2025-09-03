#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCPM PM AI客户端
提供统一的AI协作接口
"""

import os
import sys
from typing import Optional, Dict, Any

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


class AIClient:
    """AI客户端类"""
    
    def __init__(self, model_name: str = "gemini-2.5-pro",
                 api_key_env: str = "GEMINI_API_KEY"):
        self.model_name = model_name
        self.api_key_env = api_key_env
        self.model = None
        self._configured = False
    
    def configure(self) -> bool:
        """配置AI模型"""
        if self._configured:
            return True
        
        api_key = os.getenv(self.api_key_env)
        if not api_key:
            print(f"❌ 请设置环境变量 {self.api_key_env}")
            print(f"   export {self.api_key_env}=your_api_key")
            return False
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self._configured = True
            return True
        except Exception as e:
            print(f"❌ AI配置失败: {str(e)}")
            return False
    
    def generate_content(self, prompt: str,
                         max_retries: int = 3) -> Optional[str]:
        """生成内容"""
        if not self._configured and not self.configure():
            return None
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                if response.text:
                    return response.text.strip()
                else:
                    print(f"⚠️ AI响应为空，尝试 {attempt + 1}/{max_retries}")
            except Exception as e:
                msg = f"⚠️ AI生成失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}"
                print(msg)
                if attempt == max_retries - 1:
                    print("❌ AI生成最终失败，请检查网络连接和API配置")
        
        return None
    
    def is_available(self) -> bool:
        """检查AI是否可用"""
        return self._configured or self.configure()


class AIPromptBuilder:
    """AI提示词构建器"""
    
    @staticmethod
    def build_prd_analysis_prompt(feature_name: str,
                                  user_answers: Dict[str, Any]) -> str:
        """构建PRD分析提示词"""
        return f"""
你是一个资深的产品经理和技术架构师。请基于以下信息，为功能 "{feature_name}" 生成详细的PRD内容。

用户提供的信息：
{AIPromptBuilder._format_user_answers(user_answers)}

请生成以下部分的内容：

## Executive Summary
[提供功能的执行摘要，包括目标、价值和关键指标]

## Problem Statement
[详细描述要解决的问题和用户痛点]

## User Stories
[提供3-5个详细的用户故事，使用标准格式：作为...我希望...以便...]

## Requirements
### Functional Requirements
[列出功能性需求]

### Non-Functional Requirements
[列出非功能性需求，如性能、安全性、可用性等]

### Technical Constraints
[列出技术约束和限制]

请确保内容详细、专业，并且符合产品管理最佳实践。
"""
    
    @staticmethod
    def build_technical_analysis_prompt(feature_name: str,
                                        prd_content: str) -> str:
        """构建技术分析提示词"""
        return f"""
你是一个资深的技术架构师和开发团队负责人。请基于以下PRD内容，为功能 "{feature_name}" 生成详细的技术实现分析。

PRD内容：
{prd_content}

请生成以下技术分析内容：

## Architecture Decisions
[关键的架构决策和技术选型]

## Technical Approach
[技术实现方法和策略]

## Implementation Strategy
[实施策略和开发计划]

## Dependencies
[技术依赖和外部系统集成]

## Risk Assessment
[技术风险评估和缓解策略]

## Success Criteria
[技术成功标准和验收条件]

请确保分析深入、实用，并考虑可维护性、可扩展性和性能等因素。
"""
    
    @staticmethod
    def build_task_decomposition_prompt(feature_name: str,
                                        epic_content: str) -> str:
        """构建任务分解提示词"""
        return f"""
你是一个资深的项目经理和开发团队负责人。请基于以下Epic内容，为功能 "{feature_name}" 生成详细的任务分解。

Epic内容：
{epic_content}

请将Epic分解为5-8个具体的开发任务，每个任务应该：
1. 可以在1-3天内完成
2. 有明确的验收标准
3. 包含具体的技术实现细节
4. 考虑任务间的依赖关系

请按以下格式输出任务列表：

## Task 1: [任务名称]
**Description:** [任务描述]
**Category:** [frontend/backend/database/testing/deployment]
**Acceptance Criteria:**
- [验收标准1]
- [验收标准2]
**Technical Details:** [技术实现细节]
**Dependencies:** [依赖的其他任务]
**Estimated Effort:** [预估工作量，如2天]

[重复上述格式为每个任务]

请确保任务分解合理、可执行，并且覆盖完整的开发流程。
"""
    
    @staticmethod
    def _format_user_answers(answers: Dict[str, Any]) -> str:
        """格式化用户回答"""
        formatted = []
        for key, value in answers.items():
            if isinstance(value, list):
                value = ', '.join(value)
            formatted.append(f"- {key}: {value}")
        return '\n'.join(formatted)


# 全局AI客户端实例
ai_client = AIClient()