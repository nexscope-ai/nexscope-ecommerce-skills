## Nexscope billing

The migrated Skill does not inherit the source platform's point value. This operation consumes Nexscope credits. Preserve X-Cost-Token and X-Cost-Credit from the HTTP response headers as server-reported billing metadata, and preserve X-Kong-Trace-Id for diagnostics.

# Nexscope proxy contract

The endpoint uses the `/api/v1/tools/research/` prefix. Successful HTTP responses use a Nexscope envelope (`code`, `msg`, `data`, `traceId`, and cost metadata); the original business response is nested in `data`.

# Damai Data Mercado Market Intelligence and Product Research API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/damai/call`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: Bearer <api_key>`; api_key is read first from the `NEXSCOPE_API_KEY` environment variable, with `NEXSCOPE_API_KEY` as the fallback
- **User-Agent**：`Nexscope-Skill/2.0`
- **Timeout**: 150s

The script forwards the `SESSION_ID`, `MODE_ID`, and `APP_NAME` environment variables with the same names. The upstream `X-API-Key` is managed by the Nexscope backend and must not be passed to the Skill or end users.

## Request Structure

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

| Field | Type | Required | Description |
|---|---|---:|---|
| `toolName` | string | Yes | One of the 7 operations below; case must match exactly |
| `arguments` | object | No | Operation parameters object; send `{}` for operations without parameters |

Supported markets: `MLM` Mexico, `MLB` Brazil, `MLA` Argentina, `MLC` Chile, and `MCO` Colombia. When `market_code` is omitted, the upstream service uses `MLM`.

Original upstream rules: `search_categories` and `get_my_quota_status` are free; the other 5 tools are listed as costing 12 points in the original version. Do not convert this value to or describe it as Nexscope credits; migrated calls consume credits and preserve server-reported billing metadata from response headers. Upstream plan status is still determined by fields such as `credit_policy` / `points_mode` from `get_my_quota_status`.

## Tool Parameters

### search_categories

Search candidate categories for free.

| Parameter | Type | Required | Default/Range | Description |
|---|---|---:|---|---|
| `market_code` | string | No | `MLM` | Market code |
| `query` | string | No | - | Category keyword in the local language |
| `limit` | integer | No | Default and maximum 100 | Number of results |

### industry_overview

| Parameter | Type | Required | Default/Range | Description |
|---|---|---:|---|---|
| `category_id` | string | Yes | - | Category ID |
| `market_code` | string | No | `MLM` | Market code |

Paid tool; follows the upstream billing rules above.

### search_product_snapshots

Provide at least one of `keyword`, `category_id`, `sku_id`, `product_url`, `shop_id`, `shop_query`.

| Parameter | Type | Required | Default/Range | Description |
|---|---|---:|---|---|
| `market_code` | string | No | `MLM` | Market code |
| `keyword` | string | Conditionally required | - | Product keyword in the local language |
| `category_id` | string | Conditionally required | - | Category ID |
| `sku_id` | string | Conditionally required | - | Product ID for exact lookup |
| `product_url` | string | Conditionally required | - | HTTP(S) product URL |
| `shop_id` | string | Conditionally required | - | Shop or seller ID |
| `shop_query` | string | Conditionally required | - | Shop or seller name keyword |
| `price_min`, `price_max` | number | No | - | Price range |
| `sales_30d_min`, `sales_30d_max` | integer | No | - | Sales volume range over the last 30 days |
| `historical_total_sales_min`, `historical_total_sales_max` | integer | No | - | Historical cumulative sales volume range |
| `rating_min`, `rating_max` | number | No | - | Rating range |
| `review_count_min`, `review_count_max` | integer | No | - | Review count range |
| `listing_date_min`, `listing_date_max` | string | No | `YYYYMMDD` or `YYYY-MM-DD` | Listing date range |
| `stock_type` | string | No | - | Stock or fulfillment type; omit for no restriction |
| `shop_type` | string | No | `cross_border`/`local` | Seller type |
| `product_status` | string/integer | No | - | Product status, e.g. `active`, `paused`, or the original upstream integer status value |
| `sort_by` | string | No | `sales_30d` | `sales_30d`, `historical_total_sales`, `price`, `listing_date`, `rating`, `review_count`, `title` |
| `sort_order` | string | No | `desc` | `asc` or `desc` |
| `page` | integer | No | Starting from 1 | Page number |
| `limit` | integer | No | Default and maximum 100 | Items per page |

