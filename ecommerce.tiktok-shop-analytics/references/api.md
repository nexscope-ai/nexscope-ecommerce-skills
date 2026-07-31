# Kalodata TikTok Shop Search & Detail API Reference

## API Specification

- **Request URL (Shop Rank)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/shop/detail`
- **Request URL (Shop Detail)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/shop/detail`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read preferentially from environment variable `NEXSCOPE_API_KEY`, falling back to `NEXSCOPE_API_KEY` (if not configured, follow the **Resolving Authentication and Credit Issues** section in SKILL.md)
- **User-Agent**: `NexScope-Skill/2.0`
- **Timeout**: 120s

## Request Parameters

### Shop Rank: `POST /kalodata/shop/rank`

POST Body (JSON), all parameters are optional:

| Parameter | Type | Required | Description |
|------|------|------|------|
| region | string | No | Region/market code, e.g., `US`. Max length 1000 |
| dateRange | string | No | Time range, e.g., `last7Day` (last 7 days), `last30Day` (last 30 days). Max length 1000 |
| pageNumber | integer | No | Page number, value range 1-5 (out of range returns `errcode 501`) |
| pageSize | integer | No | Items per page, value range 5-100 |
| language | string | No | Return language, e.g., `zh-CN`, `en-US`. Max length 1000 |
| currency | string | No | Currency unit, e.g., `USD`. Max length 1000 |
| sortField | object | No | Sort criteria; pass an empty object `{}` for default rank order when not sorting |

> Default sort is by `revenue` (GMV) descending, with each record carrying a `rank` position. Available sort fields are subject to what the gateway actually accepts; if an unsupported sort field is passed, fall back to default sort and do not attempt other bypass logic.

### Shop Detail: `POST /kalodata/shop/detail`

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| shopId | string | Yes | TikTok shop unique ID (string, to avoid large integer precision loss), e.g., `7495514739648989419`. Obtainable from the `shop_id` field in the shop rank response |
| region | string | No | Region/market code, e.g., `US`. Max length 1000 |
| dateRange | string | No | Time range, e.g., `last7Day`, `last30Day`. Max length 1000 |
| language | string | No | Return language, e.g., `zh-CN`, `en-US`. Max length 1000 |
| currency | string | No | Currency unit, e.g., `USD`. Max length 1000 |

> `shopId` is required; omitting it will not produce valid results. This endpoint does not support searching by keyword/shop name; you must first discover shops using the shop rank endpoint and obtain `shop_id`, then query details with `shopId`. This endpoint has no pagination; the response `data` is always a 1-element array (single shop detail).

## Response Structure

### Common Top-Level Fields

| Field | Type | Description |
|------|------|------|
| errcode | integer | Business status code, 200 indicates success |
| data | array | Shop rank list (rank) or 1-element detail array (detail) |
| costToken | integer | Tokens consumed for this call, fixed at 14000 |
| errmsg | string | Status message, `ok` on success |

> `outputSchema` may declare a `total` field, but **the actual response does not contain `total`**, nor does it have pagination metadata such as total page count. When paging is needed, keep requesting the next page until a page returns fewer items than `pageSize`. The detail response `data` is always a 1-element array.

> **Detail field names differ from the shop RANK endpoint**: Detail uses `self_account_revenue` (RANK uses `self_promotion_revenue`), `shoppingmall_revenue` (**no underscore** between `shopping` and `mall`, RANK uses `shopping_mall_revenue`), `seller_type` (RANK uses `shop_type`). Detail also returns `creator_number`/`video_number`/`live_number`/`product_number` (not returned by RANK), and does not return `rank`/`revenue_growth_rate`/`on_sell_product_count`. When extracting data, always use the exact field names for the corresponding endpoint.

### Shop Rank Fields (each element in the `data` array)

| Field | Type | Description |
|------|------|------|
| rank | integer | Rank position (1 is highest) |
| shop_name | string | Shop name |
| shop_id | string | Shop unique ID (string, to avoid large integer precision loss) |
| shop_type | string | Shop type (e.g., `BRAND`) |
| revenue | number | Total revenue / GMV (in the requested `currency`) |
| sales_volumn | integer | Sales volume (note the field is spelled `volumn`) |
| on_sell_product_count | integer | Products currently on sale |
| unit_price | number | Unit price (in the requested `currency`) |
| revenue_growth_rate | number | Revenue growth rate (%, can be positive or negative) |
| self_promotion_revenue | number | Self-operated/self-promoted revenue |
| affiliate_revenue | number | Affiliate distribution revenue |
| shopping_mall_revenue | number | Mall revenue |

> **Revenue channel breakdown (rank)**: `revenue` = `self_promotion_revenue` + `affiliate_revenue` + `shopping_mall_revenue`.

### Shop Detail Fields (`data` is always a 1-element array)

