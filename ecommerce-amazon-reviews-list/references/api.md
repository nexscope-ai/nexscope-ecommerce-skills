# Amazon Product Reviews API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/reviews/list`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, read api_key from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)

## Request Parameters

POST Body (JSON):

  | Parameter | Type | Required | Description |
|------|------|------|--------------------------------------------------------------------------------------------------------------------------------|
| asin | string | Yes | Amazon product ASIN |
| domainCode | string | No | Amazon domain code, default `com`. Options: `com`, `ca`, `co.uk`, `in`, `de`, `fr`, `it`, `es`, `co.jp`, `com.au`, `com.br`, `nl`, `se`, `com.mx`, `ae`. Use `com` for the US site |
| star1Num | integer | No | Number of 1-star reviews, default 10, max 100 |
| star2Num | integer | No | Number of 2-star reviews, default 10, max 100 |
| star3Num | integer | No | Number of 3-star reviews, default 10, max 100 |
| star4Num | integer | No | Number of 4-star reviews, default 10, max 100 |
| star5Num | integer | No | Number of 5-star reviews, default 10, max 100 |
| filterByKeyword | string | No | Filter reviews by keyword, max length 1000 characters |
| sortBy | string | No | Review sort order: `recent` (most recent reviews) or `helpful` (most helpful reviews), default `recent` |
| reviewerType | string | No | Reviewer type: `all_reviews` (all reviews) or `avp_only_reviews` (verified purchases only), default `all_reviews` |
| mediaType | string | No | Media type: `all_contents` (all content) or `media_reviews_only` (reviews with media only), default `all_contents` |
| formatType | string | No | Format type: `all_formats` (all formats) or `current_format` (current format), default `all_formats` |

Note: If `star1Num` through `star5Num` are all omitted, 10 reviews per star rating are fetched by default. If any star rating count is provided, omitted star ratings default to `0`.

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
| total | integer | Total review count |
| data | array | Review list (see review object below) |
| columns | array | Rendered columns |
| costToken | integer | Total token consumption |
| type | string | Render style |

### Review Object

| Field | Type | Description |
|------|------|------|
| reviewId | string | Review ID |
| asin | string | Product ASIN |
| title | string | Review title |
| text | string | Review content |
| rating | string | Rating |
| date | string | Review date |
| userName | string | Reviewer name |
| verified | boolean | Whether verified purchase |
| vine | boolean | Whether Vine Voice review |
| numberOfHelpful | integer | Helpful count |
| imageUrlList | array | Review image list |
| videoUrlList | array | Review video list |
| domainCode | string | Country code |
| productTitle | string | Product title |
| productRating | string | Product rating |
| countRatings | integer | Product rating count |
| countReviews | integer | Product review count |
| variationId | string | Variation ID |
| variationList | array | Variation list |
| profilePath | string | Reviewer profile path |
| currentPage | integer | Current page number |
| sortStrategy | string | Sort strategy |
| statusCode | integer | Status code |
| statusMessage | string | Status message |
| locale | object | Locale information |
| reviewSummary | object | Review summary data |
| filters | object | Applied filter conditions |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| Insufficient credits | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |

## curl Example (US Site)

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/reviews/list \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "asin": "B08N5WRWNW",
    "domainCode": "com",
    "star1Num": 10,
    "star2Num": 10,
    "star3Num": 0,
    "star4Num": 0,
    "star5Num": 0,
    "sortBy": "recent",
    "reviewerType": "all_reviews"
  }'
```

---
