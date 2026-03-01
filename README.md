# vk-skills

Agent Skills 技能库。

## 技能列表

| 技能 | 说明 |
|------|------|
| [vipkid-ops](vipkid-ops/) | VIPKID 国际化运营后台助理，支持商品包查询/新建/修改、库存、优惠券、赠送权限配置 |
| [dingtalk-task-stats](dingtalk-task-stats/) | 钉钉 AI 表格任务统计与需求看板分析，全量拉取记录后按字段过滤、聚合统计 |

## 安装

```bash
# macOS / Linux
ln -s ~/git-repos/vk-skills/<skill-name> ~/.claude/skills/<skill-name>
ln -s ~/git-repos/vk-skills/<skill-name> ~/.cursor/skills/<skill-name>

# Windows (PowerShell 管理员)
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\<skill-name>" -Target "D:\git-repos\vk-skills\<skill-name>"
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.cursor\skills\<skill-name>" -Target "D:\git-repos\vk-skills\<skill-name>"
```
