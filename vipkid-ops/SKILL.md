---
name: vipkid-ops
description: VIPKID 国际化管理端运营助理。可查询、新建、修改商品包，配置优惠券使用限制、库存和赠送权限。⛔ 不执行上架/下架/删除操作。
---

# VIPKID 运营后台 Skill

## 快速开始（新用户必读）

**第一次使用前，必须完成以下初始化，否则所有操作都会失败。**

### 第 1 步：获取你的 token

1. 用 Chrome 打开 `https://sa-manager.lionabc.com/` 并登录
2. 按 `F12` → 切到 **Application** 标签 → 左侧 **Cookies → https://sa-manager.lionabc.com**
3. 找到 `intlAuthToken`，复制其 **Value**（一串类似 `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` 的 UUID）

### 第 2 步：确认你的地区码

`vk-cr-code` 是你所在地区的标识，常见值：

| 地区 | cr-code |
|------|---------|
| 沙特 | `sa` |
| 阿联酋 | `ae` |
| 科威特 | `kw` |

如果不确定，打开 DevTools → Network，随便点一个页面操作，查看请求 Headers 中的 `vk-cr-code` 值。

### 第 3 步：创建配置文件

```bash
mkdir -p ~/.vipkid-ops
cat > ~/.vipkid-ops/config.json << 'EOF'
{
  "base_url": "https://sa-manager.lionabc.com",
  "token": "在此粘贴你的 intlAuthToken",
  "cr_code": "sa"
}
EOF
```

将 `token` 替换为第 1 步复制的值，将 `cr_code` 替换为第 2 步确认的地区码。

### 第 4 步：安装辅助脚本

```bash
mkdir -p ~/.claude/skills/vipkid-ops
# ops_helper.py 应与本 SKILL.md 在同一目录，若不存在，从安装来源重新复制
ls ~/.claude/skills/vipkid-ops/ops_helper.py && echo "已存在" || echo "缺失，请检查安装"
```

### 第 5 步：验证连通性

```bash
python3 ~/.claude/skills/vipkid-ops/ops_helper.py auth
```

输出 `认证有效` 则配置完成。

---

## 使用方式

调用此 Skill 时，Claude 通过 bash 发起 HTTP 请求操作 `sa-manager.lionabc.com` 运营后台。
配置文件位于 `~/.vipkid-ops/config.json`，包含认证 token 和地区码。

---

## 1. 认证

### 读取配置

```bash
CONFIG=$(cat ~/.vipkid-ops/config.json)
TOKEN=$(echo $CONFIG | python3 -c "import json,sys; print(json.load(sys.stdin)['token'])")
BASE_URL=$(echo $CONFIG | python3 -c "import json,sys; print(json.load(sys.stdin)['base_url'])")
CR_CODE=$(echo $CONFIG | python3 -c "import json,sys; print(json.load(sys.stdin).get('cr_code', 'sa'))")
```

### 统一请求 Headers

所有请求必须携带以下 headers：

```bash
-H "intlAuthToken: $TOKEN"
-H "Cookie: intlAuthToken=$TOKEN"
-H "vk-cr-code: $CR_CODE"
-H "vk-language-code: zh-cn"
-H "app-code: international-mgt"
-H "Referer: https://sa-manager.lionabc.com/hobbit/product/productpackagemanage/"
-H "Content-Type: application/json"
-H "Accept: application/json"
```

### 验证 Token 是否有效

```bash
curl -s \
  -H "intlAuthToken: $TOKEN" -H "Cookie: intlAuthToken=$TOKEN" \
  -H "vk-cr-code: $CR_CODE" -H "app-code: international-mgt" \
  "$BASE_URL/rest/auth/api/auth/userAuthInfo" | python3 -m json.tool
```

返回 `code: 200` 且 `data.roleList` 非空则有效。

若返回 401 或 `data` 为空，说明 token 已过期，按以下步骤更新：

**Token 更新步骤（Chrome）：**

1. 用 Chrome 打开 `https://sa-manager.lionabc.com/` 并确保已登录
2. 按 `F12` 打开 DevTools，切换到 **Application** 标签页
3. 左侧展开 **Cookies → https://sa-manager.lionabc.com**
4. 在列表中找到名为 `intlAuthToken` 的条目，复制其 **Value** 列的值
5. 更新配置文件：

