# Nexscope migration contract

- All callable routes use `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/`.
- Authentication is `Authorization: Bearer <NEXSCOPE_API_KEY>`.
- Successful transport responses use the Nexscope envelope; the provider business response is nested in `data`.
- This operation consumes credits. Preserve `X-Cost-Token` and `X-Cost-Credit` from response headers as server-reported billing metadata; do not inherit or convert source-platform point values.
- HTTP 401 means Nexscope authentication failed. HTTP 402 means insufficient Nexscope credits. Do not retry paid or ambiguous failures automatically.

# Temu Category and Keyword Market Research API Reference

## API Specification

- **Endpoint (Category Research)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/categorySearch`
- **Endpoint (Keyword Research)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/keywordSearch`
- **Endpoint (Site List)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/siteList`
- **Endpoint (Category List)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/categoryList`
- **HTTP Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: Bearer <api_key>`; api_key is read first from the `NEXSCOPE_API_KEY` environment variable
- **User-Agent**：`Nexscope-Skill/1.0`
- **Forwarded Headers**: `SESSION_ID`, `MESSAGE_ID`, `MODE_ID`, `APP_NAME` (empty strings when unset)
- **Timeout**: 150s

> By default, entry scripts cache only successful responses for 24 hours, including successful empty results; HTTP or business failures are not cached. `--inline` does not bypass the cache; `--no-cache` skips cache reads/writes and forces a live request. Category/keyword searches may consume compute credits again; site/category lists are only forcibly refreshed.

> The Nexscope gateway uses `regionId`, obtained from `sites[].regionId` in the site list. Do not use the upstream internal `siteId` or upstream GET paths as gateway request parameters/URLs.

## Endpoints

### Category Research: `POST /api/v1/tools/research/geekbi/temu/categorySearch`

#### Request

The following parameters are optional for both search endpoints; an empty object uses the United States site and default pagination.

| Parameter | Type | Required | Default / Constraints | Description |
|---|---|---:|---|---|
| `regionId` | integer | No | `211`；`>=1` | Temu region ID from `sites[].regionId` |
| `page` | integer | No | `1`；`>=1` | Page number |
| `size` | integer | No | `20`；`1..200` | Items per page; `page * size` must not exceed 10000 |
| `order` | string | No | `asc` / `desc`, case-insensitive | Sort direction; no gateway default |
| `sort` | string | No | Maximum 100 characters | Sort field; use only confirmed supported fields and omit when sorting is unnecessary |

Every supplied `*Min` / `*Max` pair must satisfy Min ≤ Max.

Category search and keyword search share only the following 12 range parameters. Daily/weekly/monthly sales volume, revenue, product count, shop count, and growth rates are response metrics, not request filters.

| Parameter Group | Type | Constraints / Units |
|---|---|---|
| `dsrMin`, `dsrMax` | number | Blue ocean index; use only as a combined supply-and-demand signal |
| `totalSoldMin`, `totalSoldMax` | integer | Historical cumulative units sold, `>=0` |
| `avgPriceMin`, `avgPriceMax` | number | Average price in the selected site currency, `>=0` |
| `totalSalesMin`, `totalSalesMax` | number | Historical cumulative sales revenue in the selected site currency, `>=0` |
| `itemCountMin`, `itemCountMax` | integer | Associated product count, `>=0` |
| `mallCountMin`, `mallCountMax` | integer | Associated shop count, `>=0` |

| Parameter | Type | Required | Default / Constraints | Description |
|---|---|---:|---|---|
| `keyword` | string | No | Maximum 300 characters | Category name in Chinese or English, fuzzy search |

`categorySearch` does not accept `catLevel` or `parentCatId`. Call `categoryList` to browse the category tree by parent; `catLevel` can only appear in response items.

```bash
# Category research (the Chinese keyword means pets)
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/categorySearch" \
  -H "Authorization: Bearer $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/1.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"regionId":211,"keyword":"宠物","totalSoldMin":1000,"sort":"totalSold","order":"desc","page":1,"size":3}'
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

#### Response

| Field | Type | Description |
|---|---|---|
| `title` / `type` | string | Render title and type |
| `total` | integer | Match count; may be capped at 10,000 |
| `page` / `size` | integer | Current page and items per page |
| `regionId` | integer | Actual queried region |
| `sourceTool` / `sourceType` | string | Data source metadata |
| `columns` | array | Render column definitions, not business results |
| `items` | array | Category or keyword results; observed successful calls can return nonempty results |

