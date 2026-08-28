# EchoTik TikTok Product Search API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/listProduct`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| keyword | string | No | Product keyword (please translate to the local language). Max length 1000 |
| region | string | No | Region, default `US`. Options: US (United States), ID (Indonesia), TH (Thailand), PH (Philippines), MY (Malaysia), VN (Vietnam), GB (United Kingdom), MX (Mexico), SG (Singapore), SA (Saudi Arabia), BR (Brazil), ES (Spain), JP (Japan), DE (Germany), IT (Italy), FR (France) |
| categoryKeywordCN | string | No | Product category (please enter in Chinese). Max length 1000 |
| minTotalSaleCnt | integer | No | Total sales (minimum) |
| maxTotalSaleCnt | integer | No | Total sales (maximum) |
| minTotalSale30dCnt | integer | No | 30-day sales (minimum) |
| maxTotalSale30dCnt | integer | No | 30-day sales (maximum) |
| minTotalSaleGmvAmt | string | No | Product total GMV (minimum). Max length 1000 |
| maxTotalSaleGmvAmt | string | No | Product total GMV (maximum). Max length 1000 |
| minTotalSaleGmv30dAmt | string | No | Product total GMV (30-day) (minimum). Max length 1000 |
| maxTotalSaleGmv30dAmt | string | No | Product total GMV (30-day) (maximum). Max length 1000 |
| minSpuAvgPrice | number | No | SPU average price (minimum) |
| maxSpuAvgPrice | number | No | SPU average price (maximum) |
| minProductRating | number | No | Product rating (minimum) |
| maxProductRating | number | No | Product rating (maximum) |
| minReviewCount | integer | No | Review count (minimum) |
| maxReviewCount | integer | No | Review count (maximum) |
| minProductCommissionRate | number | No | Product commission rate (minimum). Input as percentage will be automatically converted to decimal, e.g., 5%->0.05 |
| maxProductCommissionRate | number | No | Product commission rate (maximum). Input as percentage will be automatically converted to decimal, e.g., 5%->0.05 |
| minTotalIflCnt | integer | No | Promoting creator count (minimum) |
| maxTotalIflCnt | integer | No | Promoting creator count (maximum) |
| minTotalVideoCnt | integer | No | Promotional video count (minimum) |
| maxTotalVideoCnt | integer | No | Promotional video count (maximum) |
| minTotalViewsCnt | integer | No | Promotional view count (minimum) |
| maxTotalViewsCnt | integer | No | Promotional view count (maximum) |
| minFirstCrawlDt | integer | No | Product listing time (minimum), format YYYYMMDD (e.g., 20200101 represents 2020-01-01) |
| maxFirstCrawlDt | integer | No | Product listing time (maximum), format YYYYMMDD |
| saleDays | integer | No | Days the product has been on sale, unit is days |
| productSortField | integer | No | Sort field: 1=total sales, 2=total GMV, 3=SPU average price, 4=7-day sales, 5=30-day sales, 6=7-day GMV, 7=30-day GMV. Default `1` |
| sortType | integer | No | Sort direction: 0=ascending, 1=descending. Default `1` |
| pageNum | integer | No | Page number. Default `1` |
| pageSize | integer | No | Items per page. Default `50` |


## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Record count |
| products | array | Product information list (see below) |
| columns | array | Rendered columns |
| type | string | Render style |
| costToken | integer | Token cost |

### Product Object Fields

| Field | Type | Description |
|------|------|------|
| productId | string | Product unique identifier ID |
| productName | string | Product name |
| title | string | Product name |
| imageUrl | string | Product image URL |
| coverUrl | string | Cover image URL list |
| productImageUrls | array | Product image URL list |
| categoryName | string | Product category name |
| categoryIds | array | Product category ID list |
| region | string | Region code |
| currency | string | Currency |
| price | number | Product price |
| minPrice | number | Minimum price |
| maxPrice | number | Maximum price |
| spuAvgPrice | number | SPU average price |
| productRating | number | Product rating |
| reviewCount | integer | Review count |
| ratings | integer | Review count |
| productCommissionRate | number | Product commission rate |
| totalSaleCnt | integer | Total sales |
| totalSale1dCnt | integer | Total sales in 1 day |
| totalSale7dCnt | integer | Total sales in 7 days |
| totalSale15dCnt | integer | Total sales in 15 days |
| totalSale30dCnt | integer | Total sales in 30 days |
| totalSale60dCnt | integer | Total sales in 60 days |
| totalSale90dCnt | integer | Total sales in 90 days |
| monthlySalesUnits | integer | Monthly sales |
| totalSaleGmvAmt | number | Total GMV |
| totalSaleGmv1dAmt | number | Total GMV in 1 day |
| totalSaleGmv7dAmt | number | Total GMV in 7 days |
| totalSaleGmv15dAmt | number | Total GMV in 15 days |
| totalSaleGmv30dAmt | number | Total GMV in 30 days |
| totalSaleGmv60dAmt | number | Total GMV in 60 days |
| totalSaleGmv90dAmt | number | Total GMV in 90 days |
| firstCrawlDt | integer | Listing date |
| availableDate | string | Listing time (timestamp) |
| discount | string | Discount info |
| freeShippingText | string | Whether free shipping |
| offMarkText | string | Whether there is a discount mark |
| salesFlagText | string | Selling method |
| salesTrendFlagText | string | Sales trend indicator |
| isSShopText | string | Whether S store |
| salePropsInfo | array | Sales property info (product specifications) |
| sourceTool | string | Source tool |
| sourceType | string | Product source |
| asin | string | Product ID |

## Error Codes

Under normal circumstances, the HTTP status code of the API is always 200. Business success or failure is distinguished by the `errorCode` field in the response body (`errorCode = 200` indicates success, other values indicate business errors). In cases such as unauthorized access, the HTTP status code is 401, and the corresponding `errorCode` is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
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

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/listProduct \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "phone case",
    "region": "US",
    "minTotalSale30dCnt": 1000,
    "productSortField": 5,
    "sortType": 1,
    "pageSize": 20
  }'
```

---
