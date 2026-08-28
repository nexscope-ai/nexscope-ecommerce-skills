# Temu Store Query API Reference

## Calling Instructions

- **Gateway Route**: `POST ehunt/temu/storeQuery` (full: `${NEXSCOPE_PROXY_BASE}Query`).
- **MCP Display Name**: Temu Store Query (the exact tool name is subject to the tool metadata distributed by the current environment).
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md).
- **Note**: Parameters and response structure are subject to the current gateway response; if the upstream returns a root-level `code` field in JSON, the success value (`200`) is subject to the live network. The gateway may throw an error when no data is available.

## Request Parameters (JSON)

| Parameter | Type | Required | Description |
|------|------|------|------|
| searchKey | string, maxLen=500 | No | Store name or ID keyword |
| siteId | string | No | Country site ID, multiple separated by commas (e.g., 211=US, 76=UK) |
| category | string | No | Backend category ID, multiple separated by commas |
| isLocal | string | No | Whether semi-managed: 0=fully managed, 1=semi-managed |
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
| sortBy | string | No | Sort field+direction: `order_week_count-0` (weekly sales descending, default), `order_count-0`, `total_revenue-0`, `rating-0` |
| page | integer, >=1, default 1 | No | Page number (starting from 1) |
| pageSize | integer, 1~100, default 20 | No | Items per page, max 100 |

## Response Main Fields

| Field | Type | Description |
|------|------|------|
| total | integer | Number of records on this page |
| storeNum | integer | Total number of stores matching criteria (upstream `store_num`) |
| stores | array | Temu store list |
| columns | array | Rendered columns |
| title | string | Title (`Temu Store Query`) |
| sourceType | string | Source type: temu |
| sourceTool | string | Tool type: ehunt |
| type | string | Render style: tableListWorkbenches |

### `stores[]` Elements

| Field | Upstream Alias | Description |
|------|----------|------|
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
| listedTime | `listed_time` | Store opening time |
| reviewNum | `review_num` | Review count |
| followerNum | `follower_num` | Follower count |
| productNum | `product_num` | Product count |
| categoriesCn | `categories_cn` | Chinese category list |
| categories | - | English category list |
| isLocal | `is_local` | Whether semi-managed: 0=fully managed, 1=semi-managed |

## Script Debugging (Optional)

The repository includes **`scripts/temu_store_query.py`** (Python 3, standard library only), which POSTs JSON consistent with MCP input parameters to the NexScope tool gateway.

- **Gateway**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ehunt/temu/storeQuery` (you can use `NEXSCOPE_PROXY_BASE_BASE` to override the root URL)
- **Authentication**: Environment variable `NEXSCOPE_API_KEY` (same as other `nexscope-*` skills; if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

```bash
export NEXSCOPE_API_KEY="<your-key>"
python scripts/temu_store_query.py '{"searchKey": "home", "siteId": "211", "page": 1, "pageSize": 20}'
```

