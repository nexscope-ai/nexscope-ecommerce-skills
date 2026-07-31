# PatSnap Claim Data Query API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/claimData`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from the environment variable `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| patentId | string | No* | PatSnap internal patent ID. Only a single value is supported; multiple values separated by commas are not allowed. Max length 60000 characters |
| patentNumber | string | No* | Publication/announcement number. Only a single value is supported; multiple values separated by commas are not allowed. Max length 60000 characters |
| replaceByRelated | string | No | Whether to substitute with a family patent's claims when the current patent's claims are unavailable: `1` yes, `0` no. Max length 1000 characters |

\* At least one of `patentId` and `patentNumber` must be provided. If both are present, `patentId` takes precedence.

> **Single patent limitation**: This endpoint consumes many credits. To query multiple patents, explicit user consent is required, with one request per patent. Only 1 patent per request.


## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Record count |
| data | array | Patent list (see below) |
| columns | array | Rendered column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendered style |

### data[] Element Structure

| Field | Type | Description |
|------|------|------|
| patentId | string | Patent ID |
| pn | string | Publication (announcement) number |
| pnRelated | string | Publication number of the substitute patent (only provided when a family patent substitute is used) |
| claims | array | Claims array, containing claim text and metadata |
| claimCount | integer | Number of claims |

## curl Example

```bash
# Query claims for a single patent by publication number
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/claimData \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "CN115000000A"}'
```

```bash
# Query claims by patent ID
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/claimData \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"patentId": "98a1b2c3-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}'
```

## Error Codes

Under normal circumstances, the HTTP status code is always 200. Business success or failure is determined by the errorCode field in the response body (errorCode = 200 indicates success, other values indicate business errors). In cases such as unauthorized access, the HTTP status code is 401, and the corresponding errorCode is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
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

---
