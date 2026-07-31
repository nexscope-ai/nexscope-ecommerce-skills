# SIF - Keyword Traffic Sources API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sif/keywordSummary`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| searchKeyword | string | Yes | Search keyword, translate to the corresponding country's language whenever possible. Max length 1000 characters |
| country | string | No | Country site, default `US`. Options (13 total): `US`, `UK`, `DE`, `CA`, `JP`, `FR`, `ES`, `IT`, `MX`, `AU`, `AE`, `BR`, `SA` |
| asins | string | No | ASIN filter list, comma-separated; if not provided, returns all ASINs for this keyword. Max length 1000 characters |
| condition | string | No | Condition filter, only one at a time.<br>**Flag type**: `nfPosition` (natural traffic keyword), `isSpAd` (SP ad keyword), `isVedioAd` (video ad keyword), `isBrandAd` (brand ad keyword), `isPPCAd` (PPC ad keyword), `isSearchRecommend` (search recommendation keyword), `acAd` (SP recommendation)<br>**Period count type**: `totalPeriod.in` (new incoming traffic keywords), `nfKeywordCnt.total` / `.in`, `adKeywordCnt.total` / `.in`, `allSpKeywordCnt.total` / `.in`, `spKeywordCnt.total` / `.in`, `recSpKeywordCnt.total` / `.in`, `allSbKeywordCnt.total` / `.in`, `sbKeywordCnt.total` / `.in`, `sbvKeywordCnt.total` / `.in` |
| last7d | boolean | No | Whether to get last 7 days data, default `true`. When `false`, use `startDate`/`endDate` range |
| startDate | string | No | Start date `yyyy-MM-dd` (effective when `last7d=false`; if omitted, the latest system full week is used) |
| endDate | string | No | End date `yyyy-MM-dd` (paired with `startDate`) |
| sortBy | string | No | Sort field. Options: `totalKeywordNum` (all traffic keywords), `naturalKeywordNum` (natural traffic keywords), `brandKeywordNum` (brand ad keywords), `vedioKeywordNum` (video ad keywords), `acKeywordNum` (AC recommended keywords), `erKeywordNum` (ER recommended keywords), `trKeywordNum` (TR recommended keywords), `sumScore` (total keyword exposure score), `totalNfScore`, `totalSpSocre` (note spelling), `totalBrandScore`, `totalVedioScore`, `totalAcScore`, `totalTrScore`, `totalErScore` |
| pageNum | integer | No | Page number, default `1` |
| pageSize | integer | No | Results per page, min 10, max 100, default `100` |
| desc | boolean | No | Whether to sort descending, default `true` |


## Response Structure

### Top-Level Fields

| Field | Type | Description |
|------|------|------|
| code | string | Response code |
| msg | string | Message |
| total | integer | Number of data records actually returned |
| data | array | Return data, array of product keyword traffic data objects |
| columns | array | Render columns |
| type | string | Render style |
| title | string | Title |
| costTime | integer | Latency (ms) |
| costToken | integer | Tokens consumed |

> This endpoint does not return `isParentAsin`, `variantsNum`, or `noKeywordVariantsNum`; use the `sif/asinSummary` endpoint if you need these fields.

### Data Item Fields (Each Object in the `data` Array)

> Two types of scores: unprefixed fields (e.g. `naturalSearchExposureScore`) are product-level aggregate metrics for this ASIN across all keywords; `keyword*` prefixed fields (e.g. `keywordNaturalExposureScore`) are metrics for this ASIN only on the current query keyword.

