# Amazon Business Insights Report API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/opportunity/reportByKeyword`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, read api_key from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)
- **User-Agent**: `NexScope-Skill/1.0`

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| site | string | Yes | Amazon site code, currently only supports `US` |
| keyword | string | Yes | Search keyword for the insight report |

## Response Structure

| Field | Type | Description |
|------|------|------|
| code | string | Response code |
| msg | string | Message or error information |
| stdout | string | Comprehensive business insight report content (Markdown format), covering six dimensions: market potential, product features, user reviews, customer profiles, search trends, and pricing analysis |
| costTime | integer | Total processing time (milliseconds) |
| costToken | integer | Token consumption |
| type | string | Response type |

## Error Codes

Under normal conditions, the HTTP status code is always 200. Business success or failure is determined by the `code` field in the response body. In cases such as unauthorized access, the HTTP status code will be 401.

| errcode | Meaning | Action |
|--------|------|----------|
| 200 | Success | Parse the `stdout` field normally and display the Markdown report to the user |
| 401 | Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| 402 | Insufficient credits | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| Other non-200 values | Business exception | Refer to the `msg` field for specific error cause |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/opportunity/reportByKeyword \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/1.0" \
  -d '{"site": "US", "keyword": "ice bricks"}'
```

---
