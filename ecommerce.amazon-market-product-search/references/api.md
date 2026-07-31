# Sorftime Amazon Product Search API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/amazon/productQuery`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| marketplace | string | Yes | Amazon site code: us, gb, de, fr, in, ca, jp, es, it, mx, ae, au, br, sa |
| queryMode | integer | No | Query mode. `1`: single condition query (default); `2`: multi-condition combined query (AND relationship) |
| queryType | integer | No | Query type (1-16), only effective when queryMode=1. See the complete Query Types description in SKILL.md |
| queryValue | string | No | Query condition value, format varies by queryMode and queryType. See the format description for each queryType in SKILL.md |
| page | integer | No | Page number, default 1. Max 100 products per page |
| queryMonth | string | No | Historical month lookback, format `yyyy-MM`. When not specified, queries real-time data |

- When `queryMode=2` (multi-condition combined query), `queryType` is ignored; all conditions are passed via `queryValue` as a JSON array: `[{"QueryType":1,"Content":"B0CVM8TXHP"},{"QueryType":8,"Content":"100,500"}]`
- When the user explicitly requests pagination, adjust the `page` parameter

## Response Structure

### Top-Level Fields

| Field | Type | Description |
|------|------|------|
| code | integer | Response code (200 indicates success) |
| msg | string | Response message |
| total | integer | Total result count |
| page | integer | Current page number |
| pageCount | integer | Total page count (max 200 pages) |
| costTime | integer | Latency (ms) |
| costToken | integer | Tokens consumed |
| requestConsumed | integer | Requests consumed |
| type | string | Render style |
| columns | array | Render columns |
| products | array | Product list (see below) |

### Product Object Fields (products Array Elements)

| Field | Type | Description |
|------|------|------|
| asin | string | ASIN |
| title | string | Product title |
| brand | string | Brand |
| asinUrl | string | Product link, Amazon Listing detail page URL |
| imageUrl | string | Main image URL |
| productImageUrls | array | Main image list (all product image URLs) |
| parentAsin | string | Parent ASIN, the parent ASIN if variants exist, null if no variants |
| variationNum | integer | Number of variations |
| weight | string | Weight, unit g |
| size | array | Dimensions, outer packaging [longest side, second longest side, shortest side], unit cm |
| price | number | Current price, before coupon, in local currency (e.g. USD) |
| oldPrice | number | Strikethrough price, in local currency (e.g. USD) |
| salesPrice | number | Final price, actual price after coupon deduction, in local currency (e.g. USD) |
| coupon | integer | Coupon policy. Value >= 0 = deduction amount (e.g. 500 = $5), value < 0 = discount percentage (e.g. -10 = 10% discount) |
| fbaFees | number | FBA fees, in local currency (e.g. USD) |
| fbaDetail | array | FBA detail. First item is delivery fee, subsequent items are month:storage fee, e.g. [475,"1-9:5","10-12:15"] |
| platformFee | number | Platform commission, in local currency (e.g. USD) |
| profitAmount | number | Profit, final price - FBA fee - commission, in local currency (e.g. USD) |
| profitRate | number | Profit margin, e.g. 25.83 means 25.83% |
| monthlySalesUnits | integer | Monthly sales volume, last 30 days Listing-level (does not split by variant), recommended for evaluating sales, value -1 means unable to estimate |
| monthlySalesRevenue | number | Monthly sales revenue, estimated value, in local currency (e.g. USD), value -1 means unable to estimate |
| listingSalesVolumeOfDaily | integer | Daily sales volume, Listing-level (does not split by variant), value -1 means unable to estimate |
| listingSalesOfDaily | number | Daily sales revenue, in local currency (e.g. USD), value -1 means unable to estimate |
| salesRank | integer | BSR rank, main category rank |
| category | array | Main category, [category name, NodeId] |
| bsrCategory | array | Subcategory rank list, each entry containing nodeId (node ID), name (category name), rank (rank), date (date, format yyyyMMdd) |
| rating | number | Current rating (0.0-5.0, e.g. 4.8) |
| ratings | integer | Number of ratings |
| availableDate | string | Listing time, format yyyy-MM-dd |
| onlineDays | integer | Days since listing |
| buyboxSeller | string | Buybox seller name |
| buyBoxSellerId | string | Buybox seller ID |
| buyboxSellerAddress | string | Seller location, Buybox seller nationality (two-letter code e.g. CN, US), null if Amazon's own |
| isFBA | boolean | Whether FBA, whether Buybox seller uses FBA logistics |
| sellerNum | integer | Number of sellers |
| aPlus | boolean | Has A+ |
| hasVideo | boolean | Has video |
| hasBrandStore | boolean | Has brand store |


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

**Single Condition - ASIN Similar Products:**

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/amazon/productQuery \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "queryMode": 1, "queryType": 1, "queryValue": "B0CVM8TXHP"}'
```

**Single Condition - Category Browsing:**

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/amazon/productQuery \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "queryMode": 1, "queryType": 2, "queryValue": "3743561"}'
```

**Single Condition - Brand Best Sellers:**

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/amazon/productQuery \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "queryMode": 1, "queryType": 3, "queryValue": "Anker"}'
```

**Single Condition - Historical Snapshot Lookback:**

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/amazon/productQuery \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "queryMode": 1, "queryType": 2, "queryValue": "3743561", "queryMonth": "2024-11"}'
```

**Multi-Condition Combined - New Products + High Sales + FBA:**

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/amazon/productQuery \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "queryMode": 2, "queryValue": "[{\"QueryType\":11,\"Content\":\"2024-06-01,\"},{\"QueryType\":9,\"Content\":\"300,\"},{\"QueryType\":15,\"Content\":\"FBA\"}]"}'
```

---
