# Temu Product Query API Reference

## Usage Notes

- **Gateway route**: `POST ehunt/temu/productQuery` (full: `${NEXSCOPE_PROXY_BASE}Query`).
- **MCP display name**: Temu Product Query (the exact tool name is subject to the tool metadata deployed in the current environment).
- **Authentication**: Request header `Authorization: <api_key>`, api_key read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md).
- **Note**: Business fields depend on the operation. Only the outer numeric platform `code: 0` indicates success; a nested business `code` does not replace it.

## Request Parameters (JSON)

| Parameter | Type | Required | Description |
|------|------|------|------|
| searchKey | string, maxLen=500 | No | Keyword or product ID / store ID |
| categoryHome | string | No | Front-end category ID |
| categoryBackend | string | No | Back-end category ID |
| priceBegin | number, >=0 | No | Price range start (USD), combined to form upstream `price` |
| priceEnd | number, >=0 | No | Price range end (USD) |
| ratingBegin | number (0~5) | No | Rating range start, combined to form upstream `rating` |
| ratingEnd | number (0~5) | No | Rating range end |
| reviewsBegin | integer, >=0 | No | Review count range start, combined to form `reviews` |
| reviewsEnd | integer, >=0 | No | Review count range end |
| salesTotalBegin | integer, >=0 | No | Total sales range start, combined to form `sales_total` |
| salesTotalEnd | integer, >=0 | No | Total sales range end |
| salesWeeklyBegin | integer, >=0 | No | Weekly sales range start, combined to form `sales_weekly` |
| salesWeeklyEnd | integer, >=0 | No | Weekly sales range end |
| salesDailyBegin | integer, >=0 | No | Daily sales range start, combined to form `sales_daily` |
| salesDailyEnd | integer, >=0 | No | Daily sales range end |
| publishTimeBegin | string (YYYY-MM-DD) | No | Listing date range start, combined to form `publish_time` |
| publishTimeEnd | string (YYYY-MM-DD) | No | Listing date range end |
| soldOut | integer | No | Whether delisted: 0=Listed, 1=Delisted |
| isLocal | integer | No | Whether semi-managed: 0=Fully managed, 1=Semi-managed |
| region | string | No | Semi-managed regions, comma-separated |
| tags | string | No | Product tags, comma-separated |
| customTags | string | No | Custom tags, comma-separated |
| sortBy | string | No | Sort field+direction: `order_week-0` (weekly sales descending, default), `price-0`, `order_total-0`, `rating-0`, etc. |
| page | integer, >=1, default 1 | No | Page number (starting from 1) |
| pageSize | integer, 1~100, default 20 | No | Results per page, max 100, recommended not to exceed 50 |

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Main Response Fields

| Field | Type | Description |
|------|------|------|
| total | integer | Number of results returned on this page |
| productNum | integer | Total number of matching products (upstream `product_num`) |
| products | array | Temu product list |
| columns | array | Columns for rendering |
| title | string | Title (`Temu Product Query`) |
| sourceType | string | Source type: temu |
| sourceTool | string | Tool type: ehunt |
| type | string | Render style: tableListWorkbenches |

### `products[]` Elements

| Field | Upstream Alias | Description |
|------|----------|------|
| productId | `product_id` | Product ID |
| productName | `product_name` | Product name (English) |
| productNameCn | `product_name_cn` | Product name (Chinese) |
| logoUrl | `logo_url` | Main image URL |
| price | - | Price |
| orderTotal | `order_total` | Total sales |
| orderWeek | `order_week` | Weekly sales |
| orderDay | `order_day` | Daily sales |
| orderMonth | `order_month` | Monthly sales |
| rating | - | Rating |
| reviewNum | `review_num` | Review count |
| publishTime | `publish_time` | Listing time |
| soldOut | `sold_out` | Whether delisted |
| isLocal | `is_local` | Whether semi-managed: 0=Fully managed, 1=Semi-managed |
| localRegion | `local_region` | Semi-managed region list |
| storeId | `store_id` | Store ID |
| tags | - | Tag list |
| customTags | `custom_tags` | Custom tags |
| categoryHome | `category_home` | Front-end category |
| categoryBackend | `category_backend` | Back-end category |

## Script Debugging (Optional)

The repository provides **`scripts/temu_product_query.py`** (Python 3, standard library only), which POSTs JSON matching the MCP input parameters to the Nexscope tool gateway.

- **Gateway**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ehunt/temu/productQuery` (can override root URL with `NEXSCOPE_PROXY_BASE_BASE`)
- **Authentication**: Environment variable `NEXSCOPE_API_KEY` (same as other `nexscope-*` skills; if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

```bash
export NEXSCOPE_API_KEY="<your-key>"
python scripts/temu_product_query.py '{"searchKey": "kitchen", "page": 1, "pageSize": 20}'
```
