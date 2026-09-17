# Jungle Scout Keyword Historical Search Volume API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/tool-jungle-scout/keywords/historical-search-volume`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| marketplace | string | Yes | Target marketplace code. Options: `us`, `uk`, `de`, `in`, `ca`, `fr`, `it`, `es`, `mx`, `jp` |
| keyword | string | Yes | Keyword to query |
| startDate | string | Yes | Start date (format: YYYY-MM-DD) |
| endDate | string | Yes | End date (format: YYYY-MM-DD); max interval from startDate is 366 days |

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
| costToken | integer | Tokens consumed |
| historicalSearchVolumeList | array | Historical search volume period list |

### Each Object in historicalSearchVolumeList

| Field | Type | Description |
|------|------|------|
| id | string | Data period identifier (market/keyword/date range) |
| estimateStartDate | string | Period start date (YYYY-MM-DD, 7-day statistical period start) |
| estimateEndDate | string | Period end date (YYYY-MM-DD, 7-day statistical period end) |
| estimatedExactSearchVolume | integer | Exact match search volume for this period (searches/week) |
| type | string | Resource type, fixed value `historical_keyword_search_volume` |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| Insufficient credits/balance | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/tool-jungle-scout/keywords/historical-search-volume \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "keyword": "yoga mat", "startDate": "2025-10-01", "endDate": "2026-03-31"}'
```

## Response Example

```json
{
  "costToken": 1,
  "historicalSearchVolumeList": [
    {
      "id": "us_yoga_mat_20251005_20251011",
      "estimateStartDate": "2025-10-05",
      "estimateEndDate": "2025-10-11",
      "estimatedExactSearchVolume": 85420,
      "type": "historical_keyword_search_volume"
    },
    {
      "id": "us_yoga_mat_20251012_20251018",
      "estimateStartDate": "2025-10-12",
      "estimateEndDate": "2025-10-18",
      "estimatedExactSearchVolume": 87650,
      "type": "historical_keyword_search_volume"
    }
  ]
}
```

---
