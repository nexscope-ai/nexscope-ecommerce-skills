# FastMoss TikTok Top Selling Products API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/fastmoss/productRankTopSelling`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| region | string | Yes | Market region code. Options: US (United States), GB (United Kingdom), MX (Mexico), ES (Spain), ID (Indonesia), VN (Vietnam), MY (Malaysia), TH (Thailand), PH (Philippines) |
| dateInfo | object | Yes | Date specification object, containing `type` and `value` fields |
| dateInfo.type | string | Yes | Time granularity: `day`, `week`, `month` |
| dateInfo.value | string | Yes | Date value: day format `YYYY-MM-DD`, week format `YYYY-weekNumber` (e.g., `2025-18`), month format `YYYY-MM` |
| category | string | No | Product category name (English), matched to TikTok category ID. Non-English input must be translated to English first |
| orderby | object | No | Sort rule object, containing `field` and `order` fields |
| orderby.field | string | No | Sort field: `units_sold` (sales), `gmv` (GMV), `total_units_sold` (total sales), `total_gmv` (total GMV), `growth_rate` (growth rate) |
| orderby.order | string | No | Sort direction: `desc` (descending), `asc` (ascending), default `desc` |
| page | integer | No | Page number, default `1` |
| pageSize | integer | No | Items per page, max `10`, default `10` |

## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Record count |
| products | array | Hot selling product list (see product object below) |
| columns | array | Rendered columns |
| type | string | Render style |
| costToken | integer | Token cost |

### Product Object

| Field | Type | Description |
|------|------|------|
| title | string | Product name |
| productId | string | Product ID |
| region | string | Region code |
| price | number | Product price |
| minPrice | number | Minimum price |
| maxPrice | number | Maximum price |
| currency | string | Currency |
| totalSaleCnt | integer | Total sales |
| totalSale1dCnt | integer | Sales in last 1 day (returned when dateType=day) |
| totalSale7dCnt | integer | Sales in last 7 days (returned when dateType=week) |
| totalSale30dCnt | integer | Sales in last 30 days (returned when dateType=month) |
| totalSaleGmvAmt | number | Total GMV |
| totalSaleGmv1dAmt | number | GMV in last 1 day (returned when dateType=day) |
| totalSaleGmv7dAmt | number | GMV in last 7 days (returned when dateType=week) |
| totalSaleGmv30dAmt | number | GMV in last 30 days (returned when dateType=month) |
| growthRate | number | Growth rate (percentage) |
| shopName | string | Store name |
| shopTotalUnitsSold | integer | Store total sales |
| shopSellerId | string | Store seller ID |
| categoryName | string | Product category |
| productCommissionRate | number | Product commission rate (basis points, 1000=10%) |
| imageUrl | string | Product image URL |
| offShelvesText | string | Whether delisted ("Yes"=delisted, "No"=on sale) |

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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/fastmoss/productRankTopSelling \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"region": "US", "dateInfo": {"type": "day", "value": "2026-04-15"}, "page": 1, "pageSize": 10}'
```

---