Paid tool; follows the upstream billing rules above.

### product_sales_trend

| Parameter | Type | Required | Default/Range | Description |
|---|---|---:|---|---|
| `sku_id` | string | Yes | - | Product ID |
| `market_code` | string | No | `MLM` | Market code |
| `days` | integer | No | Default 730, range 1-731 | Number of days to query |

Paid tool; follows the upstream billing rules above.

### image_search_products

Provide at least one of `image_url`, `image_base64`.

| Parameter | Type | Required | Default/Range | Description |
|---|---|---:|---|---|
| `image_url` | string | Conditionally required | - | Publicly accessible HTTP(S) image URL |
| `image_base64` | string | Conditionally required | - | Base64-encoded image string |
| `market_code` | string | No | `MLM` | Market code |
| `page` | integer | No | 1 | Page number |
| `limit` | integer | No | 50 | Number of results; maximum determined by upstream service configuration |
| `token` | string | No | Server configuration | Image search token, usually not required; if supplied, overrides the token for this request only |

Paid tool; follows the upstream billing rules above.

For local images, first run `python scripts/upload_image.py <path>`. The helper calls `POST ${NEXSCOPE_PROXY_BASE}/api/skill-asset/presign`, the presigned HTTPS `PUT`, and `POST ${NEXSCOPE_PROXY_BASE}/api/skill-asset/confirm` in sequence. Pass only `publicUrl` from the confirm response as `image_url`; do not send the Nexscope Key to the presigned upload URL or output signature parameters or full Base64 content.

### review_search

| Parameter | Type | Required | Default/Range | Description |
|---|---|---:|---|---|
| `sku_id` | string | Yes | - | Product ID |
| `market_code` | string | No | `MLM` | Market code |
| `page` | integer | No | 1 | Page number |
| `limit` | integer | No | Default 20, maximum 100 | Items per page |

Paid tool; follows the upstream billing rules above.

### get_my_quota_status

No parameters required; free upstream. This operation returns the plan, request allowance, and points status of the upstream account held by the backend. By default, use it only for connection verification and operational diagnostics; do not expose internal information such as account codes to end users. Official documentation contains two response versions; callers should read the fields actually present, as detailed in Response Structure below.

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Package scripts unwrap this platform object for their business output and retain its `code`, `msg`, and timing metadata under `_nexscope`; for those outputs, inspect `_nexscope.code` / `_nexscope.msg`. Business `code` or `error` fields are not platform success markers.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Response Structure

| Field | Type | Description |
|---|---|---|
| `code`, `msg` | string | Provider business values retained inside platform `data`; not the outer platform status |
| `type` | string | Currently `rawMcpToolResult` |
| `toolName` | string | Name of the operation actually called |
| `providerCharged` | boolean | Whether the upstream service deducted a request allowance for a successful call |
| `charged` | boolean | Whether Nexscope charged for this call; `false` for the two free operations and `true` on success for the five paid operations |
| `data` | object | Unwrapped business data; upstream arrays, scalars, or null values are treated as response errors by the backend |
| `rawResponse` | object | Original MCP `tools/call` result; read only for diagnostics |
| `contentText` | string | Original MCP text content; may be empty |
| `textParsedAsJson` | boolean | Whether text content was parsed as JSON |
| `total` | integer | Record count, returned when it can be inferred |
| `costToken` | integer | Billable tokens; may be omitted from the response body. Actual billing is determined by the `X-Cost-Token` response header |
| `costTime` | integer | Backend elapsed time, in milliseconds |

