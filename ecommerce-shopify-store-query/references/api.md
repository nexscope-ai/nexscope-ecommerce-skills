# Shopify Store Query API Reference

## Usage Notes

- **Gateway route**: `POST ehunt/shopify/storeQuery` (full: `${NEXSCOPE_PROXY_BASE}Query`).
- **MCP display name**: Shopify Store Query (the exact tool name is subject to the tool metadata deployed in the current environment).
- **Authentication**: Request header `Authorization: <api_key>`, api_key read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md).
- **Note**: Parameters and response structure are subject to the actual gateway response; if the upstream returns a root-level `code` field in JSON, the success value (`200`) is subject to the actual network response. The gateway may throw an error when there is no data.

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

The repository provides **`scripts/shopify_store_query.py`** (Python 3, standard library only), which POSTs JSON matching the MCP input parameters to the NexScope tool gateway.

- **Gateway**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ehunt/shopify/storeQuery` (can override root URL with `NEXSCOPE_PROXY_BASE_BASE`)
- **Authentication**: Environment variable `NEXSCOPE_API_KEY` (same as other `nexscope-*` skills; if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

```bash
export NEXSCOPE_API_KEY="<your-key>"
python scripts/shopify_store_query.py '{"searchKey": "fashion", "country": "US", "page": 1, "pageSize": 20}'
```

