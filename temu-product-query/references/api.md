# EHunt Temu Product Query API Reference

## Request Details

- **Gateway route**: `POST /api/v1/tools/linkfox/ehunt/temu/productQuery` (full URL: `NEXSCOPE_PROXY_BASE + /api/v1/tools/linkfox/ehunt/temu/productQuery`).
- **Display name**: Temu Product Query (exact tool name depends on the tool metadata delivered in the current environment).
- **Authentication**: Request header `Authorization: Bearer <NEXSCOPE_API_KEY>`.
- **Notes**: Parameters and response structure follow the current gateway response; if the upstream returns a root-level JSON `code` field, success value (`200`) is determined by the live response. The gateway may throw an error when no data is found.

## Request Parameters (JSON)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| searchKey | string, maxLen=500 | No | Keyword, product ID, or store ID |
| categoryHome | string | No | Front-end category ID |
| categoryBackend | string | No | Back-end category ID |
| priceBegin | number, >=0 | No | Price range start (USD), forms upstream `price` |
| priceEnd | number, >=0 | No | Price range end (USD) |
| ratingBegin | number (0~5) | No | Rating range start, forms upstream `rating` |
| ratingEnd | number (0~5) | No | Rating range end |
| reviewsBegin | integer, >=0 | No | Review count range start, forms `reviews` |
| reviewsEnd | integer, >=0 | No | Review count range end |
| salesTotalBegin | integer, >=0 | No | Total sales range start, forms `sales_total` |
| salesTotalEnd | integer, >=0 | No | Total sales range end |
| salesWeeklyBegin | integer, >=0 | No | Weekly sales range start, forms `sales_weekly` |
| salesWeeklyEnd | integer, >=0 | No | Weekly sales range end |
| salesDailyBegin | integer, >=0 | No | Daily sales range start, forms `sales_daily` |
| salesDailyEnd | integer, >=0 | No | Daily sales range end |
| publishTimeBegin | string (YYYY-MM-DD) | No | Listing date range start, forms `publish_time` |
| publishTimeEnd | string (YYYY-MM-DD) | No | Listing date range end |
| soldOut | integer | No | Listing status: 0 = listed, 1 = delisted |
| isLocal | integer | No | Fulfillment mode: 0 = fully managed, 1 = semi-managed |
| region | string | No | Semi-managed region(s), comma-separated |
| tags | string | No | Product tags, comma-separated |
| customTags | string | No | Custom tags, comma-separated |
| sortBy | string | No | Sort field + direction: `order_week-0` (weekly sales desc, default), `price-0`, `order_total-0`, `rating-0`, etc. |
| page | integer, >=1, default 1 | No | Page number (starts at 1) |
| pageSize | integer, 1~100, default 20 | No | Items per page, max 100, recommended <= 50 |

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Number of items returned on this page |
| productNum | integer | Total number of products matching the query (upstream `product_num`) |
| products | array | List of Temu products |
| columns | array | Columns for rendering |
| title | string | Title (`Temu Product Query`) |
| sourceType | string | Source type: temu |
| sourceTool | string | Tool type: ehunt |
| type | string | Render style: tableListWorkbenches |

### `products[]` Element

| Field | Upstream Alias | Description |
|-------|----------------|-------------|
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
| publishTime | `publish_time` | Listing date |
| soldOut | `sold_out` | Delisted status |
| isLocal | `is_local` | Fulfillment mode: 0 = fully managed, 1 = semi-managed |
| localRegion | `local_region` | Semi-managed region list |
| storeId | `store_id` | Store ID |
| tags | - | Tag list |
| customTags | `custom_tags` | Custom tags |
| categoryHome | `category_home` | Front-end category |
| categoryBackend | `category_backend` | Back-end category |

## Script Debugging (Optional)

The repository provides **`scripts/ehunt_temu_product_query.py`** (Python 3, stdlib only), which POSTs JSON identical to MCP input parameters via the Nexscope proxy gateway.

- **Proxy gateway**: Environment variable `NEXSCOPE_PROXY_BASE`
- **Route path**: `/api/v1/tools/linkfox/ehunt/temu/productQuery`
- **Authentication**: Environment variable `NEXSCOPE_API_KEY`, header format `Authorization: Bearer <key>`

```bash
# NEXSCOPE_API_KEY and NEXSCOPE_PROXY_BASE are pre-configured in the runtime environment
python scripts/ehunt_temu_product_query.py '{"searchKey": "kitchen", "page": 1, "pageSize": 20}'
```

If a connection error is returned, verify that the `NEXSCOPE_PROXY_BASE` and `NEXSCOPE_API_KEY` environment variables are set correctly.
