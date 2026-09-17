# Amazon Frontend Product Detail API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/product/detail`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, read api_key from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| asins | string | Yes | ASIN list, supports batch query, up to 40 ASINs. Format: `^[A-Z0-9]+(,[A-Z0-9]+){0,39}$`. Example: `B072MQ5BRX,B08N5WRWNW` |
| amazonDomain | string | No | Amazon country site, default `amazon.com`. Options: `amazon.com`, `amazon.co.uk`, `amazon.de`, `amazon.fr`, `amazon.it`, `amazon.es`, `amazon.co.jp`, `amazon.ca`, `amazon.com.au`, `amazon.com.br`, `amazon.in`, `amazon.nl`, `amazon.se`, `amazon.pl`, `amazon.sg`, `amazon.sa`, `amazon.ae`, `amazon.com.tr`, `amazon.com.mx`, `amazon.eg`, `amazon.cn`, `amazon.com.be` |
| language | string | No | Language. Examples: `en_US`, `de_DE`, `fr_FR`, `ja_JP`, `it_IT`, `es_ES`, `pt_BR`, `en_GB`, `zh_CN` |
| deliveryZip | string | No | Delivery zip code, used to get delivery-related pricing. Examples: `10001` (New York, US), `10115` (Berlin, Germany), `EC1A 1BB` (London, UK) |
| device | string | No | Device type: `desktop` (default), `mobile`, `tablet` |
| returnBoughtTogether | boolean | No | Whether to return frequently bought together items (boughtTogether), default `false` |
| returnRelatedProducts | boolean | No | Whether to return related product list (relatedProducts), default `false` |
| returnAuthorsReviews | boolean | No | Whether to return author review list (authorsReviews), default `false` |

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Response Structure

Top-level fields:

| Field | Type | Description |
|------|------|------|
| total | integer | Total rows |
| columns | array | Rendered columns |
| type | string | Render style |
| costToken | integer | Token consumption |
| products | array | Product list (see below) |

### Product Object Fields

| Field | Type | Description |
|------|------|------|
| asin | string | ASIN code |
| title | string | Product title |
| brand | string | Brand |
| price | number | Price |
| extractedPrice | number | Extracted price |
| oldPrice | number | Original price |
| extractedOldPrice | number | Extracted original price |
| currency | string | Currency |
| discount | string | Discount |
| saveWithCoupon | string | Amount saved with coupon |
| rating | number | Rating |
| ratings | integer | Number of reviews |
| prime | boolean | Whether it is a Prime item |
| stock | string | Stock status |
| delivery | string | Delivery information |
| link | string | Product link |
| linkClean | string | Clean link |
| asinUrl | string | Link |
| imageUrl | string | Thumbnail |
| thumbnail | string | Thumbnail |
| productImageUrls | array | Product image URL list |
| aboutItem | array | Bullet points |
| productDescription | string | Product description; **when A+ content exists, this is a JSON string** (see A+ structure below) |
| description | string | Product description |
| dimension | string | Product dimensions |
| weight | string | Weight |
| tags | string | Tag list |
| badges | string | Badge list |
| climatePledgeFriendly | boolean | Whether it is Climate Pledge Friendly |
| snapEbtEligible | boolean | Whether SNAP EBT eligible |
| boughtLastMonth | string | Units bought last month (string) |
| boughtLastMonthCount | integer | Units bought last month (number) |
| reviewsSummary | string | Review summary |
| reviewsImages | array | Review image list |
| sourceTool | string | Source tool |
| sourceType | string | Source type: amazon |
| pageFileUrl | string | Processed product JSON file URL; not raw HTML |
| rawHtmlFile | string | Raw Amazon product-page HTML URL from the upstream provider; optional and matched to the containing product's `asin` |

### Nested Objects

**productDetails** -- Detailed product specifications:

