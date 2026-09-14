## Nexscope billing

The migrated Skill does not inherit the source platform's point value. This operation consumes Nexscope credits. Preserve X-Cost-Token and X-Cost-Credit from the HTTP response headers as server-reported billing metadata, and preserve X-Kong-Trace-Id for diagnostics.

# Nexscope proxy contract

The endpoint uses the `/api/v1/tools/research/` prefix. Successful HTTP responses use a Nexscope envelope (`code`, `msg`, `data`, `traceId`, and cost metadata); the original business response is nested in `data`.

# Walmart Product Analysis API Reference

## Request conventions

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/productAnalysis`
- **Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: Bearer <api_key>`; Read api_key from `NEXSCOPE_API_KEY`, falling back to `NEXSCOPE_API_KEY`
- **User-Agent**：`Nexscope-Skill/2.0`
- **Timeout**: 120s
- **Forwarded headers**: `SESSION_ID`, `MODE_ID`, `APP_NAME`
- **Market**: Walmart US; the backend always uses Sorftime `domain=21`

The request body is flat JSON. Select exactly one case-sensitive `operation` per request; do not batch operations or automatically call them in sequence. The server identifies, validates, and decodes upstream plain JSON and Base64/GZip responses.

## Operations and request parameters

| operation | Purpose | Required parameters | Optional parameters | Default | Sorftime Request |
|---|---|---|---|---|---:|
| `searchByName` | Search related products by natural-language name | `name` | `pageIndex` | Page 1 | 2 |
| `detail` | Product details | `productId` | None | - | 1 |
| `trend` | Product trends | `productId` | None | - | 2 |
| `salesVolume` | Daily/variant sales | `productId` | `queryDate`, `queryEndDate`, `pageIndex` | Last 30 days; page 1 | 1 |

Operation and object fields:

| Parameter | Type | Rules |
|---|---|---|
| `operation` | string | Required; only `searchByName`, `detail`, `trend`, or `salesVolume` |
| `name` | string | Required for `searchByName`; nonempty natural-language product name |
| `productId` | string | Required for `detail`, `trend`, and `salesVolume`; nonempty Walmart ProductId |

Pagination and sales fields:

| Parameter | Type | Required | Description |
|---|---|---|---|
| `queryDate` | string | No | Start date, `yyyy-MM-dd` |
| `queryEndDate` | string | No | End date, `yyyy-MM-dd`; defaults to today if only the start date is provided |
| `pageIndex` | integer | No | Starts at 1 for `searchByName` and `salesVolume`, defaults to 1; at most 100 records per page |

`searchByName` maps to upstream `ProductSearchFromName`, returning related products from a natural-language name. `salesVolume` defaults to the last 30 days when both dates are omitted. The earliest available date depends on current Sorftime data coverage; the start date must not be later than the end date.

## Request examples

```json
{"operation":"searchByName","name":"wireless earbuds","pageIndex":1}
```

```json
{"operation":"detail","productId":"5169493923"}
```

```json
{"operation":"trend","productId":"5169493923"}
```

```json
{"operation":"salesVolume","productId":"5169493923","queryDate":"2026-07-01","queryEndDate":"2026-07-31","pageIndex":1}
```

## Response structure

The gateway uses two status layers: `errcode` / `errmsg` at the framework layer and `code` / `msg` in the successful business response body. Success usually returns both `errcode=200`, `errmsg="ok"` and `code=200`, `msg="success"`. Parameter or service errors may return only `errcode` / `errmsg`; check the framework status first.

| Field | Type | Description |
|---|---|---|
| `errcode` | integer | Gateway framework status code; `200` means the request successfully reached the business response |
| `errmsg` | string | Gateway framework status message; usually `ok` on success |
| `code` | integer | `200` indicates success |
| `msg` | string | Response message |
| `data` | object | Fixed response container; `data.value` preserves the original Sorftime object, array, scalar, or `null` for each operation |
| `operation` | string | The operation actually executed: `searchByName`, `detail`, `trend`, or `salesVolume` |
| `requestConsumed` | integer | Upstream consumption for this request; if missing or 0, use the documented consumption for the operation; keep 0 when Sorftime explicitly returns `Code=11` (no data) |
| `costTime` | integer | Elapsed time in milliseconds |
| `costToken` | integer | Compatibility field in the business body; read the `X-Cost-Token` response header for independent Nexscope billing |
| `sourceType` | string | `sorftime` |

When Sorftime explicitly returns `Code=11` (no data), the gateway keeps `requestConsumed=0` and `costToken=0` without filling in documented consumption.

| operation | Meaning of `data.value` |
|---|---|
| `searchByName` | Related product results as Sorftime ProductSummeryObject; at most 100 per page |
| `detail` | Sorftime ProductSummeryObject |
| `trend` | Sorftime ProductTrendObject |
| `salesVolume` | Array of rows, each shaped as `[date, sales, type]`; `type=2` indicates yesterday's sales |

The gateway preserves upstream fields. Use the actual response for object fields and trend units; do not fabricate missing values.

## Error codes

| errcode / HTTP | Meaning | Recommended action |
|---:|---|---|
| 200 | Success | Parse `data.value` according to the operation |
| 400 / 4000 | Missing required parameter; framework validation of `operation` returns 400, while business validation of operation-specific fields returns 4000 | Provide `operation`, `name` for `searchByName`, or `productId` for other operations |
| 4001 | Invalid parameter format | Check operation casing, dates, and pageIndex |
| 401 | Authentication failed | Follow the authentication guidance in SKILL.md |
| 402 | Insufficient credits | Follow the credit guidance in SKILL.md |
| 5101–5103 | Upstream HTTP, response, or parsing error | Do not automatically change dates or operations to retry |
| 5104–5108 | Upstream access restriction, parameter, IP, or permission error | Verify parameters; refer permission issues to the service maintainer |
| 5109–5111 | Upstream quota or rate limit | Retry later; do not send repeated requests |
| 5112 | Other upstream business error | Preserve the response information and report it |
| 5901 | Internal service error | Retry later or report the issue |

## curl examples

```bash
API_KEY="${NEXSCOPE_API_KEY:-$NEXSCOPE_API_KEY}"
curl --max-time 120 -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/productAnalysis" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"detail","productId":"5169493923"}'
```

```bash
curl --max-time 120 -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/productAnalysis" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"searchByName","name":"wireless earbuds","pageIndex":1}'
```

```bash
curl --max-time 120 -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/productAnalysis" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"salesVolume","productId":"5169493923","pageIndex":1}'
```

## Feedback API

Tool feedback uses a separate endpoint `POST https://skill-api.nexscope.com/api/v1/public/feedback`, `Content-Type: application/json`.

```json
{"skillName":"nexscope-sorftime-walmart-product-analysis","sentiment":"NEUTRAL","category":"SUGGESTION","content":"Describe intent, result, and feedback."}
```

`sentiment` must be one of `POSITIVE`, `NEUTRAL`, or `NEGATIVE`; `category` must be one of `BUG`, `COMPLAINT`, `SUGGESTION`, or `OTHER`.
