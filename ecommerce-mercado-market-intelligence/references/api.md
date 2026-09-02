## NexScope billing

The migrated Skill does not inherit the source platform's point value. Read X-Cost-Token from the HTTP response headers and calculate NexScope credits as X-Cost-Token × 0.001041. Example: 105000 × 0.001041 = 109.305. Preserve X-Cost-Credit as reported metadata only; it is not the calculation basis. Also preserve X-Kong-Trace-Id for diagnostics.

# NexScope proxy contract

The endpoint uses the `/api/v1/tools/research/` prefix. Successful HTTP responses use a NexScope envelope (`code`, `msg`, `data`, `traceId`, and cost metadata); the original business response is nested in `data`.

# 大麦数据美客多市场洞察与选品 API 参考

## 调用规范

- **请求地址**：`${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/damai/call`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: Bearer <api_key>`；api_key 优先从环境变量 `NEXSCOPE_API_KEY` 读取，回退 `NEXSCOPE_API_KEY`
- **User-Agent**：`NexScope-Skill/2.0`
- **超时**：150s

脚本透传 `SESSION_ID`、`MODE_ID`、`APP_NAME` 同名环境变量。上游 `X-API-Key` 由 NexScope 后端托管，不得传给 Skill 或最终用户。

## 请求结构

```json
{
  "toolName": "search_categories",
  "arguments": {
    "market_code": "MLM",
    "query": "celulares",
    "limit": 10
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `toolName` | string | 是 | 下表 7 个操作之一，大小写必须完全一致 |
| `arguments` | object | 否 | 操作参数对象；无参数操作传 `{}` |

支持市场：`MLM` 墨西哥、`MLB` 巴西、`MLA` 阿根廷、`MLC` 智利、`MCO` 哥伦比亚。`market_code` 缺省时由上游按 `MLM` 处理。

原版上游规则：`search_categories`、`get_my_quota_status` 免费；其余 5 个工具在原版中标记为 12 点。该数值不得换算或表述为 NexScope 积分；移植版只按响应头 `X-Cost-Token × 0.001041` 计算。上游套餐状态仍以 `get_my_quota_status` 的 `credit_policy` / `points_mode` 等字段为准。

## 工具参数

### search_categories

免费搜索候选类目。

| 参数 | 类型 | 必填 | 默认/范围 | 说明 |
|---|---|---:|---|---|
| `market_code` | string | 否 | `MLM` | 市场编码 |
| `query` | string | 否 | - | 当地语言类目关键词 |
| `limit` | integer | 否 | 默认及最大 100 | 返回数量 |

### industry_overview

| 参数 | 类型 | 必填 | 默认/范围 | 说明 |
|---|---|---:|---|---|
| `category_id` | string | 是 | - | 类目 ID |
| `market_code` | string | 否 | `MLM` | 市场编码 |

收费工具，遵循上述上游计费规则。

### search_product_snapshots

`keyword`、`category_id`、`sku_id`、`product_url`、`shop_id`、`shop_query` 至少提供一个。

| 参数 | 类型 | 必填 | 默认/范围 | 说明 |
|---|---|---:|---|---|
| `market_code` | string | 否 | `MLM` | 市场编码 |
| `keyword` | string | 条件必填 | - | 当地语言商品关键词 |
| `category_id` | string | 条件必填 | - | 类目 ID |
| `sku_id` | string | 条件必填 | - | 商品 ID，精确查询 |
| `product_url` | string | 条件必填 | - | HTTP(S) 商品链接 |
| `shop_id` | string | 条件必填 | - | 店铺或卖家 ID |
| `shop_query` | string | 条件必填 | - | 店铺或卖家名称关键词 |
| `price_min`, `price_max` | number | 否 | - | 价格区间 |
| `sales_30d_min`, `sales_30d_max` | integer | 否 | - | 近 30 天销量区间 |
| `historical_total_sales_min`, `historical_total_sales_max` | integer | 否 | - | 历史累计销量区间 |
| `rating_min`, `rating_max` | number | 否 | - | 评分区间 |
| `review_count_min`, `review_count_max` | integer | 否 | - | 评论数区间 |
| `listing_date_min`, `listing_date_max` | string | 否 | `YYYYMMDD` 或 `YYYY-MM-DD` | 上架日期区间 |
| `stock_type` | string | 否 | - | 库存或履约类型；不传表示不限 |
| `shop_type` | string | 否 | `cross_border`/`local` | 卖家类型 |
| `product_status` | string/integer | 否 | - | 商品状态，如 `active`、`paused` 或上游原始整数状态值 |
| `sort_by` | string | 否 | `sales_30d` | `sales_30d`、`historical_total_sales`、`price`、`listing_date`、`rating`、`review_count`、`title` |
| `sort_order` | string | 否 | `desc` | `asc` 或 `desc` |
| `page` | integer | 否 | 1 起 | 页码 |
| `limit` | integer | 否 | 默认及最大 100 | 每页数量 |

收费工具，遵循上述上游计费规则。

### product_sales_trend

| 参数 | 类型 | 必填 | 默认/范围 | 说明 |
|---|---|---:|---|---|
| `sku_id` | string | 是 | - | 商品 ID |
| `market_code` | string | 否 | `MLM` | 市场编码 |
| `days` | integer | 否 | 默认 730，1-731 | 查询天数 |

收费工具，遵循上述上游计费规则。

### image_search_products

`image_url`、`image_base64` 至少提供一个。

| 参数 | 类型 | 必填 | 默认/范围 | 说明 |
|---|---|---:|---|---|
| `image_url` | string | 条件必填 | - | 可公开访问的 HTTP(S) 图片 URL |
| `image_base64` | string | 条件必填 | - | 图片 Base64 字符串 |
| `market_code` | string | 否 | `MLM` | 市场编码 |
| `page` | integer | 否 | 1 | 页码 |
| `limit` | integer | 否 | 50 | 返回数量；最大值由上游服务配置决定 |
| `token` | string | 否 | 服务端配置 | 图片搜索令牌，通常无需传入；传入时仅覆盖本次请求 |

收费工具，遵循上述上游计费规则。

本地图片必须先运行 `python scripts/upload_image.py <path>`。辅助脚本请求 `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/oss/file/presignedPut` 获取预签名 PUT URL，上传成功后输出有效期 24 小时的公开 URL，再将该 URL 传入 `image_url`。不得把预签名查询参数、NexScope Key 或完整 Base64 内容写入面向用户的结果。

### review_search

| 参数 | 类型 | 必填 | 默认/范围 | 说明 |
|---|---|---:|---|---|
| `sku_id` | string | 是 | - | 商品 ID |
| `market_code` | string | 否 | `MLM` | 市场编码 |
| `page` | integer | 否 | 1 | 页码 |
| `limit` | integer | 否 | 默认 20，最大 100 | 每页数量 |

收费工具，遵循上述上游计费规则。

### get_my_quota_status

无需参数，上游免费。该操作返回后端所持上游账号的套餐、次数额度和积分状态，默认仅用于连接验证和运维诊断，不应向最终用户展示账号编码等内部信息。官方文档存在两个响应版本，调用方应按实际存在的字段读取，详见下方响应结构。

## 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `code`, `msg` | string | 成功时为 `"200"` / `"ok"` |
| `errcode`, `errmsg` | integer/string | 网关状态与错误信息；生产成功响应通常为 `200` / `ok` |
| `type` | string | 当前为 `rawMcpToolResult` |
| `toolName` | string | 实际调用的操作名 |
| `providerCharged` | boolean | 上游是否按成功调用扣次数 |
| `charged` | boolean | NexScope 是否对本次调用计费；两个免费操作为 `false`，五个收费操作成功时为 `true` |
| `data` | object | 解包后的业务数据；若上游返回数组、标量或空值，后端按响应异常处理 |
| `rawResponse` | object | MCP `tools/call` 原始 result；仅诊断时读取 |
| `contentText` | string | MCP text content 原文，可为空 |
| `textParsedAsJson` | boolean | text content 是否解析为 JSON |
| `total` | integer | 可推断时返回的记录数 |
| `costToken` | integer | 计费 token；响应体可能省略，实际计费以响应头 `X-Cost-Token` 为准 |
| `costTime` | integer | 后端耗时，毫秒 |

主要业务结构：

| 操作 | 关键字段 |
|---|---|
| 类目搜索 | `request_overview`, `record_count`, `records[]`；记录可能含类目 ID/名称/本地化名称、层级与路径、叶子标记、近 30 天活跃商品数、销量/GMV、均价和店铺数 |
| 行业概览 | `data_available`, `market_code`, `taxonomy_code`, `industry_summary`；含月销量、月均价、月 GMV、商品数、活跃商品数、平均日销量、均价和近 30 天交易额。不同文档版本中 `monthly_order_growth_rate` 可能为 number、array 或 null，按真实响应读取 |
| 商品搜索 | `request_overview`, `record_count`, `matched_count`, `records[]`, `features`, `notices`，以及上游返回时可见的 `quota_hint` |
| 销量趋势 | `market_code`, `product_code`, `input_method`, `range_start_date`, `range_end_date`, `requested_day_count`, `data_available`, `data_coverage`, `aggregation_period`, `monthly_order_series`, `weekly_order_series`, `notices` |
| 图片搜索 | `request_overview`, `provider_status`（boolean/string）、`display_message`, `record_count`, `product_code`, `provider_payload` |
| 评论查询 | `market_code`, `product_code`, `page_number`, `page_size`, `matched_count`, `reviews[]`；评论可能含 ID、评分、标题/商品名、原文、英文/本地化文本、时间和买家名 |
| 配额查询 | 新版可能返回 `customer_account_code`, `credit_balance`, `credit_policy`, `plan_code`, `plan_name`, `quota_limit`, `used_quota`, `quota_starts_at`, `quota_ends_at`, `available_points`, `points_mode`；兼容版本可能返回 `customer_code`, `service_plan`, `request_allowance`, `allowance_period_seconds`, `requests_consumed`, `requests_available`, `allowance_refresh_at`, `customer_account_code`, `credit_balance`, `credit_policy` |

商品 `records[]` 的可选字段包括：`product_code`, `product_name`, `detail_link`, `picture_link`, `selling_price`, `currency_code`, `orders_last_30_days`, `orders_last_60_days`, `orders_last_90_days`, `order_growth_last_30_days`, `lifetime_orders`, `revenue_last_30_days`, `average_conversion_rate`, `feedback_count`, `feedback_score`, `brand_label`, `merchant_code`, `merchant_name`, `merchant_type`, `listing_status`, `taxonomy_name`, `taxonomy_name_localized`, `taxonomy_trail`, `first_listed_on`, `market_rank`, `segment_rank`, `option_count`, `competing_offer_count`, `fulfillment_type`, `available_inventory`, `parcel_length_cm`, `parcel_width_cm`, `parcel_height_cm`, `dimensional_weight_kg`, `parcel_weight_kg`, `parcel_volume_cm3`。字段可能缺失或为 null，不得假设全部存在。

## 错误处理

| 状态/errcode | 含义 | 处理 |
|---|---|---|
| `1002` | 参数缺失、类型/范围错误、未知字段或不支持的 `toolName` | 按本文件修正请求，不自动改条件连续重试 |
| HTTP 401 | NexScope 网关认证失败 | 按 `references/onboarding.md` 处理 |
| HTTP 402 | NexScope 积分或套餐不足 | 按 `references/onboarding.md` 处理 |
| HTTP 403 | NexScope 网关无权访问 | 检查是否误用了上游 Key |
| `1003` | 上游限流、超时、协议或服务异常 | 收费工具不自动重放；保留脱敏请求并联系管理员 |
| `1005` | 后端托管的上游认证失败 | 联系管理员，不能让最终用户提供上游 Key |

网关可能以 HTTP 200 + `ToolErrorResponse` XML 返回业务错误。官方入口脚本会将其归一化为包含 `errcode` / `errmsg` 的 JSON 后展示，且失败响应不会写入 24h 缓存。

空结果、`data_available=false` 或覆盖不足提示通常是正常业务结果，不等同于系统故障。

## curl 示例

```bash
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/damai/call" \
  -H "Authorization: $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -d '{"toolName":"search_categories","arguments":{"market_code":"MLM","query":"celulares","limit":10}}'
```

## Feedback API

此接口独立于工具网关：

- **POST** `https://skill-api.nexscope.com/api/v1/public/feedback`
- **Content-Type**：`application/json`

```json
{
  "skillName": "nexscope-damai-mercado-market-intelligence",
  "sentiment": "NEUTRAL",
  "category": "SUGGESTION",
  "content": "Product trend coverage should be explained more clearly."
}
```

- `sentiment`：`POSITIVE`、`NEUTRAL`、`NEGATIVE`
- `category`：`BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER`
- `content`：只写必要的用户意图、实际行为和改进点，不包含 Key、隐私、Base64 图片或完整大响应
