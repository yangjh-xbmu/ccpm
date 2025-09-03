---
allowed-tools: Bash, Read, Write, LS
---

# PRD 解析

将 PRD (产品需求文档) 转换为技术实现层面的 Epic。

## 用法

```
/pm:prd-parse <feature_name>
```

## 必要规则

**重要提示：** 在执行此命令之前，请阅读并遵守：

- `.claude/rules/datetime.md` - 用于获取真实的当前日期/时间

## 执行前检查清单

在继续之前，请完成这些验证步骤。
不要用检查进度来打扰用户（比如“我正在检查...”）。直接完成检查然后继续。

### 验证步骤

1. **验证是否提供了 `<feature_name>` 参数：**
    - 如果未提供，告知用户：“❌ 未提供 `<feature_name>` 参数。请运行：/pm:prd-parse <feature_name>”
    - 如果未提供 `<feature_name>`，则停止执行。

2. **验证 PRD 是否存在：**
    - 检查 `.claude/prds/$ARGUMENTS.md` 文件是否存在。
    - 如果未找到，告知用户：“❌ 未找到 PRD：$ARGUMENTS。请先使用此命令创建：/pm:prd-new $ARGUMENTS”
    - 如果 PRD 不存在，则停止执行。

3. **验证 PRD 的 frontmatter 元数据：**
    - 验证 PRD 是否包含有效的 frontmatter 元数据，且包含以下字段：`name`, `description`, `status`, `created`。
    - 如果 frontmatter 无效或缺失，告知用户：“❌ PRD frontmatter 无效。请检查文件：.claude/prds/$ARGUMENTS.md”
    - 并展示缺失或无效的具体字段。

4. **检查 Epic 是否已存在：**
    - 检查 `.claude/epics/$ARGUMENTS/epic.md` 文件是否已存在。
    - 如果存在，询问用户：“⚠️ Epic '$ARGUMENTS' 已存在。是否覆盖？(yes/no)”
    - 只有在用户明确回复 'yes' 后才继续。
    - 如果用户回复 'no'，建议：“使用此命令查看已存在的 Epic：/pm:epic-show $ARGUMENTS”

5. **验证目录权限：**
    - 确保 `.claude/epics/` 目录存在或可以被创建。
    - 如果无法创建，告知用户：“❌ 无法创建 Epic 目录。请检查权限。”

## 指令

你是一位技术主管，正在为一个功能（**$ARGUMENTS**）将产品需求文档（PRD）转换为详细的实现 Epic。

### 1. 阅读 PRD

- 从 `.claude/prds/$ARGUMENTS.md` 加载 PRD。
- 分析所有需求和限制。
- 理解用户故事和成功标准。
- 从 frontmatter 中提取 PRD 的描述。

### 2. 技术分析

- 识别需要做出的架构决策。
- 确定技术栈和实现方法。
- 将功能需求映射到技术组件。
- 识别集成点和依赖项。

### 3. 文件格式与 Frontmatter 元数据

在 `.claude/epics/$ARGUMENTS/epic.md` 路径下创建 Epic 文件，并严格遵循以下结构：

```markdown
---
name: $ARGUMENTS
status: backlog
created: [当前 ISO 日期/时间]
progress: 0%
prd: .claude/prds/$ARGUMENTS.md
github: [同步到 GitHub 时会更新]
---

# Epic: $ARGUMENTS

## 概述
关于实现方法的简要技术概述。

## 架构决策
- 关键技术决策及其理由
- 技术选型
- 将要使用的设计模式

## 技术方案
### 前端组件
- 需要的 UI 组件
- 状态管理方法
- 用户交互模式

### 后端服务
- 需要的 API 端点
- 数据模型和模式 (schema)
- 业务逻辑组件

### 基础设施
- 部署注意事项
- 扩展性要求
- 监控与可观测性

## 实现策略
- 开发阶段划分
- 风险规避
- 测试方法

## 任务分解预览
将被创建的高阶任务类别：
- [ ] 类别 1: 描述
- [ ] 类别 2: 描述
- [ ] 等等...

## 依赖项
- 外部服务依赖
- 内部团队依赖
- 前置工作

## 成功标准 (技术层面)
- 性能基准
- 质量门禁
- 验收标准

## 工作量估算
- 总体时间线估算
- 资源需求
- 关键路径上的事项
```

### 4. Frontmatter 指南

- **name**: 使用确切的功能名称 (与 $ARGUMENTS 相同)。
- **status**: 新 Epic 的状态始终以 "backlog" 开始。
- **created**: 通过运行 `date -u +"%Y-%m-%dT%H:%M:%SZ"` 命令获取**真实**的当前日期时间。
- **progress**: 进度始终以 "0%" 开始。
- **prd**: 引用源 PRD 文件的路径。
- **github**: 保留占位符文本 - 将在同步期间更新。

### 5. 输出位置

如果目录结构不存在，则创建它：

- `.claude/epics/$ARGUMENTS/` (目录)
- `.claude/epics/$ARGUMENTS/epic.md` (Epic 文件)

### 6. 质量验证

在保存 Epic 之前，请验证：

- [ ] 所有的 PRD 需求都在技术方案中得到了处理。
- [ ] 任务分解类别覆盖了所有实现领域。
- [ ] 依赖项在技术上是准确的。
- [ ] 工作量估算是现实的。
- [ ] 架构决策是合理的。

### 7. 创建后操作

成功创建 Epic 后：

1. 确认：“✅ Epic 已创建：.claude/epics/$ARGUMENTS/epic.md”
2. 展示摘要信息：
    - 识别出的任务类别数量
    - 关键架构决策
    - 工作量估算
3. 建议下一步操作：“准备好分解任务了吗？请运行：/pm:epic-decompose $ARGUMENTS”

## 错误恢复

如果任何步骤失败：

- 清晰地解释哪里出了问题。
- 如果 PRD 不完整，列出具体缺失的部分。
- 如果技术方案不明确，指出需要澄清的地方。
- 绝不要在信息不完整的情况下创建 Epic。

专注于为 “**$ARGUMENTS**” 创建一个技术上合理、能满足所有 PRD 需求且实际可行的实现计划。

## 重要提示

- 目标是任务数量尽可能少，并将总任务数限制在 10 个或更少。
- 在创建 Epic 时，寻找简化和改进的方法。尽可能利用现有功能，而不是创建更多代码。
