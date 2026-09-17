# Jungle Scout Product Database Query API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/tool-jungle-scout/product-database/query`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, read api_key from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)

## Request Parameters

POST Body (JSON):

### Required Parameters

| Parameter | Type | Required | Description |
|------|------|------|------|
| marketplace | string | Yes | Target marketplace code. Options: `us`, `uk`, `de`, `in`, `ca`, `fr`, `it`, `es`, `mx`, `jp` |

### Keyword Filters

| Parameter | Type | Required | Description |
|------|------|------|------|
| includeKeywords | string | No | Keywords to include in title/ASIN, comma-separated, up to 100 items, max 50 chars each |
| excludeKeywords | string | No | Keywords to exclude from title/ASIN, comma-separated, up to 100 items, max 50 chars each |

### Category Filters

| Parameter | Type | Required | Description |
|------|------|------|------|
| categories | string | No | Primary category names, comma-separated, must match the standard category names for the corresponding site. US site examples: Appliances, Arts Crafts & Sewing, Automotive, Baby, Beauty & Personal Care, Books, CDs & Vinyl, Cell Phones & Accessories, Clothing Shoes & Jewelry, Collectibles & Fine Art, Computers, Digital Music, Electronics, Garden & Outdoor, Grocery & Gourmet Food, Handmade, Health Household & Baby Care, Home & Kitchen, Industrial & Scientific, Kindle Store, Kitchen & Dining, Movies & TV, Musical Instruments, Office Products, Pet Supplies, Sports & Outdoors, Tools & Home Improvement, Toys & Games, Video Games, etc. Other sites (uk, de, fr, it, es, mx, jp, ca, in) have their own localized category names |

### Price / Sales / Revenue

| Parameter | Type | Required | Description |
|------|------|------|------|
| minPrice | number | No | Minimum price |
| maxPrice | number | No | Maximum price |
| minSales | integer | No | Minimum monthly sales |
| maxSales | integer | No | Maximum monthly sales |
| minRevenue | number | No | Minimum monthly revenue |
| maxRevenue | number | No | Maximum monthly revenue |

### Reviews / Rating

| Parameter | Type | Required | Description |
|------|------|------|------|
| minReviews | integer | No | Minimum number of reviews |
| maxReviews | integer | No | Maximum number of reviews |
| minRating | number | No | Minimum rating (1.0-5.0) |
| maxRating | number | No | Maximum rating (1.0-5.0) |

### Weight / Dimensions / BSR

| Parameter | Type | Required | Description |
|------|------|------|------|
| minWeight | number | No | Minimum weight (lbs) |
| maxWeight | number | No | Maximum weight (lbs) |
| minRank | integer | No | Minimum BSR ranking |
| maxRank | integer | No | Maximum BSR ranking |
| minLqs | integer | No | Minimum LQS score (1-10) |
| maxLqs | integer | No | Maximum LQS score (1-10) |

### Sellers / Product Type

| Parameter | Type | Required | Description |
|------|------|------|------|
| minSellers | integer | No | Minimum number of sellers |
| maxSellers | integer | No | Maximum number of sellers |
| minNet | number | No | Minimum net profit |
| maxNet | number | No | Maximum net profit |
| sellerTypes | string | No | Seller types, comma-separated. Options: `amz` (Amazon self-operated), `fba`, `fbm` |
| productTiers | string | No | Product size tiers, comma-separated. Options: `oversize`, `standard` |
| excludeTopBrands | boolean | No | Whether to exclude top brands |
| excludeUnavailableProducts | boolean | No | Whether to exclude unavailable products |

### Date / Pagination / Sorting

| Parameter | Type | Required | Description |
|------|------|------|------|
| minUpdatedAt | string | No | Data update start date (YYYY-MM-DD) |
| maxUpdatedAt | string | No | Data update end date (YYYY-MM-DD) |
| needCount | integer | No | Total number of results to return, API auto-paginates internally |
| sort | string | No | Sort field. Options: `name`, `-name`, `category`, `-category`, `revenue`, `-revenue`, `sales`, `-sales`, `price`, `-price`, `rank`, `-rank`, `reviews`, `-reviews`, `lqs`, `-lqs`, `sellers`, `-sellers`. Prefix `-` indicates descending. Default: `name` |

### Site Mapping

| Site | marketplace value |
|------|---------------|
| United States | us |
| United Kingdom | uk |
| Germany | de |
| India | in |
| Canada | ca |
| France | fr |
| Italy | it |
| Spain | es |
| Mexico | mx |
| Japan | jp |

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
| costToken | integer | Token consumption |
| productDatabaseList | array | Product data list |

### Each Object in productDatabaseList Array

| Field | Type | Description |
|------|------|------|
| id | string | Product unique identifier |
| title | string | Product title |
| brand | string | Brand name |
| category | string | Primary category |
| breadcrumbPath | string | Full category path |
| price | number | Current selling price (USD) |
| approximate30DayUnitsSold | integer | Estimated units sold in last 30 days |
| approximate30DayRevenue | number | Estimated revenue in last 30 days (USD) |
| productRank | integer | BSR ranking |
| reviews | integer | Total number of reviews |
| rating | number | Average rating (1.0-5.0) |
| listingQualityScore | integer | Listing quality score (LQS, 1-10) |
| numberOfSellers | integer | Number of active sellers |
| sellerType | string | Seller type (amz/fba/fbm) |
| imageUrl | string | Product main image URL |
| dateFirstAvailable | string | Date first listed |
| weightValue | number | Product weight |
| weightUnit | string | Weight unit |
| lengthValue | number | Length |
| widthValue | number | Width |
| heightValue | number | Height |
| dimensionsUnit | string | Dimensions unit |
| parentAsin | string | Parent ASIN |
| isParent | boolean | Whether it is a parent listing |
| isVariant | boolean | Whether it is a variant |
| isStandalone | boolean | Whether it is a standalone product |
| isAvailable | boolean | Whether it is available for purchase |
| buyBoxOwner | string | Buy Box owner seller name |
| buyBoxOwnerSellerId | string | Buy Box owner seller ID |
| updatedAt | string | Data update time |
| feeBreakdown | object | Fee details: `fbaFee` (FBA fee), `referralFee` (referral fee), `variableClosingFee` (variable closing fee), `totalFees` (total fees) |
| subcategoryRanks | array | Subcategory BSR ranking list, each item contains `subcategory`, `rank`, `id` |
| type | string | Resource type |
| variants | array | Variant list |
| upcList | array | UPC code list |
| eanList | array | EAN code list |
| isbnList | array | ISBN code list |
| gtinList | array | GTIN code list |
| dateFirstAvailableIsEstimated | boolean | Whether the listing date is estimated |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| Insufficient credits | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/tool-jungle-scout/product-database/query \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "marketplace": "us",
    "includeKeywords": "yoga mat",
    "minSales": 300,
    "maxPrice": 50,
    "minRating": 4.0,
    "sort": "-sales",
    "needCount": 20
  }'
```

---
