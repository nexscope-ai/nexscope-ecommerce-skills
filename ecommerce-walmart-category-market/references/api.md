## Nexscope billing

The migrated Skill does not inherit the source platform's point value. This operation consumes Nexscope credits. Preserve X-Cost-Token and X-Cost-Credit from the HTTP response headers as server-reported billing metadata, and preserve X-Kong-Trace-Id for diagnostics.

# Nexscope proxy contract

The endpoint uses the `/api/v1/tools/research/` prefix. Successful HTTP responses use a Nexscope envelope (`code`, `msg`, `data`, `traceId`, and cost metadata); the original business response is nested in `data`.

# Walmart Category Market API Reference

## Request conventions

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/categoryMarket`
- **Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: Bearer <api_key>`; Read api_key from `NEXSCOPE_API_KEY`, falling back to `NEXSCOPE_API_KEY`
- **User-Agent**：`Nexscope-Skill/2.0`
- **Timeout**: 120s
- **Forwarded headers**: `SESSION_ID`, `MODE_ID`, `APP_NAME`
- **Market**: Walmart US; the backend always uses Sorftime `domain=21`

The request body is flat JSON. Each request allows only one case-sensitive `operation`; do not batch operations or automatically execute multiple operations in sequence. The server identifies, validates, and decodes upstream plain JSON and Base64/GZip responses.

## Operations and request parameters

| operation | Purpose | Other parameters | Required rules | Sorftime Request |
|---|---|---|---|---:|
| `tree` | Full category tree | None | Only `operation` is required | 5 |
| `searchByName` | Search related categories by natural-language category name | `name`: string | `name` is required and must be nonempty | 1 |
| `marketReport` | Category market report and Best Seller Top 80 | `nodePath`: string | `nodePath` is required | 5 |

`name` is a natural-language category name, such as `patio furniture`. This operation maps to Sorftime `CategorySearchFromName` and returns at most 3 related categories; matches do not represent exact classification.

`nodePath` is the full underscore-separated path of numeric category IDs, such as `4044_623679_1032619_5842891_9823303`. Obtain it from the category tree; do not guess it from a name.

Request examples:

```json
{"operation":"tree"}
```

```json
{"operation":"searchByName","name":"patio furniture"}
```

```json
{"operation":"marketReport","nodePath":"4044_623679_1032619_5842891_9823303"}
```

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Package scripts unwrap this platform object for their business output and retain its `code`, `msg`, and timing metadata under `_nexscope`; for those outputs, inspect `_nexscope.code` / `_nexscope.msg`. Business `code` or `error` fields are not platform success markers.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Response structure

The business `code` / `msg` fields, if present, remain inside platform `data`; only the outer numeric `code` controls platform success.

| Field | Type | Description |
|---|---|---|
| `code` | integer | Provider business value retained inside `data`; not the outer platform status |
| `msg` | string | Response message; no-data responses may contain "查询成功，但无数据" (query succeeded, but no data) |
| `data` | object | Fixed response container; `data.value` preserves the original Sorftime array, object, scalar, or `null` according to the operation |
| `operation` | string | The operation actually executed: `tree`, `searchByName`, or `marketReport` |
| `requestConsumed` | integer | Upstream consumption for this request; if missing or 0, use the documented consumption for the operation; keep 0 when Sorftime explicitly returns `Code=11` (no data) |
| `costTime` | integer | Elapsed time in milliseconds |
| `costToken` | integer | Compatibility field in the business body; read the `X-Cost-Token` response header for independent Nexscope billing |
| `sourceType` | string | `sorftime` |

When Sorftime explicitly returns `Code=11` (no data), the gateway keeps `requestConsumed=0` and `costToken=0` without filling in documented consumption.

Read business results from `data.value`. `tree` nodes may contain `Id`, `ParentId`, `NodeId`, `Name`, `CNName`, and `URL`; the complete tree is approximately 10 MB. `searchByName` returns Sorftime `CategorySearchFromName` data: at most 3 related categories, each containing `NodeId` and `CategoryName`. `marketReport` returns category market data and up to the Top 80 Best Seller products; use the actual response for specific fields.

## Error codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Missing required parameter; framework validation of globally required fields returns 400, while business validation of conditionally required fields returns 4000 | Provide `operation`, `name` for `searchByName`, or `nodePath` for `marketReport` |
| Invalid parameter format | Check operation casing, a nonempty name, and nodePath format |
| Authentication failed | Follow the authentication guidance in SKILL.md |
| Insufficient credits | Follow the credit guidance in SKILL.md |
| Upstream HTTP, response, or parsing error | Do not automatically change parameters and retry repeatedly |
| Upstream access restriction, parameter, IP, or permission error | Verify parameters; refer permission issues to the service maintainer |
| Upstream quota or rate limit | Retry later; do not send repeated requests |
| Other upstream business error | Preserve the response information and report it |
| Internal service error | Retry later or report the issue |

## curl examples

```bash
API_KEY="${NEXSCOPE_API_KEY:-$NEXSCOPE_API_KEY}"
curl --max-time 120 -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/categoryMarket" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"tree"}'
```

```bash
curl --max-time 120 -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/categoryMarket" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"searchByName","name":"patio furniture"}'
```

```bash
curl --max-time 120 -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/categoryMarket" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"marketReport","nodePath":"4044_623679_1032619_5842891_9823303"}'
```

## Feedback API

This endpoint is separate from the tool API: `POST https://skill-api.nexscope.com/api/v1/public/feedback`, `Content-Type: application/json`.

```json
{"skillName":"nexscope-sorftime-walmart-category-market","sentiment":"NEUTRAL","category":"SUGGESTION","content":"Describe intent, result, and feedback."}
```

`sentiment` must be one of `POSITIVE`, `NEUTRAL`, or `NEGATIVE`; `category` must be one of `BUG`, `COMPLAINT`, `SUGGESTION`, or `OTHER`.
