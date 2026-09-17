# Google Trends Keyword Trend Info API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/googleTrend/getTrendByKeys`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, read api_key from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| keyword | string | Yes | Keyword (the keyword must be in the language of the target country! For example, use English keywords for the US, German keywords for Germany. If not in the corresponding country's language, please translate first.) Max length 100 characters |
| region | string | No | Country/region, default `US`. Options: US, GB, JP, CA, MX, DE, FR, IT, ES, NL, AU, SG, AE, BR, IN, TR, PL, SE |
| dayRangeStart | string | No | Time range start (use when you want to freely specify the time range; custom time range takes priority), format YYYY-MM-DD, starting from 2004 |
| dayRangeEnd | string | No | Time range end (use when you want to freely specify the time range; custom time range takes priority), format YYYY-MM-DD, starting from 2004 |

- When both `dayRangeStart` and `dayRangeEnd` are provided, the custom time range takes priority

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
| trendInfoForKeys | array | Keyword trend info array |
| trendInfoForKeys[].keyword | string | Keyword |
| trendInfoForKeys[].trendValues | array | Trend value array |
| trendInfoForKeys[].trendValues[].timeRange | string | Time, format yyyy-MM-dd |
| trendInfoForKeys[].trendValues[].value | string | Value (normalized search interest, 0-100) |
| chartOption | object | Chart rendering metadata |
| chartOption.type | string | Data type |
| chartOption.fieldX | string | X-axis field |
| chartOption.fieldY | array | Y-axis fields |
| chartOption.data | array | Data |
| costToken | integer | Token consumption |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| Insufficient credits | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/googleTrend/getTrendByKeys \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "wireless charger", "region": "US", "dayRangeStart": "2024-01-01", "dayRangeEnd": "2025-01-01"}'
```

---
