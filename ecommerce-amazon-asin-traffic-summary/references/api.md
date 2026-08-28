# SIF - ASIN Traffic Sources API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sif/asinSummary`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| searchValue | string | Yes | Search value, ASIN codes, comma-separated, max 10 ASINs, max length 1000 characters |
| country | string | No | Country site, default `US`. Options (13 total): `US`, `UK`, `DE`, `CA`, `JP`, `FR`, `ES`, `IT`, `MX`, `AU`, `AE`, `BR`, `SA` |
| last7d | boolean | No | Whether to get last 7 days data, default `true`. When `false`, use `startDate`/`endDate` range |
| startDate | string | No | Start date `yyyy-MM-dd` (effective when `last7d=false`; if omitted, the latest system week is used) |
| endDate | string | No | End date `yyyy-MM-dd` (paired with `startDate`) |
| conditions | string | No | Condition filters, comma-separated. Options: `nf` (natural traffic), `sp` (SP ads), `sb` (SB regular), `sbv` (video ads), `ad` (ad traffic), `acAd` (SP recommendation), `totalPeriod.in` (new incoming traffic keywords) |
| sortBy | string | No | Sort field. Options: `totalKeywordNum` (all traffic keywords), `naturalKeywordNum` (natural traffic keywords), `brandKeywordNum` (brand ad keywords), `vedioKeywordNum` (video ad keywords), `acKeywordNum` (AC recommended keywords), `erKeywordNum` (ER recommended keywords), `trKeywordNum` (TR recommended keywords), `sumScore` (total keyword exposure score), `totalNfScore` (total natural rank exposure score), `totalSpSocre` (total SP ad exposure score, note spelling), `totalBrandScore` (total brand ad exposure score), `totalVedioScore` (total video ad exposure score), `totalAcScore` (total AC recommendation exposure score), `totalTrScore` (total TR recommendation exposure score), `totalErScore` (total ER recommendation exposure score) |
| pageNum | integer | No | Page number, default `1` |
| pageSize | integer | No | Results per page, min 10, max **10000**, default `10000` |
| desc | boolean | No | Whether to sort descending, default `true` |

## Response Structure

| Field | Type | Description |
|------|------|------|
| code | string | Response code |
| msg | string | Message |
| total | integer | Number of data records actually returned |
| data | array | Return data, ASIN summary object array (see below) |
| columns | array | Render columns |
| type | string | Render style |
| title | string | Title |
| isParentAsin | boolean | Whether the search value is a parent ASIN |
| variantsNum | integer | Number of variant products with keywords |
| noKeywordVariantsNum | integer | Number of variant products without keywords |
| costTime | integer | Latency (ms) |
| costToken | integer | Tokens consumed |

### data Array Element Fields

> Field suffix convention: `*Prev` is the previous period's value; `*In` / `*Out` are new incoming / outgoing counts compared to the previous period, used for week-over-week comparison.

