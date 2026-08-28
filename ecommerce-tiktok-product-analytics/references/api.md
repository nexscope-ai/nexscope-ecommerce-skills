# Kalodata TikTok Product Search & Detail API Reference

## API Specification

- **Request URL (Product Rank)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/product/detail`
- **Request URL (Product Detail)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/product/detail`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read preferentially from environment variable `NEXSCOPE_API_KEY`, falling back to `NEXSCOPE_API_KEY` (if not configured, follow the **Resolving Authentication and Credit Issues** section in SKILL.md)
- **User-Agent**: `NexScope-Skill/2.0`
- **Timeout**: 120s

## Request Parameters

### Product Rank: `POST /kalodata/product/rank`

POST Body (JSON), all parameters are optional:

| Parameter | Type | Required | Description |
|------|------|------|------|
| region | string | No | TikTok Shop market region code, e.g., `US`. If not specified, defaults to the server default (usually US) |
| dateRange | string | No | Relative date range, e.g., `last7Day`, `last30Day` |
| currency | string | No | Currency code, e.g., `USD` |
| language | string | No | Return language, e.g., `zh-CN`, `en-US` |
| sortField | object | No | Sort specification object; omitted to use default ranking |
| pageNumber | integer | No | Page number, range 1-5 |
| pageSize | integer | No | Items per page, range 5-100 |

> This endpoint is used to browse product rankings and does not support keyword search. Available sort fields for `sortField` are subject to what the gateway actually accepts; if an unsupported sort field is passed, handle according to the server `errmsg` and do not fabricate field names or attempt bypass logic.

### Product Detail: `POST /kalodata/product/detail`

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| productId | string | Yes | TikTok product ID, e.g., `1729508370969629931` (string format, to avoid large integer precision loss), obtainable from the `product_id` in the product rank response |
| region | string | No | Region/market code, e.g., `US` |
| dateRange | string | No | Time range, e.g., `last7Day` (last 7 days), `last30Day` (last 30 days) |
| language | string | No | Return language, e.g., `zh-CN`, `en-US` |
| currency | string | No | Currency unit, e.g., `USD` |

> `productId` is required; the gateway will return a business error if it is missing. Other parameters are optional and default to the gateway defaults when omitted. `region`/`dateRange`/`currency` determine the scope and unit of currency fields (`revenue`, `unit_price`, `min_price`, `max_price`, and channel revenue breakdowns). This endpoint does not support searching products by keyword/title; you must first discover products using the rank endpoint and obtain `product_id`, then query details with `productId`.

## Response Structure

### Common Top-Level Fields

| Field | Type | Description |
|------|------|------|
| errcode | integer | Business status code, 200 indicates success |
| data | array | Rank or detail data |
| costToken | integer | Tokens consumed for this call, typically 14000 |
| errmsg | string | Status message, `ok` on success |

> The top-level fields are `errcode` / `data` / `costToken` / `errmsg`. **The actual response does not return `total`** (nor pagination metadata such as total page count); the product list is in the `data` array. For detail, `data` is always a 1-element array.

### Product Rank Fields (each element in the `data` array)

| Field | Type | Description |
|------|------|------|
| product_id | string | Product ID (string format, to avoid large integer precision loss); used as `productId` to query details |
| product_name | string | Product title |
| unit_price | number | Unit price (currency depends on `region`, e.g., `US` means USD) |
| sales_volumn | integer | Sales volume (units). Note: the field name is spelled `sales_volumn` (as-is, not `volume`). Use this exact name when extracting with `jq`/`ConvertFrom-Json` |
| revenue | number | Total revenue (GMV), = `video_revenue` + `live_revenue` + `showcase_revenue` |
| video_revenue | number | Video channel revenue |
| live_revenue | number | Livestream channel revenue |
| showcase_revenue | number | Showcase/display channel revenue |
| revenue_growth_rate | number | Revenue growth rate (percentage, e.g., `27.94` means 27.94%) |
| commission_rate | number | Commission rate (percentage, e.g., `25.0` means 25%; **not basis points**) |
| launch_date | string | Launch date (`YYYY-MM-DD`) |

> The actual response does not include `total`, nor does it have pagination metadata such as total page count. When paging is needed, keep requesting the next page until a page returns fewer items than `pageSize` or page 5 is reached.

### Product Detail Fields (`data` is always a 1-element array)

| Field | Type | Description |
|------|------|------|
| product_id | string | Product unique ID (string, to avoid large integer precision loss) |
| product_name | string | Product name |
| product_region | string | Product region/market (e.g., `us`) |
| product_shop_id | string | Belonged shop ID |
| pri_cate_id | string | Primary category ID |
| sec_cate_id | string | Secondary category ID |
| ter_cate_id | string | Tertiary category ID |
| unit_price | number | Unit price (in the requested `currency`) |
| min_price | number | Minimum price (in the requested `currency`) |
| max_price | number | Maximum price (in the requested `currency`) |
| revenue | number | Total revenue / GMV (in the requested `currency`) |
| sales_volumn | integer | Sales volume (note the field is spelled `volumn`) |
| commission_rate | number | Commission rate, **direct percentage** (25.0 means 25%) |
| product_review_count | integer | Product review count |
| launch_date | string | Launch date (`YYYY-MM-DD`) |
| delivery_type | string | Delivery method (e.g., `local`) |
| video_number | integer | Associated video count |
| video_revenue | number | Revenue from videos (in the requested `currency`) |
| live_number | integer | Associated livestream count |
| live_revenue | number | Revenue from livestreams (in the requested `currency`) |
| shopping_mall_revenue | number | Mall revenue (in the requested `currency`) |
| creator_number | integer | Associated creator count |

