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

Under normal conditions, the HTTP status code is always 200. Business success or failure is determined by the errorCode field in the response body (errorCode = 200 indicates success; other values indicate business errors). In cases of unauthorized access, the HTTP status code will be 401, with the corresponding errorCode also being 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| 402 | - | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| Other non-200 values | Business exception | Refer to the `errmsg` field for specific error cause |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/keepa/productSeries \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"asin": "B0DFRJ7WSX", "domain": "1", "days": 90, "showBsrMain": 1, "showPrice": 1, "showSellerCount": 1}'
```

---