| Field Group | Key Fields | Description |
|---|---|---|
| Identifiers and Hierarchy | `catId`, `optId`, `catName`, `catLevel`, `parentCatId`, `parentCatItems`, `isLeaf`, `regionId` | Category ID, name, and full path |
| Display | `thumbnail` | Category thumbnail (may be absent) |
| Cumulative Market Metrics | `dsr`, `totalSold`, `totalSales`, `avgPrice`, `itemCount`, `mallCount` | Blue ocean index, demand, price, and supply |
| Semi-managed Supply | `semiManagedItemCount`, `semiManagedMallCount` | Semi-managed product and shop counts |
| Periodic Demand | `day/week/monthSold`, `day/week/monthSales` and their respective `Rate` fields | Daily, weekly, and monthly demand and growth |
| Periodic Supply | `day/week/monthItemCount`, `day/week/monthMallCount` and their respective `Rate` fields | Product/shop changes and growth rates |
| Time | `createTime`, `updateTime` | Upstream time strings; preserve unchanged |

```json
{
  "total": 231,
  "page": 1,
  "size": 3,
  "regionId": 211,
  "items": [
    {
      "catId": 1464,
      "catName": "宠物用品",
      "catLevel": 1,
      "totalSold": 81486617,
      "monthSold": 8346332,
      "avgPrice": 15.69,
      "itemCount": 26840,
      "mallCount": 11419
    }
  ]
}
```

The sample `catName` is Chinese for pet supplies. The example illustrates the shape only; field values vary with live data, and the JSON saved by the script is authoritative.

Business fields may be absent or `null`. Live responses may add fields; callers should preserve unknown extension fields.

### Keyword Research: `POST /api/v1/tools/research/geekbi/temu/keywordSearch`

#### Request

The following parameters are optional for both search endpoints; an empty object uses the United States site and default pagination.

| Parameter | Type | Required | Default / Constraints | Description |
|---|---|---:|---|---|
| `regionId` | integer | No | `211`；`>=1` | Temu region ID from `sites[].regionId` |
| `page` | integer | No | `1`；`>=1` | Page number |
| `size` | integer | No | `20`；`1..200` | Items per page; `page * size` must not exceed 10000 |
| `order` | string | No | `asc` / `desc`, case-insensitive | Sort direction; no gateway default |
| `sort` | string | No | Maximum 100 characters | Sort field; use only confirmed supported fields and omit when sorting is unnecessary |

Every supplied `*Min` / `*Max` pair must satisfy Min ≤ Max.

Category search and keyword search share only the following 12 range parameters. Daily/weekly/monthly sales volume, revenue, product count, shop count, and growth rates are response metrics, not request filters.

| Parameter Group | Type | Constraints / Units |
|---|---|---|
| `dsrMin`, `dsrMax` | number | Blue ocean index; use only as a combined supply-and-demand signal |
| `totalSoldMin`, `totalSoldMax` | integer | Historical cumulative units sold, `>=0` |
| `avgPriceMin`, `avgPriceMax` | number | Average price in the selected site currency, `>=0` |
| `totalSalesMin`, `totalSalesMax` | number | Historical cumulative sales revenue in the selected site currency, `>=0` |
| `itemCountMin`, `itemCountMax` | integer | Associated product count, `>=0` |
| `mallCountMin`, `mallCountMax` | integer | Associated shop count, `>=0` |

| Parameter | Type | Required | Default / Constraints | Description |
|---|---|---:|---|---|
| `keyword` | string | No | Maximum 300 characters | Chinese or English keyword; do not silently translate or replace user input |
| `catIds` | integer[] | No | Elements must be trusted category IDs | Multiple IDs match any of the categories; usually use first- or second-level IDs |
| `firstOnSaleTimeMin` | string | No | ISO-8601 date-time; maximum 40 characters | Lower bound for the earliest listing time of associated products |
| `firstOnSaleTimeMax` | string | No | ISO-8601 date-time; maximum 40 characters | Upper bound for the earliest listing time of associated products |

`firstOnSaleTime` is the earliest product listing time associated with the keyword, not the keyword creation time.

```bash
# Keyword research (catIds from categoryList/categorySearch)
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/keywordSearch" \
  -H "Authorization: Bearer $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/1.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"regionId":211,"keyword":"dress","catIds":[27011],"totalSoldMin":1000,"sort":"totalSold","order":"desc","page":1,"size":3}'
```

