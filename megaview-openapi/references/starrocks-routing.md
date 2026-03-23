# StarRocks Metric Routing

Read this file when the task touches StarRocks metric selection, non-default sales tables, field interpretation, or when the user references the warehouse metric document directly.

Prefer reading `data/data_warehouse_metric_manual.md` first when the question is about Saudi `leads-to-order`, trial completion, order SQL metrics, LP, TCC, marketing, or course SQL definitions.

## Two sources of truth

Treat the bundled StarRocks materials as two different layers:

1. Metric-definition layer:
   - `data/国际站全部物化视图_指标字段口径梳理_2026-03-11.md`
   - this explains the warehouse-source metric definitions and the intended business meaning
   - many names in that document use `vk_intl_dw_*_mv` / `*_lv`
2. Live-query layer:
   - the current verified StarRocks database is `intl_analysis`
   - the currently visible reporting objects are mainly `vk_sr_intl_*_lv` and `vk_sr_intl_*_da`
   - do not assume every documented `vk_intl_dw_*_mv` name can be queried directly in the live database

Current scope:

- this skill is currently scoped to `intl_analysis` only
- if the user asks for another StarRocks database, say that the current skill scope is limited to `intl_analysis` first

Driver rule:

- `intl_analysis` is the primary business driver for seller scope, ranking, and metric selection
- for broad growth questions, start from the Saudi `leads-to-order` perspective first
- Megaview is the explanation and coaching layer used after the seller question is defined

## Current verified defaults

For seller-level review, the current verified snapshot anchor remains:

- database: `intl_analysis`
- table: `vk_sr_intl_sa_cc_quality_monitor_da`
- join field: `staff_name`
- join key from `employees.json`: `staffName`
- time field: `pt`
- default metric expression: `SUM(total_new_gmv_usd)`

Verified useful fields on this table include:

- `staff_name`
- `business_line`
- `pt`
- `total_new_gmv_usd`
- `total_new_order`
- `total_calls`
- `connected_calls`
- `no_answer_calls`
- `total_duration`
- `avg_duration_sec`
- `avg_duration_min`
- `connect_rate`

Use this table first when the user asks for:

- employee performance review
- seller ranking
- Megaview score vs GMV comparison
- call volume / call connection quality / GMV in one view

Important aggregation note:

- `total_new_gmv_usd`, `total_new_order`, `total_calls`, `connected_calls`, `no_answer_calls`, and `total_duration` can usually be summed across a date range
- `connect_rate` and `avg_duration_*` are already derived metrics; for multi-day aggregation, prefer recomputing from base counts if possible instead of blindly averaging daily ratios

Important freshness note:

- `vk_sr_intl_sa_cc_quality_monitor_da` is a T+1 snapshot anchor, suitable for stable review and historical comparison
- when the user clearly wants a more live Saudi seller view, prefer:
  - `vk_sr_intl_sa_cc_quality_monitor_lv`
  - `vk_sr_intl_sa_cc_quality_monitor_today_lv`
  - `vk_sr_intl_sa_cc_quality_monitor_all_lv`

## Employee master and active scope

For employee performance analysis, define the employee scope from StarRocks before using Megaview mappings:

- primary employee master table: `vk_gl_leads_staff_team_assignment_relation`
- active rule: `termination_date is null`
- inactive rule: `termination_date is not null`
- use this table to decide whether a seller should stay in the default active performance-review pool
- use `data/employees.json` after that step to map the chosen seller into Megaview `origin_user_id`
- if the user explicitly asks about a departed seller, keep the output as historical review rather than mixing that seller into the default active review ranking

## Saudi growth-chain backbone

When the question is broad and growth-oriented, start from these tables in order:

1. Saudi leads-to-order conversion:
   - `vk_sr_intl_sa_leads_to_order_details_lv`
2. Saudi LP performance:
   - `vk_sr_intl_sa_lp_performance_evaluation_details_mtd_lv`
3. Saudi trial completion and post-trial follow-up:
   - `vk_sr_intl_sa_leads_to_order_details_lv`
   - `vk_sr_intl_sa_trial_contact_summary_lv`
4. Saudi marketing / ROAS:
   - `vk_sr_intl_sa_marketing_spend_daily_lv`
   - `vk_sr_intl_sa_marketing_spend_7d_roas_lv`
   - `vk_sr_intl_sa_marketing_spend_mtd_roas_lv`
   - `vk_sr_intl_sa_marketing_spend_ytd_roas_lv`
