# Amazon Image Search API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/searchByImage`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`; api_key is read from the `nexscope_AGENT_API_KEY` environment variable (or `nexscopeAGENT_API_KEY`) (if unset, follow **## Resolving Authentication and Credits Issues** in SKILL.md)

## Request Parameters

POST Body（JSON）：

| Parameter | Type | Required | Description |
|------|------|------|------|
| imageUrl | string | Yes | Image URL; ensure it is valid. Maximum length: 1000 |
| amazonDomain | string | Yes | Amazon marketplace. Only these marketplaces are supported: United States (`amazon.com`), United Kingdom (`amazon.co.uk`), Germany (`amazon.de`), France (`amazon.fr`), Italy (`amazon.it`), Spain (`amazon.es`), Japan (`amazon.co.jp`), and India (`amazon.in`). Default: `amazon.com` |
| sort | string | No | Sort by price, rating, or review count. Values: `default` (default), `price-asc-rank` (price low to high), `price-desc-rank` (price high to low), `rating-asc-rank` (rating low to high), `rating-desc-rank` (rating high to low), `ratings-asc-rank` (review count low to high), `ratings-desc-rank` (review count high to low) |
| deliveryZip | string | No | Domestic delivery postal code or city. If omitted by the user, the marketplace (country) default postal code is used. Maximum length: 1000. Defaults: United States=10001, United Kingdom=EC1A 1BB, Germany=10115, France=75001, Italy=00100, Spain=28001, Japan=100-0001, India=110034 |
| countryOrAreaCode | string | No | International delivery country code (e.g. CN, JP, KR, TW, HK, MO, SG, TH, VN, PH, MY). A domestic postal address and an international country/region code cannot both be specified. The India marketplace does not support delivery to an external country or region. Maximum length: 1000 |
| aggregateByKeepaData | boolean | No | Whether to aggregate Keepa data (sales rank, monthly sales, FBA fees, dimensions, etc.) |


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
| total | integer | Total rows |
| totalCount | integer | Total count |
| perPage | integer | Items per page |
| currentPage | integer | Current page number |
| type | string | Render style |
| sourceType | string | Source type |
| columns | array | Render columns |
| costToken | integer | Tokens consumed |
| products | array | Product list (see product fields below) |

### Product Fields

Core fields returned for each product:

| Field | Type | Description |
|------|------|------|
| asin | string | ASIN |
| title | string | Product title |
| imageUrl | string | Image URL (request URL) |
| asinUrl | string | Amazon ASIN detail URL |
| price | number | Current price (in currency units, e.g. US dollars/euros) |
| oldPrice | number | Strikethrough price |
| currency | string | Currency |
| rating | number | Current rating (0.0-5.0, e.g. 4.5 stars) |
| ratings | integer | Rating count |
| brand | string | Brand |
| sourceTool | string | Source tool |
| sourceType | string | Source type |

Aggregated Keepa fields (returned when `aggregateByKeepaData` is true):

| Field | Type | Description |
|------|------|------|
| salesRank | integer | Sales rank (Keepa) |
| salesRank30 | integer | Average sales rank over the last 30 days (Keepa) |
| salesRank90 | integer | Average sales rank over the last 90 days (Keepa) |
| salesRank180 | integer | Average sales rank over the last 180 days (Keepa) |
| monthlySalesUnits | integer | Monthly units sold (Keepa) |
| monthlySalesRevenue | number | Monthly sales revenue (Keepa) |
| monthlySalesUnits1MonthAgo ~ monthlySalesUnits12MonthsAgo | integer | Monthly units sold 1~12 months ago (Keepa) |
| reviewCount | integer | Review count (Keepa) |
| fbaFees | number | FBA fulfillment fee (Keepa; in currency units) |
| profit | number | Profit margin (Keepa; percentage, e.g. 25.5 means 25.5%) |
| referralFeePercentage | number | Referral fee percentage (Keepa) |
| fulfillment | string | Fulfillment method (AMZ, FBA, FBM) (Keepa) |
| primePrice | number | Prime price (Keepa) |
| buyBoxSellerId | string | Buy Box seller ID (Keepa) |
| sellerNum | integer | Seller count (Keepa) |
| variationNum | integer | Variation count (Keepa) |
| parentAsin | string | Parent ASIN (Keepa) |
| availableDate | string | Listing time (Keepa; yyyy-MM-dd HH:mm:ss) |
| lastUpdate | string | Last update time (Keepa; yyyy-MM-dd HH:mm:ss) |
| manufacturer | string | Manufacturer (Keepa) |
| model | string | Model (Keepa) |
| color | string | Color (Keepa) |
| material | string | Product material (Keepa), meaning the primary material used in its construction |
| weight | string | Weight (grams) (Keepa) |
| dimension | string | Dimensions (Keepa) |
| itemLength | integer | Product length (Keepa), in millimeters; 0 or -1 when unavailable |
| itemWidth | integer | Product width (Keepa), in millimeters; 0 or -1 when unavailable |
| itemHeight | integer | Product height (Keepa), in millimeters; 0 or -1 when unavailable |
| packageLength | integer | Package length (millimeters) (Keepa) |
| packageWidth | integer | Package width (millimeters) (Keepa) |
| packageHeight | integer | Package height (millimeters) (Keepa) |
| packageWeight | string | Package weight (grams) (Keepa) |
| packageDimensions | string | Package dimensions (Keepa) |
| packageQuantity | integer | Number of products per package (Keepa); 0 or -1 when unavailable |
| dimensionsType | string | Dimension type (Keepa) |
| categoryTree | string | Category tree (Keepa) |
| categoryTreeId | string | Category tree ID (Keepa) |
| rootCategory | integer | Root category ID (Keepa) |
| isAdultProduct | boolean | Whether this is an adult product (Keepa) |
| isHazmat | boolean | Whether this is hazardous material (Keepa) |
| urlSlug | string | URL Slug(keepa) |
| productImageUrls | array | Product image list (Keepa) |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credits Issues** in SKILL.md. |
| Insufficient credits | HTTP 402: follow **## Resolving Authentication and Credits Issues** in SKILL.md. |

## curl Examples

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/searchByImage \
  -H "Authorization: $nexscopeAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "imageUrl": "https://m.media-amazon.com/images/I/61pAlIX8SZL._AC_SY575_.jpg",
    "amazonDomain": "amazon.com",
    "sort": "default"
  }'
```

### Keepa Aggregation Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/searchByImage \
  -H "Authorization: $nexscopeAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "imageUrl": "https://m.media-amazon.com/images/I/61pAlIX8SZL._AC_SY575_.jpg",
    "amazonDomain": "amazon.com",
    "sort": "price-asc-rank",
    "aggregateByKeepaData": true
  }'
```

### International Delivery Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/searchByImage \
  -H "Authorization: $nexscopeAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "imageUrl": "https://m.media-amazon.com/images/I/61pAlIX8SZL._AC_SY575_.jpg",
    "amazonDomain": "amazon.co.jp",
    "countryOrAreaCode": "CN"
  }'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.nexscope.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "nexscope-xxx-xxx",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter
- `sentiment`: Choose ONE — `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE — `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise
