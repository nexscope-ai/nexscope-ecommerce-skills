# Seller Sprite - Competitor Lookup API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/sellersprite/competitor-lookup`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| marketplace | string | No | Amazon site code, default `US`. Options: US, UK, DE, FR, JP, CA, IT, ES, MX, AU, TR, IN |
| keyword | string | No | Search keyword. Translate to the corresponding country's language whenever possible, e.g. use English keywords for the US, German keywords for Germany, etc. |
| asinList | string | No | ASINs, multiple ASINs comma-separated, max 40. Format: `^[A-Z0-9]+(,[A-Z0-9]+){0,39}$` |
| sellerName | string | No | Seller name filter |
| brand | string | No | Brand name filter |
| nodeLabel | string | No | Amazon category name, supports multi-level category names, levels separated by colon `:`, e.g. `Electronics:Headphones` |
| nodeIdPath | string | No | Amazon category ID path |
| matchType | integer | No | Match type. 1 = phrase match (default), 2 = fuzzy match, 3 = exact match |
| showVariation | string | No | Whether to query variants. `Y` = yes, `N` = no (default) |
| dataSnapshotMonth | string | No | Amazon product data snapshot month. Default `nearly` (queries last 30 days real-time data). Use `yyyyMM` format to query historical snapshots (e.g. `202412` for December 2024). Only supports existing historical snapshots, future dates are not supported. Recommended for seasonal analysis to query the same period last year's snapshot for comparison |
| page | integer | No | Page number, starting from 1 (default 1) |
| size | integer | No | Results per page, returns 10-100 records (default 50) |
| order | object | No | Sort configuration (see below) |

### Sort Object (order)

| Field | Type | Required | Description |
|------|------|------|------|
| field | string | Yes | Sort field. Options: `total_units` (monthly sales), `total_amount` (monthly revenue), `bsr_rank` (BSR rank), `price` (price), `rating` (rating), `reviews` (review count), `profit` (gross margin), `reviews_rate` (review rate), `available_date` (listing time), `questions` (Q&A count), `total_units_growth` (monthly sales growth rate), `total_amount_growth` (monthly revenue growth rate), `reviews_increasement` (monthly new review count), `bsr_rank_cv` (7-day BSR growth count), `bsr_rank_cr` (7-day BSR growth rate), `amz_unit` (variant sales). Default: `total_units` |
| desc | string | Yes | Sort direction. `true` = descending, `false` = ascending. Default: `true` |

## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Total matching result count |
| sourceType | string | Source type (e.g. `amazon`) |
| message | string | Execution message or error description |
| type | string | Render style |
| nodeLabel | string | Category name echo |
| columns | array | Render column definitions |
| products | array | Competitor list (see below) |
| costToken | integer | Tokens consumed |

### Competitor Object Fields (products)

| Field | Type | Description |
|------|------|------|
| asin | string | Product ASIN |
| title | string | Product title |
| price | number | Current price |
| primePrice | number | Prime price |
| averagePrice | number | Average price |
| currency | string | Currency |
| monthlySalesUnits | integer | Monthly sales volume (units) |
| monthlySalesRevenue | number | Monthly sales revenue |
| monthlySalesUnitsGrowthRate | number | Monthly sales volume growth rate |
| bsr | integer | BSR rank |
| bsrGrowthRate | number | BSR growth rate |
| bsrGrowthCount | integer | BSR growth count |
| rating | number | Rating |
| ratings | integer | Review count |
| ratingsGrowth | integer | Monthly new review count |
| ratingsRate | number | Review rate |
| brand | string | Brand |
| brandUrl | string | Brand URL |
| sellerName | string | BuyBox seller name |
| sellerId | string | BuyBox seller ID |
| sellerNation | string | BuyBox seller nationality |
| sellerNum | integer | Number of sellers |
| fulfillment | string | Fulfillment method: AMZ, FBA, FBM |
| availableDate | string | Listing time (date format) |
| availableDateString | string | Listing date (string format) |
| profit | number | Gross margin |
| fba | number | FBA shipping fee |
| deliveryPrice | number | Seller shipping fee |
| imageUrl | string | Product image URL |
| parent | string | Parent ASIN |
| variationNum | integer | Number of variations |
| variant30DayUnits | integer | Variant monthly sales (units) |
| variant30DayRevenue | number | Variant monthly sales revenue |
| variant30DayUpdatedAt | string | Variant data update time (timestamp) |
| amzUnitDateString | string | Variant sales update date |
| listingQualityScore | number | Listing quality score |
| nodeLabelPath | string | Category path |
| nodeIdPath | string | Node ID path |
| nodeId | integer | Node ID |
| dimension | string | Product dimensions |
| dimensionsType | string | Dimension type |
| weight | string | Product weight |
| packageDimensions | string | Package dimensions |
| packageDimensionType | string | Package dimension type |
| packageWeight | string | Package weight |
| sku | string | SKU |
| keyword | string | Matching keyword (if searched by keyword, displays the corresponding keyword) |
| dataSnapshotMonth | string | Data query month |
| sourceTool | string | Source tool |
| sourceType | string | Source type |
| badgeBestSeller | string | Best Seller badge (Y/N) |
| badgeAmazonChoice | string | Amazon's Choice badge (Y/N) |
| badgeNewRelease | string | New Release badge (Y/N) |
| badgeEbc | string | A+ page (Y/N) |
| badgeVideo | string | Video introduction (Y/N) |
| badge | object | Badge detail object, containing: `bestSeller`, `amazonChoice`, `newRelease`, `ebc`, `video` (all Y/N strings) |
| subcategories | array | Subcategory rankings, each entry containing `code` (category code), `rank` (rank), `label` (name) |

## curl Example

### Keyword Search

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/sellersprite/competitor-lookup \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "US", "keyword": "wireless earbuds", "matchType": 1, "size": 20}'
```

### ASIN Query

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/sellersprite/competitor-lookup \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "US", "asinList": "B072MQ5BRX,B08N5WRWNW"}'
```

### Sort by Monthly Revenue with Pagination

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/sellersprite/competitor-lookup \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "US", "keyword": "phone case", "order": {"field": "total_amount", "desc": "true"}, "page": 1, "size": 50}'
```

### Historical Snapshot Query

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/sellersprite/competitor-lookup \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "US", "keyword": "space heater", "dataSnapshotMonth": "202412", "order": {"field": "total_units", "desc": "true"}, "size": 20}'
```

## Error Codes

Under normal circumstances, the HTTP status code is 200. Business success or failure is determined by the `errorCode` field in the response body (errorCode = 200 indicates success; other values indicate business errors). When encountering unauthorized access, the HTTP status code is 401 and the corresponding errorCode is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse `products` and other business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| 402 | Insufficient credits | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| Other non-200 values | Business error | Refer to the `errmsg` field for specific error details |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

---