```bash
# 将 <新token> 替换为上一步复制的值
python3 -c "
import json
from pathlib import Path
cfg = Path.home() / '.vipkid-ops/config.json'
data = json.loads(cfg.read_text())
data['token'] = '<新token>'
cfg.write_text(json.dumps(data, indent=2, ensure_ascii=False))
print('Token 已更新')
"
```

或直接编辑 `~/.vipkid-ops/config.json`，将 `token` 字段值替换即可。

---

## 2. 枚举值参考（源自 ProductEnum.java）

在调用新建/修改接口时，以下字段必须传整数值，不接受字符串。

### `productTypeId`（商品类型）

| 值 | 含义 |
|----|------|
| 1 | 商品包（Product_Package） |
| 2 | 子商品（Session） |
| 3 | 标准商业课包（列表查询默认类型） |
| 4 | 订阅包（Renewal_Package） |
| 5 | 订阅子包 |
| 9 | 补差订阅包 |
| 10 | 试学包（Trail_Package） |
| 16 | 课程有效期包（Class_Validity） |
| 18 | 最小课消包 |
| 20 | 休学权益包 |

> 新建普通商品包时，`productTypeId` 填 **3**。

### `saleType`（售卖类型）

| 值 | 含义 |
|----|------|
| 1 | 课时数量（INVENTORY_NUM） |
| 2 | 课堂有效期（CLASS_VALIDITY_PERIOD） |
| 3 | 考试报名（EXAM_REGISTRATION） |
| 4 | 实物商品（REAL_OBJECTS） |
| 5 | 休学权益（LEAVE_EQUITY） |

### `visibility` / `adminVisibility` / `leadsVisibility`（可见性）

| 值 | 含义 |
|----|------|
| 0 | 不可见 |
| 1 | 可见 |
| 2 | 部分用户可见（仅 `visibility` 支持） |
| 3 | 标签可见（需配合 `visibilityTagRelList` 等） |

### `giftable`（赠送）

| 值 | 含义 |
|----|------|
| 0 | 不可作为礼物（默认，普通商业产品） |
| 1 | 可作为礼物（赠品，无签单归属） |

> ⚠️ 注意：源码 `ProductEnum.Giftable` 中描述字符串与枚举常量名相反，以业务逻辑为准：`giftable=1` 时系统自动将 `signatureType` 设为 `0（无归属）`，说明 `1` 表示赠品。

### `discountType`（折扣类型）

| 值 | 含义 |
|----|------|
| 0 | 无折扣 |
| 1 | 正常折扣 |
| 2 | 允许折上折 |

### `status`（发布状态，只读，不可写入）

| 值 | 含义 |
|----|------|
| 0 | 未发布（下架） |
| 1 | 已发布（上架） |
| 2 | 已过期 |
| 3 | 已删除 |

### `signatureType`（签单类型）

| 值 | 含义 |
|----|------|
| 0 | 无归属 |
| 1 | 新签 / 补差 / 续费 |

---

## 3. API Reference

### 便捷函数（在 bash 脚本中定义）

```bash
api_get() {
  local path="$1"
  curl -s \
    -H "intlAuthToken: $TOKEN" -H "Cookie: intlAuthToken=$TOKEN" \
    -H "vk-cr-code: $CR_CODE" -H "vk-language-code: zh-cn" \
    -H "app-code: international-mgt" \
    -H "Referer: https://sa-manager.lionabc.com/hobbit/product/productpackagemanage/" \
    -H "Accept: application/json" \
    "$BASE_URL/rest$path"
}

api_post() {
  local path="$1"
  local data="$2"
  curl -s -X POST \
    -H "intlAuthToken: $TOKEN" -H "Cookie: intlAuthToken=$TOKEN" \
    -H "vk-cr-code: $CR_CODE" -H "vk-language-code: zh-cn" \
    -H "app-code: international-mgt" \
    -H "Referer: https://sa-manager.lionabc.com/hobbit/product/productpackagemanage/" \
    -H "Content-Type: application/json" -H "Accept: application/json" \
    -d "$data" \
    "$BASE_URL/rest$path"
}
```

---

### 商品包列表

```
GET /rest/international/api/product/list/
```

> 该端点 **硬编码** 只返回 `productTypeId=3` 的商品，不可通过参数覆盖。

**Query 参数（均可选，来自 `ProductQuery`）：**

