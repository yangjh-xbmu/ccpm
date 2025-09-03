#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCPM PM 工具函数
提供通用的工具函数和辅助方法
"""

import re
from typing import Dict, Any, List, Optional


class ContentExtractor:
    """内容提取器"""
    
    @staticmethod
    def extract_frontmatter(content: str) -> Dict[str, str]:
        """提取Frontmatter信息"""
        if not content.startswith('---'):
            return {}
        
        try:
            parts = content.split('---', 2)
            if len(parts) < 3:
                return {}
            
            frontmatter = parts[1].strip()
            result = {}
            
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    result[key.strip()] = value.strip()
            
            return result
        except Exception:
            return {}
    
    @staticmethod
    def extract_section(content: str, section_name: str) -> str:
        """提取指定章节内容"""
        pattern = rf'##\s+{re.escape(section_name)}\s*\n(.*?)(?=\n##|$)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    @staticmethod
    def extract_ai_section(text: str, section_name: str) -> str:
        """从AI生成的文本中提取指定章节"""
        # 匹配 ## Section Name 格式
        pattern = rf'##\s+{re.escape(section_name)}\s*\n(.*?)(?=\n##|$)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # 匹配 **Section Name:** 格式
        pattern = rf'\*\*{re.escape(section_name)}:\*\*\s*\n(.*?)(?=\n\*\*|$)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return ""


class ContentFormatter:
    """内容格式化器"""
    
    @staticmethod
    def format_frontmatter(data: Dict[str, str]) -> str:
        """格式化Frontmatter"""
        lines = ['---']
        for key, value in data.items():
            lines.append(f'{key}: {value}')
        lines.append('---')
        return '\n'.join(lines)
    
    @staticmethod
    def format_task_list(tasks: List[Dict[str, Any]]) -> str:
        """格式化任务列表"""
        if not tasks:
            return "暂无任务"
        
        lines = []
        for i, task in enumerate(tasks, 1):
            name = task.get('name', f'Task {i}')
            category = task.get('category', 'unknown')
            effort = task.get('effort', 'TBD')
            lines.append(f"{i}. **{name}** ({category}) - {effort}")
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_user_answers(answers: Dict[str, Any]) -> str:
        """格式化用户回答"""
        formatted = []
        for key, value in answers.items():
            if isinstance(value, list):
                value = ', '.join(str(v) for v in value)
            formatted.append(f"- **{key}**: {value}")
        return '\n'.join(formatted)


class InteractionHelper:
    """交互辅助器"""
    
    @staticmethod
    def confirm_action(message: str, default: bool = True) -> bool:
        """确认操作"""
        suffix = " [Y/n]" if default else " [y/N]"
        response = input(f"{message}{suffix}: ").strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes', '是', 'true']
    
    @staticmethod
    def get_user_input(prompt: str, default: str = "",
                       required: bool = False) -> str:
        """获取用户输入"""
        while True:
            if default:
                response = input(f"{prompt} [{default}]: ").strip()
                if not response:
                    response = default
            else:
                response = input(f"{prompt}: ").strip()
            
            if response or not required:
                return response
            
            print("❌ 此字段为必填项，请输入内容")
    
    @staticmethod
    def get_multiple_choice(prompt: str, choices: List[str],
                            default: Optional[str] = None) -> str:
        """获取多选输入"""
        print(f"\n{prompt}")
        for i, choice in enumerate(choices, 1):
            marker = " (默认)" if choice == default else ""
            print(f"  {i}. {choice}{marker}")
        
        while True:
            try:
                response = input("请选择 [1-{}]: ".format(len(choices))).strip()
                if not response and default:
                    return default
                
                index = int(response) - 1
                if 0 <= index < len(choices):
                    return choices[index]
                else:
                    print(f"❌ 请输入1到{len(choices)}之间的数字")
            except ValueError:
                print("❌ 请输入有效的数字")


class PathHelper:
    """路径辅助器"""
    
    @staticmethod
    def get_prd_path(feature_name: str) -> str:
        """获取PRD文件路径"""
        return f".claude/prds/{feature_name}.md"
    
    @staticmethod
    def get_epic_path(feature_name: str) -> str:
        """获取Epic文件路径"""
        return f"{feature_name}/epic.md"
    
    @staticmethod
    def get_task_path(feature_name: str, task_id: int) -> str:
        """获取任务文件路径"""
        return f"{feature_name}/{feature_name}-task-{task_id:02d}.md"
    
    @staticmethod
    def get_tasks_dir(feature_name: str) -> str:
        """获取任务目录路径"""
        return feature_name
    
    @staticmethod
    def get_tasks_path(feature_name: str) -> str:
        """获取任务文件路径"""
        return f"{feature_name}/tasks.md"