| Field | Type | Description |
|------|------|------|
| asin | string | ASIN code |
| productTitle | string | Product title |
| productImageUrl | string | Product main image URL |
| productPrice | number | Product price |
| customerRatingCount | integer | Total customer rating count |
| productStarRating | number | Product star rating (0-5 stars) |
| productRatingScore | number | Product rating score value |
| productUpdateTime | string | Product update time (`yyyy-MM-dd HH:mm:ss`) |
| dataPeriodStartDate | string | Data period start date (`yyyy-MM-dd`) |
| totalExposureScore | number | Total exposure score |
| totalExposureRatio | number | Total traffic share |
| naturalSearchExposureScore | number | Natural search exposure total score |
| naturalSearchExposureRatio | number | Natural search exposure ratio |
| sponsoredProductsExposureScore | number | SP ad exposure total score |
| sponsoredProductsExposureRatio | number | SP ad exposure ratio |
| brandAdExposureScore | number | Brand ad exposure total score |
| brandAdExposureRatio | number | Brand ad exposure ratio |
| videoAdExposureScore | number | Video ad exposure total score |
| videoAdExposureRatio | number | Video ad exposure ratio |
| amazonsChoiceExposureScore | number | AC exposure total score |
| amazonsChoiceExposureRatio | number | AC exposure ratio |
| editorialRecommendationsExposureScore | number | ER exposure total score |
| editorialRecommendationsExposureRatio | number | ER exposure ratio |
| topRatedExposureScore | number | TR exposure total score |
| topRatedExposureRatio | number | TR exposure ratio |
| recommendPositionExposureScore | number | Recommendation position exposure total score |
| recommendAdExposureScore | number | Recommendation position ad exposure score |
| recommendAdExposureRatio | number | Recommendation position ad traffic share |
| recommendNonadExposureScore | number | Recommendation position non-ad exposure score |
| recommendNonadExposureRatio | number | Recommendation position non-ad traffic share |
| comprehensiveNaturalExposureScore | number | Comprehensive natural traffic score (natural search + recommendation non-ad) |
| comprehensiveNaturalExposureRatio | number | Comprehensive natural traffic share |
| keywordTotalExposureScore | number | Keyword total score |
| keywordNaturalExposureScore | number | Keyword natural score |
| keywordSponsoredProductsExposureScore | number | Keyword SP ad score |
| keywordBrandAdExposureScore | number | Keyword brand ad score |
| keywordVideoAdExposureScore | number | Keyword video ad score |
| keywordAmazonsChoiceExposureScore | number | Keyword AC score |
| keywordRecommendExposureScore | number | Keyword recommendation position score |
| keywordRecommendAdExposureScore | number | Keyword recommendation position ad score |
| keywordRecommendNonadExposureScore | number | Keyword recommendation position non-ad score |
| keywordComprehensiveNaturalExposureScore | number | Keyword comprehensive natural score (natural + recommendation non-ad) |
| ppcTrafficSources | array | PPC paid ad traffic source markers. Contains: SP ads, top brand ads, bottom brand ads, video ads |
| naturalSearchTrafficSources | array | Natural search traffic source markers |
| amazonRecommendationSources | array | Amazon recommendation traffic source markers. Contains: Best Seller, AC, ER, TR, TRFOB, etc. |
| promotionalDealSources | array | Promotional deal traffic source markers. Contains: Coupon, Limited Time Deal, Lowest Price in 30 Days, etc. |

> This endpoint does not return the following fields: `productCategory`, `productFeatures`, `isVariantProduct`, `isMonitored`, `monitoringStartTime`, and per-ASIN `totalTrafficKeywordCount`, `naturalSearchKeywordCount`, `sponsoredProductsKeywordCount`, `brandAdKeywordCount`, `topBrandAdKeywordCount`, `bottomBrandAdKeywordCount`, `videoAdKeywordCount`, `amazonsChoiceKeywordCount`, `editorialRecommendationsKeywordCount`, `topRatedKeywordCount`, `frequentlyBoughtKeywordCount`. Use the `sif/asinSummary` endpoint if you need these fields.

## Error Codes

Under normal circumstances, the HTTP status code is 200. Business success or failure is determined by the `errorCode` field in the response body (errorCode = 200 indicates success; other values indicate business errors). When encountering unauthorized access, the HTTP status code is 401 and the corresponding errorCode is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| 402 | Insufficient balance | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| Other non-200 values | Business error | Refer to the `errmsg` field for specific error details |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sif/keywordSummary \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"searchKeyword": "wireless charger", "country": "US"}'
```

### With Condition Filter (SP Ad Keywords Only):

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sif/keywordSummary \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"searchKeyword": "wireless charger", "country": "US", "condition": "isSpAd"}'
```

### Filter by ASIN + Specified Date Range:

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sif/keywordSummary \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"searchKeyword": "wireless charger", "country": "US", "asins": "B01NBNDC1T,B09VLJJPL6", "last7d": false, "startDate": "2026-04-05", "endDate": "2026-04-11"}'
```

### Sort by SP Exposure Score:

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sif/keywordSummary \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"searchKeyword": "wireless charger", "country": "US", "sortBy": "totalSpSocre", "desc": true}'
```

### With Pagination:

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sif/keywordSummary \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"searchKeyword": "phone case", "country": "US", "pageNum": 2, "pageSize": 50}'
```

---
