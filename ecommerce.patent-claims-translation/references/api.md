# PatSnap Claims Translation API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/claimDataTranslated`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from the environment variable `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| patentId | string | No* | Patent ID. Only a single value is supported; multiple values separated by commas are not allowed. When both `patentNumber` and this are present, the patent ID takes precedence. Max length: 60000 characters |
| patentNumber | string | No* | Publication (announcement) number. Only a single value is supported; multiple values separated by commas are not allowed. Max length: 60000 characters |
| lang | string | No | Translation language. Supports `en` (English, default), `cn` (Chinese), `jp` (Japanese). Max length: 1000 characters |
| replaceByRelated | integer | No | Whether to substitute with a family patent when claims are unavailable: `1` yes, `0` no (default) |

> *At least one of `patentId` and `patentNumber` must be provided. If both are present, `patentId` takes precedence.

> **Single patent limitation**: This endpoint consumes many credits. To query multiple patents, explicit user consent is required, with one request per patent. Only 1 patent per request.


## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Record count |
| data | array | Patent list (see below) |
| columns | array | Rendered column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendered style |

### data[] Object

| Field | Type | Description |
|------|------|------|
| patentId | string | Patent ID |
| pn | string | Publication (announcement) number |
| pnRelated | string | Publication number of the substitute patent (only provided when a family patent substitute is used) |
| claims | string | Claims translation text |

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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/claimDataTranslated \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "CN112345678A", "lang": "en", "replaceByRelated": 0}'
```

---
