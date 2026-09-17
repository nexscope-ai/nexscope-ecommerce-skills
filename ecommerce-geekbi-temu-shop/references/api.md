# Nexscope migration contract

- All callable routes use `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/`.
- Authentication is `Authorization: Bearer <NEXSCOPE_API_KEY>`.
- Successful transport responses use the Nexscope envelope; the provider business response is nested in `data`.
- This operation consumes credits. Preserve `X-Cost-Token` and `X-Cost-Credit` from response headers as server-reported billing metadata; do not inherit or convert source-platform point values.
- HTTP 401 means Nexscope authentication failed. HTTP 402 means insufficient Nexscope credits. Do not retry paid or ambiguous failures automatically.

# Temu Shop Research API Reference

## API Specification

- **Endpoint (Shop Search)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/mallSearch`
- **Endpoint (Site List)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/siteList`
- **Endpoint (Category List)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/categoryList`
- **HTTP Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: Bearer <api_key>`; api_key is read first from the `NEXSCOPE_API_KEY` environment variable
- **User-Agent**：`Nexscope-Skill/1.0`
- **Forwarded Headers**: `SESSION_ID`, `MESSAGE_ID`, `MODE_ID`, `APP_NAME` (empty strings when unset)
- **Timeout**: 150s

> By default, entry scripts cache only successful responses for 24 hours, including successful empty results; HTTP or business failures are not cached. `--inline` does not bypass the cache; `--no-cache` skips cache reads/writes and forces a live request. Shop searches may consume compute credits again; site/category lists are only forcibly refreshed.

> These URLs are Nexscope tool gateway routes. The server then calls the upstream GET API; clients must not use upstream `/api/v1/temu/...` paths as gateway URLs.

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Package scripts unwrap this platform object for their business output and retain its `code`, `msg`, and timing metadata under `_nexscope`; for those outputs, inspect `_nexscope.code` / `_nexscope.msg`. Business `code` or `error` fields are not platform success markers.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Common Response Fields


Live integration verification summary: the site list returned 33 sites; first-level categories returned 23 nodes. Searching with `regionId=211`, `page=1`, `size=3`, `mallStarMin=4` returned 3 nonempty shop records, with upstream `total=10000`.

Each column definition usually contains `field`, `title`, `cellType`, `sortable`, `filterable`; common `cellType` values are `number` or `text`.

## Endpoints

### Shop Search: `POST /api/v1/tools/research/geekbi/temu/mallSearch`

#### Request

POST body (JSON). All fields are optional; an empty object `{}` uses `regionId=211`, `page=1`, `size=20`.

##### Pagination, Keywords, Categories, and Management Mode

| Parameter | Type | Required | Default / Constraints | Description |
|---|---|---:|---|---|
| `regionId` | integer | No | `211`；`>=1` | Temu region ID; obtain it from `sites[].regionId` in the site list |
| `page` | integer | No | `1`；`>=1` | Page number |
| `size` | integer | No | `20`；`1..200` | Items per page; `page * size` must not exceed 10000 |
| `keyword` | string | No | Maximum 300 characters | Keyword matching shop names |
| `catIds` | integer[] | No | - | Category ID array; obtain elements from `categories[].catId` in the category list |
| `hostingMode` | integer | No | `1..2` | `1`=fully managed, `2`=semi-managed |
| `sort` | string | No | Maximum 100 characters | Sort field; use only fields confirmed to be supported by the endpoint |
| `order` | string | No | `asc` or `desc` | Sort direction, case-insensitive |

In gateway JSON, `catIds` must be an array, e.g. `{"catIds":[1,27011]}`. The server encodes the array as a single comma-separated upstream parameter; do not send comma-separated strings or duplicate keys in JSON.

##### Shop Metric Ranges

