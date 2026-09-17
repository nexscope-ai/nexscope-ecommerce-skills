# Seerfar Ozon Shop Product Search API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/seerfar/ozon/shopSearch`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from the environment variable `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)
- **User-Agent**: `Nexscope-Skill/1.0`; HTTP timeout 60s

## Request Parameters

POST Body (JSON). The following fields are consistent with the interface `inputSchema`. `id` and `page` are required; all others are optional.

| Parameter | Type | Required | Description |
|------|------|------|------|
| id | integer | Yes | Shop (seller) ID, i.e., the `sellerId` returned by other Seerfar Ozon tools; negative values are Ozon platform self-operated sellers (e.g., `-2` Ozon Express, `-4` Ozon Fresh), positive values are third-party sellers |
| page | object | Yes | Pagination & sorting: `{page, pageSize, orders[]}` |
| page.page | integer | No | Page number, starting from 1, default 1 |
| page.pageSize | integer | No | Items per page, default 20, **maximum 20** (invalid values produce a platform error) |
| page.orders | array | No | Sort rules, elements `{field, direction}`; `direction` takes `DESC` (descending) / `ASC` (ascending). Common sort fields: `sales`, `price`, `reviewRating`, `upTime` |
| uId | string | No | User ID (max 1000) |
| memberId | string | No | Member ID (a unique member identifier; a user can belong to multiple teams; data is attributed to memberId, max 1000) |

> **Required constraints**: `id` and `page` are both required; missing required input produces a nonzero platform code.
> **Pagination limit**: `page.pageSize` has a maximum of 20; paginate via incrementing `page.page`.
> **Sorting**: Recommended to sort by core metrics via `page.orders` (e.g., `sales` DESC for hot products, `upTime` DESC for new products) to avoid paging through unsorted results.

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Response Structure

| Field | Type | Description |
|------|------|------|
| code | string | Provider business value retained inside `data`; not the outer platform status |
| msg | string | Message; `ok` for success |
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

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Parameter error | Check `msg`; common causes include missing `id` (`id 为必填参数`), missing `page` (`page 为必填参数`) |
| Pagination parameter exceeded limit | `page.pageSize` maximum is 20, reduce and retry |
| Too many requests | Rate limited, retry later |
| Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Billing failed | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/seerfar/ozon/shopSearch \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/1.0" \
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