5. Saudi or global channel / assignment context:
   - `vk_sr_intl_sa_leads_staff_relation_record_lv`
   - `vk_sr_intl_gl_leads_channel_analysis_follow_record_lv`
6. TCC aging:
   - `global_tcc_to_new_conversion_aging_lv`

Use Megaview only after one of these tables identifies the seller, team, or stage that needs explanation.

## Theme-to-table routing

### 1. Seller daily quality and GMV

Prefer:

- `vk_sr_intl_sa_cc_quality_monitor_da`

Use when the user wants:

- seller-level GMV
- new-order count
- total calls / connected calls
- connection efficiency
- one table that can be joined to Megaview employee names directly

### 1.5 Saudi leads-to-order conversion

Prefer:

- `vk_sr_intl_sa_leads_to_order_details_lv`

Use when the user wants:

- Saudi lead-to-order conversion
- seller or team conversion from lead to first paid order
- channel-to-order handoff by seller
- LP / trial-completed / follow-up timing impact on final payment

Verified useful fields include:

- seller and team:
  - `last_ccid`
  - `last_ccid_name`
  - `last_cc_tl_name`
  - `last_lpid`
  - `last_lpid_name`
- channel:
  - `mkt_channel_name`
  - `channel_level_one`
  - `channel_level_two`
  - `channel_level_three`
- conversion:
  - `paid_flag`
  - `first_order_deal_price`
  - `first_pay_time_jordan`
  - `leads_quality`
  - `user_hold_status`
- follow-up timing:
  - `register_first_follow_diff_hour`
  - `register_first_follow_time_category`
  - `first_trial_completed_follow_time_jordan`
  - `first_trial_completed_schedule_follow_time_diff_hour`
  - `first_trial_problematic_follow_time_jordan`
- calling:
  - `outbound_call_count`
  - `valid_call_count`
  - `total_call_duration_minutes`

Use this table as the default Saudi growth-chain entry point.

### 1.6 Saudi LP performance

Prefer:

- `vk_sr_intl_sa_lp_performance_evaluation_details_mtd_lv`

Use when the user wants:

- LP productivity
- LP service load
- LP consumption and renewal outcomes

Verified useful fields include:

- `last_lpid_name`
- `active_parent_num`
- `served_parent_num`
- `curr_month_major_as_parent_num`
- `total_actual_consumption`
- `total_plan_consumption`
- `renewal_commission_SAR`

### 1.7 Saudi trial completion, trial contact, and TCC

Prefer:

- `vk_sr_intl_sa_trial_contact_summary_lv`
- `global_tcc_to_new_conversion_aging_lv`

Use when the user wants:

- whether the trial was completed and how fast post-trial follow-up happened
- trial-contact quality before or after class
- TCC to new-sign conversion time
- seller-level trial follow-up quality

Verified useful fields include:

- from `vk_sr_intl_sa_trial_contact_summary_lv`:
  - `last_ccid_name`
  - `trial_student_class_status`
  - `class_status_description`
  - `pre_contact`
  - `pre_connect_15s`
  - `post_contact`
  - `post_connect_15s`
  - `paid_flag`
  - `first_paid_time_jordan`
- from `global_tcc_to_new_conversion_aging_lv`:
  - `last_ccid_name`
  - `last_cc_tl_name`
  - `mkt_channel_name`
  - `deal_price`
  - `last_paid_time`
  - `time_difference_days`

### 1.8 Saudi marketing and ROAS

Prefer:

- `vk_sr_intl_sa_marketing_spend_daily_lv`
- `vk_sr_intl_sa_marketing_spend_7d_roas_lv`
- `vk_sr_intl_sa_marketing_spend_mtd_roas_lv`
- `vk_sr_intl_sa_marketing_spend_ytd_roas_lv`

Use when the user wants:

- Saudi channel spend
- ROAS by channel
- acquisition efficiency before sales handoff

Verified useful fields include:

- from spend daily:
  - `date`
  - `mkt_channel_name`
  - `spend`
  - `bus_id`
- from 7d ROAS:
  - `mkt_channel_name`
  - `register_date`
  - `total_registered_parent`
  - `total_trial_parents_booked_cohort`
  - `total_new_order_noncohort`
  - `total_new_gmv_usd_noncohort`
  - `aov_usd_noncohort`
  - `cac_usd_noncohort`
  - `cpl_usd_noncohort`
  - `roas_noncohort`

