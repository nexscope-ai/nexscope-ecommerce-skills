## NexScope billing

The migrated Skill does not inherit the source platform's point value. This operation consumes NexScope credits. Preserve X-Cost-Token and X-Cost-Credit from the HTTP response headers as server-reported billing metadata, and preserve X-Kong-Trace-Id for diagnostics.

# NexScope proxy contract

The endpoint uses the `/api/v1/tools/research/` prefix. Successful HTTP responses use a NexScope envelope (`code`, `msg`, `data`, `traceId`, and cost metadata); the original business response is nested in `data`.

# TikTok Shop Product Details API Reference

## Request conventions

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/tiktok/shop/product/detail`
- **Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: Bearer <api_key>`; Read api_key from `NEXSCOPE_API_KEY`, falling back to `NEXSCOPE_API_KEY` (if unset, follow "Resolve authentication and credit issues" in SKILL.md)
- **User-Agent**：`NexScope-Skill/2.0`
- **Forwarded headers**: `SESSION_ID`, `MODE_ID`, `APP_NAME` (read each from the environment variable of the same name; use an empty string if unset)
- **Timeout**: 150s

## Request parameters

POST body (JSON):

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| productInput | string | Yes | - | TikTok HTTPS product URL (host must be `tiktok.com` or a subdomain, port must be omitted or `443`, and the path must contain consecutive `product/<19-digitID>` segments), or a 19-digit product ID. Pass the product ID as a string to avoid loss of numeric precision |
| region | string | No | `US` | Uppercase marketplace code: `US`, `GB`, `ID`, `MY`, `TH`, `VN`, `PH`, `SG`, `DE`, `FR`, `IT`, `ES` |

Only the public request parameters listed above are accepted; switching to other response modes is not supported. Each call queries only one product; if the upstream returns a number of valid products other than 1, the API returns a business error.

Minimal request:

```json
{
  "productInput": "1729937400435937604"
}
```

## Response structure

Successful responses use the standard NexScope envelope:

| Field | Type | Description |
|------|------|------|
| errcode | integer | Business status code; `200` indicates success |
| errmsg | string | Business status message; `ok` on success |
| data | array | Normalized product array; exactly 1 item on success |
| total | integer | Always `1` on success |
| costToken | integer | Tokens consumed |
| type | string | Always `tableListWorkbenches` |
| columns | array | Rendering column definitions generated from top-level product fields |

### Product object

Top-level product fields use camelCase; fields within each business group retain the source names:

| Field | Type | Description |
|------|------|------|
| productId | string | Product ID |
| status | integer | Platform product status code; cannot determine sellability on its own |
| title | string | Product title |
| category | object | Category name and ID |
| pricing | object | Currency, sale price, original price, discount, and raw price fields |
| sales | object | Public quantity sold and sales display fields |
| inventory | object | Total stock, SKUs, sales attributes, SKU prices, and default selections |
| media | object | Image URLs and image metadata |
| seller | object | Shop ID, name, rating, region, and available shop fields |
| reviews | object | Public review overview (may be empty) |
| shipping | object | Logistics and delivery modules (may be empty) |
| actions | object | Add-to-cart, purchase, and favorite states |
| additional | object | Promotions, user benefits, and other readable product modules; may be large |

Example (some product and nested fields are truncated):

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "data": [
    {
      "productId": "1729937400435937604",
      "status": 3,
      "title": "CARER SPARK Double Side Multifunctional Facial Cleanser Beauty Device...",
      "category": {"name": "Beauty & Personal Care", "id": "601450"},
      "pricing": {"currency": "USD", "currency_symbol": "$", "sale_price": "$59.99"},
      "sales": {"sold_count": 1},
      "inventory": {
        "total_stock": 0,
        "skus": [{"sku_id": "1730030266154783044", "stock": 0}],
        "sale_props": [{"prop_name": "Color"}]
      },
      "media": {"image_urls": ["https://..."]},
      "seller": {
        "seller_id": "7495351603438586180",
        "name": "CARER SPARK",
        "rating": "3.9",
        "location": "United States of America"
      }
    }
  ],
  "total": 1,
  "costToken": 84000,
  "type": "tableListWorkbenches",
  "columns": [
    {
      "filterable": true,
      "cellType": "text",
      "field": "productId",
      "sortable": true,
      "title": "商品ID"
    }
  ]
}
```

## Error codes and boundaries

| Condition | Behavior | Recommended action |
|------|------|----------|
| Success | HTTP 200 with the standard envelope above | Parse `data` |
| productInput is empty or has an invalid format | Gateway business error | Provide a TikTok HTTPS product link whose path contains `product/<19-digitID>`, or a 19-digit string ID |
| Unsupported region | Gateway business error | Use a marketplace code listed in this document |
| Product does not exist, is inaccessible in the region, or returns an empty product array | Gateway business error; does not return a successful empty list | Verify the product and region; do not automatically poll other regions |
| Upstream returns multiple valid products | Gateway business error | Treat as an upstream result anomaly; this API does not truncate results or return batches |
| 401 | Authentication failed | Follow "Resolve authentication and credit issues" in SKILL.md |
| 402 | Insufficient credits | Follow "Resolve authentication and credit issues" in SKILL.md |
| Timeout or upstream error | Connection error, 5xx, or business error | Inform the user; do not repeatedly retry automatically and incur additional charges |

Response fields may be absent depending on the product, seller, region, and page context. Structured details may still be returned even if the product is delisted or its stock is 0.

## curl examples

```bash
API_KEY="${NEXSCOPE_API_KEY:-$NEXSCOPE_API_KEY}"
curl -X POST "${NEXSCOPE_PROXY_BASE:-https://api.nexscope.ai}/api/v1/tools/research/tiktok/shop/product/detail" \
  -H "Authorization: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID:-}" \
  -H "MODE_ID: ${MODE_ID:-}" \
  -H "APP_NAME: ${APP_NAME:-}" \
  -d '{
    "productInput": "1729937400435937604",
    "region": "US"
  }'
```

---

## Feedback API

> This endpoint is separate from the tool API above. Do not mix the base URLs.

- **POST** `https://skill-api.nexscope.com/api/v1/public/feedback`
- **Content-Type**：`application/json`

```json
{
  "skillName": "nexscope-tiktok-shop-product-detail",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "The product detail matched the requested TikTok Shop listing."
}
```

- `skillName`: Always use the `name` from this Skill's frontmatter
- `sentiment`: Choose one of `POSITIVE`, `NEUTRAL`, or `NEGATIVE`
- `category`: Choose one of `BUG`, `COMPLAINT`, `SUGGESTION`, or `OTHER`
- `content`: Briefly describe the user's intent, actual behavior, and reason for the problem or praise
