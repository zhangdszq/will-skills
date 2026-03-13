---
name: vipkid-ops
description: >
  VIPKID 国际化运营后台助理，操作 sa-manager.lionabc.com 管理端。
  支持商品包查询、新建、修改，配置优惠券使用限制、库存（追加/扣减/不限制）、赠送权限。
  用户说「查商品包」「新建课包」「修改价格」「配置库存」「优惠券限制」「赠送配置」时触发。
  ⛔ 绝不执行上架、下架、删除操作。
---

# VIPKID 运营后台

通过 `scripts/ops_helper.py` 或直接 `curl` 调用 REST API 操作运营后台。

## 初始化（首次使用）

```bash
# 1. 创建配置文件
mkdir -p ~/.vipkid-ops
cat > ~/.vipkid-ops/config.json << 'EOF'
{
  "base_url": "https://sa-manager.lionabc.com",
  "token": "",
  "cr_code": "sa"
}
EOF

# 2. 自动获取 token（推荐）
python3 ~/.claude/skills/vipkid-ops/scripts/ops_helper.py refresh-token

# 3. 验证
python3 ~/.claude/skills/vipkid-ops/scripts/ops_helper.py auth
```

**自动获取 token（推荐）**：
- `refresh-token` 会打开一个独立的 Chrome 窗口，不影响你当前正在使用的浏览器
- 第一次运行时，在这个独立窗口中手动登录 `sa-manager.lionabc.com`
- 登录成功后脚本会自动读取 `intlAuthToken` 并写入 `~/.vipkid-ops/config.json`
- 独立窗口使用专用登录目录：`~/.vipkid-ops/playwright-profile`

**可选高级模式**：如果你本来就有一个带 `--remote-debugging-port` 的 Chrome，也可以运行：
```bash
python3 ~/.claude/skills/vipkid-ops/scripts/ops_helper.py refresh-token --mode cdp --port 9222
```

**手动获取 token（兜底）**：Chrome 打开后台 → F12 → Application → Cookies → `intlAuthToken` → 复制 Value。

**`cr_code` 地区码**：`sa`=沙特 · `ae`=阿联酋 · `k2`=海湾 · `hk`=香港 · `tw`=台湾 · `kr`=韩国 · `vn`=越南 · `jp`=日本 · `ts`=Tiger

**token 过期**：优先自动刷新：
```bash
python3 ~/.claude/skills/vipkid-ops/scripts/ops_helper.py refresh-token
python3 ~/.claude/skills/vipkid-ops/scripts/ops_helper.py auth
```

手动更新时也可运行：
```bash
python3 -c "
import json; from pathlib import Path
cfg = Path.home() / '.vipkid-ops/config.json'
d = json.loads(cfg.read_text()); d['token'] = input('新token: ')
cfg.write_text(json.dumps(d, indent=2, ensure_ascii=False))"
```

---

## 请求模板

```bash
CONFIG=$(cat ~/.vipkid-ops/config.json)
TOKEN=$(echo $CONFIG | python3 -c "import json,sys; print(json.load(sys.stdin)['token'])")
BASE_URL=$(echo $CONFIG | python3 -c "import json,sys; print(json.load(sys.stdin)['base_url'])")
CR_CODE=$(echo $CONFIG | python3 -c "import json,sys; print(json.load(sys.stdin).get('cr_code','sa'))")

api_get() {
  curl -s -H "intlAuthToken: $TOKEN" -H "Cookie: intlAuthToken=$TOKEN" \
    -H "vk-cr-code: $CR_CODE" -H "vk-language-code: zh-cn" \
    -H "app-code: international-mgt" \
    -H "Referer: https://sa-manager.lionabc.com/hobbit/product/productpackagemanage/" \
    -H "Accept: application/json" "$BASE_URL/rest$1"
}
api_post() {
  curl -s -X POST -H "intlAuthToken: $TOKEN" -H "Cookie: intlAuthToken=$TOKEN" \
    -H "vk-cr-code: $CR_CODE" -H "vk-language-code: zh-cn" \
    -H "app-code: international-mgt" \
    -H "Referer: https://sa-manager.lionabc.com/hobbit/product/productpackagemanage/" \
    -H "Content-Type: application/json" -H "Accept: application/json" \
    -d "$2" "$BASE_URL/rest$1"
}
```

