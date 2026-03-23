# megaview-openapi

这是一个面向销售分析和带教场景的 skill。当前默认以沙特 `leads-to-order` 转化视角为主线，在 `intl_analysis` 中先定义增长链路、销售范围和业务优先级，并补看试听完课与试听后跟进，再用 Megaview 补会话质量、客户质量和带教证据，优先解决下面两类问题：

1. 员工表现分析
2. 代表性通话样本与带教分析

它不是一个通用的 Megaview API 助手，也不应该被用来自动做淘汰决策。

## 先看这里

如果你只想快速理解这个 skill，先记住 5 句话：

1. 先看 `intl_analysis`，后看 Megaview。
2. 默认从沙特 `leads-to-order` 转化主链路切入，并补看试听是否完课、完课后是否及时跟进。
3. 员工表现分析先看数据库在职状态，再决定是否进入默认复核范围。
4. Megaview 主要用来补会话质量、客户质量、摘要、ASR 和带教证据。
5. 这个 skill 用于分析、复核、带教，不用于自动淘汰或通用 API 问答。

## 这个 skill 在解决什么

StarRocks 侧：

- 当前只面向 `intl_analysis` 数据库，并作为主驱动层
- 默认优先回答增长链路、销售表现、订单和承接问题

Megaview 侧：

- 围绕员工、会话、客户评分、摘要、ASR 做补充解释和带教分析
- 更适合回答“为什么这个销售会这样表现”“这通电话具体怎么聊的”

默认输出目标：

- 给管理者做绩效复核
- 给团队做培训样例
- 给业务做增长链路分析总结

当前优先覆盖这些分析主题：

- 沙特 `leads-to-order` 转化主链路
- 销售团队 / 个人表现与 GMV
- 渠道 x 销售 跟进与转化表现
- 投放花费、ROAS 与销售承接
- LP 人效、试听完课、试听触达、TCC 转新签
- 订单实付、退款、库存消耗
- 课消、到课、家长反馈
- 学情、作业、UA 表现

不适用的场景：

- 通用 API 文档问答
- 任意 endpoint 的 curl / Python 模板生成
- 切换到其他 StarRocks 数据库做分析

## 默认怎么走

这个 README 按 top-down 的方式理解，默认顺序是：

1. 先定义业务问题属于哪一段增长链路。
2. 再确定要看哪支团队、哪个渠道、哪个销售，或者哪个 LP / 试听完课 / TCC 节点。
3. 如果涉及员工表现，先在数据库里确认员工是否仍在职。
4. 用 `intl_analysis` 下业务结论。
5. 只有在需要解释个人问题时，才下钻 Megaview。

一句话理解：

- `intl_analysis` 决定先看什么、谁更好、谁更差
- Megaview 解释这个结果背后的会话质量和带教问题

适合这样的问题：

- 沙特从渠道到订单的转化卡在哪一段
- 哪些销售团队 / 销售个人承接更好或更差
- 哪些 LP、试听完课或 TCC 节点影响了最终转化
- 哪些销售值得继续深挖通话和带教
- 销售结果和会话质量是否一致

## 你提问时先给什么

大多数情况下，至少给这些：

- 时间范围
- 如果是增长链路问题，最好给业务范围
  - `business_line`
  - 渠道
  - 销售团队 / 销售个人
  - 是否聚焦 LP / 试听完课 / TCC / 订单

只有在特殊情况下才需要补更多信息：

- 你想切换到 `intl_analysis` 内的非默认主题表
- 你想改 join 字段、时间字段或指标表达式
- 你只想查 StarRocks，不想走内置员工分析脚本

Megaview 凭证默认按下面顺序获取：

1. 显式传入
2. 环境变量 `MEGAVIEW_APP_KEY` / `MEGAVIEW_APP_SECRET`
3. `~/.vk-cowork/megaview_credentials.json`
4. `data/megaview_credentials.json`

## 默认规则

### 员工

- 员工表现分析先看 `vk_gl_leads_staff_team_assignment_relation`
- 默认把 `termination_date is null` 视为在职，`termination_date is not null` 视为离职
- 默认绩效复核范围优先保留数据库在职员工
- 如果用户明确点名某个离职员工，可以继续做历史分析，但要显式标注为 `inactive` / 离职复盘
- 默认绩效复核排序不应把数据库已离职员工和当前在职员工混在同一个 active review 池里
- `data/employees.json` 主要用于把已确认的员工映射到 Megaview `origin_user_id`
- `employees.json` 里的 `staffId` 在当前 skill 中视为 Megaview 的 `origin_user_id`
- 员工与 StarRocks 默认按 `staffName -> staff_name` 关联

