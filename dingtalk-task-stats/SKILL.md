---
name: dingtalk-task-stats
description: 钉钉 AI 表格任务统计与员工工时分析。通过 mcporter 连接钉钉 AI 表格 MCP 和通讯录 MCP，查询任务数据并将员工 ID 解析为姓名，生成按人员维度的任务数量、工时、状态等统计报告。使用场景：查询员工任务、统计工时、生成团队工作报告、任务看板分析。
---

# 钉钉任务统计与工时分析

通过 mcporter 同时连接两个钉钉 MCP 服务：
- **dingtalk-ai-table**：读取 AI 表格中的任务数据
- **dingtalk-contacts**：将表格中的员工 ID 解析为真实姓名

## 前置要求

### 1. 安装 mcporter

```bash
npm install -g mcporter
mcporter --version
```

### 2. 配置文件

所有 MCP 服务器配置统一存放在项目的 `config/mcporter.json` 中。
当前已配置 `dingtalk-ai-table` 和 `dingtalk-contacts` 两个服务。

如需新增或修改钉钉 MCP 凭证，直接编辑 `config/mcporter.json`：

```json
{
  "mcpServers": {
    "dingtalk-ai-table": {
      "baseUrl": "<AI表格的Streamable_HTTP_URL>"
    },
    "dingtalk-contacts": {
      "baseUrl": "<通讯录的Streamable_HTTP_URL>"
    }
  }
}
```

获取 URL：访问 https://mcp.dingtalk.com 分别搜索"AI 表格"和"通讯录"，点击"获取 MCP 凭证配置"复制 Streamable HTTP URL。

> **注意**：`config/mcporter.json` 包含访问令牌，已加入 `.gitignore`，不要提交到版本控制。

### 3. 验证配置

在项目根目录（`VK-Cowork`）执行：

```bash
mcporter config list
mcporter call dingtalk-ai-table get_root_node_of_my_document --output json
mcporter list dingtalk-contacts
```

`config list` 应显示三个服务器（exa、dingtalk-ai-table、dingtalk-contacts）。

## 表格结构约定

任务表预期包含以下字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 任务名 | text | 任务标题 |
| 负责人 | user | 员工（存储为钉钉 user ID） |
| 开始时间 | date | 任务开始日期 |
| 结束时间 | date | 任务结束/截止日期 |
| 状态 | singleSelect | 如：待处理、进行中、已完成、已取消 |
| 预估工时 | number | 预估小时数 |
| 实际工时 | number | 实际花费小时数 |

> 字段名可能与实际不完全一致，执行前先用 `list_base_field` 确认真实字段名。

## 核心工作流

### 工作流 1：查询任务数据

```bash
# Step 1: 找到目标表格
mcporter call dingtalk-ai-table search_accessible_ai_tables keyword="任务" --output json

# Step 2: 列出数据表，确认表名
mcporter call dingtalk-ai-table list_base_tables dentry-uuid="<dentryUuid>" --output json

# Step 3: 确认字段结构
mcporter call dingtalk-ai-table list_base_field \
  --args '{"dentryUuid":"<UUID>","sheetIdOrName":"<表名>"}' --output json

# Step 4: 拉取全部记录
mcporter call dingtalk-ai-table search_base_record \
  --args '{"dentryUuid":"<UUID>","sheetIdOrName":"<表名>"}' --output json
```

### 工作流 2：解析员工 ID 为姓名

表格中 user 类型字段返回格式为 `{"name":"姓名","id":"userId"}`。

如果返回的只有 ID 没有姓名，使用通讯录 MCP 解析：

```bash
# 查询单个用户
mcporter call dingtalk-contacts get_user_detail userId="<userId>" --output json
```

> 通讯录 MCP 的工具名可能不同。先执行 `mcporter list dingtalk-contacts` 查看实际可用的工具列表，常见工具名包括：
> - `search_user_by_name` / `get_user_by_id` / `get_member`
> - `list_department_members` / `get_department_detail`

**批量解析策略**：收集所有不重复的 userId，逐个查询后建立 `{userId: 姓名}` 映射表，避免重复查询。

### 工作流 3：生成统计报告

拿到任务数据 + 姓名映射后，在本地用代码（Python/JS）聚合统计。

**统计维度**：

1. **按人员的任务数量**
   - 总任务数、已完成数、进行中数、待处理数
   - 完成率 = 已完成 / 总数

2. **按人员的工时统计**
   - 预估工时总计、实际工时总计
   - 工时偏差 = 实际 - 预估（正值为超时）
   - 平均单任务耗时

3. **按时间维度**
   - 本周/本月任务分布
   - 超期任务（结束时间 < 当前日期 且状态非"已完成"）

4. **团队总览**
   - 团队总任务数与完成率
   - 工时利用率
   - 任务状态分布饼图数据

**输出格式示例**：

```markdown
# 团队任务统计报告（2026-03-01）

## 团队总览
- 总任务数：45
- 已完成：32（71.1%）
- 进行中：8
- 超期未完成：3

## 按人员统计

| 姓名 | 总任务 | 已完成 | 进行中 | 完成率 | 预估工时 | 实际工时 | 偏差 |
|------|--------|--------|--------|--------|----------|----------|------|
| 张三 | 12 | 9 | 2 | 75.0% | 48h | 52h | +4h |
| 李四 | 10 | 8 | 1 | 80.0% | 40h | 38h | -2h |
| 王五 | 8 | 5 | 3 | 62.5% | 32h | 35h | +3h |

## 超期任务
| 任务名 | 负责人 | 截止日期 | 状态 |
|--------|--------|----------|------|
| XXX功能开发 | 张三 | 2026-02-25 | 进行中 |
```

## 完整执行步骤

当用户请求统计时，按以下顺序执行：

1. **定位表格** → `search_accessible_ai_tables` 找到目标表格的 `dentryUuid`
2. **确认结构** → `list_base_tables` + `list_base_field` 确认表名和字段名
3. **拉取数据** → `search_base_record` 获取所有任务记录
4. **解析人员** → 提取所有 userId，通过通讯录 MCP 批量解析姓名
5. **聚合统计** → 用代码按维度计算统计数据
6. **输出报告** → 按上方格式生成 Markdown 报告

## 创建任务表

如果用户还没有任务表，可以帮助创建：

```bash
# 获取根节点
mcporter call dingtalk-ai-table get_root_node_of_my_document --output json

# 创建表格
mcporter call dingtalk-ai-table create_base_app filename="项目任务管理" target="<rootDentryUuid>" --output json

# 创建数据表并初始化字段
mcporter call dingtalk-ai-table add_base_table \
  --args '{"dentryUuid":"<UUID>","name":"任务表","fields":[{"name":"任务名","type":"text"},{"name":"负责人","type":"user"},{"name":"开始时间","type":"date"},{"name":"结束时间","type":"date"},{"name":"状态","type":"singleSelect"},{"name":"预估工时","type":"number"},{"name":"实际工时","type":"number"}]}' \
  --output json
```

## 注意事项

1. **分页**：如任务记录超过单次返回上限，需多次调用并合并结果
2. **user 字段格式**：可能返回 `{"name":"张三","id":"xxx"}` 对象，优先使用 name 字段
3. **日期处理**：date 字段可能返回 Unix 时间戳（毫秒），需转换为可读日期
4. **通讯录权限**：确保 MCP 凭证有通讯录读取权限
5. **工具名发现**：两个 MCP 服务器的工具名可能更新，总是先 `mcporter list <server>` 确认
