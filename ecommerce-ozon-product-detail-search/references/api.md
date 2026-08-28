# Seerfar Ozon Product Detail Search API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/seerfar/ozon/productDetailSearch`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from the environment variable `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)
- **User-Agent**: `NexScope-Skill/1.0`; HTTP timeout 60s

## Request Parameters

POST Body (JSON). The following fields are consistent with the interface `inputSchema`. Only `sku` is required; all others are optional.

| Parameter | Type | Required | Description |
|------|------|------|------|
| sku | string | Yes | Product SKU (Ozon SKU, e.g., `175924376`). This is the `sku` returned by other Seerfar Ozon tools |
| dateRange | string | No | Sales/metrics statistics window, default `past_30_days`. Options: `past_7_days` / `past_30_days` / `past_60_days` / `past_90_days` / `past_180_days` / `past_365_days` |
| uId | string | No | User ID (max 1000) |
| memberId | string | No | Member ID (a unique member identifier; a user can belong to multiple teams; data is attributed to memberId, max 1000) |

> **Required constraints**: `sku` is required; missing it returns `errcode 400` (`sku 为必填参数`).
> **Single SKU query**: This endpoint queries one product detail at a time; no batch/list mode.
> **Window only affects sales aggregation**: `dateRange` only affects sales-related fields such as `totalSales` / `dailySales` / `totalRevenue` / `salesTrendVOList` / `startDate` / `endDate`; product metadata (title, price, rating, brand, seller, fulfillment method, etc.) is a current snapshot and not affected by the window.

## Response Structure

| Field | Type | Description |
|------|------|------|
| code | string | Return code, `"200"` indicates success (returned on success) |
| errcode | integer | Error code, `200` indicates success; only returned on business errors |
| msg | string | Message; `ok` for success |
| errmsg | string | Error message; `ok` for success, reason description on business error |
| total | integer | Number of records returned (`1` on hit, `0` on miss) |
| totalSales | integer | Total sales volume within the statistics window |
| dailySales | number | Average daily sales (approx totalSales / window days) |
| totalRevenue | number | Sales revenue within the statistics window (RUB) |
| stock | integer | Stock |
| startDate | string | Statistics window start date (e.g., `2026-06-01`) |
| endDate | string | Statistics window end date (e.g., `2026-06-30`) |
| salesTrendVOList | array | Daily sales data series (see below) |
| categoryRanks | array | Product category ranking history (see below) |
| products | array | Product detail list (1 record on single SKU hit, empty on miss) |
| data | array | Returned data, content identical to `products` |
| columns | array | Column definitions, elements contain `{field, title, cellType, sortable, filterable}` |
| type | string | Response display type, e.g., `productWorkbenches` |
| costTime | integer | API latency (milliseconds) |
| costToken | integer | Tokens consumed |

> Missed SKU: Returns success (`code:"200"`, `errcode:200`), but `total:0`, `products:[]`, and sales aggregation fields (`totalSales` / `dailySales` / `totalRevenue` / `stock` / `startDate` / `endDate`) are not returned. Determining "product has no data" should be based on `total=0` or `products` empty, not `errcode`.

### products[*] / data[*] Product Object Fields

