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

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| - | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/abstractDataTranslated \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "US20200012345A1", "lang": "en", "replaceByRelated": 0}'
```

---
