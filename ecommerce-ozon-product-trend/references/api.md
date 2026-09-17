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

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Insufficient credits or balance | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |

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