> **Revenue channel breakdown**: Detail `revenue` = `video_revenue` + `live_revenue` + `shopping_mall_revenue`.
> **Field spelling note**: `sales_volumn` is spelled `volumn` (not `volume`). Use the exact field name when extracting with `jq` / `ConvertFrom-Json`; `commission_rate` is a direct percentage (25.0 = 25%).

## Real Response Examples

### Product Rank

```json
{
  "errcode": 200,
  "data": [
    {
      "revenue_growth_rate": 27.94,
      "revenue": 620518.0,
      "video_revenue": 592599.0,
      "sales_volumn": 33872,
      "product_id": "1729508370969629931",
      "showcase_revenue": 311.0,
      "commission_rate": 15.0,
      "launch_date": "2026-03-18",
      "unit_price": 18.32,
      "product_name": "[NEW] [medicube] PDRN Pink Collagen Volume Multi Balm | All In One Volufiline, PDRN, NAD Stick for Youthful-Looking, Helping Look of Fine Lines, Firming Care, Anti-Aging Care | For Under-Eyes, Neck, Forehead, Smile Lines, Lip Care | Korean Skincare",
      "live_revenue": 27608.0
    }
  ],
  "costToken": 14000,
  "errmsg": "ok"
}
```

### Product Detail

```json
{
  "errcode": 200,
  "data": [
    {
      "sec_cate_id": "848776",
      "product_region": "us",
      "creator_number": 4164,
      "video_revenue": 592599.0,
      "sales_volumn": 33872,
      "video_number": 8271,
      "ter_cate_id": "601611",
      "unit_price": 18.32,
      "product_name": "[NEW] [medicube] PDRN Pink Collagen Volume Multi Balm | All In One Volufiline, PDRN, NAD Stick for Youthful-Looking, Helping Look of Fine Lines, Firming Care, Anti-Aging Care | For Under-Eyes, Neck, Forehead, Smile Lines, Lip Care | Korean Skincare",
      "revenue": 620518.0,
      "max_price": 19.0,
      "min_price": 19.0,
      "delivery_type": "local",
      "product_review_count": 42277,
      "product_id": "1729508370969629931",
      "pri_cate_id": "601450",
      "live_number": 2053,
      "commission_rate": 15.0,
      "launch_date": "2026-03-18",
      "shopping_mall_revenue": 311.0,
      "product_shop_id": "7495514739648989419",
      "live_revenue": 27608.0
    }
  ],
  "costToken": 14000,
  "errmsg": "ok"
}
```

> In the example above, `revenue` (620518.0) = `video_revenue` (592599.0) + `live_revenue` (27608.0) + `shopping_mall_revenue` (311.0), with the channel breakdown being self-consistent. The complete JSON saved by the script contains all fields. It is recommended to use `jq` or `ConvertFrom-Json` to extract as needed.

## Error Codes

Under normal circumstances, the HTTP status code of the API is always 200. Business success or failure is distinguished by the `errcode` field in the response body (`errcode = 200` indicates success, other values indicate business errors). Unauthorized cases may return HTTP 401, with the corresponding `errcode` also being 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally. Note: legally valid but data-less requests (e.g., unsupported `region`) may return 200 but the response **does not contain the `data` field** (empty result), and tokens will still be consumed |
| 401 | Authentication failed | HTTP 401 or authorized error; follow the **Resolving Authentication and Credit Issues** section in SKILL.md |
| 402 | Insufficient credits | HTTP 402: follow the **Resolving Authentication and Credit Issues** section in SKILL.md |
| 501 | Upstream call failed / parameter error | Two forms: (1) `errmsg` like `Call to Kalodata API failed: Kalodata API HTTP 5xx: ` (e.g., 522/554, transient upstream Kalodata error), retry 1-2 times with the same parameters without changing them; if it persists, contact the gateway side to confirm Kalodata upstream configuration (e.g., whether server-side `KALODATA_SECRET_KEY` is configured). (2) `errmsg` like parameter validation error (e.g., `page_number range is 1-5`, `productId` missing or invalid), fix the parameter and retry |
| Other non-200 values | Business exception | Refer to the `errmsg` field for the specific error reason |

Error response example (authentication failed):

```json
{
  "errcode": 401,
  "errmsg": "authorized error"
}
```

Upstream transient error example (retry with same parameters, no additional cost):

```json
{
  "errcode": 501,
  "errmsg": "Call to Kalodata API failed: Kalodata API HTTP 522: "
}
```

Parameter out-of-bounds example (validation happens before billing, no cost):

```json
{
  "errcode": 501,
  "errmsg": "page_number range is 1-5, current: 99"
}
```

## curl Example

### Product Rank

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/product/detail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -d '{
    "region": "US",
    "dateRange": "last7Day",
    "pageSize": 20,
    "pageNumber": 1,
    "currency": "USD"
  }'
```

### Product Detail

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/product/detail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -d '{
    "productId": "1729508370969629931",
    "region": "US",
    "dateRange": "last7Day",
    "currency": "USD"
  }'
```
