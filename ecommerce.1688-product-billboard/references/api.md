# 1688 Product Billboard API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/dld/productBillboard`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| keyWord | string | No | Product search keyword (search keyword must be in Chinese; if not, translate it first), max length 50 |
| date | string | No | Query time. Weekly chart: pass the Sunday date of that week, e.g. `2025-06-15` (up to 90 days); Monthly chart: pass the first day of the month, e.g. `2025-06-01` (up to one year) |
| pageType | integer | No | Billboard type: `2` = weekly, `3` = monthly. Default `3` |
| pageIndex | integer | No | Page number (starting from 1), default `1` |
| pageSize | integer | No | Number of results per page (10-100), default `20` |
| sortField | string | No | Sort field, default `orderCount`. Options: `orderCount` (order count), `saleCount` (units sold), `saleVolume` (estimated sales amount), `offerCreateTime` (listing time), `price` (wholesale price), `consignPrice` (dropship price) |
| sortType | string | No | Sort order: `desc` (descending), `asc` (ascending), default `desc` |
| searchType | integer | No | Product keyword search type: `1` = fuzzy match, `3` = exact match. Default `1` |
| offerType | integer | No | Product tag: `0` = no limit, `2` = new product, `3` = 1688 Select, `4` = cross-border, `5` = customization supported, `6` = store highlight. Default `0` |
| companyType | integer | No | Company type: `0` = no limit, `1` = store, `2` = factory |
| shiLiType | string | No | Seller membership type (multi-select), comma-separated. Options: `superFactory` (Super Factory), `Power` (Power Seller), `TrustPass` (TrustPass member only) |
| beginTpYear | integer | No | Start TrustPass years |
| endTpYear | integer | No | End TrustPass years |
| beginPrice | number | No | Wholesale price (start) |
| endPrice | number | No | Wholesale price (end) |
| beginConsignPrice | number | No | Dropship price (start) |
| endConsignPrice | number | No | Dropship price (end) |
| beginOrderCount | integer | No | Order count (start) |
| endOrderCount | integer | No | Order count (end) |
| beginSaleCount | integer | No | Units sold (start) |
| endSaleCount | integer | No | Units sold (end) |
| beginSaleVolume | number | No | Sales amount (start) |
| endSaleVolume | number | No | Sales amount (end) |
| beginStartQuantity | integer | No | Minimum order quantity (start) |
| endStartQuantity | integer | No | Minimum order quantity (end) |
| beginOfferCreateTime | string | No | Listing time (start), format: `YYYY-MM-DD` |
| endOfferCreateTime | string | No | Listing time (end), format: `YYYY-MM-DD` |
| sendTime | string | No | Delivery time (multi-select), comma-separated. Options: `24` (24 hours), `48` (48 hours), `72` (72 hours) |
| proxyRights | string | No | Dropship rights (multi-select), comma-separated. Options: `4360897` (one-piece dropship with free shipping), `449154` (procure now, pay later) |
| shopService | string | No | Seller services (multi-select), comma-separated. Options: `4057409` (Safe Buy), `888777` (Deep Verification Report) |
| buyerProtections | string | No | Buyer protections (multi-select), comma-separated. Options: `商品包邮` (free shipping), `7天包退货` (7-day free return), `支持运费险` (shipping insurance supported) |
| faceToFaceSupport | string | No | Waybill support (multi-select), comma-separated. Options: `441218` (Taobao), `386434` (Douyin), `422914` (Pinduoduo), `422978` (Xiaohongshu), `386370` (Kuaishou) |
| productIds | string | No | Product IDs, separated by Chinese comma for multiple, max 20 |
| goodsUrl | string | No | Product link URL |


## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Total record count |
| type | string | Render style |
| columns | array | Render columns |
| products | array | Product list (see Product Object below) |

### Product Object

| Field | Type | Description |
|------|------|------|
| offerId | string | Product ID |
| asin | string | Product number |
| title | string | Product title |
| price | number | Wholesale price |
| consignPrice | number | Dropship price |
| currency | string | Currency |
| unit | string | Unit |
| quantityBegin | integer | Minimum order quantity |
| quantityPrices | string | Price range |
| salesOrderCount | integer | Order count (returns corresponding value based on statistical period) |
| salesQuantity | integer | Units sold (returns corresponding value based on statistical period) |
| estimatedSalesAmount | integer | Estimated sales amount (returns corresponding value based on statistical period) |
| dataType | string | Data type: `weeklyData` = weekly data, `monthlyData` = monthly data |
| availableDate | string | Product listing time, format `yyyy-MM-dd HH:mm:ss` |
| deliveryTime | string | Delivery time |
| levelName | string | Category hierarchy name |
| company | string | Store name |
| shopId | string | Store ID |
| shopUrl | string | Store link URL |
| asinUrl | string | Product link URL |
| imageUrl | string | Image URL |
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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/dld/productBillboard \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "keyWord": "手机壳",
    "pageType": 3,
    "date": "2026-03-01",
    "sortField": "orderCount",
    "sortType": "desc",
    "pageSize": 20,
    "pageIndex": 1
  }'
```

---