#### Response

| Field | Type | Description |
|---|---|---|
| `title` / `type` | string | Render title and type |
| `total` | integer | Match count; may be capped at 10,000 |
| `page` / `size` | integer | Current page and items per page |
| `regionId` | integer | Actual queried region |
| `sourceTool` / `sourceType` | string | Data source metadata |
| `columns` | array | Render column definitions, not business results |
| `items` | array | Category or keyword results; observed successful calls can return nonempty results |

| Field Group | Key Fields | Description |
|---|---|---|
| Keywords | `id`, `keyword`, `cnKeyword`, `thumbnail`, `regionId` | Keyword identifier, text, and region |
| Associated Categories | `catIds`, `catItems` | Category IDs and paths; lists may contain duplicate leaf IDs, which may be deduplicated for display without rewriting raw data |
| Cumulative Market Metrics | `dsr`, `totalSold`, `totalSales`, `avgPrice`, `itemCount`, `mallCount` | Blue ocean index, demand, price, and supply |
| Semi-managed Supply | `semiManagedItemCount`, `semiManagedMallCount` | Semi-managed product and shop counts |
| Periodic Demand/Supply | The same daily, weekly, and monthly `Sold`, `Sales`, `ItemCount`, `MallCount`, and `Rate` fields as category results | Trends and supply changes |
| Time | `firstOnSaleTime`, `createTime`, `updateTime` | Earliest associated product listing time and upstream timestamps |

Business fields may be absent or `null`. Live responses may add fields; callers should preserve unknown extension fields.

### Site List: `POST /api/v1/tools/research/geekbi/temu/siteList`

#### Request

The request body is fixed to `{}`. Select the `sites[]` record matching the user's country and pass its nonempty positive-integer `regionId` to both search endpoints; do not use `siteId`.

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

- Both helper endpoints share business `title`, `type`, `sourceType`, `sourceTool`, and render metadata `columns`; they do not inherit `page`, `size`, `regionId`, or `items` from search responses.
- The site list additionally contains `total` + `sites[]`. Site entries contain `regionId`, `siteId`, `name`, `cnName`, `lang`, `currency`.

Business fields may be absent or `null`. Live responses may add fields; callers should preserve unknown extension fields.

### Category List: `POST /api/v1/tools/research/geekbi/temu/categoryList`

#### Request

| Parameter | Type | Required | Default / Constraints | Description |
|---|---|---:|---|---|
| `parentCatId` | integer | No | Omitted; `>=0` | Omit to return top-level categories; pass a known `catId` to return immediate children |

Obtain values from `categories[].catId`. When drilling down level by level, reuse only IDs actually returned.

```bash
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/categoryList" \
  -H "Authorization: Bearer $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/1.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"parentCatId":27011}'
```

#### Response

- Both helper endpoints share business `title`, `type`, `sourceType`, `sourceTool`, and render metadata `columns`; they do not inherit `page`, `size`, `regionId`, or `items` from search responses.
- The category list additionally contains `total` + `categories[]` and may contain `parentCatId` when a parent is supplied. Category entries contain `catId`, `catName`, `catLevel`, `parentCatId`, `isLeaf`.

Business fields may be absent or `null`. Live responses may add fields; callers should preserve unknown extension fields.

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Meaning | Action |
| Parameter type, range, or Min/Max relationship error | Correct the current parameters; do not automatically change conditions and probe repeatedly |
| Current credentials lack permission | Stop and explain; do not retry through the authentication/billing flow |
| Gateway or upstream error | Do not automatically retry paid category/keyword searches; explain that another charge may occur and obtain user confirmation before retrying once with the original parameters. Free site/category helper endpoints may be retried 1–2 times with the original parameters |

The entry script echoes HTTP errors as JSON. Invalid `size: 0` was verified to return `{"error":"HTTP 400: Bad Request","details":"...size 必须为整数[1,200]..."}` (size must be an integer in [1,200]), without printing a Python stack trace.

Legacy local cache: a still-valid cache created before this response contract remains usable without a new paid request. The scripts mark its copied metadata as `_nexscope.responseContract = "legacy-cache"`, with `_nexscope.code` and `_nexscope.msg` set to `null` because the original platform status/message is unavailable. Do not infer platform success from business `errcode`, `code`, or `status`. Existing business data, billing metadata, cache contents and expiration are preserved; the marker is added only to the in-memory output.
