# Seller Sprite - Product Search API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sellersprite/productSearch`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON). The following fields are consistent with the currently registered "Seller Sprite - Product Search" input schema for the tool gateway (synced on 2026-04-30).

### Session / Gateway (Optional)

| Parameter | Type | Required | Description |
|------|------|------|------|
| chatId | string | No | Chat ID, `maxLength` 1000 |
| uid | string | No | User ID, `maxLength` 1000 |
| requestId | string | No | Push ID, `maxLength` 1000 |
| teamId | string | No | Team ID, `maxLength` 1000 |

### Search and Keywords

| Parameter | Type | Required | Description |
|------|------|------|------|
| keyword | string | No | Search keyword; translate to the corresponding country's language whenever possible, e.g. use English keywords for the US, German keywords for Germany, etc.; `maxLength` 10240 |
| matchType | integer | No | Match type: 1 = phrase match (default), 2 = fuzzy match, 3 = exact match |
| excludeKeywords | string | No | Exclude keywords; `maxLength` 10240 |
| marketplace | string | No | Marketplace site code, default `US`. **Only** `US`, `UK`, `DE`, `FR`, `JP`, `CA`, `IT`, `ES`, `MX`, `IN` are allowed (must match this enum; AU, TR, and other unlisted sites are not supported) |

### Category Filter

| Parameter | Type | Required | Description |
|------|------|------|------|
| nodeLabel | string | No | Amazon category name; `maxLength` 1000 |
| nodeIdPath | string | No | Amazon category node ID; `maxLength` 1000 |
| filterSubNode | boolean | No | Whether to filter subcategory nodes; only effective when nodeLabel or nodeIdPath has a value; pass JSON boolean `true` / `false` |

### Data Snapshot

| Parameter | Type | Required | Description |
|------|------|------|------|
| dataSnapshotMonth | string | No | Product data snapshot month, format `yyyyMM` (e.g. `202412` for December 2024 data snapshot), or `nearly` for last 30 days real-time data. Default: `nearly`. Used for historical analysis and period comparison; only supports existing historical snapshots, future dates are not supported; `maxLength` 1000 |

### Price and Profit

| Parameter | Type | Required | Description |
|------|------|------|------|
| minPrice | number | No | Minimum price (>= 0) |
| maxPrice | number | No | Maximum price (>= 0) |
| minProfit | number | No | Minimum gross margin, unit % (1-100) |
| maxProfit | number | No | Maximum gross margin, unit % (1-100) |
| minRevenue | number | No | Minimum monthly sales revenue (>= 0) |
| maxRevenue | number | No | Maximum monthly sales revenue (>= 0) |
| minFba | number | No | Minimum FBA shipping fee (>= 0) |
| maxFba | number | No | Maximum FBA shipping fee (>= 0) |

### Sales Volume and BSR

| Parameter | Type | Required | Description |
|------|------|------|------|
| minUnits | integer | No | Minimum monthly sales volume (>= 0) |
| maxUnits | integer | No | Maximum monthly sales volume (>= 0) |
| minAmzUnit | integer | No | Minimum variant last-30-day sales volume (**only** supported when `dataSnapshotMonth` is a "last 30 days" type query); `minimum` 0 |
| maxAmzUnit | integer | No | Maximum variant last-30-day sales volume (**only** supported for last 30 days queries); `minimum` 0 |
| minUnitsGrowthRate | number | No | Minimum monthly sales volume growth rate, unit % |
| maxUnitsGrowthRate | number | No | Maximum monthly sales volume growth rate, unit % |
| minBsr | integer | No | Lowest main category BSR rank |
| maxBsr | integer | No | Highest main category BSR rank |
| minBsrGrowthRate | number | No | Minimum BSR growth rate, unit % |
| maxBsrGrowthRate | number | No | Maximum BSR growth rate, unit % |
| minBsrGrowthCount | integer | No | Minimum BSR growth count |
| maxBsrGrowthCount | integer | No | Maximum main category BSR growth count |
| minSubNodeBsrRank | integer | No | Lowest subcategory BSR rank (requires filterSubNode = true) |
| maxSubNodeBsrRank | integer | No | Highest subcategory BSR rank (requires filterSubNode = true) |

### Ratings and Reviews

| Parameter | Type | Required | Description |
|------|------|------|------|
| minRating | number | No | Minimum rating value (0-5) |
| maxRating | number | No | Maximum rating value (0-5), 3.8-4.3 is the product improvement opportunity range |
| minRatings | integer | No | Minimum review count (0-10000) |
| maxRatings | integer | No | Maximum review count (0-10000) |
| minRatingsGrowthCount | integer | No | Minimum monthly new review count (>= 0) |
| maxRatingsGrowthCount | integer | No | Maximum monthly new review count (>= 0) |
| minListingQualityScore | number | No | Minimum Listing page quality score (>= 0) |
| maxListingQualityScore | number | No | Maximum Listing page quality score (>= 0) |

