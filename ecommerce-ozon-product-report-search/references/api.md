# Seerfar Ozon Product Report Search API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/seerfar/ozon/productReportSearch`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from the environment variable `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)
- **User-Agent**: `NexScope-Skill/1.0`; HTTP timeout 60s

## Request Parameters

POST Body (JSON). The following fields are consistent with the interface `inputSchema`. Apart from `page` being required, all others are optional. All range filter items are `{min, max}` objects and can be passed with one or both bounds.

### Pagination & Sorting

| Parameter | Type | Required | Description |
|------|------|------|------|
| page | object | Yes | Pagination & sorting: `{page, pageSize, orders[]}` |
| page.page | integer | No | Page number, starting from 1, default 1 |
| page.pageSize | integer | No | Items per page, default 20 |
| page.orders | array | No | Sort rules, elements `{field, direction}`; `direction` takes `DESC` (descending) / `ASC` (ascending). `field` is a metric field in the response (e.g., `sales`, `revenue`, `price`, `reviewRating`, `reviewCount`, `salesRate`) |

### Filter Conditions

| Parameter | Type | Required | Description |
|------|------|------|------|
| skus | array<integer> | No | SKU array (max 10), for precise lookup of specified products |
| keywords | array<string> | No | Keyword array, filters by product title |
| categoryIds | array<string> | No | Category ID array (Seerfar category IDs, not category names) |
| sellerName | array<string> | No | Seller name array |
| brand | object | No | Brand filter: `{brandName: array<string>, type: integer}`; `type` takes `0` include brand, `1` exclude brand, `2` unbranded |
| fulfillment | array<string> | No | Fulfillment method array, fixed options: `OZON`, `FBO`, `FBS`, `RFBS`, `FBP` |
| labels | array<integer> | No | Label array, fixed options: `0` new product, `1` genuine product, `2` best seller |
| creationDate | integer | No | Listing time filter (months), fixed options: `1` last 30 days, `3` last 90 days, `6` last 180 days, `12` last year, `24` last two years; no filtering if omitted |
| variationsMerge | integer | No | Whether to merge variants: `0` do not merge, `1` merge |
| searchDate | string | No | Query date `yyyy-MM-dd` (e.g., `2026-04-01`); defaults to last 30 days if omitted; passing `2026-04-01` queries March 2026 data |
| tag | string | No | Tag word |
| uId | string | No | User ID |
| memberId | string | No | Member ID (a unique member identifier; data is attributed to memberId) |

### Range Filters (all `{min, max}` objects)

| Parameter | Filter Target | Unit / Description |
|------|----------|-----------|
| monthlySales | Monthly sales `sales` | Units |
| monthlySalesRate | Sales growth rate `salesRate` | % |
| monthlyRevenue | Monthly revenue `revenue` | RUB |
| price | Price `price` | RUB |
| convToCartPdp | Cart conversion rate `convToCartPdp` | % |
| reviewRating | Rating `reviewRating` | 0~5 |
| reviewCount | Review count `reviewCount` | Count |
| questionsAndAnswers | QA count `questionsAndAnswers` | Count |
| variants | Variant count `variants` | Count |
| drr | Ad cost share `drr` | Ratio |
| grossMargin | Gross margin `grossMargin` | % |
| returnCancellationRate | Return/cancellation rate `returnCancellationRate` | % |
| weight | Weight `weight` | g |
| volume | Volume `volume` | L |

> **Required constraints**: `page` is the only required field; requests without `page` will be rejected.
> **Range filtering**: Both sub-fields of all `{min, max}` objects are optional; passing a single bound filters by lower/upper bound only.
> **Sorting**: Data volume can reach tens of millions; must sort by core metrics via `page.orders` before pagination, avoid paging through large unsorted result sets.

## Response Structure

