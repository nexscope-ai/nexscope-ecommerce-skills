# Seerfar Ozon Keyword Mining API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/seerfar/ozon/keywordMining`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from the environment variable `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)
- **User-Agent**: `NexScope-Skill/1.0`; HTTP timeout 60s

## Request Parameters

POST Body (JSON). The following fields are consistent with the interface `inputSchema`. `keyword` and `page` are required; all others are optional. All range filter items are `{min, max}` objects and can be passed with one or both bounds.

| Parameter | Type | Required | Description |
|------|------|------|------|
| keyword | string | Yes | Seed keyword, mining expands around this term (maxLength 1000) |
| page | object | Yes | Pagination & sorting: `{page, pageSize, orders[]}` |
| page.page | integer | No | Page number, starting from 1, default 1 |
| page.pageSize | integer | No | Items per page, default 20 |
| page.orders | array | No | Sort rules, elements `{field, direction}`; `direction` takes `DESC` (descending) / `ASC` (ascending) |
| matchType | integer | No | Keyword match mode: `0` exact, `1` fuzzy |
| includeKeywords | array<string> | No | Include keyword array (max 1000), used to further narrow down / specify required words on top of the seed term |
| excludeKeywords | array<string> | No | Exclude keyword array (max 1000), used to remove irrelevant terms |
| wordCount | {min,max} | No | Keyword word count range |
| searchVolume | {min,max} | No | Search volume range |
| searchChange30 | {min,max} | No | 30-day search change range |
| productViews | {min,max} | No | Product views range |
| products | {min,max} | No | Product count range |
| sellers | {min,max} | No | Seller count range |
| price | {min,max} | No | Price range |
| marketSpace | {min,max} | No | Market space range |
| conversionSharing | {min,max} | No | Conversion concentration range |
| relevancy | {min,max} | No | Relevance range (degree of relevance to the seed keyword) |
| uniqQueriesWCa | {min,max} | No | Add-to-cart count range |
| ca | {min,max} | No | Add-to-cart conversion rate range |
| titleDensity | {min,max} | No | Title density range |
| adRivalCount | {min,max} | No | Ad competitor count range |
| uId | string | No | User ID |
| memberId | string | No | Member ID (a unique member identifier; data is attributed to memberId) |

> **Required constraints**: `keyword` and `page` are both required; missing either will cause the request to be rejected.
> **Range filtering**: Both sub-fields of all `{min,max}` objects are optional; passing a single bound filters by lower/upper bound only.
> **Difference from market keyword search**: This endpoint performs "mining around a seed keyword" — `keyword` must be passed; the results are keywords related to the seed term and their market profile. It does not support month selection via `searchDate`, does not support `categories` category filtering, and does not have `monthlySales` / `monthlyRevenue` / `volume` / `reviews` / `ratings` / `weight` filters. For browsing all market hot keywords, use `marketKeywordSearch` instead.
> **Sorting**: Recommended to sort by core metrics via `page.orders` (e.g., `searchVolume` DESC, `sellers` ASC, `relevancy` DESC) to avoid paging through large unsorted result sets.

## Response Structure

| Field | Type | Description |
|------|------|------|
| code | string | Return code, `"200"` indicates success (returned on success) |
| errcode | integer | Error code, `200` indicates success; only returned on business errors (coexists with `code` on success) |
| msg | string | Message; `ok` for success |
| errmsg | string | Error message; `ok` for success, reason description on business error |
| total | integer | Total record count |
| data | array | Keyword mining data (see details below) |
| columns | array | Column definitions, elements contain `{field, title, cellType, sortable, filterable}` |
| costTime | integer | API latency (milliseconds) |
| costToken | integer | Tokens consumed |
| type | string | Response display type, e.g., `tableListWorkbenches` |

### data[*] Keyword Market Object Fields

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
| relevancy | number | Relevance (degree of relevance to the seed keyword) |
| titleDensity | number | Title density |
| wordCount | integer | Word count |
| categories | array | Category ID array |
| categoryInfos | array | Category information (see below) |
| products | array | Top product data (see below) |
| id | string | Record ID |

