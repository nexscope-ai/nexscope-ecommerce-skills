# MPSTATS Ozon Seller Products API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/mpstats/ozon/sellerProducts`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from the environment variable `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON). The following fields are consistent with the currently registered "MPSTATS-Ozon-Seller Products" input schema in the tool gateway (sync date 2026-04-30).

| Parameter | Type | Required | Description |
|------|------|------|------|
| sellerId | string | Yes | Ozon seller ID (numeric string), matching the seller identifier in product lists/seller rankings |
| startDate | string | No | Statistics start date `YYYY-MM-DD`; latest is yesterday |
| endDate | string | No | Statistics end date `YYYY-MM-DD`; latest is yesterday |
| page | integer | No | Page number, starting from 1 |
| pageSize | integer | No | Rows per page 1-100, default 100 |
| sortField | string | No | Sort column name (snake_case), e.g., `sales`, `revenue`, `final_price`, `balance`, `rating` |
| sortDirection | string | No | `asc` / `desc` |
| currency | string | No | Currency code, default `RUB`, e.g., `USD` |
| currencyRate | integer | No | Custom exchange rate (for non-default currency) |
| includeFbs | boolean | No | Whether to include FBS data |
| filters | array | No | List of numeric filter conditions, each `{field, op, value, value2?}`, multiple conditions AND |

### filters Sub-fields

  | Sub-field | Type | Required | Description |  
|--------|------|------|------|
| field | string | Yes | Column name (snake_case). Common: `sales`, `final_price`, `rating`, `comments`, `balance`, `revenue`, `days_in_stock`, `turnover_days`, `lost_profit`, `category_position`. |
| op | string | Yes | `GTE` / `LTE` / `GT` / `LT` / `EQ` / `NOT_EQ` / `BETWEEN` |
| value | number | Yes | Main value (lower bound when `BETWEEN`) |
| value2 | number | `BETWEEN` required | Upper bound (closed interval) |

## Response Structure

| Field | Type | Description |
|------|------|------|
| code | string | Return code, `"200"` success |
| msg | string | Message; `ok` for success |
| total | integer | Total number of matched products under the seller |
| products | array | Product list (see details below) |
| columns | array | Rendered column definitions |
| costTime | integer | API latency (milliseconds) |
| costToken | integer | Tokens consumed |
| type | string | Response type |

### products[*] Product Object Fields (39 fields)

Per official outputSchema definition (`_mpstats_ozon_sellerProducts`, sync date 2026-05-06). This schema is **fully shared** with `productSearch` / `brandProducts` / `categoryProducts`; the 4 endpoints differ only in query dimension, with an identical set of product card fields returned.

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
| position | integer | Ranking within the current query dimension (seller for this endpoint) |
| categoryPosition | integer | Ranking within the category |
| revenueSharePercent | number | Revenue share of this SKU within the current query dimension, 0-100 |

## Error Codes

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse `products` |
| 401 | Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 402 | Insufficient credits or balance | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Other | Business exception | Check `errmsg`; common causes include `sellerId` not being numeric, the ID not existing, date beyond yesterday, etc. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/mpstats/ozon/sellerProducts \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "sellerId": "3628678",
    "sortField": "revenue",
    "sortDirection": "desc",
    "pageSize": 100
  }'
```

---
