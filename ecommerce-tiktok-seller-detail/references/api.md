# EchoTik TikTok Seller Detail API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/sellerDetail`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read preferentially from environment variable `NEXSCOPE_API_KEY`, falling back to `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)
- **User-Agent**: `Nexscope-Skill/2.0`
- **Timeout**: 120s

## Request Parameters

POST Body (JSON):

  | Parameter | Type | Required | Default | Description |  
|------|------|------|--------|------|
| sellerId | string | Yes | - | TikTok Shop seller ID. Obtainable from the "EchoTik TikTok Seller Search" skill (`nexscope-echotik-list-seller`) results, or from the ID in a known store link. Max length 1000 |

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Response Structure

On success, the response body is a flat object: the top level carries business status fields along with all detail fields for the seller (isomorphic to individual seller objects returned by seller search), plus two render metadata fields `columns` and `type`. **Note: this endpoint has no `total` and no `sellers` list**; the seller fields are directly at the top level.

### Status and Render Fields

| Field | Type | Description |
|------|------|------|
| costToken | integer | Token cost |
| columns | array | Render column definitions (display metadata) |
| type | string | Render style (e.g., `tableListWorkbenches`) |

### Seller Detail Fields

| Field | Type | Description |
|------|------|------|
| sellerId | string | Store ID |
| sellerName | string | Store name |
| sellerLink | string | Store link |
| coverUrl | string | Store cover image URL |
| region | string | Region |
| categoryId | string | Primary category ID |
| categoryL2Id | string | Secondary category ID |
| categoryL3Id | string | Tertiary category ID |
| totalSaleCnt | integer | Total sales |
| totalSale1dCnt | integer | Sales in last 1 day (increment) |
| totalSale7dCnt | integer | Sales in last 7 days (increment) |
| totalSale30dCnt | integer | Sales in last 30 days (increment) |
| totalSale90dCnt | integer | Sales in last 90 days (increment) |
| totalSaleGmvAmt | number | Total GMV |
| totalSaleGmv1dAmt | number | GMV in last 1 day (increment) |
| totalSaleGmv7dAmt | number | GMV in last 7 days (increment) |
| totalSaleGmv30dAmt | number | GMV in last 30 days (increment) |
| totalSaleGmv90dAmt | number | GMV in last 90 days (increment) |
| followersCount | integer | Follower count |
| rating | number | Rating |
| reviewCount | integer | Review count |
| positiveFeedbackRate | number | Positive feedback rate |
| responseRate | number | Response rate |
| deliveryRate | integer | Delivery rate |
| totalProductCnt | integer | Historical product count in store (including delisted) |
| totalCrawlProductCnt | integer | Current product count in store |
| spuAvgPrice | number | Average SKU price across the store |
| minPrice | integer | Minimum price |
| maxPrice | integer | Maximum price |
| totalIflCnt | integer | Total promoting creator count |
| totalVideoCnt | integer | Total promotional video count |
| totalLiveCnt | integer | Total livestream count |
| salesFlagText | string | Primary selling method (video sales / livestream sales) |
| salesTrendFlagText | string | Sales trend (rising / falling / stable) |
| shopIdentityLabel | string | Store identity (e.g., OFFICIAL SHOP) |
| shopTypeText | string | Whether a brand store (Yes / No) |
| fromFlagText | string | Cross-border identifier (local / cross-border) |
| productCategoryList | string | Product categories (JSON string, containing category_name / category_id) |
| mostProductCategoryList | string | TOP1 product category (JSON string) |
| firstCrawlDt | integer | Estimated listing time, in yyyyMMdd format (e.g., 20240504 represents 2024-05-04) |
| userId | string | Creator UID |
| sourceType | string | Product source (e.g., Tiktok) |
| sourceTool | string | Source tool (e.g., EchoTik-Seller Detail) |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Parameter validation error | Parameter value is invalid (e.g., `sellerId` is empty or does not exist). Refer to `msg` for the specific reason |
| Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Insufficient credits | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |

## curl Example

### Query a single seller detail

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/sellerDetail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -d '{
    "sellerId": "7495514739648989419"
  }'
```

### Combined usage with seller search

First use seller search to list sellers in a region, take their `sellerId`, then call this endpoint:

```bash
# 1) List top GMV sellers in the US (see nexscope-echotik-list-seller)
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/sellerDetail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -d '{ "region": "US", "sellerSortField": 2, "sortType": 1, "pageSize": 10 }'

# 2) Use the returned sellerId to view the full seller detail
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/sellerDetail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -d '{ "sellerId": "<sellerId returned from the previous step>" }'
```

---
