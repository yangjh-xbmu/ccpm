# AIPM - AI项目管理包

## 概述

AIPM（AI Project Management）是CCPM项目的Python实现，提供了一套完整的项目管理工具和工作流程。该包采用面向对象的设计模式，支持PRD创建、Epic分解、任务管理等核心功能。

## 功能特性

### 🎯 核心功能

- **PRD创建**: 结构化的产品需求文档生成
- **Epic分解**: 将大型功能分解为具体的开发任务
- **任务管理**: 完整的任务跟踪和进度管理
- **AI集成**: 支持AI辅助的内容生成和分析

### 🏗️ 架构特点

- **模块化设计**: 清晰的包结构和职责分离
- **可扩展性**: 基于抽象类的插件化架构
- **类型安全**: 完整的类型注解支持
- **错误处理**: 完善的异常处理机制

## 包结构

```
aipm/
├── __init__.py              # 包初始化
├── core/                    # 核心模块
│   ├── __init__.py
│   └── base.py             # 基础类和接口定义
├── commands/               # 命令实现
│   ├── __init__.py
│   ├── epic_decompose.py   # Epic分解功能
│   ├── prd_new.py         # PRD创建功能
│   └── prd_parse.py       # PRD解析功能
├── ai/                     # AI集成
│   ├── __init__.py
│   └── client.py          # AI客户端
└── utils/                  # 工具函数
    ├── __init__.py
    └── helpers.py         # 辅助工具
```

## 快速开始

### 安装依赖

```bash
# 安装基础依赖
pip install google-generativeai python-dotenv

# 可选：安装开发依赖
pip install pytest black flake8
```

### 基本使用

```python
from aipm.commands.prd_new import PRDContentGenerator
from aipm.commands.epic_decompose import TaskContentGenerator
from aipm.core.base import BaseFileManager

# 创建PRD内容
prd_generator = PRDContentGenerator()
answers = {
    'description': '用户认证系统',
    'executive_summary': '实现安全的用户登录和注册功能',
    # ... 更多字段
}

file_manager = BaseFileManager()
created_time = file_manager.get_current_datetime()
prd_content = prd_generator.generate_content('user-auth', answers, created_time)

# 创建任务分解
task_generator = TaskContentGenerator()
epic_info = {'name': 'user-auth', 'description': '用户认证Epic'}
tasks = [
    {
        'name': '设计数据库模型',
        'category': 'backend',
        'priority': 'high',
        'effort': '2天'
    }
]
task_content = task_generator.generate_content('user-auth', epic_info, tasks, created_time)
```

## 核心模块详解

### 1. 核心基础类 (core/base.py)

#### BaseValidator

验证器基类，提供数据验证功能：

```python
from aipm.core.base import BaseValidator

validator = BaseValidator()
is_valid, message = validator.validate_feature_name('user-auth')
print(f"验证结果: {is_valid}, 消息: {message}")
```

**主要方法：**

- `validate_feature_name(name)`: 验证功能名称格式（kebab-case）
- `validate_frontmatter(content, required_fields)`: 验证Frontmatter格式

#### BaseFileManager

文件管理器基类，处理文件和目录操作：

```python
from aipm.core.base import BaseFileManager
from pathlib import Path

file_manager = BaseFileManager()

# 创建目录
file_manager.ensure_directory(Path('test_dir'))

# 写入文件
file_manager.write_file(Path('test_dir/test.md'), '# 测试内容')

# 读取文件
content = file_manager.read_file(Path('test_dir/test.md'))
```

**主要方法：**

- `ensure_directory(dir_path)`: 确保目录存在
- `file_exists(file_path)`: 检查文件是否存在
- `read_file(file_path)`: 读取文件内容
- `write_file(file_path, content)`: 写入文件内容
- `get_current_datetime()`: 获取当前UTC时间

#### BaseWorkflowStep

工作流程步骤抽象基类：

```python
from aipm.core.base import BaseWorkflowStep

class CustomStep(BaseWorkflowStep):
    def validate_preconditions(self):
        # 实现前置条件验证
        return True
    
    def execute(self):
        # 实现主要逻辑
        return {'status': 'success'}
    
    def post_process(self, result):
        # 实现后处理
        return True

# 使用
step = CustomStep('feature-name')
result = step.run()
```

#### BaseContentGenerator

内容生成器抽象基类：

```python
from aipm.core.base import BaseContentGenerator

class CustomGenerator(BaseContentGenerator):
    def generate_content(self, **kwargs):
        # 实现内容生成逻辑
        return "生成的内容"
    
    def get_template(self):
        # 返回内容模板
        return "模板内容"
```

### 2. PRD创建模块 (commands/prd_new.py)

#### PRDContentGenerator

PRD内容生成器，用于创建结构化的产品需求文档：

```python
from aipm.commands.prd_new import PRDContentGenerator

generator = PRDContentGenerator()

# 准备PRD数据
answers = {
    'description': '功能描述',
    'executive_summary': '执行摘要',
    'problem_statement': '问题陈述',
    'user_stories': ['用户故事1', '用户故事2'],
    'functional_requirements': ['功能需求1', '功能需求2'],
    'non_functional_requirements': ['非功能需求1', '非功能需求2']
}

# 生成PRD内容
content = generator.generate_content('feature-name', answers, '2024-01-01 12:00:00 UTC')
```

