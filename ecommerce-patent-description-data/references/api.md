# Zhihuiya Patent Description Query API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/descriptionData`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| patentId | string | Conditionally required | Patent ID (at least one of patentId and patentNumber must be provided; if both are present, patentId takes priority). Only a single value is supported; multiple values separated by commas are not allowed. Max length: 60000 characters. |
| patentNumber | string | Conditionally required | Publication/grant number (at least one of patentId and patentNumber must be provided; if both are present, patentId takes priority). Only a single value is supported; multiple values separated by commas are not allowed. Max length: 60000 characters. |
| replaceByRelated | string | No | Whether to substitute with a family patent's description when the current patent's description is unavailable: `1` Yes, `0` No. Max length: 1000 characters. |

> **Single patent limit**: This API consumes significant credits. To query multiple patents, you must obtain explicit user consent and make separate requests. Only 1 patent per request.


## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Number of patent records returned |
| data | array | Patent list, each element contains description data |
| data[].patentId | string | Patent ID |
| data[].pn | string | Publication (grant) number |
| data[].pnRelated | string | Publication number of the substitute patent (only provided when family patent substitution is used) |
| data[].description | array | Description content sections |
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

**Query by publication number:**

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/descriptionData \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "CN115099012A"}'
```

**Query by patent ID with family substitution enabled:**

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/descriptionData \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"patentId": "abc123def456", "replaceByRelated": "1"}'
```

---
