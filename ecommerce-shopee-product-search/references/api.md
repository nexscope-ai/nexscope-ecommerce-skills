# Youying-Shopee Product Selection API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/youying/shopee/getProductInfos`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

### Required Parameters

  | Parameter | Type | Description |  
|------|------|------|
| station | string | **Required**. Shopee site, accepts name or code. See site mapping table below |

### Site Mapping

| Site | station value | Code |
|------|-----------|------|
| Malaysia | malaysia | MY |
| Taiwan, China | taiwan_china | Taiwan_CHN |
| Indonesia | indonesia | ID |
| Thailand | thailand | TH |
| Philippines | philippines | PH |
| Singapore | singapore | SG |
| Vietnam | vietnam | VN |
| Brazil | brazil | BR |
| Mexico | mexico | MX |
| Chile | chile | CL |
| Colombia | columbia | CO |

### Keyword Filtering

  | Parameter | Type | Description |  
|------|------|------|
| keyword | string | Product title keyword |
| keywordType | integer | Match mode: 1=Exact phrase (default), 2=Multi-word AND, 3=Multi-word OR |
| notExistKeyword | string | Exclude products containing this keyword |
| notExistKeywordType | integer | Exclusion match mode: 1=Exact phrase (default), 2=Multi-word AND, 3=Multi-word OR |

### Price Filtering

  | Parameter | Type | Description |  
|------|------|------|
| priceMin | number | Minimum total product price (local currency) |
| priceMax | number | Maximum total product price |

### Sales Filtering

  | Parameter | Type | Description |  
|------|------|------|
| soldMin | integer | Minimum units sold in last 30 days |
| soldMax | integer | Maximum units sold in last 30 days |
| estimateSoldStart | integer | Minimum estimated units sold in last 30 days |
| estimateSoldEnd | integer | Maximum estimated units sold in last 30 days |
| historicalSoldStart | integer | Minimum total historical units sold |
| historicalSoldEnd | integer | Maximum total historical units sold |
| paymentStart | number | Minimum sales revenue in last 30 days |
| paymentEnd | number | Maximum sales revenue in last 30 days |

### Rating Filtering

  | Parameter | Type | Description |  
|------|------|------|
| ratingMin | number | Minimum product rating (0-5) |
| ratingMax | number | Maximum product rating |
| ratingsMin | integer | Minimum number of ratings |
| ratingsMax | integer | Maximum number of ratings |
| favoriteMin | integer | Minimum number of favorites |
| favoriteMax | integer | Maximum number of favorites |

### SKU Filtering

  | Parameter | Type | Description |  
|------|------|------|
| skuNumberStart | integer | Minimum total SKU count |
| skuNumberEnd | integer | Maximum total SKU count |

### Time Filtering

  | Parameter | Type | Description |  
|------|------|------|
| listingDateFrom | string | Product listing date range start (format: yyyy-MM-dd) |
| listingDateTo | string | Product listing date range end (format: yyyy-MM-dd) |
| statTimeStart | string | Statistics time range start (format: yyyy-MM-dd HH:mm:ss) |
| statTimeEnd | string | Statistics time range end (format: yyyy-MM-dd HH:mm:ss) |
| lastModiTimeStart | string | Latest crawl time range start (format: yyyy-MM-dd) |
| lastModiTimeEnd | string | Latest crawl time range end (format: yyyy-MM-dd) |
| approvedDateStart | string | Store opening time range start (format: yyyy-MM-dd) |
| approvedDateEnd | string | Store opening time range end (format: yyyy-MM-dd) |

### Category Filtering

  | Parameter | Type | Description |  
|------|------|------|
| pL1Id | string | Level 1 category ID |
| pL2Id | string | Level 2 category ID |
| pL3Id | string | Level 3 category ID |
| cidList | string | Category ID list, full path, multiple groups separated by `|`, e.g.: `AAA,BBB,CCC|DDD,EEE` |