**生成的PRD包含以下章节：**

- Frontmatter（元数据）
- Executive Summary（执行摘要）
- Problem Statement（问题陈述）
- User Stories（用户故事）
- Functional Requirements（功能需求）
- Non-Functional Requirements（非功能需求）
- Success Metrics（成功指标）
- Timeline（时间线）

### 3. Epic分解模块 (commands/epic_decompose.py)

#### TaskContentGenerator

任务内容生成器，将Epic分解为具体的开发任务：

```python
from aipm.commands.epic_decompose import TaskContentGenerator

generator = TaskContentGenerator()

# Epic信息
epic_info = {
    'name': 'user-auth',
    'description': 'Epic描述',
    'objectives': ['目标1', '目标2']
}

# 任务列表
tasks = [
    {
        'name': '设计数据库模型',
        'category': 'backend',
        'priority': 'high',
        'effort': '2天',
        'description': '任务描述',
        'acceptance_criteria': '验收标准',
        'dependencies': '依赖关系'
    }
]

# 生成任务分解内容
content = generator.generate_content('user-auth', epic_info, tasks, '2024-01-01 12:00:00 UTC')
```

**生成的任务分解包含：**

- Frontmatter（进度跟踪信息）
- Epic Overview（Epic概述）
- Task List（任务列表）
- Task Details（任务详情）
- Progress Tracking（进度跟踪）

### 4. AI集成模块 (ai/client.py)

#### AIClient

AI客户端，提供统一的AI服务接口：

```python
from aipm.ai.client import AIClient
import os

# 设置API密钥
os.environ['GEMINI_API_KEY'] = 'your-api-key'

# 创建AI客户端
client = AIClient()

# 配置客户端
if client.configure():
    # 生成内容
    response = client.generate_content('请帮我分析这个功能需求')
    print(response)
else:
    print('AI客户端配置失败')
```

**支持的AI模型：**

- Google Gemini 2.5 Pro（默认）
- 可扩展支持其他模型

### 5. 工具函数模块 (utils/helpers.py)

#### ContentExtractor

内容提取器，用于解析和提取文档内容：

```python
from aipm.utils.helpers import ContentExtractor

# 提取Frontmatter
content = """---
name: test
status: draft
---
# 标题
## 章节
内容"""

frontmatter = ContentExtractor.extract_frontmatter(content)
print(frontmatter)  # {'name': 'test', 'status': 'draft'}

# 提取章节内容
section = ContentExtractor.extract_section(content, '章节')
print(section)  # '内容'
```

#### ContentFormatter

内容格式化器，用于格式化输出内容：

```python
from aipm.utils.helpers import ContentFormatter

# 格式化Frontmatter
frontmatter = {'name': 'test', 'status': 'draft'}
formatted = ContentFormatter.format_frontmatter(frontmatter)
print(formatted)
# ---
# name: test
# status: draft
# ---
```

## 异常处理

包定义了专门的异常类型：

```python
from aipm.core.base import ValidationError, FileOperationError

try:
    # 执行操作
    pass
except ValidationError as e:
    print(f"验证错误: {e}")
except FileOperationError as e:
    print(f"文件操作错误: {e}")
```

## 测试

运行包含的测试脚本：

```bash
# 基础功能测试
python test_aipm.py

# 工作流程测试
python test_workflow_aipm.py
```

## 配置

### 环境变量

创建 `.env` 文件配置AI服务：

```bash
# AI服务配置
GEMINI_API_KEY=your_gemini_api_key
```

### 项目结构要求

使用aipm包的项目应遵循以下目录结构：

```
project/
├── prds/           # PRD文档目录
├── epics/          # Epic目录
├── tasks/          # 任务目录
└── .env           # 环境配置
```

## 扩展开发

### 添加新的内容生成器

```python
from aipm.core.base import BaseContentGenerator

class CustomContentGenerator(BaseContentGenerator):
    def generate_content(self, **kwargs):
        # 实现自定义内容生成逻辑
        return "自定义内容"
    
    def get_template(self):
        return "自定义模板"
```

### 添加新的工作流程步骤

```python
from aipm.core.base import BaseWorkflowStep

class CustomWorkflowStep(BaseWorkflowStep):
    def validate_preconditions(self):
        # 验证前置条件
        return True
    
    def execute(self):
        # 执行主要逻辑
        return {'result': 'success'}
    
    def post_process(self, result):
        # 后处理
        return True
```

## 最佳实践

1. **功能命名**: 使用kebab-case格式（如：user-auth, payment-system）
2. **文档结构**: 保持Frontmatter的一致性
3. **错误处理**: 使用包提供的异常类型
4. **类型注解**: 为自定义类添加完整的类型注解
5. **测试**: 为新功能编写相应的测试用例

## 版本历史

- **v1.0.0**: 初始版本，包含PRD创建和Epic分解功能
- 支持AI集成和完整的工作流程

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证

本项目采用MIT许可证，详见LICENSE文件。
