---
alwaysApply: true
---
# 数据口径使用手册（SQL 口径）

本手册包含数据库表目录与可执行的 StarRocks SQL 口径。

## 数据库表目录

| 主题域 | 表名 | 表类型 | 更新频率 | 用途 |
| --- | --- | --- | --- | --- |

### 国际化

#### 手工维护的逻辑视图

##### 国家/区域维度

| 用途分类（按表名猜测） | 国家/区域 | 表名 | 表类型 | 更新频率 | 用途 |
| --- | --- | --- | --- | --- | --- |
| 订单/GMV/转化 | 全球 | intl_analysis.global_real_time_order_10_mins_lv | 逻辑视图 | 实时 | 实时订单与GMV观察（10分钟粒度） |
| 订单/GMV/转化 | 全球 | intl_analysis.global_tcc_to_new_conversion_aging_lv | 逻辑视图 | 实时 | TCC转新签转化周期/时长分析 |
| 订单/GMV/转化 | 全球 | intl_analysis.vk_sr_intl_gl_gmv_achievement_lv | 逻辑视图 | 实时 | GMV达成与目标追踪 |
| 订单/GMV/转化 | 沙特 | intl_analysis.vk_sr_intl_sa_leads_to_order_details_lv | 逻辑视图 | 实时 | 线索到订单转化明细 |
| 付费/留存/续费 | 全球 | intl_analysis.global_paid_user_analysis_lv | 逻辑视图 | 实时 | 付费用户分析 |
| 付费/留存/续费 | 全球 | intl_analysis.vk_sr_intl_gl_paid_user_retention_lv | 逻辑视图 | 实时 | 付费用户留存 |
| 付费/留存/续费 | 全球 | intl_analysis.vk_sr_intl_gl_renewal_target_tracking_analysis_lv | 逻辑视图 | 实时 | 续费目标追踪与达成分析 |
| 付费/留存/续费 | 沙特 | intl_analysis.vk_sr_intl_sa_fixed_course_consumption_analysis_lv | 逻辑视图 | 实时 | 固定课消耗/续费相关分析 |
| 市场投放/花费 | 全球 | intl_analysis.vk_sr_intl_gl_marketing_spend_daily_lv | 逻辑视图 | 实时 | 全球投放日花费 |
| 市场投放/花费 | 沙特 | intl_analysis.vk_sr_intl_sa_marketing_spend_daily_lv | 逻辑视图 | 实时 | 沙特投放日花费 |
| 市场投放/花费 | 韩国 | intl_analysis.vk_sr_intl_kr_marketing_spend_daily_lv | 逻辑视图 | 实时 | 韩国投放日花费 |
| 市场投放/花费 | 沙特 | intl_analysis.vk_sr_intl_sa_marketing_spend_7d_roas_lv | 逻辑视图 | 实时 | 7日ROAS/花费效率 |
| 市场投放/花费 | 沙特 | intl_analysis.vk_sr_intl_sa_marketing_spend_mtd_roas_lv | 逻辑视图 | 实时 | MTD ROAS/花费效率 |
| 市场投放/花费 | 沙特 | intl_analysis.vk_sr_intl_sa_marketing_spend_ytd_roas_lv | 逻辑视图 | 实时 | YTD ROAS/花费效率 |
| 广告表现/素材 | 韩国 | intl_analysis.vk_sr_intl_kr_marketing_campaign_performance_lv | 逻辑视图 | 实时 | 韩国投放活动表现 |
| 广告表现/素材 | 沙特 | intl_analysis.vk_sr_intl_sa_marketing_campaign_performance_lv | 逻辑视图 | 实时 | 沙特投放活动表现 |
| 广告表现/素材 | 沙特 | intl_analysis.vk_sr_intl_sa_marketing_creative_performance_agg_lv | 逻辑视图 | 实时 | 素材/创意表现汇总 |
| 广告表现/素材 | 沙特 | intl_analysis.vk_sr_intl_sa_meta_snap_ads_daily_agg_lv | 逻辑视图 | 实时 | Meta/Snap 广告日汇总 |
| 线索/LP/渠道 | 韩国 | intl_analysis.korea_cc_lp_allocation_lv | 逻辑视图 | 实时 | 韩国CC-LP线索分配 |
| 线索/LP/渠道 | 全球 | intl_analysis.vk_sr_intl_gl_leads_channel_analysis_follow_record_lv | 逻辑视图 | 实时 | 线索渠道跟进记录 |
| 线索/LP/渠道 | 全球 | intl_analysis.vk_sr_intl_cclp_service_follow_detail_lv_lv | 逻辑视图 | 实时 | CC-LP 服务跟进明细 |
| 线索/LP/渠道 | 全球 | intl_analysis.vk_sr_intl_gl_lp_service_node_follow_lv | 逻辑视图 | 实时 | LP 服务节点跟进 |
| 线索/LP/渠道 | 沙特 | intl_analysis.vk_sr_intl_sa_lp_performance_evaluation_details_mtd_lv | 逻辑视图 | 实时 | LP 人效/绩效评估（月度） |
| 线索/LP/渠道 | 沙特 | intl_analysis.vk_sr_intl_sa_leads_staff_relation_record_lv | 逻辑视图 | 实时 | 线索-人员关系记录 |
| 线索/LP/渠道 | 沙特 | intl_analysis.vk_sr_intl_sa_trial_contact_summary_lv | 逻辑视图 | 实时 | 试听触达/跟进汇总 |
| 课堂/课程 | 沙特 | intl_analysis.vk_sr_intl_sa_class_detail_lv_lv | 逻辑视图 | 实时 | 沙特课堂明细 |
| 课堂/课程 | Lingobus | intl_analysis.vk_intl_lingobus_teacher_slot_opening_lv | 逻辑视图 | 实时 | Lingobus 老师排课/开班 |
| 用户/画像/标签 | 全球 | intl_analysis.vk_global_parent_login_record_lv | 逻辑视图 | 实时 | 家长登录记录分析 |
| 用户/画像/标签 | Lingobus | intl_analysis.vk_sr_intl_lingobus_parent_tag_lv | 逻辑视图 | 实时 | Lingobus 家长标签 |
| 用户/画像/标签 | Lingobus | intl_analysis.vk_sr_intl_lingobus_user_follow_tag_lv | 逻辑视图 | 实时 | 用户跟进标签 |
| 设备/位置 | 全球 | intl_analysis.vk_sr_intl_gl_class_devices_analysis_lv | 逻辑视图 | 实时 | 上课设备/端分布 |
| 注册/增长 | 中国 | intl_analysis.vk_sr_cn_student_registration_cohort_analysis_lv | 逻辑视图 | 实时 | 学生注册 cohort |
| 外呼/通话 | 全球 | intl_analysis.vk_sr_intl_gl_calling_data_lv | 逻辑视图 | 实时 | 外呼明细数据 |
| 外呼/通话 | 全球 | intl_analysis.vk_sr_intl_gl_calling_metrics_staff_lv | 逻辑视图 | 实时 | 外呼人效指标 |
| 销售质检 | 沙特 | intl_analysis.vk_sr_intl_sa_cc_quality_monitor_lv | 逻辑视图 | 实时 | CC 质检监控 |
| 销售质检 | 沙特 | intl_analysis.vk_sr_intl_sa_cc_quality_monitor_today_lv | 逻辑视图 | 实时 | CC 质检（当日） |
| 销售质检 | 沙特 | intl_analysis.vk_sr_intl_sa_cc_quality_monitor_all_lv | 逻辑视图 | 实时 | CC 质检（全量） |
| 机器人销售 | 沙特 | intl_analysis.vk_sr_intl_sa_robot_sales_tcc_call_monitor_lv | 逻辑视图 | 实时 | 机器人TCC通话监控 |
| 机器人销售 | 沙特 | intl_analysis.vk_sr_intl_sa_robot_sales_tcc_call_monitor_cc_lv | 逻辑视图 | 实时 | 机器人TCC通话（CC维度） |
| 机器人销售 | 沙特 | intl_analysis.vk_sr_intl_sa_robot_sales_order_broadcast_lv | 逻辑视图 | 实时 | 机器人销售订单播报 |
| 机器人销售 | 沙特 | intl_analysis.vk_sr_intl_sa_robot_sales_order_broadcast_renew_lv | 逻辑视图 | 实时 | 机器人续费订单播报 |
| 渠道/归因 | 沙特 | intl_analysis.vk_sr_intl_sa_app_adjust_analysis_lv | 逻辑视图 | 实时 | App Adjust 渠道/归因 |

