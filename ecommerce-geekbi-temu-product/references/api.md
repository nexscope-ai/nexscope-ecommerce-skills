# NexScope migration contract

- All callable routes use `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/`.
- Authentication is `Authorization: Bearer <NEXSCOPE_API_KEY>`.
- Successful transport responses use the NexScope envelope; the provider business response is nested in `data`.
- This operation consumes credits. Preserve `X-Cost-Token` and `X-Cost-Credit` from response headers as server-reported billing metadata; do not inherit or convert source-platform point values.
- HTTP 401 means NexScope authentication failed. HTTP 402 means insufficient NexScope credits. Do not retry paid or ambiguous failures automatically.

# Temu Product Search and Detail API Reference

## API Specification

- **Endpoint (Product Search)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/goodsSearch`
- **Endpoint (Product Detail)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/goodsDetail`
- **Endpoint (Site List)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/siteList`
- **Endpoint (Category List)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/categoryList`
- **HTTP Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: Bearer <api_key>`; api_key is read first from the `NEXSCOPE_API_KEY` environment variable
- **User-Agent**：`NexScope-Skill/1.0`
- **Forwarded Headers**: `SESSION_ID`, `MESSAGE_ID`, `MODE_ID`, `APP_NAME` (empty strings when unset)
- **Timeout**: 150s

> By default, entry scripts cache only successful responses for 24 hours, including successful empty results; HTTP or business failures are not cached. `--inline` does not bypass the cache; `--no-cache` skips cache reads/writes and forces a live request. Product search/detail calls may consume compute credits again; site/category lists are only forcibly refreshed.

> These URLs are NexScope tool gateway routes. The server then calls the GeekBI upstream GET API; clients must not use upstream `/api/v1/temu/...` paths as gateway URLs.

## Common Gateway Success Fields

| Field | Type | Verified Success Value | Description |
|---|---|---|---|
| `errcode` | integer | `200` | Gateway business status code; check it even when HTTP status is 200 |
| `errmsg` | string | `ok` | Gateway business status message |

Live integration verification summary: the site list returned 33 sites, including the United States with `regionId=211`; first-level categories returned 23 nodes, and children of `parentCatId=27011` returned 12 nodes. Searching with `regionId=211`, `catIds=[27011]` returned 3 samples (upstream `total=10000`); a subsequent detail query using the first `goodsId` returned a product object and 13 history records.

The examples below use successful live responses from 2026-08-27 to confirm field hierarchy. Business values are illustrative only; nullable business fields may be omitted.

## Product Fields (Search `items[]` / Detail `goods`)

| Field Group | Field |
|---|---|
| Identifiers and Text | `goodsId`, `mallId`, `thumbnail`, `goodsName`, `goodsNameCn`, `goodsNameEn`, `brand`, `sku` |
| Categories | `catIds`, `catItems` |
| Sales Volume and Stock | `sold`, `quantity`, `daySold`, `weekSold`, `monthSold`, `mallSold` |
| Monetary Values | `sales`, `minPrice`, `maxPrice`, `daySales`, `weekSales`, `monthSales` |
| Sales Volume Growth Rates | `daySoldRate`, `weekSoldRate`, `monthSoldRate` |
| Sales Revenue Growth Rates | `daySalesRate`, `weekSalesRate`, `monthSalesRate` |
| Supply Prices | `supplyPrice`, `minSupplyPrice`, `medianSupplyPrice`, `maxSupplyPrice` |
| Reviews | `goodsScore`, `reviewNum` |
| Status | `hostingMode`, `status`, `isAd`, `isCustom`, `isPresale` |
| Time | `onSaleTime`, `mallOpenTime`, `createTime`, `updateTime` |
| Other | `similarNum`, `extraFields` |

`catItems[]` contains `catId`, `catLevel`, `catName`, `isLeaf`, `parentCatId`, `extraFields`. Interpret monetary fields in the current site currency, except supply prices.

## Product Search: `POST /api/v1/tools/research/geekbi/temu/goodsSearch`

### Request

POST body (JSON). All fields are optional; an empty object `{}` uses `regionId=211`, `page=1`, `size=20`, `matchMode=2`.

#### Pagination, Matching, Categories, and Status

| Parameter | Type | Required | Default / Constraints | Description |
|---|---|---:|---|---|
| `regionId` | integer | No | `211`；`>=1` | Temu region ID; obtain it from `sites[].regionId` in the site list |
| `page` | integer | No | `1`；`>=1` | Page number |
| `size` | integer | No | `20`；`1..200` | Items per page; `page * size` must not exceed 10000 |
| `keyword` | string | No | Maximum 300 characters | Keyword matching product titles |
| `matchMode` | integer | No | `2`；`1..2` | `1`=strict matching, `2`=fuzzy matching |
| `catIds` | integer[] | No | - | Category ID array; obtain elements from `categories[].catId` in the category list |
| `status` | integer[] | No | Elements must be `1`, `2`, or `3` | `1`=normal, `2`=out of stock, `3`=delisted |
| `hostingMode` | integer | No | `1..2` | `1`=fully managed, `2`=semi-managed |
| `sort` | string | No | Maximum 100 characters | Sort field; use only fields confirmed to be supported by the endpoint |
| `order` | string | No | `asc` or `desc` | Sort direction, case-insensitive |

In gateway JSON, `catIds` and `status` must be arrays, e.g. `{"catIds":[984,982],"status":[1,2]}`. The server encodes each array as a single comma-separated upstream parameter; do not send comma-separated strings or duplicate keys in JSON.

#### Sales Volume, Revenue, and Growth Rates

| Parameter Group | Type | Constraints / Units |
|---|---|---|
| `soldMin`, `soldMax` | integer | Historical cumulative units sold, `>=0` |
| `daySoldMin`, `daySoldMax` | integer | Average daily units sold, `>=0` |
| `weekSoldMin`, `weekSoldMax` | integer | Average weekly units sold, `>=0` |
| `monthSoldMin`, `monthSoldMax` | integer | Average monthly units sold, `>=0` |
| `daySoldRateMin`, `daySoldRateMax` | number | Daily sales volume growth rate, percentage |
| `weekSoldRateMin`, `weekSoldRateMax` | number | Weekly sales volume growth rate, percentage |
| `monthSoldRateMin`, `monthSoldRateMax` | number | Monthly sales volume growth rate, percentage |
| `salesMin`, `salesMax` | number | Historical cumulative sales revenue in the current site currency, `>=0` |
| `daySalesMin`, `daySalesMax` | number | Average daily sales revenue in the current site currency, `>=0` |
| `weekSalesMin`, `weekSalesMax` | number | Average weekly sales revenue in the current site currency, `>=0` |
| `monthSalesMin`, `monthSalesMax` | number | Average monthly sales revenue in the current site currency, `>=0` |
| `daySalesRateMin`, `daySalesRateMax` | number | Daily sales revenue growth rate, percentage |
| `weekSalesRateMin`, `weekSalesRateMax` | number | Weekly sales revenue growth rate, percentage |
| `monthSalesRateMin`, `monthSalesRateMax` | number | Monthly sales revenue growth rate, percentage |

#### Prices, Stock, Shops, and Reviews

| Parameter Group | Type | Constraints / Units |
|---|---|---|
| `quantityMin`, `quantityMax` | integer | Remaining stock, `>=0` |
| `mallSoldMin`, `mallSoldMax` | integer | Shop historical cumulative units sold, `>=0` |
| `priceMin`, `priceMax` | number | Product price in the current site currency, `>=0` |
| `supplyPriceMin`, `supplyPriceMax` | number | Supply price in CNY, `>=0` |
| `goodsScoreMin`, `goodsScoreMax` | number | Product rating, `0..5` |
| `reviewNumMin`, `reviewNumMax` | integer | Historical cumulative review count, `>=0` |

#### Time Ranges

| Parameter Group | Type | Description |
|---|---|---|
| `onSaleTimeMin`, `onSaleTimeMax` | string | Product listing time range, ISO-8601 date-time, maximum 40 characters |
| `mallOpenTimeMin`, `mallOpenTimeMax` | string | Shop opening time range, ISO-8601 date-time, maximum 40 characters |

Every paired `*Min` must not exceed its corresponding `*Max`. Always use ISO-8601 date-time for time fields; the server parses and compares times only when both Min/Max in the same group are supplied. A single invalid time string may be rejected upstream.

#### curl Examples

```bash
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/goodsSearch" \
  -H "Authorization: Bearer $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/1.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"regionId":211,"keyword":"dress","catIds":[984],"page":1,"size":20,"sort":"sold","order":"desc"}'
