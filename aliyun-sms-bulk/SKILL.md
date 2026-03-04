---
name: aliyun-sms-bulk
description: >
  使用阿里云 MCP 短信服务发送单条或批量群发短信。支持单发、同内容群发（SendSms，最多 1000 个号码/次）、
  个性化批量发送（SendBatchSms，最多 100 个号码/次），以及上传 Excel 文件自动解析号码和变量后批量发送。
  当用户需要"发短信"、"群发短信"、"阿里云短信"、"批量发送通知"、"SMS"、"短信通知"、
  "上传 Excel 发短信"、"导入名单发短信"时触发。
---

# 阿里云短信群发 Skill

> 本技能为**市场部**定制，用于营销通知、活动推送等批量发送场景。

## 三个核心 API 能力对比

| 接口 | 单次号码上限 | 适用场景 |
|------|------------|---------|
| `SendSms` | **1000 个** | 同一签名 + 同一模板变量，群发相同内容 |
| `SendBatchSms` | 100 个 | 不同签名 / 不同模板变量，个性化内容 |
| `SendMessageWithTemplate` | 1 个 | 单条发送（支持国际短信） |

> **市场部群发推荐优先使用 `SendSms`**：单次可发 1000 人，适合统一内容的活动通知。

## MCP 自动配置

**首次使用时，先检查并自动写入 MCP 配置，再调用工具。**

### 检查步骤

1. 读取 `~/.cursor/mcp.json`
2. 检查是否已存在 `mcp_sms` 字段
3. 若不存在，合并写入以下配置并告知用户已自动配置，需**重启 Cursor** 生效：

```json
{
  "mcp_sms": {
    "type": "streamableHttp",
    "description": "阿里云短信服务",
    "isActive": true,
    "name": "mcp_sms",
    "baseUrl": "https://openapi-mcp.cn-hangzhou.aliyuncs.com/accounts/31764980/custom/mcp_sms/id/a2iysyADk2BBO0Hd/mcp"
  }
}
```

4. 若已存在，直接继续发短信流程。

## API 详细说明

### 1. 单发：SendMessageWithTemplate

向单个号码发送短信（支持国际短信）。

**必填参数：**
- `To` — 手机号，含国家代码（如 `+8613800001234`）
- `TemplateCode` — 短信模板 ID（控制台获取）
- `From` — 短信签名（国内必填）

**可选参数：**
- `TemplateParam` — 模板变量，JSON 字符串（如 `{"code":"1234"}`）
- `SmsUpExtendCode` — 上行扩展码

**响应字段：**
- `ResponseCode` = `"OK"` 表示成功
- `MessageId` — 用于后续查询投递状态

---

### 2. 同内容群发：SendSms（推荐用于市场部统一通知）

向多个号码发送**相同签名、相同模板**的短信，单次最多 **1000 个**。

**必填参数：**
- `PhoneNumbers` — 号码字符串，英文逗号分隔（如 `"13800001111,13900002222"`），上限 1000 个
- `SignName` — 短信签名名称（单个，所有号码共用）
- `TemplateCode` — 短信模板 Code

**可选参数：**
- `TemplateParam` — 模板变量，JSON 字符串（如 `{"activity":"双十一"}`），所有号码使用相同变量值

**关键限制：**
- 单次最多 1000 个号码
- 所有号码共用同一签名和同一模板变量值（无法个性化）
- 批量发送相比单条有一定延迟，验证码类短信不建议使用

---

### 3. 个性化批量群发：SendBatchSms

向多个号码批量发送，单次最多 **100 个**。各号码可使用不同签名和模板变量。

**必填参数：**
- `PhoneNumberJson` — 号码数组，JSON 字符串（如 `["13800001111","13900002222"]`）
- `SignNameJson` — 签名数组，与号码数量一致（如 `["我的签名","我的签名"]`）
- `TemplateCode` — 短信模板 Code（所有号码共用同一模板）
- `TemplateParamJson` — 模板变量数组，与号码数量一致（如 `[{"name":"张三"},{"name":"李四"}]`）