### StarRocks

- StarRocks 默认配置来自 `data/starrocks_config.json`
- 默认数据库是 `intl_analysis`
- 默认沙特转化主表是 `vk_sr_intl_sa_leads_to_order_details_lv`
- 默认销售快照锚点是 `vk_sr_intl_sa_cc_quality_monitor_da`
- 默认销售金额指标是 `SUM(total_new_gmv_usd)`

关于销售质量表，当前建议这样理解：

- `vk_sr_intl_sa_cc_quality_monitor_da`
  - T+1 快照
  - 更适合回溯、日级复盘、稳定排序
- `vk_sr_intl_sa_cc_quality_monitor_lv`
  - 实时逻辑视图
  - 更适合近实时销售质量观察
- `vk_sr_intl_sa_cc_quality_monitor_today_lv`
  - 更适合看当日表现
- `vk_sr_intl_sa_cc_quality_monitor_all_lv`
  - 更适合看全量范围

### 口径与时间

订单口径的默认提醒：

- 默认 GMV 讨论通常按业务口径看总 GMV
- 默认应提示“GMV 含退费金额”
- 只有在明确讨论退费时，才单列或剔除 `refunded` 相关口径

时间字段的默认提醒：

- 订单表里的 `paid_time` 是北京时间
- `paid_date_country` 是当地日期
- 沙特转化链路如果看跟进时效、试听完课、试听后触达、首单转化，优先使用带 `_jordan` 的约旦时间字段

### 常见 live reporting tables

- `vk_sr_intl_sa_leads_to_order_details_lv`
- `vk_sr_intl_sa_lp_performance_evaluation_details_mtd_lv`
- `vk_sr_intl_sa_leads_staff_relation_record_lv`
- `vk_sr_intl_sa_trial_contact_summary_lv`
- `global_tcc_to_new_conversion_aging_lv`
- `vk_sr_intl_sa_marketing_spend_daily_lv`
- `vk_sr_intl_sa_marketing_spend_7d_roas_lv`
- `vk_sr_intl_sa_marketing_spend_mtd_roas_lv`
- `vk_sr_intl_sa_marketing_spend_ytd_roas_lv`
- `vk_sr_intl_sa_cc_quality_monitor_da`
- `vk_sr_intl_gl_leads_channel_analysis_follow_record_lv`
- `vk_sr_intl_ae_order_detail_lv`
- `vk_sr_intl_kr_order_detail_lv`
- `vk_sr_intl_ae_class_consumption_detail_lv`
- `vk_sr_intl_kr_class_consumption_detail_lv`
- `vk_sr_intl_sa_student_learning_performance_lv`

## 沙特主链路默认怎么下钻

如果问题是“沙特增长链路哪里出问题了”，默认按这条链路往下看：

1. 投放 / 渠道
   - `vk_sr_intl_sa_marketing_spend_daily_lv`
   - `vk_sr_intl_sa_marketing_spend_7d_roas_lv`
   - `vk_sr_intl_sa_marketing_spend_mtd_roas_lv`
2. 渠道承接与线索跟进
   - `vk_sr_intl_gl_leads_channel_analysis_follow_record_lv`
   - `vk_sr_intl_sa_leads_staff_relation_record_lv`
3. 沙特 leads-to-order 转化
   - `vk_sr_intl_sa_leads_to_order_details_lv`
4. LP / 服务承接
   - `vk_sr_intl_sa_lp_performance_evaluation_details_mtd_lv`
5. 试听完课与完课后跟进
   - `vk_sr_intl_sa_leads_to_order_details_lv`
   - `vk_sr_intl_sa_trial_contact_summary_lv`
6. TCC / 试听触达
   - `global_tcc_to_new_conversion_aging_lv`
   - `vk_sr_intl_sa_trial_contact_summary_lv`
7. 个人会话深挖
   - Megaview 会话、评分、摘要、ASR

默认下钻顺序：

- 先看渠道和投放
- 再看销售团队和个人承接
- 再看 LP / 试听完课 / TCC / 试听触达
- 最后再到 Megaview 深挖个人会话

## 再往下：先看主链路案例

### 主链路案例 1：先看沙特 leads-to-order 转化总览

