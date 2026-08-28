# ABA Intelligent Query API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/aba/intelligentQuery`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| analysisDescription | string | Yes | Natural language description that precisely expresses the query intent |
| region | string | No | Site code, default `US`. Options: US, DE, BR, CA, AU, JP, AE, ES, FR, IT, SA, TR, MX, SE, NL |
| createDownloadUrl | boolean | No | Whether to generate a CSV download link, default `false` |

- When the user explicitly requests "download", "export", or "generate file", set `createDownloadUrl` to `true`

## Response Structure

| Field | Type | Description |
|------|------|------|
| success | boolean | Whether the query succeeded |
| tables | array | Result data array, each element containing `data` (data rows), `columns` (column definitions), `name` (Sheet name) |
| total | integer | Total result count |
| downloadUrl | string | When `createDownloadUrl` is true, returns the CSV file URL |
| msg | string | Additional message |
| downloadNote | string | Download-related note |
| code | string | Response code |
| costTime | integer | Latency (ms) |
| costToken | integer | Tokens consumed |

## Error Codes

Under normal circumstances, the HTTP status code is 200. Business success or failure is determined by the `errorCode` field in the response body (errorCode = 200 indicates success; other values indicate business errors). When encountering unauthorized access, the HTTP status code is 401 and the corresponding errorCode is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse `tables` / `data` and other business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| 402 | Insufficient credits | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/aba/intelligentQuery \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"analysisDescription": "Filter US site, keyword gift search popularity ranking over the past 12 weeks", "region": "US"}'
```

---
