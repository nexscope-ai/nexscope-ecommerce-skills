# `_ehunt_productQuery` API Reference

## Call Notes

- **Tool Name**: `_ehunt_productQuery` (Nexscope MCP, `serverName`: Third-party data service).
- **MCP Display Name**: Etsy Product Query.
- **Note**: Business fields depend on the operation. Only the outer numeric platform `code: 0` indicates success; a nested business `code` does not replace it.

## Request Parameters (JSON)

| Parameter | Type | Required | Description |
|------|------|------|------|
| beginFavorites | integer, >=0 | No | Favorite count (start), combined with end value to form the upstream favorites range |
| beginFavoritesWeekly | integer, >=0 | No | Weekly new favorites (start), combined with end value to form the upstream favorites_weekly range |
| beginPrice | number, >=0 | No | Price (start), combined with end price to form the upstream price range (e.g., 20~100). When only one side is provided, the upstream returns start~ or ~end |
| beginReviews | integer, >=0 | No | Review count (start), combined with end value to form the upstream reviews range |
| beginReviewsWeekly | integer, >=0 | No | Weekly new reviews (start), combined with end value to form the upstream reviews_weekly range |
| beginSales | integer, >=0 | No | Total sales (start), combined with end value to form the upstream sales range |
| beginSalesWeekly | integer, >=0 | No | Weekly sales (start), combined with end value to form the upstream sales_weekly range (e.g., 1~100) |
| category | string, maxLen=1000 | No | Product category ID (single category), see the Category Query API |
| country | string, maxLen=1000 | No | Shipping country |
| currencyCode | string, default=USD, maxLen=1000 | No | Currency code |
| endFavorites | integer, >=0 | No | Favorite count (end) |
| endFavoritesWeekly | integer, >=0 | No | Weekly new favorites (end) |
| endPrice | number, >=0 | No | Price (end), combined with start price to form the upstream price range |
| endReviews | integer, >=0 | No | Review count (end) |
| endReviewsWeekly | integer, >=0 | No | Weekly new reviews (end) |
| endSales | integer, >=0 | No | Total sales (end) |
| endSalesWeekly | integer, >=0 | No | Weekly sales (end) |
| isBestsell | integer | No | Whether the product is a bestseller |
| isPick | integer | No | Whether the product is a Pick item |
| isRaving | integer | No | Whether the product is a Raving item |
| listedTime | string, pattern | No | Listing time no earlier than this date (YYYY-MM-DD) |
| page | integer, >=1, default 1 | No | Page number (starting from 1) |
| pageSize | integer, 1~100, default 20 | No | Items per page, max 100, recommended not to exceed 50 |
| productType | string, must match schema regex | No | Product type, comma-separated for multiple: 1=Handmade 2=Vintage 3=Digital 4=Custom 9=Other |
| searchKey | string, maxLen=500 | No | Search keyword or Etsy product URL |
| sortBy | integer (1~6) | No | Sort field (corresponds to upstream sort_by, values 1~6) |
| sortDesc | integer | No | Sort direction (corresponds to upstream `desc`). Schema example: descending `1`, ascending `2` (encoding differs from store query's `sortDesc`) |
| status | integer | No | Product status (example: 1=active, 0=inactive) |

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
| total | integer | Record count (number of records returned on this page, for alignment with list length) |
| sourceTool | string | Tool type: ehunt |
| sourceType | string | Source type: etsy |
| columns | array | Rendered columns |
| costToken | integer | Token consumption (estimated based on records returned on this page) |
| productNum | integer | Total number of matching products (upstream product_num) |
| title | string | Title |
| type | string | Render style |
| products | array | Etsy product list |

### `products[]` Elements

| Field | Type | Description |
|------|------|------|
| category | string | Category name |
| favorites | integer | Favorite count |
| favoritesWeekly | integer | Weekly new favorites |
| imageUrl | string | Main image URL |
| isBestsell | integer | Whether bestseller: 1=Yes |
| isPick | integer | Whether Pick: 1=Yes |
| isRaving | integer | Whether Raving: 1=Yes |
| price | number | Price |
| productUrl | string | Product link |
| releaseTime | string | Listing/release time |
| reviews | integer | Review count |
| reviewsWeekly | integer | Weekly new reviews |
| salesTotal | integer | Total sales |
| salesWeekly | integer | Weekly sales |
| shipsFrom | string | Shipping country |
| status | integer | Product status: 1=active, 0=inactive |
| storeName | string | Store name |
| tags | string | Tags |
| title | string | Product title |

## Script Debugging (Optional)

The repository provides **`scripts/etsy_product_query.py`** (Python 3, standard library only).

- **Gateway**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ehunt/etsy/productQuery` (can be overridden via `NEXSCOPE_PROXY_BASE_BASE`); **Authentication**: `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)

```bash
export NEXSCOPE_API_KEY="<your-key>"
python scripts/etsy_product_query.py '{"searchKey": "poster", "currencyCode": "USD", "page": 1, "pageSize": 20}'
```
