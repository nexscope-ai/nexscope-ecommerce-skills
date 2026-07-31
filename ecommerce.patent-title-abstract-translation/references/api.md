# Zhihuiya Abstract Translation API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/abstractDataTranslated`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| patentId | string | At least one of patentId and patentNumber is required | Zhihuiya internal patent ID. Only a single value is supported; multiple values separated by commas are not allowed. Max length: 60,000 characters |
| patentNumber | string | At least one of patentId and patentNumber is required | Publication (grant) number. Only a single value is supported; multiple values separated by commas are not allowed. Max length: 60,000 characters |
| replaceByRelated | integer | No | Whether to substitute with a family patent's abstract when the abstract is unavailable: `1` Yes, `0` No. Default `0` |
| lang | string | No | Target translation language. Options: `en` (English, default), `cn` (Chinese), `jp` (Japanese). Max length: 1,000 characters |

- At least one of `patentId` and `patentNumber` must be provided. If both are present, `patentId` takes priority

> **Single patent limit**: This API consumes significant credits. To query multiple patents, you must obtain explicit user consent and make separate requests. Only 1 patent per request.

## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Number of patent records returned |
| data | array | Patent list |
| data[].patentId | string | Zhihuiya internal patent ID |
| data[].pn | string | Publication (grant) number |
| data[].title | string | Title translation |
| data[].abstractText | string | Abstract translation |
| data[].pnRelated | string | Publication number of the substitute patent (only provided when family patent substitution is used) |
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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/abstractDataTranslated \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "US20200012345A1", "lang": "en", "replaceByRelated": 0}'
```

---