```

### Response

| Field | Type | Description |
|---|---|---|
| `items` | array | Products on the current page; every business field may be absent or `null` |
| `columns` | array | Render column definitions |
| `total` | integer | Total matches reported upstream; the service limits only the accessible window to `page * size <= 10000` without truncating `total`; if absent upstream, falls back to the current `items` length |
| `page` | integer | Current page number |
| `size` | integer | Items per page |
| `regionId` | integer | Region ID used for this request |
| `title` | string | `Temu 数据查询` (Temu data query) |
| `sourceType` | string | `temu` |
| `sourceTool` | string | `geekbi_temu` |
| `type` | string | `tableListWorkbenches` |

#### Response Example

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "total": 1,
  "page": 1,
  "size": 20,
  "regionId": 211,
  "items": [
    {
      "goodsId": "601099512345678",
      "goodsName": "Example product",
      "catIds": [984],
      "sold": 12,
      "sales": 3.5
    }
  ],
  "columns": [],
  "title": "Temu 数据查询",
  "sourceType": "temu",
  "sourceTool": "geekbi_temu",
  "type": "tableListWorkbenches"
}
```

## Product Detail: `POST /api/v1/tools/research/geekbi/temu/goodsDetail`

### Request

| Parameter | Type | Required | Default / Constraints | Description |
|---|---|---:|---|---|
| `goodsId` | string | Yes | Nonempty; maximum 100 characters | Temu product ID, usually from search `items[].goodsId` |
| `regionId` | integer | No | `211`；`>=1` | Temu region ID; use the same value as in the search |

