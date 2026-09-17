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

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Insufficient credits | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/listNewProductRank \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"date": "2025-06-15", "region": "US", "pageNum": 1, "pageSize": 50}'
```

---