| 参数 | 类型 | 说明 |
|------|------|------|
| start | int | 分页偏移量，默认 0 |
| limit | int | 每页数量，默认 10 |
| productId | long | 按 ID **精确查询** |
| productName | string | 按名称**精确匹配**（非模糊，SQL 使用 `=`） |
| courseType | string | 按课程类型过滤（如 `MAJOR`） |
| courseId | long | 按课程 ID 过滤 |
| discountType | byte | 按折扣类型过滤，见枚举表 |
| visibility | byte | 按用户侧可见性过滤，见枚举表 |
| adminVisibility | byte | 按客服侧可见性过滤 |
| leadsVisibility | byte | 按 Leads 侧可见性过滤 |
| giftable | byte | 0=普通商品, 1=赠品 |
| status | byte | 0=未发布, 1=已发布（上架），2=已过期，3=已删除 |
| contractId | long | 按合同 ID 过滤 |

**示例：**
```bash
# 精确查找名为 "AIKID-36-Test" 的商品
api_get "/international/api/product/list/?start=0&limit=10&productName=AIKID-36-Test"

# 查看已上架的所有商品
api_get "/international/api/product/list/?start=0&limit=20&status=1"
```

**响应结构：**
```json
{
  "code": 200,
  "data": {
    "total": 246,
    "data": [
      {
        "id": 3539,
        "name": "Migration-Nada-84pack",
        "showName": "{\"default\":\"Migration-Nada-84pack\"}",
        "subProductName": "Migration-Nada",
        "status": 1,
        "courseType": "MAJOR",
        "inventoryTypeName": "1V1正式课时",
        "originPrice": "5381.00",
        "realPrice": "4892.00",
        "visibility": 0,
        "giftable": 0,
        "createTime": 1771924186000,
        "createName": "dyon"
      }
    ]
  }
}
```

---

### 商品包详情

```
GET /rest/international/api/product/detail
```

> 注：后端只读取 `productId` 参数，`type` 参数被忽略。

**参数：**

| 参数 | 说明 |
|------|------|
| productId | 商品包 ID（必填） |

**示例：**
```bash
api_get "/international/api/product/detail?productId=3539"
```

**响应 data 主要字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | long | 商品包 ID |
| name | string | 名称 |
| showName | string | 展示名称（JSON 字符串，如 `{"default":"xxx"}`） |
| productTypeId | long | 商品类型，见枚举表 |
| saleType | int | 售卖类型，见枚举表 |
| originPrice | string | 原价 |
| realPrice | string | 售卖价 |
| discount | decimal | 折扣（0-1 小数，如 0.8 表示八折） |
| discountType | byte | 折扣类型，见枚举表 |
| visibility | byte | 用户侧可见性，见枚举表 |
| adminVisibility | byte | 客服侧可见性，见枚举表 |
| leadsVisibility | byte | Leads 侧可见性，见枚举表 |
| giftable | byte | 0=可赠送, 1=不可赠送 |
| status | byte | 发布状态（只读），见枚举表 |
| expireTime | int | 有效期（天） |
| stockLimit | boolean | 是否限制库存 |
| signatureType | byte | 签单类型，见枚举表 |
| multiCurrencyPricingList | array | 多币种定价列表 |
| detail | array | 子商品明细 `[{subProductId, productCount}]` |
| content | array | CMS 内容列表 |

---

### 新建商品包

```
POST /rest/international/order-service/api/product/new
```

**请求字段（`*` 为必填，由 `@NotNull` 约束）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 商品包名称 |
| `productTypeId` | long | ✅ | 商品类型，普通课包填 `3` |
| `showName` | string | | 展示名称，JSON 格式：`{"default":"xxx"}` |
| `subProductName` | string | | 关联子商品名称（前端展示用） |
| `saleType` | int | | 售卖类型，见枚举表（`1`=课时, `2`=有效期...） |
| `originPrice` | decimal | | 原价 |
| `realPrice` | decimal | | 售卖价 |
| `localeDiscount` | int | | 折扣力度，1-100（如 80 表示八折） |
| `discountType` | byte | | 折扣类型，见枚举表 |
| `visibility` | byte | | 用户侧展示，见枚举表（默认 0=不可见） |
| `adminVisibility` | byte | | 客服侧展示，见枚举表 |
| `leadsVisibility` | byte | | Leads 侧展示，见枚举表 |
| `giftable` | byte | | `0`=可赠送, `1`=不可赠送 |
| `expireTime` | int | | 有效期（天） |
| `stockLimit` | boolean | | 是否限制库存 |
| `signatureType` | byte | | 签单类型，见枚举表 |
| `summary` | string | | 摘要，JSON 格式：`{"default":"xxx"}` |
| `thumbnail` | string | | 封面图 URL |
| `detail` | array | | 子商品明细，见下方结构 |
| `multiCurrencyPricingData` | array | | 多币种定价，见下方结构 |
| `content` | array | | CMS 内容列表 |

