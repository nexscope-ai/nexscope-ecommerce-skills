# Shopify Product Query API Reference

## Usage Notes

- **Gateway route**: `POST ehunt/shopify/productQuery` (full: `${NEXSCOPE_PROXY_BASE}Query`).
- **MCP display name**: Shopify Product Query (the exact tool name is subject to the tool metadata deployed in the current environment).
- **Authentication**: Request header `Authorization: <api_key>`, api_key read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md).
- **Note**: Business fields depend on the operation. Only the outer numeric platform `code: 0` indicates success; a nested business `code` does not replace it.

## Request Parameters (JSON)

| Parameter | Type | Required | Description |
|------|------|------|------|
| searchKey | string, maxLen=500 | No | Keyword or Shopify product/store URL |
| priceMin | number, >=0 | No | Price range start (USD), combined with priceMax to form upstream `price` |
| priceMax | number, >=0 | No | Price range end (USD) |
| salesWeeklyMin | integer, >=0 | No | Weekly sales range start |
| salesWeeklyMax | integer, >=0 | No | Weekly sales range end |
| publishedTimeBegin | string (YYYY-MM-DD) | No | Listing date range start |
| publishedTimeEnd | string (YYYY-MM-DD) | No | Listing date range end |
| facebookAd | integer | No | Has Facebook ad: 1=Yes |
| competitionMin | integer, >=0 | No | Competition (number of stores selling) range start |
| competitionMax | integer, >=0 | No | Competition (number of stores selling) range end |
| hasSupplier | integer | No | Has supplier: 1=Yes, 0=No |
| showDeleted | integer | No | Show delisted products: 1=Yes, 0=No |
| country | string | No | Shipping country (two-letter country code, e.g., US) |
| sortBy | integer | No | Sort field (default 14=Weekly sales descending; also includes price/ad count/competition/revenue etc. values, see enumeration below) |
| page | integer, >=1, default 1 | No | Page number (starting from 1) |
| pageSize | integer, 1~100, default 20 | No | Results per page, max 100, recommended not to exceed 50 |

### `sortBy` Values

Upstream sort enumeration, default `14` (weekly sales descending). Common values include ascending/descending combinations of price, listing time, ad count, competition, weekly sales, weekly revenue, revenue growth rate, etc.; specific codes are subject to the current gateway tool schema comments. Use the default when unknown.

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
| products | array | Shopify product list |
| columns | array | Columns for rendering |
| title | string | Title (`Shopify Product Query`) |
| sourceType | string | Source type: shopify |
| sourceTool | string | Tool type: ehunt |
| type | string | Render style: tableListWorkbenches |

### `products[]` Elements

| Field | Upstream Alias | Description |
|------|----------|------|
| productId | `product_id` | Product ID |
| title | - | Product title |
| productLink | `product_link` | Product link |
| previewImageUrl | `preview_image_url` | Main image URL |
| country | - | Shipping country |
| minPrice | `min_price` | Minimum price |
| maxPrice | `max_price` | Maximum price |
| storeId | `store_id` | Store ID |
| shopId | `shop_id` | Shopify shop ID |
| storeLink | `store_link` | Store link |
| storeRank | `store_rank` | Store rank |
| competitorCount | `competitor_count` | Competition (number of stores selling) |
| facebookAdCount | `facebook_ad_count` | Facebook ad count |
| weekOrderCount | `week_order_count` | Weekly order count (string) |
| weekRevenueCount | `week_revenue_count` | Weekly revenue |
| weekRevenueGrowth | `week_revenue_growth` | Weekly revenue growth rate (%) |
| shelfTime | `shelf_time` | Listing time |
| isDeleted | `is_deleted` | Whether delisted: 0=Listed, 1=Delisted |
| isFavourite | `is_favourite` | Whether favorited |

## Script Debugging (Optional)

The repository provides **`scripts/shopify_product_query.py`** (Python 3, standard library only), which POSTs JSON matching the MCP input parameters to the Nexscope tool gateway.

- **Gateway**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ehunt/shopify/productQuery` (can override root URL with `NEXSCOPE_PROXY_BASE_BASE`)
- **Authentication**: Environment variable `NEXSCOPE_API_KEY` (same as other `nexscope-*` skills; if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

```bash
export NEXSCOPE_API_KEY="<your-key>"
python scripts/shopify_product_query.py '{"searchKey": "phone case", "country": "US", "page": 1, "pageSize": 20}'
```