或使用辅助脚本（推荐批量/复杂场景）：
```bash
HELPER="python3 ~/.claude/skills/vipkid-ops/scripts/ops_helper.py"
$HELPER list [名称]              # 列表
$HELPER detail <id>              # 详情
$HELPER inventory <id>           # 库存
$HELPER refresh-token            # 打开独立 Chrome 窗口登录并自动刷新 token
$HELPER refresh-token --mode cdp --port 9222 # 可选：从已开启 CDP 的 Chrome 读取 token
$HELPER update-stock <id> add 100        # 追加库存
$HELPER update-stock <id> subtract 10   # 扣减库存
$HELPER update-stock <id> infinity       # 不限制库存
$HELPER coupon-limit <id>        # 优惠券限制
$HELPER from-excel <file.xlsx>   # 解析 Excel
$HELPER batch-create <file.json> # 批量新建（需确认）
```

---

## 常用工作流

**查找商品包**
```bash
api_get "/international/api/product/list/?start=0&limit=10&productName=精确名称"
api_get "/international/api/product/detail?productId=<ID>"
```

**新建商品包**（必填：`name` + `productTypeId=3` + `multiCurrencyPricingData` 至少一条）
```bash
api_post "/international/order-service/api/product/new" '{
  "name": "AIKID-36class-Test", "productTypeId": 3, "saleType": 1,
  "originPrice": "11880.00", "realPrice": "7247.00", "localeCurrencyRealPrice": "7247.00", "localeDiscount": 61,
  "discountType": 1, "visibility": 0, "adminVisibility": 1,
  "giftable": 0, "expireTime": 180, "stockLimit": false, "signatureType": 1,
  "detail": [{"subProductId": 100, "productCount": 36}],
  "multiCurrencyPricingData": [
    {"currencyCode": "AED", "originalPrice": "11880.00", "discountPercent": 61, "sellingPrice": "7247.00", "isEnabled": 1}
  ], "content": []
}'
```

**修改商品包**（必须带 `id`，未传字段不清空）
```bash
api_post "/international/order-service/api/product/edit" '{"id": 3537, "realPrice": "6500.00"}'
```

**库存 / 优惠券 / 赠送** → 见 [references/api.md](references/api.md)

---

## 参考文档

- **完整 API 列表、请求/响应结构**：[references/api.md](references/api.md)
- **所有枚举值**（productTypeId / saleType / visibility / giftable 等）：[references/enums.md](references/enums.md)

---

## 安全约束

⛔ **禁止调用：**
- `POST .../product/release/` — 上架
- `POST .../product/unrelease/` — 下架
- 任何含 `delete`、`remove`、`destroy` 的接口

✅ 批量写入前**必须展示清单并等待用户二次确认**。

## 错误处理

| 情况 | 处理 |
|------|------|
| HTTP 401 | Token 过期，先运行 `refresh-token` 打开独立 Chrome 登录，失败再手动复制 Cookie |
| Playwright 打开的独立窗口里未检测到 `intlAuthToken` | 先确认已在独立窗口中完成登录，再重试自动刷新 |
| 想复用一个已开启远程调试端口的 Chrome | 改用 `refresh-token --mode cdp --port 9222` |
| code=400 含 "country or region" | `cr_code` 错误，检查 config.json |
| `MAINPRODUCT_HAVE_BEEN_RELATED` | 子商品已被其他商品包关联 |
| `PRODUCT_DUPLICATE_TAG` | 标签重复 |
| 批量部分失败 | 继续执行，最终汇总失败列表 |