| Field | Type | Description |
|------|------|------|
| shop_id | string | Shop unique ID (string, to avoid large integer precision loss) |
| shop_name | string | Shop name |
| seller_type | string | Shop/seller type (e.g., `BRAND`) -- detail uses `seller_type`, not `shop_type` |
| region | string | Region/market (e.g., `US`) |
| revenue | number | Total revenue / GMV (in the requested `currency`) |
| sales_volumn | integer | Sales volume (note the field is spelled `volumn`) |
| product_number | integer | Products currently on sale |
| unit_price | number | Unit price (in the requested `currency`) |
| self_account_revenue | number | Self-operated/self-broadcast revenue -- detail uses `self_account_revenue`, not `self_promotion_revenue` |
| affiliate_revenue | number | Affiliate distribution revenue |
| shoppingmall_revenue | number | Mall revenue (note: **no underscore** between `shopping` and `mall`) |
| creator_number | integer | Creator collaborations |
| video_number | integer | Associated video count |
| live_number | integer | Associated livestream count |

> **Revenue channel breakdown (detail)**: `revenue` = `self_account_revenue` + `affiliate_revenue` + `shoppingmall_revenue`. Individual components may be independently rounded (e.g., `shoppingmall_revenue` may return `10431.0` in the detail endpoint while the rank endpoint returns `10431.39`), so the sum of the three may differ slightly from `revenue`; do not treat it as an exact equality.

## Real Response Examples

### Shop Rank (`region=US, dateRange=last7Day, pageSize=5`, excerpt of first 2 records)

```json
{
  "errcode": 200,
  "data": [
    {
      "shop_id": "7495514739648989419",
      "revenue_growth_rate": 16.98,
      "revenue": 4036424.77,
      "sales_volumn": 142080,
      "on_sell_product_count": 146,
      "self_promotion_revenue": 133774.9,
      "affiliate_revenue": 3892218.48,
      "shop_type": "BRAND",
      "rank": 1,
      "shop_name": "medicube US Store",
      "unit_price": 28.41,
      "shopping_mall_revenue": 10431.39
    },
    {
      "shop_id": "7495830785034323995",
      "revenue_growth_rate": -4.78,
      "revenue": 2487949.36,
      "sales_volumn": 88156,
      "on_sell_product_count": 147,
      "self_promotion_revenue": 92771.54,
      "affiliate_revenue": 2383899.26,
      "shop_type": "BRAND",
      "rank": 2,
      "shop_name": "Dr.Melaxin",
      "unit_price": 28.22,
      "shopping_mall_revenue": 11278.56
    }
  ],
  "costToken": 14000,
  "errmsg": "ok"
}
```

### Shop Detail (`shopId=7495514739648989419, region=US, dateRange=last7Day`)

```json
{
  "errcode": 200,
  "data": [
    {
      "self_account_revenue": 133774.9,
      "creator_number": 25367,
      "sales_volumn": 142080,
      "affiliate_revenue": 3892218.48,
      "video_number": 66199,
      "shop_name": "medicube US Store",
      "unit_price": 28.41,
      "shoppingmall_revenue": 10431.0,
      "product_number": 158,
      "shop_id": "7495514739648989419",
      "revenue": 4036424.77,
      "seller_type": "BRAND",
      "live_number": 8433,
      "region": "US"
    }
  ],
  "costToken": 14000,
  "errmsg": "ok"
}
```

> The complete JSON saved by the script contains all fields. It is recommended to use `jq` or `ConvertFrom-Json` to extract as needed.

## Error Codes

Under normal circumstances, the HTTP status code is 200. Business success or failure is distinguished by the `errcode` field in the response body. Unauthorized cases may return HTTP 401, with the corresponding `errcode` also being 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
| 400 | Parameter missing/invalid | For example, when `shopId` is missing in detail, returns `errmsg: shopId is a required parameter`; fix according to `errmsg` and retry |
| 401 | Authentication failed | HTTP 401 or authorized error; follow the **Resolving Authentication and Credit Issues** section in SKILL.md |
| 402 | Insufficient credits | Follow the **Resolving Authentication and Credit Issues** section in SKILL.md |
| 501 | Upstream call failed / parameter out of bounds | Two forms: (1) `errmsg` like `Call to Kalodata API failed: Kalodata API HTTP 554: ` (transient upstream Kalodata error), retry 1-2 times with the same parameters without changing them. (2) `errmsg` like `page_number range is 1-5, current: 999` (rank parameter out of bounds), fix the parameter and retry |
| Other non-200 values | Business exception | Refer to the `errmsg` field for the specific error reason |

Error response example:

```json
{
  "errcode": 501,
  "errmsg": "page_number range is 1-5, current: 999"
}
```

## curl Example

### Shop Rank

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/shop/detail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -d '{
    "region": "US",
    "dateRange": "last7Day",
    "pageSize": 10,
    "pageNumber": 1
  }'
```

### Shop Detail

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/shop/detail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -d '{
    "shopId": "7495514739648989419",
    "region": "US",
    "dateRange": "last7Day",
    "currency": "USD"
  }'
```
