# AIPM API 参考文档

本文档提供了AIPM包中所有公共API的详细说明。

## 目录

- [核心模块 (core)](#核心模块-core)
- [命令模块 (commands)](#命令模块-commands)
- [AI模块 (ai)](#ai模块-ai)
- [工具模块 (utils)](#工具模块-utils)

## 核心模块 (core)

### BaseValidator

基础验证器类，提供数据验证功能。

#### 方法

##### `validate_feature_name(feature_name: str) -> tuple[bool, str]`

验证功能名称格式。

**参数：**
- `feature_name` (str): 要验证的功能名称

**返回值：**
- `tuple[bool, str]`: (是否有效, 错误消息)

**示例：**
```python
from aipm.core.base import BaseValidator

validator = BaseValidator()
is_valid, message = validator.validate_feature_name('user-auth')
print(f"有效: {is_valid}, 消息: {message}")
# 输出: 有效: True, 消息: 

is_valid, message = validator.validate_feature_name('UserAuth')
print(f"有效: {is_valid}, 消息: {message}")
# 输出: 有效: False, 消息: ❌ 功能名称必须是kebab-case格式...
```

##### `validate_frontmatter(content: str, required_fields: List[str]) -> tuple[bool, str]`

验证Frontmatter格式和必需字段。

**参数：**
- `content` (str): 包含Frontmatter的文档内容
- `required_fields` (List[str]): 必需字段列表

**返回值：**
- `tuple[bool, str]`: (是否有效, 错误消息)

**示例：**
```python
content = """---
name: test
status: draft
---
# 内容"""

is_valid, message = validator.validate_frontmatter(content, ['name', 'status'])
print(f"有效: {is_valid}")
# 输出: 有效: True
```

### BaseFileManager

基础文件管理器类，处理文件和目录操作。

#### 构造函数

```python
BaseFileManager(base_dir: str = ".")
```

**参数：**
- `base_dir` (str): 基础目录路径，默认为当前目录

#### 方法

##### `ensure_directory(dir_path: Path) -> bool`

确保目录存在，如果不存在则创建。

**参数：**
- `dir_path` (Path): 目录路径

**返回值：**
- `bool`: 操作是否成功

**异常：**
- `FileOperationError`: 目录创建失败时抛出

##### `file_exists(file_path: Path) -> bool`

检查文件是否存在。

**参数：**
- `file_path` (Path): 文件路径

**返回值：**
- `bool`: 文件是否存在

##### `read_file(file_path: Path) -> str`

读取文件内容。

**参数：**
- `file_path` (Path): 文件路径

**返回值：**
- `str`: 文件内容

**异常：**
- `FileOperationError`: 文件读取失败时抛出

##### `write_file(file_path: Path, content: str) -> bool`

写入文件内容。

**参数：**
- `file_path` (Path): 文件路径
- `content` (str): 要写入的内容

**返回值：**
- `bool`: 操作是否成功

**异常：**
- `FileOperationError`: 文件写入失败时抛出

##### `get_current_datetime() -> str` (静态方法)

获取当前UTC时间字符串。

**返回值：**
- `str`: 格式化的UTC时间字符串 (YYYY-MM-DD HH:MM:SS UTC)

**示例：**
```python
from aipm.core.base import BaseFileManager
from pathlib import Path

file_manager = BaseFileManager()

# 创建目录
file_manager.ensure_directory(Path('test_dir'))

# 写入文件
file_manager.write_file(Path('test_dir/test.md'), '# 测试内容')

# 检查文件存在
if file_manager.file_exists(Path('test_dir/test.md')):
    # 读取文件
    content = file_manager.read_file(Path('test_dir/test.md'))
    print(content)

# 获取当前时间
current_time = file_manager.get_current_datetime()
print(f"当前时间: {current_time}")
```

### BaseWorkflowStep

工作流程步骤抽象基类。

#### 构造函数

```python
BaseWorkflowStep(feature_name: str, mode: str = 'interactive')
```

**参数：**
- `feature_name` (str): 功能名称
- `mode` (str): 执行模式，可选值：'interactive', 'non-interactive', 'ai'

#### 抽象方法

##### `validate_preconditions() -> bool`

验证前置条件。子类必须实现此方法。

**返回值：**
- `bool`: 前置条件是否满足

##### `execute() -> Dict[str, Any]`

执行主要逻辑。子类必须实现此方法。

**返回值：**
- `Dict[str, Any]`: 执行结果

##### `post_process(result: Dict[str, Any]) -> bool`

后处理。子类必须实现此方法。

**参数：**
- `result` (Dict[str, Any]): execute方法的返回结果

**返回值：**
- `bool`: 后处理是否成功

#### 公共方法

##### `run() -> Dict[str, Any]`

运行完整的工作流程。

**返回值：**
- `Dict[str, Any]`: 执行结果

**异常：**
- `ValidationError`: 前置条件验证失败时抛出
- `Exception`: 后处理失败时抛出

**示例：**
```python
from aipm.core.base import BaseWorkflowStep

class CustomStep(BaseWorkflowStep):
    def validate_preconditions(self):
        # 检查前置条件
        return True
    
    def execute(self):
        # 执行主要逻辑
        return {'status': 'success', 'data': 'processed'}
    
    def post_process(self, result):
        # 后处理
        print(f"处理结果: {result}")
        return True

# 使用
step = CustomStep('my-feature')
result = step.run()
```

### BaseContentGenerator

内容生成器抽象基类。

#### 抽象方法

##### `generate_content(**kwargs) -> str`

生成内容。子类必须实现此方法。

**参数：**
- `**kwargs`: 生成内容所需的参数

**返回值：**
- `str`: 生成的内容

##### `get_template() -> str`

获取内容模板。子类必须实现此方法。

**返回值：**
- `str`: 内容模板

### BaseInteractionHandler

交互处理器抽象基类。

#### 抽象方法

##### `collect_user_input(**kwargs) -> Dict[str, Any]`

收集用户输入。子类必须实现此方法。

**参数：**
- `**kwargs`: 收集输入所需的参数

**返回值：**
- `Dict[str, Any]`: 用户输入数据

##### `confirm_action(message: str) -> bool`

确认操作。子类必须实现此方法。

**参数：**
- `message` (str): 确认消息

**返回值：**
- `bool`: 用户是否确认

## 命令模块 (commands)

### PRDContentGenerator

PRD内容生成器，继承自BaseContentGenerator。

#### 方法

##### `generate_content(feature_name: str, answers: Dict[str, Any], created_time: str) -> str`

生成PRD内容。

**参数：**
- `feature_name` (str): 功能名称
- `answers` (Dict[str, Any]): PRD数据字典
- `created_time` (str): 创建时间

**返回值：**
- `str`: 生成的PRD内容

**answers字典结构：**
```python
{
    'description': str,                    # 功能描述
    'executive_summary': str,              # 执行摘要
    'problem_statement': str,              # 问题陈述
    'user_stories': List[str],            # 用户故事列表
    'functional_requirements': List[str],  # 功能需求列表
    'non_functional_requirements': List[str] # 非功能需求列表
}
```

**示例：**
```python
from aipm.commands.prd_new import PRDContentGenerator
from aipm.core.base import BaseFileManager

generator = PRDContentGenerator()
file_manager = BaseFileManager()

answers = {
    'description': '用户认证系统',
    'executive_summary': '实现安全的用户登录和注册功能',
    'problem_statement': '当前系统缺乏用户认证机制',
    'user_stories': [
        '作为用户，我希望能够注册账户',
        '作为用户，我希望能够安全登录'
    ],
    'functional_requirements': [
        '支持邮箱注册',
        '支持密码登录'
    ],
    'non_functional_requirements': [
        '登录响应时间<2秒',
        '支持1000并发用户'
    ]
}

created_time = file_manager.get_current_datetime()
content = generator.generate_content('user-auth', answers, created_time)
print(content)
```

##### `get_template() -> str`

获取PRD模板。

**返回值：**
- `str`: PRD模板字符串

### TaskContentGenerator

任务内容生成器，继承自BaseContentGenerator。

#### 方法

##### `generate_content(feature_name: str, epic_info: Dict[str, Any], tasks: List[Dict[str, Any]], created_time: str) -> str`

生成任务分解内容。

**参数：**
- `feature_name` (str): 功能名称
- `epic_info` (Dict[str, Any]): Epic信息字典
- `tasks` (List[Dict[str, Any]]): 任务列表
- `created_time` (str): 创建时间

**返回值：**
- `str`: 生成的任务分解内容

**epic_info字典结构：**
```python
{
    'name': str,           # Epic名称
    'description': str,    # Epic描述
    'objectives': List[str], # 目标列表（可选）
    'scope': str          # 范围说明（可选）
}
```

**tasks列表中每个任务的结构：**
```python
{
    'name': str,                # 任务名称
    'category': str,            # 任务类别 (backend/frontend/devops等)
    'priority': str,            # 优先级 (high/medium/low)
    'effort': str,              # 工作量估算
    'description': str,         # 任务描述
    'acceptance_criteria': str, # 验收标准
    'dependencies': str         # 依赖关系
}
```

**示例：**
```python
from aipm.commands.epic_decompose import TaskContentGenerator
from aipm.core.base import BaseFileManager

generator = TaskContentGenerator()
file_manager = BaseFileManager()

epic_info = {
    'name': 'user-auth',
    'description': '用户认证系统Epic',
    'objectives': ['实现安全认证', '提升用户体验']
}

tasks = [
    {
        'name': '设计数据库模型',
        'category': 'backend',
        'priority': 'high',
        'effort': '2天',
        'description': '设计用户表和认证相关表结构',
        'acceptance_criteria': '数据库表创建完成并通过测试',
        'dependencies': '无'
    },
    {
        'name': '实现注册API',
        'category': 'backend',
        'priority': 'high',
        'effort': '3天',
        'description': '实现用户注册RESTful API',
        'acceptance_criteria': 'API功能完整并通过单元测试',
        'dependencies': '数据库模型'
    }
]

created_time = file_manager.get_current_datetime()
content = generator.generate_content('user-auth', epic_info, tasks, created_time)
print(content)
```

##### `get_template() -> str`

获取任务分解模板。

**返回值：**
- `str`: 任务分解模板字符串

## AI模块 (ai)

### AIClient

AI客户端类，提供统一的AI服务接口。

#### 构造函数

```python
AIClient(model_name: str = "gemini-2.5-pro", api_key_env: str = "GEMINI_API_KEY")
```

**参数：**
- `model_name` (str): AI模型名称，默认为"gemini-2.5-pro"
- `api_key_env` (str): API密钥环境变量名，默认为"GEMINI_API_KEY"

#### 方法

##### `configure() -> bool`

配置AI模型。

**返回值：**
- `bool`: 配置是否成功

##### `generate_content(prompt: str, **kwargs) -> Optional[str]`

生成内容。

**参数：**
- `prompt` (str): 输入提示
- `**kwargs`: 其他生成参数

**返回值：**
- `Optional[str]`: 生成的内容，失败时返回None

**示例：**
```python
from aipm.ai.client import AIClient
import os

# 设置API密钥
os.environ['GEMINI_API_KEY'] = 'your-api-key'

# 创建并配置客户端
client = AIClient()
if client.configure():
    # 生成内容
    response = client.generate_content(
        "请帮我分析用户认证系统的技术需求"
    )
    if response:
        print(response)
    else:
        print("内容生成失败")
else:
    print("AI客户端配置失败")
```

### AIPromptBuilder

AI提示构建器类，用于构建结构化的AI提示。

#### 静态方法

##### `build_prd_prompt(feature_name: str, basic_info: Dict[str, str]) -> str`

构建PRD生成提示。

**参数：**
- `feature_name` (str): 功能名称
- `basic_info` (Dict[str, str]): 基础信息

**返回值：**
- `str`: 构建的提示字符串

##### `build_task_decomposition_prompt(feature_name: str, epic_content: str) -> str`

构建任务分解提示。

**参数：**
- `feature_name` (str): 功能名称
- `epic_content` (str): Epic内容

**返回值：**
- `str`: 构建的提示字符串

## 工具模块 (utils)

### ContentExtractor

内容提取器类，用于解析和提取文档内容。

#### 静态方法

##### `extract_frontmatter(content: str) -> Dict[str, str]`

从文档中提取Frontmatter信息。

**参数：**
- `content` (str): 文档内容

**返回值：**
- `Dict[str, str]`: Frontmatter字典

**示例：**
```python
from aipm.utils.helpers import ContentExtractor

content = """---
name: test-feature
status: draft
created: 2024-01-01
---

# Test Feature
内容..."""

frontmatter = ContentExtractor.extract_frontmatter(content)
print(frontmatter)
# 输出: {'name': 'test-feature', 'status': 'draft', 'created': '2024-01-01'}
```

##### `extract_section(content: str, section_name: str) -> str`

从文档中提取指定章节的内容。

**参数：**
- `content` (str): 文档内容
- `section_name` (str): 章节名称

**返回值：**
- `str`: 章节内容

**示例：**
```python
content = """# 标题

## Overview
这是概述内容。

## Requirements
这是需求内容。"""

overview = ContentExtractor.extract_section(content, "Overview")
print(overview)
# 输出: 这是概述内容。
```

##### `extract_ai_section(text: str, section_name: str) -> str`

从AI生成的文本中提取指定章节。

**参数：**
- `text` (str): AI生成的文本
- `section_name` (str): 章节名称

**返回值：**
- `str`: 章节内容

### ContentFormatter

内容格式化器类，用于格式化输出内容。

#### 静态方法

##### `format_frontmatter(data: Dict[str, Any]) -> str`

格式化Frontmatter数据。

**参数：**
- `data` (Dict[str, Any]): Frontmatter数据字典

**返回值：**
- `str`: 格式化的Frontmatter字符串

**示例：**
```python
from aipm.utils.helpers import ContentFormatter

data = {
    'name': 'test-feature',
    'status': 'draft',
    'created': '2024-01-01 12:00:00 UTC'
}

formatted = ContentFormatter.format_frontmatter(data)
print(formatted)
# 输出:
# ---
# name: test-feature
# status: draft
# created: 2024-01-01 12:00:00 UTC
# ---
```

##### `format_list(items: List[str], style: str = 'bullet') -> str`

格式化列表项。

**参数：**
- `items` (List[str]): 列表项
- `style` (str): 格式样式，可选值：'bullet', 'numbered'

**返回值：**
- `str`: 格式化的列表字符串

**示例：**
```python
items = ['项目1', '项目2', '项目3']

# 无序列表
bullet_list = ContentFormatter.format_list(items, 'bullet')
print(bullet_list)
# 输出:
# - 项目1
# - 项目2
# - 项目3

# 有序列表
numbered_list = ContentFormatter.format_list(items, 'numbered')
print(numbered_list)
# 输出:
# 1. 项目1
# 2. 项目2
# 3. 项目3
```

### InteractionHelper

交互辅助器类，提供用户交互相关的工具方法。

#### 静态方法

##### `get_user_input(prompt: str, default: str = "") -> str`

获取用户输入。

**参数：**
- `prompt` (str): 提示信息
- `default` (str): 默认值

**返回值：**
- `str`: 用户输入的内容

##### `confirm_yes_no(message: str, default: bool = False) -> bool`

获取用户的是/否确认。

**参数：**
- `message` (str): 确认消息
- `default` (bool): 默认值

**返回值：**
- `bool`: 用户的确认结果

### PathHelper

路径辅助器类，提供路径相关的工具方法。

#### 静态方法

##### `get_project_root() -> Path`

获取项目根目录。

**返回值：**
- `Path`: 项目根目录路径

##### `get_prd_path(feature_name: str) -> Path`

获取PRD文件路径。

**参数：**
- `feature_name` (str): 功能名称

**返回值：**
- `Path`: PRD文件路径

##### `get_epic_path(feature_name: str) -> Path`

获取Epic文件路径。

**参数：**
- `feature_name` (str): 功能名称

**返回值：**
- `Path`: Epic文件路径

##### `get_tasks_path(feature_name: str) -> Path`

获取任务文件路径。

**参数：**
- `feature_name` (str): 功能名称

**返回值：**
- `Path`: 任务文件路径

## 异常类

### ValidationError

验证错误异常，继承自Exception。

**用途：** 当数据验证失败时抛出。

### FileOperationError

文件操作错误异常，继承自Exception。

**用途：** 当文件操作失败时抛出。

## 类型定义

包中使用的主要类型定义：

```python
from typing import Dict, Any, List, Optional, Tuple

# 常用类型别名
FrontmatterDict = Dict[str, str]
AnswersDict = Dict[str, Any]
TaskDict = Dict[str, Any]
EpicInfoDict = Dict[str, Any]
ResultDict = Dict[str, Any]
```

## 使用示例

### 完整的PRD创建流程

```python
from aipm.commands.prd_new import PRDContentGenerator
from aipm.core.base import BaseFileManager
from pathlib import Path

# 初始化
generator = PRDContentGenerator()
file_manager = BaseFileManager()
feature_name = "user-auth"

# 准备数据
answers = {
    'description': '用户认证系统',
    'executive_summary': '实现安全的用户登录和注册功能',
    'problem_statement': '当前系统缺乏用户认证机制',
    'user_stories': [
        '作为用户，我希望能够注册账户',
        '作为用户，我希望能够安全登录'
    ],
    'functional_requirements': [
        '支持邮箱注册',
        '支持密码登录',
        '支持密码重置'
    ],
    'non_functional_requirements': [
        '登录响应时间<2秒',
        '支持1000并发用户',
        '99.9%可用性'
    ]
}

# 生成内容
created_time = file_manager.get_current_datetime()
content = generator.generate_content(feature_name, answers, created_time)

# 保存文件
prd_path = Path(f"prds/{feature_name}.md")
file_manager.write_file(prd_path, content)

print(f"PRD已创建: {prd_path}")
```

### 完整的Epic分解流程

```python
from aipm.commands.epic_decompose import TaskContentGenerator
from aipm.core.base import BaseFileManager
from pathlib import Path

# 初始化
generator = TaskContentGenerator()
file_manager = BaseFileManager()
feature_name = "user-auth"

# Epic信息
epic_info = {
    'name': feature_name,
    'description': '用户认证系统的完整实现',
    'objectives': [
        '实现安全的用户认证机制',
        '提供良好的用户体验',
        '确保系统安全性'
    ]
}

# 任务列表
tasks = [
    {
        'name': '设计数据库模型',
        'category': 'backend',
        'priority': 'high',
        'effort': '2天',
        'description': '设计用户表、角色表和权限表结构',
        'acceptance_criteria': '数据库表创建完成，通过数据完整性测试',
        'dependencies': '无'
    },
    {
        'name': '实现用户注册API',
        'category': 'backend',
        'priority': 'high',
        'effort': '3天',
        'description': '实现用户注册RESTful API，包括邮箱验证',
        'acceptance_criteria': 'API功能完整，通过单元测试和集成测试',
        'dependencies': '数据库模型'
    },
    {
        'name': '实现用户登录API',
        'category': 'backend',
        'priority': 'high',
        'effort': '2天',
        'description': '实现用户登录API，包括JWT令牌生成',
        'acceptance_criteria': '登录功能正常，令牌验证通过',
        'dependencies': '数据库模型'
    },
    {
        'name': '开发前端注册页面',
        'category': 'frontend',
        'priority': 'medium',
        'effort': '3天',
        'description': '开发用户注册界面，包括表单验证',
        'acceptance_criteria': '界面符合设计稿，用户体验良好',
        'dependencies': '用户注册API'
    },
    {
        'name': '开发前端登录页面',
        'category': 'frontend',
        'priority': 'medium',
        'effort': '2天',
        'description': '开发用户登录界面和状态管理',
        'acceptance_criteria': '登录流程顺畅，状态管理正确',
        'dependencies': '用户登录API'
    }
]

# 生成内容
created_time = file_manager.get_current_datetime()
content = generator.generate_content(feature_name, epic_info, tasks, created_time)

# 保存文件
tasks_path = Path(f"{feature_name}/tasks.md")
file_manager.write_file(tasks_path, content)

print(f"任务分解已创建: {tasks_path}")
print(f"总任务数: {len(tasks)}")
```

这个API参考文档提供了AIPM包中所有公共接口的详细说明，包括参数、返回值、异常和使用示例。开发者可以根据这个文档快速了解和使用包中的各种功能。