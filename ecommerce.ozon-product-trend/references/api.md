# MPSTATS Ozon Product Trend (Daily) API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/mpstats/ozon/productTrend`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from the environment variable `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON). The following fields are consistent with the currently registered "MPSTATS-Ozon-Product Trend" input schema in the tool gateway (sync date 2026-04-30).

| Parameter | Type | Required | Description |
|------|------|------|------|
| productId | integer | Yes | Ozon product SKU |
| startDate | string | No | Statistics start date, `YYYY-MM-DD`; data delayed by T-1, latest is yesterday |
| endDate | string | No | Statistics end date, `YYYY-MM-DD`; data delayed by T-1, latest is yesterday |
| includeFbs | boolean | No | Whether to include FBS data |
| includeSearchStats | boolean | No | Whether to include search position / visibility; not supported for some niches |

## Response Structure

| Field | Type | Description |
|------|------|------|
| code | string | Return code (string), `"200"` indicates success |
| errcode | integer | Return code (integer), `200` indicates success |
| msg / errmsg | string | Message; `ok` for success |
| total | integer | Number of daily data points (window days) |
| data | array | List of daily data points (see details below) |
| columns | array | Rendered column definitions |
| costTime | integer | API latency (milliseconds) |
| costToken | integer | Tokens consumed |
| type | string | Response type |

> Note: **The daily series field name is `data`**, not `trend`; the response body does not include a separate `productId` echo.

### data Data Point Fields

Per official outputSchema definition (`_mpstats_ozon_productTrend`, sync date 2026-05-06). 13 fields total:

| Field | Type | Description |
|------|------|------|
| date | string | Date, `YYYY-MM-DD` |
| hasData | boolean | Whether there is data for this day (`false` indicates a missing day, distinct from `sales=0`) |
| price | number | Daily selling price |
| oldPrice | number | Daily original price before discount |
| ozonCardPrice | number | Ozon Card price (Ozon official bank card discount price) |
| discount | integer | Discount, integer percentage 0-100 |
| currency | string | Currency symbol (e.g., `₽` / `$` / `€`) |
| sales | integer | Daily sales (units) |
| balance | integer | Daily FBO warehouse stock (units) |
| rating | number | Rating, 0-5 |
| comments | integer | Review count |
| isBestseller | boolean | Whether the "bestseller" badge was active that day |
| isNew | boolean | Whether the "new product" badge was active that day |

> **Fields not declared in the schema will not be returned**: The endpoint does not independently return `revenue`, `reviewCount`, `balanceFbs`, `isInStock`, etc. Estimate revenue using `sales x price`.

### includeSearchStats Notes

The input parameter `includeSearchStats=true` serves only as an optional server-side capability switch; the official outputSchema does not declare any additional top-level arrays or per-point fields. If the schema is extended in the future, refer to the latest outputSchema returned by the tool gateway's `listEnabledTool`.

## Error Codes

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse `data` |
| 401 | Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 402 | Insufficient credits or balance | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Other non-200 values | Business exception | Check `errmsg` / `msg`; common causes include invalid `productId`, date beyond yesterday, etc. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/mpstats/ozon/productTrend \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "productId": 1786874757,
    "startDate": "2025-03-01",
    "endDate": "2025-03-31",
    "includeSearchStats": true
  }'
```

---