### Product Attributes

| Parameter | Type | Required | Description |
|------|------|------|------|
| minVariations | integer | No | Minimum number of variations |
| maxVariations | integer | No | Maximum number of variations |
| minWeights | number | No | Minimum weight (>= 0) |
| maxWeights | number | No | Maximum weight (>= 0) |
| weightUnit | string | No | Weight unit: g, kg, oz, lb. This field must be specified if the parameters include weight filtering |
| dimensionType | string | No | Package dimension type (codes vary by site, see below) |
| minSellers | integer | No | Minimum number of sellers |
| maxSellers | integer | No | Maximum number of sellers |

### Badges and Fulfillment

| Parameter | Type | Required | Description |
|------|------|------|------|
| badgeBestSeller | string | No | Best Seller badge filter: `Y`, `N`, or empty (all) |
| badgeAmazonsChoice | string | No | Amazon's Choice badge filter: `Y`, `N`, or empty (all) |
| badgeNewRelease | string | No | New Release badge filter: `Y`, `N`, or empty (all) |
| fulfillment | string | No | Fulfillment method: single select `AMZ` / `FBA` / `FBM`, or multi-select such as `AMZ,FBA`, `FBA,FBM`, `AMZ,FBA,FBM`, etc.; multiple conditions use comma separation; empty means no limit |
| showVariation | string | No | Whether to query variants: `Y` or `N`, default `N` |
| hideUnlistedProduct | boolean | No | Whether to hide delisted products, default `true` |
| listedWithinLastMonths | integer | No | Time since listing (months), **only** allowed: `1`, `3`, `6`, `12`, `24` (must match these enum values; do not pass other integers) |

### Sellers and Brands

| Parameter | Type | Required | Description |
|------|------|------|------|
| sellerNation | string | No | Seller location code (e.g. US, CN, HK), multiple conditions comma-separated, default no limit |
| includeSellers | string | No | Include sellers; `maxLength` 10240 |
| excludeSellers | string | No | Exclude sellers; `maxLength` 10240 |
| includeBrands | string | No | Include brands; `maxLength` 10240 |
| excludeBrands | string | No | Exclude brands; `maxLength` 10240 |

### Sort and Pagination

| Parameter | Type | Required | Description |
|------|------|------|------|
| order | object | No | Sort configuration; if passed, it is recommended to provide both `field` and `desc` (both are required in the sub-schema) |
| order.field | string | No | Sort field: `total_units` (monthly sales), `total_amount` (monthly revenue), `bsr_rank`, `price`, `rating`, `reviews`, `profit`, `reviews_rate`, `available_date`, `questions`, `total_units_growth`, `total_amount_growth`, `reviews_increasement`, `bsr_rank_cv`, `bsr_rank_cr`, `amz_unit` (variant sales). Default `total_units`. Pass an empty string `""` to not sort by the above business fields (full query sort semantics are handled by the server) |
| order.desc | string | No | `"true"` descending, `"false"` ascending; default `"true"`; `maxLength` 1000 |
| page | integer | No | Page number, starting from 1, default 1 |
| size | integer | No | Results per page (10-100), default 20 |

## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Total matching product count |
| products | array | Product list (see product object fields below) |
| columns | array | Render column definitions |
| keyword | string | Search keyword used (if any) |
| nodeIdPath | string | Searched category node |
| nodeLabel | string | Amazon category name |
| dataSnapshotMonth | string | Data query month |
| sourceType | string | Source type (e.g. "amazon") |
| type | string | Render style |
| message | string | Additional message or error info |
| costToken | integer | Tokens consumed |

### Product Object Fields