适用问题：

- 沙特最近 7 天 / 30 天从线索到订单的转化怎么样
- 哪支销售团队或哪些销售承接效果更好
- 哪些环节的转化速度、试听完课后的跟进效率或触达效率有问题

默认走法：

- 主表优先看 `vk_sr_intl_sa_leads_to_order_details_lv`
- 先看：
  - `first_order_deal_price`
  - `paid_flag`
  - `leads_quality`
  - `last_ccid_name`
  - `last_cc_tl_name`
  - `last_lpid_name`
  - `register_first_follow_diff_hour`
  - `first_trial_completed_follow_time_jordan`
  - `first_trial_completed_schedule_follow_time_diff_hour`
- 再决定是否需要下钻到个人 Megaview 会话

示例提问：

```text
先帮我看沙特最近 30 天 leads-to-order 转化总览，按销售团队和个人拆开。
```

### 主链路案例 2：根据渠道看销售表现

适用问题：

- 我想看不同渠道下各销售的表现
- 我想看渠道带来的线索，最后是哪些销售在跟进、转化更好
- 我想按一级 / 二级渠道看销售跟进和成单表现

你至少要提供：

- 时间范围
- 你想看的渠道层级，或者直接给渠道名
- 如果要看某组销售，给出销售范围或市场范围

默认走法：

- 先在 `intl_analysis` 里按“渠道 x 销售”主题选表
- 如果想看渠道下的跟进、通话、触达情况，优先参考：
  - `vk_sr_intl_gl_leads_channel_analysis_follow_record_lv`
- 如果想看沙特渠道到订单的转化、首单金额、跟进到成单链路，优先参考：
  - `vk_sr_intl_sa_leads_to_order_details_lv`
- 如果后续需要解释某个销售在某个渠道下为什么表现异常，再补 Megaview 会话证据

常见字段：

- 渠道字段：
  - `mkt_channel_name`
  - `channel_level_one`
  - `channel_level_two`
  - `channel_level_three`
- 销售字段：
  - `last_ccid`
  - `last_ccid_name`
  - `last_cc_tl_name`
- 跟进 / 通话字段：
  - `total_calls`
  - `valid_calls`
  - `invalid_calls`
  - `not_connected_calls`
  - `talk_minutes`
  - `call_connect_rate_per_parent`
- 转化字段：
  - `paid_flag`
  - `first_order_deal_price`
  - `lifetime_purchase_count`
  - `outbound_call_count`
  - `valid_call_count`

示例提问：

```text
我想看最近 30 天不同渠道下各销售的表现，先按一级渠道看，再看哪些销售的跟进和转化更好。
```

### 主链路案例 3：看投放到销售承接

适用问题：

- 某些渠道花费高，但销售承接是否跟上了
- 7d ROAS、注册、试听、成单之间是否匹配

默认走法：

- 花费看：
  - `vk_sr_intl_sa_marketing_spend_daily_lv`
  - `vk_sr_intl_sa_marketing_spend_7d_roas_lv`
- 结合渠道和销售承接，再看：
  - `vk_sr_intl_sa_leads_to_order_details_lv`
  - `vk_sr_intl_gl_leads_channel_analysis_follow_record_lv`

常见字段：

- `spend`
- `mkt_channel_name`
- `total_registered_parent`
- `total_trial_parents_booked_cohort`
- `total_new_order_noncohort`
- `total_new_gmv_usd_noncohort`
- `roas_noncohort`

示例提问：

```text
我想看沙特最近 30 天各渠道花费、7d ROAS，以及这些渠道后续被哪些销售承接得更好。
```

### 主链路案例 4：看 LP 人效与服务承接

适用问题：

- 哪些 LP 承接效果更好
- 哪些 LP 服务了更多家长，但续费或消耗结果不理想

默认走法：

- 主表优先看 `vk_sr_intl_sa_lp_performance_evaluation_details_mtd_lv`
- 常见字段：
  - `last_lpid_name`
  - `active_parent_num`
  - `served_parent_num`
  - `curr_month_major_as_parent_num`
  - `total_actual_consumption`
  - `total_plan_consumption`
  - `renewal_commission_SAR`

示例提问：

```text
我想看沙特本月 LP 人效，重点看服务家长数、实际消耗和续费佣金。
```

### 主链路案例 5：看试听完课 / TCC / 试听触达与转化

适用问题：