| Field | Type | Description |
|------|------|------|
| asin | string | ASIN code. Amazon Standard Identification Number |
| productTitle | string | Product title |
| productCategory | string | Product category |
| productPrice | number | Product price |
| productImageUrl | string | Product main image URL |
| productFeatures | array | Product feature list |
| customerRatingCount | integer | Total customer rating count |
| productStarRating | number | Product star rating (0-5 stars) |
| productRatingScore | number | Product rating score value (0-5, as displayed on Amazon page) |
| isVariantProduct | boolean | Whether it is a variant |
| recentMonthlySalesBucket | string | Recent month sales bucket (only has value in keywordSummary path, e.g. `"300+"` or `"1,000+"`) |
| isMonitored | boolean | Whether it is being monitored |
| monitoringStartTime | string | Product monitoring start time |
| dataPeriodStartDate | string | Data period start date (`yyyy-MM-dd`) |
| totalExposureScore | number | Total exposure score. Composite exposure score of this product across all keywords |
| totalExposureScorePrev | number | Previous period total exposure score |
| totalTrafficKeywordCount | integer | Total traffic keyword count |
| totalTrafficKeywordCountIn | integer | New incoming traffic keyword count for this period |
| totalTrafficKeywordCountOut | integer | Outgoing traffic keyword count for this period |
| totalTrafficKeywordCountPrev | integer | Previous period total traffic keyword count |
| naturalSearchExposureScore | number | Natural search exposure total score |
| naturalSearchExposureRatio | number | Natural search exposure ratio |
| naturalSearchExposureScorePrev | number | Previous period natural search exposure score |
| naturalSearchKeywordCount | integer | Natural search keyword count |
| naturalSearchKeywordCountIn | integer | New incoming natural search keyword count for this period |
| naturalSearchKeywordCountOut | integer | Outgoing natural search keyword count for this period |
| naturalSearchKeywordCountPrev | integer | Previous period natural search keyword count |
| sponsoredProductsExposureScore | number | SP ad exposure total score |
| sponsoredProductsExposureRatio | number | SP ad exposure ratio |
| sponsoredProductsExposureScorePrev | number | Previous period SP ad exposure score |
| sponsoredProductsKeywordCount | integer | SP ad keyword count |
| brandAdExposureScore | number | Brand ad exposure total score |
| brandAdExposureRatio | number | Brand ad exposure ratio |
| brandAdExposureScorePrev | number | Previous period brand ad exposure score |
| brandAdKeywordCount | integer | Total brand ad keyword count |
| topBrandAdKeywordCount | integer | Top-of-page brand ad keyword count |
| bottomBrandAdKeywordCount | integer | Bottom-of-page brand ad keyword count |
| videoAdExposureScore | number | Video ad exposure total score |
| videoAdExposureRatio | number | Video ad exposure ratio |
| videoAdExposureScorePrev | number | Previous period video ad exposure score |
| videoAdKeywordCount | integer | Video ad keyword count |
| amazonsChoiceExposureScore | number | Amazon's Choice exposure total score |
| amazonsChoiceExposureRatio | number | Amazon's Choice exposure ratio |
| amazonsChoiceExposureScorePrev | number | Previous period AC exposure score |
| amazonsChoiceKeywordCount | integer | Amazon's Choice keyword count |
| amazonsChoiceKeywordCountIn | integer | New incoming AC keyword count for this period |
| amazonsChoiceKeywordCountOut | integer | Outgoing AC keyword count for this period |
| editorialRecommendationsExposureScore | number | Editorial Recommendations exposure total score |
| editorialRecommendationsExposureRatio | number | Editorial Recommendations exposure ratio |
| editorialRecommendationsKeywordCount | integer | Editorial Recommendations keyword count |
| topRatedExposureScore | number | Top Rated recommendation exposure total score |
| topRatedExposureRatio | number | Top Rated recommendation exposure ratio |
| topRatedKeywordCount | integer | Top Rated recommendation keyword count |
| frequentlyBoughtKeywordCount | integer | Frequently Bought recommendation keyword count (Top Rated Frequently Bought) |
| recommendPositionExposureScore | number | Recommendation position exposure total score |
| recommendAdExposureScore | number | Recommendation position ad exposure score |
| recommendNonadExposureScore | number | Recommendation position non-ad exposure score |
| nonAcRecommendExposureScore | number | Non-AC recommendation position exposure score |
| recommendKeywordCount | integer | Total recommendation position keyword count |
| recommendAdKeywordCount | integer | Recommendation position ad keyword count |
| recommendNonadKeywordCount | integer | Recommendation position non-ad keyword count |
| ppcTrafficSources | array | PPC paid ad traffic source markers. Contains: SP ads, top brand ads, bottom brand ads, video ads |
| naturalSearchTrafficSources | array | Natural search traffic source markers |
| amazonRecommendationSources | array | Amazon recommendation traffic source markers. Contains: Best Seller, AC, ER, TR, TRFOB, etc. |
| promotionalDealSources | array | Promotional deal traffic source markers. Contains: Coupon, Limited Time Deal, Lowest Price in 30 Days, etc. |

## Error Codes

Under normal circumstances, the HTTP status code is 200. Business success or failure is determined by the `errorCode` field in the response body (errorCode = 200 indicates success; other values indicate business errors). When encountering unauthorized access, the HTTP status code is 401 and the corresponding errorCode is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| 402 | Insufficient credits | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sif/asinSummary \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"searchValue": "B09V3KXJPB", "country": "US"}'
```

### Multi-ASIN Query

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sif/asinSummary \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"searchValue": "B09V3KXJPB,B0BN1K7WJP", "country": "US", "pageSize": 10000, "pageNum": 1, "desc": true}'
```

### Specified Date Range + Ad Traffic Only

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sif/asinSummary \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"searchValue": "B09V3KXJPB", "country": "US", "last7d": false, "startDate": "2026-03-08", "endDate": "2026-03-14", "conditions": "ad", "sortBy": "totalSpSocre"}'
```

---
