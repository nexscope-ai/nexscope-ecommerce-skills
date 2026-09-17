## Nexscope billing

The migrated Skill does not inherit the source platform's point value. This operation consumes Nexscope credits. Preserve X-Cost-Token and X-Cost-Credit from the HTTP response headers as server-reported billing metadata, and preserve X-Kong-Trace-Id for diagnostics.

# Shopee Product Detail API

## Request

- Endpoint: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/shopee/product/detail`
- Method: `POST`
- Content type: `application/json`
- Authentication: `Authorization: Bearer ${NEXSCOPE_API_KEY}`
- Timeout: 150 seconds
- Forwarded tracing headers: `SESSION_ID`, `MESSAGE_ID`, `MODE_ID`, and `APP_NAME` when present

### Body

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `productUrl` | string | yes | Shopee HTTPS listing URL whose path ends in `-i.<numeric shopId>.<numeric itemId>` |

Supported hosts are `shopee.sg`, `shopee.co.id`, `shopee.com.my`, `shopee.ph`, `shopee.co.th`, `shopee.tw`, `shopee.vn`, and `shopee.com.br`. Ports are omitted or must be `443`.

Only `productUrl` is public input. The service infers the marketplace from the host and must return exactly the product identified by the URL.

```json
{
  "productUrl": "https://shopee.sg/example-i.9641401.29691169956"
}
```

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Response

| Field | Type | Description |
|---|---|---|
| `data` | array | Exactly one product on success |
| `total` | integer | `1` on success |
| `costToken` | integer | Legacy business-body token field; do not use it instead of the `X-Cost-Token` response header |
| `type` | string | Rendering type, normally `tableListWorkbenches` |
| `columns` | array | Rendering column definitions |

Common product fields:

| Group | Fields |
|---|---|
| Identity | `itemId`, `shopId`, `url`, `name`, `brand`, `categoryId`, `categoryBreadcrumb` |
| Media | `image`, `images`, `videos` |
| Pricing | `price`, `priceBeforeDiscount`, `priceMin`, `priceMax`, `discountPercent`, `currency` |
| Demand | `sold`, `soldDisplayed`, `rating`, `ratingCount`, `ratingDistribution`, `likedCount` |
| Inventory | `stock`, `tierVariations`, `models` |
| Shop | `shopName`, `shopRating`, `shopLocation`, `isMall`, `isOfficialShop`, `isShopeeVerified`, `shop` |
| Content | `description`, `attributes`, category data, availability, and condition when supplied |

Less-common top-level product fields are preserved. Fields may be absent or `null`, and some marketplaces return lighter records.

## Errors and invariants

| Condition | Expected handling |
|---|---|
| Missing or malformed `productUrl` | Reject before network access in the client; the gateway also returns a business error |
| Unsupported host or URL form | Use a supported direct listing URL; do not silently rewrite it |
| Removed or market-mismatched listing | Report the gateway error; do not automatically probe other marketplaces |
| Returned IDs differ from the URL | Treat the response as invalid and do not present the wrong product |
| More or fewer than one valid product | Treat as an upstream error |
| HTTP 401 | Check `NEXSCOPE_API_KEY` and authorization |
| HTTP 402 | Report insufficient credits |
| Timeout or 5xx | Report the failure; do not automatically repeat a paid call |

## curl

```bash
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/shopee/product/detail" \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "SESSION_ID: ${SESSION_ID:-}" \
  -H "MESSAGE_ID: ${MESSAGE_ID:-}" \
  -H "MODE_ID: ${MODE_ID:-}" \
  -H "APP_NAME: ${APP_NAME:-}" \
  -d '{"productUrl":"https://shopee.sg/example-i.9641401.29691169956"}'
```