- 试听是否顺利完课，完课后多久被跟进
- TCC 到新签的周期和时长
- 试听前后触达是否影响转化
- 哪些销售在试听承接上表现更好

默认走法：

- 试听完课与完课后跟进优先补看：
  - `vk_sr_intl_sa_leads_to_order_details_lv`
- TCC 转新签优先看：
  - `global_tcc_to_new_conversion_aging_lv`
- 试听触达优先看：
  - `vk_sr_intl_sa_trial_contact_summary_lv`

常见字段：

- `first_trial_completed_follow_time_jordan`
- `first_trial_completed_schedule_follow_time_diff_hour`
- `trial_class_time`
- `trial_student_class_status`
- `class_status_description`
- `last_paid_time`
- `time_difference_days`
- `last_ccid_name`
- `mkt_channel_name`
- `pre_contact`
- `pre_connect_15s`
- `post_contact`
- `post_connect_15s`
- `paid_flag`

示例提问：

```text
我想看沙特试听前后触达和 TCC 到新签的周期，按销售个人拆开。
```

### 主链路案例 6：按个人维度深挖 Megaview

适用问题：

- 某个销售在转化链路里表现异常，我想听他到底怎么聊的
- 某个销售的业务结果差，是触达不够，还是话术质量有问题
- 某个团队里谁最值得先做会话带教

默认走法：

- 先从 `intl_analysis` 里选出要深挖的个人
- 再从 `employees.json` 解析到 Megaview `origin_user_id`
- 再拉：
  - 会话列表
  - 会话评分
  - 客户评分
  - `summary_pro`
  - `asr_data`

示例提问：

```text
先从沙特 leads-to-order 转化里找出最近 30 天承接较差的销售，再深挖他在 Megaview 里的会话问题。
```

## 再往下：按专题问题看

### 案例 1：看单个销售最近表现

适用问题：

- 帮我看某个销售最近 7 天 / 14 天 / 30 天表现
- 我想看会话评分、客户评分、会话量，再和 GMV 对比

你至少要提供：

- 一个真实存在于 `employees.json` 的员工姓名
- 如果是正常绩效分析，默认优先看数据库里仍在职的员工
- 开始时间和结束时间，或明确的最近 N 天

默认走法：

- 先在 `vk_gl_leads_staff_team_assignment_relation` 里确认员工状态，优先按在职员工进入默认复核范围
- StarRocks：先查 `vk_sr_intl_sa_cc_quality_monitor_da`
- Megaview：再用 `employees.json` 映射员工信息、会话列表、会话评分、客户评分
- join：`staffName -> staff_name`

典型输出：

- `sales_amount`
- `conversation_count`
- `average_conversation_score`
- `average_customer_score`
- 业务结果与会话质量的解释

示例提问：

```text
帮我看 Mohammad Qasem 最近 30 天的表现，我想看会话评分、客户评分、会话数量，再和 StarRocks 销售额对比。
```

### 案例 2：比较多个销售

适用问题：

- 比较两位或多位销售最近 14 天表现
- 这组销售里谁更值得优先复核

你至少要提供：

- 多个真实销售姓名
- 时间范围

默认走法：

- 仍然优先走 `scripts/employee_performance.py`
- 先在 `vk_gl_leads_staff_team_assignment_relation` 里确认员工状态，默认优先对数据库在职员工做对比和排序
- 再在 `intl_analysis` 里完成销售对比和排序
- 再用 Megaview 解释各销售的会话质量差异

典型输出：

- 每个销售的 Megaview 指标
- 每个销售的 StarRocks 指标
- 对比说明
- `review_priority_ranking`

示例提问：

```text
我想比较 Mohammad Qasem 和 Salman Awaysheh 最近 14 天的表现。
```

### 案例 3：抓代表性通话做带教

适用问题：

- 给我找几个好 / 中 / 差的代表性通话
- 我要做培训样例
- 我想看具体对话片段和改进建议

你至少要提供：

- 一个员工
- 时间范围

默认走法：

- 先从 `intl_analysis` 的销售视角确定要带教的员工或时间段
- 如果 StarRocks 可用，先在 `vk_gl_leads_staff_team_assignment_relation` 里补充员工状态
- 再从 `employees.json` 解析员工
- 用 `origin_user_id` 查会话列表
- 选 low / median / high 三档样本
- 拉取 `score_result`、`summary_pro`、`asr_data`

补充规则：

