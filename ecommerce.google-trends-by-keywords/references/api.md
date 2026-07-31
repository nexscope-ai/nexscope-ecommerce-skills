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

Under normal conditions, the HTTP status code is always 200. Business success or failure is determined by the errorCode field in the response body (errorCode = 200 indicates success; other values indicate business errors). In cases of unauthorized access, the HTTP status code will be 401, with the corresponding errorCode also being 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| 402 | Insufficient credits | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| Other non-200 values | Business exception | Refer to the `errmsg` field for specific error cause |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/googleTrend/getTrendByKeys \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "wireless charger", "region": "US", "dayRangeStart": "2024-01-01", "dayRangeEnd": "2025-01-01"}'
```

---
