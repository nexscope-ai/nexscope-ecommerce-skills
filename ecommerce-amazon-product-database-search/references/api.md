# Keepa Amazon Product Search API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/keepa/productSearch`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, read api_key from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| domain | string | Yes | Amazon domain ID: 1=United States, 2=United Kingdom, 3=Germany, 4=France, 5=Japan, 6=Canada, 8=Italy, 9=Spain, 10=India, 11=Mexico |
| keyword | string | No | Title keyword (case-insensitive; spaces mean AND tokenization; wrap keywords containing spaces in double quotes; prefix `-` for exclusion; `&` symbol is replaced with space; up to 50 keywords, max 1000 characters) |
| rootCategory | array[int] | No | Root category IDs (up to 50), only include products in these root categories |
| rootCategoryNames | array[string] | No | Root category names (up to 50), used when rootCategory is empty; the system automatically looks up corresponding category IDs |
| categoriesInclude | array[int] | No | Subcategory IDs to include only (up to 50), only include products directly listed in these subcategories |
| categoriesIncludeNames | array[string] | No | Subcategory names to include (up to 50), used when categoriesInclude is empty; the system automatically looks up corresponding category IDs. Supports full category paths (separated by `:` or `>`) for more accurate results |
| categoriesExclude | array[int] | No | Subcategory IDs to exclude (up to 50) |
| categoriesExcludeNames | array[string] | No | Subcategory names to exclude (up to 50), used when categoriesExclude is empty; the system automatically looks up corresponding category IDs. Supports full category paths for more accurate results |
| currentSalesGte / currentSalesLte | integer | No | Current sales rank range (lower value = better ranking) |
| avg90SalesGte / avg90SalesLte | integer | No | 90-day average sales rank range |
| deltaPercent90SalesGte / deltaPercent90SalesLte | integer | No | 90-day sales rank change percentage range |
| monthlySoldGte / monthlySoldLte | integer | No | Units sold / monthly sales range |
| srAvgGte / srAvgLte | integer | No | Historical sales rank range (positive integer, lower value = better ranking, used for the month specified by srAvgMonth) |
| srAvgMonth | string | No | Historical sales rank - selected month (format: YYYYMM, e.g., 202511 for November 2025, within the last 36 months) |
| currentNewGte / currentNewLte | integer | No | Current new price range (in minor currency unit) |
| currentBuyBoxShippingGte / currentBuyBoxShippingLte | integer | No | Current Buy Box price with shipping range (in minor currency unit) |
| currentCountReviewsGte / currentCountReviewsLte | integer | No | Current review count range |
| currentRatingGte / currentRatingLte | number | No | Current rating range (0.0-5.0) |
| packageLengthGte / packageLengthLte | integer | No | Package length range (mm) |
| packageWidthGte / packageWidthLte | integer | No | Package width range (mm) |
| packageHeightGte / packageHeightLte | integer | No | Package height range (mm) |
| packageWeightGte / packageWeightLte | integer | No | Package weight range (grams) |
| brand | array[string] | No | Brand (OR match) |
| color | array[string] | No | Color (OR match), filter products with specified colors |
| size | array[string] | No | Size (OR match), filter products with specified sizes |
| availableDateGte / availableDateLte | string | No | Product listing time range (date format: yyyy-MM-dd) |
| buyBoxIsAmazon | boolean | No | Whether the Buy Box seller is Amazon |
| buyBoxIsFBA | boolean | No | Whether the Buy Box is FBA |
| isHazMat | boolean | No | Whether it is hazardous material |
| variationCountGte / variationCountLte | integer | No | Variation count range |
| currentCountNewGte / currentCountNewLte | integer | No | Current new offer count range |
| outOfStockPercentage90Gte / outOfStockPercentage90Lte | integer | No | 90-day out-of-stock percentage range |
| singleVariation | boolean | No | Return only one variation; when set to true, multi-variation products will only return one variation |
| productType | array[int] | No | Product type filter (default [0,1,2]): 0=standard product, 1=downloadable product, 2=eBook, 5=variant parent ASIN |
| history | integer | No | Whether to include historical data / historical sales in the response (1=include, 0=exclude, default 0) |
| rating | integer | No | Whether to fetch rating info (1=fetch, 0=do not fetch, default 1) |
| page | integer | No | Page number (starting from 1, default 1) |
| perPage | integer | No | Maximum results per page (min 50, max 100, default 50) |
| sort | array[object] | No | Sort (up to 3): array of objects, each containing `{"fieldName": "...", "sortDirection": "asc\|desc"}`. Sortable fields: availableDate (listing time), currentSales (current sales rank), monthlySold (units sold / monthly sales), currentRating (current rating), currentCountReviews (current review count), currentBuyBoxShipping (current Buy Box price with shipping), currentNew (current new price) |

