# Zhihuiya Patent Citation Query API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/patentForwardCitation`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| patentId | string | Conditionally required | Patent IDs, up to 100 comma-separated values. At least one input field is required; `patentId` takes priority when both are present. Max length: 60000 characters. |
| patentNumber | string | Conditionally required | Publication/grant numbers, up to 100 comma-separated values. At least one input field is required. Max length: 60000 characters. |

- At least one of `patentId` or `patentNumber` must be provided per request

> **Batch limit**: Up to 100 comma-separated patents are accepted. Confirm the intended batch because the endpoint consumes significant credits.

## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Number of records |
| data | array | Patent list, each element contains citation details |
| data[].patentId | string | Patent ID of the queried patent |
| data[].pn | string | Publication (grant) number of the queried patent |
| data[].citedPatents | array | Cited patent list |
| data[].citedOthers | array | Cited non-patent literature list |
| columns | array | Column definitions for rendering |
| costToken | integer | Tokens consumed |
| type | string | Render style |

## Error Codes

Under normal circumstances, the HTTP status code is 200. Business success or failure is distinguished by the `errorCode` field in the response body (`errorCode = 200` indicates success; other values indicate business errors). When unauthorized, the HTTP status code is 401, and the corresponding errorCode is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields such as `data` normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| 402 | - | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| Other non-200 values | Business exception | Refer to the `errmsg` field for the specific error reason |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Example

### Query by publication/grant number

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/patentForwardCitation \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "US10000000B2"}'
```

### Query by patent ID

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/patentForwardCitation \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"patentId": "12345678"}'
```

---
