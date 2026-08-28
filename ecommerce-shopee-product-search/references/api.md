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

Under normal circumstances, the HTTP status code is 200. Business success or failure is distinguished by the `errorCode` field in the response body (`errorCode = 200` indicates success; other values indicate business errors). When unauthorized, the HTTP status code is 401, and the corresponding errorCode is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields such as `products` normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| 402 | - | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| Other non-200 values | Business exception | Refer to the `errmsg` field for the specific error reason |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/youying/shopee/getProductInfos \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"station": "malaysia", "keyword": "Storage Box", "keywordType": 2, "soldMin": 100, "orderBy": "sold", "orderByType": "DESC", "pageSize": 50}'
```

---
