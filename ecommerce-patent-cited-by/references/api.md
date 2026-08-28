# PatSnap Patent Cited By API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/patentCited`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from the environment variable `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| patentId | string | No* | Patent IDs, up to 100 comma-separated values. If both fields are present, `patentId` takes precedence. Max length: 60000 characters |
| patentNumber | string | No* | Publication/announcement numbers, up to 100 comma-separated values. Max length: 60000 characters |

\* At least one of `patentId` and `patentNumber` must be provided. If both are present, `patentId` takes precedence.

> **Batch limit**: Up to 100 comma-separated patents are accepted. Confirm the intended batch because the endpoint consumes significant credits.


## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Record count |
| data | array | Patent list (see field descriptions below) |
| columns | array | Rendered column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendered style |

### data Array Element Fields

Each object in the `data` array contains the following fields:

| Field | Type | Description |
|------|------|------|
| patentId | string | Patent ID |
| pn | string | Publication (announcement) number |
| citedBy3y | integer | Times cited within 3 years |
| citedBy5y | integer | Times cited within 5 years |
| citedBySimpleFamily | integer | Number of citing patents in the simple family |
| citedByInpadocFamily | integer | Number of citing patents in the INPADOC family |
| citedByPatsnapFamily | integer | Number of citing patents in the PatSnap family |
| citedByPatents | array | List of citing patents |

## Error Codes

Under normal circumstances, the HTTP status code is always 200. Business success or failure is determined by the errorCode field in the response body (errorCode = 200 indicates success, other values indicate business errors). In cases such as unauthorized access, the HTTP status code is 401, and the corresponding errorCode is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse `data` and other business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 402 | - | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/patentCited \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "US10123456B2"}'
```

### Query by Patent ID

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/patentCited \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"patentId": "abc123def456"}'
```

---