#### curl Examples

```bash
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/goodsDetail" \
  -H "Authorization: Bearer $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/1.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"goodsId":"601099512345678","regionId":211}'
```

### Response

| Field | Type | Description |
|---|---|---|
| `goods` | object | Product object, with the same fields as search `items[]` |
| `history` | array | History records from the last 30 days; business fields may be absent or `null` |
| `regionId` | integer | Region ID used for this request |
| `title` | string | `Temu 商品详情` (Temu product detail) |
| `sourceType` | string | `temu` |
| `sourceTool` | string | `geekbi_temu` |
| `type` | string | `productWorkbenches` |
| `columns` | array | Product detail render columns |

#### Product History `history[]`

All history entry fields may be absent or `null`:

`id`, `sold`, `sales`, `minPrice`, `maxPrice`, `quantity`, `goodsScore`, `reviewNum`, `daySold`, `weekSold`, `monthSold`, `daySales`, `weekSales`, `monthSales`, `daySoldRate`, `weekSoldRate`, `monthSoldRate`, `daySalesRate`, `weekSalesRate`, `monthSalesRate`, `createTime`, `extraFields`。

#### Response Example

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "goods": {"goodsId": "601099512345678", "goodsName": "Example product"},
  "history": [{"sold": 12, "sales": 3.5, "createTime": "2026-08-25T00:00:00Z"}],
  "regionId": 211,
  "title": "Temu 商品详情",
  "sourceType": "temu",
  "sourceTool": "geekbi_temu",
  "type": "productWorkbenches",
  "columns": []
}
```

## Site List: `POST /api/v1/tools/research/geekbi/temu/siteList`

### Request

No business parameters; send `{}` as the body. Use only nonempty positive-integer `sites[].regionId` for product search and detail; `sites[].siteId` is an upstream internal ID and must not replace `regionId`. If no valid `regionId` exists, stop chained calls and inform the user.

#### curl Examples

```bash
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/siteList" \
  -H "Authorization: Bearer $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/1.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{}'
```

### Response

| Field | Type | Description |
|---|---|---|
| `sites` | array | Supported Temu sites |
| `total` | integer | Site count |
| `title` / `sourceType` / `sourceTool` / `type` | string | `Temu 站点列表` (Temu site list) / `temu` / `geekbi_temu` / `tableListWorkbenches` |
| `columns` | array | Render column definitions |

`sites[]` fields: `siteId` (internal ID, not used for filtering), `regionId`, `name`, `cnName` (Chinese name; the sample value means United States), `lang`, `currency`, `extraFields`. Business fields may be null; filter out empty `regionId` values before chained calls.

#### Response Example

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "sites": [{"siteId": 1, "regionId": 211, "name": "United States", "cnName": "美国", "lang": "en", "currency": "USD"}],
  "total": 1,
  "title": "Temu 站点列表",
  "sourceType": "temu",
  "sourceTool": "geekbi_temu",
  "type": "tableListWorkbenches",
  "columns": []
}
```