- For the request parameter `categoriesIncludeNames` category name, multi-level category names are supported, with levels separated by English colon `:`. Conversion should be automatic based on user input.

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
| total | integer | Total rows |
| perPage | integer | Items per page |
| currentPage | integer | Current page number |
| totalCount | integer | Total count |
| sourceType | string | Source type: keepa |
| type | string | Render style |
| columns | array | Rendered columns |
| costToken | integer | Token consumption |
| products | array | Product list (see below) |

### Product Object Fields

| Field | Type | Description |
|------|------|------|
| asin | string | ASIN |
| title | string | Product title |
| brand | string | Brand |
| manufacturer | string | Manufacturer |
| model | string | Model |
| price | number | Current price (in local currency, e.g., USD/EUR) |
| primePrice | number | Prime price |
| currency | string | Currency |
| salesRank | integer | Sales rank |
| salesRank30 | integer | Average sales rank in last 30 days |
| salesRank90 | integer | Average sales rank in last 90 days |
| salesRank180 | integer | Average sales rank in last 180 days |
| monthlySalesUnits | integer | Monthly sales units |
| monthlySalesRevenue | number | Monthly sales revenue |
| monthlySalesUnits1MonthAgo .. monthlySalesUnits12MonthsAgo | integer | Monthly sales units for each of the last 12 months |
| rating | number | Current rating (0.0-5.0) |
| ratings | integer | Number of ratings |
| reviewCount | integer | Number of reviews |
| availableDate | string | Listing time (yyyy-MM-dd HH:mm:ss) |
| lastUpdate | string | Last update time (yyyy-MM-dd HH:mm:ss) |
| imageUrl | string | Image URL (request address) |
| productImageUrls | array | Product image list |
| asinUrl | string | Amazon ASIN detail page URL |
| categoryTree | string | Category tree |
| categoryTreeId | string | Category tree ID |
| rootCategory | integer | Root category ID |
| subcategories | array | Subcategory list, containing code (category ID), rank (ranking), label (category name) |
| fulfillment | string | Fulfillment method (AMZ, FBA, FBM) |
| buyBoxSellerId | string | Buy Box seller ID |
| sellerNum | integer | Number of sellers |
| parentAsin | string | Parent ASIN |
| variationNum | integer | Number of variations |
| color | string | Color |
| dimension | string | Dimensions |
| dimensionsType | string | Dimensions type |
| material | string | Product material, the primary material used in its construction |
| weight | string | Weight (grams) |
| packageWeight | string | Package weight (grams) |
| packageLength | integer | Package length (mm) |
| packageWidth | integer | Package width (mm) |
| packageHeight | integer | Package height (mm) |
| packageDimensions | string | Package dimensions |
| packageQuantity | integer | Quantity of items in the package, 0 or -1 if unavailable |
| itemLength | integer | Item length (mm), 0 or -1 if unavailable |
| itemWidth | integer | Item width (mm), 0 or -1 if unavailable |
| itemHeight | integer | Item height (mm), 0 or -1 if unavailable |
| isAdultProduct | boolean | Whether it is an adult product |
| isHazmat | boolean | Whether it is hazardous material |
| referralFeePercentage | number | Referral fee percentage |
| fbaFees | number | FBA fulfillment fee (in local currency) |
| profit | number | Profit margin (percentage, e.g., 25.5 means 25.5%) |
| urlSlug | string | URL slug |
| sourceType | string | Source type: keepa |
| sourceTool | string | Source tool |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| - | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/keepa/productSearch \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"domain": "1", "keyword": "wireless charger", "monthlySoldGte": 500, "currentRatingGte": 4.0}'
```

---
