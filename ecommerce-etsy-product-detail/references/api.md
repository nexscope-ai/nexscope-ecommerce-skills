## Nexscope billing

The migrated Skill does not inherit the source platform's point value. This operation consumes Nexscope credits. Preserve X-Cost-Token and X-Cost-Credit from the HTTP response headers as server-reported billing metadata, and preserve X-Kong-Trace-Id for diagnostics.

# Nexscope proxy contract

The endpoint uses the `/api/v1/tools/research/` prefix. Successful HTTP responses use a Nexscope envelope (`code`, `msg`, `data`, `traceId`, and cost metadata); the original business response is nested in `data`.

# Etsy Product Details API Reference

## Request conventions

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/etsy/product/detail`
- **Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: Bearer <api_key>`; Read api_key from `NEXSCOPE_API_KEY`, falling back to `NEXSCOPE_API_KEY` (if unset, follow "Resolve authentication and credit issues" in SKILL.md)
- **User-Agent**：`Nexscope-Skill/2.0`
- **Forwarded headers**: `SESSION_ID`, `MODE_ID`, `APP_NAME` (read each from the environment variable of the same name; use an empty string if unset)
- **Timeout**: 150s

## Request parameters

POST body (JSON):

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| productUrl | string | Yes | - | Direct Etsy product HTTPS URL. Must not contain userinfo; the host must be `etsy.com` or a subdomain, and the port must be omitted or `443`; the path must be `/listing/<numericID>`, optionally followed by at most one nonempty title slug, a trailing slash, and query parameters |

Etsy search pages, shop pages, non-Etsy domains, and URLs without a numeric listing ID are not accepted. Each call queries only one Listing; if the upstream returns a number of valid products other than 1, the API returns a business error.

```json
{
  "productUrl": "https://www.etsy.com/listing/1710567856/its-okay-to-make-some-mistakes-shirt"
}
```

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Package scripts unwrap this platform object for their business output and retain its `code`, `msg`, and timing metadata under `_nexscope`; for those outputs, inspect `_nexscope.code` / `_nexscope.msg`. Business `code` or `error` fields are not platform success markers.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Response structure

Successful responses use the standard Nexscope envelope:

| Field | Type | Description |
|------|------|------|
| data | array | Array of product objects; exactly 1 item on success |
| total | integer | Always `1` on success |
| costToken | integer | Tokens consumed |
| type | string | Always `tableListWorkbenches` |
| columns | array | Rendering column definitions generated from top-level product fields |

### Product object

| Field | Type | Description |
|------|------|------|
| productId | string | Etsy listing ID |
| shopId | string | Shop ID |
| shopUrl | string | Shop URL; may be empty or misidentified if the page is abnormal |
| shopSales | string | Public shop sales text |
| shopName | string | Shop name; may be empty or misidentified if the page is abnormal |
| productUrl | string | Product URL |
| searchPosition | string | Source search position; usually empty for direct URL queries |
| image | string | Main image URL |
| images | array | List of image URLs |
| maxQuantity | integer | Maximum purchasable quantity reported by the page |
| variants | array | Product variants; empty array if there are no variants |
| title | string | Product title |
| description | array | List of description paragraphs |
| deliveryDaysMin / deliveryDaysMax | integer/null | Estimated delivery range in days; may be null or omitted when absent from the source |
| shopReviews | integer | Shop review count |
| reviews | integer | Review count for the current Listing |
| star | string | Current rating; may be an empty string |
| highlightsTags | array | Buyer feedback highlight tags |
| reviewsTags | array | Review tags and frequency objects |
| yearsOnEtsy | string | Public shop tenure on Etsy |
| hasRatingsBadge | boolean | Whether the shop has a ratings badge |
| hasConvosBadge | boolean | Whether the shop has a communication badge |
| hasShippingBadge | boolean | Whether the shop has a shipping badge |
| reviewsScores | object | Dynamic review subcategories; keys and values vary by page |
| category | string | Category breadcrumb |
| price / lowPrice / highPrice / oldPrice | string | Price fields; some may be empty |
| countryShippingFrom | string | Shipping origin country/region |
| currency | string | Currency code |
| moreLikeUrl | string | Similar recommendation link; may be empty |

The API returns only review counts, tags, and aggregate scores, not individual review content.

Example (some product fields, descriptions, images, and `columns` are truncated):

```json
{
  "data": [
    {
      "productId": "1710567856",
      "shopId": "35055979",
      "shopName": "",
      "productUrl": "https://www.etsy.com/listing/1710567856/its-okay-to-make-some-mistakes-shirt",
      "title": "It's Okay To Make Some Mistakes Shirt...",
      "images": ["https://i.etsystatic.com/..."],
      "maxQuantity": 952,
      "variants": [],
      "reviews": 134,
      "star": "",
      "lowPrice": "9.76",
      "highPrice": "32.55",
      "currency": "EUR"
    }
  ],
  "total": 1,
  "costToken": 7000,
  "type": "tableListWorkbenches",
  "columns": [
    {
      "filterable": true,
      "cellType": "text",
      "field": "productId",
      "sortable": true,
      "title": "商品 ID"
    }
  ]
}
```

## Error codes and boundaries

| Condition | Behavior | Recommended action |
|------|------|----------|
| Success | HTTP 200 with the standard envelope above | Parse `data` |
| productUrl is empty or the URL is invalid | Gateway business error | Provide a complete Etsy Listing HTTPS URL |
| Non-Listing page, non-Etsy domain, or excessive path depth | Gateway business error | Check the host and use `/listing/<numericID>` followed by at most one title slug |
| Listing does not exist, is inaccessible, or returns an empty array | Gateway business error; do not treat it as a successful empty list | Verify the link; do not automatically modify it and repeatedly probe |
| Upstream returns multiple valid Listings | Gateway business error | Treat as an upstream result anomaly; this API does not truncate results or return batches |
| 401 | Authentication failed | Follow "Resolve authentication and credit issues" in SKILL.md |
| 402 | Insufficient credits | Follow "Resolve authentication and credit issues" in SKILL.md |
| Timeout or upstream error | Connection error, 5xx, or business error | Inform the user; do not repeatedly retry automatically and incur additional charges |

Changes to public page structure may cause missing fields, empty strings, null values, or occasional misidentification. Callers should present these faithfully without inferring values or silently correcting them.

## curl examples

```bash
API_KEY="${NEXSCOPE_API_KEY:-$NEXSCOPE_API_KEY}"
curl -X POST "${NEXSCOPE_PROXY_BASE:-https://api.nexscope.ai}/api/v1/tools/research/etsy/product/detail" \
  -H "Authorization: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID:-}" \
  -H "MODE_ID: ${MODE_ID:-}" \
  -H "APP_NAME: ${APP_NAME:-}" \
  -d '{
    "productUrl": "https://www.etsy.com/listing/1710567856/its-okay-to-make-some-mistakes-shirt"
  }'
```

---

## Feedback API

> This endpoint is separate from the tool API above. Do not mix the base URLs.

- **POST** `https://skill-api.nexscope.com/api/v1/public/feedback`
- **Content-Type**：`application/json`

```json
{
  "skillName": "nexscope-etsy-product-detail",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "The listing detail matched the requested Etsy product."
}
```

- `skillName`: Always use the `name` from this Skill's frontmatter
- `sentiment`: Choose one of `POSITIVE`, `NEUTRAL`, or `NEGATIVE`
- `category`: Choose one of `BUG`, `COMPLAINT`, `SUGGESTION`, or `OTHER`
- `content`: Briefly describe the user's intent, actual behavior, and reason for the problem or praise
