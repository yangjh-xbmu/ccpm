# AIPM 安装指南

## 概述

AIPM (AI-Powered Project Management) 是一个基于AI的产品管理工具包，支持通过CLI和脚本两种方式使用。

## 安装方式

### 方式一：开发模式安装（推荐）

在项目根目录下执行：

```bash
# 进入aipm包目录
cd aipm

# 开发模式安装
pip install -e .
```

安装完成后，可以直接使用 `aipm` 命令：

```bash
aipm --version
aipm --help
```

### 方式二：直接安装

```bash
# 进入aipm包目录
cd aipm

# 安装包
pip install .
```

### 方式三：从源码运行（无需安装）

```bash
# 在项目根目录下
python -m aipm.cli --help
```

## 依赖安装

### 基础依赖

```bash
# 无额外依赖，使用Python标准库
```

### AI功能依赖（可选）

如果需要使用AI增强功能，请安装：

```bash
pip install google-generativeai
```

并设置环境变量：

```bash
export GEMINI_API_KEY="your-api-key-here"
```

## 验证安装

### 1. 检查版本

```bash
aipm --version
```

预期输出：

```
AIPM - AI-Powered Project Management
版本: 1.0.0
作者: AIPM Team
描述: 基于AI的产品管理工具包
```

### 2. 查看帮助

```bash
aipm --help
```

### 3. 测试基本功能

```bash
# 创建PRD文档
aipm prd create --product-name "测试产品" --author "你的名字" --batch --output test.md

# 分解Epic任务
aipm epic decompose --title "用户认证" --batch --output tasks.md

# 解析PRD文档
aipm prd parse test.md --output result.json
```

## 使用方式

### CLI命令行使用

```bash
# 创建PRD文档
aipm prd create --product-name "我的产品" --author "张三"

# 使用批处理模式（跳过交互输入）
aipm prd create --product-name "我的产品" --author "张三" --batch

# 分解Epic为任务
aipm epic decompose --title "用户管理系统"

# 使用AI自动分解（需要API密钥）
aipm epic decompose --title "用户管理系统" --ai-decompose

# 解析PRD文档
aipm prd parse prds/my-product.md
```

### Python脚本使用

```python
from aipm.commands.prd_new import PRDContentGenerator
from aipm.commands.epic_decompose import TaskContentGenerator
from aipm.commands.prd_parse import PRDParser
from aipm.core.base import BaseFileManager

# 创建PRD
generator = PRDContentGenerator()
prd_info = {
    'product_name': '我的产品',
    'version': '1.0.0',
    'author': '张三'
}
content = generator.generate_content(prd_info)

# 分解Epic
task_generator = TaskContentGenerator()
epic_info = {'title': '用户认证', 'description': '实现用户登录注册功能'}
tasks = [{'title': '设计数据库', 'description': '设计用户表结构'}]
task_content = task_generator.generate_content('用户认证', epic_info, tasks, '2024-01-01')

# 解析PRD
parser = PRDParser()
with open('prd.md', 'r') as f:
    prd_content = f.read()
result = parser.parse_content(prd_content)
```

## 目录结构

安装后的包结构：

```
aipm/
├── __init__.py          # 包初始化
├── cli.py              # CLI入口
├── commands/           # 命令模块
│   ├── prd_new.py     # PRD创建
│   ├── epic_decompose.py # Epic分解
│   └── prd_parse.py   # PRD解析
├── core/              # 核心模块
│   └── base.py        # 基础类
├── ai/                # AI模块
│   └── client.py      # AI客户端
└── utils/             # 工具模块
    └── helpers.py     # 辅助函数
```

## 配置文件

### 环境变量

```bash
# AI功能配置
export GEMINI_API_KEY="your-gemini-api-key"

# 可选：自定义输出目录
export AIPM_OUTPUT_DIR="/path/to/output"
```

### 配置文件（可选）

创建 `~/.aipm/config.json`：

```json
{
  "ai": {
    "provider": "gemini",
    "api_key": "your-api-key"
  },
  "output": {
    "default_dir": "./output",
    "prd_template": "default",
    "task_template": "default"
  }
}
```

## 故障排除

### 常见问题

1. **命令未找到**

   ```bash
   aipm: command not found
   ```

   解决：确保已正确安装包，或使用 `python -m aipm.cli` 运行

2. **导入错误**

   ```
   ModuleNotFoundError: No module named 'aipm'
   ```

   解决：检查Python路径，重新安装包

3. **AI功能不可用**

   ```
   AI功能不可用，请检查API密钥配置
   ```

   解决：安装 `google-generativeai` 并设置 `GEMINI_API_KEY` 环境变量

### 调试模式

```bash
# 启用详细输出
aipm --verbose prd create --product-name "测试"

# 查看调试信息
PYTHONPATH=. python -c "import aipm; print(aipm.__file__)"
```

## 卸载

```bash
pip uninstall aipm
```

## 更新

```bash
# 开发模式下，直接拉取最新代码即可
git pull

# 正式安装需要重新安装
pip uninstall aipm
pip install .
```

## 支持

如有问题，请查看：

- [使用指南](USAGE_GUIDE.md)
- [API参考](API_REFERENCE.md)
- [项目文档](README.md)