### 核心表

| 主题域 | 表名 | 表类型 | 更新频率 | 用途 |
| --- | --- | --- | --- | --- |
| 家长 | bi_analysis.bi_analysis_parent_tag_gl_lv | 逻辑视图 | 实时查询 | 家长标签/画像分析 |
| 付费家长 | intl_analysis.global_paid_user_analysis_lv | 逻辑视图 | 实时 | 付费家长分析 |
| 课程 | vk_intl_dw.vk_intl_dw_evt_online_class_analyse_gl_mv | 物化视图模型表 | 实时(10 mins) | 线上课程分析 |
| 订单 | vk_intl_dw.vk_intl_dw_evt_pack_order_analyse_gl_mv | 物化视图模型表 | 实时(10 mins) | 订单分析 |

### 拓展表

| 主题域 | 表名 | 表类型 | 更新频率 | 用途 |
| --- | --- | --- | --- | --- |
| 学生 | vk_intl_dw.vk_intl_dw_pty_student_info_da | 离线模型表 | T+1 | 学生信息 |
| 渠道归属表 | intl_analysis.vk_gl_marketing_channel_mapping_relation | 钉钉在线表格 | T+1 (Bi-daily) | 渠道归属映射 |
| 韩国历史广告花销 | intl_analysis.vk_kr_marketing_spending_history_manual | 离线数据 | T+1 | 韩国历史广告花销 |
| 韩国手动广告花销 | intl_analysis.vk_kr_marketing_spending_manual | 钉钉在线表格 | T+1(Monthly) | 韩国手动广告花销 |

