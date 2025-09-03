#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCPM PM 核心基础类
定义PM工作流程的基础抽象类和接口
"""

import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List


class ValidationError(Exception):
    """验证错误异常"""
    pass


class FileOperationError(Exception):
    """文件操作错误异常"""
    pass


class BaseValidator:
    """基础验证器类"""
    
    @staticmethod
    def validate_feature_name(feature_name: str) -> tuple[bool, str]:
        """验证功能名称格式"""
        if not feature_name:
            return False, "功能名称不能为空"
        
        # 检查格式：只允许小写字母、数字和连字符，必须以字母开头
        if not re.match(r'^[a-z][a-z0-9-]*$', feature_name):
            return False, ("❌ 功能名称必须是kebab-case格式（小写字母、数字、连字符），"
                           "例如：user-auth, payment-v2, notification-system")
        
        return True, ""
    
    @staticmethod
    def validate_frontmatter(content: str,
                             required_fields: List[str]) -> tuple[bool, str]:
        """验证Frontmatter格式"""
        if not content.startswith('---'):
            return False, "文件必须以Frontmatter开头"
        
        try:
            # 提取frontmatter部分
            parts = content.split('---', 2)
            if len(parts) < 3:
                return False, "Frontmatter格式不正确"
            
            frontmatter = parts[1].strip()
            
            # 检查必需字段
            for field in required_fields:
                if f'{field}:' not in frontmatter:
                    return False, f"缺少必需字段: {field}"
            
            return True, ""
        except Exception as e:
            return False, f"Frontmatter解析错误: {str(e)}"


class BaseFileManager:
    """基础文件管理器类"""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
    
    def ensure_directory(self, dir_path: Path) -> bool:
        """确保目录存在"""
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            raise FileOperationError(f"创建目录失败: {str(e)}")
    
    def file_exists(self, file_path: Path) -> bool:
        """检查文件是否存在"""
        return file_path.exists() and file_path.is_file()
    
    def read_file(self, file_path: Path) -> str:
        """读取文件内容"""
        try:
            return file_path.read_text(encoding='utf-8')
        except Exception as e:
            raise FileOperationError(f"读取文件失败: {str(e)}")
    
    def write_file(self, file_path: Path, content: str) -> bool:
        """写入文件内容"""
        try:
            # 确保父目录存在
            self.ensure_directory(file_path.parent)
            file_path.write_text(content, encoding='utf-8')
            return True
        except Exception as e:
            raise FileOperationError(f"写入文件失败: {str(e)}")
    
    @staticmethod
    def get_current_datetime() -> str:
        """获取当前时间字符串"""
        return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')


class BaseWorkflowStep(ABC):
    """工作流程步骤基类"""
    
    def __init__(self, feature_name: str, mode: str = 'interactive'):
        self.feature_name = feature_name
        self.mode = mode  # 'interactive', 'non-interactive', 'ai'
        self.validator = BaseValidator()
        self.file_manager = BaseFileManager()
    
    @abstractmethod
    def validate_preconditions(self) -> bool:
        """验证前置条件"""
        pass
    
    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """执行主要逻辑"""
        pass
    
    @abstractmethod
    def post_process(self, result: Dict[str, Any]) -> bool:
        """后处理"""
        pass
    
    def run(self) -> Dict[str, Any]:
        """运行完整流程"""
        # 验证前置条件
        if not self.validate_preconditions():
            raise ValidationError("前置条件验证失败")
        
        # 执行主要逻辑
        result = self.execute()
        
        # 后处理
        if not self.post_process(result):
            raise Exception("后处理失败")
        
        return result


class BaseContentGenerator(ABC):
    """内容生成器基类"""
    
    @abstractmethod
    def generate_content(self, **kwargs) -> str:
        """生成内容"""
        pass
    
    @abstractmethod
    def get_template(self) -> str:
        """获取模板"""
        pass


class BaseInteractionHandler(ABC):
    """交互处理器基类"""
    
    @abstractmethod
    def collect_user_input(self, **kwargs) -> Dict[str, Any]:
        """收集用户输入"""
        pass
    
    @abstractmethod
    def confirm_action(self, message: str) -> bool:
        """确认操作"""
        pass