**`detail` 子商品明细结构（每项均必填）：**

```json
"detail": [
  {
    "subProductId": 100,
    "productCount": 36
  }
]
```

**`multiCurrencyPricingData` 多币种定价结构：**

```json
"multiCurrencyPricingData": [
  {
    "currencyCode": "AED",
    "originalPrice": "11880.00",
    "discountPercent": 61,
    "sellingPrice": "7247.00",
    "isEnabled": 1
  },
  {
    "currencyCode": "SAR",
    "originalPrice": "11880.00",
    "discountPercent": 61,
    "sellingPrice": "7247.00",
    "isEnabled": 1
  }
]
```

> `discountPercent` 传 0-100 整数（如 61 表示 61% 的折扣），后端自动转换为小数存储。`isEnabled`: 0=未启用, 1=启用。

**完整示例：**
```bash
api_post "/international/order-service/api/product/new" '{
  "name": "AIKID-36class-Test",
  "productTypeId": 3,
  "saleType": 1,
  "showName": "{\"default\":\"36 Classes Test\"}",
  "originPrice": "11880.00",
  "realPrice": "7247.00",
  "localeDiscount": 61,
  "discountType": 1,
  "visibility": 0,
  "adminVisibility": 1,
  "leadsVisibility": 0,
  "giftable": 0,
  "expireTime": 180,
  "stockLimit": false,
  "signatureType": 1,
  "detail": [{"subProductId": 100, "productCount": 36}],
  "multiCurrencyPricingData": [
    {"currencyCode": "AED", "originalPrice": "11880.00", "discountPercent": 61, "sellingPrice": "7247.00", "isEnabled": 1},
    {"currencyCode": "SAR", "originalPrice": "11880.00", "discountPercent": 61, "sellingPrice": "7247.00", "isEnabled": 1}
  ],
  "content": []
}'
```

**成功响应：** `{"code": 200, "data": <新商品包ID>}`

**错误码：**
- `MAINPRODUCT_HAVE_BEEN_RELATED`：子商品已关联其他商品包
- `PRODUCT_DUPLICATE_TAG`：标签重复

---

### 修改商品包

```
POST /rest/international/order-service/api/product/edit
```

**请求体：** 同新建，**必须包含 `id` 字段**。未传的字段不会被清空（部分更新）。

```json
{
  "id": 3537,
  "name": "新名称",
  "realPrice": "6500.00",
  "localeDiscount": 55,
  "multiCurrencyPricingData": [
    {"currencyCode": "AED", "originalPrice": "11880.00", "discountPercent": 55, "sellingPrice": "6534.00", "isEnabled": 1}
  ],
  "content": [],
  "productTagRelList": []
}
```

---

### 优惠券使用限制

#### 查询

```
GET /rest/international/api/product/getCouponLimit/
```

参数：`productId`（必填）

响应：
```json
{
  "code": 200,
  "data": {
    "productId": 3539,
    "couponLimitRate": "50",
    "couponLimitNum": "99"
  }
}
```

#### 更新

```
POST /rest/international/order-service/api/product/editCouponLimit/
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `productId` | long | 商品包 ID（必填） |
| `couponLimitNum` | string | 数量限制，字符串格式，范围 1-999999 |
| `couponLimitRate` | string | 金额比例限制，字符串格式，范围 (0, 100)，不含 0 和 100 |

```json
{
  "productId": 3539,
  "couponLimitRate": "50",
  "couponLimitNum": "100"
}
```

> 两个限制字段均为 **字符串类型**，不可传数字。两者均为可选，不传或传空字符串则表示不限制。

---

### 库存管理

#### 查询

```
GET /rest/international/order-service/api/product/package/stock
```

参数：`packageId`（必填）

响应：
```json
{
  "code": 200,
  "data": {
    "stockLimit": false,
    "stockNum": 0,
    "toBePaidNum": 5,
    "inRefundNum": 1,
    "paymentNum": 120
  }
}
```

#### 更新

```
POST /rest/international/order-service/api/product/package/updateStock
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `packageId` | long | 商品包 ID（必填） |
| `stockLimit` | boolean | `true`=限制库存, `false`=不限制库存 |
| `operateType` | string | `"add"`=追加库存, `"subtract"`=扣减库存（仅 `stockLimit=true` 时有效） |
| `operateNum` | int | 操作数量，必须 > 0（仅 `stockLimit=true` 时有效） |
| `productTypeId` | long | 商品类型 ID，订阅包类型（4/5/9）不支持限制库存 |
| `updateId` | long | 操作人 ID（可选） |

