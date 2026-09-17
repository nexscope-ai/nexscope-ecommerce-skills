# Walmart Frontend Product List API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/walmart/search`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| keyword | string | No* | Search keyword, max length 1024 characters. *At least one of keyword and categoryId must be provided |
| categoryId | string | No* | Category ID. *At least one of keyword and categoryId must be provided. `0` means all departments. For example: `976759_976787` means "Cookies" |
| sort | string | No | Sort method. Options: `price_low` (price low to high), `price_high` (price high to low), `best_seller` (best seller), `best_match` (best match) |
| page | integer | No | Page number for pagination, default 1, max 100 |
| minPrice | number | No | Minimum price |
| maxPrice | number | No | Maximum price |
| spelling | boolean | No | Enable spelling correction, default `true`. `true` includes spelling correction, `false` excludes it |
| softSort | boolean | No | Sort by relevance, default `true`. Set to `false` to disable relevance sorting |
| storeId | string | No | Store ID, used to filter products by a specific store |
| device | string | No | Device type, default `desktop`. Options: `desktop`, `tablet`, `mobile` |
| facet | string | No | Filter conditions, format as key:value pairs separated by `\|\|` |
| nextDayEnabled | boolean | No | Only show NextDay delivery results, default `false`. `true` to enable, `false` to disable |
| jsonRestrictor | string | No | JSON field restrictor |


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
| total | integer | Record count |
| products | array | Product list (see product object below) |
| columns | array | Rendered columns |
| type | string | Render style |
| costToken | integer | Token cost |

### Product Object

| Field | Type | Description |
|------|------|------|
| productId | string | Product ID |
| usItemId | string | US item ID |
| title | string | Title |
| description | string | Description |
| price | number | Price |
| wasPrice | number | Original price (was_price) |
| currency | string | Currency unit |
| minPrice | number | Minimum price |
| pricePerUnitAmount | string | Price per unit amount |
| pricePerUnit | string | Price per unit |
| rating | number | Rating |
| reviews | integer | Review count |
| sellerName | string | Seller name |
| sellerId | string | Seller ID |
| imageUrl | string | Thumbnail |
| productPageUrl | string | Product page URL |
| sponsored | boolean | Whether a sponsored product |
| outOfStock | boolean | Whether out of stock |
| freeShipping | boolean | Whether free shipping |
| twoDayShipping | boolean | Whether two-day shipping supported |
| freeShippingWithWalmartPlus | boolean | Free shipping for Walmart Plus members |
| shippingPrice | number | Shipping cost |
| multipleOptionsAvailable | boolean | Whether multiple options available |
| variantSwatches | array | Variant swatch list (each item contains `name` variant name, `imageUrl` variant image URL, `productPageUrl` variant product page URL, `variantFieldId` variant field ID) |
| sourceTool | string | Source tool |
| sourceType | string | Source type: walmart |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Insufficient balance | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/walmart/search \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "wireless earbuds", "sort": "best_seller", "page": 1}'
```

---
