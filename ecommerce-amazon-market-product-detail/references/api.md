# Sorftime Product Detail (with Trends) API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/amazon/productDetail`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| asin | string | Yes | Amazon Standard Identification Number (ASIN), supports multiple (max 10), comma-separated. Example: `B0088PUEPK` or `B0088PUEPK,B00U26V4VQ` |
| marketplace | string | Yes | Amazon site code: us, gb, de, fr, in, ca, jp, es, it, mx, ae, au, br, sa |
| includeTrend | integer | No | Whether to include trend data. `1`: include (default); `2`: exclude |
| queryTrendStartDate | string | No | Trend start date, format `yyyy-MM-dd`. Default returns only the last 15 days; querying more than 15 days doubles the cost |
| queryTrendEndDate | string | No | Trend end date, format `yyyy-MM-dd` |

## Response Structure

### Top-Level Fields

| Field | Type | Description |
|------|------|------|
| code | integer | Response code (200 indicates success) |
| msg | string | Response message |
| total | integer | Total result count |
| costTime | integer | Latency (ms) |
| costToken | integer | Tokens consumed |
| requestConsumed | integer | Requests consumed |
| sourceType | string | Source type: sorftime |
| type | string | Render style |
| columns | array | Render columns |
| products | array | Product detail list (see below) |

### Product Object Fields (products Array Elements)

Trend arrays use an interleaved format: even indices are dates (yyyyMMdd), odd indices are corresponding values.

| Field | Type | Description |
|------|------|------|
| asin | string | ASIN |
| title | string | Product title |
| brand | string | Brand |
| asinUrl | string | Product link, Amazon Listing detail page URL |
| imageUrl | string | Main image URL |
| productImageUrls | array | Main image list (all product image URLs) |
| ebcPhoto | array | A+ image list |
| storeName | string | Store name |
| description | string | Five bullet points |
| productBadge | array | Product badges, e.g. Amazon Choice, Best Seller, New Release, etc. |
| lastUpdate | string | Update time, most recent ASIN data collection time (format yyyy-MM-dd) |
| offSale | boolean | Whether delisted. true = unavailable, false = available |
| productType | string | Category, Amazon product category node name |
| weight | string | Weight, unit g |
| size | array | Dimensions, outer packaging [longest side, second longest side, shortest side], unit cm |
| parentAsin | string | Parent ASIN, the parent ASIN if variants exist, null if no variants |
| variationNum | integer | Number of variations |
| variationASIN | array | Child ASIN list, empty if no variants |
| attribute | array | Product attributes, variant attributes if variants exist. Each entry contains asin (child ASIN), name (attribute name), value (attribute value) |
| price | number | Selling price, actual price after coupon deduction, in local currency (e.g. USD) |
| coupon | integer | Coupon policy. Value >= 0 = deduction amount (e.g. 500 = $5), value < 0 = discount percentage (e.g. -10 = 10% discount) |
| platformFee | number | Platform commission, in local currency (e.g. USD) |
| fbaFees | number | FBA fees, in local currency (e.g. USD) |
| fbaDetail | array | FBA detail. First item is delivery fee, subsequent items are month:storage fee, e.g. [475,"1-9:5","10-12:15"] |
| shipCost | number | FBM shipping cost, in local currency (e.g. USD) |
| shipsFrom | string | Ship-from location |
| profitAmount | number | Profit, final price - FBA fee - commission, in local currency (e.g. USD) |
| profitRate | number | Profit margin, e.g. 25.83 means 25.83% |
| monthlySalesUnits | integer | Official monthly sales volume, Amazon published ASIN monthly sales, latest value from the last 7 calendar days, 0 if unavailable |
| salesRank | integer | BSR rank, main category rank |
| category | array | Main category, [category name, NodeId] |
| bsrCategory | array | Subcategory rank list, each entry containing nodeId (node ID), name (category name), rank (rank), date (date, format yyyyMMdd) |
| availableDate | string | Listing time, format yyyy-MM-dd |
| onlineDays | integer | Days since listing |
| rating | number | Current rating (0.0-5.0, e.g. 4.70) |
| ratings | integer | Number of ratings |
| fiveStarRatings | number | 5-star percentage, e.g. 57.7 means 57.7% |
| fourStarRatings | number | 4-star percentage |
| threeStarRatings | number | 3-star percentage |
| twoStarRatings | number | 2-star percentage |
| oneStarRatings | number | 1-star percentage |
| buyboxSeller | string | Buybox seller name |
| buyBoxSellerId | string | Buybox seller ID |
| buyboxSellerAddress | string | Seller location, Buybox seller nationality (two-letter code e.g. CN, US), null if Amazon's own |
| isFBA | boolean | Whether FBA, whether Buybox seller uses FBA logistics |
| sellerNum | integer | Number of sellers |
| aPlus | boolean | Has A+ |
| hasVideo | boolean | Has video |
| hasBrandStore | boolean | Has brand store |
| feature | object | Product feature ratings, features and star ratings collected by Amazon for this product, e.g. {"Battery life":4.0} |
| productInfo | object | Product information, structured data from the Product Information section in the Listing |
| property | object | Attribute list, including variant attributes and Bullet Points header descriptions |
| brandPromotion | string | Brand promotion |
| dealType | string | Deal label |
| extraSavings | array | Associated promotions, e.g. [{Asin:xxx, Text:"Save 5%..."}] |
| rankTrend | array | BSR trend, main category rank change history, interleaved format [date, rank, ...] |
| bsrRankTrend | array | Subcategory rank trend, JSON format [{NodeId:xxx, Rank:[date, rank, ...]}] |
| listingSalesVolumeOfDailyTrend | array | Daily sales volume trend, value -1 means unable to estimate |
| listingSalesOfDailyTrend | array | Daily sales revenue trend, in local currency smallest unit (e.g. cents), value -1 means unable to estimate |
| listingSalesVolumeOfMonthTrend | array | Monthly sales volume trend (last 30 days), value -1 means unable to estimate |
| listingSalesOfMonthTrend | array | Monthly sales revenue trend, in local currency smallest unit (e.g. cents) |
| priceTrend | array | Selling price trend, before coupon, in local currency smallest unit, -1 means no price available for that day |
| listPriceTrend | array | Original price trend (strikethrough price history), in local currency smallest unit, -1 means no price available for that day |
| dealTrend | array | Deal trend, value 1 = has deal, 0 = no deal |

## Error Codes

Under normal circumstances, the HTTP status code is 200. Business success or failure is determined by the `code` field in the response body (code = 200 indicates success; other values indicate business errors). When encountering unauthorized access, the HTTP status code is 401 and the corresponding errcode is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse `products` and other business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| 402 | Insufficient balance | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| Other non-200 values | Business error | Refer to the `msg` field for specific error details |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/amazon/productDetail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"asin": "B00FLYWNYQ", "marketplace": "us"}'
```

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/amazon/productDetail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"asin": "B00FLYWNYQ", "marketplace": "us", "includeTrend": 1, "queryTrendStartDate": "2025-01-01", "queryTrendEndDate": "2025-03-01"}'
```

---