> **Field population (based on actual responses)**: `relevancy` (relevance), `titleDensity` (title density), and `wordCount` (word count) **are all returned** in actual responses — relevance is the core output of seed keyword mining, with the seed keyword itself having relevance of `100` and related terms decreasing in relevance. `productCount` (product count) is returned for most rows, but rows identical to the seed keyword may lack it. `dimension` (dimension information) and `categoryInfos` (category information) are defined in outputSchema / `columns` but **not returned** in `data[*]` rows; null-check before use.

#### products[*] Top Product Object Fields

| Field | Type | Description |
|------|------|------|
| ozonId | integer | Ozon product ID |
| sku | integer | SKU ID |
| title | string | Product title (Russian) |
| imageUrl | string | Main image URL |
| advert | integer | Ad indicator (0/1) |

#### categoryInfos[*] Category Information Object Fields

> Warning: `categoryInfos` was **not returned** in actual `data[*]` rows (only appears in `columns` column definitions); the fields below are from outputSchema definition, provided for reference if they appear.

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
| 400 | Parameter error | Check `errmsg`; common causes include missing `keyword` / `page`, empty keyword, etc. |
| 401 | Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 402 | Billing failed | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Other non-200 values | Business exception | Check `errmsg` for specific reason |

Error response example (missing `keyword`):

```json
{
    "errcode": 400,
    "errmsg": "keyword 为必填参数",
    "keyword": ""
}
```

When `page` is missing:

```json
{
    "errcode": 400,
    "errmsg": "page 为必填参数"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/seerfar/ozon/keywordMining \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/1.0" \
  -d '{
    "keyword": "платье",
    "page": {"page": 1, "pageSize": 5, "orders": [{"field": "searchVolume", "direction": "DESC"}]}
  }'
```

## Response Example (abbreviated)

Actual response for `keyword:"платье"`, sorted by `searchVolume` DESC (2 rows shown, `products` each kept 1 entry):

```json
{
  "code": "200",
  "msg": "ok",
  "errcode": 200,
  "errmsg": "ok",
  "total": 1000,
  "costTime": 4255,
  "costToken": 16000,
  "type": "tableListWorkbenches",
  "data": [
    {
      "id": "6a4559d2d1fd12d9b57e7d19",
      "query": "платье",
      "queryCn": "裙子",
      "platform": 0,
      "searchVolume": 392783,
      "count30GrowthRate": -4.2,
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
      "relevancy": 100,
      "titleDensity": 1.0,
      "wordCount": 1,
      "categories": ["15621031_200000933_93182"],
      "products": [
        {"ozonId": 4380710124, "sku": 4380710124, "title": "Платье T-SOD", "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-7/wc300/10636393147.jpg", "advert": 0}
      ]
    },
    {
      "id": "6a4559bcd1fd12d9b57b6866",
      "query": "платье женское",
      "queryCn": "女装",
      "platform": 0,
      "searchVolume": 349725,
      "count30GrowthRate": -29.4,
      "productCount": 711194,
      "competingProducts": 5974,
      "sellers": 1063,
      "avgPrice": 5261.0,
      "itemsViews": 137.3,
      "viewSharing": 15.0,
      "conversionSharing": 18.8,
      "marketSpace": 59,
      "returnCancellationRate": 49.4,
      "uniqQueriesWCa": 41624,
      "ca": 11.9,
      "relevancy": 12,
      "titleDensity": 0.1,
      "wordCount": 2,
      "categories": ["15621031_200000933_93182", "15621031_200000933_93184"],
      "products": [
        {"ozonId": 4380710124, "sku": 4380710124, "title": "Платье T-SOD", "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-7/wc300/10636393147.jpg", "advert": 0}
      ]
    }
  ]
}
```

> Row 1 is the seed keyword itself (`relevancy: 100`, no `productCount`); Row 2 is a related term (`relevancy: 12`, includes `productCount`). `dimension` / `categoryInfos` are not returned in actual `data[*]`.

---
