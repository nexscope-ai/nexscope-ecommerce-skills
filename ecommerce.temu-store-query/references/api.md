# EHunt Temu Store Query API Reference

## Request Details

- **Gateway route**: `POST /api/v1/tools/linkfox/ehunt/temu/storeQuery` (full URL: `NEXSCOPE_PROXY_BASE + /api/v1/tools/linkfox/ehunt/temu/storeQuery`).
- **Display name**: Temu Store Query (exact tool name depends on the tool metadata delivered in the current environment).
- **Authentication**: Request header `Authorization: Bearer <NEXSCOPE_API_KEY>`.
- **Notes**: Parameters and response structure follow the current gateway response; if the upstream returns a root-level JSON `code` field, success value (`200`) is determined by the live response. The gateway may throw an error when no data is found.

## Request Parameters (JSON)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| searchKey | string, maxLen=500 | No | Store name or ID keyword |
| siteId | string | No | Country site ID, comma-separated (100=US, 101=UK, 102=EU, 103=JP, 105=KR) |
| category | string | No | Back-end category ID, comma-separated |
| isLocal | string | No | Fulfillment mode: 0 = fully managed, 1 = semi-managed |
| orderTotalMin | integer, >=0 | No | Total sales range (start) |
| orderTotalMax | integer, >=0 | No | Total sales range (end) |
| orderWeekMin | integer, >=0 | No | Weekly sales range (start) |
| orderWeekMax | integer, >=0 | No | Weekly sales range (end) |
| orderMonthMin | integer, >=0 | No | Monthly sales range (start) |
| orderMonthMax | integer, >=0 | No | Monthly sales range (end) |
| totalRevenueMin | number, >=0 | No | Total revenue range (USD, start) |
| totalRevenueMax | number, >=0 | No | Total revenue range (USD, end) |
| weekRevenueMin | number, >=0 | No | Weekly revenue range (USD, start) |
| weekRevenueMax | number, >=0 | No | Weekly revenue range (USD, end) |
| monthRevenueMin | number, >=0 | No | Monthly revenue range (USD, start) |
| monthRevenueMax | number, >=0 | No | Monthly revenue range (USD, end) |
| ratingMin | number (0~5) | No | Rating range (start) |
| ratingMax | number (0~5) | No | Rating range (end) |
| reviewNumMin | integer, >=0 | No | Review count range (start) |
| reviewNumMax | integer, >=0 | No | Review count range (end) |
| followerNumMin | integer, >=0 | No | Follower count range (start) |
| followerNumMax | integer, >=0 | No | Follower count range (end) |
| productNumMin | integer, >=0 | No | Product count range (start) |
| productNumMax | integer, >=0 | No | Product count range (end) |
| listedTimeBegin | string (YYYY-MM-DD) | No | Store opening date range (start) |
| listedTimeEnd | string (YYYY-MM-DD) | No | Store opening date range (end) |
| sortBy | string | No | Sort field + direction: `order_week_count-0` (weekly sales desc, default), `order_count-0`, `total_revenue-0`, `rating-0` |
| page | integer, >=1, default 1 | No | Page number (starts at 1) |
| pageSize | integer, 1~100, default 20 | No | Items per page, max 100 |

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Number of items returned on this page |
| storeNum | integer | Total number of stores matching the query (upstream `store_num`) |
| stores | array | List of Temu stores |
| columns | array | Columns for rendering |
| title | string | Title (`Temu Store Query`) |
| sourceType | string | Source type: temu |
| sourceTool | string | Tool type: ehunt |
| type | string | Render style: tableListWorkbenches |

### `stores[]` Element

| Field | Upstream Alias | Description |
|-------|----------------|-------------|
| storeId | `store_id` | Store ID |
| siteId | `site_id` | Country site ID |
| storeName | `store_name` | Store name |
| logoUrl | `logo_url` | Store logo URL |
| orderTotal | `order_total` | Total sales |
| orderWeek | `order_week` | Weekly sales |
| orderMonth | `order_month` | Monthly sales |
| totalRevenue | `total_revenue` | Total revenue |
| weekRevenue | `week_revenue` | Weekly revenue |
| monthRevenue | `month_revenue` | Monthly revenue |
| rating | - | Rating |
| listedTime | `listed_time` | Store opening date |
| reviewNum | `review_num` | Review count |
| followerNum | `follower_num` | Follower count |
| productNum | `product_num` | Product count |
| categoriesCn | `categories_cn` | Category list (Chinese) |
| categories | - | Category list (English) |
| isLocal | `is_local` | Fulfillment mode: 0 = fully managed, 1 = semi-managed |

## Script Debugging (Optional)

The repository provides **`scripts/ehunt_temu_store_query.py`** (Python 3, stdlib only), which POSTs JSON identical to MCP input parameters via the Nexscope proxy gateway.

- **Proxy gateway**: Environment variable `NEXSCOPE_PROXY_BASE`
- **Route path**: `/api/v1/tools/linkfox/ehunt/temu/storeQuery`
- **Authentication**: Environment variable `NEXSCOPE_API_KEY`, header format `Authorization: Bearer <key>`

```bash
# NEXSCOPE_API_KEY and NEXSCOPE_PROXY_BASE are pre-configured in the runtime environment
python scripts/ehunt_temu_store_query.py '{"searchKey": "home", "siteId": "100", "page": 1, "pageSize": 20}'
```

If a connection error is returned, verify that the `NEXSCOPE_PROXY_BASE` and `NEXSCOPE_API_KEY` environment variables are set correctly.
