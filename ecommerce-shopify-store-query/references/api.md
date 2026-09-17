# Shopify Store Query API Reference

## Usage Notes

- **Gateway route**: `POST ehunt/shopify/storeQuery` (full: `${NEXSCOPE_PROXY_BASE}Query`).
- **MCP display name**: Shopify Store Query (the exact tool name is subject to the tool metadata deployed in the current environment).
- **Authentication**: Request header `Authorization: <api_key>`, api_key read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md).
- **Note**: Business fields depend on the operation. Only the outer numeric platform `code: 0` indicates success; a nested business `code` does not replace it.

## Request Parameters (JSON)

| Parameter | Type | Required | Description |
|------|------|------|------|
| searchKey | string, maxLen=500 | No | Store name or domain keyword |
| country | string | No | Country code (e.g., US, CN) |
| year | integer | No | Store creation year: 1=Last 1 year, 2=1~2 years, 3=2~3 years, 4=3+ years |
| productNumMin | integer, >=0 | No | Product count range start |
| productNumMax | integer, >=0 | No | Product count range end |
| advertiseCountMin | integer, >=0 | No | Ad count range start |
| advertiseCountMax | integer, >=0 | No | Ad count range end |
| monthlyVisitMin | integer, >=0 | No | Monthly visits range start |
| monthlyVisitMax | integer, >=0 | No | Monthly visits range end |
| monthOrderMin | integer, >=0 | No | Monthly orders range start |
| monthOrderMax | integer, >=0 | No | Monthly orders range end |
| sortBy | integer | No | Sort field: 0=Product count, 1=Category count, 2=Monthly visits, 3=FB followers, 4=Ins followers, 5=Ad count, 6=Relevance, 7=Monthly orders (default) |
| orderBy | string | No | Sort direction: `desc` (default) / `asc` |
| page | integer, >=1, default 1 | No | Page number (starting from 1) |
| pageSize | integer, 1~100, default 20 | No | Results per page, max 100 |

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
| storeNum | integer | Total number of matching stores (upstream `store_num`) |
| stores | array | Shopify store list |
| columns | array | Columns for rendering |
| title | string | Title (`Shopify Store Query`) |
| sourceType | string | Source type: shopify |
| sourceTool | string | Tool type: ehunt |
| type | string | Render style: tableListWorkbenches |

### `stores[]` Elements

| Field | Upstream Alias | Description |
|------|----------|------|
| storeId | `store_id` | Store ID |
| shopId | `shop_id` | Shopify shop ID |
| storeName | `store_name` | Store name |
| storeDomain | `store_domain` | Store domain |
| storeLink | `store_link` | Store link |
| country | - | Country |
| createdTime | `created_time` | Creation time |
| productNum | `product_num` | Product count |
| categoryNum | `category_num` | Category count |
| categories | - | Category list (elements contain `id`, `name`) |
| monthlyVisit | `monthly_visit` | Monthly visits (formatted) |
| monthOrderNum | `month_order_num` | Monthly orders (formatted) |
| fbFollowers | `fb_followers` | Facebook followers |
| insFollowers | `ins_followers` | Instagram followers |
| advertiseCount | `advertise_count` | Ad count |
| adLink | `ad_link` | Ad library link |
| email | - | Contact email |
| facebookUrl | `facebook_url` | Facebook page |
| instagramUrl | `instagram_url` | Instagram page |
| socialLinks | `social_links` | Social media links (Map) |
| globalRank | `global_rank` | Global rank |
| logo | - | Store logo URL |
| availableStatus | `available_status` | Whether active: 1=Active |

## Script Debugging (Optional)

The repository provides **`scripts/shopify_store_query.py`** (Python 3, standard library only), which POSTs JSON matching the MCP input parameters to the Nexscope tool gateway.

- **Gateway**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ehunt/shopify/storeQuery` (can override root URL with `NEXSCOPE_PROXY_BASE_BASE`)
- **Authentication**: Environment variable `NEXSCOPE_API_KEY` (same as other `nexscope-*` skills; if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

```bash
export NEXSCOPE_API_KEY="<your-key>"
python scripts/shopify_store_query.py '{"searchKey": "fashion", "country": "US", "page": 1, "pageSize": 20}'
```