| Parameter Group | Type | Constraints / Units |
|---|---|---|
| `mallSoldMin`, `mallSoldMax` | integer | Shop historical cumulative units sold, `>=0` |
| `mallSalesMin`, `mallSalesMax` | number | Shop historical cumulative sales revenue in the current site currency, `>=0` |
| `mallStarMin`, `mallStarMax` | number | Shop rating, `0..5` |
| `reviewNumMin`, `reviewNumMax` | integer | Shop historical cumulative review count, `>=0` |
| `goodsNumMin`, `goodsNumMax` | integer | Shop products currently on sale, `>=0` |
| `followerNumMin`, `followerNumMax` | integer | Shop follower count, `>=0` |
| `avgPriceMin`, `avgPriceMax` | number | Shop average order value in the current site currency, `>=0` |

Every paired `*Min` must not exceed its corresponding `*Max`.

##### Shop Opening Time

| Parameter Group | Type | Description |
|---|---|---|
| `mallOpenTimeMin`, `mallOpenTimeMax` | string | Shop opening time range, ISO-8601 date-time, maximum 40 characters |

When both minimum and maximum times are supplied, both must be valid ISO-8601 date-time values, and the minimum must not be later than the maximum.

```bash
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/mallSearch" \
  -H "Authorization: Bearer $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/1.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"regionId":211,"page":1,"size":3,"mallStarMin":4}'
```

#### Response

| Field | Type | Description |
|---|---|---|
| `items` | array | Shops on the current page; every business field may be absent or `null` |
| `columns` | array | Render column definitions; 49 definitions in the observed response |
| `total` | integer | Total matches reported upstream; the service limits the accessible window to `page * size <= 10000` |
| `page` | integer | Current page number |
| `size` | integer | Items per page |
| `regionId` | integer | Region ID used for this request |
| `title` | string | `Temu 数据查询` (Temu data query) |
| `sourceType` | string | `temu` |
| `sourceTool` | string | `geekbi_temu` |
| `type` | string | `tableListWorkbenches` |

##### Shop Fields `items[]`

| Field Group | Field |
|---|---|
| Identifiers and Basic Information | `id`, `mallId`, `mallLogo`, `mallName`, `regionId`, `hot` |
| Categories | `catIds`, `catItems` |
| Core Performance | `mallStar`, `reviewNum`, `goodsNum`, `followerNum`, `mallSold`, `mallSales`, `avgPrice` |
| Management Mode and Time | `hostingMode`, `mallOpenTime`, `createTime`, `updateTime` |
| Follower Changes | `dayFollower`, `weekFollower`, `monthFollower` and corresponding `*Rate` fields |
| Product Count Changes | `dayItemCount`, `weekItemCount`, `monthItemCount` and corresponding `*Rate` fields |
| Sales Revenue | `daySales`, `weekSales`, `monthSales` and corresponding `*Rate` fields |
| Products with Sales | `daySellthroughCount`, `weekSellthroughCount`, `monthSellthroughCount` and corresponding `*Rate` fields |
| Sales Volume | `daySold`, `weekSold`, `monthSold` and corresponding `*Rate` fields |
| Upstream Extensions | `extraFields`; returned only when upstream fields are not yet included in the fixed contract |

`catItems[]` may contain `catId`, `catLevel`, `catName`, `isLeaf`, `parentCatId`, `extraFields`. Interpret monetary fields in the current site currency; preserve upstream string formats for time fields. All business fields may be absent or `null`.

The examples below use successful live responses from 2026-08-27 to confirm field hierarchy. Business values are illustrative only; nullable fields may be omitted.

```json
{
  "total": 10000,
  "page": 1,
  "size": 3,
  "regionId": 211,
  "items": [
    {
      "mallId": "634418224987870",
      "mallName": "cazan",
      "mallStar": 4.6,
      "mallSold": 5817,
      "mallSales": 101534.72,
      "followerNum": 25,
      "goodsNum": 2,
      "hostingMode": 2,
      "catIds": []
    }
  ],
  "columns": [],
  "title": "Temu 数据查询",
  "sourceType": "temu",
  "sourceTool": "geekbi_temu",
  "type": "tableListWorkbenches"
}
```

