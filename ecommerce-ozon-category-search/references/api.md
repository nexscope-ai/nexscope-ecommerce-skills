# Seerfar Ozon Category Product Search API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/seerfar/ozon/categorySearch`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from the environment variable `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)
- **User-Agent**: `NexScope-Skill/1.0`; HTTP timeout 60s

## Request Parameters

POST Body (JSON). The following fields are consistent with the interface `inputSchema`. `categoryId` and `page` are required, the rest are optional.

| Parameter | Type | Required | Description |
|------|------|------|------|
| categoryId | string | Yes | Ozon category ID, obtained from Ozon category documentation or other Seerfar Ozon tools. Format like `15621032_15621049_115951147` (multi-level categories joined by `_`) |
| page | object | Yes | Pagination & sorting: `{page, pageSize, orders[]}` |
| page.page | integer | No | Page number, starting from 1, default 1 |
| page.pageSize | integer | No | Items per page, default 20, **maximum 20** (exceeding returns `errcode 1002`) |
| page.orders | array | No | Sort rules, elements `{field, direction}` (both required); `direction` takes `DESC` (descending) / `ASC` (ascending). Common sort fields: `sales`, `price`, `revenue`, `reviewRating` |
| date | string | No | Query historical month, format `yyyy-MM` (e.g., `2026-02`); defaults to last 30 days if omitted |
| fulfillment | string | No | Fulfillment method filter, fixed options: `FBO`, `FBS`, `RFBS`, `FBP`, `OZON`; queries all if omitted. **Note: single string, not an array** |
| uId | string | No | User ID (max 1000) |
| memberId | string | No | Member ID (a unique member identifier; a user can belong to multiple teams; data is attributed to memberId, max 1000) |

> **Required constraints**: `categoryId` and `page` are both required; missing either returns `errcode 400`.
> **Pagination limit**: `page.pageSize` has a maximum of 20; paginate via incrementing `page.page`.
> **Sorting**: Recommended to sort by core metrics via `page.orders` (e.g., `sales` DESC for hot products, `revenue` DESC for high revenue, `price` DESC for high price tier) to avoid paging through unsorted results.
> **Historical month**: Passing `yyyy-MM` in `date` queries the snapshot for that month; omitting returns the last 30 days of data, with `startDate`/`endDate` in the response indicating the actual statistics interval.

## Response Structure

| Field | Type | Description |
|------|------|------|
| code | string | Return code, `"200"` indicates success (returned on success) |
| errcode | integer | Error code, `200` indicates success; only returned on business errors (coexists with `code` on success) |
| msg | string | Message; `ok` for success |
| errmsg | string | Error message; `ok` for success, reason description on business error |
| id | string | Echoed category ID |
| total | integer | **Number of records returned on this page** (equals the current page `data` count, not total category product count) |
| totalSales | integer | Total category sales volume (within the statistics interval) |
| totalRevenue | number | Total category sales revenue (RUB) |
| avgPrice | number | Average category product price (RUB) |
| rating | number | Average category product rating |
| seasonalityAmplitude | string | Seasonality intensity, e.g., `STRONG_SEASONALITY` |
| seasonalityCoef | string | Seasonality phase, e.g., `OFF_SEASON` |
| startDate | string | Statistics start date |
| endDate | string | Statistics end date |
| sellerType | object | **Fulfillment method distribution** (not seller domestic/cross-border type), keys are fulfillment methods and values are product counts for that method, e.g., `{"FBO":218,"RFBS":528,"FBP":5,"FBS":240,"OZON":1}` |
| categoryInfo | object | Category metadata, structure see "categoryInfo Structure" below |
| data | array | Category product list (see details below) |
| products | array | Category product list, content identical to `data` |
| hasNextPage | boolean | Whether there is a next page |
| columns | array | Column definitions, elements contain `{field, title, cellType, sortable, filterable}` |
| type | string | Response display type |
| costTime | integer | API latency (milliseconds) |
| costToken | integer | Tokens consumed |

### data[*] / products[*] Category Product Object Fields

| Field | Type | Description |
|------|------|------|
| sku | integer | Product SKU |
| productId | integer | Unified product ID, mapped from `sku` |
| title | string | Product title |
| price | number | Product price (RUB) |
| currency | string | Currency, always `₽` |
| sales | integer | Product sales volume |
| monthlySalesUnits | integer | Unified monthly sales, mapped from `sales` |
| revenue | number | Product sales revenue |
| monthlySalesRevenue | number | Unified monthly revenue, mapped from `revenue` |
| reviewRating | number | Product rating |
| rating | number | Unified rating, mapped from `reviewRating` |
| reviewCount | integer | Number of reviews |
| brandName | string | Brand name |
| brand | string | Unified brand, mapped from `brandName` |
| sellerName | string | Seller name |
| fulfillment | array | Product fulfillment methods, e.g., `["FBO"]`, may contain multiple values |
| imageUrl | string | Product image URL |
| productUrl | string | Product URL |
| productPageUrl | string | Unified product page URL, mapped from `productUrl` |
| categoryInfo | object | Product category attribution information, structure see "categoryInfo Structure" below |
| sourceType | string | Data source, always `ozon` |
| sourceTool | string | Source tool, e.g., `Seerfar-Ozon-查类目` |

> **Unified fields vs original fields**: `productId`/`rating`/`brand`/`monthlySalesUnits`/`monthlySalesRevenue`/`productPageUrl` are backend unified mapping fields, equivalent to the original `sku`/`reviewRating`/`brandName`/`sales`/`revenue`/`productUrl`; choose either one for display, original fields are recommended (semantically more intuitive).