### 离线快照表（用于回溯历史状态）

| 主题域 | 表名 | 表类型 | 更新频率 | 用途 |
| --- | --- | --- | --- | --- |
| 付费家长快照表 | intl_analysis.global_paid_user_analysis_lv_his | 离线快照表 | T+1 | 付费家长历史快照 |
| 约旦销售质量快照 | intl_analysis.vk_sr_intl_sa_cc_quality_monitor_da | 离线快照表 | T+1 | 约旦销售质量监控快照 |
| Lingobus付费快照 | intl_analysis.vk_sr_intl_lingobus_paid_user_analysis_da | 离线快照表 | T+1 | Lingobus 付费快照 |

### 广告账号素材级别更新（离线数据，自动任务 T+1）

| 主题域 | 表名 | 表类型 | 更新频率 | 用途 |
| --- | --- | --- | --- | --- |
| 广告投放 | vk_intl_dwd_evt_gl_snapchat_report_di | 离线明细表 | T+1 | Snapchat 广告报表 |
| 广告投放 | vk_intl_dwd_evt_gl_tiktok_report_di | 离线明细表 | T+1 | TikTok 广告报表 |
| 广告投放 | vk_intl_dwd_evt_gl_twitter_report_di | 离线明细表 | T+1 | Twitter 广告报表 |
| 广告投放 | vk_intl_dwd_evt_google_report_di | 离线明细表 | T+1 | Google 广告报表 |
| 广告投放 | vk_intl_dwd_evt_kr_naver_report_di | 离线明细表 | T+1 | Naver 广告报表 |
| 广告投放 | vk_intl_dwd_evt_gl_meta_report_di | 离线明细表 | T+1 | Meta 广告报表 |
| 广告投放 | vk_intl_dwd_evt_gl_apple_asa_report_rt | 离线明细表 | T+1 | Apple ASA 广告报表（StarRocks 直接同步表，业务线在 python 脚本中维护） |

---

## 默认汇率（如未提供字段则使用常量）
- KRW/USD = 1420
- AED/USD = 3.67
- SAR/USD = 3.75

---

## 字段命名规则

- 口径中的字段统一使用数据库字段命名（小写 + 下划线）。
- 若来源公式为 `Type Eng` 这种形式，对应数据库字段为 `type_eng`。

---

## 订单表口径

**表名**: `vk_intl_dw.vk_intl_dw_evt_pack_order_analyse_gl_mv`

### 订单表字段说明（口径前置）

