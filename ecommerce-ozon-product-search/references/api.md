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

## Response Structure

| Field | Type | Description |
|------|------|------|
| code | string | Return code (string), `"200"` indicates success |
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

Under normal circumstances, the HTTP status code is 200. Business success or failure is distinguished by `code` / `errcode` (`200` success).

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse `products` field normally |
| 401 | Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 402 | Insufficient credits or balance | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Other non-200 values | Business exception | Check `errmsg` / `msg` for specific reason; common causes include both keyword/productIds missing, date beyond yesterday, non-Russian keyword, etc. |

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
