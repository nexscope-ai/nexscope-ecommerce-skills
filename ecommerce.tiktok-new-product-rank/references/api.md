# EchoTik TikTok New Product Rank API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/listNewProductRank`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| date | string | Yes | Date in `YYYY-MM-DD` format |
| region | string | No | Region, default `US`. Options: US (United States), ID (Indonesia), TH (Thailand), PH (Philippines), MY (Malaysia), VN (Vietnam), GB (United Kingdom), MX (Mexico), SG (Singapore), SA (Saudi Arabia), BR (Brazil), ES (Spain), JP (Japan), DE (Germany), IT (Italy), FR (France) |
| pageNum | integer | No | Page number, default `1` |
| pageSize | integer | No | Items per page, default `50` |


## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Record count |
| products | array | New product list (see product object below) |
| columns | array | Rendered columns |
| type | string | Render style |
| costToken | integer | Token cost |

### Product Object

| Field | Type | Description |
|------|------|------|
| title | string | Product name |
| asin | string | Product ID |
| region | string | Region code |
| price | number | SPU average price |
| minPrice | number | Minimum price |
| maxPrice | number | Maximum price |
| currency | string | Currency |
| totalSaleCnt | integer | Total sales |
| totalSale30dCnt | integer | Sales in last 30 days |
| totalSaleGmvAmt | number | Total GMV |
| totalSaleGmv30dAmt | number | GMV in last 30 days |
| salesTrendFlagText | string | Sales trend indicator, 0=stable 1=rising 2=falling |
| totalVideoCnt | integer | Total video count |
| totalLiveCnt | integer | Total livestream count |
| totalIflCnt | integer | Total creator count |
| productCommissionRate | number | Product commission rate |
| productRating | number | Product rating |
| reviewCount | integer | Review count |
| availableDate | string (date) | First crawl date |
| categoryId | string | Product category ID |
| imageUrl | string | Product image |
| productImageUrls | array | Product image URL list |
| sourceTool | string | Source tool |
| sourceType | string | Product source |

## Error Codes

Under normal circumstances, the HTTP status code of the API is always 200. Business success or failure is distinguished by the `errorCode` field in the response body (`errorCode = 200` indicates success, other values indicate business errors). In cases such as unauthorized access, the HTTP status code is 401, and the corresponding `errorCode` is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 402 | Insufficient credits | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/listNewProductRank \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"date": "2025-06-15", "region": "US", "pageNum": 1, "pageSize": 50}'
```

---
