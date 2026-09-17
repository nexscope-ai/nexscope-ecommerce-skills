# MPSTATS Ozon Product Search API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/mpstats/ozon/productSearch`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from the environment variable `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON). The following fields are consistent with the backend `OzonItemSearchRequest` DTO (sync date 2026-05-27).

| Parameter | Type | Required | Description |
|------|------|------|------|
| keyword | string | One of two | Russian search keyword, e.g., `кроссовки` (running shoes) |
| productIds | array | One of two | List of Ozon product SKUs (integer or string) |
| startDate | string | No | Statistics start date, format `YYYY-MM-DD`; defaults to one year ago if empty; latest is yesterday |
| endDate | string | No | Statistics end date, format `YYYY-MM-DD`; defaults to yesterday if empty; latest is yesterday |

> **One-of-two constraint**: At least one of `keyword` / `productIds` must be provided; request will be rejected if both are empty.
>
> **No pagination/sorting/filtering**: Upstream returns up to ~36 records per call (official limit). Underlying call uses fixed startRow=0, endRow=100, empty sortModel/filterModel; `page` / `pageSize` / `sortField` / `sortDirection` / `filters` parameters are no longer exposed. For more precise results, narrow keyword/SKU or date window.

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
| msg | string | Message; `ok` for success, error description on failure |
| total | integer | Total matched count |
| products | array | Product list (see details below) |
| columns | array | Rendered column definitions |
| costTime | integer | API latency (milliseconds) |
| costToken | integer | Tokens consumed |
| type | string | Response type |

### products[*] Product Object Fields (10 fields)

Per backend `OzonProductSearchItem` DTO definition (sync date 2026-05-11). **The search endpoint serves identity resolution purposes and does not return business metrics such as price/sales/ratings/inventory/turnover/ranking** — this is a hard contract, not a sparse payload. If you need those metrics:

- Single/batch SKU full card: Use `productDetail` (36 fields, including price, sales, revenue, period comparison, etc.)
- Dimension drill-down: Use `brandProducts` / `categoryProducts` / `sellerProducts` (39-field full product card)

| Field | Type | Description |
|------|------|------|
| productId | integer | SKU ID |
| title | string | Product name (Russian) |
| productPageUrl | string | Product page URL |
| imageUrl | string | Main image URL |
| brand | string | Brand name |
| brandId | integer | Brand ID |
| sellerName | string | Seller name |
| sellerId | integer | Seller ID |
| sourceType | string | Data source identifier, always `ozon` |
| sourceTool | string | Source tool name, always `MPSTATS-Ozon商品搜索` |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Insufficient credits or balance | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/mpstats/ozon/productSearch \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "кроссовки"
  }'
```

## Response Example (abbreviated)

```json
{
  "code": "200",
  "msg": "ok",
  "total": 8721,
  "products": [
    {
      "productId": 1786874757,
      "title": "Кроссовки мужские ...",
      "brand": "Nike",
      "sellerName": "ООО Ромашка",
      "sellerId": 3628678,
      "imageUrl": "https://...",
      "productPageUrl": "https://www.ozon.ru/product/..."
    }
  ],
  "costToken": 1
}
```

---
