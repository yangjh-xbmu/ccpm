# AIPM AI增强版使用指南

## 概述

AIPM AI增强版默认启用AI功能，为您提供更智能的产品管理体验。

## 快速配置

### 1. 设置API密钥

```bash
# 方式一：设置环境变量
export GOOGLE_API_KEY="your_api_key_here"

# 方式二：创建配置文件
python aipm_config.py
# 然后编辑 ~/.aipm_config.py 文件
```

### 2. 验证配置

```bash
# 运行任何命令都会显示AI状态
python aipm_cli.py --version
```

## 默认AI增强功能

### PRD创建（默认启用AI增强）

```bash
# 基本用法 - 自动启用AI增强
python aipm_cli.py prd create --product-name "智能音箱" --author "产品经理"

# 如果不想使用AI增强，需要明确指定
python aipm_cli.py prd create --product-name "智能音箱" --author "产品经理" --no-ai-enhance
```

**AI增强效果：**
- 自动生成详细的产品描述
- 智能推荐功能需求
- 生成用户故事和验收标准
- 提供技术架构建议

### Epic分解（默认启用AI分解）

```bash
# 基本用法 - 自动启用AI分解
python aipm_cli.py epic decompose --title "用户认证系统"

# 如果不想使用AI分解，需要明确指定
python aipm_cli.py epic decompose --title "用户认证系统" --no-ai-decompose
```

**AI分解效果：**
- 智能分析Epic复杂度
- 自动生成合理的任务分解
- 估算开发工时
- 设置任务优先级
- 生成详细的验收标准

## 命令示例

### 创建智能PRD

```bash
# AI会根据产品名称自动生成丰富的内容
python aipm_cli.py prd create \
  --product-name "在线教育平台" \
  --author "张三" \
  --output education_platform_prd.md
```

### 智能Epic分解

```bash
# AI会智能分解为具体可执行的任务
python aipm_cli.py epic decompose \
  --title "视频播放功能" \
  --output video_player_tasks.md
```

### 批量处理（结合AI）

```bash
# 批处理模式 + AI增强
python aipm_cli.py prd create \
  --product-name "电商APP" \
  --author "李四" \
  --batch \
  --output ecommerce_prd.md
```

## 配置选项

### 全局配置文件 (~/.aipm_config.py)

```python
# 用户自定义配置
USER_CONFIG = {
    # AI功能默认启用
    'ai_enhance_default': True,
    'ai_decompose_default': True,
    
    # 默认作者
    'default_author': '你的名字',
    
    # 默认输出目录
    'default_output_dir': 'ai_output',
    
    # API配置
    'google_api_key': 'your_api_key_here',
}
```

### 环境变量

```bash
# API密钥
export GOOGLE_API_KEY="your_api_key_here"

# 默认作者
export AIPM_DEFAULT_AUTHOR="你的名字"
```

## AI功能对比

| 功能 | 普通模式 | AI增强模式 |
|------|----------|------------|
| PRD创建 | 基础模板 | 智能内容生成 |
| Epic分解 | 默认任务模板 | 智能任务分解 |
| 内容质量 | 需要手动完善 | 自动生成详细内容 |
| 工时估算 | 固定值 | 智能评估 |
| 验收标准 | 模板化 | 具体可测试 |

## 故障排除

### AI功能不可用

1. **检查API密钥**
   ```bash
   echo $GOOGLE_API_KEY
   ```

2. **测试API连接**
   ```bash
   python -c "from aipm.ai.client import AIClient; print(AIClient().test_connection())"
   ```

3. **查看详细错误**
   ```bash
   python aipm_cli.py prd create --product-name "测试" --author "测试" -v
   ```

### 禁用AI功能

如果您暂时不想使用AI功能：

```bash
# PRD创建不使用AI
python aipm_cli.py prd create --product-name "产品" --author "作者" --no-ai-enhance

# Epic分解不使用AI
python aipm_cli.py epic decompose --title "功能" --no-ai-decompose
```

## 最佳实践

### 1. 提供详细的产品信息

```bash
# 好的做法：提供详细信息让AI更好地理解
python aipm_cli.py prd create \
  --product-name "面向企业的项目管理SaaS平台" \
  --author "产品经理" \
  --product-version "2.0.0"
```

### 2. 使用描述性的Epic标题

```bash
# 好的做法：具体描述功能
python aipm_cli.py epic decompose \
  --title "支持多人实时协作的在线文档编辑器"
```

### 3. 结合批处理和AI

```bash
# 快速生成高质量文档
python aipm_cli.py prd create \
  --product-name "智能客服机器人" \
  --batch \
  --output smart_bot_prd.md
```

## 高级用法

### 工作流自动化

```bash
#!/bin/bash
# 自动化产品管理工作流

# 1. 创建PRD
python aipm_cli.py prd create \
  --product-name "$1" \
  --author "$USER" \
  --output "${1}_prd.md"

# 2. 分解主要Epic
for epic in "用户管理" "核心功能" "数据分析" "系统集成"; do
  python aipm_cli.py epic decompose \
    --title "$epic" \
    --output "${1}_${epic}_tasks.md"
done

# 3. 解析PRD
python aipm_cli.py prd parse "${1}_prd.md" \
  --output "${1}_analysis.json"
```

### 配置管理

```bash
# 为不同项目设置不同配置
export AIPM_PROJECT="mobile_app"
export AIPM_DEFAULT_AUTHOR="移动端团队"

python aipm_cli.py prd create --product-name "移动应用" --author "$AIPM_DEFAULT_AUTHOR"
```

## 支持与反馈

如果您在使用AI增强功能时遇到问题：

1. 检查API配额和限制
2. 确认网络连接正常
3. 查看错误日志
4. 联系技术支持

---

**提示**: AI增强功能需要网络连接和有效的API密钥。首次使用建议先测试基本功能。