- 如果该员工已经离职，但你是明确点名要复盘，仍然可以继续输出带教样本
- 这时更适合把结果理解为 `historical review`，而不是当前在职带教池

典型输出：

- 低分样本
- 中位样本
- 高分样本
- 摘要重点
- ASR 预览
- 带教建议

示例提问：

```text
抓 Abdelrahman Al-Hamdan 在 2026 年 2 月的几个代表性会话，给我做培训样例。我要看到低分、中间值、高分的会话和一小段转写。
```

### 案例 4：做绩效复核优先级，而不是淘汰结论

适用问题：

- 谁最弱
- 谁应该先进入绩效复核
- 谁最需要优先带教

正确使用方式：

- skill 会先基于 `vk_gl_leads_staff_team_assignment_relation` 定义当前在职复核范围
- 再基于 `intl_analysis` 做销售复核优先级
- 再用 Megaview 补充质量原因和带教方向
- 不会输出自动淘汰决策

默认参考指标：

- `sales_amount`
- `average_conversation_score`
- `average_customer_score`
- `conversation_count`

典型输出：

- `high / medium / low`
- `urgent_manual_review / coach_and_recheck / stable`
- 具体原因

示例提问：

```text
这组销售里谁应该优先进入绩效复核？你结合会话评分、客户评分、GMV 和通话量给我排一下。
```

### 案例 5：查订单实付、退款、库存消耗

适用问题：

- 我不只想看 GMV，我还想看实付、退款和库存
- 我想按销售或区域看订单细项

你至少要提供：

- 时间范围
- 如果要按销售分析，最好提供区域或销售口径

默认走法：

- 不再强行使用默认 GMV 表
- 仍然先以 `intl_analysis` 为主
- 改为走 `references/starrocks-routing.md` 的订单路由
- 当前 `intl_analysis` 里优先参考 live reporting table，例如：
  - `vk_sr_intl_ae_order_detail_lv`
  - `vk_sr_intl_kr_order_detail_lv`

常见字段：

- `order_given_staff_name`
- `order_given_staff_id`
- `pay_time`
- `refund_time`
- `deal_price`
- `refund_price`
- `inventory_quantity`
- `consumed_quantity`
- `available_quantity`
- `unavailable_quantity`

示例提问：

```text
我想看 AE 市场最近 30 天的订单实付、退款和库存消耗，最好还能按销售看。
```

### 案例 6：根据渠道看销售表现

适用问题：

- 我想看不同渠道下各销售的表现
- 我想看渠道带来的线索，最后是哪些销售在跟进、转化更好
- 我想按一级 / 二级渠道看销售跟进和成单表现

你至少要提供：

- 时间范围
- 你想看的渠道层级，或者直接给渠道名
- 如果要看某组销售，给出销售范围或市场范围

默认走法：

- 先在 `intl_analysis` 里按“渠道 x 销售”主题选表
- 如果想看渠道下的跟进、通话、触达情况，优先参考：
  - `vk_sr_intl_gl_leads_channel_analysis_follow_record_lv`
- 如果想看渠道到订单的转化、首单金额、跟进到成单链路，优先参考：
  - `vk_sr_intl_sa_leads_to_order_details_lv`
- 如果后续需要解释某个销售在某个渠道下为什么表现异常，再补 Megaview 会话证据

常见字段：

- 渠道字段：
  - `mkt_channel_name`
  - `channel_level_one`
  - `channel_level_two`
  - `channel_level_three`
- 销售字段：
  - `last_ccid`
  - `last_ccid_name`
  - `last_cc_tl_name`
- 跟进 / 通话字段：
  - `total_calls`
  - `valid_calls`
  - `invalid_calls`
  - `not_connected_calls`
  - `talk_minutes`
  - `call_connect_rate_per_parent`
- 转化字段：
  - `paid_flag`
  - `first_order_deal_price`
  - `lifetime_purchase_count`
  - `outbound_call_count`
  - `valid_call_count`

示例提问：

```text
我想看最近 30 天不同渠道下各销售的表现，先按一级渠道看，再看哪些销售的跟进和转化更好。
```

### 案例 7：查课消、到课、家长反馈

适用问题：

- 我想看课消量、到课情况、完课情况
- 我想把课堂相关指标和老师 / 学生 / 家长反馈结合起来

默认走法：

- 参考 `references/starrocks-routing.md`
- 在 `intl_analysis` 中优先找 class consumption 类 live table，例如：
  - `vk_sr_intl_ae_class_consumption_detail_lv`
  - `vk_sr_intl_kr_class_consumption_detail_lv`