### Site List: `POST /api/v1/tools/research/geekbi/temu/siteList`

#### Request

No business parameters; send `{}` as the body. Use only nonempty positive-integer `sites[].regionId` for shop search; `sites[].siteId` is an upstream internal ID and must not replace `regionId`. If no valid `regionId` exists, stop chained calls and inform the user.

```bash
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/siteList" \
  -H "Authorization: Bearer $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/1.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{}'
```

#### Response

| Field | Type | Description |
|---|---|---|
| `sites` | array | Supported Temu sites |
| `total` | integer | Site count |
| `title` / `sourceType` / `sourceTool` / `type` | string | `Temu 站点列表` (Temu site list) / `temu` / `geekbi_temu` / `tableListWorkbenches` |
| `columns` | array | Render column definitions |

`sites[]` fields: `siteId` (internal ID, not used for filtering), `regionId`, `name`, `cnName` (Chinese name; the sample value means United States), `lang`, `currency`, `extraFields`. Business fields may be null; filter out empty `regionId` values before chained calls.

### Category List: `POST /api/v1/tools/research/geekbi/temu/categoryList`

#### Request

| Parameter | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `parentCatId` | integer | No | `>=0` | Omit to return first-level categories; pass a `categories[].catId` to query its immediate children |

First use `{}` to obtain first-level nodes. When drilling down, use only a nonempty nonnegative-integer `catId` as the next request's `parentCatId`; when filtering shops, put only valid `catId` values in the `catIds` array. Passing `0` is valid, but there is no evidence that it is equivalent to omitting `parentCatId`.

```bash
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/categoryList" \
  -H "Authorization: Bearer $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/1.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"parentCatId":1}'
```

#### Response

| Field | Type | Description |
|---|---|---|
| `categories` | array | Category nodes under the specified parent |
| `total` | integer | Number of returned nodes |
| `parentCatId` | integer / omitted | Parent ID for this query; may be omitted for first-level queries |
| `title` / `sourceType` / `sourceTool` / `type` | string | `Temu 品类列表` (Temu category list) / `temu` / `geekbi_temu` / `tableListWorkbenches` |
| `columns` | array | Render column definitions |

`categories[]` fields: `catId`, `catName`, `catLevel`, `parentCatId`, `isLeaf`, `extraFields`. Only nonempty valid `catId` values may be used for shop search `catIds` or the next `parentCatId`.

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Upstream business rejection | Stop or correct parameters according to the error message; do not parse it as success |
| Parameter validation failed | Correct fields; do not automatically change keywords, pages, or sites and retry repeatedly |
| Authentication failed | Check `NEXSCOPE_API_KEY` and follow the authentication guidance in `SKILL.md` |
| Insufficient compute credits or balance | Stop calling and follow the authentication/compute-credit guidance |
| Access denied | Stop calling and contact the tool administrator; do not treat this as a top-up issue |
| Too many requests | Stop repeated calls and try again later |
| Gateway or upstream error | Do not automatically retry paid shop searches; explain that another charge may occur and obtain user confirmation before retrying once with the original parameters. Free site/category helper endpoints may be retried 1–2 times with the original parameters |

Shop search rejects `regionId<1`, `page<1`, `size` outside 1–200, `page*size>10000`, invalid `hostingMode/order`, `mallStar` outside 0–5, and any minimum exceeding its maximum. Null values in `catIds` are filtered out; callers should send only valid integers.

Legacy local cache: a still-valid cache created before this response contract remains usable without a new paid request. The scripts mark its copied metadata as `_nexscope.responseContract = "legacy-cache"`, with `_nexscope.code` and `_nexscope.msg` set to `null` because the original platform status/message is unavailable. Do not infer platform success from business `errcode`, `code`, or `status`. Existing business data, billing metadata, cache contents and expiration are preserved; the marker is added only to the in-memory output.
