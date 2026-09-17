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

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Insufficient credits | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |

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
