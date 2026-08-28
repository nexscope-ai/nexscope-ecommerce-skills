# MPSTATS Ozon Product Detail (Batch) API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/mpstats/ozon/productDetail`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from the environment variable `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON). The following fields are consistent with the currently registered "MPSTATS-Ozon-Product Detail" input schema in the tool gateway (sync date 2026-04-30).

| Parameter | Type | Required | Description |
|------|------|------|------|
| productIds | array | Yes | List of Ozon product IDs (integer or string), **max 100 per request**, split into batches if exceeding |
| startDate | string | No | Statistics start date, format `YYYY-MM-DD`; shared across the batch; latest is yesterday |
| endDate | string | No | Statistics end date, format `YYYY-MM-DD`; shared across the batch; latest is yesterday |
| includeFbs | boolean | No | Whether to include FBS data; shared across the batch |

> The server concurrently requests each SKU, with a single automatic retry on failure; partial success is supported.

## Response Structure

| Field | Type | Description |
|------|------|------|
| code | string | Return code (string), `"200"` indicates success |
| errcode | integer | Return code (integer), `200` indicates success |
| msg / errmsg | string | Message; `ok` for success |
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

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse `products` normally |
| 401 | Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 402 | Insufficient credits or balance | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Other non-200 values | Business exception | Check `errmsg` / `msg`; common causes include batch exceeding 100, date beyond yesterday, etc. |

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
