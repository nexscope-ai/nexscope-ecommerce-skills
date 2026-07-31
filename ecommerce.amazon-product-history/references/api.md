# Keepa Amazon Product Detail API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/keepa/productRequest`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, read api_key from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| asin | string | Yes | Amazon Standard Identification Number (ASIN), multiple ASINs separated by English commas, up to 5, max length 300 characters. Example: `B0088PUEPK` or `B0088PUEPK,B00U26V4VQ,B07M68S376` |
| domain | string | Yes | Amazon domain ID. Options: `1` (United States), `2` (United Kingdom), `3` (Germany), `4` (France), `5` (Japan), `6` (Canada), `8` (Italy), `9` (Spain), `10` (India), `11` (Mexico), `12` (Brazil) |
| history | integer | No | Whether to include historical data and historical sales in the response. `1` = include price history, sales rank, historical sales and other time-series data (sales for previous months), `0` = return only basic product information. Default: `0` |


## Response Structure

### Top-level Fields

| Field | Type | Description |
|------|------|------|
| total | integer | Total rows |
| perPage | integer | Items per page |
| sourceType | string | Source type: keepa |
| columns | array | Rendered columns |
| costToken | integer | Token consumption |
| totalCount | integer | Total count |
| currentPage | integer | Current page number |
| type | string | Render style |
| products | array | Product list (see below) |

### Product Object Fields

| Field | Type | Description |
|------|------|------|
| asin | string | ASIN |
| title | string | Product title |
| brand | string | Brand |
| manufacturer | string | Manufacturer |
| model | string | Model |
| color | string | Color |
| material | string | Product material, the primary material used in its construction |
| price | number | Current price (in local currency, e.g., USD/EUR) |
| primePrice | number | Prime price |
| currency | string | Currency |
| rating | number | Current rating (0.0-5.0, e.g., 4.5 stars) |
| ratings | integer | Number of ratings |
| reviewCount | integer | Number of reviews |
| salesRank | integer | Sales rank |
| salesRank30 | integer | Average sales rank in last 30 days |
| salesRank90 | integer | Average sales rank in last 90 days |
| salesRank180 | integer | Average sales rank in last 180 days |
| monthlySalesUnits | integer | Monthly sales units |
| monthlySalesRevenue | number | Monthly sales revenue |
| monthlySalesUnits1MonthAgo | integer | Monthly sales 1 month ago |
| monthlySalesUnits2MonthsAgo | integer | Monthly sales 2 months ago |
| monthlySalesUnits3MonthsAgo | integer | Monthly sales 3 months ago |
| monthlySalesUnits4MonthsAgo | integer | Monthly sales 4 months ago |
| monthlySalesUnits5MonthsAgo | integer | Monthly sales 5 months ago |
| monthlySalesUnits6MonthsAgo | integer | Monthly sales 6 months ago |
| monthlySalesUnits7MonthsAgo | integer | Monthly sales 7 months ago |
| monthlySalesUnits8MonthsAgo | integer | Monthly sales 8 months ago |
| monthlySalesUnits9MonthsAgo | integer | Monthly sales 9 months ago |
| monthlySalesUnits10MonthsAgo | integer | Monthly sales 10 months ago |
| monthlySalesUnits11MonthsAgo | integer | Monthly sales 11 months ago |
| monthlySalesUnits12MonthsAgo | integer | Monthly sales 12 months ago |
| availableDate | string | Listing time (yyyy-MM-dd HH:mm:ss) |
| lastUpdate | string | Last update time (yyyy-MM-dd HH:mm:ss) |
| imageUrl | string | Image URL (request address) |
| productImageUrls | array | Product image list |
| asinUrl | string | Amazon ASIN detail page URL |
| urlSlug | string | URL slug |
| itemLength | integer | Item length in millimeters, 0 or -1 if unavailable |
| itemWidth | integer | Item width in millimeters, 0 or -1 if unavailable |
| itemHeight | integer | Item height in millimeters, 0 or -1 if unavailable |
| dimension | string | Dimensions |
| dimensionsType | string | Dimensions type |
| weight | string | Weight (grams) |
| packageLength | integer | Package length (mm) |
| packageWidth | integer | Package width (mm) |
| packageHeight | integer | Package height (mm) |
| packageWeight | string | Package weight (grams) |
| packageDimensions | string | Package dimensions |
| packageQuantity | integer | Quantity of items in the package, 0 or -1 if unavailable |
| fulfillment | string | Fulfillment method (AMZ, FBA, FBM) |
| fbaFees | number | FBA fulfillment fee (in local currency) |
| referralFeePercentage | number | Referral fee percentage |
| profit | number | Profit margin (percentage, e.g., 25.5 means 25.5%) |
| buyBoxSellerId | string | Buy Box seller ID |
| sellerNum | integer | Number of sellers |
| variationNum | integer | Number of variations |
| parentAsin | string | Parent ASIN |
| rootCategory | integer | Root category ID |
| categoryTree | string | Category tree |
| categoryTreeId | string | Category tree ID |
| subcategories | array | Subcategory list, each element contains `code` (category ID), `rank` (ranking), `label` (category name) |
| isAdultProduct | boolean | Whether it is an adult product |
| isHazmat | boolean | Whether it is hazardous material |
| sourceType | string | Source type: keepa |
| sourceTool | string | Source tool |

## Error Codes

Under normal conditions, the HTTP status code is always 200. Business success or failure is determined by the errorCode field in the response body (errorCode = 200 indicates success; other values indicate business errors). In cases of unauthorized access, the HTTP status code will be 401, with the corresponding errorCode also being 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| 402 | Insufficient credits | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| Other non-200 values | Business exception | Refer to the `errmsg` field for specific error cause |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/keepa/productRequest \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"asin": "B0088PUEPK", "domain": "1", "history": 1}'
```

### Batch Query Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/keepa/productRequest \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"asin": "B0088PUEPK,B00U26V4VQ,B07M68S376", "domain": "1", "history": 0}'
```

---