| Field | Type | Description |
|------|------|------|
| asin | string | Amazon ASIN |
| title | string | Product title |
| asinUrl | string | Amazon product detail page URL |
| imageUrl | string | Product image URL |
| price | number | Current price |
| averagePrice | number | Average price |
| primePrice | number | Prime price, -1 means not available |
| currency | string | Currency |
| monthlySalesUnits | integer | Monthly sales volume |
| monthlySalesRevenue | number | Monthly sales revenue |
| monthlySalesUnitsGrowthRate | number | Monthly sales volume growth rate |
| bsr | integer | BSR rank |
| bsrGrowthRate | number | BSR growth rate |
| rating | number | Rating |
| ratings | integer | Review count |
| ratingsRate | number | Review rate |
| profit | number | Gross margin (%) |
| fba | number | FBA shipping fee |
| sellerNum | integer | Number of sellers |
| sellerId | string | BuyBox seller ID |
| sellerName | string | BuyBox seller name |
| sellerNation | string | BuyBox seller nationality |
| brand | string | Brand |
| brandUrl | string | Brand page URL |
| fulfillment | string | Fulfillment method (AMZ / FBA / FBM) |
| availableDate | string | Listing time (timestamp) |
| availableDateString | string | Listing date (formatted string) |
| variationNum | integer | Number of variations |
| variant30DayUnits | integer | Variant monthly sales (units) |
| variant30DayRevenue | number | Variant monthly sales revenue (amount) |
| variant30DayUpdatedAt | string | Variant data update time |
| weight | string | Weight |
| packageWeight | string | Package weight |
| dimension | string | Dimensions |
| packageDimensions | string | Package dimensions |
| dimensionsType | string | Dimension type |
| packageDimensionType | string | Package dimension type |
| listingQualityScore | number | Listing quality score |
| deliveryPrice | number | Seller shipping fee, -1 means not available |
| nodeLabelPath | string | Category path |
| nodeIdPath | string | Node ID path |
| nodeId | integer | Node ID |
| dataSnapshotMonth | string | Data query month |
| badgeBestSeller | string | Best Seller badge (Y/N) |
| badgeAmazonChoice | string | Amazon's Choice badge (Y/N) |
| badgeNewRelease | string | New Release badge (Y/N) |
| badgeVideo | string | Video introduction (Y/N) |
| badgeEbc | string | A+ page (Y/N) |
| badge | object | Badge summary object, containing: bestSeller, amazonChoice, newRelease, video, ebc |
| subcategories | array | Subcategory list, each entry containing code (category code), rank (rank), label (name) |
| sku | string | SKU |
| keyword | string | Matching keyword |
| sourceType | string | Source type |
| sourceTool | string | Source tool identifier |

## Package Dimension Type Codes by Marketplace

### US Marketplace

| Code | Description |
|------|-------------|
| SS | Small standard-size |
| LS | Large standard-size |
| SO | Small oversize |
| MO | Medium oversize |
| LO / LB | Large oversize |
| SP | Special oversize |
| O | Other sizes |
| ELO | Extra-large oversize: 0 to 50 lb |
| EL5O | Extra-large oversize: 50 to 70 lb (excl. 50 lb) |
| EL7O | Extra-large oversize: 70 to 150 lb (excl. 70 lb) |
| EL15O | Extra-large oversize: over 150 lb (excl. 150 lb) |

### Japan Marketplace (JP)

| Code | Description |
|------|-------------|
| SM | Small |
| ST | Standard |
| OV | Oversize |
| SS | Extra-large size |
| O | Other sizes |

### Canada Marketplace (CA)

| Code | Description |
|------|-------------|
| EN | Envelope |
| ST | Standard |
| SO | Small oversize |
| MO | Medium oversize |
| LO | Large oversize |
| SP | Special oversize |
| O | Other sizes |

### UK / France / Germany / Italy / Spain (UK / FR / DE / IT / ES)

| Code | Description |
|------|-------------|
| SL | Small envelope |
| NL | Standard envelope |
| LL | Large envelope |
| ELL | Extra-large envelope |
| SM | Small parcel |
| SD | Standard parcel |
| SB | Small oversize |
| NB | Standard oversize |
| LB | Large oversize |
| SPO | Special oversize |
| O | Other sizes |

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

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sellersprite/productSearch \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "yoga mat",
    "marketplace": "US",
    "minUnits": 300,
    "minPrice": 10,
    "maxPrice": 50,
    "order": {"field": "total_units", "desc": "true"},
    "page": 1,
    "size": 20
  }'
```

## Response Example (Abbreviated)

```json
{
  "total": 1523,
  "sourceType": "amazon",
  "dataSnapshotMonth": "nearly",
  "keyword": "yoga mat",
  "nodeLabel": "",
  "products": [
    {
      "asin": "B07XXXXXXX",
      "title": "Premium Yoga Mat - Non Slip, Eco Friendly...",
      "price": 29.99,
      "monthlySalesUnits": 12500,
      "monthlySalesRevenue": 374875.0,
      "bsr": 156,
      "rating": 4.6,
      "ratings": 35420,
      "profit": 42.5,
      "fulfillment": "FBA",
      "brand": "ExampleBrand",
      "sellerNation": "CN",
      "availableDateString": "2021-03-15",
      "badgeBestSeller": "Y",
      "badgeAmazonChoice": "N"
    }
  ],
  "message": "",
  "costToken": 1
}
```

---
