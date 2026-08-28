# Seerfar Ozon Keyword Back-Search API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/seerfar/ozon/keywordBackSearch`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from the environment variable `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)
- **User-Agent**: `NexScope-Skill/1.0`; HTTP timeout 60s

## Request Parameters

POST Body (JSON). The following fields are consistent with the interface `inputSchema`. `skuIds`, `hasVariant`, and `page` are required; all others are optional. All range filter items are `{min, max}` objects and can be passed with one or both bounds.

| Parameter | Type | Required | Description |
|------|------|------|------|
| skuIds | array<integer> | Yes | List of SKUs to back-search, max 20 |
| hasVariant | integer | Yes | Whether to exclude variants: `0` do not exclude variants, `1` exclude variants |
| page | object | Yes | Pagination & sorting: `{page, pageSize, orders[]}` |
| page.page | integer | No | Page number, starting from 1, default 1 |
| page.pageSize | integer | No | Items per page, default 20 |
| page.orders | array | No | Sort rules, elements `{field, direction}`; `direction` takes `DESC` (descending) / `ASC` (ascending) |
| matchType | integer | No | Keyword match mode: `0` exact, `1` fuzzy |
| type | array<string> | No | Search term type filter, fixed options: `0` organic search terms, `1` ad search terms; no filtering if omitted |
| historyDate | string | No | Historical month `yyyy-MM` (e.g., `2026-02`); can be left blank per docs to query current period |
| includeKeywords | array<string> | No | Include keyword array (max 1000), only returns search terms containing the specified words |
| excludeKeywords | array<string> | No | Exclude keyword array (max 1000), removes irrelevant terms |
| searchVolume | {min,max} | No | Monthly search volume range |
| searchChange30 | {min,max} | No | 30-day search change range |
| wordCount | {min,max} | No | Keyword word count range |
| productViews | {min,max} | No | Product views range |
| products | {min,max} | No | Product count range |
| sellers | {min,max} | No | Seller count range |
| marketSpace | {min,max} | No | Market space range |
| conversionSharing | {min,max} | No | Conversion concentration range |
| uniqQueriesWCa | {min,max} | No | Add-to-cart count range |
| ca | {min,max} | No | Add-to-cart conversion rate range |
| conversion | {min,max} | No | Conversion rate range |
| titleDensity | {min,max} | No | Title density range |
| adRivalCount | {min,max} | No | Ad competitor count range |
| adRank | {min,max} | No | Ad ranking range |
| naturalRank | {min,max} | No | Organic ranking range |
| exposure | {min,max} | No | Exposure range |
| uId | string | No | User ID |
| memberId | string | No | Member ID (a unique member identifier; data is attributed to memberId) |

> **Required constraints**: `skuIds`, `hasVariant`, and `page` are all required; missing any will cause the request to be rejected. `skuIds` max 20; exceeding will be rejected or truncated.
> **Range filtering**: Both sub-fields of all `{min,max}` objects are optional; passing a single bound filters by lower/upper bound only.
> **Organic / Ad terms**: `type` is used to view only organic search terms (`["0"]`) or ad search terms (`["1"]`); both types are returned if omitted.
> **Difference from market keyword search / keyword mining**: This endpoint is a "keyword back-search by SKU" — `skuIds` must be passed; the results show the search terms these products appear under and their market profile. It does not support month selection via `searchDate` (only `historyDate` historical month), does not support `categories` category filtering, and does not accept `keyword` seed terms or mining/market-only filters like `price`.
> **Sorting**: Recommended to sort by core metrics via `page.orders` (e.g., `searchVolume` DESC, `sellers` ASC) to avoid paging through large unsorted result sets.

## Response Structure

| Field | Type | Description |
|------|------|------|
| code | string | Return code, `"200"` indicates success (returned on success) |
| errcode | integer | Error code, `200` indicates success; only returned on business errors (coexists with `code` on success) |
| msg | string | Message; `ok` for success |
| errmsg | string | Error message; `ok` for success, reason description on business error |
| total | integer | Total record count |
| data | array | Keyword back-search data (see details below) |
| columns | array | Column definitions, elements contain `{field, title, cellType, sortable, filterable}` |
| costTime | integer | API latency (milliseconds) |
| costToken | integer | Tokens consumed |
| type | string | Response display type, e.g., `tableListWorkbenches` |