### 2. Order-level revenue, refund, and inventory analysis

The warehouse document's order-analysis MVs map conceptually to live order-detail reporting tables such as:

- `vk_sr_intl_ae_order_detail_lv`
- `vk_sr_intl_kr_order_detail_lv`

Verified fields from `vk_sr_intl_ae_order_detail_lv` include:

- join candidates:
  - `order_given_staff_name`
  - `order_given_staff_id`
- time fields:
  - `pay_time`
  - `refund_time`
  - `confirm_time`
  - `create_time`
- business fields:
  - `deal_price`
  - `refund_price`
  - `bus_id`
  - `inventory_quantity`
  - `consumed_quantity`
  - `available_quantity`
  - `unavailable_quantity`
  - `parent_id`

Use this route when the user asks for:

- paid amount / refund amount
- inventory consumption or remaining sessions
- new vs renewal order analysis
- order-detail analysis by region or salesperson

Do not keep using `vk_sr_intl_sa_cc_quality_monitor_da` if the user clearly wants order-detail metrics.

### 3. Class consumption, attendance, and teacher feedback

The warehouse document's online-class analysis maps conceptually to live class-consumption tables such as:

- `vk_sr_intl_ae_class_consumption_detail_lv`
- `vk_sr_intl_kr_class_consumption_detail_lv`

Verified fields from `vk_sr_intl_ae_class_consumption_detail_lv` include:

- identifiers:
  - `teacher_id`
  - `student_id`
  - `parent_id`
- business fields:
  - `course_type`
  - `student_class_status`
  - `consume_inventory`
  - `consumed_inventory`
  - `parent_to_teacher_score`
- time fields:
  - `book_time`
  - `schedule_time`
  - `open_time`
  - `student_enter_time`
  - `teacher_enter_time`
  - `parent_feedback_time`
  - `homework_start_time`
  - `homework_completed_time`

Use this route when the user asks for:

- class attendance
- consumption details
- class completion / no-show style analysis
- parent feedback tied to classes

### 4. Student learning performance

The warehouse document's learning-detail model maps conceptually to live learning-performance tables such as:

- `vk_sr_intl_sa_student_learning_performance_lv`
- `vk_sr_intl_ae_student_learning_performance_lv`
- `vk_sr_intl_kr_student_learning_performance_lv`

Verified fields from `vk_sr_intl_sa_student_learning_performance_lv` include:

- `teacher_id`
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

Use this route when the user asks for:

- student learning quality
- UA score / homework completion
- parent feedback to teacher or courseware
- pre-class video usage

### 5. Region or portfolio GMV achievement

Use:

- `vk_sr_intl_gl_gmv_achievement_lv`

Verified fields include:

- dimensions:
  - `bus_id`
  - `business_line_name`
  - `product_line`
- metrics:
  - `yday_new_gmv_usd`
  - `yday_renew_gmv_usd`
  - `yday_total_gmv_usd`
  - `today_new_gmv_usd`
  - `today_total_gmv_usd`
  - `mtd_new_gmv_usd`
  - `mtd_renew_gmv_usd`
  - `mtd_total_gmv_usd`
  - matching target and achievement-rate fields

Use this route when the user asks for:

- region-level GMV target achievement
- today / yesterday / MTD GMV dashboards
- business-line or product-line performance

Do not use this table for seller-level joins with `employees.json`.

## Querying rules

1. If the user asks a normal employee-performance question, use the bundled default config first.
2. For employee review, check `vk_gl_leads_staff_team_assignment_relation` first and prefer database-active employees in the default review scope.
3. If the user asks for order, class, learning, or region metrics, select the table by business theme instead of forcing everything into the default GMV table.
4. If the user cites a table from the metric-definition document, verify that the table exists in the current live database before querying it.
5. If the documented table is not visible in `intl_analysis`, explain that the document is a warehouse-definition reference and then choose the closest verified live reporting table.
6. If the user asks to switch away from `intl_analysis`, treat that as out of scope for the current version of the skill unless the skill is explicitly expanded.
7. If the request is primarily exploratory StarRocks work rather than the built-in Megaview employee workflow, prefer `scripts/starrocks_query.py`.

## Safe wording

Use wording like:

- `documented metric-definition table`: for names from the warehouse document
- `verified live reporting table`: for names confirmed in the current StarRocks database

Avoid wording like:

- `this table definitely exists online`
- `the metric-definition MV can be queried directly`

unless you already verified it in the current database.
