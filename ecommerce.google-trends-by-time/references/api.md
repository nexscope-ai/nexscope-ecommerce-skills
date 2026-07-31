# Google Trends Trending Now API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/googleTrend/getTrendByTime`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, read api_key from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| days | integer | No | Time range, query trend data for the last N days, default `7`. Common values: 1, 2, 7 |
| region | string | No | Country/region code, default `US`. Options: US, GB, JP, CA, MX, DE, FR, IT, ES, NL, AU, SG, AE, BR, IN, TR, PL, SE |


## Response Structure

| Field | Type | Description |
|------|------|------|
| costToken | integer | Token consumption |
| chartOption | object | Chart config object, containing visualization data |
| chartOption.data | array | Data, array of chart data point objects |
| chartOption.fieldX | string | X-axis field |
| chartOption.fieldY | array | Y-axis fields |
| chartOption.type | string | Data type |
| chartOption.title | string | Title |
| trendValues | array | Trend values, array of trending query objects (see below) |

### trendValues Element Structure

| Field | Type | Description |
|------|------|------|
| query | string | Keyword |
| searchVolume | integer | Search volume value |
| increasePercentage | integer | Percentage increase: integer, range -100 to 100, unit is % |
| startTime | string | Start timestamp |
| endTime | string | End timestamp |

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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/googleTrend/getTrendByTime \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"days": 7, "region": "US"}'
```

---
