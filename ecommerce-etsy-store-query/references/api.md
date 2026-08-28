# `_ehunt_storeQuery` API Reference

## Call Notes

- **Tool Name**: `_ehunt_storeQuery` (NexScope MCP, `serverName`: Third-party data service).
- **MCP Display Name**: Etsy Store Query.
- **Note**: Parameters and response structure are subject to the actual gateway response. If the upstream returns a JSON root-level `code` field, the success value is determined by the actual response.

## Request Parameters (JSON)

| Parameter | Type | Required | Description |
|------|------|------|------|
| beginFavorites | integer, >=0 | No | Store favorite count (start), combined with end value to form the upstream favorites range |
| beginFavoritesWeekly | integer, >=0 | No | Store weekly new favorites (start), combined with end value to form the upstream favorites_weekly range |
| beginReviews | integer, >=0 | No | Store review count (start), combined with end value to form the upstream reviews range |
| beginReviewsWeekly | integer, >=0 | No | Store weekly new reviews (start), combined with end value to form the upstream reviews_weekly range |
| beginSales | integer, >=0 | No | Store total sales (start), combined with end value to form the upstream sales range |
| beginSalesWeekly | integer, >=0 | No | Store weekly sales (start), combined with end value to form the upstream sales_weekly range, e.g., 10,100 |
| beginStoreOpenedAt | string, pattern | No | Store opening date range start (YYYY-MM-DD), combined with end date to form the upstream start_at, e.g., 2020-01-01~2023-01-01 |
| category | string, maxLen=1000 | No | Store primary category |
| country | string, maxLen=1000 | No | Store country |
| endFavorites | integer, >=0 | No | Store favorite count (end) |
| endFavoritesWeekly | integer, >=0 | No | Store weekly new favorites (end) |
| endReviews | integer, >=0 | No | Store review count (end) |
| endReviewsWeekly | integer, >=0 | No | Store weekly new reviews (end) |
| endSales | integer, >=0 | No | Store total sales (end) |
| endSalesWeekly | integer, >=0 | No | Store weekly sales (end) |
| endStoreOpenedAt | string, pattern | No | Store opening date range end (YYYY-MM-DD) |
| isRaving | integer | No | Whether Raving store: 1=Yes |
| isStar | integer | No | Whether starred store: 1=Yes |
| page | integer, >=1, default 1 | No | Page number (starting from 1) |
| pageSize | integer, 1~100, default 20 | No | Items per page, max 100 |
| searchKey | string, maxLen=500 | No | Search keyword, store name, or store URL |
| sortBy | integer (8~11) | No | Sort field sort_by: 8=total sales, 9=weekly sales, 10=review count, 11=favorite count |
| sortDesc | integer | No | Sort direction (corresponds to upstream desc): 1=descending, 0=ascending |
| status | integer | No | Store status: 1=active, 0=inactive |

## Main Response Fields

| Field | Type | Description |
|------|------|------|
| total | integer | Record count (number of records returned on this page) |
| sourceTool | string | Tool type: ehunt |
| sourceType | string | Source type: etsy |
| stores | array | Store list |
| columns | array | Rendered columns |
| costToken | integer | Token consumption (estimated based on records returned on this page) |
| storeNum | integer | Total number of matching stores (upstream store_num) |
| title | string | Title |
| type | string | Render style |

### `stores[]` Elements

| Field | Type | Description |
|------|------|------|
| category | array | Primary category list |
| country | array | Country/region list |
| favorites | integer | Favorite count |
| favoritesWeekly | integer | Weekly new favorites |
| isRaving | integer | Whether Raving: 1=Yes |
| isStar | integer | Whether starred: 1=Yes |
| logoUrl | string | Store avatar URL |
| productCount | integer | Store product count |
| rating | number | Rating |
| reviews | integer | Review count |
| reviewsWeekly | integer | Weekly new reviews |
| salesTotal | integer | Total sales |
| salesWeekly | integer | Weekly sales |
| shopWebsite | string | Store website/external link |
| startAt | string | Store opening date |
| status | integer | Store status: 1=active, 0=inactive |
| storeId | string | Store ID |
| storeName | string | Store name |
| storeUrl | string | Store link |

## Script Debugging (Optional)

The repository provides **`scripts/etsy_store_query.py`** (Python 3, standard library only), which POSTs JSON matching the MCP parameters to the NexScope tool gateway.

- **Gateway**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ehunt/etsy/storeQuery` (can be overridden via `NEXSCOPE_PROXY_BASE_BASE` for the root URL)
- **Authentication**: Environment variable `NEXSCOPE_API_KEY` (same as other `nexscope-*` skills; if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)

```bash
export NEXSCOPE_API_KEY="<your-key>"
python scripts/etsy_store_query.py '{"searchKey": "ceramic", "country": "US", "page": 1, "pageSize": 20}'
```

