# Keepa Amazon Price History API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/keepa/productSeries`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, read api_key from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| asin | string | Yes | Amazon Standard Identification Number (ASIN), single ASIN only, max length 1000 |
| domain | string | Yes | Amazon domain ID. Options: `1` (United States), `2` (United Kingdom), `3` (Germany), `4` (France), `5` (Japan), `6` (Canada), `8` (Italy), `9` (Spain), `10` (India), `11` (Mexico), `12` (Brazil) |
| days | integer | No | Limit historical data to this many days, default `90`, max `365` |
| showPrice | integer | No | Set to `1` to return the lowest new price curve in the market |
| showPriceList | integer | No | Set to `1` to return the list/strikethrough price curve |
| showPriceDeal | integer | No | Set to `1` to return the deal/flash sale price curve |
| showPricePrime | integer | No | Set to `1` to return the Prime-exclusive new price curve |
| showPriceFba | integer | No | Set to `1` to return the third-party FBA new price curve |
| showPriceFbm | integer | No | Set to `1` to return the third-party FBM new price curve |
| showPriceCoupon | integer | No | Set to `1` to return the coupon-applied Buy Box price curve |
| showBsrMain | integer | No | Set to `1` to return the main category BSR curve |
| showSellerCount | integer | No | Set to `1` to return the seller count curve |


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
| asin | string | ASIN |
| buyboxPrice | array | Buy Box price (time=timestamp, value=Buy Box price) |
| price | array | Price (time=timestamp, value=price) |
| priceList | array | List/strikethrough price (time=timestamp, value=list price) |
| priceDeal | array | Deal price (time=timestamp, value=deal price) |
| pricePrime | array | Prime price (time=timestamp, value=Prime price) |
| priceFba | array | FBA price (time=timestamp, value=FBA price) |
| priceFbm | array | FBM price (time=timestamp, value=FBM price) |
| priceCoupon | array | Coupon price (time=timestamp, value=coupon price) |
| bsrMain | array | Main category BSR, each element contains `categoryName` (category name) and `points` (time=timestamp, value=ranking) |
| bsrSub | array | Subcategory BSR, each element contains `categoryName` (category name) and `points` (time=timestamp, value=ranking) |
| sellerCount | array | Seller count (time=timestamp, value=seller count) |
| rating | array | Rating (time=timestamp, value=rating) |
| ratingCount | array | Rating count (time=timestamp, value=rating count) |
| monthlySold | array | Child ASIN sales (time=timestamp, value=sales units) |
| costToken | integer | Token consumption |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| - | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/keepa/productSeries \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"asin": "B0DFRJ7WSX", "domain": "1", "days": 90, "showBsrMain": 1, "showPrice": 1, "showSellerCount": 1}'
```

---
