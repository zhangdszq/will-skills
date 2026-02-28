# vipkid-ops

VIPKID 国际化运营后台 AI Skill，供 Claude / Cursor Agent 使用。

## 功能

- 查询、新建、修改商品包（ProductPackage）
- 配置优惠券使用限制（couponLimitNum / couponLimitRate）
- 管理库存（追加、扣减、设为不限制）
- 配置赠送权限

> ⛔ 不执行上架、下架、删除操作

## 文件说明

| 文件 | 说明 |
|------|------|
| `SKILL.md` | Skill 主文档，包含快速开始、枚举值参考、API Reference、工作流、错误处理 |
| `ops_helper.py` | Python CLI 辅助工具，封装认证、列表查询、库存更新等操作 |

## 快速开始

### 1. 创建配置文件

```bash
mkdir -p ~/.vipkid-ops
cat > ~/.vipkid-ops/config.json << 'EOF'
{
  "base_url": "https://sa-manager.lionabc.com",
  "token": "<从浏览器 Cookie 复制 intlAuthToken>",
  "cr_code": "sa"
}
EOF
```

### 2. 验证连接

```bash
python3 ops_helper.py auth
```

### 3. 常用命令

```bash
python3 ops_helper.py list                          # 列出商品包
python3 ops_helper.py detail <packageId>            # 查看详情
python3 ops_helper.py inventory <packageId>         # 查看库存
python3 ops_helper.py update-stock <id> add 100     # 追加库存 100
python3 ops_helper.py update-stock <id> infinity    # 设为不限制库存
python3 ops_helper.py coupon-limit <packageId>      # 查看优惠券限制
```

## `vk-cr-code` 地区码

| 代码 | 地区 |
|------|------|
| `sa` | 沙特阿拉伯 |
| `ae` | 阿联酋 |
| `k2` | 海湾地区（K2） |
| `hk` | 香港 |
| `tw` | 台湾 |
| `kr` | 韩国 |
| `vn` | 越南 |
| `jp` | 日本 |
| `ts` | 测试环境 |

## 安装为 Claude Skill

将本仓库克隆到 `~/.claude/skills/vipkid-ops/`：

```bash
git clone https://github.com/zhangdszq/vipkid-ops.git ~/.claude/skills/vipkid-ops
```

## 数据来源

API 字段文档和枚举值均来自 `international-gw` 后端服务源码：
- `ProductVO.java` — 商品包字段定义
- `ProductEnum.java` — 所有枚举值（visibility、giftable、saleType、productTypeId 等）
- `ProductMapper.xml` — 实际 SQL 查询参数
- `ProductServiceImpl.java` — 库存操作逻辑（operateType: add / subtract）