**关键字段说明（口径相关）**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| order_num | varchar | 订单号 |
| type_eng | varchar | 订单类型英文（如 Paid_Order） |
| customer_type_eng | varchar | 客户类型英文（New_Order / Renew_Order） |
| order_status_eng | varchar | 订单状态英文（如 refund_completed） |
| order_status_cn | varchar | 订单状态中文 |
| deal_price | decimal | 成交金额（原币） |
| paid_time | datetime | 支付时间（北京时间） |
| paid_date_country | varchar | 支付日期（当地日期，YYYY-MM-DD，无时间） |
| business_line | varchar | 业务线（如 kr/ae/sa） |
| bus_id | varchar | 业务站点/渠道标识（如 kr/k2/sa） |
| currency | varchar | 币种 |
| pay_method_eng | varchar | 支付方式英文 |
| inventory_type | varchar | 课时包类型（TRIAL/MAJOR/GROUP_MAJOR） |
| course_type | varchar | 课程类型（TRIAL/MAJOR/OVERSEAS 等） |
| if_trial | tinyint | 是否试听订单（1=试听） |
| refundable | smallint | 是否可退（1=可退） |
| refund_time | datetime | 退费时间 |
| refund_price | decimal | 退费金额（原币） |
| first_paid_order | tinyint | 是否首购订单标记 |
| second_renew_order | tinyint | 是否二次续费订单标记 |
| first_refund_order | tinyint | 是否首退订单标记 |
| if_all_refund | tinyint | 是否全额退费标记 |

**字段枚举值清单（低基数）**

| 字段 | 类型 | 枚举值(去重/限200) |
| --- | --- | --- |
| order_source | smallint | 1, 61, 10, 2, 11, 12, 6, 7, 30, 9, 3, 5, 8, 4 |
| order_source_cn | varchar(1048576) | Leads代下单, 用户自行下单, 客服下单, 自动续费-系统, 活动赠送, 系统赠单, 推荐赠单, 兑换, 服务赠送, 自动续费-自主, 迁移课时（有有效期）, 抖音, 线下收款, 对公 |
| order_source_eng | varchar(1048576) | REDEEM, OFFLINE, TOB, ACTIVITY, CUSTOMER_SERVICE_ORDER, SELF, LEADS_SERVICE_ORDER, RENEWAL_SYS, REFERRAL, SERVICE_EXPIRE, RENEWAL, SYSTEM, DOU_YIN, SERVICE |
| customer_type | varchar(1048576) | null, 新签单, 续费单 |
| customer_type_eng | varchar(1048576) | null, Renew_Order, New_Order |
| order_status_num | smallint | 9, 7, 0, 3, 4, 10, 2, 11, 12, 1 |
| order_status_eng | varchar(1048576) | closed, in_refund, refund_completed, to_be_paid, in_payment, payment_incompleted, expired, created, in_renewal_payment, payment_completed |
| order_status_cn | varchar(1048576) | 已关闭, 待支付, 退费完成, 支付未完成, 支付完成, 退费中, 自动续费支付中, 新创建, 支付中, 已过期 |
| type | varchar(1048576) | 赠送单, 兑换单, 迁移单, 付费单, 小额付费单 |
| type_eng | varchar(1048576) | Migration_Order, Paid_Order, Exchange_Order, Gift_Order, Promotional_Orders |
| inventory_type | varchar(1048576) | TRIAL, MAJOR, GROUP_MAJOR |
| student_type | tinyint | 0, 1 |
| rebated | smallint | 0, 1 |
| refundable | smallint | 0, 1 |
| pay_method | smallint | 15, 21, 2, 11, 12, 1, 0, 22, 8, 5, 3, 20, 14, 6, 23, 4, 16, 7 |
| pay_method_eng | varchar(1048576) | AIRWALLEX_KAKAO, Redeem, WECHAT, STRIPE_CARD, AIRWALLEX_LOCAL_CARD, ALIPAY, Offline, AIRWALLEX_CARD, TRANSFER, OFFLINE, AIRWALLEX_SAMSUNGPAY, PayLetter, AIRWALLEX_NAVERPAY, FREE, APPLE_PAY, AIRWALLEX_PAYCO, PayPal, CARD, TABBY, Free, TAMARA |
| currency | varchar(1048576) | SAR, AED, , KRW, USD, BHD |
| pay_status | smallint | 1, 0, 3 |
| device_type | varchar(1048576) | PC_APP, ANDROID APP, H5, , PC |
| signature_type | smallint | 1, 2, 0, 3 |
| signature_type_cn | varchar(1048576) | 无归属, 补差, 续费, 新签 |
| signature_type_en | varchar(1048576) | Unassigned, New, Renew, Makeup |
| course_mode | varchar(1048576) | ONE_TO_MANY, ONE_ON_ONE |
| course_type | varchar(1048576) | TRIAL, MAJOR, OVERSEAS, OPEN2, AI_OVERSEAS, OPEN1 |
| bus_id | varchar(1048576) | sa, ae, kr, us, ls, k2 |
| order_type | smallint | 0, 2, 1 |
| business_line | varchar(1048576) | sa, us, ae, kr, ls |
| if_trial | tinyint | 0, 1 |
| first_paid_order | tinyint | 1 |
| last_paid_order | tinyint | 1 |
| second_renew_order | tinyint | 1 |
| first_refund_order | tinyint | 1 |
| last_refund_order | tinyint | 1 |
| if_all_refund | tinyint | 0, 1 |
| first_gifted | tinyint | 1 |
| first_emigration | tinyint | 1 |
| parent_status | varchar(1048576) | TEST, NORMAL, CANCEL |
| remittance_flag | tinyint | 0, 1 |

