## Nexscope billing

The migrated Skill does not inherit the source platform's point value. This operation consumes Nexscope credits. Preserve X-Cost-Token and X-Cost-Credit from the HTTP response headers as server-reported billing metadata, and preserve X-Kong-Trace-Id for diagnostics.

# Nexscope proxy contract

The endpoint uses the `/api/v1/tools/research/` prefix. Successful HTTP responses use a Nexscope envelope (`code`, `msg`, `data`, `traceId`, and cost metadata); the original business response is nested in `data`.

# Walmart Keyword Research API Reference

## Request conventions

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/keywordResearch`
- **Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: Bearer <api_key>`; Read api_key from `NEXSCOPE_API_KEY`, falling back to `NEXSCOPE_API_KEY`
- **User-Agent**：`Nexscope-Skill/2.0`
- **Timeout**: 120s
- **Forwarded headers**: `SESSION_ID`, `MODE_ID`, `APP_NAME`
- **Market**: Walmart US; the backend always uses Sorftime `domain=21`

The request body uses flat lowerCamel JSON, with exactly one case-sensitive `operation` per request. `marketQuery.pattern` is the only nested business object; do not wrap parameters in `params` or automatically execute multiple operations in sequence. The server identifies, validates, and decodes upstream plain JSON and Base64/GZip responses.

## Operation matrix

| operation | Purpose | Required parameters | Optional parameters | Default | Sorftime Request |
|---|---|---|---|---|---:|
| `marketQuery` | Filter current trending keywords | None | `pattern`, `pageIndex`, `pageSize` | Page 1, 20 records | 5 |
| `searchByName` | Find trending keywords by product/category name | `name` | `pageIndex` | Page 1 | 1 |
| `searchProducts` | Products in trending keyword search results | `keyword` | `pageIndex`, `pageSize` | Page 1, 20 records | 5 |
| `detail` | Keyword details | `keyword` | None | - | 1 |
| `productKeywords` | Keywords associated with a product | `productId` | `pageIndex`, `pageSize` | Page 1, 20 records | 1 |
| `relatedKeywords` | Expand related keywords | `keyword` | `pageIndex`, `pageSize` | Page 1, 20 records | 5 |
| `favoriteList` | Look up saved keywords or directories | `command` | `pageIndex` | Page 1 | 1 |

## Parameter rules

### marketQuery

`pattern` may contain `keyword` (a nonempty string), `rankCondition`, and `searchVolumeCondition`. Each condition field contains 1 or 2 nonnegative integers; the lower bound must not exceed the upper bound. A single element `[10000]` means greater than 10000; two elements `[0,10000]` mean less than 10000 according to the official semantics. `pageSize` ranges from 20–200.

### Query operations

- `searchByName.name` is a product or category name; `pageIndex` starts at 1, with at most 200 records per page.
- `searchProducts` supports only current trending keywords and returns products appearing in search results within the last 15 days; `pageSize` is 20–200.
- `detail.keyword` is one nonempty keyword.
- `productKeywords` returns keywords for which the product appeared in the first three search result pages within the last 30 days; `productId` is a string and `pageSize` is 20–200.
- `relatedKeywords` uses one seed keyword; `pageSize` is 20–200.

### Public favorite lookup

- `favoriteList`: `command` allows only `all`, `dict`, or `dict=<directory>`; the public parameter is consistently `pageIndex`, which the backend maps to upstream `Page`; at most 100 records per page.
- `favoriteAdd` and `favoriteChange` are intentionally excluded from this public read-only migration.
- The API keyword library and Sorftime Professional favorites are separate; saved data is not shared.

## Request examples

```json
{"operation":"marketQuery","pattern":{"keyword":"wireless","searchVolumeCondition":[10000]},"pageIndex":1,"pageSize":20}
```

```json
{"operation":"searchByName","name":"wireless earbuds","pageIndex":1}
```

```json
{"operation":"favoriteList","command":"dict","pageIndex":1}
```

Write operation format example (do not execute without authorization):

```json
The client rejects `favoriteAdd` and `favoriteChange` before any HTTP request.
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

The successful business response body has the same structure for every operation: `data`, `operation`, `requestConsumed`, `costTime`, `costToken`, and `sourceType`. `operation` echoes the operation actually executed. `data` is a fixed object container; `data.value` can be an object, array, number, string, or `null`, preserved exactly as returned by Sorftime. `requestConsumed` is the upstream consumption for this request; when missing or 0, it is filled with the documented consumption for the operation. When Sorftime explicitly returns `Code=11` (no data), consumption is not filled in: `requestConsumed=0` and `costToken=0` are preserved. `sourceType` is `sorftime`.

| operation | Meaning of `data.value` |
|---|---|
| `marketQuery` | Keyword summary data |
| `searchByName` | Trending keywords related to a product or category name |
| `searchProducts` | ProductSummeryObject product summaries; last 15-day window |
| `detail` | KeywordSummeryObject |
| `productKeywords` | ProductKeywordItemObject; last 30-day window |
| `relatedKeywords` | KeywordSummeryObject expanded keywords |
| `favoriteList` | String array whose content depends on `command` |

Use the actual Sorftime response for specific business object fields.

## Error codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Missing required parameter; framework validation of globally required fields returns 400, while business validation of conditionally required fields returns 4000 | Provide the conditionally required fields for the operation |
| Invalid parameter format | Check operation casing, pagination, condition arrays, and command |
| Authentication failed | Follow the authentication guidance in SKILL.md |
| Insufficient credits | Follow the credit guidance in SKILL.md |
| Upstream HTTP, response, or parsing error | Do not automatically change keywords, advance pages, or switch operation |
| Upstream access restriction, parameter, IP, or permission error | Verify parameters; refer permission issues to the service maintainer |
| Upstream quota or rate limit | Retry later; do not send repeated requests |
| Other upstream business error | Preserve the response information and report it |
| Internal service error | Retry later or report the issue |

## curl examples

```bash
API_KEY="${NEXSCOPE_API_KEY:-$NEXSCOPE_API_KEY}"
curl --max-time 120 -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/keywordResearch" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"marketQuery","pattern":{"keyword":"wireless"},"pageIndex":1,"pageSize":20}'
```

```bash
curl --max-time 120 -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/keywordResearch" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"favoriteList","command":"dict","pageIndex":1}'
```

## Feedback API

Tool feedback uses a separate endpoint `POST https://skill-api.nexscope.com/api/v1/public/feedback`, `Content-Type: application/json`.

```json
{"skillName":"nexscope-sorftime-walmart-keyword-research","sentiment":"NEUTRAL","category":"SUGGESTION","content":"Describe intent, result, and feedback."}
```

`sentiment` must be one of `POSITIVE`, `NEUTRAL`, or `NEGATIVE`; `category` must be one of `BUG`, `COMPLAINT`, `SUGGESTION`, or `OTHER`.
