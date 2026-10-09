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
| aggregateByKeepaData | boolean | No | Whether to aggregate Nexscope data (sales rank, monthly sales, FBA fees, dimensions, etc.) |


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

Aggregated Nexscope fields (returned when `aggregateByKeepaData` is true):

| Field | Type | Description |
|------|------|------|
| salesRank | integer | Sales rank (Nexscope) |
| salesRank30 | integer | Average sales rank over the last 30 days (Nexscope) |
| salesRank90 | integer | Average sales rank over the last 90 days (Nexscope) |
| salesRank180 | integer | Average sales rank over the last 180 days (Nexscope) |
| monthlySalesUnits | integer | Monthly units sold (Nexscope) |
| monthlySalesRevenue | number | Monthly sales revenue (Nexscope) |
| monthlySalesUnits1MonthAgo ~ monthlySalesUnits12MonthsAgo | integer | Monthly units sold 1~12 months ago (Nexscope) |
| reviewCount | integer | Review count (Nexscope) |
| fbaFees | number | FBA fulfillment fee (Nexscope; in currency units) |
| profit | number | Profit margin (Nexscope; percentage, e.g. 25.5 means 25.5%) |
| referralFeePercentage | number | Referral fee percentage (Nexscope) |
| fulfillment | string | Fulfillment method (AMZ, FBA, FBM) (Nexscope) |
| primePrice | number | Prime price (Nexscope) |
| buyBoxSellerId | string | Buy Box seller ID (Nexscope) |
| sellerNum | integer | Seller count (Nexscope) |
| variationNum | integer | Variation count (Nexscope) |
| parentAsin | string | Parent ASIN (Nexscope) |
| availableDate | string | Listing time (Nexscope; yyyy-MM-dd HH:mm:ss) |
| lastUpdate | string | Last update time (Nexscope; yyyy-MM-dd HH:mm:ss) |
| manufacturer | string | Manufacturer (Nexscope) |
| model | string | Model (Nexscope) |
| color | string | Color (Nexscope) |
| material | string | Product material (Nexscope), meaning the primary material used in its construction |
| weight | string | Weight (grams) (Nexscope) |
| dimension | string | Dimensions (Nexscope) |
| itemLength | integer | Product length (Nexscope), in millimeters; 0 or -1 when unavailable |
| itemWidth | integer | Product width (Nexscope), in millimeters; 0 or -1 when unavailable |
| itemHeight | integer | Product height (Nexscope), in millimeters; 0 or -1 when unavailable |
| packageLength | integer | Package length (millimeters) (Nexscope) |
| packageWidth | integer | Package width (millimeters) (Nexscope) |
| packageHeight | integer | Package height (millimeters) (Nexscope) |
| packageWeight | string | Package weight (grams) (Nexscope) |
| packageDimensions | string | Package dimensions (Nexscope) |
| packageQuantity | integer | Number of products per package (Nexscope); 0 or -1 when unavailable |
| dimensionsType | string | Dimension type (Nexscope) |
| categoryTree | string | Category tree (Nexscope) |
| categoryTreeId | string | Category tree ID (Nexscope) |
| rootCategory | integer | Root category ID (Nexscope) |
| isAdultProduct | boolean | Whether this is an adult product (Nexscope) |
| isHazmat | boolean | Whether this is hazardous material (Nexscope) |
| urlSlug | string | URL Slug(Nexscope) |
| productImageUrls | array | Product image list (Nexscope) |

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

### Nexscope Aggregation Example

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
