# ABA Intelligent Query API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/aba/intelligentQuery`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| analysisDescription | string | Yes | Natural language description that precisely expresses the query intent |
| region | string | No | Site code, default `US`. Options: US, DE, BR, CA, AU, JP, AE, ES, FR, IT, SA, TR, MX, SE, NL |
| createDownloadUrl | boolean | No | Whether to generate a CSV download link, default `false` |

- When the user explicitly requests "download", "export", or "generate file", set `createDownloadUrl` to `true`

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
| success | boolean | Whether the query succeeded |
| tables | array | Result data array, each element containing `data` (data rows), `columns` (column definitions), `name` (Sheet name) |
| total | integer | Total result count |
| downloadUrl | string | When `createDownloadUrl` is true, returns the CSV file URL |
| msg | string | Additional message |
| downloadNote | string | Download-related note |
| code | string | Response code |
| costTime | integer | Latency (ms) |
| costToken | integer | Tokens consumed |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| Insufficient credits | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/aba/intelligentQuery \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"analysisDescription": "Filter US site, keyword gift search popularity ranking over the past 12 weeks", "region": "US"}'
```

---