**设置为不限库存：**
```json
{
  "packageId": 3539,
  "stockLimit": false
}
```

**追加库存 100：**
```json
{
  "packageId": 3539,
  "stockLimit": true,
  "operateType": "add",
  "operateNum": 100,
  "productTypeId": 3
}
```

**扣减库存 10：**
```json
{
  "packageId": 3539,
  "stockLimit": true,
  "operateType": "subtract",
  "operateNum": 10,
  "productTypeId": 3
}
```

> ⚠️ `operateType` 只接受 `"add"` 或 `"subtract"`，其他值返回错误。订阅包（4/5/9）不支持限制库存操作。

---

### 赠送权限配置

#### 查询

```
GET /rest/international/api/productPackage/auth/list
```

参数：`packageId`（必填）

响应：`data` 为角色列表 `[{id, productpackageId, role}]`

#### 更新

```
POST /rest/international/api/productPackage/auth/config
```

```json
{
  "packageId": 3539,
  "roleIds": [2397, 2398]
}
```

---

### 辅助查询接口

```bash
# 获取所有课程库存类型（返回 typeCode/typeName，用于确认 inventoryTypeId）
api_get "/international/api/inventory/type/course/rel/list/"

# 获取所有角色列表（返回 id/name，用于赠送权限配置）
api_get "/auth/api/auth/role/all"

# 获取商品类型列表（返回 id/name，确认 productTypeId 含义）
api_get "/international/api/product/type/list"
```

---

## 4. 常用工作流

### 工作流 1：查找并查看商品包

```bash
# 1. 按名称搜索
api_get "/international/api/product/list/?queryType=Product_Package&start=0&limit=10&productName=关键词"

# 2. 查看详情
api_get "/international/api/product/detail?productId=<ID>&type=Package"
```

### 工作流 2：新建商品包（多步依赖）

1. 查询可用子商品：`GET /product/list/?queryType=Product`
2. 查询课程类型：`GET /inventory/type/course/rel/list/`
3. 调用新建接口：`POST /order-service/api/product/new`
4. 配置优惠券限制（可选）：`POST /order-service/api/product/editCouponLimit/`
5. 配置库存（可选）：`POST /order-service/api/product/package/updateStock`
6. 配置赠送权限（可选）：`POST /productPackage/auth/config`

### 工作流 3：批量新建商品包

1. 用户提供 Excel/CSV 文件路径
2. 用 Python 解析文件（参见 `ops_helper.py`）
3. 向用户展示解析结果，**等待二次确认**
4. 逐行调用新建接口，汇总成功/失败数量

### 工作流 4：修改商品包

1. 查询详情获取当前字段值：`GET /product/detail`
2. 向用户确认修改内容
3. 调用修改接口（保留 id 字段）：`POST /order-service/api/product/edit`

---

## 5. 错误处理

| 情况 | 处理方式 |
|------|---------|
| HTTP 401 / code=401 | Token 过期，提示用户重新从浏览器复制 token 到 `~/.vipkid-ops/config.json` |
| code=400, msg 含 "country or region" | 缺少 `vk-cr-code` header，检查请求头配置 |
| `MAINPRODUCT_HAVE_BEEN_RELATED` | 子商品已被其他商品包关联 |
| `PRODUCT_DUPLICATE_TAG` | 标签重复，需修改标签配置 |
| 批量操作部分失败 | 继续执行其余项，最终汇总失败列表供用户处理 |

---

## 6. 安全约束

⛔ **以下操作绝对禁止调用：**
- `POST /rest/international/order-service/api/product/release/` — 上架
- `POST /rest/international/order-service/api/product/unrelease/` — 下架
- 任何包含 `delete`、`remove`、`destroy` 的接口

✅ 批量写入操作（新建/修改）前，**必须先向用户展示清单并等待确认**。
