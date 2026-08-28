# SIF - ASIN Keywords API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sif/asinKeywords`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| asin | string | Yes | ASIN code, max length 1000 characters. This tool can only query one ASIN at a time |
| country | string | No | Country site, default `US`. Options (13 total): `US`, `UK`, `DE`, `CA`, `JP`, `FR`, `ES`, `IT`, `MX`, `AU`, `AE`, `BR`, `SA` |
| keyword | string | No | Keyword, max length 1000. Translate to the corresponding country's language whenever possible |
| timePieceType | string | No | Time slice type, default `latelyDay`. Options: `latelyDay` (last N days), `month` (a specific month), `week` (a specific week) |
| timePieceValue | string | No | Time slice value, default `7`, max length 1000. For `latelyDay` only `7` or `30`; for `month` format `YYYY-MM` (e.g. `2026-04`); for `week` format week start date `YYYY-MM-DD` (e.g. `2026-04-13`) |
| conditions | string | No | Condition filters, comma-separated. Options:<br>**Flag type**: `nfPosition` (natural traffic keyword), `isSpAd` (SP ad keyword), `isBrandAd` (brand ad keyword), `isVedioAd` (video ad keyword), `isAC` (AC recommended keyword), `isAccurateKw` (precise traffic keyword), `isAccurateTailKw` (precise long-tail keyword), `isPurchaseKw` (converting keyword), `isQualityKw` (high-quality conversion keyword), `isStableKw` (stable conversion keyword), `isLossKw` (lost conversion keyword), `isInvalidKw` (invalid impression keyword), `isMultiVariantKw` (multi-variant natural rank keyword), `isSearchVolUpKw` (search volume YoY growth keyword), `isSearchVolDownKw` (search volume YoY decline keyword)<br>**Period count type (`.total` all / `.in` new)**: `totalPeriod.in`, `nfKeywordCnt.total`, `nfKeywordCnt.in`, `adKeywordCnt.total`, `adKeywordCnt.in`, `allSpKeywordCnt.total`, `allSpKeywordCnt.in`, `spKeywordCnt.total`, `spKeywordCnt.in`, `recSpKeywordCnt.total`, `recSpKeywordCnt.in`, `allSbKeywordCnt.total`, `allSbKeywordCnt.in`, `sbKeywordCnt.total`, `sbKeywordCnt.in`, `sbvKeywordCnt.total`, `sbvKeywordCnt.in` |
| sortBy | string | No | Sort field. Options: `lastRank` (natural rank), `adLastRank` (ad rank), `updateTime` (keyword crawl time), `searchesRank` (search rank), `estSearchesNum` (monthly search volume). Empty string means default system sort |
| desc | boolean | No | Whether to sort descending, default `true` |
| pageNum | integer | No | Page number, default `1` |
| pageSize | integer | No | Results per page, min 10, max 100, default `100` |


## Response Structure

| Field | Type | Description |
|------|------|------|
| code | string | Response code |
| msg | string | Message |
| total | integer | Number of data records actually returned |
| data | array | Data array (see below) |
| columns | array | Render columns |
| type | string | Render style |
| title | string | Title |
| isParentAsin | boolean | Whether it is a parent ASIN (pasin) |
| hasVaiants | boolean | Whether it has variants |
| abaCreateDateWeek | string | Week date corresponding to the latest weekly ABA data |
| costTime | integer | Latency (ms) |
| costToken | integer | Tokens consumed |

### data Array Element Fields

| Field | Type | Description |
|------|------|------|
| keyword | string | Keyword |
| translateKeyword | string | Keyword translation, localized translation for the site |
| asin | string | Product ASIN |
| productNaturalRank | integer | Product natural search rank. The position ranking of this product in natural search results for this keyword, e.g. 1 means ranked 1st (top position) in search results |
| naturalRankDisplay | string | Natural rank display text. String representation of natural search rank |
| productAdRank | integer | Product SP ad rank. The ranking position of this product in Sponsored Products ad placements for this keyword, e.g. 3 means ranked 3rd in ad placement |
| adRankDisplay | string | Ad rank display text. String representation of SP ad rank |
| weeklySearchVolume | integer | Weekly search volume. Estimated weekly search count for this keyword on Amazon |
| keywordPopularityRank | integer | Keyword search popularity rank. This keyword's monthly search volume ranking among all Amazon keywords; lower values indicate higher search volume |
| totalSearchResultProductCount | integer | Total search result product count for this keyword (active listings) |
| trafficShare | number | Traffic share. Proportion of traffic this keyword brings to the product out of all keywords' total traffic, where 1 = 100% |
| naturalTrafficShare | number | Natural traffic score share. Natural search traffic score / total score |
| paidTrafficShare | number | Paid ad traffic score share. Ad traffic score / total score; ad total = sp + sb + sbv + recAd |
| naturalTrafficScore | number | Natural traffic score. Natural search exposure score this keyword brings to this ASIN; 0 = no natural traffic exposure |
| sponsoredProductsScore | number | SP ad regular score. Traffic score for Sponsored Products regular placements (excluding SP recommendation placements) |
| brandAdScore | number | SB brand ad score. Traffic score for Sponsored Brands brand ads (regular + video, combined) |
| videoAdScore | number | SBV video ad score. Traffic score for Sponsored Brands Video video ads |
| sponsoredRecommendationScore | number | SP recommendation placement score. Combined score for Trending now / Seen on social media / Customers frequently viewed / 4 stars and above, etc. |
| sponsoredRecommendationBreakdown | array | SP recommendation placement score breakdown. Each entry `{title, score, scoreRatio}` |
| clickConcentrationShare | number | ABA TOP3 click concentration. Measures whether clicks are concentrated on top ASINs; note this is **not conversion rate** |
| clickToPurchaseConversionRate | number | Click-to-purchase conversion rate (purchaseQty / clickQty) |
| displayPositionTypes | array | Product display position type array. May contain: natural=natural search result position; ac=Amazon's Choice recommendation position; sp=Sponsored Products ad position; top=top-of-page brand ad position; bottom=bottom-of-page brand ad position; er=Editorial Recommendations position; vedio=video ad position; tr=Top Rated recommendation position; trfob=Top Rated Frequently Bought recommendation position |
| trafficCharacteristicMarkers | array | Keyword traffic characteristic marker array. May contain: isMainKw=main traffic keyword; isAccurateKw=precise traffic keyword; isAccurateAboveKw=precise broad keyword; isAccurateTailKw=precise long-tail keyword |
| conversionPerformanceMarkers | array | Conversion performance marker array. May contain: isPurchaseKw=converting keyword; isQualityKw=high-quality conversion keyword; isStableKw=stable conversion keyword; isLossKw=lost conversion keyword; isInvalidKw=invalid impression keyword |
| lastNaturalRankTime | string | Time of the most recent valid natural rank |
| lastAdRankTime | string | Time of the most recent valid SP ad rank |
| periodEndDate | string | Current period (weekly granularity) end date = start week + 7 days (site time) |
| updateTime | string | Keyword data update time |

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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sif/asinKeywords \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"asin": "B0XXXXXXXX", "country": "US", "pageSize": 100, "sortBy": "estSearchesNum", "desc": true}'
```

### Example with Keyword Filter and Conditions

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sif/asinKeywords \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"asin": "B0XXXXXXXX", "country": "US", "keyword": "charger", "conditions": "nfPosition,isPurchaseKw", "sortBy": "lastRank", "desc": false, "pageNum": 1, "pageSize": 50}'
```

---
