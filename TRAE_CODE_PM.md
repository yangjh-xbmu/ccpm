# Trae Code PM - Python版本的CCPM工具

这是CCPM（Claude Code Project Management）的Python实现版本，专为Trae AI IDE优化。

## 功能特性

### 1. PRD创建工具 (`prd_new.py`)

自动化创建产品需求文档（PRD），实现原 `/pm:prd-new` 命令的功能。

#### 功能特点
- ✅ 输入验证（kebab-case格式检查）
- ✅ 重复文件检查和确认
- ✅ 自动创建目录结构
- ✅ 交互式问答收集需求
- ✅ 非交互模式支持
- ✅ 标准化PRD模板
- ✅ 前置元数据（frontmatter）
- ✅ 时间戳记录

#### 使用方法

**交互模式（推荐）：**
```bash
python prd_new.py <feature-name>
```

**非交互模式（快速创建）：**
```bash
python prd_new.py <feature-name> --non-interactive
```

#### 使用示例

```bash
# 创建用户认证功能的PRD
python prd_new.py user-authentication

# 快速创建支付系统PRD（使用默认模板）
python prd_new.py payment-system --non-interactive

# 创建通知系统PRD
python prd_new.py notification-system
```

#### 输出文件结构

生成的PRD文件保存在 `.claude/prds/<feature-name>.md`，包含以下结构：

```markdown
---
name: feature-name
description: 功能简要描述
status: backlog
created: 2025-08-25T09:31:13Z
---

# PRD: feature-name

## Executive Summary
## Problem Statement
## User Stories
## Requirements
### Functional Requirements
### Non-Functional Requirements
## Success Criteria
## Constraints & Assumptions
## Out of Scope
## Dependencies
## Implementation Notes
```

#### 验证规则

- **功能名称格式**：必须是kebab-case（小写字母、数字、连字符，以字母开头）
- **文件冲突处理**：检测重复文件并要求用户确认
- **目录自动创建**：自动创建 `.claude/prds/` 目录

## 安装和设置

### 前置要求

- Python 3.7+
- 标准库（无需额外依赖）

### 快速开始

1. **克隆或下载脚本**
   ```bash
   # 确保脚本在项目根目录
   ls prd_new.py
   ```

2. **创建第一个PRD**
   ```bash
   python prd_new.py my-first-feature
   ```

3. **查看生成的文件**
   ```bash
   cat .claude/prds/my-first-feature.md
   ```

## 与原CCPM的对比

| 功能 | 原CCPM | Trae Code PM |
|------|--------|-------------|
| PRD创建 | `/pm:prd-new` 命令 | `python prd_new.py` |
| 交互方式 | Claude对话 | 命令行交互 |
| 输入验证 | ✅ | ✅ |
| 文件格式 | ✅ | ✅ |
| 非交互模式 | ❌ | ✅ |
| 批量处理 | ❌ | 🔄 计划中 |

## 开发路线图

### 已完成 ✅
- [x] PRD创建工具
- [x] 输入验证和错误处理
- [x] 非交互模式
- [x] 标准化模板

### 开发中 🔄
- [ ] PRD解析工具 (`prd_parse.py`)
- [ ] Epic创建和管理
- [ ] 任务管理工具
- [ ] GitHub集成

### 计划中 📋
- [ ] 批量PRD处理
- [ ] PRD模板自定义
- [ ] 项目统计和报告
- [ ] 配置文件支持
- [ ] 插件系统

## 错误处理

脚本包含完善的错误处理机制：

- **输入验证错误**：提供清晰的格式要求说明
- **文件系统错误**：权限和路径问题的详细提示
- **用户取消操作**：优雅退出并提供替代建议

## 贡献指南

欢迎贡献代码！请遵循以下规范：

1. **代码风格**：遵循PEP 8
2. **注释语言**：所有注释使用中文
3. **错误处理**：提供用户友好的错误信息
4. **测试**：添加相应的测试用例

## 许可证

与原CCPM项目保持一致的许可证。

---

**注意**：这是CCPM的Python实现版本，专为提高开发效率和自动化程度而设计。建议与原CCPM工具配合使用，以获得最佳的项目管理体验。