# Zhihuiya Patent Family Query API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/patentFamily`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| patentId | string | Conditionally required | Patent IDs, up to 100 comma-separated values. At least one input field is required; `patentId` takes priority when both are present. Max length: 60000 characters |
| patentNumber | string | Conditionally required | Publication/grant numbers, up to 100 comma-separated values. At least one input field is required. Max length: 60000 characters |

- At least one of `patentId` and `patentNumber` must be provided
- If both parameters are provided, the API will prioritize `patentId` and ignore `patentNumber`

> **Batch limit**: Up to 100 comma-separated patents are accepted. Confirm the intended batch because the endpoint consumes significant credits.

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Number of records |
| data | array | Patent family result list (see below) |
| columns | array | Column definitions for rendering |
| costToken | integer | Tokens consumed |
| type | string | Render style |

### data[] Object Fields

| Field | Type | Description |
|------|------|------|
| patentId | string | Patent ID |
| pn | string | Publication (grant) number |
| simpleFamilyId | integer | Simple family ID |
| simpleFamily | array | Simple family patent list |
| inpadocFamilyId | integer | INPADOC family ID |
| inpadocFamily | array | INPADOC family patent list |
| patsnapFamilyId | integer | PatSnap family ID |
| patsnapFamily | array | PatSnap family patent list |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| - | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |

## curl Example

### Query by publication number

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/patentFamily \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "US10000001B2"}'
```

### Query by patent ID

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/patentFamily \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"patentId": "5af83e12-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}'
```

---