### categoryInfo Structure (returned at top level and for each product)

| Field | Type | Description |
|------|------|------|
| cnTitlePath | string | Chinese category path, e.g., `鞋类 > 运动鞋和工作鞋 > 举重鞋` |
| enTitlePath | string | English category path, e.g., `Footwear > Sports and Work Footwear > Weightlifting Shoes` |
| titlePath | string | Russian (front-end) category path, e.g., `Обувь > Спортивная и рабочая обувь > Штангетки` |
| fullCategoryId | array | Array of category IDs at each level, e.g., `["15621032","15621032_15621049","15621032_15621049_115951147"]` |
| category | object | Terminal category object, containing `cnTitle`/`enTitle`/`title`(Russian)/`level`/`crossBorderSellable`(whether cross-border sales are allowed)/`pid`/`disabled`/`id` |

> `categoryInfo` is returned identically at both the top level and in each `data[*]`, and can be used to verify category names (CN/EN/RU) and cross-border salability (`category.crossBorderSellable`).

## Error Codes

Under normal circumstances the HTTP status code is 200, business results are distinguished via the response body:
- **Success**: Returns `code:"200"` + `errcode:200` (`msg` / `errmsg` both `ok`).
- **Business error**: HTTP still 200, but only returns `errcode` (non-200) + `errmsg` (reason), no `code` field.
- **Authentication failure**: HTTP status code 401, response body `{"errcode":401,"errmsg":"authorized error"}`.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse `data` / `products` fields normally |
| 400 | Parameter error | Check `errmsg`; common causes include missing `categoryId`, missing `page` |
| 1002 | Pagination parameter exceeded limit | `page.pageSize` maximum is 20, reduce and retry |
| 1003 | Too many requests | Rate limited, retry later |
| 401 | Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 402 | Billing failed | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Other non-200 values | Business exception | Check `errmsg` for specific reason |

> **Non-existent category ID**: Passing a non-existent `categoryId` typically returns `errcode:200`, `total:0`, `data:[]` (empty result). Determining "category has no data" should be based on `total=0`, not `errcode`.

Error response examples:

```json
{
    "errcode": 1002,
    "errmsg": "分页参数超出限制，请检查输入。参数 page.pageSize 最大为 20，请调小后重试。"
}
```

```json
{
    "errcode": 400,
    "errmsg": "categoryId 为必填参数"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/seerfar/ozon/categorySearch \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/1.0" \
  -d '{
    "categoryId": "15621032_15621049_115951147",
    "page": {"page": 1, "pageSize": 5, "orders": [{"field": "sales", "direction": "DESC"}]}
  }'
```

## Response Example (abbreviated)

```json
{
  "code": "200",
  "msg": "ok",
  "errcode": 200,
  "errmsg": "ok",
  "id": "15621032_15621049_115951147",
  "total": 5,
  "totalSales": 2066,
  "totalRevenue": 12973043,
  "avgPrice": 7228.0,
  "rating": 4.9,
  "seasonalityAmplitude": "STRONG_SEASONALITY",
  "seasonalityCoef": "OFF_SEASON",
  "startDate": "2026-06-01",
  "endDate": "2026-07-01",
  "hasNextPage": true,
  "type": "productWorkbenches",
  "costTime": 1415,
  "costToken": 16000,
  "sellerType": {"FBO": 218, "RFBS": 528, "FBP": 5, "FBS": 240, "OZON": 1},
  "categoryInfo": {
    "cnTitlePath": "鞋类 > 运动鞋和工作鞋 > 举重鞋",
    "enTitlePath": "Footwear > Sports and Work Footwear > Weightlifting Shoes",
    "titlePath": "Обувь > Спортивная и рабочая обувь > Штангетки",
    "fullCategoryId": ["15621032", "15621032_15621049", "15621032_15621049_115951147"],
    "category": {
      "cnTitle": "举重鞋", "enTitle": "Weightlifting Shoes", "title": "Штангетки",
      "level": 3, "crossBorderSellable": true, "pid": "15621032_15621049",
      "disabled": false, "id": "15621032_15621049_115951147"
    }
  },
  "data": [
    {
      "sku": 1546459445,
      "productId": 1546459445,
      "title": "Штангетки YOUNGS",
      "price": 6481.0,
      "currency": "₽",
      "sales": 21,
      "monthlySalesUnits": 21,
      "revenue": 122635.0,
      "monthlySalesRevenue": 122635.0,
      "reviewRating": 4.8,
      "rating": 4.8,
      "reviewCount": 524,
      "brandName": "YOUNGS",
      "brand": "YOUNGS",
      "sellerName": "YoungS shoes",
      "fulfillment": ["FBO"],
      "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-j/wc300/7000839379.jpg",
      "productUrl": "https://www.ozon.ru/product/1546459445",
      "productPageUrl": "https://www.ozon.ru/product/1546459445",
      "categoryInfo": { "...": "same as top-level categoryInfo" },
      "sourceType": "ozon",
      "sourceTool": "Seerfar-Ozon-查类目"
    }
  ],
  "products": [ "..." ],
  "columns": [ { "field": "sku", "title": "商品SKU", "cellType": "number", "sortable": true, "filterable": true } ]
}
```

> `products` content is identical to `data`, represented as `"..."` in the example to indicate omission. `total` is the number of records returned on this page (5 in this example), not total category product count; `hasNextPage=true` indicates more pages exist. `sellerType` is fulfillment method distribution (not seller domestic/cross-border type).

---