### data[*] Keyword Back-Search Object Fields

| Field | Type | Description |
|------|------|------|
| query | string | Keyword (original Russian) |
| queryCn | string | Keyword Chinese translation |
| platform | integer | Platform: `0` Ozon, `1` Wildberries |
| searchVolume | integer | Monthly search volume |
| count30GrowthRate | number | Monthly search growth (%, can be negative) |
| productCount | integer | Product count (may be missing in some rows) |
| competingProducts | integer | Competing product count |
| sellers | integer | Seller count |
| avgPrice | number | Average price |
| itemsViews | number | Product visibility |
| viewSharing | number | View concentration (%) |
| conversionSharing | number | Conversion concentration (%) |
| marketSpace | number | Market space |
| returnCancellationRate | number | Return/cancellation rate (%) |
| uniqQueriesWCa | integer | Add-to-cart count |
| ca | number | Add-to-cart conversion rate (%) |
| titleDensity | number | Title density |
| wordCount | integer | Word count |
| categories | array | Category ID array |
| dimension | object | Dimension object, carrying back-search-specific metrics (see below) |
| products | array | Top product data (see below) |
| id | string | Record ID |

> **Field population (based on actual responses)**: `dimension` (dimension object) **is returned for every row**, carrying back-search-specific metrics (`type` / `naturalRank` / `exposure` / `conversion` / `x`, see below). `titleDensity` (title density) and `wordCount` (word count) are returned for every row. `productCount` (product count) is returned for most rows, but individual rows may be `null`. `relevancy` (relevance) is defined in outputSchema / `columns` but **not returned** in actual `data[*]`; `categoryInfos` (category information) is similarly **not returned** (also not returned in sibling `keywordMining`, but `marketKeywordSearch` does return it — do not assume consistency).

#### dimension Dimension Object Fields

`dimension` is returned for every `data[*]` row and carries the search term's specific metrics relative to the back-searched SKU; the input-side `type` / `naturalRank` / `adRank` / `exposure` / `conversion` filters operate on these values.

