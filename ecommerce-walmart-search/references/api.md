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

Under normal circumstances, the HTTP status code of the API is always 200. Business success or failure is distinguished by the `errorCode` field in the response body (`errorCode = 200` indicates success, other values indicate business errors). In cases such as unauthorized access, the HTTP status code is 401, and the corresponding `errorCode` is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 402 | Insufficient balance | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Other non-200 values | Business exception | Refer to the `errmsg` field for the specific error reason |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/walmart/search \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "wireless earbuds", "sort": "best_seller", "page": 1}'
```

---
