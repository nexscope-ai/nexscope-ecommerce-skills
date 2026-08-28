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

Under normal circumstances, the HTTP status code is 200. Business success or failure is determined by the `errorCode` field in the response body (errorCode = 200 indicates success; other values indicate business errors). When encountering unauthorized access, the HTTP status code is 401 and the corresponding errorCode is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse `historicalSearchVolumeList` normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| 402 | Insufficient credits/balance | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| Other non-200 values | Business error | Refer to the `errmsg` field for specific error details |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

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