**说明**
- 枚举值来自 `SELECT DISTINCT` 抽样（每字段最多 200 条），用于口径理解与筛选参考。
- 高基数字段（如订单号、唯一键、姓名等）不在此枚举清单中。
- 韩国站有新旧站区分：`business_line` 仅为 `kr`，但 `bus_id` 存在 `kr`（老站，`deal_price` 为 USD）与 `k2`（新站，`deal_price` 为 KRW）。GMV 口径需按 `bus_id` 区分币种。

**字段含义补充**
- `type_eng`:
  - `Migration_Order`：韩国站特有，老站迁移到新站的订单
  - `Paid_Order`：付费单（唯一口径）
  - `Gift_Order`：赠送单
  - `Promotional_Orders`：小额付费单（沙特也会定义为定金单）
- `customer_type_eng`:
  - `New_Order`：新签
  - `Renew_Order`：续费

**type_eng 判定口径（底层逻辑摘要）**
- `Gift_Order`：`order_source` ∈ (2,3,5,6)，且 `order_status` ∈ (4,5,6,7,8,9)，`order_type` ∈ (0,1)，`student_type`=1，且 `pay_time` 非空
- `Exchange_Order`：`order_source` ∈ (9,13)，且 `order_status` ∈ (4,5,6,7,8,9)，`order_type` ∈ (0,1)，`student_type`=1，且 `pay_time` 非空
- `Migration_Order`：`order_source` ∈ (61,62)，且 `order_status` ∈ (4,5,6,7,8,9)，`order_type` ∈ (0,1)，`student_type`=1，且 `pay_time` 非空
- `Paid_Order` / `Promotional_Orders`：`order_source` 不在 (2,3,5,6,9,13,61,62)，且 `order_status` ∈ (4,5,6,7,8,9)，`order_type` ∈ (0,1)，`student_type`=1，且 `pay_time` 非空；再按 `bus_id` + `origin_price` 阈值区分
  - `bus_id` = 'kr'：`origin_price` ≥ 100 → Paid_Order；0 < `origin_price` < 100 → Promotional_Orders
  - `bus_id` = 'k2'：`origin_price` ≥ 100000 → Paid_Order；0 < `origin_price` < 100000 → Promotional_Orders
  - `bus_id` = 'ae'/'ts'/'hk'/'us'/'tl'：`origin_price` ≥ 100 → Paid_Order；0 < `origin_price` < 100 → Promotional_Orders
  - `bus_id` = 'sa'/'ls'：`origin_price` ≥ 375 → Paid_Order；0 < `origin_price` < 375 → Promotional_Orders

**Paid_Order 覆盖的订单状态**
- `payment_completed` / `refund_initiate` / `refund_rejected` / `in_refund` / `refund_cancel` / `refund_completed`

