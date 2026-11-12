# Dianleida 1688 Product Search API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/dld/productSearch`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: Bearer <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` (if not configured, follow the authentication guidance in SKILL.md)

`NEXSCOPE_PROXY_BASE` defaults to `https://api.nexscope.ai`. Invoking this Skill consumes credits. HTTP 401 means Nexscope authentication failed; HTTP 402 means insufficient credits. Do not substitute another buyer/store after marketplace authorization failure or automatically retry paid requests.

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
| buyerProtections | string | No | - | Comma-separated provider-localized labels. English meanings: free shipping, 7-day free returns, shipping insurance. Translate to exact Chinese provider values before sending; these English meanings are not wire enum values. |

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. On both success and failure, the direct fields `code`, `errcode`, `errorCode`, `msg`, `errmsg`, `message`, and `errorMsg` are removed from public `data`. Read the message only from outer `msg`; deeper business fields are preserved, including nested `code` and `status`.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

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

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow the authentication guidance in SKILL.md. |
| Insufficient credits | HTTP 402: follow the authentication guidance in SKILL.md. |

## curl Example

This product-ID lookup can be sent without keyword translation. For an English keyword request, the Agent first translates the keyword into Simplified Chinese, then sends the prepared payload.

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE:-https://api.nexscope.ai}/api/v1/tools/research/dld/productSearch \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"productIds": "805578065498", "cycle": "30", "sortField": "saleCount30d", "sortType": "desc", "pageSize": 20}'
```

---

## API Key request rate and retries

All API Keys of one Nexscope user share the public API execution request-rate allowance, measured in any rolling 1-second window. The allowed RPS depends on that user's entitlements; it is not a universal 1 RPS. One Skill operation may issue multiple public API requests, each of which uses the allowance.

HTTP 429 with Nexscope outer code `13012` means request-rate exhaustion: honor the response's `Retry-After`. Outer code `13013` means concurrent-request exhaustion, not rate exhaustion; honor `Retry-After` when supplied. Check the HTTP status and outer JSON code separately. Do not automatically replay writes or requests with uncertain outcomes; first reconcile the operation's state.
