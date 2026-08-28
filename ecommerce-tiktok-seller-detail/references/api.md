# EchoTik TikTok Seller Detail API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/sellerDetail`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read preferentially from environment variable `NEXSCOPE_API_KEY`, falling back to `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)
- **User-Agent**: `NexScope-Skill/2.0`
- **Timeout**: 120s

## Request Parameters

POST Body (JSON):

  | Parameter | Type | Required | Default | Description |  
|------|------|------|--------|------|
| sellerId | string | Yes | - | TikTok Shop seller ID. Obtainable from the "EchoTik TikTok Seller Search" skill (`nexscope-echotik-list-seller`) results, or from the ID in a known store link. Max length 1000 |

## Response Structure

On success, the response body is a flat object: the top level carries business status fields along with all detail fields for the seller (isomorphic to individual seller objects returned by seller search), plus two render metadata fields `columns` and `type`. **Note: this endpoint has no `total` and no `sellers` list**; the seller fields are directly at the top level.

### Status and Render Fields

| Field | Type | Description |
|------|------|------|
| errcode | integer | Business status code, 200 indicates success (see error codes below) |
| errmsg | string | Business status description |
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

Under normal circumstances, the HTTP status code of the API is always 200. Business success or failure is distinguished by the `errcode` field in the response body (`errcode = 200` indicates success, other values indicate business errors). In cases such as unauthorized access, the HTTP status code is 401, and the corresponding `errcode` is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
| 400 | Parameter validation error | Parameter value is invalid (e.g., `sellerId` is empty or does not exist). Refer to `errmsg` for the specific reason |
| 401 | Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 402 | Insufficient credits | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Other non-200 values | Business exception | Refer to the `errmsg` field for the specific error reason |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Example

### Query a single seller detail

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/sellerDetail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
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
  -H "User-Agent: NexScope-Skill/2.0" \
  -d '{ "region": "US", "sellerSortField": 2, "sortType": 1, "pageSize": 10 }'

# 2) Use the returned sellerId to view the full seller detail
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/sellerDetail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -d '{ "sellerId": "<sellerId returned from the previous step>" }'
```

---
