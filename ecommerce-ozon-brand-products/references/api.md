# MPSTATS Ozon Brand Products API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/mpstats/ozon/brandProducts`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from the environment variable `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON). The following fields are consistent with the currently registered "MPSTATS-Ozon-Brand Products" input schema in the tool gateway (sync date 2026-04-30).

| Parameter | Type | Required | Description |
|------|------|------|------|
| brandName | string | Yes | Ozon brand display name (Russian or Latin) |
| startDate | string | No | Statistics start date, `YYYY-MM-DD`; latest is yesterday |
| endDate | string | No | Statistics end date, `YYYY-MM-DD`; latest is yesterday |
| page | integer | No | Page number, starting from 1 |
| pageSize | integer | No | Rows per page, 1-100, default 100 |
| sortField | string | No | Sort column name (snake_case), e.g., `sales`, `revenue`, `final_price`, `balance`, `rating` |
| sortDirection | string | No | `asc` ascending / `desc` descending |
| currency | string | No | Currency code for result amounts, default `RUB`, e.g., `USD` / `EUR` / `CNY` |
| currencyRate | integer | No | Custom exchange rate (for non-default currency) |
| includeFbs | boolean | No | Whether to include FBS data |
| filters | array | No | List of numeric filter conditions, each `{field, op, value, value2?}`, multiple conditions AND |

### filters Field Description

  | Sub-field | Type | Required | Description |  
|--------|------|------|------|
| field | string | Yes | Column name (snake_case), common ones listed below |
| op | string | Yes | `GTE` / `LTE` / `GT` / `LT` / `EQ` / `NOT_EQ` / `BETWEEN` |
| value | number | Yes | Main value (lower bound when `BETWEEN`) |
| value2 | number | `BETWEEN` required | Upper bound (closed interval) |

**Common field**: `sales` (monthly sales), `final_price` (selling price RUB), `rating` (rating 0-5), `comments` (review count), `balance` (stock), `revenue` (sales revenue RUB), `days_in_stock` (days in stock), `turnover_days` (turnover days), `lost_profit` (lost revenue RUB), `category_position` (category ranking).

## Response Structure

| Field | Type | Description |
|------|------|------|
| code | string | Return code, `"200"` success |
| msg | string | Message; `ok` for success |
| total | integer | Total number of matched products under the brand |
| products | array | Product list (see details below) |
| columns | array | Rendered column definitions |
| costTime | integer | API latency (milliseconds) |
| costToken | integer | Tokens consumed |
| type | string | Response type |

### products[*] Product Object Fields (39 fields)

Per official outputSchema definition (`_mpstats_ozon_brandProducts`, sync date 2026-05-06). This schema is **fully shared** with `productSearch` / `categoryProducts` / `sellerProducts`; the 4 endpoints differ only in query dimension, with an identical set of product card fields returned.

**Identity & Basic Information**

| Field | Type | Description |
|------|------|------|
| productId | integer | SKU ID |
| title | string | Product name (Russian) |
| brand | string | Brand |
| brandId | integer | Brand ID |
| sellerName | string | Seller name |
| sellerId | integer | Seller ID |
| category | string | Category path (Russian, `/` separated) |
| nicheName | string | Niche path (Russian) |
| nicheId | integer | Niche ID |
| country | string | Country of sale, always `RU` for Ozon |
| firstDate | string | Listing date (`yyyy-MM-dd`) |
| imageUrl | string | Main image URL |
| productPageUrl | string | Product page URL |
| sourceTool / sourceType | string | Source tool / data source identifier |

**Price & Currency**

| Field | Type | Description |
|------|------|------|
| price | number | Current selling price |
| oldPrice | number | Original price before discount |
| ozonCardPrice | number | Ozon Card price |
| minPrice / maxPrice / averagePrice | number | Minimum / maximum / average price during the statistics period |
| currency | string | Currency symbol (`₽` / `$` / `€`) |

**Ratings & Reviews**

| Field | Type | Description |
|------|------|------|
| rating | number | Rating, 0-5 |
| reviewCount | integer | Number of reviews |

**Inventory & FBS**

| Field | Type | Description |
|------|------|------|
| balance | integer | Current stock (units) |
| balanceFbs | integer | FBS stock (seller self-ship units) |
| frozenStocks | integer | Slow-moving stock |
| warehousesCount | integer | Number of FBO warehouses |
| isFbs | boolean | Whether shipped via FBS |

**Sales & Turnover**

| Field | Type | Description |
|------|------|------|
| salesPerDay | number | Average daily sales (units/day) |
| monthlySalesUnits | integer | Sales volume during the statistics period (units) |
| monthlySalesRevenue | number | Sales revenue during the statistics period |
| lostProfit | number | Lost revenue (due to stockouts, etc.) |
| daysInSite | integer | Days on sale (statistics period, including out-of-stock days) |
| daysInStock | integer | Days in stock |
| turnoverDays | number | Turnover days (lower is faster) |

**Ranking & Revenue Share**

| Field | Type | Description |
|------|------|------|
| position | integer | Ranking within the current query dimension (brand for this endpoint) |
| categoryPosition | integer | Ranking within the category |
| revenueSharePercent | number | Revenue share of this SKU within the current query dimension, 0-100 |

## Error Codes

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse `products` |
| 401 | Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 402 | Insufficient credits or balance | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Other | Business exception | Check `errmsg`; common causes include `brandName` spelling errors, date beyond yesterday, etc. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/mpstats/ozon/brandProducts \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "brandName": "adidas",
    "sortField": "sales",
    "sortDirection": "desc",
    "pageSize": 50,
    "filters": [
      {"field": "rating", "op": "GTE", "value": 4.5}
    ]
  }'
```

---
