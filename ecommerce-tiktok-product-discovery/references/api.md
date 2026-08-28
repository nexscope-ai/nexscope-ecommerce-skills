# FastMoss TikTok Product Discovery API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/fastmoss/productSearch`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| keyword | string | No | Search keyword (fuzzy match on product title) |
| region | string | No | Market region code. Options: US (United States), GB (United Kingdom), MX (Mexico), ES (Spain), DE (Germany), IT (Italy), FR (France), ID (Indonesia), VN (Vietnam), MY (Malaysia), TH (Thailand), PH (Philippines), BR (Brazil), JP (Japan), SG (Singapore) |
| category | string | No | English category name, automatically matched to TikTok category ID. Non-English input must be translated to English first |
| shopType | integer | No | Store type: 1=local store, 2=cross-border store |
| isTopSelling | boolean | No | Filter hot-selling products only |
| isNewListed | boolean | No | Filter newly listed products only |
| isSshop | boolean | No | Filter TikTok fully managed (S-shop) products only |
| isFreeShipping | boolean | No | Filter free shipping products only |
| isLocalWarehouse | boolean | No | Filter local warehouse shipping products only |
| unitsSoldRange | object | No | Sales volume range filter, format: `{"min": 100, "max": 5000}` |
| commissionRateRange | object | No | Commission rate range filter, format: `{"min": 0.05, "max": 0.20}` (decimal, 0.10=10%) |
| creatorCountRange | object | No | Creator count range filter, format: `{"min": 10, "max": 500}` |
| orderField | string | No | Sort field: day7_units_sold (7-day sales), day7_gmv (7-day GMV), commission_rate (commission rate), total_units_sold (total sales), total_gmv (total GMV), creator_count (creator count). Default descending order |
| page | integer | No | Page number, default 1 |
| pageSize | integer | No | Items per page, max 10, default 10 |

## Response Structure

### Top-Level Fields

| Field | Type | Description |
|------|------|------|
| total | integer | Total number of matching records |
| products | array | Product information list (see below) |
| columns | array | Render column definitions |
| type | string | Render style type |
| costToken | integer | Token cost |

### Product Object Fields (products array)

| Field | Type | Description |
|------|------|------|
| title | string | Product title |
| productId | string | Product unique identifier ID |
| region | string | Market region code |
| price | number | Product price |
| minPrice | number | Minimum price |
| maxPrice | number | Maximum price |
| currency | string | Currency code |
| totalSaleCnt | integer | Cumulative total sales |
| totalSale1dCnt | integer | 1-day sales |
| totalSale7dCnt | integer | 7-day sales |
| totalSale28dCnt | integer | 28-day sales |
| totalSale90dCnt | integer | 90-day sales |
| totalSaleGmvAmt | number | Cumulative total GMV |
| totalSaleGmv7dAmt | number | 7-day GMV |
| totalSaleGmv28dAmt | number | 28-day GMV |
| totalVideoCnt | integer | Number of promotional videos |
| totalLiveCnt | integer | Number of livestream promotions |
| totalIflCnt | integer | Number of promoting creators |
| productCommissionRate | number | Product commission rate (decimal, 0.10=10%) |
| productRating | number | Product rating |
| reviewCount | integer | Review count |
| skuCount | integer | SKU count |
| shopName | string | Store name |
| shopSellerId | string | Seller ID |
| shopTotalUnitsSold | integer | Store total sales |
| isCrossBorder | integer | Whether cross-border: 1=cross-border, 0=local |
| isSShopText | string | Whether a fully managed store (Yes/No) |
| freeShippingText | string | Whether free shipping (Yes/No) |
| availableDate | string | Listing time |
| categoryName | string | Product category name |
| salesTrendFlagText | string | Sales trend indicator |
| tiktokUrl | string | TikTok product link |
| fastmossUrl | string | FastMoss product detail link |
| imageUrl | string | Product image URL |

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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/fastmoss/productSearch \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "phone case",
    "region": "US",
    "orderField": "day7_units_sold",
    "pageSize": 10
  }'
```

Example with range filters:

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/fastmoss/productSearch \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "beauty",
    "region": "US",
    "commissionRateRange": {"min": 0.10},
    "creatorCountRange": {"min": 50},
    "orderField": "commission_rate",
    "pageSize": 10
  }'
```

---
