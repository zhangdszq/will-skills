# 阿里云短信常见错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| `OK` | 请求成功 | — |
| `isv.BUSINESS_LIMIT_CONTROL` | 触发频控限制 | 降低调用频率，检查是否超过每分钟/每天限额 |
| `isv.SMS_TEMPLATE_ILLEGAL` | 短信模板不合法 | 检查 TemplateCode 是否正确且已审核通过 |
| `isv.SMS_SIGNATURE_ILLEGAL` | 短信签名不合法 | 检查签名名称是否正确且已审核通过 |
| `isv.MOBILE_NUMBER_ILLEGAL` | 手机号格式不正确 | 检查号码格式，国内用 1xxxxxxxxxx，国际含国家代码 |
| `isv.MOBILE_COUNT_OVER_LIMIT` | 手机号码数量超过限制 | 单次发送不超过 100 个号码 |
| `isv.TEMPLATE_MISSING_PARAMETERS` | 模板缺少变量 | 补全 TemplateParam/TemplateParamJson 中的变量 |
| `isv.INVALID_PARAMETERS` | 参数格式不正确 | 检查 JSON 格式是否合法 |
| `isv.ACCOUNT_NOT_EXISTS` | 账户不存在 | 检查 AccessKey 是否正确 |
| `isv.ACCOUNT_ABNORMAL` | 账户异常 | 联系阿里云客服 |
| `isv.OUT_OF_SERVICE` | 服务停机 | 检查账户余额或套餐是否有效 |
| `isv.DOMESTIC_NUMBER_NOT_SUPPORTED` | 国际/港澳台短信模板不支持发送境内号码 | 使用国内短信模板 |
| `SignatureDoesNotMatch` | 签名不匹配 | 检查 AccessKey Secret 是否正确 |
| `InvalidTimeStamp.Expired` | 请求时间戳过期 | 检查系统时间是否准确 |
