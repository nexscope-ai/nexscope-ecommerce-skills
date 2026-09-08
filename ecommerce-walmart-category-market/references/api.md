## NexScope billing

The migrated Skill does not inherit the source platform's point value. This operation consumes NexScope credits. Preserve X-Cost-Token and X-Cost-Credit from the HTTP response headers as server-reported billing metadata, and preserve X-Kong-Trace-Id for diagnostics.

# NexScope proxy contract

The endpoint uses the `/api/v1/tools/research/` prefix. Successful HTTP responses use a NexScope envelope (`code`, `msg`, `data`, `traceId`, and cost metadata); the original business response is nested in `data`.

# Walmart Category Market API Reference

## Request conventions

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/categoryMarket`
- **Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: Bearer <api_key>`; Read api_key from `NEXSCOPE_API_KEY`, falling back to `NEXSCOPE_API_KEY`
- **User-Agent**：`NexScope-Skill/2.0`
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

## Response structure

The gateway uses two status layers: `errcode` / `errmsg` at the framework layer and `code` / `msg` in the successful business response body. Success usually returns both `errcode=200`, `errmsg="ok"` and `code=200`, `msg="success"`. Parameter or service errors may return only `errcode` / `errmsg`; check the framework status first.

| Field | Type | Description |
|---|---|---|
| `errcode` | integer | Gateway framework status code; `200` means the request successfully reached the business response |
| `errmsg` | string | Gateway framework status message; usually `ok` on success |
| `code` | integer | `200` indicates success |
| `msg` | string | Response message; no-data responses may contain "查询成功，但无数据" (query succeeded, but no data) |
| `data` | object | Fixed response container; `data.value` preserves the original Sorftime array, object, scalar, or `null` according to the operation |
| `operation` | string | The operation actually executed: `tree`, `searchByName`, or `marketReport` |
| `requestConsumed` | integer | Upstream consumption for this request; if missing or 0, use the documented consumption for the operation; keep 0 when Sorftime explicitly returns `Code=11` (no data) |
| `costTime` | integer | Elapsed time in milliseconds |
| `costToken` | integer | Compatibility field in the business body; read the `X-Cost-Token` response header for independent NexScope billing |
| `sourceType` | string | `sorftime` |

When Sorftime explicitly returns `Code=11` (no data), the gateway keeps `requestConsumed=0` and `costToken=0` without filling in documented consumption.

Read business results from `data.value`. `tree` nodes may contain `Id`, `ParentId`, `NodeId`, `Name`, `CNName`, and `URL`; the complete tree is approximately 10 MB. `searchByName` returns Sorftime `CategorySearchFromName` data: at most 3 related categories, each containing `NodeId` and `CategoryName`. `marketReport` returns category market data and up to the Top 80 Best Seller products; use the actual response for specific fields.

## Error codes

| errcode / HTTP | Meaning | Recommended action |
|---:|---|---|
| 200 | Success | Parse `data.value` according to the selected operation |
| 400 / 4000 | Missing required parameter; framework validation of globally required fields returns 400, while business validation of conditionally required fields returns 4000 | Provide `operation`, `name` for `searchByName`, or `nodePath` for `marketReport` |
| 4001 | Invalid parameter format | Check operation casing, a nonempty name, and nodePath format |
| 401 | Authentication failed | Follow the authentication guidance in SKILL.md |
| 402 | Insufficient credits | Follow the credit guidance in SKILL.md |
| 5101–5103 | Upstream HTTP, response, or parsing error | Do not automatically change parameters and retry repeatedly |
| 5104–5108 | Upstream access restriction, parameter, IP, or permission error | Verify parameters; refer permission issues to the service maintainer |
| 5109–5111 | Upstream quota or rate limit | Retry later; do not send repeated requests |
| 5112 | Other upstream business error | Preserve the response information and report it |
| 5901 | Internal service error | Retry later or report the issue |

## curl examples

```bash
API_KEY="${NEXSCOPE_API_KEY:-$NEXSCOPE_API_KEY}"
curl --max-time 120 -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/categoryMarket" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"tree"}'
```

```bash
curl --max-time 120 -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/categoryMarket" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"searchByName","name":"patio furniture"}'
```

```bash
curl --max-time 120 -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/categoryMarket" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"marketReport","nodePath":"4044_623679_1032619_5842891_9823303"}'
```

## Feedback API

This endpoint is separate from the tool API: `POST https://skill-api.nexscope.com/api/v1/public/feedback`, `Content-Type: application/json`.

```json
{"skillName":"nexscope-sorftime-walmart-category-market","sentiment":"NEUTRAL","category":"SUGGESTION","content":"Describe intent, result, and feedback."}
```

`sentiment` must be one of `POSITIVE`, `NEUTRAL`, or `NEGATIVE`; `category` must be one of `BUG`, `COMPLAINT`, `SUGGESTION`, or `OTHER`.
