# AIPM 使用指南

本指南将帮助您快速上手AIPM包，了解如何在项目中使用各种功能。

## 目录

- [快速开始](#快速开始)
- [环境配置](#环境配置)
- [基础用法](#基础用法)
- [高级用法](#高级用法)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)
- [示例项目](#示例项目)

## 快速开始

### 1. 项目结构准备

首先，确保您的项目具有以下目录结构：

```
your-project/
├── prds/           # PRD文档目录
├── epics/          # Epic文档目录
├── features/       # 功能开发目录
│   └── feature-name/
│       ├── tasks.md
│       ├── backend/
│       ├── frontend/
│       └── docs/
└── aipm/          # AIPM包
```

### 2. 基本导入

```python
# 导入核心模块
from aipm.core.base import (
    BaseValidator,
    BaseFileManager,
    BaseWorkflowStep,
    BaseContentGenerator,
    BaseInteractionHandler
)

# 导入命令模块
from aipm.commands.prd_new import PRDContentGenerator
from aipm.commands.epic_decompose import (
    TaskContentGenerator,
    TaskDecompositionHandler
)

# 导入AI模块
from aipm.ai.client import AIClient, AIPromptBuilder

# 导入工具模块
from aipm.utils.helpers import (
    ContentExtractor,
    ContentFormatter,
    InteractionHelper,
    PathHelper
)
```

### 3. 第一个示例

创建一个简单的PRD文档：

```python
from aipm.commands.prd_new import PRDContentGenerator
from aipm.core.base import BaseFileManager
from pathlib import Path

# 初始化组件
generator = PRDContentGenerator()
file_manager = BaseFileManager()

# 定义功能信息
feature_name = "user-profile"
answers = {
    'description': '用户个人资料管理功能',
    'executive_summary': '允许用户查看和编辑个人资料信息',
    'problem_statement': '用户需要能够管理自己的个人信息',
    'user_stories': [
        '作为用户，我希望能够查看我的个人资料',
        '作为用户，我希望能够编辑我的个人信息',
        '作为用户，我希望能够上传头像'
    ],
    'functional_requirements': [
        '显示用户基本信息',
        '支持信息编辑',
        '支持头像上传',
        '数据验证'
    ],
    'non_functional_requirements': [
        '页面加载时间<3秒',
        '支持移动端响应式设计',
        '数据加密存储'
    ]
}

# 生成并保存PRD
created_time = file_manager.get_current_datetime()
content = generator.generate_content(feature_name, answers, created_time)

prd_path = Path(f"prds/{feature_name}.md")
file_manager.ensure_directory(prd_path.parent)
file_manager.write_file(prd_path, content)

print(f"✅ PRD已创建: {prd_path}")
```

## 环境配置

### 环境变量设置

如果您计划使用AI功能，需要设置相应的API密钥：

```bash
# 设置Gemini API密钥
export GEMINI_API_KEY="your-gemini-api-key"

# 或者在Python代码中设置
import os
os.environ['GEMINI_API_KEY'] = 'your-gemini-api-key'
```

### 项目配置文件

创建一个配置文件 `aipm_config.py`：

```python
# aipm_config.py
from pathlib import Path

class AIPMConfig:
    # 项目路径配置
    PROJECT_ROOT = Path(".")
    PRDS_DIR = PROJECT_ROOT / "prds"
    EPICS_DIR = PROJECT_ROOT / "epics"
    FEATURES_DIR = PROJECT_ROOT / "features"
    
    # AI配置
    AI_MODEL = "gemini-2.5-pro"
    AI_API_KEY_ENV = "GEMINI_API_KEY"
    
    # 文件模板配置
    PRD_TEMPLATE_PATH = None  # 使用默认模板
    TASK_TEMPLATE_PATH = None  # 使用默认模板
    
    # 验证规则
    REQUIRED_PRD_FIELDS = ['name', 'status', 'created', 'description']
    REQUIRED_TASK_FIELDS = ['name', 'status', 'created', 'epic']
    
    @classmethod
    def ensure_directories(cls):
        """确保所有必需的目录存在"""
        from aipm.core.base import BaseFileManager
        file_manager = BaseFileManager()
        
        for dir_path in [cls.PRDS_DIR, cls.EPICS_DIR, cls.FEATURES_DIR]:
            file_manager.ensure_directory(dir_path)
```

## 基础用法

### 1. 数据验证

```python
from aipm.core.base import BaseValidator

validator = BaseValidator()

# 验证功能名称
feature_names = ['user-auth', 'UserAuth', 'user_auth', 'user-auth-system']
for name in feature_names:
    is_valid, message = validator.validate_feature_name(name)
    print(f"{name}: {'✅' if is_valid else '❌'} {message}")

# 验证Frontmatter
content = """---
name: user-auth
status: draft
created: 2024-01-01 12:00:00 UTC
---

# User Authentication
内容..."""

is_valid, message = validator.validate_frontmatter(
    content, 
    ['name', 'status', 'created']
)
print(f"Frontmatter验证: {'✅' if is_valid else '❌'} {message}")
```

### 2. 文件操作

```python
from aipm.core.base import BaseFileManager
from pathlib import Path

file_manager = BaseFileManager()

# 创建目录结构
dirs_to_create = [
    Path("prds"),
    Path("epics"),
    Path("features/user-auth/backend"),
    Path("features/user-auth/frontend"),
    Path("features/user-auth/docs")
]

for dir_path in dirs_to_create:
    if file_manager.ensure_directory(dir_path):
        print(f"✅ 目录已创建: {dir_path}")
    else:
        print(f"❌ 目录创建失败: {dir_path}")

# 文件操作示例
test_file = Path("test.md")
test_content = "# 测试文档\n\n这是一个测试文档。"

# 写入文件
if file_manager.write_file(test_file, test_content):
    print(f"✅ 文件已写入: {test_file}")

# 检查文件存在
if file_manager.file_exists(test_file):
    # 读取文件
    content = file_manager.read_file(test_file)
    print(f"📄 文件内容: {content[:50]}...")

# 获取当前时间
current_time = file_manager.get_current_datetime()
print(f"🕒 当前时间: {current_time}")
```

### 3. 内容生成

#### PRD生成

```python
from aipm.commands.prd_new import PRDContentGenerator
from aipm.core.base import BaseFileManager

def create_prd_example():
    generator = PRDContentGenerator()
    file_manager = BaseFileManager()
    
    # 功能信息
    feature_name = "shopping-cart"
    answers = {
        'description': '购物车功能模块',
        'executive_summary': '实现用户购物车的添加、删除、修改和结算功能',
        'problem_statement': '用户需要一个方便的购物车来管理要购买的商品',
        'user_stories': [
            '作为用户，我希望能够将商品添加到购物车',
            '作为用户，我希望能够修改购物车中商品的数量',
            '作为用户，我希望能够从购物车中删除商品',
            '作为用户，我希望能够查看购物车总价',
            '作为用户，我希望能够进行结算'
        ],
        'functional_requirements': [
            '添加商品到购物车',
            '修改商品数量',
            '删除购物车商品',
            '计算总价',
            '购物车持久化',
            '结算流程'
        ],
        'non_functional_requirements': [
            '购物车操作响应时间<1秒',
            '支持离线购物车',
            '购物车数据同步',
            '支持大量商品（1000+）'
        ]
    }
    
    # 生成内容
    created_time = file_manager.get_current_datetime()
    content = generator.generate_content(feature_name, answers, created_time)
    
    # 保存文件
    prd_path = Path(f"prds/{feature_name}.md")
    file_manager.ensure_directory(prd_path.parent)
    file_manager.write_file(prd_path, content)
    
    print(f"✅ PRD已创建: {prd_path}")
    return prd_path

# 执行示例
prd_path = create_prd_example()
```

#### 任务分解

```python
from aipm.commands.epic_decompose import TaskContentGenerator
from aipm.core.base import BaseFileManager

def create_task_decomposition_example():
    generator = TaskContentGenerator()
    file_manager = BaseFileManager()
    
    feature_name = "shopping-cart"
    
    # Epic信息
    epic_info = {
        'name': feature_name,
        'description': '购物车功能的完整实现',
        'objectives': [
            '提供完整的购物车功能',
            '确保良好的用户体验',
            '保证数据一致性和安全性'
        ],
        'scope': '包括前端界面、后端API、数据存储和业务逻辑'
    }
    
    # 任务列表
    tasks = [
        {
            'name': '设计购物车数据模型',
            'category': 'backend',
            'priority': 'high',
            'effort': '1天',
            'description': '设计购物车表结构，包括用户关联、商品信息、数量等',
            'acceptance_criteria': '数据模型设计完成，通过评审',
            'dependencies': '无'
        },
        {
            'name': '实现购物车API',
            'category': 'backend',
            'priority': 'high',
            'effort': '3天',
            'description': '实现购物车的CRUD操作API，包括添加、删除、修改、查询',
            'acceptance_criteria': 'API功能完整，通过单元测试',
            'dependencies': '数据模型'
        },
        {
            'name': '开发购物车前端组件',
            'category': 'frontend',
            'priority': 'high',
            'effort': '4天',
            'description': '开发购物车界面组件，包括商品列表、数量控制、总价计算',
            'acceptance_criteria': '界面功能完整，用户体验良好',
            'dependencies': '购物车API'
        },
        {
            'name': '实现购物车状态管理',
            'category': 'frontend',
            'priority': 'medium',
            'effort': '2天',
            'description': '实现购物车的全局状态管理，包括数据同步和持久化',
            'acceptance_criteria': '状态管理正确，数据同步正常',
            'dependencies': '前端组件'
        },
        {
            'name': '集成测试',
            'category': 'testing',
            'priority': 'medium',
            'effort': '2天',
            'description': '进行购物车功能的端到端测试',
            'acceptance_criteria': '所有测试用例通过',
            'dependencies': '前后端开发完成'
        }
    ]
    
    # 生成内容
    created_time = file_manager.get_current_datetime()
    content = generator.generate_content(feature_name, epic_info, tasks, created_time)
    
    # 保存文件
    tasks_path = Path(f"features/{feature_name}/tasks.md")
    file_manager.ensure_directory(tasks_path.parent)
    file_manager.write_file(tasks_path, content)
    
    print(f"✅ 任务分解已创建: {tasks_path}")
    print(f"📊 总任务数: {len(tasks)}")
    
    # 统计任务信息
    categories = {}
    priorities = {}
    
    for task in tasks:
        cat = task['category']
        pri = task['priority']
        categories[cat] = categories.get(cat, 0) + 1
        priorities[pri] = priorities.get(pri, 0) + 1
    
    print("📈 任务统计:")
    print(f"   按类别: {dict(categories)}")
    print(f"   按优先级: {dict(priorities)}")
    
    return tasks_path

# 执行示例
tasks_path = create_task_decomposition_example()
```

### 4. 内容提取和解析

```python
from aipm.utils.helpers import ContentExtractor, ContentFormatter
from aipm.core.base import BaseFileManager

def content_extraction_example():
    file_manager = BaseFileManager()
    
    # 假设我们有一个PRD文件
    prd_content = """---
name: user-auth
status: draft
created: 2024-01-01 12:00:00 UTC
description: 用户认证系统
---

# User Authentication System

## Executive Summary
这是一个用户认证系统的PRD文档。

## Problem Statement
当前系统缺乏用户认证机制。

## User Stories
- 作为用户，我希望能够注册账户
- 作为用户，我希望能够安全登录

## Functional Requirements
1. 支持邮箱注册
2. 支持密码登录
3. 支持密码重置
"""
    
    # 提取Frontmatter
    frontmatter = ContentExtractor.extract_frontmatter(prd_content)
    print("📋 Frontmatter信息:")
    for key, value in frontmatter.items():
        print(f"   {key}: {value}")
    
    # 提取特定章节
    sections = ['Executive Summary', 'Problem Statement', 'User Stories']
    for section in sections:
        content = ContentExtractor.extract_section(prd_content, section)
        if content:
            print(f"\n📄 {section}:")
            print(f"   {content.strip()}")
    
    # 格式化内容
    user_stories = [
        '作为用户，我希望能够注册账户',
        '作为用户，我希望能够安全登录',
        '作为用户，我希望能够重置密码'
    ]
    
    formatted_list = ContentFormatter.format_list(user_stories, 'bullet')
    print(f"\n📝 格式化的用户故事:")
    print(formatted_list)
    
    # 格式化Frontmatter
    new_frontmatter = {
        'name': 'payment-system',
        'status': 'in-progress',
        'created': file_manager.get_current_datetime(),
        'description': '支付系统模块'
    }
    
    formatted_fm = ContentFormatter.format_frontmatter(new_frontmatter)
    print(f"\n📋 格式化的Frontmatter:")
    print(formatted_fm)

# 执行示例
content_extraction_example()
```

## 高级用法

### 1. 自定义工作流步骤

```python
from aipm.core.base import BaseWorkflowStep
from aipm.core.base import BaseFileManager, ValidationError
from typing import Dict, Any
from pathlib import Path

class CustomPRDValidationStep(BaseWorkflowStep):
    """自定义PRD验证步骤"""
    
    def __init__(self, feature_name: str, prd_path: Path):
        super().__init__(feature_name)
        self.prd_path = prd_path
        self.file_manager = BaseFileManager()
    
    def validate_preconditions(self) -> bool:
        """验证PRD文件是否存在"""
        if not self.file_manager.file_exists(self.prd_path):
            raise ValidationError(f"PRD文件不存在: {self.prd_path}")
        return True
    
    def execute(self) -> Dict[str, Any]:
        """执行PRD验证"""
        content = self.file_manager.read_file(self.prd_path)
        
        # 验证必需章节
        required_sections = [
            'Executive Summary',
            'Problem Statement', 
            'User Stories',
            'Functional Requirements'
        ]
        
        missing_sections = []
        for section in required_sections:
            if f"## {section}" not in content:
                missing_sections.append(section)
        
        # 验证用户故事数量
        user_stories_count = content.count('作为用户') + content.count('As a user')
        
        return {
            'prd_path': str(self.prd_path),
            'missing_sections': missing_sections,
            'user_stories_count': user_stories_count,
            'validation_passed': len(missing_sections) == 0 and user_stories_count >= 3
        }
    
    def post_process(self, result: Dict[str, Any]) -> bool:
        """后处理验证结果"""
        if result['validation_passed']:
            print(f"✅ PRD验证通过: {result['prd_path']}")
            print(f"   用户故事数量: {result['user_stories_count']}")
        else:
            print(f"❌ PRD验证失败: {result['prd_path']}")
            if result['missing_sections']:
                print(f"   缺失章节: {', '.join(result['missing_sections'])}")
            if result['user_stories_count'] < 3:
                print(f"   用户故事不足: {result['user_stories_count']} < 3")
        
        return result['validation_passed']

# 使用自定义工作流步骤
def run_custom_validation():
    feature_name = "user-auth"
    prd_path = Path(f"prds/{feature_name}.md")
    
    validation_step = CustomPRDValidationStep(feature_name, prd_path)
    
    try:
        result = validation_step.run()
        print(f"🎯 验证结果: {result}")
    except ValidationError as e:
        print(f"❌ 验证错误: {e}")
    except Exception as e:
        print(f"❌ 执行错误: {e}")

# 执行示例
# run_custom_validation()
```

### 2. AI集成示例

```python
from aipm.ai.client import AIClient, AIPromptBuilder
from aipm.commands.prd_new import PRDContentGenerator
from aipm.core.base import BaseFileManager
import os

def ai_assisted_prd_creation():
    """AI辅助PRD创建示例"""
    
    # 检查API密钥
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  请设置GEMINI_API_KEY环境变量")
        return
    
    # 初始化AI客户端
    ai_client = AIClient()
    if not ai_client.configure():
        print("❌ AI客户端配置失败")
        return
    
    # 基础功能信息
    feature_name = "notification-system"
    basic_info = {
        'name': feature_name,
        'description': '系统通知功能模块'
    }
    
    # 构建AI提示
    prompt = AIPromptBuilder.build_prd_prompt(feature_name, basic_info)
    print(f"🤖 AI提示: {prompt[:200]}...")
    
    # 生成AI内容
    print("🔄 正在生成AI内容...")
    ai_response = ai_client.generate_content(prompt)
    
    if ai_response:
        print(f"✅ AI生成成功，内容长度: {len(ai_response)}")
        
        # 解析AI响应（这里需要根据实际AI响应格式进行解析）
        # 简化示例，实际使用中需要更复杂的解析逻辑
        answers = {
            'description': '系统通知功能模块',
            'executive_summary': 'AI生成的执行摘要',
            'problem_statement': 'AI生成的问题陈述',
            'user_stories': [
                '作为用户，我希望能够接收系统通知',
                '作为用户，我希望能够管理通知设置'
            ],
            'functional_requirements': [
                '实时通知推送',
                '通知历史记录',
                '通知设置管理'
            ],
            'non_functional_requirements': [
                '通知延迟<1秒',
                '支持10万并发用户',
                '99.9%可用性'
            ]
        }
        
        # 生成最终PRD
        generator = PRDContentGenerator()
        file_manager = BaseFileManager()
        
        created_time = file_manager.get_current_datetime()
        prd_content = generator.generate_content(feature_name, answers, created_time)
        
        # 保存文件
        prd_path = Path(f"prds/{feature_name}.md")
        file_manager.ensure_directory(prd_path.parent)
        file_manager.write_file(prd_path, prd_content)
        
        print(f"✅ AI辅助PRD已创建: {prd_path}")
    else:
        print("❌ AI内容生成失败")

# 执行示例（需要API密钥）
# ai_assisted_prd_creation()
```

### 3. 批量处理示例

```python
from aipm.core.base import BaseFileManager, BaseValidator
from aipm.utils.helpers import ContentExtractor
from pathlib import Path
import json

def batch_process_prds():
    """批量处理PRD文件示例"""
    
    file_manager = BaseFileManager()
    validator = BaseValidator()
    
    prds_dir = Path("prds")
    if not prds_dir.exists():
        print(f"❌ PRD目录不存在: {prds_dir}")
        return
    
    # 收集所有PRD文件
    prd_files = list(prds_dir.glob("*.md"))
    print(f"📁 找到 {len(prd_files)} 个PRD文件")
    
    results = []
    
    for prd_file in prd_files:
        print(f"\n🔍 处理文件: {prd_file.name}")
        
        try:
            # 读取文件内容
            content = file_manager.read_file(prd_file)
            
            # 提取Frontmatter
            frontmatter = ContentExtractor.extract_frontmatter(content)
            
            # 验证Frontmatter
            is_valid, message = validator.validate_frontmatter(
                content, 
                ['name', 'status', 'created']
            )
            
            # 统计信息
            word_count = len(content.split())
            section_count = content.count('##')
            user_stories_count = content.count('作为用户') + content.count('As a user')
            
            result = {
                'file': prd_file.name,
                'frontmatter': frontmatter,
                'validation': {
                    'is_valid': is_valid,
                    'message': message
                },
                'statistics': {
                    'word_count': word_count,
                    'section_count': section_count,
                    'user_stories_count': user_stories_count
                }
            }
            
            results.append(result)
            
            # 输出结果
            status = "✅" if is_valid else "❌"
            print(f"   {status} 验证: {message or '通过'}")
            print(f"   📊 统计: {word_count}词, {section_count}章节, {user_stories_count}用户故事")
            
        except Exception as e:
            print(f"   ❌ 处理错误: {e}")
            results.append({
                'file': prd_file.name,
                'error': str(e)
            })
    
    # 生成报告
    report_path = Path("prd_analysis_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 分析报告已生成: {report_path}")
    
    # 汇总统计
    valid_count = sum(1 for r in results if r.get('validation', {}).get('is_valid', False))
    total_words = sum(r.get('statistics', {}).get('word_count', 0) for r in results)
    total_stories = sum(r.get('statistics', {}).get('user_stories_count', 0) for r in results)
    
    print(f"\n📈 汇总统计:")
    print(f"   有效PRD: {valid_count}/{len(results)}")
    print(f"   总字数: {total_words}")
    print(f"   总用户故事: {total_stories}")

# 执行示例
# batch_process_prds()
```

## 最佳实践

### 1. 错误处理

```python
from aipm.core.base import ValidationError, FileOperationError
from aipm.core.base import BaseFileManager
from pathlib import Path

def robust_file_operations():
    """健壮的文件操作示例"""
    
    file_manager = BaseFileManager()
    
    try:
        # 尝试读取可能不存在的文件
        file_path = Path("non-existent-file.md")
        
        if file_manager.file_exists(file_path):
            content = file_manager.read_file(file_path)
            print(f"✅ 文件读取成功: {len(content)}字符")
        else:
            print(f"⚠️  文件不存在: {file_path}")
            
            # 创建默认内容
            default_content = "# 默认文档\n\n这是一个默认创建的文档。"
            
            # 确保目录存在
            file_manager.ensure_directory(file_path.parent)
            
            # 写入文件
            if file_manager.write_file(file_path, default_content):
                print(f"✅ 默认文件已创建: {file_path}")
            else:
                print(f"❌ 文件创建失败: {file_path}")
                
    except FileOperationError as e:
        print(f"❌ 文件操作错误: {e}")
    except ValidationError as e:
        print(f"❌ 验证错误: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")

# 执行示例
robust_file_operations()
```

### 2. 配置管理

```python
from pathlib import Path
import json
from typing import Dict, Any

class ProjectConfig:
    """项目配置管理"""
    
    def __init__(self, config_path: Path = Path("aipm_config.json")):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "project": {
                "name": "My Project",
                "version": "1.0.0",
                "description": "项目描述"
            },
            "directories": {
                "prds": "prds",
                "epics": "epics",
                "features": "features",
                "docs": "docs"
            },
            "ai": {
                "model": "gemini-2.5-pro",
                "api_key_env": "GEMINI_API_KEY",
                "enabled": False
            },
            "validation": {
                "required_prd_fields": ["name", "status", "created", "description"],
                "required_task_fields": ["name", "status", "created", "epic"],
                "min_user_stories": 3
            },
            "templates": {
                "prd_template": None,
                "task_template": None
            }
        }
    
    def save_config(self):
        """保存配置到文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get(self, key: str, default=None):
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value):
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value

# 使用配置管理
def config_management_example():
    config = ProjectConfig()
    
    # 获取配置
    project_name = config.get('project.name', 'Unknown Project')
    prds_dir = config.get('directories.prds', 'prds')
    ai_enabled = config.get('ai.enabled', False)
    
    print(f"📋 项目名称: {project_name}")
    print(f"📁 PRD目录: {prds_dir}")
    print(f"🤖 AI功能: {'启用' if ai_enabled else '禁用'}")
    
    # 修改配置
    config.set('ai.enabled', True)
    config.set('project.description', '这是一个使用AIPM的项目')
    
    # 保存配置
    config.save_config()
    print(f"✅ 配置已保存到: {config.config_path}")

# 执行示例
config_management_example()
```

### 3. 日志记录

```python
import logging
from pathlib import Path
from datetime import datetime

def setup_logging():
    """设置日志记录"""
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 配置文件日志
    log_file = log_dir / f"aipm_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('aipm')

def logging_example():
    """日志记录示例"""
    
    logger = setup_logging()
    
    logger.info("🚀 AIPM应用启动")
    
    try:
        # 模拟一些操作
        logger.info("📋 开始创建PRD")
        
        # 模拟成功操作
        feature_name = "test-feature"
        logger.info(f"✅ PRD创建成功: {feature_name}")
        
        # 模拟警告
        logger.warning("⚠️  检测到重复的功能名称")
        
        # 模拟错误
        try:
            raise ValueError("测试错误")
        except ValueError as e:
            logger.error(f"❌ 操作失败: {e}")
    
    except Exception as e:
        logger.critical(f"💥 严重错误: {e}")
    
    finally:
        logger.info("🏁 AIPM应用结束")

# 执行示例
logging_example()
```

## 故障排除

### 常见问题

#### 1. 模块导入错误

```python
# 错误示例
try:
    from aipm.core.base import BaseValidator
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("💡 解决方案:")
    print("   1. 确保aipm包在Python路径中")
    print("   2. 检查包结构是否完整")
    print("   3. 确保__init__.py文件存在")
```

#### 2. 文件权限问题

```python
from aipm.core.base import BaseFileManager, FileOperationError
from pathlib import Path

def handle_permission_issues():
    file_manager = BaseFileManager()
    
    try:
        # 尝试写入可能没有权限的位置
        restricted_path = Path("/root/test.md")
        file_manager.write_file(restricted_path, "测试内容")
    
    except FileOperationError as e:
        print(f"❌ 文件操作失败: {e}")
        print("💡 解决方案:")
        print("   1. 检查文件/目录权限")
        print("   2. 使用有权限的目录")
        print("   3. 以适当的用户身份运行")
        
        # 使用替代路径
        alternative_path = Path("./test.md")
        if file_manager.write_file(alternative_path, "测试内容"):
            print(f"✅ 使用替代路径成功: {alternative_path}")
```

#### 3. AI API配置问题

```python
from aipm.ai.client import AIClient
import os

def diagnose_ai_issues():
    print("🔍 AI配置诊断:")
    
    # 检查环境变量
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY环境变量未设置")
        print("💡 解决方案:")
        print("   export GEMINI_API_KEY='your-api-key'")
        return
    
    print(f"✅ API密钥已设置 (长度: {len(api_key)})")
    
    # 测试AI客户端
    client = AIClient()
    if client.configure():
        print("✅ AI客户端配置成功")
        
        # 测试简单请求
        try:
            response = client.generate_content("Hello, AI!")
            if response:
                print(f"✅ AI响应测试成功 (长度: {len(response)})")
            else:
                print("❌ AI响应为空")
        except Exception as e:
            print(f"❌ AI请求失败: {e}")
    else:
        print("❌ AI客户端配置失败")

# 执行诊断
# diagnose_ai_issues()
```

## 示例项目

### 完整的电商项目示例

```python
from aipm.commands.prd_new import PRDContentGenerator
from aipm.commands.epic_decompose import TaskContentGenerator
from aipm.core.base import BaseFileManager
from pathlib import Path

def create_ecommerce_project():
    """创建完整的电商项目示例"""
    
    file_manager = BaseFileManager()
    prd_generator = PRDContentGenerator()
    task_generator = TaskContentGenerator()
    
    # 电商功能列表
    features = {
        'user-management': {
            'description': '用户管理系统',
            'user_stories': [
                '作为用户，我希望能够注册账户',
                '作为用户，我希望能够登录系统',
                '作为用户，我希望能够管理个人资料',
                '作为管理员，我希望能够管理用户账户'
            ],
            'tasks': [
                {'name': '用户注册API', 'category': 'backend', 'priority': 'high', 'effort': '3天'},
                {'name': '用户登录API', 'category': 'backend', 'priority': 'high', 'effort': '2天'},
                {'name': '用户管理界面', 'category': 'frontend', 'priority': 'medium', 'effort': '4天'}
            ]
        },
        'product-catalog': {
            'description': '商品目录系统',
            'user_stories': [
                '作为用户，我希望能够浏览商品',
                '作为用户，我希望能够搜索商品',
                '作为用户，我希望能够查看商品详情',
                '作为管理员，我希望能够管理商品信息'
            ],
            'tasks': [
                {'name': '商品数据模型', 'category': 'backend', 'priority': 'high', 'effort': '2天'},
                {'name': '商品API', 'category': 'backend', 'priority': 'high', 'effort': '4天'},
                {'name': '商品列表页面', 'category': 'frontend', 'priority': 'high', 'effort': '3天'},
                {'name': '商品详情页面', 'category': 'frontend', 'priority': 'medium', 'effort': '3天'}
            ]
        },
        'shopping-cart': {
            'description': '购物车系统',
            'user_stories': [
                '作为用户，我希望能够添加商品到购物车',
                '作为用户，我希望能够修改购物车商品数量',
                '作为用户，我希望能够删除购物车商品',
                '作为用户，我希望能够查看购物车总价'
            ],
            'tasks': [
                {'name': '购物车数据模型', 'category': 'backend', 'priority': 'high', 'effort': '1天'},
                {'name': '购物车API', 'category': 'backend', 'priority': 'high', 'effort': '3天'},
                {'name': '购物车组件', 'category': 'frontend', 'priority': 'high', 'effort': '4天'}
            ]
        },
        'order-management': {
            'description': '订单管理系统',
            'user_stories': [
                '作为用户，我希望能够创建订单',
                '作为用户，我希望能够查看订单状态',
                '作为用户，我希望能够取消订单',
                '作为管理员，我希望能够处理订单'
            ],
            'tasks': [
                {'name': '订单数据模型', 'category': 'backend', 'priority': 'high', 'effort': '2天'},
                {'name': '订单API', 'category': 'backend', 'priority': 'high', 'effort': '5天'},
                {'name': '订单管理界面', 'category': 'frontend', 'priority': 'medium', 'effort': '4天'}
            ]
        },
        'payment-system': {
            'description': '支付系统',
            'user_stories': [
                '作为用户，我希望能够选择支付方式',
                '作为用户，我希望能够安全地完成支付',
                '作为用户，我希望能够查看支付记录',
                '作为系统，我希望能够处理支付回调'
            ],
            'tasks': [
                {'name': '支付接口集成', 'category': 'backend', 'priority': 'high', 'effort': '4天'},
                {'name': '支付安全验证', 'category': 'backend', 'priority': 'high', 'effort': '3天'},
                {'name': '支付界面', 'category': 'frontend', 'priority': 'high', 'effort': '3天'}
            ]
        }
    }
    
    print("🚀 开始创建电商项目文档...")
    
    created_time = file_manager.get_current_datetime()
    
    for feature_name, feature_info in features.items():
        print(f"\n📋 创建功能: {feature_name}")
        
        # 创建PRD
        prd_answers = {
            'description': feature_info['description'],
            'executive_summary': f"{feature_info['description']}的完整实现",
            'problem_statement': f"系统需要{feature_info['description']}来支持业务需求",
            'user_stories': feature_info['user_stories'],
            'functional_requirements': [f"实现{story.split('，')[1]}" for story in feature_info['user_stories']],
            'non_functional_requirements': [
                '响应时间<2秒',
                '支持高并发',
                '数据安全性'
            ]
        }
        
        prd_content = prd_generator.generate_content(feature_name, prd_answers, created_time)
        prd_path = Path(f"prds/{feature_name}.md")
        file_manager.ensure_directory(prd_path.parent)
        file_manager.write_file(prd_path, prd_content)
        print(f"   ✅ PRD已创建: {prd_path}")
        
        # 创建任务分解
        epic_info = {
            'name': feature_name,
            'description': feature_info['description'],
            'objectives': [f"实现{feature_info['description']}的核心功能"]
        }
        
        # 扩展任务信息
        detailed_tasks = []
        for task in feature_info['tasks']:
            detailed_task = {
                'name': task['name'],
                'category': task['category'],
                'priority': task['priority'],
                'effort': task['effort'],
                'description': f"实现{task['name']}的完整功能",
                'acceptance_criteria': f"{task['name']}功能完整并通过测试",
                'dependencies': '前置任务完成'
            }
            detailed_tasks.append(detailed_task)
        
        task_content = task_generator.generate_content(feature_name, epic_info, detailed_tasks, created_time)
        task_path = Path(f"features/{feature_name}/tasks.md")
        file_manager.ensure_directory(task_path.parent)
        file_manager.write_file(task_path, task_content)
        print(f"   ✅ 任务分解已创建: {task_path}")
        print(f"   📊 任务数量: {len(detailed_tasks)}")
    
    # 创建项目总览
    project_overview = f"""# 电商项目总览

创建时间: {created_time}

## 项目功能模块

{chr(10).join([f"- **{name}**: {info['description']}" for name, info in features.items()])}

## 统计信息

- 功能模块数: {len(features)}
- 总任务数: {sum(len(info['tasks']) for info in features.values())}
- 总用户故事数: {sum(len(info['user_stories']) for info in features.values())}

## 项目结构

```txt

ecommerce-project/
├── prds/                 # PRD文档
{chr(10).join([f"│   ├── {name}.md" for name in features.keys()])}
├── features/             # 功能开发
{chr(10).join([f"│   ├── {name}/" for name in features.keys()])}
{chr(10).join([f"│   │   └── tasks.md" for _ in features.keys()])}
└── docs/                 # 项目文档
    └── project-overview.md

```

## 开发建议

1. **开发顺序**: 建议按照用户管理 → 商品目录 → 购物车 → 订单管理 → 支付系统的顺序进行开发
2. **技术栈**: 建议使用现代化的技术栈，如React/Vue + Node.js/Python + MySQL/PostgreSQL
3. **测试策略**: 每个模块都应该包含单元测试、集成测试和端到端测试
4. **部署方案**: 建议使用容器化部署，支持CI/CD流程

## 里程碑

- **阶段1**: 用户管理和商品目录 (预计4周)
- **阶段2**: 购物车和订单管理 (预计3周)
- **阶段3**: 支付系统和优化 (预计3周)
- **阶段4**: 测试和部署 (预计2周)

总预计开发时间: 12周
"""

    overview_path = Path("docs/project-overview.md")
    file_manager.ensure_directory(overview_path.parent)
    file_manager.write_file(overview_path, project_overview)
    
    print(f"\n🎉 电商项目文档创建完成!")
    print(f"📋 总功能数: {len(features)}")
    print(f"📄 总文档数: {len(features) * 2 + 1}")
    print(f"📊 项目总览: {overview_path}")

# 执行完整项目创建

# create_ecommerce_project()

```

这个使用指南提供了从基础用法到高级功能的完整示例，帮助用户快速掌握AIPM包的使用方法。通过这些示例，用户可以了解如何在实际项目中应用AIPM的各种功能。