| Field | Type | Description |
|------|------|------|
| type | integer | Search term channel: `0` organic search term, `1` ad search term |
| naturalRank | integer | Organic ranking (the back-searched SKU's organic position under this term) |
| exposure | number | Exposure (0–1) |
| conversion | number | Conversion rate (0–1) |
| x | array | Position/pagination indicator, semantics opaque |

> Ad term (`type:1`) rows may additionally carry `adRank`; the test SKU had only organic terms (`type:0`, querying with `type:["1"]` returned `total:0`), so `adRank` was not observed; null-check before use.

#### products[*] Top Product Object Fields

| Field | Type | Description |
|------|------|------|
| ozonId | integer | Ozon product ID |
| sku | integer | SKU ID |
| title | string | Product title (Russian) |
| imageUrl | string | Main image URL |
| advert | integer | Ad indicator (0/1) |

#### categoryInfos[*] Category Information Object Fields

> Warning: `categoryInfos` is **not returned** in actual `data[*]` rows (only appears in `columns` column definitions); the fields below are from outputSchema definition, provided for reference if they appear.

| Field | Type | Description |
|------|------|------|
| titleCn | string | Category Chinese name |
| titleEn | string | Category English name |
| titleRu | string | Category Russian name |
| cnTitlePath | string | Chinese category path |
| enTitlePath | string | English category path |
| titlePath | string | Russian category path |
| id | string | Category ID |
| crossBorderSellable | boolean | Whether cross-border sales are allowed |

## Error Codes

Under normal circumstances the HTTP status code is 200, business results are distinguished via the response body:
- **Success**: Returns `code:"200"` + `errcode:200` (`msg` / `errmsg` both `ok`).
- **Business error**: HTTP still 200, but only returns `errcode` (non-200) + `errmsg` (reason), no `code` field.
- **Authentication failure**: HTTP status code 401, response body `{"errcode":401,"errmsg":"authorized error"}`.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse `data` field normally |
| 400 | Parameter error | Check `errmsg`; common causes include missing `skuIds` / `hasVariant` / `page` etc. |
| 1002 | Parameter validation failed | Check `errmsg`; common causes include passing empty array for `skuIds` etc. |
| 401 | Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 402 | Billing failed | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Other non-200 values | Business exception | Check `errmsg` for specific reason |

Error response example (missing `skuIds`):

```json
{
    "errcode": 400,
    "errmsg": "skuIds 为必填参数"
}
```

When `skuIds` is an empty array:

```json
{
    "errcode": 1002,
    "errmsg": "参数校验失败，请检查输入。参数 skuIds 不能为空，请至少传入一个值。"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/seerfar/ozon/keywordBackSearch \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/1.0" \
  -d '{
    "skuIds": [4380710124],
    "hasVariant": 0,
    "page": {"page": 1, "pageSize": 5, "orders": [{"field": "searchVolume", "direction": "DESC"}]}
  }'
```

## Response Example (abbreviated)

Actual response for `skuIds:[4380710124]`, `hasVariant:0`, sorted by `searchVolume` DESC (2 rows shown, `products` each kept 2 entries):

```json
{
  "code": "200",
  "msg": "ok",
  "errcode": 200,
  "errmsg": "ok",
  "total": 388,
  "costTime": 1376,
  "costToken": 16000,
  "type": "tableListWorkbenches",
  "data": [
    {
      "id": "6a4559b8d1fd12d9b57aacea",
      "query": "платье женское летнее",
      "queryCn": "夏季女装",
      "platform": 0,
      "searchVolume": 1167418,
      "count30GrowthRate": -4.7,
      "productCount": 519605,
      "competingProducts": 6221,
      "sellers": 974,
      "avgPrice": 2635.0,
      "itemsViews": 131.3,
      "viewSharing": 16.9,
      "conversionSharing": 17.9,
      "marketSpace": 188,
      "returnCancellationRate": 51.7,
      "uniqQueriesWCa": 153707,
      "ca": 13.1,
      "titleDensity": 0.0,
      "wordCount": 3,
      "categories": ["15621031_200000933_93182"],
      "dimension": {"exposure": 0.3495, "x": [1], "naturalRank": 1, "type": 0, "conversion": 0.353},
      "products": [
        {"ozonId": 4380710124, "sku": 4380710124, "title": "Платье T-SOD", "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-7/wc300/10636393147.jpg", "advert": 0},
        {"ozonId": 3042328733, "sku": 3042328733, "title": "Платье BELLA ROSA", "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-3/wc300/9689632131.jpg", "advert": 0}
      ]
    },
    {
      "id": "6a4559d2d1fd12d9b57e7d19",
      "query": "платье",
      "queryCn": "裙子",
      "platform": 0,
      "searchVolume": 392783,
      "count30GrowthRate": -4.2,
      "productCount": null,
      "competingProducts": 5763,
      "sellers": 974,
      "avgPrice": 5791.0,
      "itemsViews": 99.8,
      "viewSharing": 16.2,
      "conversionSharing": 18.3,
      "marketSpace": 68,
      "returnCancellationRate": 55.4,
      "uniqQueriesWCa": 43543,
      "ca": 11.1,
      "titleDensity": 1.0,
      "wordCount": 1,
      "categories": ["15621031_200000933_93182"],
      "dimension": {"exposure": 0.1176, "x": [1], "naturalRank": 1, "type": 0, "conversion": 0.1004},
      "products": [
        {"ozonId": 4380710124, "sku": 4380710124, "title": "Платье T-SOD", "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-7/wc300/10636393147.jpg", "advert": 0},
        {"ozonId": 3563361777, "sku": 3563361777, "title": "Платье SIMBAL Коллекция лето 2026", "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-0/wc300/9173740572.jpg", "advert": 0}
      ]
    }
  ]
}
```

> Both rows are organic terms (`dimension.type:0`); row 2 has `productCount` as `null` (missing in some rows). `relevancy` / `categoryInfos` are not returned in actual `data[*]`.

---
