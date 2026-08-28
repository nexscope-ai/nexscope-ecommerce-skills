# SIF - Keyword Competitor Count API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sif/keywordOverview`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| keyword | string | Yes | Keyword, translate to the corresponding country's language whenever possible. Max length: 1000 characters |
| country | string | No | Country site, default `US`. Options (13 total): `US`, `UK`, `DE`, `CA`, `JP`, `FR`, `ES`, `IT`, `MX`, `AU`, `AE`, `BR`, `SA` |
| last7d | boolean | No | Whether to get last 7 days data, default `true`. When `false`, use `startDate`/`endDate` range |
| startDate | string | No | Start date `yyyy-MM-dd` (effective when `last7d=false`) |
| endDate | string | No | End date `yyyy-MM-dd` (paired with `startDate`) |


## Response Structure

### Top-Level Fields

| Field | Type | Description |
|------|------|------|
| msg | string | Message |
| total | integer | Total data count. Note: this endpoint typically returns only a single record, total is usually 1 |
| code | string | Response code |
| data | array | Return data (see data fields below) |
| costTime | integer | Latency (ms) |
| costToken | integer | Tokens consumed |
| columns | array | Render columns |
| type | string | Render style |
| title | string | Title |

### Data Fields (Each Object in the `data` Array)

| Field | Type | Description |
|------|------|------|
| keyword | string | Keyword. The keyword text of the search query |
| keywordPopularityRank | integer | Keyword popularity rank. This keyword's monthly search volume ranking among all Amazon keywords; lower values indicate higher search volume |
| estimatedWeeklySearchVolume | integer | Estimated weekly search volume. Estimated weekly search count for this keyword on Amazon, reflecting its search popularity |
| supplyDemandRatio | number | Supply-demand ratio. Ratio of supply to demand, formula: search result product count / monthly search volume; lower values indicate less competition and greater opportunity |
| totalSearchResultProductCount | integer | Total search result product count. Total number of products displayed for this keyword (including natural search, ad placements, recommendation placements, etc.) |
| naturalSearchProductCount | integer | Natural search product count. Number of products displayed in natural search results for this keyword (excluding ad placements) |
| sponsoredProductsCount | integer | SP ad product count. Number of products running Sponsored Products ads for this keyword |
| brandAdProductCount | integer | Brand ad product count. Number of products running brand ads for this keyword |
| videoAdProductCount | integer | Video ad product count. Number of products running video ads for this keyword |
| paidAdvertisingProductCount | integer | Total PPC ad product count. Total number of products running any PPC paid ads for this keyword (including SP, brand ads, video ads, etc.) |
| amazonChoiceProductCount | integer | Amazon's Choice product count. Number of products with the Amazon's Choice badge for this keyword |
| topRatedProductCount | integer | Top Rated recommended product count. Number of products appearing in the Top Rated (high rating) recommendation placement for this keyword |
| searchRecommendationProductCount | integer | Search recommendation product count. Number of products recommended by Amazon when searching this keyword |
| editorialRecommendationsProductCount | integer | Editorial Recommendations product count. Number of products appearing in the editorial recommendation placement for this keyword |
| recNonadProductCount | integer | Recommendation placement non-ad product count. Number of non-ad (organic) products in recommendation placements for this keyword |
| recAdProductCount | integer | Recommendation placement ad product count. Number of ad products in recommendation placements for this keyword |
| trackedAsinTotalCount | integer | SIF tracked ASIN deduplicated total count. Deduplicated count of ASINs that SIF has tracked with exposure scores across all positions (natural/ad/recommendation) for this keyword (upstream field: `totalAsinNum`) |
| totalMarketplaceKeywordCount | integer | Total marketplace keyword count. Total number of keywords for this site, used to understand overall market size |
| dataPeriodStartDate | string | Data period start date. ABA week start date corresponding to the returned data (`yyyy-MM-dd`) |
| dataPeriodEndDate | string | Data period end date. ABA week end date corresponding to the returned data (`yyyy-MM-dd`) |
| keywordDataUpdateTime | string | Keyword data update time |

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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sif/keywordOverview \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "wireless charger", "country": "US"}'
```

### Specified Date Range

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sif/keywordOverview \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "yoga mat", "country": "US", "last7d": false, "startDate": "2026-03-08", "endDate": "2026-03-14"}'
```

---
