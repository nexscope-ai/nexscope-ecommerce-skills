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

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| - | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |

## curl Example

```bash
# Query by publication number
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/legalStatus \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "CN115000000A"}'
```

---