**GMV 口径提醒**
- 业务通常在看 GMV 达成时忽略退费金额，仅关注总 GMV。
- 默认口径请提示“GMV 含退费金额”；只有在明确讨论“退费”时才单独标注或剔除。

### 时间字段与时区规则

- `paid_time` 为北京时间（Asia/Shanghai）。
- `paid_date_country` 为当地日期（仅年月日，无时间）。
- 计算涉及当地时间时，默认将 `paid_time` 转换为当地时区：
  - `business_line = 'kr'` → 韩国首尔时间（Asia/Seoul）
  - `business_line = 'sa'` → 沙特利雅得时间（Asia/Riyadh）
  - `business_line = 'ae'` → 阿联酋迪拜时间（Asia/Dubai）
- 若口径涉及“销售转化”且有特殊说明，则 `business_line = 'sa'` 使用约旦时间（Asia/Amman），其余仍按利雅得时间处理。
- 时区转换函数示例：
  ```sql
  CONVERT_TZ(paid_time, 'Asia/Shanghai', 'Asia/Seoul')
  ```

### 口径 1: New Orders

**SQL 口径（StarRocks）**
```sql
COUNT(
  CASE
    WHEN type_eng = 'Paid_Order'
     AND customer_type_eng = 'New_Order'
    THEN order_num
  END
) AS new_orders
```

**说明**
- `COUNT` 统计非空行数，与 Tableau 语义一致（不做去重）。

---

### 口径 2: $ New GMV USD

**SQL 口径（StarRocks）**
```sql
SUM(
  CASE
    WHEN type_eng = 'Paid_Order'
     AND customer_type_eng = 'New_Order'
    THEN
      CASE
        WHEN business_line = 'kr' THEN
          CASE
            WHEN bus_id = 'kr' THEN deal_price
            WHEN bus_id = 'k2' THEN deal_price / 1420
          END
        WHEN business_line = 'ae' THEN deal_price / 3.67
        WHEN business_line = 'sa' THEN deal_price / 3.75
      END
  END
) AS new_gmv_usd
```

**说明**
- 汇率默认使用常量：KRW/USD=1420，AED/USD=3.67，SAR/USD=3.75。
- 若 `Business Line` 非 kr/ae/sa 或汇率条件不满足，返回 `NULL`，不计入 `SUM`。

---

### 口径 3: Renew Orders（续费单量）

**SQL 口径（StarRocks）**
```sql
COUNT(
  CASE
    WHEN type_eng = 'Paid_Order'
     AND customer_type_eng = 'Renew_Order'
    THEN order_num
  END
) AS renew_orders
```

**说明**
- `COUNT` 统计非空行数，与 Tableau 语义一致（不做去重）。

---

### 口径 4: $ Renew GMV USD（续费 GMV）

**SQL 口径（StarRocks）**
```sql
SUM(
  CASE
    WHEN type_eng = 'Paid_Order'
     AND customer_type_eng = 'Renew_Order'
    THEN
      CASE
        WHEN business_line = 'kr' THEN
          CASE
            WHEN bus_id = 'kr' THEN deal_price
            WHEN bus_id = 'k2' THEN deal_price / 1420
          END
        WHEN business_line = 'ae' THEN deal_price / 3.67
        WHEN business_line = 'sa' THEN deal_price / 3.75
      END
  END
) AS renew_gmv_usd
```

**说明**
- 汇率默认使用常量：KRW/USD=1420，AED/USD=3.67，SAR/USD=3.75。
- 若 `business_line` 非 kr/ae/sa 或汇率条件不满足，返回 `NULL`，不计入 `SUM`。

---

### 口径 5: Refunded Orders（退费单量）

**SQL 口径（StarRocks）**
```sql
COUNT(
  CASE
    WHEN type_eng = 'Paid_Order'
     AND order_status_eng = 'refund_completed'
    THEN order_num
  END
) AS refunded_orders
```

**说明**
- `COUNT` 统计非空行数，与 Tableau 语义一致（不做去重）。

---

### 口径 6: $ Refunded GMV USD（退费 GMV）

