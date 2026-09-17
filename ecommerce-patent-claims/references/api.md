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

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| - | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
