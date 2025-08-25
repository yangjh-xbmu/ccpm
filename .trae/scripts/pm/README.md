# CCPM 项目管理脚本

这个目录包含了 CCPM 项目管理系统的 Python 脚本工具。

## 脚本列表

### 1. epic_sync.py
**功能**: 将本地 Epic 和任务同步到 GitHub Issues

**用法**:
```bash
python epic_sync.py <epic_name>
```

**示例**:
```bash
python epic_sync.py simple-flask-app
```

### 2. issue_close.py
**功能**: 手动更新任务状态，标记任务完成并关闭对应的 GitHub Issue

**用法**:
```bash
python issue_close.py <issue_number> [completion_notes]
```

**参数说明**:
- `issue_number`: 要关闭的 GitHub Issue 编号
- `completion_notes`: 可选的完成说明

**示例**:
```bash
# 关闭 Issue #8
python issue_close.py 8

# 关闭 Issue #10 并添加完成说明
python issue_close.py 10 "Flask 应用已成功实现并测试通过"
```

### 3. epic_close.py
**功能**: 关闭已完成的 Epic，更新状态并关闭对应的 GitHub Issue

**用法**:
```bash
python epic_close.py <epic_name> [completion_notes]
```

**参数说明**:
- `epic_name`: 要关闭的 Epic 名称
- `completion_notes`: 可选的完成说明

**示例**:
```bash
# 关闭 Epic
python epic_close.py simple-flask-app

# 关闭 Epic 并添加完成说明
python epic_close.py simple-flask-app "所有功能已实现并测试通过"
```

## 环境配置

在使用这些脚本之前，请确保已正确配置环境：

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
在项目根目录的 `.env` 文件中配置：
```
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=username/repository-name
```

### 3. GitHub Token 权限
确保 GitHub Token 具有以下权限：
- `repo` - 完整的仓库访问权限
- `issues` - 读写 Issues 权限

## 工作流程

### 典型的 CCPM 工作流程：

1. **创建 Epic 和任务**：使用 `/pm:prd-new` 和 `/pm:epic-decompose` 创建项目结构
2. **同步到 GitHub**：使用 `epic_sync.py` 将本地文件同步到 GitHub Issues
3. **执行任务**：开发人员完成具体的开发工作
4. **关闭任务**：使用 `issue_close.py` 标记任务完成
5. **关闭 Epic**：使用 `epic_close.py` 关闭已完成的 Epic

### 完整的自动化流程

CCPM 系统现在支持完全自动化的任务和 Epic 管理：

```bash
# 1. 同步 Epic 到 GitHub
python .trae/scripts/pm/epic_sync.py simple-flask-app

# 2. 关闭完成的任务
python .trae/scripts/pm/issue_close.py 8 "项目结构创建完成"
python .trae/scripts/pm/issue_close.py 10 "Flask 应用逻辑实现完成"
python .trae/scripts/pm/issue_close.py 9 "GitHub 映射文件创建完成"

# 3. 关闭 Epic
python .trae/scripts/pm/epic_close.py simple-flask-app "所有功能已实现并测试通过"
```

## 脚本功能详解

### issue_close.py 执行的操作：

1. **查找本地任务文件**
   - 优先查找新命名方式：`*/{issue_number}.md`
   - 备用查找包含 `github:.*issues/{issue_number}` 的文件

2. **更新本地状态**
   - 设置任务状态为 `closed`
   - 更新 `updated` 时间戳

3. **更新进度文件**（如果存在）
   - 设置完成度为 100%
   - 添加完成时间和状态说明

4. **关闭 GitHub Issue**
   - 添加完成评论
   - 将 Issue 状态设置为 closed

5. **更新 Epic 进度**
   - 统计已完成任务数量
   - 计算并更新 Epic 进度百分比
   - 更新本地 `epic.md` 文件

## 注意事项

1. **运行目录**: 脚本需要在项目根目录下运行
2. **文件结构**: 确保 Epic 和任务文件按照 CCPM 规范组织
3. **网络连接**: 需要稳定的网络连接以访问 GitHub API
4. **权限验证**: 确保 GitHub Token 有效且具有必要权限

## 故障排除

### 常见错误及解决方案：

1. **"未找到本地任务文件"**
   - 检查 Issue 编号是否正确
   - 确认任务文件存在且命名正确

2. **"连接到 GitHub 仓库失败"**
   - 检查网络连接
   - 验证 GitHub Token 和仓库名称
   - 确认 Token 权限设置

3. **"更新本地任务文件失败"**
   - 检查文件权限
   - 确认文件格式正确（frontmatter + markdown）

4. **"关闭 GitHub Issue 失败"**
   - 确认 Issue 存在且未被删除
   - 检查 Token 是否有 Issues 写权限