| Field | Type | Description |
|------|------|------|
| sku | integer | Product SKU |
| productId | integer | Unified product ID, mapped from `sku` |
| title | string | Product title |
| price | number | Product price (RUB) |
| currency | string | Currency, always `₽` |
| reviewRating | number | Product rating |
| rating | number | Unified rating, mapped from `reviewRating` |
| reviewCount | integer | Number of reviews |
| questionsAndAnswers | integer | QA count |
| brandName | string | Brand name |
| brand | string | Unified brand, mapped from `brandName` |
| brandId | integer | Brand ID |
| brandUrl | string | Brand link |
| sellerName | string | Seller name |
| sellerId | integer | Seller ID (negative values indicate Ozon platform self-operated sellers, e.g., `-4` Ozon Россия) |
| fulfillment | array | Product fulfillment methods, e.g., `["FBO"]`, `["OZON"]`, may contain multiple values |
| upTime | integer | Listing time, millisecond timestamp |
| upDays | integer | Days since listing |
| upMonths | integer | Months since listing |
| imageUrl | string | Unified main image URL, mapped from the first of `imageUrls` |
| imageUrls | array | List of product image URLs |
| productUrl | string | Product URL |
| productPageUrl | string | Unified product page URL, mapped from `productUrl` |
| categoryInfo | object | Product category information (see below) |
| monthlySalesUnits | integer | Unified monthly sales, actual value equals `totalSales` of the current statistics window |
| monthlySalesRevenue | number | Unified monthly revenue, actual value equals `totalRevenue` of the current statistics window |
| sourceType | string | Data source, always `ozon` |
| sourceTool | string | Source tool, identifies the Seerfar Ozon interface (e.g., `Seerfar-Ozon-查竞品`) |
| weight | number | Product weight, in grams (digital/service products may not return this, see field differences) |
| grossMargin | number | Gross margin (defined in schema, some products may not return this in practice, see field differences) |

> **`data` and `products`**: Both have identical content; each contains 1 record on a single SKU hit.

### salesTrendVOList[*] Daily Sales Object

| Field | Type | Description |
|------|------|------|
| date | string | Date (e.g., `2026-06-01`) |
| sales | integer | Daily sales (may be `0`) |
| revenue | number | Daily revenue (RUB) |
| price | number | Daily price (RUB) |
| stock | integer | Daily stock |
| reviewCount | integer | Cumulative review count as of this date |
| reviewRating | number | Rating as of this date |

### categoryRanks[*] Category Ranking Object

| Field | Type | Description |
|------|------|------|
| date | string | Month (e.g., `2026-02`; current month shows as specific date `2026-07-01`) |
| rank | integer | Category ranking |
| count | integer | Statistics count (subject to actual gateway interpretation) |

> `categoryRanks` only contains `date` / `rank` / `count`, without category name; category name/path should be taken from `categoryInfo`.

### categoryInfo Category Information Object

| Field | Type | Description |
|------|------|------|
| cnTitlePath | string | Chinese category path |
| enTitlePath | string | English category path |
| titlePath | string | Category path (original text) |
| category | object | Terminal category object (fields see below) |
| fullCategoryId | array | Full category ID path (string array, root to terminal, e.g., `["99999999", "99999999_200001489", "99999999_200001489_970727001"]`) |

#### category Object Fields

| Field | Type | Description |
|------|------|------|
| cnTitle | string | Category Chinese name |
| enTitle | string | Category English name |
| title | string | Category original title |
| level | integer | Category level |
| id | string | Category ID |
| pid | string | Parent category ID |
| crossBorderSellable | boolean | Whether cross-border sales are supported |
| disabled | boolean | Whether disabled |

## Error Codes

Under normal circumstances the HTTP status code is 200, business results are distinguished via the response body:
- **Success**: Returns `code:"200"` + `errcode:200` (`msg` / `errmsg` both `ok`).
- **Business error**: HTTP still 200, but only returns `errcode` (non-200) + `errmsg` (reason), no `code` field.
- **Authentication failure**: HTTP status code 401, response body `{"errcode":401,"errmsg":"authorized error"}`.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse `products` / `data` and sales aggregation fields normally |
| 400 | Parameter error | Check `errmsg`; common causes include missing `sku` (`sku 为必填参数`) |
| 1003 | Too many requests | Rate limited, retry later |
| 401 | Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 402 | Billing failed | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Other non-200 values | Business exception | Check `errmsg` for specific reason |

Error response example:

```json
{
    "errcode": 400,
    "errmsg": "sku 为必填参数"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/seerfar/ozon/productDetailSearch \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/1.0" \
  -d '{"sku": "175924376", "dateRange": "past_30_days"}'
```

