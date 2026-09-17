# FastMoss TikTok Top Selling Products API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/fastmoss/productRankTopSelling`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| region | string | Yes | Market region code. Options: US (United States), GB (United Kingdom), MX (Mexico), ES (Spain), DE (Germany), IT (Italy), FR (France), ID (Indonesia), VN (Vietnam), MY (Malaysia), TH (Thailand), PH (Philippines), BR (Brazil), JP (Japan), SG (Singapore) |
| dateInfo | object | Yes | Date specification object, containing `type` and `value` fields |
| dateInfo.type | string | Yes | Time granularity: `day`, `week`, `month` |
| dateInfo.value | string | Yes | Date value: day format `YYYY-MM-DD`, week format `YYYY-weekNumber` (e.g., `2025-18`), month format `YYYY-MM` |
| category | string | No | Product category name (English), matched to TikTok category ID. Non-English input must be translated to English first |
| orderby | object | No | Sort rule object, containing `field` and `order` fields |
| orderby.field | string | No | Sort field: `units_sold` (sales), `gmv` (GMV), `total_units_sold` (total sales), `total_gmv` (total GMV), `growth_rate` (growth rate) |
| orderby.order | string | No | Sort direction: `desc` (descending), `asc` (ascending), default `desc` |
| page | integer | No | Page number, default `1` |
| pageSize | integer | No | Items per page, max `10`, default `10` |

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

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Insufficient credits | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/fastmoss/productRankTopSelling \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"region": "US", "dateInfo": {"type": "day", "value": "2026-04-15"}, "page": 1, "pageSize": 10}'
```

---
