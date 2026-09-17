# WallySmarter Product Detail API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/wallysmarter/productDetail`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| productId | integer | Yes | Product ID (ItemId), the numeric ID contained in the product detail link. For example: the `5169493923` in `https://www.walmart.com/ip/5169493923` |
| includeStats | boolean | No | Whether to include historical price/historical sales, default `true` |

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
| msg | string | Message (`"ok"` on success, error description on failure) |
| total | integer | Number of products returned (typically 1 for this endpoint) |
| products | array | Product list (see product object below) |
| columns | array | Column definitions (metadata describing each field in products, including field, title, cellType, etc.) |
| type | string | Response render type (fixed value `"productWorkbenches"`) |
| costTime | integer | API elapsed time (milliseconds) |
| costToken | integer | Token cost |

### Product Object

| Field | Type | Description |
|------|------|------|
| usItemId | integer | Internal product ID (same as the requested productId) |
| productId | string | Walmart product unique identifier (alphanumeric, e.g., `"6YBM50F6ZXAE"`) |
| title | string | Product name |
| description | string | Product description |
| price | number | Current selling price (USD) |
| wasPrice | number | Striketrough price (USD), may be null when no discount |
| minPrice | number | Minimum price (USD) |
| brand | string | Brand name |
| rating | number | Product rating (0.0-5.0) |
| reviews | integer | Review count |
| salesEstimate | integer | Sales estimate (units, in recent period) |
| revenue | number | Revenue estimate (USD) |
| sellerName | string | Seller name |
| fulfillmentType | string | Fulfillment type: `"MARKETPLACE"` (third-party seller self-fulfilled) or `"WFS"` (Walmart Fulfillment Services) |
| productPageUrl | string | Product page URL |
| imageUrl | string | Product image URL (thumbnail) |
| departmentName | string | Department name (e.g., `"Cell Phones"`) |
| departmentId | integer | Department ID |
| listingScore | integer | Listing quality score |
| contentScore | integer | Content quality score |
| outOfStock | integer | Whether out of stock (`0`=in stock, `1`=out of stock) |
| sponsored | integer | Whether a sponsored product (`0`=no, `1`=yes) |
| isBranded | integer | Whether a branded product (`0`=no, `1`=yes) |
| multipleOptionsAvailable | integer | Whether there are variants (`0`=no, `1`=yes) |
| createdAt | string | First indexed time by WallySmarter (format: `yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'`) |
| updatedAt | string | Most recent data update time (same format as above) |
| stats | object/null | Historical statistics (only returned when `includeStats=true`, otherwise null. See structure below) |
| sourceTool | string | Source tool identifier |
| sourceType | string | Product source platform (fixed value `"walmart"`) |

### stats Object Structure

Returned when `includeStats=true` (default), aggregated by day and sorted by time ascending, timezone UTC. Contains two time series arrays:

| Field | Type | Description |
|------|------|------|
| stats.price | array | Historical selling price time series (sorted by date ascending). Each item is a single date-price mapping |
| stats.sales | array | Historical sales time series (sorted by date ascending). Each item is a single date-sales mapping |

**Array element structure:**

Each element is an object containing exactly one key-value pair. The key is a date string (format `yyyy-MM-dd`, UTC), and the value is the numeric amount for that day (price: in USD; sales: in units).

**Sample excerpt:**

```json
{
  "stats": {
    "price": [
      {"2025-08-18": 279.94},
      {"2025-09-29": 279.94}
    ],
    "sales": [
      {"2025-08-18": 62},
      {"2025-09-29": 79}
    ]
  }
}
```

> Data is aggregated by day (UTC timezone), sorted in ascending time order, covering the full history since the product was first indexed by WallySmarter. When consuming, iterate the arrays and take each object's unique key as the date and its unique value as the numeric amount.

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Insufficient balance | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/wallysmarter/productDetail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"productId": 5177343351, "includeStats": true}'
```

---
