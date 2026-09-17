# MPSTATS Ozon Product Detail API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/mpstats/ozon/productDetail`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from the environment variable `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON). The following fields are consistent with the currently registered "MPSTATS-Ozon-Product Detail" input schema in the tool gateway (sync date 2026-04-30).

| Parameter | Type | Required | Description |
|------|------|------|------|
| productIds | array | Yes | Exactly one Ozon product ID (integer or string), for example `[1786874757]`; multiple IDs are currently unsupported |
| startDate | string | No | Statistics start date, format `YYYY-MM-DD`; latest is yesterday |
| endDate | string | No | Statistics end date, format `YYYY-MM-DD`; latest is yesterday |
| includeFbs | boolean | No | Whether to include FBS data for the requested SKU |

> `productIds` must contain exactly one item. To query another SKU, make a separate request; each request consumes credits.

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
| total | integer | Number of SKUs returned (= `successCount` + `failedCount`) |
| successCount | integer | Number of SKUs for which cards were successfully returned |
| failedCount | integer | Number of SKUs that failed |
| failures | array | List of failed SKU details (each item contains the failed `productId` and error info) |
| products | array | Product card list (see details below) |
| columns | array | Rendered column definitions |
| costTime | integer | API latency (milliseconds) |
| costToken | integer | Tokens consumed |
| type | string | Response type |

### products[*] Product Detail Fields (36 fields)

Per official outputSchema definition (`_mpstats_ozon_productDetail`, sync date 2026-05-06). **The detail field set differs from brand/category/seller**: detail has unique deep fields such as `previous*` / `revenuePotential` / `deliveryScheme` / `productImageUrls`, but does not return `brandId` / `country` / `category` / `minPrice/maxPrice/averagePrice` / `balanceFbs` / `frozenStocks` / `warehousesCount` / `daysInSite/daysInStock/turnoverDays` / `position/categoryPosition/revenueSharePercent` / `isFbs`.

**Identity & Basic Information**

| Field | Type | Description |
|------|------|------|
| productId | integer | SKU ID |
| title | string | Product name (Russian) |
| brand | string | Brand |
| sellerName | string | Seller name |
| sellerId | integer | Seller ID |
| sellerIsBestSeller | boolean | Whether the seller is a best seller |
| nicheName | string | Niche path (Russian, `/` separated) |
| nicheId | integer | Niche ID |
| firstDate | string | Listing date (`yyyy-MM-dd`) |
| updated | string | Data update time (`yyyy-MM-dd HH:mm:ss`) |
| note | string | Notes |
| sourceTool / sourceType | string | Source tool / data source identifier |

**Images**

| Field | Type | Description |
|------|------|------|
| imageUrl | string | Main image URL (first large image) |
| imageCount | integer | Total image count |
| productImageUrls | array<string> | Remaining large image URLs besides the main image |
| productPageUrl | string | Product page URL |

**Price & Discount**

| Field | Type | Description |
|------|------|------|
| price | number | Current selling price |
| oldPrice | number | Original price before discount |
| ozonCardPrice | number | Ozon Card price (bank card discount price) |
| discount | integer | Discount, integer percentage 0-100 |
| currency | string | Currency symbol (`₽` / `$` / `€`) |

**Ratings**

| Field | Type | Description |
|------|------|------|
| rating | number | Rating, 0-5 |
| reviewCount | integer | Number of reviews |

**Inventory & Delivery**

| Field | Type | Description |
|------|------|------|
| balance | integer | Current stock (units) |
| deliveryScheme | string | Delivery scheme; `FBO` = Ozon fulfillment, `FBS` = seller self-delivery |

**Sales & Revenue (Current Period + Prior Period Comparison)**

| Field | Type | Description |
|------|------|------|
| salesPerDay | number | Average daily sales (units/day) |
| salesPerDayWithStock | number | Average daily sales counting only days with stock |
| dailySalesRevenue | number | Average daily sales revenue |
| dailySalesRevenueWithStock | number | Average daily sales revenue counting only days with stock |
| monthlySalesUnits | integer | Sales volume during the statistics period (units) |
| monthlySalesRevenue | number | Sales revenue during the statistics period |
| previousSalesUnits | integer | Prior period sales volume (the same-length period before the current statistics period) |
| previousRevenue | number | Prior period sales revenue |
| revenuePotential | number | Potential revenue (estimated based on full-period stock availability) |
| lostProfit | number | Lost revenue (due to stockouts, etc.) |
| lostProfitPercent | number | Lost revenue percentage (%) |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Insufficient credits or balance | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/mpstats/ozon/productDetail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "productIds": [1786874757],
    "startDate": "2025-03-01",
    "endDate": "2025-03-31",
    "includeFbs": true
  }'
```

---
