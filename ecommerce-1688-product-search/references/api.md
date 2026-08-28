# Dianleida 1688 Product Search API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/dld/productSearch`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| keyWord | string | No | - | Search keyword (must be in Chinese, max 50 characters) |
| goodsUrl | string | No | - | Product link URL (mutually exclusive with keyWord) |
| productIds | string | No | - | Product IDs, comma-separated, max 20 |
| cycle | string | No | - | Statistical period: `7` (last 7 days) or `30` (last 30 days) |
| searchType | integer | No | 1 | Search type: 1 = fuzzy match, 3 = exact match |
| sortField | string | No | orderCount30d | Sort field: orderCount7d, saleCount7d, saleVolume7d, orderCount30d, saleCount30d, saleVolume30d, offerCreateTime, price, consignPrice |
| sortType | string | No | desc | Sort order: desc (descending), asc (ascending) |
| pageIndex | integer | No | 1 | Page number (starting from 1) |
| pageSize | integer | No | 20 | Results per page (10-100) |
| beginPrice | number | No | - | Wholesale price (start) |
| endPrice | number | No | - | Wholesale price (end) |
| beginConsignPrice | number | No | - | Dropship price (start) |
| endConsignPrice | number | No | - | Dropship price (end) |
| beginOrderCount | integer | No | - | Order count (start) |
| endOrderCount | integer | No | - | Order count (end) |
| beginSaleCount | integer | No | - | Units sold (start) |
| endSaleCount | integer | No | - | Units sold (end) |
| beginSaleVolume | number | No | - | Sales amount (start) |
| endSaleVolume | number | No | - | Sales amount (end) |
| beginStartQuantity | integer | No | - | Minimum purchase quantity (start) |
| endStartQuantity | integer | No | - | Minimum purchase quantity (end) |
| beginTpYear | integer | No | - | TrustPass years (start) |
| endTpYear | integer | No | - | TrustPass years (end) |
| beginOfferCreateTime | string | No | - | Listing time start (format: YYYY-MM-DD) |
| endOfferCreateTime | string | No | - | Listing time end (format: YYYY-MM-DD) |
| companyType | integer | No | 0 | Company type: 0 = no limit, 1 = store, 2 = factory |
| offerType | integer | No | 0 | Product tag: 0 = no limit, 2 = new product, 3 = 1688 Select, 4 = cross-border, 5 = customization supported, 6 = store highlight |
| shiLiType | string | No | - | Seller type (multi-select, comma-separated): superFactory (Super Factory), Power (Power Seller), TrustPass (TrustPass) |
| sendTime | string | No | - | Delivery time (multi-select, comma-separated): 24, 48, 72 |
| faceToFaceSupport | string | No | - | Waybill support (multi-select, comma-separated): 441218 (Taobao), 386434 (Douyin), 422914 (Pinduoduo), 422978 (Xiaohongshu), 386370 (Kuaishou) |
| proxyRights | string | No | - | Dropship rights (multi-select, comma-separated): 4360897 (one-piece dropship with free shipping), 449154 (procure now, pay later) |
| shopService | string | No | - | Seller services (multi-select, comma-separated): 4057409 (Safe Buy), 888777 (Deep Verification Report) |
| buyerProtections | string | No | - | Buyer protections (multi-select, comma-separated): 商品包邮 (free shipping), 7天包退货 (7-day free return), 支持运费险 (shipping insurance supported) |

## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Total record count |
| type | string | Render style |
| columns | array | Render column definitions |
| products | array | Product list (see fields below) |

### products Array Element Fields

| Field | Type | Description |
|------|------|------|
| offerId | string | Product ID |
| asin | string | Product number |
| title | string | Product title |
| asinUrl | string | Product link URL |
| imageUrl | string | Product image URL |
| price | number | Wholesale price |
| consignPrice | number | Dropship price |
| quantityPrices | string | Price range |
| quantityBegin | integer | Minimum order quantity |
| unit | string | Unit |
| currency | string | Currency |
| salesOrderCount | integer | Order count (by statistical period) |
| salesQuantity | integer | Units sold (by statistical period) |
| estimatedSalesAmount | integer | Estimated sales amount (by statistical period) |
| deliveryTime | string | Delivery time |
| availableDate | string | Product listing time |
| levelName | string | Category hierarchy name |
| company | string | Store name |
| shopId | string | Store ID |
| shopUrl | string | Store link URL |
| dataType | string | Data type: weeklyData (weekly data), monthlyData (monthly data) |
| sourceType | string | Source platform (1688) |
| sourceTool | string | Source tool |

## Error Codes

Under normal circumstances, the HTTP status code is 200. Business success or failure is determined by the `errorCode` field in the response body (errorCode = 200 indicates success; other values indicate business errors). When encountering unauthorized access, the HTTP status code is 401 and the corresponding errorCode is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| 402 | Insufficient credits | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| Other non-200 values | Business error | Refer to the `errmsg` field for specific error details |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/dld/productSearch \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"keyWord": "瑜伽垫", "cycle": "30", "sortField": "saleCount30d", "sortType": "desc", "pageSize": 20}'
```

---