| Field | Type | Description |
|------|------|------|
| code | string | Return code, `"200"` indicates success (returned on success) |
| errcode | integer | Error code, `200` indicates success; only returned on business errors (coexists with `code` on success) |
| msg | string | Message; `ok` for success |
| errmsg | string | Error message; `ok` for success, reason description on business error |
| total | integer | Total matched record count (can reach tens of millions with no filters; equals hit count when using `skus` precise lookup) |
| data | array | Product report data (see details below), content identical to `products` |
| products | array | Product report data (identical to `data`, two keys for the same data) |
| columns | array | Column definitions, elements contain `{field, title, cellType, sortable, filterable}`, identifying sortable/filterable fields |
| type | string | Response display type, e.g., `productWorkbenches` |
| costTime | integer | API latency (milliseconds) |
| costToken | integer | Tokens consumed |

> **`data` and `products`**: Both are the same array; read either one.
> **`total` semantics**: The total matched count across the entire database (not the current page count); can reach tens of millions without filters; must use sorting and pagination together.

### data[*] / products[*] Product Report Object Fields

**Identity & Basics**

| Field | Type | Description |
|------|------|------|
| sku | integer | Product SKU |
| productId | integer | Unified product ID (= `sku`) |
| title | string | Product title (original Russian) |
| imageUrl | string | Product main image URL |
| productUrl | string | Product URL |
| productPageUrl | string | Unified product page URL (= `productUrl`) |
| currency | string | Currency, always `₽` |
| sourceType | string | Data source, always `ozon` |
| sourceTool | string | Source tool identifier (e.g., `Seerfar-Ozon-查热销榜单`) |

**Sales Volume & Revenue**

| Field | Type | Description |
|------|------|------|
| sales | integer | Monthly sales volume |
| monthlySalesUnits | integer | Unified monthly sales (= `sales`) |
| revenue | number | Monthly sales revenue (RUB) |
| monthlySalesRevenue | number | Unified monthly revenue (= `revenue`) |
| missedRevenue | number | Lost revenue (RUB) |
| price | number | Price (RUB) |

**Conversion & Growth**

| Field | Type | Description |
|------|------|------|
| convToCartPdp | number | Cart conversion rate (%) |
| orderConversionRate | number | Order conversion rate (%) |
| salesRate | number | Sales growth rate (%) |
| revenueRate | number | Revenue growth rate (%) |
| drr | number | Ad cost share (ratio) |
| grossMargin | number | Gross margin (%) |
| returnCancellationRate | number | Return/cancellation rate (%) |
| views | integer | Views |

**Reviews & Engagement**

| Field | Type | Description |
|------|------|------|
| reviewRating | number | Rating (0~5) |
| rating | number | Unified rating (= `reviewRating`) |
| reviewCount | integer | Review count |
| questionsAndAnswers | integer | QA count |
| variants | integer | Variant count |

**Fulfillment & Logistics**

| Field | Type | Description |
|------|------|------|
| fulfillment | array<string> | Fulfillment methods (values `OZON`/`FBO`/`FBS`/`RFBS`/`FBP`) |
| weight | number | Weight (g) |
| volume | number | Volume (L) |

**Listing Time**

| Field | Type | Description |
|------|------|------|
| upTime | integer | Listing timestamp (milliseconds) |
| upDays | integer | Days since listing |
| upMonths | integer | Months since listing |

**Brand & Seller**

| Field | Type | Description |
|------|------|------|
| brandName | string | Brand name |
| brand | string | Unified brand (= `brandName`) |
| brandId | integer | Brand ID |
| brandUrl | string | Brand link |
| sellerName | string | Seller name |
| sellerId | integer | Seller ID (may be negative for Ozon self-operated) |
| categoryInfo | object | Category information (see below) |

### categoryInfo Category Information Object Fields

| Field | Type | Description |
|------|------|------|
| cnTitlePath | string | Chinese category path |
| enTitlePath | string | English category path |
| titlePath | string | Russian category path |
| fullCategoryId | array<string> | Full category ID hierarchy array |
| category | object | Category node: `{cnTitle, enTitle, title, level, id, pid, crossBorderSellable, disabled}` |

### Unified Field to Original Field Mapping (identical values)

