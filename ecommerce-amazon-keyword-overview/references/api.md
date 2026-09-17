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


## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Response Structure

### Top-Level Fields

| Field | Type | Description |
|------|------|------|
| msg | string | Message |
| total | integer | Total data count. Note: this endpoint typically returns only a single record, total is usually 1 |
| code | string | SIF business response code; `"1"` indicates success |
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

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| Insufficient balance | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |

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