**关键限制：**
- 单次最多 100 个号码
- 签名数组长度 = 号码数组长度
- 模板变量数组长度 = 号码数组长度（若模板无变量可不传）

---

## 工作流程

### 发单条短信

1. 确认用户提供：目标号码、签名名称、模板 Code、模板变量（若有）
2. 调用 `SendMessageWithTemplate`
3. 检查响应 `ResponseCode` 是否为 `OK`

### 统一内容群发（≤1000 人，推荐）

适用场景：所有人收到相同内容，如活动通知、公告推送。

1. 收集号码列表，用英文逗号拼接为字符串
2. 调用 `SendSms`，传入 `PhoneNumbers`、`SignName`、`TemplateCode`、`TemplateParam`
3. 检查响应 `Code` 是否为 `OK`，记录 `BizId` 用于后续查询

### 统一内容群发（>1000 人）

1. 将号码列表按 1000 个一组切分
2. 循环调用 `SendSms`，每批间隔约 200ms
3. 汇总所有批次结果，报告总发送数和失败数

### 个性化群发（≤100 人，不同姓名/变量）

适用场景：每条短信含个人姓名等不同内容。

1. 收集号码列表和对应变量
2. 构建等长的 `SignNameJson`、`PhoneNumberJson`、`TemplateParamJson` 数组
3. 调用 `SendBatchSms`
4. 报告成功/失败结果

### 个性化群发（>100 人）

1. 将号码列表按 100 个一组切分
2. 循环调用 `SendBatchSms`，每批间隔约 200ms
3. 汇总所有批次结果，报告总发送数和失败数

### Excel 导入发送

适用场景：市场部将客户名单整理在 Excel 中，直接上传后批量发送。

#### Excel 格式要求

Excel 文件需包含以下列（列名不区分大小写，支持中英文）：

| 列名示例 | 说明 | 是否必填 |
|---------|------|---------|
| `手机号` / `phone` / `mobile` | 接收号码 | 必填 |
| 其他列 | 模板变量，列名即变量名（如 `姓名`、`活动名称`） | 视模板而定 |

**示例表格：**

| 手机号 | 姓名 | 活动名称 |
|--------|------|---------|
| 13800001111 | 张三 | 双十一大促 |
| 13900002222 | 李四 | 双十一大促 |

#### Excel 发送工作流

1. **解析文件**：用 Python `openpyxl` 或 `pandas` 读取 Excel，识别手机号列和变量列
2. **预览确认**：向用户展示解析结果（总行数、号码样例、变量列名），请用户确认签名和模板 Code
3. **判断发送模式**：
   - 若所有变量值相同（或无个性化列）→ 使用 `SendSms`，按 1000 个一批
   - 若有个性化变量列（如姓名各不同）→ 使用 `SendBatchSms`，按 100 个一批
4. **发送并汇总**：循环发送，收集每批结果，最终报告：
   - 总发送数 / 成功数 / 失败数
   - 失败的号码列表（若有）
5. **可选输出**：将发送结果写回 Excel 新增一列 `发送状态`，供市场部存档

#### 解析代码参考

```python
import pandas as pd

df = pd.read_excel("名单.xlsx", dtype=str)

# 自动识别手机号列
phone_col = next(
    (c for c in df.columns if c.lower() in ["手机号", "phone", "mobile", "电话", "手机"]),
    None
)
if not phone_col:
    raise ValueError("未找到手机号列，请确认列名为：手机号 / phone / mobile")

# 其余列作为模板变量
var_cols = [c for c in df.columns if c != phone_col]

phones = df[phone_col].dropna().str.strip().tolist()
rows = df.to_dict(orient="records")
```

---

## 常见注意事项

- 模板和签名需在 [阿里云短信控制台](https://dysms.console.aliyun.com/) 预先审核通过
- `TemplateParam` / `TemplateParamJson` 中的变量名必须与模板中定义的变量名一致
- 国内号码无需加 `+86` 前缀（`SendBatchSms` 直接用 `1xxxxxxxxxx` 格式）
- 遇到错误码 `isv.BUSINESS_LIMIT_CONTROL` 表示触发频控，需降低发送频率
- 详细错误码参考：`references/error-codes.md`