## Category List: `POST /api/v1/tools/research/geekbi/temu/categoryList`

### Request

| Parameter | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `parentCatId` | integer | No | `>=0` | Omit to return first-level categories; pass a `categories[].catId` to query its immediate children |

Category search dependency: first use `{}` to obtain first-level nodes. When drilling down, use only a nonempty nonnegative-integer `catId` as the next request's `parentCatId`; when filtering products, put only valid `catId` values in the product search `catIds` array. If no valid `catId` exists, stop chained calls and inform the user. Passing `0` is valid, but the source code does not establish equivalence with omitting `parentCatId`.

#### curl Examples

```bash
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/categoryList" \
  -H "Authorization: Bearer $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/1.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"parentCatId":100}'
```

### Response

| Field | Type | Description |
|---|---|---|
| `categories` | array | Category nodes under the specified parent |
| `total` | integer | Number of returned nodes |
| `parentCatId` | integer / omitted | Parent ID for this query; observed first-level queries omit it, while queries specifying a parent return that ID |
| `title` / `sourceType` / `sourceTool` / `type` | string | `Temu 品类列表` (Temu category list) / `temu` / `geekbi_temu` / `tableListWorkbenches` |
| `columns` | array | Render column definitions |

`categories[]` fields: `catId`, `catName`, `catLevel`, `parentCatId`, `isLeaf`, `extraFields`. Business fields may be null; only nonempty valid `catId` values may be used for product search `catIds` or the next `parentCatId`.

#### Response Example

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "categories": [{"catId": 984, "catName": "Women Clothing", "catLevel": 2, "parentCatId": 100, "isLeaf": false}],
  "total": 1,
  "parentCatId": 100,
  "title": "Temu 品类列表",
  "sourceType": "temu",
  "sourceTool": "geekbi_temu",
  "type": "tableListWorkbenches",
  "columns": []
}
```

## `columns[]` Structure

Each column definition usually contains `field`, `title`, `cellType`, `sortable`, `filterable`; `cellType` is `number` or `text`.

## Error Codes

The entry script echoes gateway JSON errors unchanged and does not replace business errors with Python stack traces.

| HTTP / Business Code | Meaning | Action |
|---|---|---|
| 200 with no failing business code | Success | Parse the corresponding top-level structure; still check for empty results or error messages |
| HTTP 200 + `errcode=30001` | Upstream business rejection | Stop or correct parameters according to the error message; do not parse it as success |
| HTTP 200 + `errcode=30005` | Upstream authorization failed | Stop calling and contact the tool administrator; do not parse it as success |
| 400 | Parameter validation failed | Correct fields according to the message; do not automatically change keywords, pages, or sites and retry repeatedly |
| 401 | Authentication failed | Check `NEXSCOPE_API_KEY` and follow the authentication guidance in `SKILL.md` |
| 402 | Insufficient compute credits or balance | Stop calling and follow the authentication/compute-credit guidance |
| 403 | Access denied | Stop calling and contact the tool administrator; do not treat this as a top-up issue |
| 429 | Too many requests | Stop repeated calls and try again later |
| 502 / 503 / 504 | Gateway or upstream error | Do not automatically retry paid search/detail calls; explain that another charge may occur and obtain user confirmation before retrying once with the original parameters. Free site/category helper endpoints may be retried 1–2 times with the original parameters |

Product search also rejects `regionId<1`, `page<1`, `size` outside 1–200, `page*size>10000`, invalid `status/hostingMode/order`, and any minimum exceeding its maximum. Null values in `catIds` are filtered out; null values in `status` are rejected. Callers should send only valid integers. Product detail rejects empty `goodsId` or invalid `regionId`; reuse only nonempty `items[].goodsId` from search results.

The observed gateway response without `Authorization` is HTTP 401:

```json
{"errcode":401,"errmsg":"authorized error"}
```
