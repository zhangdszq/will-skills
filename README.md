# will-skills

个人 AI Agent Skill 合集，供 Claude / Cursor Agent 使用。

## 目录

| Skill | 说明 |
|-------|------|
| [vipkid-ops](./vipkid-ops/) | VIPKID 国际化运营后台助理（商品包查询、新建、修改、库存管理） |

## 安装

将本仓库克隆到 Claude Skills 目录，然后为各 Skill 建立软链接：

```bash
git clone https://github.com/zhangdszq/will-skills.git ~/git-repos/will-skills

# vipkid-ops
ln -sf ~/git-repos/will-skills/vipkid-ops ~/.claude/skills/vipkid-ops
```

## 新增 Skill

在仓库根目录新建子目录，包含 `SKILL.md`（必须），其余文件按需添加。
