# Seerfar Ozon Market Keyword Search API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/seerfar/ozon/marketKeywordSearch`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from the environment variable `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)
- **User-Agent**: `NexScope-Skill/1.0`; HTTP timeout 60s

## Request Parameters

POST Body (JSON). The following fields are consistent with the interface `inputSchema`. Apart from `page` being required, all others are optional. All range filter items are `{min, max}` objects and can be passed with one or both bounds.

| Parameter | Type | Required | Description |
|------|------|------|------|
| page | object | Yes | Pagination & sorting: `{page, pageSize, orders[]}` |
| page.page | integer | No | Page number, starting from 1, default 1 |
| page.pageSize | integer | No | Items per page, default 20 |
| page.orders | array | No | Sort rules, elements `{field, direction}`; `direction` takes `DESC` (descending) / `ASC` (ascending) |
| keywords | array<string> | No | Keyword array (max 1000), used with `matchType` |
| matchType | integer | No | Keyword match mode: `0` exact, `1` fuzzy |
| searchDate | string | No | Query date `yyyy-MM-dd` (e.g., `2026-04-01`); defaults to last 30 days if omitted; passing `2026-04-01` queries March 2026 data |
| categories | array<string> | No | Category ID array (max 1000) |
| searchVolume | {min,max} | No | Search volume range |
| searchChange30 | {min,max} | No | 30-day search change range |
| monthlySales | {min,max} | No | Monthly sales range |
| monthlyRevenue | {min,max} | No | Monthly revenue range |
| price | {min,max} | No | Price range |
| productViews | {min,max} | No | Product views range |
| products | {min,max} | No | Product count range |
| volume | {min,max} | No | Volume range |
| marketSpace | {min,max} | No | Market space range |
| conversionSharing | {min,max} | No | Conversion concentration range |
| reviews | {min,max} | No | Review count range |
| ratings | {min,max} | No | Rating range |
| sellers | {min,max} | No | Seller count range |
| weight | {min,max} | No | Weight range |
| uId | string | No | User ID |
| memberId | string | No | Member ID (a unique member identifier; data is attributed to memberId) |

> **Required constraints**: `page` is the only required field; requests without `page` will be rejected.
> **Range filtering**: Both sub-fields of all `{min,max}` objects are optional; passing a single bound filters by lower/upper bound only.
> **Sorting**: Recommended to sort by core metrics via `page.orders` (e.g., `searchVolume` DESC, `sellers` ASC) to avoid paging through large unsorted result sets.

## Response Structure

| Field | Type | Description |
|------|------|------|
| code | string | Return code, `"200"` indicates success (returned on success) |
| errcode | integer | Error code, `200` indicates success; only returned on business errors (coexists with `code` on success) |
| msg | string | Message; `ok` for success |
| errmsg | string | Error message; `ok` for success, reason description on business error |
| total | integer | Total record count |
| data | array | Market hot keyword data (see details below) |
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
| marketSpace | integer | Market space |
| returnCancellationRate | number | Return/cancellation rate (%) |
| uniqQueriesWCa | integer | Add-to-cart count |
| ca | number | Add-to-cart conversion rate (%) |
| categories | array | Category ID array |
| categoryInfos | array | Category information (see below) |
| products | array | Top product data (see below) |
| id | string | Record ID |

> `relevancy` (relevance), `titleDensity` (title density), `wordCount` (word count), and `dimension` (dimension information) are defined in outputSchema but typically not returned or `null` in actual responses; null-check before use.

#### products[*] Top Product Object Fields

| Field | Type | Description |
|------|------|------|
| ozonId | integer | Ozon product ID |
| sku | integer | SKU ID |
| title | string | Product title (Russian) |
| imageUrl | string | Main image URL |
| advert | integer | Ad indicator (0/1) |

#### categoryInfos[*] Category Information Object Fields

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
| 400 | Parameter error | Check `errmsg`; common causes include missing `page`, `searchDate` format error, invalid category ID, etc. |
| 401 | Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 402 | Billing failed | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Other non-200 values | Business exception | Check `errmsg` for specific reason |

Error response example:

```json
{
    "errcode": 400,
    "errmsg": "page 为必填参数"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/seerfar/ozon/marketKeywordSearch \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/1.0" \
  -d '{
    "page": {"page": 1, "pageSize": 5, "orders": [{"field": "searchVolume", "direction": "DESC"}]}
  }'
```

## Response Example (abbreviated)

```json
{
  "code": "200",
  "msg": "ok",
  "errcode": 200,
  "errmsg": "ok",
  "total": 506910,
  "costTime": 4706,
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
      "ca": 13.1,
      "uniqQueriesWCa": 153707,
      "categories": ["15621031_200000933_93182"],
      "categoryInfos": [
        {
          "titleCn": "连衣裙",
          "titleEn": "Dress",
          "titleRu": "Платье",
          "cnTitlePath": "服装 > 服装 > 连衣裙",
          "enTitlePath": "Clothing > Clothing > Dress",
          "titlePath": "Одежда > Одежда > Платье",
          "id": "15621031_200000933_93182",
          "crossBorderSellable": true
        }
      ],
      "products": [
        {
          "ozonId": 4380710124,
          "sku": 4380710124,
          "title": "Платье T-SOD",
          "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-7/wc300/10636393147.jpg",
          "advert": 0
        }
      ],
      "dimension": null
    }
  ]
}
```

---