**SQL 口径（StarRocks）**
```sql
SUM(
  CASE
    WHEN type_eng = 'Paid_Order'
     AND order_status_eng IN ('in_refund', 'refund_completed')
    THEN
      CASE
        WHEN business_line = 'kr' THEN
          CASE
            WHEN bus_id = 'kr' THEN deal_price
            WHEN bus_id = 'k2' THEN deal_price / 1420
          END
        WHEN business_line = 'ae' THEN deal_price / 3.67
        WHEN business_line = 'sa' THEN deal_price / 3.75
      END
  END
) AS refunded_gmv_usd
```

**说明**
- 汇率默认使用常量：KRW/USD=1420，AED/USD=3.67，SAR/USD=3.75。
- 若 `business_line` 非 kr/ae/sa 或汇率条件不满足，返回 `NULL`，不计入 `SUM`。

---

## 课程表口径

**表名**: `vk_intl_dw.vk_intl_dw_evt_online_class_analyse_gl_mv`

### 课程状态标准化（trial_class_status_std）

**SQL 口径（StarRocks）**
```sql
CASE
  WHEN student_class_status IS NULL
       OR TRIM(student_class_status) = '' THEN 'Upcoming Class'
  ELSE
    CASE student_class_status
      WHEN 'COMPLETED'           THEN 'Completed'
      WHEN 'STUDENT_NO_SHOW'     THEN 'Student No Show'
      WHEN 'STUDENT_IT_PROBLEM'  THEN 'Student IT Problem'
      WHEN 'TEACHER_CANCEL_2H'       THEN 'Teacher Hard Cancel'
      WHEN 'TEACHER_CANCEL_2H_8H'    THEN 'Teacher Hard Cancel'
      WHEN 'TEACHER_CANCEL_8H'       THEN 'Teacher Hard Cancel'
      WHEN 'TEACHER_CANCEL_8H_24H'   THEN 'Teacher Hard Cancel'
      WHEN 'TEACHER_NO_SHOW'     THEN 'Teacher No Show'
      WHEN 'TEACHER_IT_PROBLEM'  THEN 'Teacher IT Problem'
      WHEN 'TEACHER_CANCEL_24H'  THEN 'Teacher Soft Cancel'
      WHEN 'SYSTEM_PROBLEM'      THEN 'System Problem'
      ELSE
        CASE
          WHEN class_status = 'CANCELED' THEN
            CASE
              WHEN CAST(consume_inventory AS INT) = 1 THEN 'Student Hard Cancel'
              WHEN CAST(consume_inventory AS INT) = 0 THEN 'Student Soft Cancel'
              ELSE 'CANCELED'
            END
          ELSE student_class_status
        END
    END
END AS trial_class_status_std
```

**说明**
- 保持原逻辑：空状态视为 Upcoming Class。
- 取消类状态根据 `class_status` 和 `consume_inventory` 进一步细分。

---

### 时间字段与时区规则

- `book_time`（约课时间）为北京时间（Asia/Shanghai）。
- `scheduled_date_time`（预约上课时间）为北京时间（Asia/Shanghai）。
- 使用时若需当地时间，请按订单表的时区规则转换（参考“订单表口径”中的规则）。
- 示例：
  ```sql
  CONVERT_TZ(book_time, 'Asia/Shanghai', 'Asia/Seoul')
  ```

### 口径 1: Major Consumption

**SQL 口径（StarRocks）**
```sql
SUM(
  CASE
    WHEN course_type <> 'TRIAL'
     AND consume_inventory = 1
    THEN consumenum
  END
) AS major_consumption
```

**说明**
- 仅统计非试听课程（`course_type <> 'TRIAL'`）且 `consume_inventory = 1` 的消耗课时。

---

### 口径 2: Major Parents

**SQL 口径（StarRocks）**
```sql
COUNT(
  DISTINCT CASE
    WHEN course_type <> 'TRIAL'
    THEN parent_id
  END
) AS major_parents
```

**说明**
- `COUNT DISTINCT` 统计非试听课程的家长数。

---

### 口径 3: Trial Class Damaged

**SQL 口径（StarRocks）**
```sql
COUNT(
  DISTINCT CASE
    WHEN course_type = 'TRIAL'
     AND trial_class_status_std IN (
       'Student IT Problem',
       'Student No Show',
       'Student Hard Cancel'
     )
    THEN code
  END
) AS trial_class_damaged
```

**说明**
- `Class Status` 需先按 `trial_class_status_std` 标准化后再计算。
