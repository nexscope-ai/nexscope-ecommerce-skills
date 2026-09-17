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

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| - | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |

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