| Field | Type | Description |
|------|------|------|
| asin | string | ASIN code |
| manufacturer | string | Manufacturer |
| productDimensions | string | Product dimensions |
| upc | string | UPC code |
| units | string | Units |
| rating | number | Rating |
| review | integer | Number of reviews |

**customerReviews** -- Star rating distribution:

| Field | Type | Description |
|------|------|------|
| fiveStar | integer | Five-star review count |
| fourStar | integer | Four-star review count |
| threeStar | integer | Three-star review count |
| twoStar | integer | Two-star review count |
| oneStar | integer | One-star review count |

**variants** -- Product variant list (array):

| Field | Type | Description |
|------|------|------|
| title | string | Variant title (e.g., color, size) |
| items | array | Variant item list, each item contains `name` (name), `asin` (ASIN code), `position` (position), `selected` (whether selected) |

**itemSpecifications** -- Product specifications (dynamic key-value).

**itemIngredients** -- Product ingredient list (array).

**reviewsImages** -- Review image list (array).

### A+ Content in productDescription (when A+ present)

When a listing has A+ Content configured, `productDescription` may be a **JSON string** (rather than HTML description). When parsed, it becomes an array of objects:

| Field | Type | Description |
|------|------|------|
| position | integer | Module order |
| title | string | Module title |
| image | string | A+ module main image URL (often contains `aplus-media-library-service-media`) |
| carouselImages | array | Optional; carousel sub-items, each containing `position` / `title` / `image` |

Without A+, this field is usually plain HTML/text, and `json.loads` will fail -- consumers should silently skip A+ extraction and use only `productImageUrls`.

### Optional Nested Arrays (returned on demand)

**boughtTogether** (returned when `returnBoughtTogether: true`):

| Field | Type | Description |
|------|------|------|
| asin | string | ASIN code |
| title | string | Title |
| price | string | Price |
| extractedPrice | number | Extracted price |
| priceUnit | string | Unit price |
| extractedPriceUnit | number | Extracted unit price |
| thumbnail | string | Thumbnail |
| link | string | Link |
| linkClean | string | Clean link |
| stock | string | Stock status |
| delivery | array | Delivery information |
| position | integer | Position |

**relatedProducts** (returned when `returnRelatedProducts: true`):

| Field | Type | Description |
|------|------|------|
| asin | string | ASIN code |
| title | string | Title |
| price | string | Price |
| extractedPrice | number | Extracted price |
| oldPrice | string | Original price |
| extractedOldPrice | number | Extracted original price |
| priceUnit | string | Unit price |
| extractedPriceUnit | number | Extracted unit price |
| rating | number | Rating |
| reviews | integer | Number of reviews |
| thumbnail | string | Thumbnail |
| link | string | Link |
| linkClean | string | Clean link |
| prime | boolean | Whether it is a Prime item |
| sponsored | boolean | Whether it is a sponsored item |
| climatePledgeFriendly | boolean | Whether Climate Pledge Friendly |
| discount | string | Discount |
| badges | array | Badge list |
| position | integer | Position |

**authorsReviews** (returned when `returnAuthorsReviews: true`):

| Field | Type | Description |
|------|------|------|
| title | string | Title |
| text | string | Review content |
| author | string | Author |
| authorImage | string | Author avatar |
| authorLink | string | Author link |
| rating | integer | Rating |
| date | string | Date |
| verifiedPurchase | boolean | Whether verified purchase |
| helpfulVotes | string | Helpful vote count |
| productSize | string | Product size |
| productFlavorName | string | Product flavor name |
| position | integer | Position |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| Insufficient credits | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/product/detail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"asins": "B072MQ5BRX,B08N5WRWNW", "amazonDomain": "amazon.com"}'
```

### With Optional Parameters

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/product/detail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "asins": "B072MQ5BRX",
    "amazonDomain": "amazon.de",
    "language": "de_DE",
    "deliveryZip": "10115",
    "returnBoughtTogether": true,
    "returnAuthorsReviews": true
  }'
```

---