Main business data structures:

| Operation | Key Fields |
|---|---|
| Category search | `request_overview`, `record_count`, `records[]`; records may include category ID/name/localized name, level and path, leaf flag, active products over the last 30 days, sales/GMV, average price, and shop count |
| Industry overview | `data_available`, `market_code`, `taxonomy_code`, `industry_summary`; includes monthly sales, monthly average price, monthly GMV, product count, active product count, average daily sales, average price, and transaction value over the last 30 days. Different documentation versions show `monthly_order_growth_rate` as number, array, or null; read the actual response |
| Product search | `request_overview`, `record_count`, `matched_count`, `records[]`, `features`, `notices`, and `quota_hint` when returned upstream |
| Sales trend | `market_code`, `product_code`, `input_method`, `range_start_date`, `range_end_date`, `requested_day_count`, `data_available`, `data_coverage`, `aggregation_period`, `monthly_order_series`, `weekly_order_series`, `notices` |
| Image search | `request_overview`, `provider_status` (boolean/string), `display_message`, `record_count`, `product_code`, `provider_payload` |
| Review lookup | `market_code`, `product_code`, `page_number`, `page_size`, `matched_count`, `reviews[]`; reviews may include ID, rating, title/product name, original text, English/localized text, time, and buyer name |
| Quota lookup | The new version may return `customer_account_code`, `credit_balance`, `credit_policy`, `plan_code`, `plan_name`, `quota_limit`, `used_quota`, `quota_starts_at`, `quota_ends_at`, `available_points`, `points_mode`; the compatibility version may return `customer_code`, `service_plan`, `request_allowance`, `allowance_period_seconds`, `requests_consumed`, `requests_available`, `allowance_refresh_at`, `customer_account_code`, `credit_balance`, `credit_policy` |

Optional fields in product `records[]` include: `product_code`, `product_name`, `detail_link`, `picture_link`, `selling_price`, `currency_code`, `orders_last_30_days`, `orders_last_60_days`, `orders_last_90_days`, `order_growth_last_30_days`, `lifetime_orders`, `revenue_last_30_days`, `average_conversion_rate`, `feedback_count`, `feedback_score`, `brand_label`, `merchant_code`, `merchant_name`, `merchant_type`, `listing_status`, `taxonomy_name`, `taxonomy_name_localized`, `taxonomy_trail`, `first_listed_on`, `market_rank`, `segment_rank`, `option_count`, `competing_offer_count`, `fulfillment_type`, `available_inventory`, `parcel_length_cm`, `parcel_width_cm`, `parcel_height_cm`, `dimensional_weight_kg`, `parcel_weight_kg`, `parcel_volume_cm3`. Fields may be absent or null; do not assume all are present.

## Error Handling

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Missing parameters, type/range errors, unknown fields, or unsupported `toolName` | Correct the request according to this document; do not automatically change conditions and retry repeatedly |
| Nexscope gateway authentication failed | Follow `references/onboarding.md` |
| Insufficient Nexscope credits or plan allowance | Follow `references/onboarding.md` |
| Access denied by the Nexscope gateway | Check whether an upstream Key was used by mistake |
| Upstream rate limit, timeout, protocol, or service error | Do not automatically replay paid tools; retain a sanitized request and contact an administrator |
| Authentication failed for the upstream credentials managed by the backend | Contact an administrator; do not ask end users to supply an upstream Key |

Empty results, `data_available=false`, or insufficient coverage notices are usually normal business outcomes and do not imply a system failure.

## curl Examples

```bash
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/damai/call" \
  -H "Authorization: $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -d '{"toolName":"search_categories","arguments":{"market_code":"MLM","query":"celulares","limit":10}}'
```

## Feedback API

This endpoint is separate from the tool gateway:

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
- `content`: Include only necessary user intent, actual behavior, and suggested improvements; exclude Keys, private information, Base64 images, and full large responses