### Store Filtering

  | Parameter | Type | Description |  
|------|------|------|
| shopIdList | string | Specific store ID list, comma-separated |
| notExistShopIdList | string | Excluded store ID list, comma-separated |
| merchant | string | Store name or username |
| shopLocation | string | Store location |

### Product Attribute Filtering

  | Parameter | Type | Description |  
|------|------|------|
| shippingIconType | integer | Store location type: 0=Local, 1=Overseas |
| cbOption | integer | Shipping origin: 0=Local, 1=Cross-border |
| isShopeeVerified | integer | Shopee Preferred: 0=Not preferred, 1=Preferred |
| isOfficialShop | integer | Official store: 0=No, 1=Yes |
| isHotSales | integer | Hot selling: 0=Not hot, 1=Hot |
| pids | string | Product ID list (max 500), comma-separated |

### Sorting and Pagination

  | Parameter | Type | Default | Description |  
|------|------|--------|------|
| orderBy | string | - | Sort field: `rating`, `price`, `historical_sold` (total sales), `sold` (30-day sales), `payment` (30-day revenue), `favorite`, `ratings`, `gen_time` (listing time), `estimate_sold` (estimated sales) |
| orderByType | string | DESC | Sort direction: `ASC` (ascending), `DESC` (descending) |
| page | integer | 1 | Page number (starting from 1) |
| pageSize | integer | 1000 | Products per page (range 1-1000) |

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Number of records returned in current response |
| totalSize | integer | Total number of results |
| sourceTool | string | Source tool identifier |
| sourceType | string | Source type: `shopee` |
| columns | array | Column definitions for rendering |
| costToken | integer | Tokens consumed |
| type | string | Render style |
| products | array | Product list (see fields below) |

### Each product object in the products array

| Field | Type | Description |
|------|------|------|
| pid | string | Unique product ID |
| title | string | Product title |
| description | string | Product description |
| imageUrl | string | Product main image URL |
| productUrl | string | Shopee product link |
| price | number | Default product price (local currency) |
| minPrice | number | Lowest SKU price |
| maxPrice | number | Highest SKU price |
| sold | integer | Units sold in last 30 days |
| estimateSold | integer | Estimated units sold in last 30 days |
| historicalSold | integer | Total historical units sold |
| payment | number | Sales revenue in last 30 days (local currency) |
| rating | number | Product rating (0-5) |
| ratings | integer | Number of ratings |
| favorite | integer | Number of favorites |
| viewCount | integer | View count |
| stock | integer | Stock quantity |
| skuNumber | integer | Number of SKUs |
| genTime | string | Listing time |
| statTime | string | Statistics time |
| lastModiTime | string | Latest crawl time |
| categoryStructure | string | Category structure path |
| cid | string | Category ID (comma-separated) |
| shopId | string | Store ID |
| shopName | string | Store name |
| shopUrl | string | Store link |
| userName | string | Store owner name |
| shopLocation | string | Store location |
| shopProductsCount | integer | Total products in store |
| approvedDate | string | Store opening time |
| isOfficialShop | integer | Whether official store (1=Yes, 0=No) |
| isShopeeVerified | integer | Shopee Preferred (1=Yes, 0=No) |
| isHotSales | integer | Whether hot selling (1=Yes, 0=No) |
| shippingIconType | integer | Store location type (0=Local, 1=Overseas, 3 or null=Unknown) |
| cbOption | integer | Shipping origin (0=Local, 1=Cross-border) |
| estimatedDays | integer | Estimated delivery days |
| status | integer | Product status (1=Active, 0=Delisted, 8=Excluded from listing) |
| notExist | integer | Whether exists (0=Exists, 1=Does not exist) |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| - | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/youying/shopee/getProductInfos \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"station": "malaysia", "keyword": "Storage Box", "keywordType": 2, "soldMin": 100, "orderBy": "sold", "orderByType": "DESC", "pageSize": 50}'
```

---
