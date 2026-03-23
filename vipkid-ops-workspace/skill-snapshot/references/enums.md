# 枚举值参考

> 来源：`international-gw` 源码 `ProductEnum.java`。新建/修改接口传整数值，不接受字符串。

## productTypeId（商品类型）

| 值 | 含义 |
|----|------|
| 1 | 商品包（Product_Package） |
| 2 | 子商品（Session） |
| **3** | **标准商业课包（新建普通商品包用此值）** |
| 4 | 订阅包（Renewal_Package）⚠️ 不支持限制库存 |
| 5 | 订阅子包 ⚠️ 不支持限制库存 |
| 9 | 补差订阅包 ⚠️ 不支持限制库存 |
| 10 | 试学包（Trail_Package） |
| 16 | 课程有效期包（Class_Validity） |
| 18 | 最小课消包 |
| 20 | 休学权益包 |

## saleType（售卖类型）

| 值 | 含义 |
|----|------|
| 1 | 课时数量（INVENTORY_NUM） |
| 2 | 课堂有效期（CLASS_VALIDITY_PERIOD） |
| 3 | 考试报名（EXAM_REGISTRATION） |
| 4 | 实物商品（REAL_OBJECTS） |
| 5 | 休学权益（LEAVE_EQUITY） |

## visibility / adminVisibility / leadsVisibility（可见性）

| 值 | 含义 |
|----|------|
| 0 | 不可见 |
| 1 | 可见 |
| 2 | 部分用户可见（仅 `visibility` 支持） |
| 3 | 标签可见（需配合 `visibilityTagRelList`） |

## giftable（赠送）

| 值 | 含义 |
|----|------|
| 0 | 普通商业产品（默认） |
| 1 | 赠品，无签单归属 |

> ⚠️ 源码 `ProductEnum.Giftable` 的描述字符串与枚举常量名相反（历史 bug）。以业务逻辑为准：`giftable=1` 时系统自动将 `signatureType` 设为 `0`（无归属），即 `1` 表示赠品。

## discountType（折扣类型）

| 值 | 含义 |
|----|------|
| 0 | 无折扣 |
| 1 | 正常折扣 |
| 2 | 允许折上折 |

## status（发布状态，只读）

| 值 | 含义 |
|----|------|
| 0 | 未发布（下架） |
| 1 | 已发布（上架） |
| 2 | 已过期 |
| 3 | 已删除 |

## signatureType（签单类型）

| 值 | 含义 |
|----|------|
| 0 | 无归属 |
| 1 | 新签 / 补差 / 续费 |
