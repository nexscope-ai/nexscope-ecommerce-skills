# Seerfar Ozon Shop Product Search API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/seerfar/ozon/shopSearch`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from the environment variable `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)
- **User-Agent**: `NexScope-Skill/1.0`; HTTP timeout 60s

## Request Parameters

POST Body (JSON). The following fields are consistent with the interface `inputSchema`. `id` and `page` are required; all others are optional.

| Parameter | Type | Required | Description |
|------|------|------|------|
| id | integer | Yes | Shop (seller) ID, i.e., the `sellerId` returned by other Seerfar Ozon tools; negative values are Ozon platform self-operated sellers (e.g., `-2` Ozon Express, `-4` Ozon Fresh), positive values are third-party sellers |
| page | object | Yes | Pagination & sorting: `{page, pageSize, orders[]}` |
| page.page | integer | No | Page number, starting from 1, default 1 |
| page.pageSize | integer | No | Items per page, default 20, **maximum 20** (exceeding returns `errcode 1002`) |
| page.orders | array | No | Sort rules, elements `{field, direction}`; `direction` takes `DESC` (descending) / `ASC` (ascending). Common sort fields: `sales`, `price`, `reviewRating`, `upTime` |
| uId | string | No | User ID (max 1000) |
| memberId | string | No | Member ID (a unique member identifier; a user can belong to multiple teams; data is attributed to memberId, max 1000) |

> **Required constraints**: `id` and `page` are both required; missing either returns `errcode 400`.
> **Pagination limit**: `page.pageSize` has a maximum of 20; paginate via incrementing `page.page`.
> **Sorting**: Recommended to sort by core metrics via `page.orders` (e.g., `sales` DESC for hot products, `upTime` DESC for new products) to avoid paging through unsorted results.

## Response Structure

| Field | Type | Description |
|------|------|------|
| code | string | Return code, `"200"` indicates success (returned on success) |
| errcode | integer | Error code, `200` indicates success; only returned on business errors (coexists with `code` on success) |
| msg | string | Message; `ok` for success |
| errmsg | string | Error message; `ok` for success, reason description on business error |
| total | integer | **Number of records returned on this page** (equals the current page data count, not total shop product count) |
| totalSales | integer | Total shop sales in the last 30 days |
| data | array | Shop product list (see details below) |
| products | array | Shop product list, content identical to `data` |
| hasNextPage | boolean | Whether there is a next page |
| columns | array | Column definitions, elements contain `{field, title, cellType, sortable, filterable}` |
| type | string | Response display type, e.g., `productWorkbenches` |
| costTime | integer | API latency (milliseconds) |
| costToken | integer | Tokens consumed |

### data[*] / products[*] Shop Product Object Fields

| Field | Type | Description |
|------|------|------|
| productId | integer | Unified product ID, mapped from `sku` |
| sku | integer | Product SKU |
| rating | number | Unified rating, mapped from `reviewRating` |
| reviewRating | number | Product rating |
| weight | number | Product weight, in grams |
| sales | integer | Product sales in the last 30 days |
| monthlySalesUnits | integer | Unified monthly sales, mapped from `sales` |
| upTime | integer | Product listing time, millisecond timestamp |
| price | number | Product price (RUB) |
| currency | string | Currency, always `₽` |
| imageUrl | string | Unified main image URL |
| fulfillment | array | Product fulfillment methods, e.g., `["FBO"]`, may contain multiple values |
| sellerType | integer | Seller type: `0` domestic, `1` cross-border |
| returnCancellationRate | number | Product return/cancellation rate (%) |
| sourceType | string | Data source, always `ozon` |
| sourceTool | string | Source tool, e.g., `Seerfar-Ozon-查店铺` |

> **Field differences**: `returnCancellationRate` is generally returned for third-party sellers, but is often missing for Ozon platform self-operated sellers (`id` is negative); null-check before use.
> **Defined in schema but not returned in practice**: `productPageUrl` (unified product page URL), `monthlySalesRevenue` (unified monthly revenue), `brand` (unified brand) are marked in outputSchema as "no corresponding upstream field, kept as null" and are **not returned** in actual responses (neither null nor empty); do not depend on them.

## Error Codes

Under normal circumstances the HTTP status code is 200, business results are distinguished via the response body:
- **Success**: Returns `code:"200"` + `errcode:200` (`msg` / `errmsg` both `ok`).
- **Business error**: HTTP still 200, but only returns `errcode` (non-200) + `errmsg` (reason), no `code` field.
- **Authentication failure**: HTTP status code 401, response body `{"errcode":401,"errmsg":"authorized error"}`.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse `data` / `products` fields normally |
| 400 | Parameter error | Check `errmsg`; common causes include missing `id` (`id 为必填参数`), missing `page` (`page 为必填参数`) |
| 1002 | Pagination parameter exceeded limit | `page.pageSize` maximum is 20, reduce and retry |
| 1003 | Too many requests | Rate limited, retry later |
| 401 | Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 402 | Billing failed | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Other non-200 values | Business exception | Check `errmsg` for specific reason |

> **Non-existent shop ID**: Passing a non-existent `id` does not error; instead returns `errcode:200`, `total:0`, `data:[]` (empty result). Determining "shop has no data" should be based on `total=0`, not `errcode`.

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
    "errmsg": "id 为必填参数"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/seerfar/ozon/shopSearch \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/1.0" \
  -d '{
    "id": 1362816,
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
  "total": 5,
  "totalSales": 11782,
  "hasNextPage": true,
  "type": "productWorkbenches",
  "costTime": 4706,
  "costToken": 16000,
  "data": [
    {
      "productId": 1310550649,
      "sku": 1310550649,
      "rating": 4.9,
      "reviewRating": 4.9,
      "weight": 5650.0,
      "sales": 1098,
      "monthlySalesUnits": 1098,
      "upTime": 1700928000000,
      "price": 2591.0,
      "currency": "₽",
      "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-h/wc300/11110286861.jpg",
      "fulfillment": ["FBO"],
      "sellerType": 0,
      "returnCancellationRate": 15.6,
      "sourceType": "ozon",
      "sourceTool": "Seerfar-Ozon-查店铺"
    }
  ],
  "products": [ ... ]
}
```

> `products` content is identical to `data`; represented as `[ ... ]` in the example to indicate omission; the actual return contains the same complete product array as `data`.

---
