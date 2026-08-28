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

Under normal conditions, the HTTP status code is always 200. Business success or failure is determined by the errorCode field in the response body (errorCode = 200 indicates success; other values indicate business errors). In cases of unauthorized access, the HTTP status code will be 401, with the corresponding errorCode also being 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| 402 | Insufficient credits | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| Other non-200 values | Business exception | Refer to the `errmsg` field for specific error cause |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

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
