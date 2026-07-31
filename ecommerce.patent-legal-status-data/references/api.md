# Zhihuiya Patent Legal Status Query API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/legalStatus`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| patentId | string | Conditionally required | Patent ID. At least one of `patentId` and `patentNumber` must be provided; if both are present, `patentId` takes priority. Only a single value is supported; multiple values separated by commas are not allowed. Max length: 60000 characters. |
| patentNumber | string | Conditionally required | Publication (grant) number. At least one of `patentId` and `patentNumber` must be provided; if both are present, `patentId` takes priority. Only a single value is supported; multiple values separated by commas are not allowed. Max length: 60000 characters. |

> **Single patent limit**: This API consumes significant credits. To query multiple patents, you must obtain explicit user consent and make separate requests. Only 1 patent per request.


## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Number of records |
| data | array | Patent legal status list |
| data[].patentId | string | Patent ID |
| data[].pn | string | Publication (grant) number |
| data[].simpleLegalStatus | array | Simple legal status. Options: Inactive, Active, Pending, Undetermined, PCT designated period, PCT designated expiration |
| data[].legalStatus | array | Legal status. Options: Published, Examining, Granted, Double, Abandoned-Undetermined, Abandoned-Voluntarily, Abandoned-Deemed, Withdrawn-Undetermined, Withdrawn-Voluntarily, Withdrawn-Deemed, Rejected, Revoked, Expired, Non-Payment, Restoration, Ceased, P-Revoked, Discontinuation, PCT published, PCT entering(designated period), PCT entering(designated expiration), PCT unentered |
| data[].eventStatus | array | Legal events. Options: Transfer, License, Pledge, Trust, Opposition, Re-examination, Customs, Litigation, Preservation, Invalid-procedure, Oral-procedure, Declassification, Double application |
| data[].legalDate | integer | Legal status update date (timestamp) |
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

```bash
# Query by publication number
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/legalStatus \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "CN115000000A"}'
```

---