常见字段：

- `teacher_id`
- `student_id`
- `parent_id`
- `course_type`
- `student_class_status`
- `consume_inventory`
- `consumed_inventory`
- `parent_to_teacher_score`
- `book_time`
- `schedule_time`

示例提问：

```text
我想看 AE 市场最近两周的课消、到课和家长对老师评分，应该查哪张表？
```

### 案例 8：查学情、作业、UA 表现

适用问题：

- 我想看学情表现
- 我想看作业完成、预习视频和 UA 得分

默认走法：

- 参考 `references/starrocks-routing.md`
- 在 `intl_analysis` 中优先找 learning performance 类表，例如：
  - `vk_sr_intl_sa_student_learning_performance_lv`
  - `vk_sr_intl_ae_student_learning_performance_lv`
  - `vk_sr_intl_kr_student_learning_performance_lv`

常见字段：

- `parent_to_teacher_score`
- `parent_to_courseware_score`
- `ua_score`
- `ua_full_score`
- `ua_grade_percentage`
- `if_homework_started`
- `if_homework_completed`
- `homework_correct_quiz_amount`
- `homework_total_quiz_amount`
- `preview_video_opened_count`
- `preview_video_completed_count`

示例提问：

```text
我想看 SA 市场最近一个月的学情表现，重点看 UA、作业和预习视频数据。
```

### 案例 9：验证文档里的表名能不能直接查

适用问题：

- 文档里这个 `vk_intl_dw_*_mv` 现在能直接查吗
- 这个字段口径我知道了，但线上库里实际该查哪张表

默认走法：

- 先把文档里的名字当作指标定义层对象
- 然后只在 `intl_analysis` 里验证是否存在
- 如果不存在，就映射到当前可查的 live reporting table

正确理解：

- `data/国际站全部物化视图_指标字段口径梳理_2026-03-11.md` 更像指标口径说明
- 当前线上实际可查对象主要是 `vk_sr_intl_*_lv` 和 `vk_sr_intl_*_da`

示例提问：

```text
你文档里提到的 vk_intl_dw_evt_pack_order_analyse_gl_mv 可以直接在现在这个库里查吗？如果不行，你会怎么处理？
```

## 最后：默认脚本入口

### 1. 员工表现分析

```bash
python3 "/Users/zhang/.claude/skills/megaview-openapi/scripts/employee_performance.py" \
  --employee-name "Mohammad Qasem" \
  --begin-time "2026-03-01 00:00:00" \
  --end-time "2026-03-08 00:00:00"
```

### 2. 培训样例抽取

```bash
python3 "/Users/zhang/.claude/skills/megaview-openapi/scripts/conversation_training_samples.py" \
  --employee-name "Abdelrahman Al-Hamdan" \
  --begin-time "2026-02-01 00:00:00" \
  --end-time "2026-03-01 00:00:00"
```

### 3. StarRocks 探索式查询

```bash
python3 "/Users/zhang/.claude/skills/megaview-openapi/scripts/starrocks_query.py" \
  --sql "SELECT table_name FROM information_schema.tables WHERE table_schema='intl_analysis' LIMIT 20"
```

## 维护时再看这些文件

- `SKILL.md`
  入口说明、场景路由、默认行为
- `references/analytics.md`
  员工分析链路
- `references/coaching.md`
  带教样本链路
- `references/starrocks-routing.md`
  StarRocks 选表说明
- `references/auth-common.md`
  Megaview 鉴权、通用规则、已知文档坑
- `scripts/employee_performance.py`
  默认员工表现分析脚本
- `scripts/conversation_training_samples.py`
  默认带教样本脚本
- `scripts/starrocks_query.py`
  StarRocks 通用查询脚本

## 已知限制

- 当前只支持 `intl_analysis`
- 默认 Megaview 员工映射依赖 `data/employees.json`
- 数据库在职判断依赖 `vk_gl_leads_staff_team_assignment_relation` 的同步质量
- 文档里的 `vk_intl_dw_*_mv` 不等于当前一定可直接查询
- Megaview 会话批量查询有单次 7 天窗口限制，但脚本已做分片处理
- 有些会话可能没有完整评分、摘要或 ASR
- 当前默认叙事是销售主驱动，不是 Megaview 主驱动
- 结论只能用于人工分析、带教和绩效复核，不能直接用于自动淘汰
