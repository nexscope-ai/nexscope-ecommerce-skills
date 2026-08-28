# EchoTik TikTok Batch Product Detail API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/batchProductDetail`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| productIds | array&lt;string&gt; | No* | List of product IDs (max 1000). Example: `["1729382310407603945", "1729382310407603946"]` |
| productUrls | array&lt;string&gt; | No* | List of product URLs (max 1000), in the form `https://shop.tiktok.com/us/pdp/<slug>/<productId>?...`; the backend will extract the trailing `productId` from each URL and merge into `productIds`, not mutually exclusive with `productIds` |

\* At least one of `productIds` or `productUrls` must be provided; both can be passed simultaneously. The combined total after merging is at most 1000 products.

## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Record count |
| products | array | Product detail list (see product object below) |
| columns | array | Rendered columns |
| type | string | Render style |
| costToken | integer | Token cost |

### Product Object Fields

> Sales, GMV, livestream, video, creator, and view metrics are returned across multiple periods: `1d / 7d / 15d / 30d / 60d / 90d` and cumulative (total). Price fields are in USD.

**Basic Information**

| Field | Type | Description |
|------|------|------|
| productId | string | Product ID |
| productName | string | Product name |
| imageUrl | string | Product image |
| productImageUrls | array | Product image URL list |
| region | string | Region code |
| sellerId | string | Seller ID |
| categoryId | string | Primary category ID |
| categoryL2Id | string | Secondary category ID |
| categoryL3Id | string | Tertiary category ID |

**Price / Rating / Commission**

| Field | Type | Description |
|------|------|------|
| minPrice | number | Minimum SKU price (USD) |
| maxPrice | number | Maximum SKU price (USD) |
| spuAvgPrice | number | SPU average price (USD) |
| productRating | number | Product rating |
| reviewCount | integer | Review count |
| productCommissionRate | number | Product commission rate |

**Sales (multi-period)**

| Field | Type | Description |
|------|------|------|
| totalSaleCnt | integer | Total sales |
| totalSale1dCnt | integer | Sales in last 1 day |
| totalSale7dCnt | integer | Sales in last 7 days |
| totalSale15dCnt | integer | Sales in last 15 days |
| totalSale30dCnt | integer | Sales in last 30 days |
| totalSale60dCnt | integer | Sales in last 60 days |
| totalSale90dCnt | integer | Sales in last 90 days |

**GMV (multi-period)**

| Field | Type | Description |
|------|------|------|
| totalSaleGmvAmt | number | Total GMV |
| totalSaleGmv1dAmt | number | GMV in last 1 day |
| totalSaleGmv7dAmt | number | GMV in last 7 days |
| totalSaleGmv15dAmt | number | GMV in last 15 days |
| totalSaleGmv30dAmt | number | GMV in last 30 days |
| totalSaleGmv60dAmt | number | GMV in last 60 days |
| totalSaleGmv90dAmt | number | GMV in last 90 days |

**Livestream (multi-period)**

| Field | Type | Description |
|------|------|------|
| totalLiveCnt | integer | Total livestream count |
| totalLive1dCnt | integer | Livestream count in last 1 day |
| totalLive7dCnt | integer | Livestream count in last 7 days |
| totalLive15dCnt | integer | Livestream count in last 15 days |
| totalLive30dCnt | integer | Livestream count in last 30 days |
| totalLive60dCnt | integer | Livestream count in last 60 days |
| totalLive90dCnt | integer | Livestream count in last 90 days |

**Livestream Sales / Livestream GMV (multi-period)**

| Field | Type | Description |
|------|------|------|
| totalLiveSale1dCnt | integer | Livestream sales in last 1 day |
| totalLiveSale7dCnt | integer | Livestream sales in last 7 days |
| totalLiveSale15dCnt | integer | Livestream sales in last 15 days |
| totalLiveSale30dCnt | integer | Livestream sales in last 30 days |
| totalLiveSale60dCnt | integer | Livestream sales in last 60 days |
| totalLiveSale90dCnt | integer | Livestream sales in last 90 days |
| totalLiveSaleGmv1dAmt | integer | Livestream GMV in last 1 day |
| totalLiveSaleGmv7dAmt | integer | Livestream GMV in last 7 days |
| totalLiveSaleGmv15dAmt | integer | Livestream GMV in last 15 days |
| totalLiveSaleGmv30dAmt | integer | Livestream GMV in last 30 days |
| totalLiveSaleGmv60dAmt | integer | Livestream GMV in last 60 days |
| totalLiveSaleGmv90dAmt | integer | Livestream GMV in last 90 days |

**Videos (multi-period)**

| Field | Type | Description |
|------|------|------|
| totalVideoCnt | integer | Total video count |
| totalVideo1dCnt | integer | Video count in last 1 day |
| totalVideo7dCnt | integer | Video count in last 7 days |
| totalVideo15dCnt | integer | Video count in last 15 days |
| totalVideo30dCnt | integer | Video count in last 30 days |
| totalVideo60dCnt | integer | Video count in last 60 days |
| totalVideo90dCnt | integer | Video count in last 90 days |

**Creators (multi-period)**

| Field | Type | Description |
|------|------|------|
| totalIflCnt | integer | Total creator count |
| totalIflVideo1dCnt | integer | Creator video count in last 1 day |
| totalIflVideo7dCnt | integer | Creator video count in last 7 days |
| totalIflVideo15dCnt | integer | Creator video count in last 15 days |
| totalIflVideo30dCnt | integer | Creator video count in last 30 days |
| totalIflVideo60dCnt | integer | Creator video count in last 60 days |
| totalIflVideo90dCnt | integer | Creator video count in last 90 days |
| totalIflLive1dCnt | integer | Creator livestream count in last 1 day |
| totalIflLive7dCnt | integer | Creator livestream count in last 7 days |
| totalIflLive15dCnt | integer | Creator livestream count in last 15 days |
| totalIflLive30dCnt | integer | Creator livestream count in last 30 days |
| totalIflLive60dCnt | integer | Creator livestream count in last 60 days |
| totalIflLive90dCnt | integer | Creator livestream count in last 90 days |

**Views (multi-period)**

| Field | Type | Description |
|------|------|------|
| totalViewsCnt | integer | Total view count |
| totalViews1dCnt | integer | Views in last 1 day |
| totalViews7dCnt | integer | Views in last 7 days |
| totalViews15dCnt | integer | Views in last 15 days |
| totalViews30dCnt | integer | Views in last 30 days |
| totalViews60dCnt | integer | Views in last 60 days |
| totalViews90dCnt | integer | Views in last 90 days |

**Status Indicators and Others**

| Field | Type | Description |
|------|------|------|
| discount | string | Discount info |
| freeShipping | integer | Whether free shipping |
| salesFlag | integer | Primary shipping method |
| salesTrendFlag | integer | Sales trend indicator: 0=stable, 1=rising, 2=falling |
| isSShop | integer | Whether fully managed store |
| offMark | integer | Product delisting indicator |
| firstCrawlDt | string | First crawl date |
| descDetail | string | Product detail description |

## Error Codes

Under normal circumstances, the HTTP status code of the API is always 200. Business success or failure is distinguished by the `errorCode` field in the response body (`errorCode = 200` indicates success, other values indicate business errors). In cases such as unauthorized access, the HTTP status code is 401, and the corresponding `errorCode` is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 402 | Insufficient credits | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Other non-200 values | Business exception | Refer to the `errmsg` field for the specific error reason (e.g., incorrect product ID, product does not exist, etc.) |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/batchProductDetail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "productIds": ["1729382310407603945", "1729382310407603946"]
  }'
```

---