| Unified Field | Original Field |
|----------|----------|
| productId | sku |
| monthlySalesUnits | sales |
| monthlySalesRevenue | revenue |
| rating | reviewRating |
| brand | brandName |
| productPageUrl | productUrl |

> These six pairs of fields are two keys for the same value; read either one, no need for duplicate display.

## Error Codes

Under normal circumstances the HTTP status code is 200, business results are distinguished via the response body:
- **Success**: Returns `code:"200"` + `errcode:200` (`msg` / `errmsg` both `ok`).
- **Business error**: HTTP still 200, but only returns `errcode` (non-200) + `errmsg` (reason), no `code` field.
- **Authentication failure**: HTTP status code 401, response body `{"errcode":401,"errmsg":"authorized error"}`.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse `data` / `products` fields normally |
| 400 | Parameter error | Check `errmsg`; common causes include missing `page`, `searchDate` format error, invalid category ID, etc. |
| 401 | Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 402 | Billing failed | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 1003 | Too many requests | Rate limited, wait and retry; do not bypass by reducing `pageSize` |
| Other non-200 values | Business exception | Check `errmsg` for specific reason |

Error response example:

```json
{
    "errcode": 1003,
    "errmsg": "请求过于频繁，请稍后再试。"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/seerfar/ozon/productReportSearch \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/1.0" \
  -d '{
    "page": {"page": 1, "pageSize": 3, "orders": [{"field": "sales", "direction": "DESC"}]}
  }'
```

## Response Example (abbreviated)

```json
{
  "code": "200",
  "msg": "ok",
  "errcode": 200,
  "errmsg": "ok",
  "total": 27879682,
  "type": "productWorkbenches",
  "costTime": 1492,
  "costToken": 16000,
  "data": [
    {
      "sku": 2107989735,
      "productId": 2107989735,
      "title": "Туалетная Бумага ROSE 12 рулонов 3 слоя с ароматом Розы",
      "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-a/wc300/7814428966.jpg",
      "productUrl": "https://www.ozon.ru/product/2107989735",
      "productPageUrl": "https://www.ozon.ru/product/2107989735",
      "price": 297.0,
      "currency": "₽",
      "sales": 307524,
      "monthlySalesUnits": 307524,
      "revenue": 83095800.0,
      "monthlySalesRevenue": 83095800.0,
      "missedRevenue": 0.0,
      "salesRate": 56.0,
      "revenueRate": 58.0,
      "convToCartPdp": 25.1,
      "orderConversionRate": 87.9,
      "reviewRating": 4.9,
      "rating": 4.9,
      "reviewCount": 492242,
      "questionsAndAnswers": 277,
      "variants": 2,
      "views": 48680877,
      "drr": 0.23,
      "grossMargin": 12.7,
      "returnCancellationRate": 4.9,
      "weight": 718.0,
      "volume": 11.088,
      "upTime": 1746565200000,
      "upDays": 421,
      "upMonths": 14,
      "brandName": "Лилия",
      "brand": "Лилия",
      "brandId": 100218750,
      "brandUrl": "https://www.ozon.ru/brand/100218750",
      "sellerName": "ЛИЛИЯ",
      "sellerId": 1275208,
      "fulfillment": ["FBO"],
      "sourceType": "ozon",
      "sourceTool": "Seerfar-Ozon-查热销榜单",
      "categoryInfo": {
        "cnTitlePath": "美容和卫生 > 个人卫生用品 > 卫生纸",
        "enTitlePath": "Beauty & Hygiene > Personal Hygiene Products > Toilet Paper",
        "titlePath": "Красота и гигиена > Товары личной гигиены > Туалетная бумага",
        "fullCategoryId": ["17027489", "17027489_200001243", "17027489_200001243_93507"],
        "category": {
          "cnTitle": "卫生纸",
          "enTitle": "Toilet Paper",
          "title": "Туалетная бумага",
          "level": 3,
          "id": "17027489_200001243_93507",
          "pid": "17027489_200001243",
          "crossBorderSellable": true,
          "disabled": false
        }
      }
    }
  ]
}
```

---