## Response Example (real response with sanitized abbreviation)

```json
{
  "code": "200",
  "msg": "ok",
  "errcode": 200,
  "errmsg": "ok",
  "total": 1,
  "totalSales": 58357,
  "dailySales": 1945,
  "totalRevenue": 232823930.0,
  "stock": 9999,
  "startDate": "2026-06-01",
  "endDate": "2026-06-30",
  "type": "productWorkbenches",
  "costTime": 1492,
  "costToken": 16000,
  "salesTrendVOList": [
    {"date": "2026-06-01", "sales": 3233, "revenue": 11283170.0, "price": 3490.0, "stock": 9999, "reviewCount": 73482, "reviewRating": 5.0},
    {"date": "2026-06-30", "sales": 0, "revenue": 0.0, "price": 4490.0, "stock": 9999, "reviewCount": 89148, "reviewRating": 4.9}
  ],
  "categoryRanks": [
    {"date": "2026-05", "count": 46, "rank": 1},
    {"date": "2026-06", "count": 49, "rank": 1}
  ],
  "products": [
    {
      "sku": 175924376,
      "productId": 175924376,
      "title": "Яндекс Плюс на 12 месяцев",
      "price": 4490.0,
      "currency": "₽",
      "reviewRating": 4.9,
      "rating": 4.9,
      "reviewCount": 89148,
      "questionsAndAnswers": 4141,
      "brandName": "Яндекс",
      "brand": "Яндекс",
      "brandId": 13013270,
      "brandUrl": "https://www.ozon.ru/brand/13013270/",
      "sellerName": "Ozon Россия",
      "sellerId": -4,
      "fulfillment": ["OZON"],
      "upTime": 1591647267000,
      "upDays": 2214,
      "upMonths": 73,
      "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-g/wc500/11171014792.jpg",
      "imageUrls": ["https://ir.ozone.ru/s3/multimedia-1-g/wc500/11171014792.jpg"],
      "productUrl": "https://www.ozon.ru/product/175924376",
      "productPageUrl": "https://www.ozon.ru/product/175924376",
      "categoryInfo": {"cnTitlePath": "电影、音乐、视频游戏、软件 > 数码商品 > 订阅音乐", "enTitlePath": "Movies, Music, Video Games, Software > Digital Products > Music Subscription", "titlePath": "Кино, музыка, видеоигры, софт > Цифровые товары > Подписка на музыку", "category": {"cnTitle": "订阅音乐", "enTitle": "Music Subscription", "title": "Подписка на музыку", "level": 3, "id": "99999999_200001489_970727001", "pid": "99999999_200001489", "crossBorderSellable": false, "disabled": true}, "fullCategoryId": ["99999999", "99999999_200001489", "99999999_200001489_970727001"]},
      "monthlySalesUnits": 58357,
      "monthlySalesRevenue": 232823930.0,
      "sourceType": "ozon",
      "sourceTool": "Seerfar-Ozon-查竞品"
    }
  ],
  "data": [ "..." ]
}
```

> `data` content is identical to `products`; `salesTrendVOList` / `categoryRanks` / `imageUrls` / `categoryInfo` are truncated in the example, real responses are more complete.

## Field Differences (Observed)

- **`monthlySalesUnits` / `monthlySalesRevenue`**: The outputSchema notes "no corresponding upstream field, kept as null", but **observed to be returned**, with values respectively equal to `totalSales` / `totalRevenue` of the current statistics window; can be used directly.
- **`weight`**: Returned for physical products (in grams); **not observed** for digital/service products (e.g., subscription memberships); null-check before use.
- **`grossMargin`**: Defined in schema as gross margin; **not observed** for some products (e.g., Ozon platform self-operated sellers); null-check before use.
- **`fulfillment` values**: In addition to `FBO` / `FBS`, platform self-operated products may show `["OZON"]`.

---
