# Jungle Scout ASIN Sales Estimates API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/tool-jungle-scout/sales-estimates/query`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, read api_key from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| marketplace | string | Yes | Target marketplace code. Options: `us`, `uk`, `de`, `in`, `ca`, `fr`, `it`, `es`, `mx`, `jp` |
| asin | string | Yes | Amazon ASIN to query |
| startDate | string | Yes | Start date (format: YYYY-MM-DD) |
| endDate | string | Yes | End date (format: YYYY-MM-DD); must be earlier than the current date |

### Site Mapping

| Site | marketplace value |
|------|---------------|
| United States | us |
| United Kingdom | uk |
| Germany | de |
| India | in |
| Canada | ca |
| France | fr |
| Italy | it |
| Spain | es |
| Mexico | mx |
| Japan | jp |

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
| costToken | integer | Token consumption |
| salesEstimateList | array | Sales estimate result list |

### Each Object in salesEstimateList Array

| Field | Type | Description |
|------|------|------|
| asin | string | Queried ASIN |
| id | string | Data point identifier |
| type | string | Resource type, fixed value `sales_estimate_result` |
| parentAsin | string | Parent ASIN (returned for variant scenarios) |
| isParent | boolean | Whether it is a parent listing |
| isVariant | boolean | Whether it is a variant listing |
| isStandalone | boolean | Whether it is a standalone listing (non-variant) |
| variants | array | Array of variant ASINs under this parent |
| dailyEstimates | array | Array of daily estimate data |

### Each Object in dailyEstimates Array

| Field | Type | Description |
|------|------|------|
| date | string | Data date (YYYY-MM-DD) |
| estimatedUnitsSold | integer | Estimated units sold on that day |
| lastKnownPrice | number | Last known price (USD) |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| Insufficient credits | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/tool-jungle-scout/sales-estimates/query \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "asin": "B0F15TM77B", "startDate": "2026-03-01", "endDate": "2026-03-31"}'
```

## Response Example

```json
{
  "costToken": 1,
  "salesEstimateList": [
    {
      "asin": "B0CXXX1234",
      "id": "sales_estimate_B0CXXX1234_20260301",
      "type": "sales_estimate_result",
      "parentAsin": "B0CXXX0000",
      "isParent": false,
      "isVariant": true,
      "isStandalone": false,
      "variants": [],
      "dailyEstimates": [
        {
          "date": "2026-03-01",
          "estimatedUnitsSold": 35,
          "lastKnownPrice": 29.99
        },
        {
          "date": "2026-03-02",
          "estimatedUnitsSold": 42,
          "lastKnownPrice": 29.99
        },
        {
          "date": "2026-03-03",
          "estimatedUnitsSold": 38,
          "lastKnownPrice": 27.99
        }
      ]
    }
  ]
}
```

---
